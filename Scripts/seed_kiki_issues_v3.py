#!/usr/bin/env python3
"""
Seed corrected issues for health probe and delegation probe.
Fixes: /health now returns 200 no-auth, delegation uses = not == for /bin/sh.
"""
import json, datetime

ISSUES_FILE = "/mnt/c/dev/Karma/k2/cache/kiki_issues.jsonl"
now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

issues = [
    {
        "id": "evolve-c01",
        "title": "P1 health probe v2: verify kiki alive + hub /health returns 200",
        "priority": 1,
        "status": "open",
        "created_at": now,
        "details": (
            "Run TWO commands and write ALL output to /mnt/c/dev/Karma/k2/cache/health_probe_v2.txt: "
            "CMD1: systemctl is-active karma-kiki "
            "CMD2: curl -s -o /dev/null -w '%{http_code}' https://hub.arknexus.net/health "
            "PASS = CMD1 output is 'active' AND CMD2 output is '200'. "
            "Use bash (not sh) for the test: bash -c 'result=$(curl ...); if [ \"$result\" = \"200\" ]; then echo PASS; fi' "
            "Write raw stdout of both commands to the output file as evidence."
        )
    },
    {
        "id": "evolve-c02",
        "title": "P5 delegation probe v2: echo delegation_ok verify with bash",
        "priority": 2,
        "status": "open",
        "created_at": now,
        "details": (
            "Run via bash (NOT sh): bash -c 'out=$(echo delegation_ok); echo \"$out\" > /mnt/c/dev/Karma/k2/cache/delegation_probe_v2.txt; "
            "if [ \"$out\" = \"delegation_ok\" ]; then echo PASS; else echo FAIL; fi' "
            "PASS = exit 0 AND delegation_probe_v2.txt contains 'delegation_ok'. "
            "NOTE: use single = not == for string comparison in bash test brackets."
        )
    },
    {
        "id": "evolve-c03",
        "title": "Self-report v2: write evolution status using python3",
        "priority": 3,
        "status": "open",
        "created_at": now,
        "details": (
            "Use python3 (NOT python) to read /mnt/c/dev/Karma/k2/cache/kiki_state.json. "
            "Write a plain text summary to /mnt/c/dev/Karma/k2/cache/kiki_evolution_status.txt containing: "
            "cycles, idle_cycles, actions_succeeded, actions_failed, issues_closed, total_rules_promoted. "
            "Example command: python3 -c \"import json; s=json.load(open('/mnt/c/dev/Karma/k2/cache/kiki_state.json')); "
            "open('/mnt/c/dev/Karma/k2/cache/kiki_evolution_status.txt','w').write(str(s))\" "
            "PASS = file written with numeric values, python3 exits 0."
        )
    },
]

# Read existing issues, keep any still open that aren't being replaced
try:
    existing = [json.loads(l) for l in open(ISSUES_FILE).readlines() if l.strip()]
    keep = [i for i in existing if i.get("status") == "open"
            and i["id"] not in [n["id"] for n in issues]]
except Exception:
    keep = []

all_issues = keep + issues
with open(ISSUES_FILE, "w") as f:
    for issue in all_issues:
        f.write(json.dumps(issue) + "\n")

print(f"SEEDED {len(issues)} issues ({len(keep)} existing kept), total: {len(all_issues)}")
