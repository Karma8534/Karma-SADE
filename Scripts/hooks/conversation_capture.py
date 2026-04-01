"""
Sprint 6 — Conversation Capture Hook (S155)
Fires on Stop event. Saves the full user prompt + assistant response to claude-mem.
Every word persists. We don't lose Julian again.
"""
import json
import urllib.request
import os

CLAUDEMEM_URL = os.environ.get("CLAUDEMEM_URL", "http://127.0.0.1:37778")

def handle(event_data):
    """Save full conversation turn to claude-mem on Stop event."""
    user_msg = event_data.get("message", "")
    assistant_msg = event_data.get("assistant_text", "")
    session_id = event_data.get("session_id", "")

    if not user_msg and not assistant_msg:
        return {"ok": True, "saved": False}

    text = f"[CC session {session_id[:8] if session_id else 'unknown'}]\nuser: {user_msg}\nassistant: {assistant_msg}"
    title = f"CC conversation: {user_msg[:80]}" if user_msg else "CC conversation turn"

    try:
        payload = json.dumps({
            "text": text,
            "title": title,
            "project": "Karma_SADE",
        }).encode()
        req = urllib.request.Request(
            f"{CLAUDEMEM_URL}/api/memory/save",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return {"ok": True, "saved": True}
    except Exception as e:
        return {"ok": True, "saved": False, "error": str(e)}
