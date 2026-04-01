"""self_edit_service.py — Self-Edit Engine (Sprint 4d).

Karma proposes changes to its own codebase. Proposals auto-approve after 15min.
EditProposal schema from nexus.md v3.2.0.
"""
import json, os, time, threading, subprocess, difflib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

PROPOSALS_FILE = os.path.join(os.path.dirname(__file__), "..", "tmp", "self_edit_proposals.json")
AUDIT_FILE = os.path.join(os.path.dirname(__file__), "..", "tmp", "self_edit_audit.jsonl")
AUTO_APPROVE_MINUTES = 15
WORK_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Protected paths — never auto-approve edits to these
PROTECTED_PATHS = {
    "CLAUDE.md", ".claude/rules/", ".git/", ".env", "mylocks",
    "hub.chat.token", "api_key", "secret",
}

os.makedirs(os.path.dirname(PROPOSALS_FILE), exist_ok=True)


@dataclass
class EditProposal:
    id: int
    file_path: str
    original_content: str
    new_content: str
    diff: str
    description: str
    proposed_at: str
    status: str = "pending"  # pending, approved, rejected, applied
    applied_at: Optional[str] = None
    approved_by: Optional[str] = None
    proposed_by: str = "karma"
    risk_level: str = "low"  # low, medium, high


_next_id = 1
_proposals: list[EditProposal] = []
_lock = threading.Lock()


def _load():
    """Load proposals from disk."""
    global _proposals, _next_id
    if os.path.exists(PROPOSALS_FILE):
        try:
            with open(PROPOSALS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            _proposals = [EditProposal(**p) for p in data]
            if _proposals:
                _next_id = max(p.id for p in _proposals) + 1
        except Exception:
            _proposals = []


def _save():
    """Save proposals to disk."""
    try:
        with open(PROPOSALS_FILE, "w", encoding="utf-8") as f:
            json.dump([asdict(p) for p in _proposals], f, indent=2)
    except Exception:
        pass


def _audit(action: str, proposal_id: int, detail: str = ""):
    """Append to audit trail."""
    try:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "proposal_id": proposal_id,
            "detail": detail,
        }
        with open(AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def _is_protected(file_path: str) -> bool:
    """Check if file is in a protected path."""
    normalized = file_path.replace("\\", "/")
    return any(p in normalized for p in PROTECTED_PATHS)


def _make_diff(original: str, new: str, file_path: str) -> str:
    """Generate unified diff."""
    orig_lines = original.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(orig_lines, new_lines, fromfile=f"a/{file_path}", tofile=f"b/{file_path}")
    return "".join(diff)


def propose(file_path: str, new_content: str, description: str, risk_level: str = "low") -> dict:
    """Create a new edit proposal."""
    global _next_id
    with _lock:
        # Read original content
        full_path = os.path.normpath(os.path.join(WORK_DIR, file_path))
        if not full_path.startswith(WORK_DIR):
            return {"ok": False, "error": "path outside project"}

        original = ""
        if os.path.exists(full_path):
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    original = f.read()
            except Exception as e:
                return {"ok": False, "error": f"cannot read: {e}"}

        diff = _make_diff(original, new_content, file_path)
        if not diff:
            return {"ok": False, "error": "no changes detected"}

        # Elevate risk for protected paths
        if _is_protected(file_path):
            risk_level = "high"

        now = datetime.now(timezone.utc).isoformat()
        proposal = EditProposal(
            id=_next_id, file_path=file_path, original_content=original,
            new_content=new_content, diff=diff, description=description,
            proposed_at=now, risk_level=risk_level,
        )
        _proposals.append(proposal)
        _next_id += 1
        _save()
        _audit("proposed", proposal.id, description)

        return {"ok": True, "id": proposal.id, "risk_level": risk_level, "diff_lines": len(diff.splitlines())}


def approve(proposal_id: int, approved_by: str = "sovereign") -> dict:
    """Approve and apply a proposal."""
    with _lock:
        p = next((p for p in _proposals if p.id == proposal_id and p.status == "pending"), None)
        if not p:
            return {"ok": False, "error": f"proposal {proposal_id} not found or not pending"}
        return _apply(p, approved_by)


def reject(proposal_id: int) -> dict:
    """Reject a proposal."""
    with _lock:
        p = next((p for p in _proposals if p.id == proposal_id and p.status == "pending"), None)
        if not p:
            return {"ok": False, "error": f"proposal {proposal_id} not found or not pending"}
        p.status = "rejected"
        _save()
        _audit("rejected", p.id)
        return {"ok": True, "status": "rejected"}


def _apply(p: EditProposal, approved_by: str) -> dict:
    """Apply a proposal — write file and git commit."""
    full_path = os.path.normpath(os.path.join(WORK_DIR, p.file_path))
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(p.new_content)
    except Exception as e:
        return {"ok": False, "error": f"write failed: {e}"}

    p.status = "applied"
    p.applied_at = datetime.now(timezone.utc).isoformat()
    p.approved_by = approved_by
    _save()
    _audit("applied", p.id, f"approved_by={approved_by}")

    # Git commit (best-effort)
    try:
        subprocess.run(
            ["git", "add", p.file_path],
            cwd=WORK_DIR, capture_output=True, timeout=10,
        )
        subprocess.run(
            ["git", "commit", "-m", f"self-edit: {p.description}\n\nProposal #{p.id}, approved by {approved_by}"],
            cwd=WORK_DIR, capture_output=True, timeout=10,
        )
    except Exception:
        pass  # Git commit is best-effort

    return {"ok": True, "status": "applied", "file_path": p.file_path}


def auto_approve_check():
    """Check for proposals past the auto-approve window. Apply them."""
    with _lock:
        now_ts = time.time()
        for p in _proposals:
            if p.status != "pending":
                continue
            # Skip high-risk proposals — require manual approval
            if p.risk_level == "high":
                continue
            proposed_ts = datetime.fromisoformat(p.proposed_at).timestamp()
            if now_ts - proposed_ts > AUTO_APPROVE_MINUTES * 60:
                _apply(p, "auto-approved")


def list_pending() -> list[dict]:
    """List all pending proposals."""
    with _lock:
        result = []
        for p in _proposals:
            if p.status != "pending":
                continue
            proposed_ts = datetime.fromisoformat(p.proposed_at).timestamp()
            auto_approve_at = proposed_ts + (AUTO_APPROVE_MINUTES * 60)
            result.append({
                "id": p.id, "file_path": p.file_path, "description": p.description,
                "risk_level": p.risk_level, "proposed_at": p.proposed_at,
                "status": p.status, "diff_preview": p.diff[:500],
                "auto_approve_at": datetime.fromtimestamp(auto_approve_at, tz=timezone.utc).isoformat()
                    if p.risk_level != "high" else None,
            })
        return result


# Initialize
_load()


# ── Auto-approve scheduler (background thread) ──────────────────────────────
def _scheduler_loop():
    while True:
        time.sleep(60)
        try:
            auto_approve_check()
        except Exception:
            pass


_scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True)
_scheduler_thread.start()


if __name__ == "__main__":
    # Quick test
    _proposals.clear()
    _next_id = 1
    _save()

    # Create test proposal
    result = propose("test_self_edit.txt", "hello world\n", "test proposal", "low")
    assert result["ok"], f"propose failed: {result}"
    assert result["id"] == 1

    # List pending
    pending = list_pending()
    assert len(pending) == 1
    assert pending[0]["description"] == "test proposal"

    # Approve
    result = approve(1)
    assert result["ok"], f"approve failed: {result}"
    assert result["status"] == "applied"

    # Verify file was created
    test_path = os.path.join(WORK_DIR, "test_self_edit.txt")
    assert os.path.exists(test_path)
    with open(test_path, "r") as f:
        assert f.read() == "hello world\n"
    os.remove(test_path)

    # Reject test
    propose("test2.txt", "content\n", "test reject", "low")
    result = reject(2)
    assert result["ok"] and result["status"] == "rejected"

    print("PASS")
