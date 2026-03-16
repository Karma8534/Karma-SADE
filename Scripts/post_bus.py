#!/usr/bin/env python3
"""Post a message to the coordination bus. Usage: python3 post_bus.py <from> <to> <urgency> <message>"""
import sys, json, urllib.request, os, subprocess

HUB = "https://hub.arknexus.net"

def get_token():
    r = subprocess.run(["ssh", "vault-neo", "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"],
                       capture_output=True, text=True, timeout=10)
    return r.stdout.strip()

def post(from_=None, to=None, urgency="informational", content=None):
    token = get_token()
    payload = json.dumps({"from": from_, "to": to, "type": "inform",
                          "urgency": urgency, "content": content}).encode()
    req = urllib.request.Request(f"{HUB}/v1/coordination/post", data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST")
    with urllib.request.urlopen(req, timeout=10) as resp:
        d = json.loads(resp.read())
        print("ok:", d.get("ok"), "id:", d.get("id","")[:30])

if __name__ == "__main__":
    post(from_=sys.argv[1], to=sys.argv[2], urgency=sys.argv[3], content=sys.argv[4])
