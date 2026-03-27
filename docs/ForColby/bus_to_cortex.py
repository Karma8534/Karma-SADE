#!/usr/bin/env python3
"""
bus_to_cortex.py — Feed coordination bus messages to Julian cortex.
Runs every 2 minutes on K2 via cron.
Polls recent bus messages, ingests new ones into cortex at localhost:7892.
No Anthropic API needed — pure local pipeline.
"""
import json
import os
import sys
import datetime
import urllib.request
import urllib.error
from pathlib import Path

HUB_URL     = "https://hub.arknexus.net"
CORTEX_URL  = "http://localhost:7892"
CACHE       = Path("/mnt/c/dev/Karma/k2/cache")
WATERMARK_F = CACHE / "bus_to_cortex_watermark.json"
TOKEN       = os.environ.get("HUB_AUTH_TOKEN", "")


def load_watermark():
    try:
        return json.loads(WATERMARK_F.read_text())
    except Exception:
        return {"seen_ids": [], "last_run": None}


def save_watermark(wm):
    WATERMARK_F.write_text(json.dumps(wm))


def fetch_bus_messages():
    """Fetch recent bus messages (all senders, all targets)."""
    url = f"{HUB_URL}/v1/coordination/recent?limit=30"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        return data if isinstance(data, list) else (data.get("entries") or data.get("messages") or [])
    except Exception as e:
        print(f"Bus fetch failed: {e}", file=sys.stderr)
        return []


def ingest_to_cortex(label, text):
    """POST a message to the Julian cortex ingest endpoint."""
    payload = json.dumps({"label": label, "text": text}).encode()
    req = urllib.request.Request(
        f"{CORTEX_URL}/ingest",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            result = json.loads(r.read())
        return result.get("ok", False)
    except Exception as e:
        print(f"Cortex ingest failed: {e}", file=sys.stderr)
        return False


def main():
    if not TOKEN:
        print("ERROR: HUB_AUTH_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    # Health check cortex
    try:
        with urllib.request.urlopen(f"{CORTEX_URL}/health", timeout=5) as r:
            health = json.loads(r.read())
        if not health.get("ok"):
            print("Cortex not healthy, skipping", file=sys.stderr)
            return
    except Exception:
        print("Cortex unreachable, skipping", file=sys.stderr)
        return

    wm = load_watermark()
    seen_ids = set(wm.get("seen_ids", []))
    messages = fetch_bus_messages()

    if not messages:
        return

    ingested = 0
    for msg in messages:
        msg_id = msg.get("id") or msg.get("ts") or ""
        if not msg_id or msg_id in seen_ids:
            continue

        from_ = msg.get("from", "unknown")
        to_ = msg.get("to", "all")
        content = msg.get("content") or msg.get("message") or msg.get("text") or ""
        ts = msg.get("ts") or msg.get("timestamp") or msg.get("created_at") or ""

        if not content.strip():
            seen_ids.add(msg_id)
            continue

        # Build cortex-friendly summary
        label = f"bus-{from_}-{ts[:16] if ts else msg_id[:20]}"
        text = f"[BUS {from_}→{to_}] {content[:500]}"

        if ingest_to_cortex(label, text):
            ingested += 1

        seen_ids.add(msg_id)

    # Persist watermark (keep last 300 IDs)
    wm["seen_ids"] = list(seen_ids)[-300:]
    wm["last_run"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    wm["last_ingested"] = ingested
    save_watermark(wm)

    if ingested:
        print(f"Ingested {ingested} bus message(s) to cortex")


if __name__ == "__main__":
    main()
