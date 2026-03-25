#!/usr/bin/env python3
"""
A1: JSONL Backfill — ingest Julian's CC session history into claude-mem.
Processes top-level UUID.jsonl files from the CC projects directory.
Extracts DECISION/PROOF/PITFALL/DIRECTION/INSIGHT events from assistant messages.
Saves each event as a claude-mem observation via HTTP API.
"""

import json
import os
import re
import sys
import glob
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
PROJECTS_DIR = os.path.expanduser(
    r"C:\Users\raest\.claude\projects\C--Users-raest-Documents-Karma-SADE"
)
WATERMARK_FILE = os.path.join(
    os.path.dirname(__file__), "..", ".harvest_watermark_jsonl.json"
)
CLAUDE_MEM_URL = "http://localhost:37777"
PROJECT_NAME   = "Karma_SADE"

# Event detection keywords — same bar as /harvest
EVENT_KEYWORDS = {
    "DECISION":  r"\b(DECISION|decided|decision)\b",
    "PROOF":     r"\b(PROOF|verified|confirmed|proved)\b",
    "PITFALL":   r"\b(PITFALL|pitfall|trap|gotcha|foot.?gun)\b",
    "DIRECTION": r"\b(DIRECTION|direction|pivot|reframe|course.?correct)\b",
    "INSIGHT":   r"\b(INSIGHT|insight|realization|breakthrough)\b",
}

CONTEXT_WINDOW = 400   # chars around the keyword match
MIN_TEXT_LEN   = 50    # skip very short text blobs


# ── Watermark ─────────────────────────────────────────────────────────────────
def load_watermark():
    try:
        with open(WATERMARK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_watermark(wm):
    os.makedirs(os.path.dirname(WATERMARK_FILE) or ".", exist_ok=True)
    with open(WATERMARK_FILE, "w", encoding="utf-8") as f:
        json.dump(wm, f, indent=2)


# ── claude-mem ────────────────────────────────────────────────────────────────
def save_observation(title: str, text: str, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"    [DRY-RUN] Would save: {title[:80]}")
        return True

    safe_text  = re.sub(r"[^\x20-\x7E\r\n]", "", text)[:3000]
    safe_title = re.sub(r"[^\x20-\x7E]", "", title)[:150]

    payload = json.dumps({
        "text":    safe_text,
        "title":   safe_title,
        "project": PROJECT_NAME,
    }).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{CLAUDE_MEM_URL}/api/memory/save",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            return bool(result.get("id") or result.get("success"))
    except Exception as e:
        print(f"    WARN: save_observation failed: {e}", file=sys.stderr)
        return False


# ── JSONL parsing ─────────────────────────────────────────────────────────────
def extract_text_from_content(content) -> list[str]:
    """Extract text strings from a CC message content field."""
    texts = []
    if isinstance(content, str):
        texts.append(content)
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                t = block.get("text") or block.get("thinking") or ""
                if t and isinstance(t, str):
                    texts.append(t)
    return texts


def find_events_in_text(text: str) -> list[tuple[str, str, str]]:
    """Return list of (event_type, title, snippet) for each event match."""
    events = []
    if len(text) < MIN_TEXT_LEN:
        return events

    for event_type, pattern in EVENT_KEYWORDS.items():
        for m in re.finditer(pattern, text, re.IGNORECASE):
            start = max(0, m.start() - CONTEXT_WINDOW)
            end   = min(len(text), m.end() + CONTEXT_WINDOW)
            snippet = text[start:end].strip()

            # Build a title from the first line after the keyword
            lines_after = text[m.start():m.start() + 200].strip().split("\n")
            first_line  = lines_after[0].strip() if lines_after else snippet[:80]
            title = f"[{event_type}] {first_line[:100]}"

            events.append((event_type, title, snippet))

    return events


def process_jsonl_file(filepath: str, dry_run: bool = False) -> int:
    """Process one JSONL file. Returns number of observations saved."""
    saved = 0
    seen_snippets = set()  # dedup within file

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Only process assistant messages
                if obj.get("type") != "assistant":
                    continue

                msg = obj.get("message", {})
                if not isinstance(msg, dict):
                    continue

                content = msg.get("content", [])
                texts   = extract_text_from_content(content)

                for text in texts:
                    events = find_events_in_text(text)
                    for event_type, title, snippet in events:
                        key = snippet[:100]
                        if key in seen_snippets:
                            continue
                        seen_snippets.add(key)

                        obs_text = (
                            f"Session: {os.path.basename(filepath)}\n"
                            f"Event: {event_type}\n\n"
                            f"{snippet}"
                        )
                        if save_observation(title, obs_text, dry_run):
                            saved += 1
                            safe_title = title[:70].encode('ascii', 'replace').decode()
                            print(f"    SAVED [{event_type}]: {safe_title}")
                            time.sleep(0.05)  # gentle rate limit

    except Exception as e:
        print(f"  ERROR reading {filepath}: {e}", file=sys.stderr)

    return saved


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    dry_run    = "--dry-run" in sys.argv
    single     = next((a for a in sys.argv[1:] if not a.startswith("--")), None)
    force_all  = "--force" in sys.argv

    if dry_run:
        print("DRY-RUN MODE — no observations will be saved")

    watermark = load_watermark()

    if single:
        # Process one specific file
        files = [single]
    else:
        # Glob top-level UUID.jsonl files only (not subagents)
        pattern = os.path.join(PROJECTS_DIR, "*.jsonl")
        files   = [f for f in glob.glob(pattern)
                   if "subagents" not in f.replace("\\", "/")]

    print(f"Files to process: {len(files)} | Dry-run: {dry_run}")

    total_saved = 0
    skipped     = 0

    for filepath in sorted(files):
        fname = os.path.basename(filepath)

        if not force_all and watermark.get(fname):
            skipped += 1
            continue

        print(f"\nProcessing: {fname}")
        n = process_jsonl_file(filepath, dry_run)
        total_saved += n
        print(f"  -> {n} observations saved")

        if not dry_run:
            watermark[fname] = datetime.utcnow().isoformat() + "Z"
            save_watermark(watermark)

    print(f"\n{'='*50}")
    print(f"Total saved: {total_saved} | Skipped (already done): {skipped}")
    print(f"Watermark: {WATERMARK_FILE}")


if __name__ == "__main__":
    main()
