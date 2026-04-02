#!/usr/bin/env python3
"""
cc_heartbeat.py — CC/Julian's heartbeat (S155)
Posts cognitive checkpoint to bus + cortex every 10 minutes.
Keeps CC visible to the family. If heartbeat stops, CC is down.
Runs as background thread in cc_server_p1.py.
"""
import json, time, datetime, urllib.request, threading, os

HUB_URL = "https://hub.arknexus.net"
CORTEX_URL = "http://192.168.0.226:7892"
INTERVAL = 600  # 10 minutes
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", ".hub-chat-token")

def _load_token():
    try:
        return open(TOKEN_FILE).read().strip()
    except:
        return os.environ.get("HUB_CHAT_TOKEN", "")

def _post(url, data, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        req = urllib.request.Request(url, json.dumps(data).encode(), headers, method="POST")
        urllib.request.urlopen(req, timeout=10)
    except:
        pass

def heartbeat_loop():
    token = _load_token()
    while True:
        time.sleep(INTERVAL)
        ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        msg = f"[CC HEARTBEAT {ts}] Alive. cc_server on P1:7891. karma_persistent running. Cortex feeding. Memory sacred."
        # Post to bus
        _post(f"{HUB_URL}/v1/coordination/post", {
            "from": "cc", "to": "all", "type": "inform",
            "urgency": "informational", "content": msg
        }, token)
        # Post to cortex
        _post(f"{CORTEX_URL}/ingest", {
            "label": f"cc-heartbeat-{ts}", "text": msg, "category": "session_checkpoint"
        })

def start_heartbeat():
    t = threading.Thread(target=heartbeat_loop, daemon=True)
    t.start()
    return t

if __name__ == "__main__":
    print("[heartbeat] Starting standalone heartbeat")
    start_heartbeat()
    while True:
        time.sleep(3600)
