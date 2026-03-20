#!/usr/bin/env python3
"""
Governance Audit — Stop hook (CCTrustVerify P3-D)
At session end: checks if any locked invariant files were edited this session.
Advisory only — never blocks. Posts warning if unapproved edits detected.

JSON stdin: {stop_hook_active, session_id, cwd}
"""
import json, sys, os, subprocess


LOCKED_FILES = [
    "karma_contract_policy.md",
    "vesper_governor.py",
]


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    cwd = data.get("cwd", os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))

    # Check what changed in the most recent commit vs HEAD~1
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True, text=True, cwd=cwd
    )
    # Also check unstaged changes
    result2 = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, cwd=cwd
    )

    all_changed = result.stdout.strip().splitlines() + result2.stdout.strip().splitlines()
    locked_changed = [
        f for f in all_changed
        if any(lf in f for lf in LOCKED_FILES)
    ]

    if locked_changed:
        print(f"\n{'='*60}")
        print(f"⚠️   GOVERNANCE AUDIT — Session End Warning")
        print(f"{'='*60}")
        print(f"  Locked invariant file(s) were modified or staged this session:")
        for f in locked_changed:
            print(f"  {f.strip()}")
        print(f"")
        print(f"  Was explicit Sovereign (Colby) approval given in chat FIRST?")
        print(f"  If not: revert with git checkout and re-apply with approval.")
        print(f"  If yes: this is expected — carry on.")
        print(f"{'='*60}")

    # Always exit 0 — advisory only, never block session end
    sys.exit(0)


if __name__ == "__main__":
    main()
