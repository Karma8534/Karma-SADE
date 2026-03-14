"""
karma_kiki_v5.py — Karma Autonomous Loop (Minimal Viable)
Built: 2026-03-13

Design principle: prove ONE real cycle end-to-end before adding complexity.
- Read an issue → think (devstral) → act → verify → close issue → journal
- Issues get CLOSED after action (no infinite repeat)
- Actions verified by byte-level diff (no fake "fix completed")
- Failed actions journaled as failures, not successes
- No TITANS, no surprise scoring — add back once base works

Zero Anthropic calls. Local Ollama only. Free. Continuous.
"""

import os
import sys
import json
import time
import signal
import logging
import subprocess
import urllib.request
import threading
from datetime import datetime, timezone
from pathlib import Path

# ============ Configuration ============

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://172.22.240.1:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "devstral:latest")
LOOP_INTERVAL = int(os.environ.get("LOOP_INTERVAL", "60"))

BASE_DIR = Path(os.environ.get("KARMA_BASE", "/mnt/c/dev/Karma/k2"))
CACHE_DIR = BASE_DIR / "cache"
SCRIPTS_DIR = BASE_DIR / "scripts"

ISSUES_FILE = CACHE_DIR / "kiki_issues.jsonl"
JOURNAL_FILE = CACHE_DIR / "kiki_journal.jsonl"
STATE_FILE = CACHE_DIR / "kiki_state.json"
DIRECTIVE_FILE = CACHE_DIR / "karma_directive.md"
JOURNAL_MAX_ENTRIES = 200

VAULT_AMBIENT_URL = os.environ.get(
    "VAULT_AMBIENT_URL", "https://hub.arknexus.net/v1/ambient"
)

# ============ Logging ============

LOG_FILE = os.environ.get("YOYO_LOG", "/var/log/karma_kiki.log")
_handlers = [logging.StreamHandler()]
try:
    _handlers.append(logging.FileHandler(LOG_FILE))
except (PermissionError, FileNotFoundError):
    _handlers.append(logging.FileHandler(CACHE_DIR / "kiki.log"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [YOYOv5] %(levelname)s %(message)s",
    handlers=_handlers,
)
log = logging.getLogger("kiki")

# ============ Ollama ============

def ollama_chat(system_prompt: str, user_prompt: str, timeout: int = 360) -> str:
    """Call local Ollama via /api/chat. Returns raw text response."""
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 2048},
    }).encode()

    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read())
    return body.get("message", {}).get("content", "")


def ollama_alive() -> bool:
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False

# ============ Issues ============

def load_issues() -> list[dict]:
    """Load all issues from JSONL file."""
    if not ISSUES_FILE.exists():
        return []
    issues = []
    for line in ISSUES_FILE.read_text().strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            issues.append(json.loads(line))
        except Exception:
            pass
    return issues


def save_issues(issues: list[dict]):
    """Rewrite issues file without closed issues."""
    ISSUES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ISSUES_FILE, "w") as f:
        for issue in issues:
            f.write(json.dumps(issue) + "\n")


def close_issue(issues: list[dict], index: int) -> list[dict]:
    """Remove issue at index. Returns new list."""
    return [i for idx, i in enumerate(issues) if idx != index]

# ============ State ============

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {
        "cycles": 0, "started_at": _now(),
        "actions_attempted": 0, "actions_succeeded": 0,
        "actions_failed": 0, "issues_closed": 0,
        "idle_cycles": 0,
    }


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))

# ============ Context ============

def gather_context() -> str:
    """Minimal context: workspace files + directive snippet."""
    parts = []

    # Directive
    try:
        if DIRECTIVE_FILE.exists():
            parts.append(f"DIRECTIVE:\n{DIRECTIVE_FILE.read_text()[:1500]}")
    except Exception:
        pass

    # Workspace files
    try:
        files = []
        for f in sorted(CACHE_DIR.iterdir()):
            if f.is_file():
                sz = f.stat().st_size
                mt = datetime.fromtimestamp(f.stat().st_mtime).strftime("%m-%d %H:%M")
                files.append(f"  {f.name} ({sz}B, {mt})")
        parts.append("WORKSPACE:\n" + "\n".join(files[:20]))
    except Exception:
        pass

    # Recent journal (last 5 entries only)
    try:
        if JOURNAL_FILE.exists():
            lines = JOURNAL_FILE.read_text().strip().split("\n")
            recent = lines[-5:] if len(lines) > 5 else lines
            entries = []
            for line in recent:
                try:
                    e = json.loads(line)
                    entries.append(f"  [{e.get('ts','')}] {e.get('ok','?')} {e.get('type','?')}: {e.get('summary','')}")
                except Exception:
                    pass
            if entries:
                parts.append("RECENT JOURNAL:\n" + "\n".join(entries))
    except Exception:
        pass

    return "\n\n".join(parts)

# ============ Think ============

SYSTEM_PROMPT = """You are Karma's autonomous brain running on K2 via Ollama.
You receive ONE issue to work on. Your job: produce a concrete fix.

RESPOND IN VALID JSON ONLY. No markdown fences. No explanation outside JSON.
{
  "action": "description of what you're doing",
  "target_file": "/absolute/path/to/file/to/write",
  "content": "the COMPLETE file content to write",
  "test_command": "shell command to verify (null if none)"
}

RULES:
- target_file MUST be an absolute path under /mnt/c/dev/Karma/k2/
- content MUST be the COMPLETE file content, not a patch
- If the issue asks you to modify an existing file, include ALL of its content with your changes
- If you cannot solve the issue, set target_file to null and explain in action
"""


def think(issue: dict, context: str) -> dict | None:
    """Ask devstral to solve one issue. Returns parsed action or None."""
    user_msg = f"""ISSUE TO SOLVE:
{issue.get('issue', '')}

DETAILS:
{issue.get('details', '')}

CONTEXT:
{context}

Produce a JSON fix for this issue. target_file must be absolute path under /mnt/c/dev/Karma/k2/."""

    try:
        raw = ollama_chat(SYSTEM_PROMPT, user_msg)
    except Exception as e:
        log.error(f"Ollama call failed: {e}")
        return None

    log.info(f"LLM response length: {len(raw)} chars")
    log.info(f"LLM first 200: {repr(raw[:200])}")

    # Strip markdown fences
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    # Strip think tags
    if "<think>" in raw:
        parts = raw.split("</think>")
        raw = parts[-1].strip() if len(parts) > 1 else raw

    # Parse JSON
    try:
        return json.loads(raw)
    except Exception:
        pass

    # Try extracting JSON object
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(raw[start:end])
        except Exception:
            pass

    log.warning(f"Unparseable LLM response: {raw[:300]}")
    return None

# ============ Act + Verify ============

def act_and_verify(decision: dict) -> dict:
    """Write file, run test, verify bytes actually changed. Returns result."""
    target = decision.get("target_file")
    content = decision.get("content", "")
    test_cmd = decision.get("test_command")

    if not target or not content:
        return {"ok": False, "reason": "no target_file or content in LLM response"}

    target_path = Path(target)

    # Security: must be under K2 base
    try:
        target_path.resolve().relative_to(BASE_DIR.resolve())
    except ValueError:
        return {"ok": False, "reason": f"target_file {target} is outside {BASE_DIR}"}

    # Read before-state
    before_bytes = None
    if target_path.exists():
        try:
            before_bytes = target_path.read_bytes()
        except Exception:
            pass

    # Write
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(content)
        log.info(f"Wrote {len(content)} chars to {target}")
    except Exception as e:
        return {"ok": False, "reason": f"write failed: {e}"}

    # Verify bytes actually changed
    after_bytes = target_path.read_bytes()
    if before_bytes is not None and before_bytes == after_bytes:
        return {"ok": False, "reason": "file unchanged — wrote identical content"}

    # Run test if provided
    if test_cmd:
        try:
            result = subprocess.run(
                test_cmd, shell=True, capture_output=True, text=True, timeout=30
            )
            if result.returncode != 0:
                # Revert
                if before_bytes is not None:
                    target_path.write_bytes(before_bytes)
                    log.warning(f"Test failed, reverted {target}")
                else:
                    target_path.unlink(missing_ok=True)
                    log.warning(f"Test failed, removed {target}")
                return {
                    "ok": False,
                    "reason": f"test failed (exit {result.returncode}): {result.stderr[:200]}",
                    "reverted": True,
                }
            log.info(f"Test passed: {test_cmd}")
        except subprocess.TimeoutExpired:
            if before_bytes is not None:
                target_path.write_bytes(before_bytes)
            else:
                target_path.unlink(missing_ok=True)
            return {"ok": False, "reason": "test timed out, reverted"}

    bytes_changed = len(after_bytes) - (len(before_bytes) if before_bytes else 0)
    return {
        "ok": True,
        "reason": f"wrote {len(content)} chars to {target} (delta: {bytes_changed:+d} bytes)",
        "new_file": before_bytes is None,
    }

# ============ Journal ============

def journal_write(cycle: int, issue: dict, decision: dict | None, result: dict):
    """Append structured entry to journal."""
    entry = {
        "ts": _now(),
        "cycle": cycle,
        "type": "action" if result.get("ok") else "failure",
        "issue": issue.get("issue", "")[:100],
        "summary": (decision or {}).get("action", "no decision"),
        "result": result.get("reason", ""),
        "ok": result.get("ok", False),
        "vault_worthy": result.get("ok", False),
    }

    JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(JOURNAL_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    # Rotate
    try:
        lines = JOURNAL_FILE.read_text().strip().split("\n")
        if len(lines) > JOURNAL_MAX_ENTRIES:
            JOURNAL_FILE.write_text("\n".join(lines[-JOURNAL_MAX_ENTRIES:]) + "\n")
    except Exception:
        pass

    # Sync successful actions to vault
    if result.get("ok"):
        _sync_to_vault(entry)


def _sync_to_vault(entry: dict):
    content = (
        f"[karma-kiki-v5] Cycle #{entry.get('cycle',0)}: "
        f"{entry.get('summary','')} — {entry.get('result','')}"
    )
    payload = json.dumps({
        "source": "karma_kiki_v5",
        "content": content,
        "lane": "k2_evolution",
        "timestamp": entry.get("ts", _now()),
    }).encode()
    try:
        req = urllib.request.Request(
            VAULT_AMBIENT_URL, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            log.info(f"Vault sync: {resp.status}")
    except Exception as e:
        log.warning(f"Vault sync failed (non-fatal): {e}")

# ============ Main Loop ============

_shutdown = threading.Event()

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _handle_signal(signum, _):
    log.info(f"Signal {signum} — stopping.")
    _shutdown.set()

signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


def run_cycle(state: dict):
    """One cycle: pick issue → think → act → verify → close → journal."""
    state["cycles"] += 1
    state["last_cycle_ts"] = _now()
    cycle = state["cycles"]
    log.info(f"=== Cycle #{cycle} ===")

    # 1. Load issues
    issues = load_issues()
    if not issues:
        log.info("No issues in backlog — idle")
        state["idle_cycles"] += 1
        return

    # 2. Pick first issue
    issue = issues[0]
    log.info(f"Working on: {issue.get('issue', '')[:80]}")

    # 3. Check Ollama
    if not ollama_alive():
        log.error("Ollama unreachable — skipping cycle")
        journal_write(cycle, issue, None, {"ok": False, "reason": "Ollama unreachable"})
        return

    # 4. Think
    context = gather_context()
    decision = think(issue, context)

    if not decision or not decision.get("target_file"):
        reason = "LLM returned no actionable response"
        if decision:
            reason = decision.get("action", reason)
        log.warning(f"No action: {reason}")
        journal_write(cycle, issue, decision, {"ok": False, "reason": reason})
        # Still close the issue if LLM says it can't solve it — prevent infinite loop
        if decision and not decision.get("target_file"):
            issues = close_issue(issues, 0)
            save_issues(issues)
            state["issues_closed"] += 1
            log.info(f"Closed unsolvable issue. {len(issues)} remaining.")
        return

    # 5. Act + Verify
    state["actions_attempted"] += 1
    result = act_and_verify(decision)
    log.info(f"Result: ok={result['ok']} — {result.get('reason', '')[:100]}")

    # 6. Journal
    journal_write(cycle, issue, decision, result)

    # 7. Close issue (whether success or failure — prevent infinite retry)
    issues = close_issue(issues, 0)
    save_issues(issues)
    state["issues_closed"] += 1

    if result["ok"]:
        state["actions_succeeded"] += 1
        log.info(f"SUCCESS — issue closed, {len(issues)} remaining")
    else:
        state["actions_failed"] += 1
        log.info(f"FAILED — issue closed anyway (no infinite retry), {len(issues)} remaining")


def main():
    log.info("=" * 50)
    log.info("KARMA YOYO v5.0 — MINIMAL VIABLE AUTONOMOUS LOOP")
    log.info(f"Model: {OLLAMA_MODEL} @ {OLLAMA_URL}")
    log.info(f"Cycle interval: {LOOP_INTERVAL}s")
    log.info(f"Issues file: {ISSUES_FILE}")
    log.info("Design: read issue → think → act → VERIFY → close → journal")
    log.info("=" * 50)

    state = load_state()
    # Reset counters for v5
    state["started_at"] = _now()
    state["cycles"] = 0
    state["actions_attempted"] = 0
    state["actions_succeeded"] = 0
    state["actions_failed"] = 0
    state["issues_closed"] = 0
    state["idle_cycles"] = 0
    save_state(state)

    if not ollama_alive():
        log.error(f"Ollama not reachable at {OLLAMA_URL} — cannot start")
        sys.exit(1)

    log.info("Ollama verified. Starting loop.")

    while not _shutdown.is_set():
        try:
            run_cycle(state)
            save_state(state)
        except Exception as e:
            log.error(f"Cycle error: {e}", exc_info=True)
        _shutdown.wait(timeout=LOOP_INTERVAL)

    save_state(state)
    log.info("Karma kiki v5 stopped. State saved.")


if __name__ == "__main__":
    main()
