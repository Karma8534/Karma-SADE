#!/usr/bin/env python3
"""
sync_k2_to_p1.py — Sync K2 cortex knowledge blocks to P1 fallback cortex.
Pulls K2 state via SSH, compares with P1, ingests missing blocks.
Run periodically (every 30min) or manually before failover testing.
"""
import json
import subprocess
import urllib.request
import sys

K2_STATE = "/mnt/c/dev/Karma/k2/cache/cortex/state.json"
K2_SSH = "karma@192.168.0.226"
P1_CORTEX = "http://localhost:7893"


def fetch_k2_state():
    """Fetch K2 cortex state via SSH."""
    result = subprocess.run(
        ["ssh", "-o", "ConnectTimeout=5", K2_SSH, f"cat {K2_STATE}"],
        capture_output=True, timeout=15, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        print(f"ERROR: SSH to K2 failed: {result.stderr}", file=sys.stderr)
        return None
    return json.loads(result.stdout)


def fetch_p1_labels():
    """Get labels of blocks already in P1 cortex."""
    try:
        req = urllib.request.Request(f"{P1_CORTEX}/health")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
        if not data.get("ok"):
            return None
    except Exception:
        print("ERROR: P1 cortex unreachable", file=sys.stderr)
        return None

    # Read P1 state file directly (local) — MUST use utf-8 encoding (P053: Windows cp1252 breaks on non-ASCII)
    try:
        with open(r"C:\Users\raest\Documents\Karma_SADE\Scripts\cortex\state\state.json", encoding="utf-8") as f:
            p1_state = json.load(f)
        return {label for label, _ in p1_state.get("knowledge_blocks", [])}
    except Exception as e:
        print(f"WARNING: Could not read P1 state file: {e}", file=sys.stderr)
        return set()


def ingest_to_p1(label, text):
    """POST a block to P1 cortex."""
    payload = json.dumps({"label": label, "text": text}).encode()
    req = urllib.request.Request(
        f"{P1_CORTEX}/ingest",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            result = json.loads(r.read())
        return result.get("ok", False)
    except Exception as e:
        print(f"Ingest failed for [{label}]: {e}", file=sys.stderr)
        return False


def main():
    print("Fetching K2 cortex state...")
    k2_state = fetch_k2_state()
    if not k2_state:
        sys.exit(1)

    k2_blocks = k2_state.get("knowledge_blocks", [])
    print(f"K2 has {len(k2_blocks)} blocks")

    p1_labels = fetch_p1_labels()
    if p1_labels is None:
        sys.exit(1)
    print(f"P1 has {len(p1_labels)} known labels")

    # Find missing blocks
    missing = [(label, text) for label, text in k2_blocks if label not in p1_labels]
    print(f"Missing from P1: {len(missing)} blocks")

    if not missing:
        print("P1 is up to date.")
        return

    synced = 0
    for label, text in missing:
        if ingest_to_p1(label, text):
            synced += 1

    print(f"Synced {synced}/{len(missing)} blocks to P1")


if __name__ == "__main__":
    main()
