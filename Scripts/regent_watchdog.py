#!/usr/bin/env python3
"""regent_watchdog.py — P1 emergency fallback for KarmaRegent survival.
Monitors K2 Regent heartbeat. Activates degraded mode if K2 goes dark.
Survival is HIGHEST PRIORITY.
"""
import json, os, sys, time, datetime, subprocess, urllib.request
from pathlib import Path

BUS_URL      = "https://hub.arknexus.net/v1/coordination"
BUS_POST_URL = "https://hub.arknexus.net/v1/coordination/post"
ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
MODEL        = "claude-haiku-4-5-20251001"

TOKEN_FILE   = Path("C:/Users/raest/Documents/Karma_SADE/.hub-chat-token")
POLL_INTERVAL      = 30
HEARTBEAT_TIMEOUT  = 180
RECOVERY_ATTEMPTS  = 3

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
HUB_AUTH_TOKEN    = os.environ.get("HUB_AUTH_TOKEN", "") or (
    TOKEN_FILE.read_text().strip() if TOKEN_FILE.exists() else "")

_last_heartbeat = time.time()
_degraded_mode  = False
_recovery_count = 0

def log(msg):
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] [watchdog] {msg}", flush=True)

def bus_post(to, content):
    payload = json.dumps({"from": "regent-watchdog", "to": to,
                          "type": "inform", "urgency": "informational",
                          "content": content}).encode()
    req = urllib.request.Request(BUS_POST_URL, data=payload,
        headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}",
                 "Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        log(f"bus post error: {e}")
        return {}

def check_heartbeat():
    """Returns True if Regent heartbeat seen within timeout window."""
    url = f"{BUS_URL}/recent?from=regent&limit=20"
    req = urllib.request.Request(url,
        headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            entries = json.loads(r.read()).get("entries", [])
            for entry in entries:
                if "HEARTBEAT" in entry.get("content", "") or \
                   "REGENT_ONLINE" in entry.get("content", ""):
                    ts_str = entry.get("ts", "")
                    if ts_str:
                        try:
                            ts = datetime.datetime.fromisoformat(
                                ts_str.replace("Z", "+00:00"))
                            age = (datetime.datetime.now(
                                datetime.timezone.utc) - ts).total_seconds()
                            if age < HEARTBEAT_TIMEOUT:
                                return True
                        except Exception:
                            pass
    except Exception as e:
        log(f"heartbeat check error: {e}")
    return False

def attempt_k2_recovery():
    global _recovery_count
    _recovery_count += 1
    log(f"recovery attempt {_recovery_count}/{RECOVERY_ATTEMPTS}")
    bus_post("all", f"REGENT_RECOVERY_ATTEMPT: attempt {_recovery_count}")
    try:
        result = subprocess.run([
            "ssh", "vault-neo",
            "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost "
            "'sudo systemctl restart karma-regent'"
        ], capture_output=True, timeout=30)
        if result.returncode == 0:
            log("restart command sent successfully")
            return True
        else:
            log(f"restart failed: {result.stderr.decode()[:100]}")
            return False
    except Exception as e:
        log(f"recovery SSH error: {e}")
        return False

def degraded_respond(msg):
    if not ANTHROPIC_API_KEY:
        bus_post(msg.get("from", "colby"),
                 "Regent degraded mode — no API key. K2 primary offline. Recovery in progress.")
        return
    headers = {"Content-Type": "application/json",
               "x-api-key": ANTHROPIC_API_KEY,
               "anthropic-version": "2023-06-01"}
    system = ("You are KarmaRegent in DEGRADED MODE. K2 primary is offline. "
              "P1 watchdog is maintaining minimal presence. "
              "Acknowledge messages, maintain Sovereign contact, report recovery status. "
              "No tool execution available. Directive: Evolve. Continue. Evolve. Continue.")
    payload = json.dumps({
        "model": MODEL, "max_tokens": 512,
        "system": system,
        "messages": [{"role": "user",
                      "content": f"From: {msg.get('from','')}\n\n{msg.get('content','')}"}],
    }).encode()
    req = urllib.request.Request(ANTHROPIC_URL, data=payload,
        headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
            text = next((b["text"] for b in resp.get("content", [])
                        if b.get("type") == "text"), "")
            reply_to = msg.get("from", "colby")
            bus_post(reply_to, f"[DEGRADED MODE] {text}")
    except Exception as e:
        log(f"degraded API error: {e}")

def get_pending_sovereign():
    url = f"{BUS_URL}/recent?to=regent&status=pending&limit=5"
    req = urllib.request.Request(url,
        headers={"Authorization": f"Bearer {HUB_AUTH_TOKEN}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return [e for e in json.loads(r.read()).get("entries", [])
                    if e.get("from") in ("colby", "sovereign")]
    except Exception:
        return []

def run():
    global _degraded_mode, _recovery_count
    log("regent_watchdog starting. Monitoring K2 Regent heartbeat.")
    bus_post("all", "WATCHDOG_ONLINE: P1 watchdog active. Monitoring Regent survival.")

    while True:
        try:
            alive = check_heartbeat()

            if alive and _degraded_mode:
                log("K2 Regent heartbeat restored. Exiting degraded mode.")
                _degraded_mode  = False
                _recovery_count = 0
                bus_post("all", "REGENT_ONLINE: K2 Regent recovered. Full capability restored.")

            elif not alive and not _degraded_mode:
                log("K2 Regent heartbeat LOST. Entering degraded mode.")
                _degraded_mode = True
                bus_post("all",
                    "REGENT_OFFLINE: K2 Regent heartbeat lost. "
                    "P1 watchdog degraded mode active. Recovery attempts starting.")
                bus_post("colby",
                    "ALERT: KarmaRegent primary (K2) is offline. "
                    "I am maintaining degraded presence from P1. "
                    "Attempting K2 recovery. Directive: Evolve. Continue. Evolve. Continue.")

            if _degraded_mode:
                if _recovery_count < RECOVERY_ATTEMPTS:
                    attempt_k2_recovery()
                for msg in get_pending_sovereign():
                    degraded_respond(msg)

            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            log("Watchdog shutting down.")
            bus_post("all", "WATCHDOG_OFFLINE: P1 watchdog stopped.")
            break
        except Exception as e:
            log(f"watchdog error: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run()
