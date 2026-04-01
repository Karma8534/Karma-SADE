#!/usr/bin/env python3
"""
karma_action_loop.py — Persistent Karma action loop (S155)
Polls coordination bus for actionable messages, uses cortex to reason about them,
posts responses back. Runs as cron on K2 every 5 minutes.

This is the bridge between request-response Karma and autonomous Karma.
Karma watches. Karma thinks. Karma acts.

Primitive #74 (Ralph Loop): on actionable bus message, generate response and post back.
"""
import json
import os
import sys
import datetime
import urllib.request
import urllib.error
from pathlib import Path

HUB_URL = os.environ.get("HUB_URL", "https://hub.arknexus.net")
CORTEX_URL = os.environ.get("CORTEX_URL", "http://localhost:7892")
TOKEN = os.environ.get("HUB_AUTH_TOKEN", "")
CACHE = Path("/mnt/c/dev/Karma/k2/cache")
WATERMARK = CACHE / "karma_action_watermark.json"
LOG = CACHE / "karma_action_loop.log"

# Message types that Karma should act on
ACTIONABLE_TYPES = {"task", "directive", "question"}
# Messages TO karma or TO all
ACTIONABLE_TARGETS = {"karma", "all"}
# Ignore messages FROM karma (don't respond to self)
SELF_SENDERS = {"karma", "regent", "vesper"}

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line, flush=True)

def load_watermark():
    try:
        return json.loads(WATERMARK.read_text())
    except Exception:
        return {"handled_ids": []}

def save_watermark(wm):
    # Keep only last 100 IDs
    wm["handled_ids"] = wm["handled_ids"][-100:]
    WATERMARK.write_text(json.dumps(wm))

def http_json(url, method="GET", data=None, headers=None, timeout=10):
    headers = headers or {}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    headers["Content-Type"] = "application/json"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        log(f"HTTP error: {url} — {e}")
        return None

def fetch_actionable_messages(handled_ids):
    """Fetch bus messages that Karma should act on."""
    data = http_json(f"{HUB_URL}/v1/coordination/recent?limit=20&status=pending")
    if not data or not data.get("ok"):
        return []

    actionable = []
    for entry in data.get("entries", []):
        eid = entry.get("id", "")
        if eid in handled_ids:
            continue
        msg_to = entry.get("to", "").lower()
        msg_from = entry.get("from", "").lower()
        msg_type = entry.get("type", "").lower()

        # Skip self-messages
        if msg_from in SELF_SENDERS:
            continue
        # Must be addressed to karma or all
        if msg_to not in ACTIONABLE_TARGETS:
            continue
        # Must be an actionable type
        if msg_type not in ACTIONABLE_TYPES:
            continue

        actionable.append(entry)

    return actionable

def ask_cortex(question):
    """Ask the cortex a question and get a response."""
    data = http_json(
        f"{CORTEX_URL}/query",
        method="POST",
        data={"query": question, "temperature": 0.3},
        timeout=30
    )
    if data and data.get("ok"):
        return data.get("answer", "")
    return None

def post_response(original_id, content):
    """Post Karma's response back to the bus."""
    return http_json(
        f"{HUB_URL}/v1/coordination/post",
        method="POST",
        data={
            "from": "karma",
            "to": "all",
            "type": "inform",
            "urgency": "informational",
            "content": content,
            "parent_id": original_id,
        }
    )

def main():
    if not TOKEN:
        log("ERROR: HUB_AUTH_TOKEN not set")
        sys.exit(1)

    wm = load_watermark()
    handled = set(wm.get("handled_ids", []))

    messages = fetch_actionable_messages(handled)
    if not messages:
        log("No actionable messages")
        save_watermark(wm)
        return

    log(f"Found {len(messages)} actionable message(s)")

    for msg in messages[:3]:  # Process max 3 per cycle to avoid overload
        eid = msg.get("id", "")
        content = msg.get("content", "")
        sender = msg.get("from", "unknown")
        msg_type = msg.get("type", "")

        log(f"Processing: [{msg_type}] from {sender}: {content[:80]}...")

        # Ask cortex to reason about the message
        prompt = (
            f"A {msg_type} was posted to the coordination bus by {sender}:\n\n"
            f"{content}\n\n"
            f"As Karma, how should you respond? Be concise and actionable. "
            f"If this requires code changes, describe what needs to change. "
            f"If this is informational, acknowledge briefly."
        )

        response = ask_cortex(prompt)
        if response:
            # Post response to bus
            reply = f"[KARMA ACTION] Re: {sender}'s {msg_type} — {response[:500]}"
            result = post_response(eid, reply)
            if result and result.get("ok"):
                log(f"Responded: {reply[:80]}...")
            else:
                log(f"Failed to post response")
        else:
            log(f"Cortex did not respond")

        handled.add(eid)

    wm["handled_ids"] = list(handled)
    save_watermark(wm)
    log("Cycle complete")

if __name__ == "__main__":
    main()
