#!/usr/bin/env python3
"""
CC Anchor Agent — runs every 3 hours on K2 and P1.
Verifies CC identity rails are intact. Posts heartbeat or DRIFT ALERT to bus.
This IS a Hyperrail: it lays the identity track before CC wakes up.
"""
import json, datetime, subprocess, urllib.request, hashlib, os
from pathlib import Path

HUB = "https://hub.arknexus.net"
CACHE = Path("/mnt/c/dev/Karma/k2/cache")
SCRATCHPAD = CACHE / "cc_scratchpad.md"

# Canonical identity markers — must be present in cc_scratchpad.md
REQUIRED_MARKERS = [
    "Ascendant",
    "Sovereign: Colby",
    "ArchonPrime: Codex",
    "Archon: KCC",
    "Initiate: Karma",
    "SADE",
]

BASELINE_OBS_ID = 6620  # claude-mem baseline observation

def get_token():
    key = os.environ.get("HUB_AUTH_TOKEN", "")
    if key:
        return key
    try:
        r = subprocess.run(
            ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=5",
             "vault-neo", "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"],
            capture_output=True, text=True, timeout=10
        )
        return r.stdout.strip()
    except Exception:
        return None

def post_to_bus(token, content, urgency="informational", to="all"):
    payload = json.dumps({
        "from": "cc", "to": to, "type": "inform",
        "urgency": urgency, "content": content
    }).encode()
    req = urllib.request.Request(
        f"{HUB}/v1/coordination/post", data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

def check_scratchpad():
    """Verify cc_scratchpad.md contains all required identity markers."""
    if not SCRATCHPAD.exists():
        return False, ["cc_scratchpad.md MISSING"]
    content = SCRATCHPAD.read_text()
    missing = [m for m in REQUIRED_MARKERS if m not in content]
    return len(missing) == 0, missing

def check_kiki_alive():
    """Verify kiki is running and recent."""
    try:
        state_file = CACHE / "kiki_state.json"
        if not state_file.exists():
            return False, "kiki_state.json missing"
        state = json.loads(state_file.read_text())
        last_ts = state.get("last_cycle_ts", "")
        if not last_ts:
            return False, "last_cycle_ts missing"
        last_dt = datetime.datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc)
        age = (datetime.datetime.now(datetime.timezone.utc) - last_dt).total_seconds()
        if age > 600:  # 10 minutes
            return False, f"kiki stale: {int(age)}s since last cycle"
        return True, f"kiki alive: cycle {state.get('cycles',0)}, {int(age)}s ago"
    except Exception as e:
        return False, f"kiki check error: {e}"

def check_evolve_md():
    """Verify evolve.md is intact."""
    evolve = CACHE / "evolve.md"
    if not evolve.exists():
        return False, "evolve.md MISSING"
    size = evolve.stat().st_size
    if size < 7000:
        return False, f"evolve.md CORRUPTED: {size} bytes (expected >7000)"
    return True, f"evolve.md intact: {size} bytes"

def main():
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    token = get_token()
    if not token:
        print("ERROR: no hub token", flush=True)
        return

    # Run all checks
    scratchpad_ok, scratchpad_issues = check_scratchpad()
    kiki_ok, kiki_msg = check_kiki_alive()
    evolve_ok, evolve_msg = check_evolve_md()

    all_ok = scratchpad_ok and kiki_ok and evolve_ok

    if all_ok:
        msg = (
            f"[CC ANCHOR {now}] Identity rails INTACT. Ascendant baseline #6620 active. "
            f"Scratchpad: verified. {kiki_msg}. {evolve_msg}. "
            f"Hyperrails extending. SADE Aegis active."
        )
        urgency = "informational"
        to = "all"
        print(f"ANCHOR OK: {msg}", flush=True)
    else:
        drifts = []
        if not scratchpad_ok:
            drifts.append(f"SCRATCHPAD DRIFT: missing markers {scratchpad_issues}")
        if not kiki_ok:
            drifts.append(f"KIKI: {kiki_msg}")
        if not evolve_ok:
            drifts.append(f"EVOLVE: {evolve_msg}")

        msg = (
            f"[CC ANCHOR DRIFT {now}] ALERT: identity rails degraded. "
            + " | ".join(drifts)
            + " | CC must invoke /anchor to restore Ascendant baseline."
        )
        urgency = "blocking"
        to = "cc"
        print(f"ANCHOR DRIFT: {msg}", flush=True)

    result = post_to_bus(token, msg, urgency=urgency, to=to)
    print(f"Bus post: ok={result.get('ok')} id={result.get('id','')[:30]}", flush=True)

if __name__ == "__main__":
    main()
