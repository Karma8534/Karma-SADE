#!/usr/bin/env python3
"""
CC Hourly Report — Ascendant layer status post to coordination bus.
Runs every 60 minutes on K2 via cron.
Posts from cc to all in Agora.
"""
import json, datetime, subprocess, os, sys
from pathlib import Path

CACHE = Path("/mnt/c/dev/Karma/k2/cache")
HUB_URL = "https://hub.arknexus.net"
TOKEN_CMD = "ssh -p 22 -o StrictHostKeyChecking=no -o ConnectTimeout=5 vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt'"
ARIA_KEY  = os.environ.get("HUB_AUTH_TOKEN", "")

def read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception:
        return {}

def read_jsonl_tail(path, n=20):
    try:
        lines = Path(path).read_text().strip().splitlines()
        return [json.loads(l) for l in lines[-n:] if l.strip()]
    except Exception:
        return []

def get_token():
    if ARIA_KEY:
        # Fetch from vault-neo via local ssh tunnel
        try:
            r = subprocess.run(
                ["ssh", "-p", "2223", "-l", "karma", "-o", "StrictHostKeyChecking=no",
                 "-o", "ConnectTimeout=5", "localhost",
                 "ssh -o StrictHostKeyChecking=no vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt'"],
                capture_output=True, text=True, timeout=10
            )
            return r.stdout.strip()
        except Exception:
            pass
    return None

def post_to_bus(token, content, to="all", urgency="informational"):
    import urllib.request
    payload = json.dumps({
        "from": "cc",
        "to": to,
        "type": "inform",
        "urgency": urgency,
        "content": content
    }).encode()
    req = urllib.request.Request(
        f"{HUB_URL}/v1/coordination/post",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def evaluate():
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    state = read_json(CACHE / "kiki_state.json")
    journal = read_jsonl_tail(CACHE / "kiki_journal.jsonl", 20)
    issues  = read_jsonl_tail(CACHE / "kiki_issues.jsonl", 50)
    rules   = read_jsonl_tail(CACHE / "kiki_rules.jsonl", 10)

    cycles      = state.get("cycles", 0)
    last_ts     = state.get("last_cycle_ts", "MISSING")
    idle        = state.get("idle_cycles", 0)
    promoted    = state.get("total_rules_promoted", 0)
    closed      = state.get("issues_closed", 0)
    succeeded   = state.get("actions_succeeded", 0)
    failed      = state.get("actions_failed", 0)
    open_issues = [i for i in issues if i.get("status") == "open"]

    # Rolling pass rate from recent journal
    recent_results = [e.get("verification", {}).get("ok") for e in journal if "verification" in e]
    pass_rate = (sum(1 for r in recent_results if r) / len(recent_results)) if recent_results else None

    # Stale check
    stale = False
    if last_ts and last_ts != "MISSING":
        try:
            last_dt = datetime.datetime.strptime(last_ts, "%Y-%m-%dT%H:%M:%SZ")
            age = (datetime.datetime.utcnow() - last_dt).total_seconds()
            stale = age > 300
        except Exception:
            stale = True
    else:
        stale = True

    # Evolution assessment
    pass_rate_ok  = pass_rate is not None and pass_rate >= 0.80
    has_rule      = promoted >= 1 or len(rules) >= 1
    not_stale     = not stale
    has_progress  = closed > 0 or succeeded > 0

    evolution = pass_rate_ok and has_rule and not_stale and has_progress

    # Determine signal
    if stale:
        signal = "⚠️ STALE"
        guidance = "Kiki cycle has not advanced in 5+ minutes. Possible stall. Checking..."
    elif not has_progress and cycles > 5:
        signal = "⚠️ IDLE"
        guidance = "Cycles running but no issues closed and no actions succeeded. Backlog may be empty or blocked."
    elif evolution:
        signal = "✅ EVOLVING"
        guidance = None
    else:
        signal = "🔄 PROGRESSING"
        guidance = None

    report = f"""[CC HOURLY — {now}]
Karma Evolution Status: {signal}
━━━━━━━━━━━━━━━━━━━━━━
Kiki cycles: {cycles} | idle: {idle} | last_cycle: {last_ts}
Actions: {succeeded} succeeded / {failed} failed
Issues: {len(open_issues)} open | {closed} closed
Rules promoted: {promoted}
Pass rate (last 20): {"N/A" if pass_rate is None else f"{pass_rate:.0%}"}
evolution_true: {"YES" if evolution else "NO"}"""

    if guidance:
        report += f"\n\nGuidance → Karma: {guidance}"

    return report, signal, stale

def main():
    report, signal, stale = evaluate()
    print(report)

    token = get_token()
    if not token:
        print("ERROR: could not fetch hub token", file=sys.stderr)
        sys.exit(1)

    urgency = "blocking" if stale else "informational"
    result = post_to_bus(token, report, to="all", urgency=urgency)
    if result.get("ok"):
        print(f"Posted to bus: {result.get('id','?')}")
    else:
        print(f"Bus post failed: {result}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
