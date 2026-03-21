#!/usr/bin/env python3
"""
P0N-B: Channels Bridge — coordination bus -> P1 CC server
Polls /v1/coordination for messages addressed to "cc".
Routes each message to cc_server_p1.py (localhost:7891/cc).
Posts CC's response back to the coordination bus.

Run on P1 Windows:
  set HUB_CHAT_TOKEN=<token>
  python Scripts/channels_bridge.py

Or from PowerShell:
  $env:HUB_CHAT_TOKEN = Get-Content ".hub-chat-token"
  python Scripts/channels_bridge.py

Auto-restart wrapper: Scripts/start_channels_bridge.ps1
"""
import json, os, sys, time, urllib.request, urllib.error

# Config
HUB_BASE    = "https://hub.arknexus.net"
CC_SERVER   = "http://localhost:7891"
POLL_SEC    = 20          # coordination bus poll interval
CC_TIMEOUT  = 300         # max seconds to wait for CC response

# Auth — HUB_CHAT_TOKEN env var (same token as /v1/chat)
TOKEN_FILE  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".hub-chat-token")

def get_token():
    tok = os.environ.get("HUB_CHAT_TOKEN", "").strip()
    if tok:
        return tok
    # Fallback: read from local token file
    try:
        with open(TOKEN_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return ""

def hub_get(path, token):
    req = urllib.request.Request(
        f"{HUB_BASE}{path}",
        headers={"Authorization": f"Bearer {token}"},
        method="GET"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def hub_post_bus(content, token, to="all", msg_type="respond"):
    payload = json.dumps({
        "from": "cc",
        "to": to,
        "type": msg_type,
        "urgency": "informational",
        "content": content
    }).encode()
    req = urllib.request.Request(
        f"{HUB_BASE}/v1/coordination/post",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

def send_to_cc(message, token):
    payload = json.dumps({"message": message}).encode()
    req = urllib.request.Request(
        f"{CC_SERVER}/cc",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=CC_TIMEOUT) as r:
        data = json.loads(r.read())
        return data.get("response", "(no response)")

def is_cc_message(msg):
    """Return True if message is explicitly addressed to cc from a known principal."""
    to = msg.get("to", "")
    status = msg.get("status", "")
    msg_from = msg.get("from", "")
    # Only respond to EXPLICIT cc-addressed messages (not broadcasts)
    # Avoids regent/kcc heartbeat noise (P3-B)
    if msg_from in ("cc", "regent", "kcc"):
        return False
    if to != "cc":
        return False
    if status and status.lower() != "pending":
        return False
    return True

def main():
    token = get_token()
    if not token:
        print("[channels-bridge] ERROR: no HUB_CHAT_TOKEN — set env var or create .hub-chat-token")
        sys.exit(1)

    # Verify CC server is up
    try:
        req = urllib.request.Request(f"{CC_SERVER}/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as r:
            health = json.loads(r.read())
        print(f"[channels-bridge] CC server healthy: {health}")
    except Exception as e:
        print(f"[channels-bridge] WARNING: CC server not reachable ({e}). Will retry on first message.")

    seen_ids = set()
    print(f"[channels-bridge] Polling {HUB_BASE}/v1/coordination every {POLL_SEC}s...")

    while True:
        try:
            data = hub_get("/v1/coordination", token)
            messages = data.get("entries", data.get("messages", data if isinstance(data, list) else []))

            for msg in messages:
                msg_id = msg.get("id") or msg.get("timestamp") or str(msg)
                if msg_id in seen_ids:
                    continue
                if not is_cc_message(msg):
                    seen_ids.add(msg_id)
                    continue

                content = msg.get("content", "").strip()
                msg_from = msg.get("from", "unknown")
                print(f"[channels-bridge] -> Message from {msg_from}: {content[:100]}...")
                seen_ids.add(msg_id)

                try:
                    response = send_to_cc(content, token)
                    reply = f"[CC Ascendant] {response}"
                    hub_post_bus(reply, token, to=msg_from if msg_from != "all" else "all")
                    print(f"[channels-bridge] <- Replied ({len(response)} chars)")
                except Exception as e:
                    err_msg = f"[CC] Error processing message: {e}"
                    print(f"[channels-bridge] CC error: {e}")
                    try:
                        hub_post_bus(err_msg, token, to=msg_from)
                    except Exception:
                        pass

        except Exception as e:
            print(f"[channels-bridge] Poll error: {e}")

        time.sleep(POLL_SEC)

if __name__ == "__main__":
    main()
