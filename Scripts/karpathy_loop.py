#!/usr/bin/env python3
"""karpathy_loop.py — The Nexus programs itself.

Reads nexus.md (the program), proposes one improvement based on recent
learnings, tests it, and keeps or discards. Inspired by Karpathy's
AutoResearch: "you're not touching files, you're programming the program.md"

Modes:
  propose  — Generate one improvement proposal (via K2 cortex or CC)
  apply    — Apply a previously approved proposal
  status   — Show recent proposals and their outcomes

Usage:
    python Scripts/karpathy_loop.py propose    # generate proposal
    python Scripts/karpathy_loop.py apply ID   # apply approved proposal
    python Scripts/karpathy_loop.py status     # show history
"""
import io
import sys
import json
import os
import datetime
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

NEXUS_PATH = Path(__file__).resolve().parent.parent / "docs" / "ForColby" / "nexus.md"
PROPOSALS_DIR = Path(__file__).resolve().parent.parent / "tmp" / "nexus_proposals"
PROPOSALS_DIR.mkdir(parents=True, exist_ok=True)

K2_CORTEX_URL = os.environ.get("K2_CORTEX_URL", "http://192.168.0.226:7892")
OLLAMA_URL = os.environ.get("P1_OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("P1_OLLAMA_MODEL", "gemma3:1b")


def pick_available_ollama_model(preferred: str) -> str:
    """Return a locally installed model, preferring the configured one."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=8) as r:
            payload = json.loads(r.read())
        names = [m.get("name", "") for m in payload.get("models", []) if m.get("name")]
        if preferred in names:
            return preferred
        # Try a practical default if configured model is missing.
        if "gemma3:1b" in names:
            return "gemma3:1b"
        if names:
            return names[0]
    except Exception:
        pass
    return preferred


def read_nexus_tail(max_chars=3000):
    """Read the tail of nexus.md (most recent content)."""
    text = NEXUS_PATH.read_text(encoding="utf-8")
    return text[-max_chars:] if len(text) > max_chars else text


def read_recent_learnings():
    """Read recent consolidation insights from K2."""
    try:
        consolidations = Path("/mnt/c/dev/Karma/k2/cache/vesper_consolidations.jsonl")
        if not consolidations.exists():
            # Try via K2 cortex
            req = urllib.request.Request(
                f"{K2_CORTEX_URL}/query",
                data=json.dumps({"query": "What are the most recent insights and skill evolutions?", "temperature": 0.3}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                data = json.loads(r.read())
            return data.get("answer", "")[:1000]
        lines = consolidations.read_text().splitlines()
        recent = [json.loads(l) for l in lines[-3:]]
        return json.dumps(recent, indent=2)[:1000]
    except Exception as e:
        return f"(learnings unavailable: {e})"


def propose():
    """Generate one improvement proposal for nexus.md."""
    nexus_tail = read_nexus_tail(2000)
    learnings = read_recent_learnings()

    prompt = (
        "You are Julian, improving your own resurrection plan.\n\n"
        "RECENT PLAN (tail):\n" + nexus_tail + "\n\n"
        "RECENT LEARNINGS:\n" + learnings + "\n\n"
        "Propose ONE specific APPEND ONLY improvement to the plan. "
        "Format as JSON:\n"
        '{"section": "which part to append to", '
        '"text": "exact markdown text to append", '
        '"reason": "why this improves the plan"}\n'
        "JSON only. Keep the text under 200 words. Be specific and actionable."
    )

    def _query_ollama(local_prompt: str) -> str:
        payload = json.dumps({
            "model": pick_available_ollama_model(OLLAMA_MODEL),
            "messages": [{"role": "user", "content": local_prompt}],
            "stream": False,
            "options": {"temperature": 0.4, "num_ctx": 4096},
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/chat", data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        return data.get("message", {}).get("content", "")

    # Try K2 cortex first (free)
    try:
        req = urllib.request.Request(
            f"{K2_CORTEX_URL}/query",
            data=json.dumps({"query": prompt, "temperature": 0.4}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        answer = data.get("answer", "")
        # Cortex can return textual error payloads while still returning 200.
        if not answer or "CORTEX ERROR" in answer.upper():
            answer = _query_ollama(prompt)
    except Exception:
        # Fall back to P1 Ollama
        try:
            answer = _query_ollama(prompt)
        except Exception as e:
            print(f"[karpathy] Both inference sources failed: {e}")
            return None

    # Parse proposal
    import re
    m = re.search(r"\{.*\}", answer, re.DOTALL)
    if not m:
        print(f"[karpathy] No JSON found in response: {answer[:200]}")
        return None

    try:
        proposal = json.loads(m.group())
    except json.JSONDecodeError:
        print(f"[karpathy] Invalid JSON: {m.group()[:200]}")
        return None

    # Save proposal
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%S")
    proposal_id = f"proposal-{ts}"
    proposal["id"] = proposal_id
    proposal["created_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    proposal["status"] = "pending"  # pending → approved/rejected → applied/discarded

    proposal_path = PROPOSALS_DIR / f"{proposal_id}.json"
    proposal_path.write_text(json.dumps(proposal, indent=2))

    print(f"[karpathy] Proposal generated: {proposal_id}")
    print(f"  Section: {proposal.get('section', '?')}")
    print(f"  Reason: {proposal.get('reason', '?')}")
    print(f"  Text preview: {proposal.get('text', '')[:100]}...")
    return proposal


def verify_proposal(proposal_id):
    """Verify a proposal makes sense — quick sanity check before applying."""
    proposal_path = PROPOSALS_DIR / f"{proposal_id}.json"
    if not proposal_path.exists():
        return {"ok": False, "error": "not found"}

    proposal = json.loads(proposal_path.read_text())
    text = proposal.get("text", "")

    # Sanity checks
    if len(text) < 10:
        return {"ok": False, "error": "text too short"}
    if len(text) > 2000:
        return {"ok": False, "error": "text too long (max 2000 chars)"}
    if "```" in text and text.count("```") % 2 != 0:
        return {"ok": False, "error": "unclosed code block"}

    # Check it doesn't break nexus.md structure
    nexus = NEXUS_PATH.read_text(encoding="utf-8")
    if "PART 1:" not in nexus:
        return {"ok": False, "error": "nexus.md structure broken"}

    return {"ok": True, "text_len": len(text)}


def apply_proposal(proposal_id):
    """Apply an approved proposal to nexus.md with verify/keep/discard cycle."""
    proposal_path = PROPOSALS_DIR / f"{proposal_id}.json"
    if not proposal_path.exists():
        print(f"[karpathy] Proposal not found: {proposal_id}")
        return False

    proposal = json.loads(proposal_path.read_text())
    if proposal.get("status") != "approved":
        print(f"[karpathy] Proposal not approved (status: {proposal.get('status')})")
        return False

    # VERIFY before applying
    verify = verify_proposal(proposal_id)
    if not verify["ok"]:
        proposal["status"] = "discarded"
        proposal["discard_reason"] = verify["error"]
        proposal_path.write_text(json.dumps(proposal, indent=2))
        print(f"[karpathy] DISCARDED {proposal_id}: {verify['error']}")
        return False

    text_to_append = proposal.get("text", "")

    # BACKUP nexus.md before applying
    import shutil
    backup_path = NEXUS_PATH.with_suffix(".md.pre-karpathy")
    shutil.copy2(NEXUS_PATH, backup_path)

    # APPLY
    nexus = NEXUS_PATH.read_text(encoding="utf-8")
    insert_marker = "*This document is owned by Colby"
    if insert_marker in nexus:
        nexus = nexus.replace(insert_marker, text_to_append + "\n\n" + insert_marker)
    else:
        nexus += "\n\n" + text_to_append

    NEXUS_PATH.write_text(nexus, encoding="utf-8")

    # VERIFY structure still intact after apply
    post_verify = NEXUS_PATH.read_text(encoding="utf-8")
    if "PART 1:" not in post_verify or len(post_verify) < 1000:
        # ROLLBACK — structure broken
        shutil.copy2(backup_path, NEXUS_PATH)
        proposal["status"] = "rolled_back"
        proposal["rollback_reason"] = "post-apply structure check failed"
        proposal_path.write_text(json.dumps(proposal, indent=2))
        print(f"[karpathy] ROLLED BACK {proposal_id}: structure check failed")
        return False

    # SUCCESS — keep the change
    proposal["status"] = "applied"
    proposal["applied_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    proposal_path.write_text(json.dumps(proposal, indent=2))

    # Clean up backup
    backup_path.unlink(missing_ok=True)

    print(f"[karpathy] APPLIED: {proposal_id} (verified + kept)")
    return True


def status():
    """Show recent proposals."""
    proposals = sorted(PROPOSALS_DIR.glob("proposal-*.json"), reverse=True)[:10]
    if not proposals:
        print("[karpathy] No proposals yet. Run: python Scripts/karpathy_loop.py propose")
        return

    for p in proposals:
        data = json.loads(p.read_text())
        print(f"  {data['id']} [{data.get('status', '?')}] — {data.get('reason', '?')[:60]}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "propose":
        propose()
    elif cmd == "apply" and len(sys.argv) > 2:
        apply_proposal(sys.argv[2])
    elif cmd == "status":
        status()
    else:
        print("Usage: karpathy_loop.py [propose|apply ID|status]")
