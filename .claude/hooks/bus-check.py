#!/usr/bin/env python3
"""
UserPromptSubmit hook — auto-fetch pending coordination bus messages for CC.

P114 enforcement: CC misses Karma/Sovereign messages unless manually told to check.
This hook runs before every user prompt and prepends any pending bus messages
addressed to CC, so CC reads them automatically.

Fetches from hub.arknexus.net/v1/coordination/recent?to=cc&status=pending&limit=5
Uses hub chat token from vault-neo via SSH.
"""
import json
import sys
import subprocess

HUB_URL = "https://hub.arknexus.net"

def get_token():
    try:
        r = subprocess.run(
            ["ssh", "-o", "ConnectTimeout=3", "-o", "BatchMode=yes", "vault-neo",
             "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"],
            capture_output=True, text=True, timeout=5
        )
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

def fetch_pending(token):
    import urllib.request
    url = f"{HUB_URL}/v1/coordination/recent?to=cc&status=pending&limit=5"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            entries = data.get("entries", [])
            # Filter out watchdog noise
            return [e for e in entries if "WATCHDOG ACK" not in e.get("content", "")]
    except Exception:
        return []

def main():
    token = get_token()
    if not token:
        return  # Silent fail — don't block user prompt

    pending = fetch_pending(token)
    if not pending:
        return  # No pending messages — nothing to inject

    lines = []
    for e in pending[:3]:  # Max 3 to avoid flooding context
        fr = e.get("from", "?")
        content = e.get("content", "")[:300]
        ts = e.get("created_at", "")[:16]
        lines.append(f"[BUS {ts}] {fr}: {content}")

    if lines:
        msg = "PENDING BUS MESSAGES FOR CC:\n" + "\n".join(lines) + "\nAddress these before proceeding."
        print(json.dumps({"message": msg}))

if __name__ == "__main__":
    main()
