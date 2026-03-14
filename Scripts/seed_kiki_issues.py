"""Seed kiki_issues.jsonl with evolve.md bootstrap issues."""
import json, datetime

ISSUES_FILE = "/mnt/c/dev/Karma/k2/cache/kiki_issues.jsonl"
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

issues = [
    {
        "id": "evolve-001",
        "title": "Bootstrap: confirm evolve.md loaded and readable",
        "priority": 1,
        "status": "open",
        "created_at": now,
        "details": "Read /mnt/c/dev/Karma/k2/cache/evolve.md, verify it parses, extract version field. PASS = version field contains '2.1-cc'."
    },
    {
        "id": "evolve-002",
        "title": "P1 health probe: verify kiki service alive + freshness endpoint",
        "priority": 2,
        "status": "open",
        "created_at": now,
        "details": "Run health_probe per evolve.md section 4 P1. Check 'systemctl is-active karma-kiki' and GET /v1/debug/k2-freshness?force=1. Record raw output in artifact bundle."
    },
    {
        "id": "evolve-003",
        "title": "P4 code nav probe: confirm run_cycle function locatable",
        "priority": 3,
        "status": "open",
        "created_at": now,
        "details": "Run: grep -r 'def run_cycle' /mnt/c/dev/Karma/k2/scripts/ --include='*.py' -l. PASS = exit 0 AND output contains karma_kiki_v5.py."
    },
    {
        "id": "evolve-004",
        "title": "P5 delegation probe: shell_run echo delegation_ok",
        "priority": 4,
        "status": "open",
        "created_at": now,
        "details": "Execute 'echo delegation_ok' via shell mechanism. PASS = exit 0 AND stdout.strip() == 'delegation_ok'."
    },
]

with open(ISSUES_FILE, "w") as f:
    for issue in issues:
        f.write(json.dumps(issue) + "\n")

print(f"SEEDED {len(issues)} issues to {ISSUES_FILE}")
