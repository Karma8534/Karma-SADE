#!/usr/bin/env python3
"""Generate cc-session-brief.md from current system state.
Runs on vault-neo cron to keep the brief fresh for CC sessions."""

import json
import subprocess
import datetime
import os

OUTPUT = "/home/neo/karma-sade/cc-session-brief.md"
MEMORY_MD = "/home/neo/karma-sade/MEMORY.md"
LEDGER = "/opt/seed-vault/memory_v1/ledger/memory.jsonl"

def ts():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def main():
    now = ts()
    parts = [f"# CC Session Brief — {now}"]
    parts.append("> Auto-generated every 30 minutes on vault-neo. Read this at session start.\n")

    # Git status
    git_log = run("cd /home/neo/karma-sade && git log --oneline -5")
    git_branch = run("cd /home/neo/karma-sade && git branch --show-current")
    parts.append(f"## Git State")
    parts.append(f"Branch: `{git_branch}`")
    parts.append(f"Recent commits:\n```\n{git_log}\n```\n")

    # Docker containers
    docker_ps = run("docker ps --format '{{.Names}}: {{.Status}}'")
    parts.append(f"## Containers")
    parts.append(f"```\n{docker_ps}\n```\n")

    # Disk
    disk = run("df -h / --output=pcent,avail | tail -1")
    parts.append(f"## Disk: {disk.strip()}\n")

    # Ledger
    if os.path.exists(LEDGER):
        ledger_count = run(f"wc -l < {LEDGER}")
        parts.append(f"## Ledger: {ledger_count} entries\n")

    # FalkorDB
    falkor = run("docker exec falkordb redis-cli GRAPH.QUERY neo_workspace 'MATCH (n) RETURN labels(n) AS t, count(n) AS c' 2>/dev/null")
    if falkor:
        parts.append(f"## FalkorDB\n```\n{falkor[:500]}\n```\n")

    # MEMORY.md (last 60 lines)
    if os.path.exists(MEMORY_MD):
        with open(MEMORY_MD) as f:
            lines = f.readlines()
        tail = "".join(lines[-60:])
        parts.append(f"## MEMORY.md (tail)\n```\n{tail[:3000]}\n```\n")

    # Active task (from MEMORY.md first header)
    if os.path.exists(MEMORY_MD):
        with open(MEMORY_MD) as f:
            for line in f:
                if line.startswith("## Session"):
                    parts.insert(2, f"## Active: {line.strip()}\n")
                    break

    brief = "\n".join(parts)
    with open(OUTPUT, "w") as f:
        f.write(brief)

    print(f"[{now}] Brief generated: {len(brief)} chars -> {OUTPUT}")

if __name__ == "__main__":
    main()
