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
OLLAMA_MODEL = os.environ.get("P1_OLLAMA_MODEL", "sam860/LFM2:350m")


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
    except Exception:
        # Fall back to P1 Ollama
        try:
            payload = json.dumps({
                "model": OLLAMA_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
                "options": {"temperature": 0.4, "num_ctx": 4096},
            }).encode()
            req = urllib.request.Request(
                f"{OLLAMA_URL}/api/chat", data=payload,
                headers={"Content-Type": "application/json"}, method="POST",
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
            answer = data.get("message", {}).get("content", "")
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


def apply_proposal(proposal_id):
    """Apply an approved proposal to nexus.md."""
    proposal_path = PROPOSALS_DIR / f"{proposal_id}.json"
    if not proposal_path.exists():
        print(f"[karpathy] Proposal not found: {proposal_id}")
        return False

    proposal = json.loads(proposal_path.read_text())
    if proposal.get("status") != "approved":
        print(f"[karpathy] Proposal not approved (status: {proposal.get('status')})")
        return False

    text_to_append = proposal.get("text", "")
    if not text_to_append:
        print("[karpathy] No text to append")
        return False

    # Append to nexus.md (before the final signature line)
    nexus = NEXUS_PATH.read_text(encoding="utf-8")
    insert_marker = "*This document is owned by Colby"
    if insert_marker in nexus:
        nexus = nexus.replace(insert_marker, text_to_append + "\n\n" + insert_marker)
    else:
        nexus += "\n\n" + text_to_append

    NEXUS_PATH.write_text(nexus, encoding="utf-8")
    proposal["status"] = "applied"
    proposal["applied_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    proposal_path.write_text(json.dumps(proposal, indent=2))

    print(f"[karpathy] Applied: {proposal_id}")
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
