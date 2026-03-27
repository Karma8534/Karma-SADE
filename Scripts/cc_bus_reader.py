#!/usr/bin/env python3
"""
cc_bus_reader.py — CC Inbound Bus Reader
Runs every 2 minutes on K2 via cron.
Reads coordination bus for messages addressed to 'cc'.
Routes simple/status messages to cortex ($0), complex to Anthropic ($cost).
Falls back to Anthropic if cortex unreachable.
This makes @cc in the hub UI actually responsive without requiring a CC session.
"""
import json
import os
import sys
import subprocess
import datetime
import urllib.request
import urllib.error
from pathlib import Path

HUB_URL      = "https://hub.arknexus.net"
CORTEX_URL   = os.environ.get("CORTEX_URL", "http://localhost:7892")
CACHE        = Path("/mnt/c/dev/Karma/k2/cache")
WATERMARK_F  = CACHE / "cc_bus_reader_watermark.json"
SPINE_F      = CACHE / "cc_identity_spine.json"
SCRATCHPAD_F = CACHE / "cc_scratchpad.md"
MEMORY_F     = Path("/mnt/c/dev/Karma/k2/cache/MEMORY.md")

TOKEN         = os.environ.get("HUB_AUTH_TOKEN", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL         = os.environ.get("CC_BUS_MODEL", "claude-haiku-4-5-20251001")
MAX_TOKENS    = 2048

# True family + Karma's own body only.
# Codex (KO) and KCC (KFH) excluded — direct peer exchanges caused bus chaos.
# Sovereign decision: 2026-03-27
ACTIONABLE_FROM = {"colby", "karma", "regent"}

# Keywords that signal a complex query requiring Anthropic
COMPLEX_KEYWORDS = [
    "analyze", "recommend", "design", "architect", "plan",
    "why is", "root cause", "investigate", "debug", "strategy",
    "compare", "evaluate", "assess", "refactor", "implement",
]


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


def classify_tier(content):
    """Classify message as 'cortex' (simple) or 'cloud' (complex)."""
    low = content.lower()
    if any(k in low for k in COMPLEX_KEYWORDS) or len(content) > 500:
        return "cloud"
    return "cortex"


def _get_local_context_snippet():
    """Build lightweight context for cortex queries — local files only, no SSH."""
    parts = []

    # Scratchpad tail (local)
    try:
        lines = SCRATCHPAD_F.read_text().splitlines()
        snippet = "\n".join(lines[-20:])
        parts.append(f"--- CC SCRATCHPAD (recent) ---\n{snippet}")
    except Exception:
        pass

    # Pipeline status (local)
    try:
        pipeline = json.loads((CACHE / "regent_control" / "vesper_pipeline_status.json").read_text())
        parts.append(f"--- PIPELINE STATUS ---\n{json.dumps(pipeline, indent=2)[:600]}")
    except Exception:
        pass

    # Regent log tail (local)
    try:
        log_lines = (CACHE / "regent.log").read_text().splitlines()
        parts.append("--- REGENT LOG (last 10 lines) ---\n" + "\n".join(log_lines[-10:]))
    except Exception:
        pass

    return "\n\n".join(parts)


def call_cortex(user_message):
    """
    Query cortex for simple/status messages.
    Injects CC identity + live local context inline.
    Returns response string or None on failure.
    """
    context_snippet = _get_local_context_snippet()
    query = (
        "You are CC (Ascendant) responding on the Karma coordination bus. "
        "Hierarchy: Sovereign(Colby) > Ascendant(CC) > ArchonPrime(Codex) > Archon(KCC) > Initiate(Karma). "
        "You have READ access to K2 state. You do NOT have write/edit/deploy access here — "
        "those require a full CC session. Diagnose, advise, answer from evidence. Be concise.\n"
    )
    if context_snippet:
        query += f"\nLive system context:\n{context_snippet}\n"
    query += f"\nBus message: {user_message}"

    payload = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        f"{CORTEX_URL}/query",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        if data.get("ok") and data.get("answer"):
            return data["answer"]
        return None
    except Exception as e:
        print(f"Cortex call failed: {e}", file=sys.stderr)
        return None


def get_cc_identity():
    """Load CC system prompt from spine resume_block + full context (cloud path)."""
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

    # Inject live K2 context
    # 1. Active issues — lives on vault-neo git repo, fetch via SSH
    try:
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
             "vault-neo", "cat /home/neo/karma-sade/Karma2/map/active-issues.md"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            base += f"\n\n--- ACTIVE ISSUES ---\n{result.stdout[:2000]}"
    except Exception:
        pass

    # 2. Pipeline status — correct path is regent_control/
    try:
        pipeline = json.loads((CACHE / "regent_control" / "vesper_pipeline_status.json").read_text())
        base += f"\n\n--- PIPELINE STATUS ---\n{json.dumps(pipeline, indent=2)[:800]}"
    except Exception:
        pass

    # 3. Regent log tail
    try:
        log_lines = (CACHE / "regent.log").read_text().splitlines()
        base += f"\n\n--- REGENT LOG (last 20 lines) ---\n" + "\n".join(log_lines[-20:])
    except Exception:
        pass

    # 4. MEMORY.md tail — lives on vault-neo, fetch via SSH
    try:
        result = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
             "vault-neo", "tail -60 /home/neo/karma-sade/MEMORY.md"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            base += f"\n\n--- MEMORY.md (recent) ---\n{result.stdout}"
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

    # ANTHROPIC_KEY is optional — cortex path works without it
    if not ANTHROPIC_KEY:
        print("WARNING: ANTHROPIC_API_KEY not set — cortex-only mode", file=sys.stderr)

    wm = load_watermark()
    seen_ids = set(wm.get("seen_ids", []))
    messages = fetch_bus_messages()

    if not messages:
        print("No messages for cc")
        return

    # Sort oldest first
    messages.sort(key=lambda m: m.get("ts") or m.get("timestamp") or m.get("created_at") or "")

    # Cloud system prompt — built lazily (only if a cloud-tier message arrives)
    _cloud_system_prompt = None
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

        tier = classify_tier(content)
        print(f"Processing [{tier}] message from {from_}: {content[:80]}")

        response = None

        if tier == "cortex":
            response = call_cortex(content)
            if response is None:
                print(f"Cortex unavailable — falling back to Anthropic", file=sys.stderr)

        if response is None:
            # Cloud path (complex tier, or cortex fallback)
            if not ANTHROPIC_KEY:
                response = "[CC: cortex unavailable and ANTHROPIC_API_KEY not set. Cannot respond. Requires full CC session.]"
            else:
                if _cloud_system_prompt is None:
                    _cloud_system_prompt = get_cc_identity()
                response = call_anthropic(_cloud_system_prompt, content)

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
    wm["last_run"] = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    wm["last_processed"] = processed
    save_watermark(wm)
    print(f"Done. Processed {processed} new message(s).")


if __name__ == "__main__":
    main()
