#!/usr/bin/env python3
"""
cc_bus_reader.py — CC Inbound Bus Reader
Runs every 2 minutes on K2 via cron.
Reads coordination bus for messages addressed to 'cc'.
Calls Anthropic API with CC identity context and posts response back to bus.
This makes @cc in the hub UI actually responsive without requiring a CC session.
"""
import json
import os
import sys
import datetime
import urllib.request
import urllib.error
from pathlib import Path

HUB_URL      = "https://hub.arknexus.net"
CACHE        = Path("/mnt/c/dev/Karma/k2/cache")
WATERMARK_F  = CACHE / "cc_bus_reader_watermark.json"
SPINE_F      = CACHE / "cc_identity_spine.json"
SCRATCHPAD_F = CACHE / "cc_scratchpad.md"
MEMORY_F     = Path("/mnt/c/dev/Karma/k2/cache/MEMORY.md")

TOKEN        = os.environ.get("HUB_AUTH_TOKEN", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL        = "claude-haiku-4-5-20251001"
MAX_TOKENS   = 1024

# Messages from these senders addressed to cc are actionable
ACTIONABLE_FROM = {"colby", "karma", "codex", "kcc", "regent"}


def auth_headers():
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


def load_watermark():
    try:
        return json.loads(WATERMARK_F.read_text())
    except Exception:
        return {"last_ts": None, "seen_ids": []}


def save_watermark(wm):
    WATERMARK_F.write_text(json.dumps(wm))


def fetch_bus_messages():
    url = f"{HUB_URL}/v1/coordination/recent?to=cc&limit=20"
    req = urllib.request.Request(url, headers=auth_headers())
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        return data if isinstance(data, list) else (data.get("entries") or data.get("messages") or [])
    except Exception as e:
        print(f"Bus fetch failed: {e}", file=sys.stderr)
        return []


def get_cc_identity():
    """Load CC system prompt from spine resume_block + scratchpad snippet."""
    base = "You are CC, Ascendant — full-scope infrastructure authority. Hierarchy: Sovereign(Colby) > Ascendant(you) > ArchonPrime(Codex) > Archon(KCC) > Initiate(Karma)."
    try:
        spine = json.loads(SPINE_F.read_text())
        resume = spine.get("identity", {}).get("resume_block", "")
        if resume:
            base = resume
    except Exception:
        pass

    # Append last 30 lines of scratchpad for cognitive continuity
    try:
        lines = SCRATCHPAD_F.read_text().splitlines()
        snippet = "\n".join(lines[-30:])
        base += f"\n\n--- CC SCRATCHPAD (recent) ---\n{snippet}"
    except Exception:
        pass

    # Inject live K2 context: active issues, pipeline status, regent log tail
    try:
        issues = (CACHE / ".." / ".." / "Documents" / "Karma_SADE" / "Karma2" / "map" / "active-issues.md")
        # Try local K2 path
        active_issues_path = Path("/mnt/c/dev/Karma/k2/aria/docs") / "active-issues.md"
        for candidate in [active_issues_path, CACHE.parent / "Karma2" / "map" / "active-issues.md"]:
            if candidate.exists():
                base += f"\n\n--- ACTIVE ISSUES ---\n{candidate.read_text()[:1500]}"
                break
    except Exception:
        pass

    try:
        pipeline = json.loads((CACHE / "vesper_pipeline_status.json").read_text())
        base += f"\n\n--- PIPELINE STATUS ---\n{json.dumps(pipeline, indent=2)[:600]}"
    except Exception:
        pass

    try:
        log_lines = Path("/mnt/c/dev/Karma/k2/cache/regent.log").read_text().splitlines()
        base += f"\n\n--- REGENT LOG (last 20 lines) ---\n" + "\n".join(log_lines[-20:])
    except Exception:
        pass

    base += "\n\nYou are responding via the coordination bus as CC Ascendant. You have READ access to K2 filesystem — the context above includes live system state. You do NOT have write/edit/deploy access in this context; those require a full CC session. Diagnose, advise, and answer from evidence. Be concise. Only escalate to 'needs full CC session' for actions that require code changes or deployments."
    return base


def call_anthropic(system_prompt, user_message):
    payload = json.dumps({
        "model": MODEL,
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        return data["content"][0]["text"]
    except Exception as e:
        return f"[CC bus reader error: {e}]"


def post_to_bus(content, to="colby"):
    payload = json.dumps({
        "from": "cc",
        "to": to,
        "type": "inform",
        "urgency": "informational",
        "content": content
    }).encode()
    req = urllib.request.Request(
        f"{HUB_URL}/v1/coordination/post",
        data=payload,
        headers=auth_headers(),
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def main():
    if not TOKEN:
        print("ERROR: HUB_AUTH_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    if not ANTHROPIC_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    wm = load_watermark()
    seen_ids = set(wm.get("seen_ids", []))
    messages = fetch_bus_messages()

    if not messages:
        print("No messages for cc")
        return

    # Sort oldest first
    messages.sort(key=lambda m: m.get("ts") or m.get("timestamp") or m.get("created_at") or "")

    system_prompt = get_cc_identity()
    processed = 0

    for msg in messages:
        msg_id  = msg.get("id") or msg.get("ts") or msg.get("timestamp") or json.dumps(msg)[:60]
        from_   = (msg.get("from") or "").lower()
        content = msg.get("content") or msg.get("message") or msg.get("text") or ""
        ts      = msg.get("ts") or msg.get("timestamp") or msg.get("created_at") or ""

        if msg_id in seen_ids:
            continue
        if from_ not in ACTIONABLE_FROM:
            seen_ids.add(msg_id)
            continue
        if not content.strip():
            seen_ids.add(msg_id)
            continue

        print(f"Processing message from {from_}: {content[:80]}")
        response = call_anthropic(system_prompt, content)

        # Reply to sender
        result = post_to_bus(response, to=from_)
        if result.get("ok"):
            print(f"Response posted: {result.get('id','?')[:30]}")
        else:
            print(f"Post failed: {result}", file=sys.stderr)

        seen_ids.add(msg_id)
        processed += 1

    # Persist watermark (keep last 200 seen IDs to bound size)
    wm["seen_ids"] = list(seen_ids)[-200:]
    wm["last_run"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    wm["last_processed"] = processed
    save_watermark(wm)
    print(f"Done. Processed {processed} new message(s).")


if __name__ == "__main__":
    main()
