#!/usr/bin/env python3
"""
Seed kiki_issues.jsonl with corrected evolve.md bootstrap issues.
Fixes: READ-ONLY verification tasks, python3 not python, correct hub URL.
NEVER writes to: evolve.md, karma_directive.md, cc_scratchpad.md
"""
import json, datetime

ISSUES_FILE = "/mnt/c/dev/Karma/k2/cache/kiki_issues.jsonl"
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

issues = [
    {
        "id": "evolve-b01",
        "title": "READ-ONLY: verify evolve.md intact (version=2.1-cc, size>7000 bytes)",
        "priority": 1,
        "status": "open",
        "created_at": now,
        "details": (
            "IMPORTANT: DO NOT WRITE TO evolve.md. READ ONLY. "
            "Run: wc -c /mnt/c/dev/Karma/k2/cache/evolve.md "
            "AND: grep -m1 'version:' /mnt/c/dev/Karma/k2/cache/evolve.md "
            "PASS = file size > 7000 bytes AND version line contains '2.1-cc'. "
            "Write results to /mnt/c/dev/Karma/k2/cache/evolve_verify.txt only."
        )
    },
    {
        "id": "evolve-b02",
        "title": "P1 health probe: check kiki alive + hub health endpoint",
        "priority": 2,
        "status": "open",
        "created_at": now,
        "details": (
            "Run two commands and write results to /mnt/c/dev/Karma/k2/cache/health_probe.txt: "
            "1) systemctl is-active karma-kiki (expect: active) "
            "2) curl -s -o /dev/null -w '%{http_code}' https://hub.arknexus.net/health "
            "(expect: 200). "
            "Use python3 (NOT python). "
            "PASS = both return expected values. Write raw output as evidence."
        )
    },
    {
        "id": "evolve-b03",
        "title": "P4 code nav: locate run_cycle in kiki scripts",
        "priority": 3,
        "status": "open",
        "created_at": now,
        "details": (
            "Run: grep -rl 'def run_cycle' /mnt/c/dev/Karma/k2/scripts/ "
            "Write output to /mnt/c/dev/Karma/k2/cache/nav_probe.txt. "
            "PASS = exit 0 AND output contains karma_kiki_v5.py."
        )
    },
    {
        "id": "evolve-b04",
        "title": "P5 delegation: echo delegation_ok and verify stdout",
        "priority": 4,
        "status": "open",
        "created_at": now,
        "details": (
            "Run: echo delegation_ok "
            "Capture stdout. Write to /mnt/c/dev/Karma/k2/cache/delegation_probe.txt. "
            "PASS = exit 0 AND stdout.strip() == 'delegation_ok'."
        )
    },
    {
        "id": "evolve-b05",
        "title": "Self-report: write evolution status to kiki_evolution_status.txt",
        "priority": 5,
        "status": "open",
        "created_at": now,
        "details": (
            "Use python3 to read kiki_state.json. "
            "Compute: cycles, idle_cycles, actions_succeeded, actions_failed, issues_closed, total_rules_promoted. "
            "Write a plain text summary to /mnt/c/dev/Karma/k2/cache/kiki_evolution_status.txt. "
            "PASS = file written, contains numeric values, exit 0."
        )
    },
]

with open(ISSUES_FILE, "w") as f:
    for issue in issues:
        f.write(json.dumps(issue) + "\n")

print(f"SEEDED {len(issues)} corrected issues")
