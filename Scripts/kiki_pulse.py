#!/usr/bin/env python3
"""
kiki_pulse.py — Zero-token Karma evolution monitor.
Runs every 2h on K2 via cron. No Anthropic API calls.
- Reads kiki_state.json
- Writes kiki_pulse.md to cache (CC reads at session start)
- Posts one-line status to coordination bus
- If queue empty: seeds 3 fresh probe issues automatically
"""
import json, datetime, pathlib, urllib.request, os, sys

CACHE = pathlib.Path("/mnt/c/dev/Karma/k2/cache")
ISSUES_FILE = CACHE / "kiki_issues.jsonl"
STATE_FILE  = CACHE / "kiki_state.json"
PULSE_FILE  = CACHE / "kiki_pulse.md"
HUB_URL     = "https://hub.arknexus.net"
TOKEN       = os.environ.get("HUB_AUTH_TOKEN", "")

def _now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}

def load_issues():
    if not ISSUES_FILE.exists() or ISSUES_FILE.stat().st_size == 0:
        return []
    return [json.loads(l) for l in ISSUES_FILE.read_text().splitlines() if l.strip()]

def post_bus(msg):
    if not TOKEN:
        print("WARN: HUB_AUTH_TOKEN not set, skipping bus post", file=sys.stderr)
        return
    payload = json.dumps({
        "from": "cc", "to": "all",
        "type": "inform", "urgency": "informational",
        "content": msg
    }).encode()
    req = urllib.request.Request(
        f"{HUB_URL}/v1/coordination/post", data=payload,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            print(f"bus post: {d.get('id','?')[:24]}")
    except Exception as e:
        print(f"bus post failed: {e}", file=sys.stderr)

def seed_issues():
    now = _now()
    uid = now.replace(":", "").replace("-", "")[:14]
    issues = [
        {"id": f"auto-{uid}-01", "title": "Write probe token A", "priority": 1,
         "status": "open", "attempts": 0, "created_at": now,
         "details": f"Write exact text PULSE_{uid}_A to {CACHE}/pulse_{uid}_a.txt. "
                    f"Done_when: grep -qx PULSE_{uid}_A {CACHE}/pulse_{uid}_a.txt exits 0."},
        {"id": f"auto-{uid}-02", "title": "Write probe token B", "priority": 2,
         "status": "open", "attempts": 0, "created_at": now,
         "details": f"Write exact text PULSE_{uid}_B to {CACHE}/pulse_{uid}_b.txt. "
                    f"Done_when: grep -qx PULSE_{uid}_B {CACHE}/pulse_{uid}_b.txt exits 0."},
        {"id": f"auto-{uid}-03", "title": "Write probe token C", "priority": 3,
         "status": "open", "attempts": 0, "created_at": now,
         "details": f"Write exact text PULSE_{uid}_C to {CACHE}/pulse_{uid}_c.txt. "
                    f"Done_when: grep -qx PULSE_{uid}_C {CACHE}/pulse_{uid}_c.txt exits 0."},
    ]
    ISSUES_FILE.write_text("\n".join(json.dumps(i) for i in issues) + "\n")
    print(f"seeded {len(issues)} auto issues")
    return len(issues)

def main():
    ts = _now()
    state = load_state()
    issues = load_issues()

    cycles      = state.get("cycles", 0)
    succeeded   = state.get("actions_succeeded", 0)
    failed      = state.get("actions_failed", 0)
    promoted    = state.get("total_rules_promoted", 0)
    idle        = state.get("idle_cycles", 0)
    last_cycle  = state.get("last_cycle_ts", "unknown")
    total_acts  = max(1, succeeded + failed)
    pass_pct    = round(100 * succeeded / total_acts)
    evolution   = "TRUE" if pass_pct >= 80 and promoted >= 1 else "FALSE"
    queue_count = len(issues)

    # Write pulse file for CC to read at session start
    pulse = f"""# kiki_pulse — {ts}
cycles={cycles}  idle={idle}  pass_rate={succeeded}/{total_acts}({pass_pct}%)
rules_promoted={promoted}  queue={queue_count}  last_cycle={last_cycle}
evolution_true={evolution}
"""
    PULSE_FILE.write_text(pulse)
    print(pulse.strip())

    # Auto-seed if queue empty
    seeded = 0
    if queue_count == 0:
        seeded = seed_issues()

    # Post to bus
    seeded_note = f" Auto-seeded {seeded} issues." if seeded else ""
    msg = (f"KIKI PULSE [{ts}] cycles={cycles} pass={pass_pct}% "
           f"promoted={promoted} queue={queue_count} evolution={evolution}.{seeded_note}")
    post_bus(msg)

if __name__ == "__main__":
    main()
