#!/usr/bin/env python3
"""
corpus_builder.py — E-1-A: Build Alpaca-format corpus from vault ledger hub+chat entries.

Usage:
  python3 Scripts/corpus_builder.py [--dry-run] [--limit N]

Output: Logs/corpus_alpaca.jsonl
Format: {"instruction": user_text, "input": "", "output": assistant_text}
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

LEDGER_PATH = "/opt/seed-vault/memory_v1/ledger/memory.jsonl"
OUTPUT_PATH = Path("Logs/corpus_alpaca.jsonl")
MIN_ASSISTANT_CHARS = 50

FETCH_SCRIPT = r"""
import json, sys
path = '/opt/seed-vault/memory_v1/ledger/memory.jsonl'
count = 0
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        tags = e.get('tags', [])
        if 'hub' in tags and 'chat' in tags:
            sys.stdout.write(line + '\n')
            count += 1
"""


def extract_pair(entry: dict) -> tuple[str, str] | None:
    """Extract (user_text, assistant_text) from a ledger entry. Returns None if unusable."""
    content = entry.get("content", {})
    if not isinstance(content, dict):
        return None

    user_text = content.get("user_message", "").strip()
    # Try both field names: newer entries use assistant_text, legacy use assistant_message
    assistant_text = (
        content.get("assistant_text", "") or content.get("assistant_message", "")
    ).strip()

    if not user_text or not assistant_text:
        return None
    if len(assistant_text) < MIN_ASSISTANT_CHARS:
        return None

    return user_text, assistant_text


def fetch_entries_from_vault() -> list[dict]:
    """SSH to vault-neo and stream all ledger entries with hub+chat tags."""
    cmd = ["ssh", "vault-neo", "python3 -"]

    result = subprocess.run(
        cmd,
        input=FETCH_SCRIPT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )

    if result.returncode != 0:
        print(f"ERROR: SSH fetch failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    entries = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"WARN: skipping malformed line: {e}", file=sys.stderr)

    return entries


def build_corpus(limit: int = 0, dry_run: bool = False) -> int:
    print(f"Fetching hub+chat entries from vault-neo...")
    entries = fetch_entries_from_vault()
    print(f"  Raw entries fetched: {len(entries)}")

    pairs = []
    skipped = 0
    for entry in entries:
        result = extract_pair(entry)
        if result is None:
            skipped += 1
            continue
        user_text, assistant_text = result
        pairs.append(
            {"instruction": user_text, "input": "", "output": assistant_text}
        )
        if limit > 0 and len(pairs) >= limit:
            break

    print(f"  Valid pairs: {len(pairs)} | Skipped (in window): {skipped}")

    if dry_run:
        print(f"Would write {len(pairs)} pairs to {OUTPUT_PATH}")
        if pairs:
            print(f"\nSample pair 1:")
            print(f"  instruction: {pairs[0]['instruction'][:120]}")
            print(f"  output: {pairs[0]['output'][:120]}")
        return len(pairs)

    # Write output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        for pair in pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    print(f"Written: {OUTPUT_PATH} ({len(pairs)} lines)")
    return len(pairs)


def main():
    parser = argparse.ArgumentParser(description="Build Alpaca corpus from vault ledger.")
    parser.add_argument("--dry-run", action="store_true", help="Count pairs without writing")
    parser.add_argument("--limit", type=int, default=0, help="Cap raw entries fetched (0 = all)")
    args = parser.parse_args()

    n = build_corpus(limit=args.limit, dry_run=args.dry_run)
    if n == 0:
        print("WARNING: 0 pairs produced. Check field names or ledger access.")
        sys.exit(1)


if __name__ == "__main__":
    main()
