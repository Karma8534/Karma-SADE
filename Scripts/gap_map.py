#!/usr/bin/env python3
"""gap_map.py — Atomic gap-map row + summary updater for preclaw1-gap-map.md.

Shared helper used by vesper_governor.py and any other Phase 0 tooling.
Updates a feature row status AND recomputes summary counts in one atomic write.

Usage:
    from gap_map import update_gap_status
    update_gap_status("Session persistence", "HAVE", evidence="Verified S160")
"""
import re
from pathlib import Path

GAP_MAP_PATH = Path(__file__).resolve().parent.parent / "Karma2" / "map" / "preclaw1-gap-map.md"

# Valid statuses
VALID_STATUSES = {"HAVE", "PARTIAL", "MISSING", "N/A"}

# Category header pattern: ## N. CATEGORY NAME
CATEGORY_HEADER_RE = re.compile(r"^## \d+\.\s+(.+)$")

# Table row pattern: | Feature | File | **STATUS** | Gap |
TABLE_ROW_RE = re.compile(r"^\|(.+)\|(.+)\|\s*\*\*(\w+(?:/\w+)?)\*\*\s*\|(.+)\|$")

# Summary row pattern: | Category | N | N | N | N |
SUMMARY_ROW_RE = re.compile(r"^\|\s*(.+?)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|$")
SUMMARY_TOTAL_RE = re.compile(r"^\|\s*\*\*TOTAL\*\*\s*\|")


def parse_gap_map(path=None):
    """Parse gap map into structured data. Returns (lines, features, categories)."""
    p = Path(path) if path else GAP_MAP_PATH
    lines = p.read_text(encoding="utf-8").splitlines()

    features = []  # list of {line_idx, feature, file, status, gap, category}
    current_category = None

    for i, line in enumerate(lines):
        cat_match = CATEGORY_HEADER_RE.match(line.strip())
        if cat_match:
            current_category = cat_match.group(1).strip()
            continue

        row_match = TABLE_ROW_RE.match(line.strip())
        if row_match and current_category:
            feature = row_match.group(1).strip()
            file_ref = row_match.group(2).strip()
            status = row_match.group(3).strip()
            gap = row_match.group(4).strip()
            features.append({
                "line_idx": i,
                "feature": feature,
                "file": file_ref,
                "status": status,
                "gap": gap,
                "category": current_category,
            })

    # Compute category counts
    categories = {}
    for f in features:
        cat = f["category"]
        if cat not in categories:
            categories[cat] = {"HAVE": 0, "PARTIAL": 0, "MISSING": 0, "N/A": 0}
        s = f["status"]
        if s in categories[cat]:
            categories[cat][s] += 1

    return lines, features, categories


def update_gap_status(feature_name, new_status, evidence=None, gap_text=None, path=None):
    """Update a feature row's status and recompute summary counts atomically.

    Args:
        feature_name: Substring match against the feature column
        new_status: One of HAVE, PARTIAL, MISSING, N/A
        evidence: Optional text to append to gap column
        gap_text: Optional replacement for gap column
        path: Override gap map path

    Returns:
        dict with {updated: bool, feature: str, old_status: str, new_status: str, error: str|None}
    """
    if new_status not in VALID_STATUSES:
        return {"updated": False, "error": f"Invalid status: {new_status}"}

    p = Path(path) if path else GAP_MAP_PATH
    lines, features, categories = parse_gap_map(p)

    # Find the feature row (substring match, case-insensitive)
    target = None
    for f in features:
        if feature_name.lower() in f["feature"].lower():
            target = f
            break

    if not target:
        return {"updated": False, "error": f"Feature not found: {feature_name}"}

    if target["status"] == new_status and not evidence and not gap_text:
        return {"updated": False, "error": "No change needed"}

    old_status = target["status"]
    old_category = target["category"]

    # Update the row in lines
    line = lines[target["line_idx"]]
    # Replace **OLD_STATUS** with **NEW_STATUS**
    new_line = line.replace(f"**{old_status}**", f"**{new_status}**")

    # Update gap text if provided
    if gap_text is not None:
        # Replace the gap column (last column before final |)
        parts = new_line.rsplit("|", 2)
        if len(parts) >= 3:
            new_line = parts[0] + "| " + gap_text + " |"
    elif evidence:
        # Append evidence to existing gap text
        parts = new_line.rsplit("|", 2)
        if len(parts) >= 3:
            existing_gap = parts[1].strip()
            new_line = parts[0] + "| " + existing_gap + f" [{evidence}]" + " |"

    lines[target["line_idx"]] = new_line

    # Recompute category counts
    categories[old_category][old_status] -= 1
    categories[old_category][new_status] += 1

    # Rewrite summary table
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("| **TOTAL**"):
            # Compute totals
            totals = {"HAVE": 0, "PARTIAL": 0, "MISSING": 0, "N/A": 0}
            for cat_counts in categories.values():
                for s in totals:
                    totals[s] += cat_counts.get(s, 0)
            lines[i] = f"| **TOTAL** | **{totals['HAVE']}** | **{totals['PARTIAL']}** | **{totals['MISSING']}** | **{totals['N/A']}** |"
            continue

        summary_match = SUMMARY_ROW_RE.match(stripped)
        if summary_match:
            cat_name = summary_match.group(1).strip()
            # Find matching category
            for real_cat, counts in categories.items():
                if cat_name.lower() in real_cat.lower() or real_cat.lower() in cat_name.lower():
                    lines[i] = f"| {cat_name} | {counts['HAVE']} | {counts['PARTIAL']} | {counts['MISSING']} | {counts['N/A']} |"
                    break

    # Update the trailing summary line
    totals = {"HAVE": 0, "PARTIAL": 0, "MISSING": 0, "N/A": 0}
    for cat_counts in categories.values():
        for s in totals:
            totals[s] += cat_counts.get(s, 0)
    for i, line in enumerate(lines):
        if "features fully implemented" in line:
            lines[i] = f"**{totals['HAVE']} features fully implemented. {totals['PARTIAL']} partial. {totals['MISSING']} MISSING.**"

    # Atomic write
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "updated": True,
        "feature": target["feature"],
        "old_status": old_status,
        "new_status": new_status,
        "category": old_category,
    }


if __name__ == "__main__":
    # Dry-run: parse and show current state
    _, features, categories = parse_gap_map()
    totals = {"HAVE": 0, "PARTIAL": 0, "MISSING": 0, "N/A": 0}
    for cat, counts in sorted(categories.items()):
        for s in totals:
            totals[s] += counts.get(s, 0)
        print(f"  {cat}: {counts}")
    print(f"\nTOTAL: {totals}")
    print(f"Features parsed: {len(features)}")
