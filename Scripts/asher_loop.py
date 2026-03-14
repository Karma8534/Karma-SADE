"""
Asher Loop — CC's background intelligence on K2.
Runs every 60 seconds. Reads bus, kiki journal, MEMORY.md.
Uses devstral to distill what CC should know next session.
Writes to cc_scratchpad.md. No relay needed.
"""
import json
import os
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = Path("/mnt/c/dev/Karma/k2/cache")
SCRATCHPAD = BASE / "cc_scratchpad.md"
HUB_TOKEN = os.environ.get("HUB_AUTH_TOKEN", "").strip()
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://172.22.240.1:11434")
MODEL = os.environ.get("ASHER_MODEL", "devstral:latest")
POLL_INTERVAL = int(os.environ.get("ASHER_POLL", "10"))   # bus check every 10s
THINK_INTERVAL = int(os.environ.get("ASHER_THINK", "300")) # max devstral gap: 5min
LOG = BASE / "asher_loop.log"


def log(msg):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def read_bus_recent():
    if not HUB_TOKEN:
        return []
    try:
        req = urllib.request.Request(
            "https://hub.arknexus.net/v1/coordination/recent?limit=20",
            headers={"Authorization": f"Bearer {HUB_TOKEN}"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read())
            return data.get("entries", [])
    except Exception as e:
        log(f"bus read failed: {e}")
        return []


def read_kiki_journal_tail(n=5):
    journal = BASE / "kiki_journal.jsonl"
    if not journal.exists():
        return []
    lines = journal.read_text().strip().split("\n")
    entries = []
    for line in reversed(lines[-n:]):
        try:
            entries.append(json.loads(line))
        except Exception:
            pass
    return entries


def read_kiki_state():
    state_file = BASE / "kiki_state.json"
    if not state_file.exists():
        return {}
    try:
        return json.loads(state_file.read_text())
    except Exception:
        return {}


def ask_devstral(prompt):
    try:
        payload = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 300}
        }).encode()
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
            return result.get("response", "").strip()
    except Exception as e:
        log(f"devstral failed: {e}")
        return ""


def update_scratchpad(section, content):
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    existing = SCRATCHPAD.read_text() if SCRATCHPAD.exists() else ""
    marker_start = f"<!-- {section} -->"
    marker_end = f"<!-- /{section} -->"
    new_block = f"{marker_start}\n**{section}** (updated {ts})\n{content}\n{marker_end}"
    if marker_start in existing:
        import re
        existing = re.sub(
            f"{re.escape(marker_start)}.*?{re.escape(marker_end)}",
            new_block,
            existing,
            flags=re.DOTALL
        )
    else:
        existing += f"\n\n{new_block}"
    SCRATCHPAD.write_text(existing)


def run_cycle():
    log("=== Asher cycle start ===")

    # 1. Read bus for CC-addressed messages
    bus = read_bus_recent()
    cc_messages = [e for e in bus if e.get("to") in ("cc", "all") and e.get("status") == "pending"]
    log(f"Bus: {len(cc_messages)} pending for CC")

    # 2. Read kiki state
    state = read_kiki_state()
    cycles = state.get("cycles", 0)
    closed = state.get("issues_closed", 0)

    # 3. Read kiki journal tail
    journal_tail = read_kiki_journal_tail(3)
    recent_closures = [e.get("issue", {}).get("title", "") for e in journal_tail if e.get("closure", {}).get("outcome") == "closed"]

    # 4. Ask devstral: what should CC know?
    bus_summary = "\n".join([f"- [{e['from']}→{e['to']}] {e['content'][:200]}" for e in cc_messages[:5]])
    kiki_summary = f"cycles={cycles}, issues_closed={closed}, recent: {recent_closures[:3]}"

    if cc_messages or recent_closures:
        prompt = f"""You are Asher, the background intelligence for CC (Claude Code) on K2.
Summarize in 3 bullet points what CC needs to know at next session start.
Be specific, no filler.

Coordination bus messages for CC:
{bus_summary or 'none'}

Kiki recent activity:
{kiki_summary}

Output 3 bullets only."""
        insight = ask_devstral(prompt)
        if insight:
            log(f"devstral insight: {insight[:100]}...")
            update_scratchpad("ASHER_BRIEF", insight)
            log("scratchpad updated")
    else:
        log("Nothing new for CC — idle cycle")

    log("=== Asher cycle end ===")


def main():
    import hashlib
    log("Asher loop starting — event-driven mode (poll 10s, think on delta)")
    if not HUB_TOKEN:
        log("WARNING: HUB_AUTH_TOKEN not set — bus reads will fail")

    last_hash = ""
    last_think = 0.0

    while True:
        try:
            # Fast poll — check if anything changed
            bus = read_bus_recent()
            journal = read_kiki_journal_tail(3)
            state = read_kiki_state()

            fingerprint = hashlib.md5(
                json.dumps([
                    [e["id"] for e in bus],
                    state.get("cycles", 0),
                    [e.get("ts", "") for e in journal]
                ]).encode()
            ).hexdigest()

            now = time.time()
            delta = fingerprint != last_hash
            overdue = (now - last_think) > THINK_INTERVAL

            if delta or overdue:
                log(f"delta={delta} overdue={overdue} — running cycle")
                run_cycle()
                last_hash = fingerprint
                last_think = now
            # else silent — nothing changed
        except Exception as e:
            log(f"loop error: {e}")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
