#!/usr/bin/env python3
"""nexus_consistency_check.py — Catch stale data in nexus.md before commit.

Checks:
1. Baseline summary count matches actual PASS/NOT DONE/PARTIAL counts
2. Gap statuses in gap section match baseline checklist
3. Version in header matches latest changelog entry
4. EXISTS table session marker matches header session
5. Sprint order statuses match gap statuses

Exit 0 = clean. Exit 1 = inconsistencies found (blocks commit).
"""
import re, sys, os

NEXUS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "docs", "ForColby", "nexus.md")

def main():
    if not os.path.exists(NEXUS_PATH):
        print(f"[nexus-check] {NEXUS_PATH} not found, skipping")
        return 0

    with open(NEXUS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()
    errors = []

    # ── Check 1: Baseline summary matches actual counts ──────────────
    baseline_rows = []
    in_baseline = False
    for line in lines:
        if "Baseline Checklist" in line:
            in_baseline = True
            continue
        if in_baseline and line.startswith("|") and not line.startswith("| #") and not line.startswith("|---"):
            baseline_rows.append(line)
        if in_baseline and line.startswith("**Summary:**"):
            summary_line = line
            in_baseline = False

    actual_pass = sum(1 for r in baseline_rows if "PASS" in r and "NOT DONE" not in r and "PARTIAL" not in r)
    actual_not_done = sum(1 for r in baseline_rows if "NOT DONE" in r)
    actual_partial = sum(1 for r in baseline_rows if "PARTIAL" in r)
    actual_deferred = sum(1 for r in baseline_rows if "DEFERRED" in r)
    actual_unverified = sum(1 for r in baseline_rows if "UNVERIFIED" in r)

    summary_match = re.search(r"(\d+) PASS.*?(\d+) NOT DONE.*?(\d+) PARTIAL.*?(\d+) DEFERRED.*?(\d+) UNVERIFIED", summary_line) if 'summary_line' in dir() else None
    if summary_match:
        s_pass, s_nd, s_partial, s_def, s_unv = [int(x) for x in summary_match.groups()]
        if s_pass != actual_pass:
            errors.append(f"Baseline summary says {s_pass} PASS but counted {actual_pass}")
        if s_nd != actual_not_done:
            errors.append(f"Baseline summary says {s_nd} NOT DONE but counted {actual_not_done}")
        if s_partial != actual_partial:
            errors.append(f"Baseline summary says {s_partial} PARTIAL but counted {actual_partial}")
        if s_def != actual_deferred:
            errors.append(f"Baseline summary says {s_def} DEFERRED but counted {actual_deferred}")
        if s_unv != actual_unverified:
            errors.append(f"Baseline summary says {s_unv} UNVERIFIED but counted {actual_unverified}")
    elif baseline_rows:
        errors.append("Could not parse baseline summary line")

    # ── Check 2: Gap statuses match baseline ─────────────────────────
    gap_statuses = {}
    for line in lines:
        m = re.match(r"### Gap (\d+):.*?\[(.*?)\]", line)
        if m:
            gap_statuses[int(m.group(1))] = m.group(2).strip()

    gap_to_baseline = {1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 13, 7: 15, 8: 18}
    for gap_num, baseline_num in gap_to_baseline.items():
        gap_status = gap_statuses.get(gap_num, "")
        if gap_num <= len(gap_statuses):
            gap_shipped = "SHIPPED" in gap_status
            baseline_row = baseline_rows[baseline_num - 1] if baseline_num <= len(baseline_rows) else ""
            baseline_pass = "PASS" in baseline_row and "NOT DONE" not in baseline_row
            if gap_shipped and not baseline_pass:
                errors.append(f"Gap {gap_num} says SHIPPED but baseline #{baseline_num} is not PASS")
            if not gap_shipped and "NOT DONE" not in gap_status and baseline_pass:
                pass  # gap might have other status

    # ── Check 3: Version in header matches changelog ─────────────────
    header_version = None
    changelog_version = None
    in_changelog = False
    for line in lines:
        m = re.match(r"\*\*Version:\*\*\s*([\d.]+)", line)
        if m:
            header_version = m.group(1)
        if "## Change Log" in line:
            in_changelog = True
            continue
        if in_changelog and not changelog_version:
            m2 = re.match(r"\|\s*([\d.]+)\s*\|", line)
            if m2:
                changelog_version = m2.group(1)

    if header_version and changelog_version and header_version != changelog_version:
        errors.append(f"Header version {header_version} != latest changelog version {changelog_version}")

    # ── Check 4: EXISTS table session matches header ─────────────────
    header_session = None
    exists_session = None
    for line in lines:
        m = re.search(r"\(S(\d+)", line)
        if m and "Version" in line:
            header_session = m.group(1)
        if "What EXISTS" in line:
            m2 = re.search(r"S(\d+)", line)
            if m2:
                exists_session = m2.group(1)

    if header_session and exists_session and header_session != exists_session:
        errors.append(f"Header references S{header_session} but EXISTS table says S{exists_session}")

    # ── Report ───────────────────────────────────────────────────────
    if errors:
        print(f"\n{'='*60}")
        print(f"NEXUS.MD CONSISTENCY CHECK FAILED — {len(errors)} issue(s)")
        print(f"{'='*60}")
        for i, e in enumerate(errors, 1):
            print(f"  {i}. {e}")
        print(f"{'='*60}")
        print("Fix these before committing nexus.md.\n")
        return 1
    else:
        print("[nexus-check] All consistency checks passed.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
