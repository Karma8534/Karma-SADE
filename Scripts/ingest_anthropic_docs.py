#!/usr/bin/env python3
"""
K-2: Ingest scraped Anthropic docs to vault ledger via /v1/ambient.
Run after scrape_anthropic_docs.py completes.
"""

import json
import time
import sys
import urllib.request
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs" / "knowledge" / "anthropic-docs"
HUB_URL = "https://hub.arknexus.net/v1/ambient"
DELAY = 0.3  # seconds between requests

def get_token() -> str:
    """Get the hub capture token from vault-neo via SSH."""
    import subprocess
    result = subprocess.run(
        ["ssh", "vault-neo", "cat /opt/seed-vault/memory_v1/hub_auth/hub.capture.token.txt"],
        capture_output=True, text=True, timeout=10
    )
    token = result.stdout.strip()
    if token:
        return token
    raise ValueError("Could not get capture token from vault-neo")

def post_ambient(token: str, content: str, source_url: str, filename: str) -> bool:
    import datetime
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry_id = f"amb_k2_docs_{filename[:40].replace('.','_')}_{int(time.time())}"
    payload = json.dumps({
        "id": entry_id,
        "type": "log",
        "tags": ["anthropic-docs", "knowledge", "k2-scrape", "capture"],
        "content": {
            "source": "k2-docs-scrape",
            "source_node": "P1",
            "summary": f"Anthropic docs: {source_url}",
            "detail": {
                "filename": filename,
                "url": source_url,
                "text": content[:6000],
                "scraped_at": "2026-03-22",
            }
        },
        "timestamp": ts,
    }).encode("utf-8")

    req = urllib.request.Request(
        HUB_URL,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            result = json.loads(r.read())
            return result.get("ok", False) or result.get("id") is not None
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def main():
    if not DOCS_DIR.exists():
        print(f"ERROR: {DOCS_DIR} not found. Run scrape_anthropic_docs.py first.")
        return 1

    try:
        token = get_token()
    except ValueError as e:
        print(f"ERROR: {e}")
        return 1

    files = sorted([f for f in DOCS_DIR.glob("*.md") if f.name != "_index.md"])
    total = len(files)
    success = 0

    print(f"Ingesting {total} docs to vault...")
    print("-" * 60)

    for i, filepath in enumerate(files, 1):
        content = filepath.read_text(encoding="utf-8")
        # Extract source URL from first lines
        source_url = ""
        for line in content.splitlines()[:3]:
            if line.startswith("Source:"):
                source_url = line.replace("Source:", "").strip()
                break

        ok = post_ambient(token, content, source_url, filepath.name)
        status = "OK  " if ok else "FAIL"
        print(f"[{i:3d}/{total}] {status}: {filepath.name}")
        if ok:
            success += 1
        time.sleep(DELAY)

    print("-" * 60)
    print(f"Done: {success}/{total} ingested")
    return 0 if success > 0 else 1

if __name__ == "__main__":
    sys.exit(main())
