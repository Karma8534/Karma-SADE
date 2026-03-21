#!/usr/bin/env python3
"""
session_obs_writer.py — Karma session ingestion pipeline, Phase 3 prep.

Reads all reviewed event files, deduplicates by title similarity,
and prints observations to stdout for CC to write to claude-mem.

Usage:
  python3 Scripts/session_obs_writer.py [MAX_EMIT]

CC reads the output and calls mcp__plugin_claude-mem_mcp-search__save_observation
for each observation block.
"""
import json
import pathlib
import sys
import re

REVIEWED_DIR = pathlib.Path("Logs/sessions_reviewed")
MAX_EMIT     = int(sys.argv[1]) if len(sys.argv) > 1 else 50

TYPE_PRIORITY = {"PITFALL": 0, "DECISION": 1, "PROOF": 2, "DIRECTION": 3}


def title_key(title: str) -> str:
    """Normalize title for dedup comparison."""
    return re.sub(r"[^a-z0-9]", "", title.lower())


def main():
    if not REVIEWED_DIR.exists():
        print(f"ERROR: {REVIEWED_DIR} does not exist. Run session_review.py first.")
        sys.exit(1)

    all_events = []
    for path in sorted(REVIEWED_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"WARN: could not read {path.name}: {e}", file=sys.stderr)
            continue
        for e in data.get("events", []):
            if not isinstance(e, dict):
                continue
            e["_source_file"] = path.stem
            all_events.append(e)

    # Sort by type priority
    all_events.sort(key=lambda e: TYPE_PRIORITY.get(e.get("type", ""), 9))

    # Deduplicate by normalized title
    seen_keys = set()
    deduped   = []
    for e in all_events:
        k = title_key(e.get("title", ""))
        if k and k not in seen_keys:
            seen_keys.add(k)
            deduped.append(e)

    print(f"Total events: {len(all_events)}, after dedup: {len(deduped)}, emitting top {MAX_EMIT}")
    print("=" * 60)

    for e in deduped[:MAX_EMIT]:
        etype  = e.get("type", "UNKNOWN")
        title  = e.get("title", "(no title)")
        body   = e.get("body", "")
        date   = e.get("session_date", "")
        src    = e.get("session_title", e.get("_source_file", ""))

        obs_title = f"[{etype}] {title}"
        obs_text  = f"{body}"
        if date or src:
            obs_text += f"\n\nSession: {date} — {src}"

        print(json.dumps({
            "title":   obs_title,
            "text":    obs_text,
            "project": "Karma_SADE",
            "type":    etype
        }, indent=2))
        print("---")


if __name__ == "__main__":
    main()
