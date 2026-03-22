#!/usr/bin/env python3
"""
Generate JSONL ledger entries from scraped Anthropic docs.
Output goes to stdout — pipe to vault-neo via SSH.
Usage: python gen_docs_ledger_entries.py | ssh vault-neo 'cat >> /opt/seed-vault/memory_v1/ledger/memory.jsonl'
"""
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

DOCS_DIR = Path(__file__).parent.parent / "docs" / "knowledge" / "anthropic-docs"

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

def main():
    files = sorted([f for f in DOCS_DIR.glob("*.md") if f.name != "_index.md"])
    ts = now_iso()

    for filepath in files:
        content = filepath.read_text(encoding="utf-8")

        # Extract source URL and title from header
        source_url = ""
        title = filepath.stem.replace("__", "/").replace("docs/en/", "")
        for line in content.splitlines()[:5]:
            if line.startswith("Source:"):
                source_url = line.replace("Source:", "").strip()
            elif line.startswith("# ") and not line.startswith("# Source"):
                title = line[2:].strip()

        # Use first 4000 chars of content as text value
        text = content[:4000].strip()

        entry = {
            "type": "log",
            "content": {
                "value": text,
                "title": title,
                "url": source_url,
            },
            "tags": ["anthropic-docs", "knowledge", "k2-scrape", "capture"],
            "source": {
                "kind": "tool",
                "ref": "k2-docs-scrape",
            },
            "created_at": ts,
            "updated_at": ts,
            "confidence": 1,
            "verification": {
                "protocol_version": "fp.v1",
                "verified_at": ts,
                "verifier": "cc-p1",
                "status": "verified",
                "notes": "K-2 Anthropic docs scrape 2026-03-22",
            }
        }
        print(json.dumps(entry))
        sys.stdout.flush()

if __name__ == "__main__":
    # Write to explicit output file to avoid Windows stdout encoding issues
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/k2_docs_entries.jsonl")
    import io
    old_stdout = sys.stdout
    sys.stdout = io.open(out_path, 'w', encoding='utf-8', newline='\n')
    main()
    sys.stdout.close()
    sys.stdout = old_stdout
    print(f"Written to {out_path}")
