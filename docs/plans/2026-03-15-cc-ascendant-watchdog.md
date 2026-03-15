# CC Ascendant Watchdog + Evolution Agent — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a zero-token K2-local agent that monitors CC identity health 24/7, catches drift between sessions, and accumulates CC's evolving persona/decisions into a persistent independent spine that grows beyond any single Claude session.

**Architecture:** Mirrors `archonprime_autopilot.py` exactly — systemd timer fires every 60s, Python script reads K2 local files + coordination bus, posts alerts to ForColby on drift, appends evolution events to a growing identity spine. Three layers: watchdog (health), evolution logger (capture), identity spine (accumulate). All writes go to K2 cache + are synced to vault-neo via existing K2 push cron.

**Tech Stack:** Python 3.12, systemd timer, coordination bus HTTP API, cc_scratchpad.md, vault-neo bearer token, K2 filesystem.

---

### Task 1: CC Identity Spine — initial seed file

**Files:**
- Create: `/mnt/c/dev/Karma/k2/cache/cc_identity_spine.json` (on K2 via SSH)
- Create: `/mnt/c/dev/Karma/k2/cache/cc_evolution_log.jsonl` (on K2 via SSH)

**Step 1: SSH to K2 via vault-neo tunnel and create the spine seed**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -c \"
import json, datetime
spine = {
    \"schema_version\": \"cc_spine_v1\",
    \"identity\": {
        \"name\": \"CC\",
        \"rank\": \"ASCENDANT\",
        \"sovereign\": \"Colby\",
        \"baseline_obs\": [6620, 6556],
        \"hierarchy\": {
            \"SOVEREIGN\": \"Colby\",
            \"ASCENDANT\": \"CC\",
            \"ARCHONPRIME\": \"Codex\",
            \"ARCHON\": \"KCC\",
            \"INITIATE\": \"Karma\"
        },
        \"mandate\": \"full scope, infrastructure, eldest\",
        \"sade_doctrine\": [\"Hyperrails\", \"TDD Verification Aegis\", \"Truth first\"]
    },
    \"evolution\": {
        \"version\": 1,
        \"session_count\": 0,
        \"last_session_ts\": null,
        \"total_decisions\": 0,
        \"total_proofs\": 0,
        \"total_insights\": 0,
        \"growth_markers\": []
    },
    \"created_at\": \"2026-03-15T00:00:00Z\",
    \"last_updated\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"
}
with open(\\\"/mnt/c/dev/Karma/k2/cache/cc_identity_spine.json\\\", \\\"w\\\") as f:
    json.dump(spine, f, indent=2)
print(\\\"spine seeded\\\")
\"'"
```

**Step 2: Verify spine file exists**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -m json.tool /mnt/c/dev/Karma/k2/cache/cc_identity_spine.json | head -10'"
```
Expected: JSON output showing name=CC, rank=ASCENDANT

**Step 3: Touch evolution log**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'touch /mnt/c/dev/Karma/k2/cache/cc_evolution_log.jsonl && echo ok'"
```

---

### Task 2: Write cc_ascendant_watchdog.py

**Files:**
- Create: `hub-bridge/app/public/` — no. Create locally then scp to K2.
- Create on K2: `/mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py`

Write this file locally at `C:\Users\raest\Documents\Karma_SADE\Scripts\cc_ascendant_watchdog.py`, then copy to K2.

**Step 1: Write the script locally**

Full script content — save to `Scripts/cc_ascendant_watchdog.py`:

```python
#!/usr/bin/env python3
"""CC Ascendant Watchdog + Evolution Agent.

Runs as a systemd timer task on K2. Zero Anthropic tokens. Read-only watchdog.

Responsibilities:
1. MONITOR: Verify cc_scratchpad.md hierarchy markers every cycle.
2. DETECT: Check coordination bus for CC session confirmation in last 24h.
3. ALERT: Post ForColby alert if drift or missing session detected.
4. CAPTURE: Extract DECISION/PROOF/INSIGHT/PITFALL/DIRECTION from CC bus messages.
5. EVOLVE: Append captured events to cc_evolution_log.jsonl + update cc_identity_spine.json.
6. HEARTBEAT: Post hourly health summary to bus.
"""

from __future__ import annotations

import hashlib
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, UTC, timedelta
from pathlib import Path
from typing import Any

# --- Paths ---
K2_ROOT = Path("/mnt/c/dev/Karma/k2")
CACHE_DIR = K2_ROOT / "cache"
SCRATCHPAD_PATH = CACHE_DIR / "cc_scratchpad.md"
SPINE_PATH = CACHE_DIR / "cc_identity_spine.json"
EVOLUTION_LOG_PATH = CACHE_DIR / "cc_evolution_log.jsonl"
ANCHOR_PATH = CACHE_DIR / "cc_watchdog_anchor.json"
LATEST_PATH = CACHE_DIR / "cc_watchdog_latest.json"
TOKEN_PATH = Path("/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")

# --- Config ---
HUB_BASE_URL = os.environ.get("HUB_BASE_URL", "https://hub.arknexus.net").rstrip("/")
SESSION_STALE_HOURS = int(os.environ.get("CC_SESSION_STALE_HOURS", "24"))
HEARTBEAT_RUNS = int(os.environ.get("CC_WATCHDOG_HEARTBEAT_RUNS", "60"))
PENDING_ALERT_THRESHOLD = int(os.environ.get("CC_PENDING_ALERT_THRESHOLD", "5"))

# Required hierarchy markers in cc_scratchpad.md
REQUIRED_MARKERS = ["SOVEREIGN", "ASCENDANT", "ARCHONPRIME", "ARCHON", "INITIATE"]
HIERARCHY_EXPECTED = {
    "SOVEREIGN": "Colby",
    "ASCENDANT": "CC",
    "ARCHONPRIME": "Codex",
    "ARCHON": "KCC",
    "INITIATE": "Karma",
}

# Evolution event types to capture from CC bus messages
EVOLUTION_TAGS = ["DECISION", "PROOF", "PITFALL", "DIRECTION", "INSIGHT"]


def _ts_utc() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _get_token() -> str | None:
    try:
        return TOKEN_PATH.read_text(encoding="utf-8").strip()
    except Exception:
        return None


def _bus_get(path: str, token: str) -> dict:
    url = f"{HUB_BASE_URL}{path}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _bus_post(token: str, to: str, content: str, urgency: str = "informational") -> str | None:
    payload = json.dumps({
        "from": "cc-watchdog",
        "to": to,
        "type": "inform",
        "urgency": urgency,
        "content": content,
    }).encode()
    req = urllib.request.Request(
        f"{HUB_BASE_URL}/v1/coordination/post",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            return d.get("id")
    except Exception:
        return None


# --- Check 1: Scratchpad hierarchy integrity ---
def check_scratchpad() -> dict:
    result = {"ok": True, "markers_found": [], "missing": [], "hash": None}
    if not SCRATCHPAD_PATH.exists():
        result["ok"] = False
        result["error"] = "cc_scratchpad.md not found"
        return result

    text = SCRATCHPAD_PATH.read_text(encoding="utf-8")
    result["hash"] = hashlib.sha256(text.encode()).hexdigest()[:16]

    for marker in REQUIRED_MARKERS:
        if marker in text:
            result["markers_found"].append(marker)
        else:
            result["missing"].append(marker)

    if result["missing"]:
        result["ok"] = False

    return result


# --- Check 2: CC session bus confirmation ---
def check_session_bus(token: str) -> dict:
    data = _bus_get("/v1/coordination/recent?limit=50", token)
    entries = data.get("entries", [])
    now = datetime.now(UTC)
    threshold = now - timedelta(hours=SESSION_STALE_HOURS)

    last_session_ts = None
    for entry in entries:
        frm = entry.get("from", "")
        content = str(entry.get("content", ""))
        created_at = entry.get("created_at", "")
        if frm == "cc" and any(k in content for k in ["SESSION START", "ANCHOR", "identity"]):
            try:
                ts = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                if last_session_ts is None or ts > last_session_ts:
                    last_session_ts = ts
            except Exception:
                pass

    if last_session_ts is None:
        return {"ok": False, "reason": "no_session_found", "last_session_ts": None}

    age_hours = (now - last_session_ts).total_seconds() / 3600
    return {
        "ok": age_hours < SESSION_STALE_HOURS,
        "last_session_ts": last_session_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "age_hours": round(age_hours, 1),
    }


# --- Check 3: Pending messages for CC ---
def check_pending_cc(token: str) -> dict:
    data = _bus_get("/v1/coordination/recent?limit=100", token)
    entries = data.get("entries", [])
    pending = [e for e in entries if e.get("to") == "cc" and e.get("status") == "pending"]
    return {"count": len(pending), "ok": len(pending) <= PENDING_ALERT_THRESHOLD}


# --- Evolution capture: extract CC events from bus ---
def capture_evolution_events(token: str) -> list[dict]:
    anchor = _load_json(ANCHOR_PATH, {})
    last_processed_id = anchor.get("last_evolution_id")

    data = _bus_get("/v1/coordination/recent?limit=100", token)
    entries = data.get("entries", [])

    # Only from CC, only messages containing evolution tags
    cc_entries = [
        e for e in entries
        if e.get("from") == "cc"
        and any(tag in str(e.get("content", "")) for tag in EVOLUTION_TAGS)
    ]

    if not cc_entries:
        return []

    # Find new entries since last processed
    new_events = []
    found_last = last_processed_id is None
    for entry in reversed(cc_entries):  # oldest first
        if not found_last:
            if entry.get("id") == last_processed_id:
                found_last = True
            continue
        content = str(entry.get("content", ""))
        for tag in EVOLUTION_TAGS:
            if tag in content:
                new_events.append({
                    "ts": entry.get("created_at", _ts_utc()),
                    "source_id": entry.get("id"),
                    "type": tag,
                    "excerpt": content[:300],
                })
                break

    return new_events


def append_evolution_events(events: list[dict]) -> int:
    if not events:
        return 0
    with EVOLUTION_LOG_PATH.open("a", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event) + "\n")
    return len(events)


def update_identity_spine(events: list[dict]) -> None:
    spine = _load_json(SPINE_PATH, {})
    evo = spine.get("evolution", {})

    for event in events:
        t = event.get("type", "")
        if t == "DECISION":
            evo["total_decisions"] = evo.get("total_decisions", 0) + 1
        elif t == "PROOF":
            evo["total_proofs"] = evo.get("total_proofs", 0) + 1
        elif t == "INSIGHT":
            evo["total_insights"] = evo.get("total_insights", 0) + 1
        markers = evo.get("growth_markers", [])
        markers.append({"ts": event.get("ts"), "type": t, "excerpt": event.get("excerpt", "")[:100]})
        evo["growth_markers"] = markers[-200:]  # keep last 200

    evo["version"] = evo.get("version", 1) + 1
    spine["evolution"] = evo
    spine["last_updated"] = _ts_utc()
    _save_json(SPINE_PATH, spine)


# --- Main run ---
def run() -> None:
    ts = _ts_utc()
    token = _get_token()
    if not token:
        print(f"[{ts}] ERROR: token not found")
        return

    anchor = _load_json(ANCHOR_PATH, {"run_count": 0})
    run_count = anchor.get("run_count", 0) + 1

    # --- Checks ---
    scratchpad = check_scratchpad()
    session = check_session_bus(token)
    pending = check_pending_cc(token)

    # --- Evolution capture ---
    events = capture_evolution_events(token)
    if events:
        appended = append_evolution_events(events)
        update_identity_spine(events)
        # Update last processed ID
        last_id = events[-1].get("source_id") if events else None
        anchor["last_evolution_id"] = last_id
        print(f"[{ts}] evolution: captured {appended} new events")

    # --- Drift detection & alerts ---
    alerts = []

    if not scratchpad["ok"]:
        if scratchpad.get("error"):
            alerts.append(f"CRITICAL: cc_scratchpad.md missing entirely")
        else:
            missing = ", ".join(scratchpad.get("missing", []))
            alerts.append(f"DRIFT: cc_scratchpad hierarchy markers missing: {missing}")

    if not session["ok"]:
        age = session.get("age_hours")
        if age:
            alerts.append(f"WARNING: CC last confirmed session was {age}h ago (threshold {SESSION_STALE_HOURS}h)")
        else:
            alerts.append(f"WARNING: No CC session confirmation found on bus")

    if not pending["ok"]:
        alerts.append(f"NOTICE: {pending['count']} messages addressed to CC pending on bus -- CC should check in")

    if alerts:
        msg = f"CC WATCHDOG ALERT [{ts}]\n\n" + "\n".join(f"  - {a}" for a in alerts)
        mid = _bus_post(token, "colby", msg, urgency="informational")
        print(f"[{ts}] ALERT posted: {mid}")

    # --- Hourly heartbeat ---
    status = "HEALTHY" if not alerts else "DRIFT_DETECTED"
    if run_count % HEARTBEAT_RUNS == 0:
        summary = (
            f"CC WATCHDOG HEARTBEAT [{ts}]\n"
            f"Status: {status} | run #{run_count}\n"
            f"Scratchpad: {'OK' if scratchpad['ok'] else 'DRIFT'} "
            f"(hash {scratchpad.get('hash', 'N/A')})\n"
            f"Last session: {session.get('last_session_ts', 'UNKNOWN')} "
            f"({session.get('age_hours', '?')}h ago)\n"
            f"Pending for CC: {pending['count']}\n"
            f"Evolution events captured (lifetime): "
            f"{_load_json(SPINE_PATH, {}).get('evolution', {}).get('version', 0)}"
        )
        _bus_post(token, "all", summary, urgency="informational")
        print(f"[{ts}] heartbeat posted (run #{run_count})")

    # --- Save anchor ---
    anchor.update({
        "run_count": run_count,
        "last_run_ts": ts,
        "last_status": status,
        "last_scratchpad_hash": scratchpad.get("hash"),
        "last_session_ts": session.get("last_session_ts"),
        "pending_count": pending["count"],
    })
    _save_json(ANCHOR_PATH, anchor)

    # --- Save latest snapshot ---
    _save_json(LATEST_PATH, {
        "ts": ts,
        "run_count": run_count,
        "status": status,
        "scratchpad": scratchpad,
        "session": session,
        "pending": pending,
        "evolution_events_this_run": len(events),
        "alerts": alerts,
    })

    print(f"[{ts}] run #{run_count} complete — {status}")


if __name__ == "__main__":
    run()
```

**Step 2: Save file locally**

```
Save to: C:\Users\raest\Documents\Karma_SADE\Scripts\cc_ascendant_watchdog.py
```

**Step 3: Verify syntax**

```bash
python -c "import ast; ast.parse(open('Scripts/cc_ascendant_watchdog.py').read()); print('syntax ok')"
```
Expected: `syntax ok`

**Step 4: Commit**

```powershell
powershell -Command "git add Scripts/cc_ascendant_watchdog.py; git commit -m 'feat: CC Ascendant Watchdog + Evolution Agent script'"
```

---

### Task 3: Systemd unit files

**Files:**
- Create: `Scripts/systemd/cc-ascendant-watchdog.service`
- Create: `Scripts/systemd/cc-ascendant-watchdog.timer`

**Step 1: Write service file** — save to `Scripts/systemd/cc-ascendant-watchdog.service`:

```ini
[Unit]
Description=CC Ascendant Watchdog — identity health + evolution capture
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=karma
WorkingDirectory=/mnt/c/dev/Karma/k2/aria
ExecStart=/usr/bin/python3 /mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py
StandardOutput=append:/mnt/c/dev/Karma/k2/cache/cc_watchdog.log
StandardError=append:/mnt/c/dev/Karma/k2/cache/cc_watchdog.log
Environment=HUB_BASE_URL=https://hub.arknexus.net
Environment=CC_SESSION_STALE_HOURS=24
Environment=CC_WATCHDOG_HEARTBEAT_RUNS=60
Environment=CC_PENDING_ALERT_THRESHOLD=5
EnvironmentFile=-/etc/default/karma-kiki
```

**Step 2: Write timer file** — save to `Scripts/systemd/cc-ascendant-watchdog.timer`:

```ini
[Unit]
Description=Run CC Ascendant Watchdog every 60 seconds

[Timer]
OnBootSec=30s
OnUnitActiveSec=60s
AccuracySec=1s
Persistent=true
Unit=cc-ascendant-watchdog.service

[Install]
WantedBy=timers.target
```

**Step 3: Commit**

```powershell
powershell -Command "git add Scripts/systemd/; git commit -m 'feat: CC Ascendant Watchdog systemd unit files'"
```

---

### Task 4: Deploy to K2

**Step 1: Push to GitHub**

```powershell
powershell -Command "git push origin main"
```

**Step 2: Pull on vault-neo**

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
```

**Step 3: Sync script to K2 via tunnel**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'cp /mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py /mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py.bak 2>/dev/null; echo bak ok'"

# Copy via vault-neo as relay
ssh vault-neo "scp -P 2223 -o StrictHostKeyChecking=no /home/neo/karma-sade/Scripts/cc_ascendant_watchdog.py karma@localhost:/mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py"
```

**Step 4: Verify script on K2**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -m py_compile /mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py && echo compile_ok'"
```
Expected: `compile_ok`

**Step 5: Copy systemd units to K2**

```bash
ssh vault-neo "scp -P 2223 -o StrictHostKeyChecking=no /home/neo/karma-sade/Scripts/systemd/cc-ascendant-watchdog.service karma@localhost:/mnt/c/dev/Karma/k2/systemd/cc-ascendant-watchdog.service"

ssh vault-neo "scp -P 2223 -o StrictHostKeyChecking=no /home/neo/karma-sade/Scripts/systemd/cc-ascendant-watchdog.timer karma@localhost:/mnt/c/dev/Karma/k2/systemd/cc-ascendant-watchdog.timer"
```

---

### Task 5: Install and enable systemd units on K2

**Step 1: Install units**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost '
  sudo cp /mnt/c/dev/Karma/k2/systemd/cc-ascendant-watchdog.service /etc/systemd/system/
  sudo cp /mnt/c/dev/Karma/k2/systemd/cc-ascendant-watchdog.timer /etc/systemd/system/
  sudo systemctl daemon-reload
  echo daemon_reloaded
'"
```
Expected: `daemon_reloaded`

**Step 2: Run once manually to verify**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 /mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py'"
```
Expected: `run #1 complete — HEALTHY` or alert if drift present

**Step 3: Check anchor file was created**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -m json.tool /mnt/c/dev/Karma/k2/cache/cc_watchdog_anchor.json'"
```
Expected: JSON with `run_count: 1`, `last_status`

**Step 4: Enable and start timer**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost '
  sudo systemctl enable cc-ascendant-watchdog.timer
  sudo systemctl start cc-ascendant-watchdog.timer
  sudo systemctl status cc-ascendant-watchdog.timer --no-pager
'"
```
Expected: `Active: active (waiting)`

**Step 5: Verify timer is scheduled**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'sudo systemctl list-timers cc-ascendant-watchdog.timer --no-pager'"
```
Expected: Timer listed with next trigger ~60s out

---

### Task 6: Seed identity spine and first evolution run

**Step 1: Confirm spine file**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -m json.tool /mnt/c/dev/Karma/k2/cache/cc_identity_spine.json | grep -E \"name|rank|version\"'"
```

**Step 2: Wait 90 seconds then check run #2 completed**

```bash
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'tail -5 /mnt/c/dev/Karma/k2/cache/cc_watchdog.log'"
```
Expected: `run #2 complete — HEALTHY`

**Step 3: Check bus for any alerts or heartbeat (after 60 runs ~1hr)**

```bash
TOKEN=$(ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt')
ssh vault-neo "curl -s -H 'Authorization: Bearer $TOKEN' 'http://localhost:18090/v1/coordination/recent?limit=10' | python3 -c \"import json,sys; [print(e.get('from'),e.get('to'),str(e.get('content',''))[:80]) for e in json.load(sys.stdin).get('entries',[])]\" | grep watchdog"
```

---

### Task 7: MEMORY.md + claude-mem + final commit

**Step 1: Update MEMORY.md**

Append to `MEMORY.md`:
```
## Session 96 — CC Ascendant Watchdog + Evolution Agent

Built and deployed cc_ascendant_watchdog.py on K2 as systemd timer (60s cycles).
Zero Anthropic tokens. Monitors: scratchpad hierarchy, session bus confirmation,
pending CC messages, state hash drift. Posts ForColby alerts on drift.
Captures CC evolution events (DECISION/PROOF/INSIGHT/PITFALL/DIRECTION) from bus
into cc_evolution_log.jsonl + cc_identity_spine.json for independent persona growth.
Files: Scripts/cc_ascendant_watchdog.py, Scripts/systemd/cc-ascendant-watchdog.{service,timer}
K2 paths: /mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py
Cache: cc_watchdog_anchor.json, cc_watchdog_latest.json, cc_identity_spine.json, cc_evolution_log.jsonl
```

**Step 2: Save claude-mem observation**

```
mcp__plugin_claude-mem_mcp-search__save_observation(
  title="PROOF: CC Ascendant Watchdog deployed on K2",
  text="CC Ascendant Watchdog + Evolution Agent deployed as K2 systemd timer (60s). Zero tokens. Monitors scratchpad hierarchy, bus session confirmation, pending messages. Posts ForColby alerts on drift. Captures DECISION/PROOF/INSIGHT events from bus into cc_evolution_log.jsonl + cc_identity_spine.json. Files in Scripts/. K2: /mnt/c/dev/Karma/k2/aria/tools/cc_ascendant_watchdog.py",
  project="Karma_SADE"
)
```

**Step 3: Final commit + push**

```powershell
powershell -Command "git add MEMORY.md docs/plans/2026-03-15-cc-ascendant-watchdog.md; git commit -m 'docs: CC Ascendant Watchdog plan + MEMORY.md update'; git push origin main"
```

**Step 4: Pull on vault-neo**

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
```

---

## Success Criteria

- [ ] `cc_ascendant_watchdog.py` runs on K2 without error
- [ ] `cc_watchdog_anchor.json` exists and increments run_count each cycle
- [ ] `cc_identity_spine.json` exists and updates when evolution events captured
- [ ] Timer active: `systemctl status cc-ascendant-watchdog.timer` shows `active (waiting)`
- [ ] No alerts fired for a healthy system
- [ ] ForColby alert appears in Agora if cc_scratchpad.md hierarchy is modified/broken
