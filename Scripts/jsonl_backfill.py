#!/usr/bin/env python3
"""
A1: JSONL Backfill — ingest Julian's CC session history into claude-mem.
Extracts save_observation tool_use calls from CC session JSONL files.
Each tool call's input (text + title) is re-saved to claude-mem.

Root cause of v1 failure: regex-matched common English words (verified,
confirmed, decided) instead of extracting actual structured events.
Fix: extract the real save_observation tool_use inputs from JSONL.
"""

import json
import os
import re
import sys
import glob
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Config ────────────────────────────────────────────────────────────────────
PROJECTS_DIR = os.path.expanduser(
    r"C:\Users\raest\.claude\projects\C--Users-raest-Documents-Karma-SADE"
)
WATERMARK_FILE = os.path.join(
    os.path.dirname(__file__), "..", ".harvest_watermark_jsonl.json"
)
CLAUDE_MEM_URL = "http://localhost:37778"
PROJECT_NAME   = "Karma_SADE"

# Tool names that represent save_observation calls
SAVE_OBS_NAMES = {
    "mcp__plugin_claude-mem_mcp-search__save_observation",
    "save_observation",
}

MIN_TEXT_LEN = 30  # skip trivially short observations


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
def save_to_claude_mem(title: str, text: str, dry_run: bool = False) -> bool:
    if dry_run:
        print(f"    [DRY-RUN] Would save: {title[:80]}")
        return True

    # Sanitize but preserve unicode — only strip control chars
    safe_text  = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)[:4000]
    safe_title = re.sub(r"[\x00-\x1f\x7f]", "", title)[:200]

    if len(safe_text.strip()) < MIN_TEXT_LEN:
        return False

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
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return bool(result.get("id") or result.get("success"))
    except Exception as e:
        print(f"    WARN: save failed: {e}", file=sys.stderr)
        return False


# ── JSONL parsing ─────────────────────────────────────────────────────────────
def extract_tool_use_observations(filepath: str) -> list[dict]:
    """Extract save_observation tool_use inputs from a CC session JSONL file.

    Returns list of dicts with 'title' and 'text' keys.
    """
    observations = []
    seen_texts = set()

    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Quick filter — skip lines without save_observation
                if "save_observation" not in line:
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
                if not isinstance(content, list):
                    continue

                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") != "tool_use":
                        continue

                    name = block.get("name", "")
                    if name not in SAVE_OBS_NAMES:
                        continue

                    inp = block.get("input", {})
                    if not isinstance(inp, dict):
                        continue

                    text  = inp.get("text", "").strip()
                    title = inp.get("title", "").strip()

                    if not text or len(text) < MIN_TEXT_LEN:
                        continue

                    # Dedup within file by text prefix
                    dedup_key = text[:200]
                    if dedup_key in seen_texts:
                        continue
                    seen_texts.add(dedup_key)

                    # Generate title if missing
                    if not title:
                        first_line = text.split("\n")[0][:120]
                        title = f"Session obs: {first_line}"

                    observations.append({"title": title, "text": text})

    except Exception as e:
        print(f"  ERROR reading {filepath}: {e}", file=sys.stderr)

    return observations


def process_jsonl_file(filepath: str, dry_run: bool = False) -> int:
    """Process one JSONL file. Returns number of observations saved."""
    observations = extract_tool_use_observations(filepath)
    saved = 0

    for obs in observations:
        fname = os.path.basename(filepath)[:8]
        # Prefix title with session UUID fragment for traceability
        title = obs["title"]
        text  = f"Source: {os.path.basename(filepath)}\n\n{obs['text']}"

        if save_to_claude_mem(title, text, dry_run):
            saved += 1
            safe_title = title[:70].encode('ascii', 'replace').decode()
            print(f"    SAVED: {safe_title}")
            time.sleep(0.02)  # gentle rate limit

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
        files = [single]
    else:
        # Glob top-level UUID.jsonl files only (not subagents)
        pattern = os.path.join(PROJECTS_DIR, "*.jsonl")
        files   = [f for f in glob.glob(pattern)
                   if "subagents" not in f.replace("\\", "/")]

    print(f"Files to process: {len(files)} | Dry-run: {dry_run} | Force: {force_all}")

    total_saved = 0
    total_found = 0
    skipped     = 0

    for filepath in sorted(files):
        fname = os.path.basename(filepath)

        if not force_all and watermark.get(fname):
            skipped += 1
            continue

        # Quick check: does this file have save_observation calls?
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content_sample = f.read()
            if "save_observation" not in content_sample:
                # No observations in this file — mark done and skip
                if not dry_run:
                    watermark[fname] = datetime.now(timezone.utc).isoformat()
                    save_watermark(watermark)
                continue
        except Exception:
            continue

        observations = extract_tool_use_observations(filepath)
        total_found += len(observations)

        if not observations:
            if not dry_run:
                watermark[fname] = datetime.now(timezone.utc).isoformat()
                save_watermark(watermark)
            continue

        print(f"\nProcessing: {fname} ({len(observations)} observations)")
        n = process_jsonl_file(filepath, dry_run)
        total_saved += n
        print(f"  -> {n}/{len(observations)} saved")

        if not dry_run:
            watermark[fname] = datetime.now(timezone.utc).isoformat()
            save_watermark(watermark)

    print(f"\n{'='*50}")
    print(f"Total found: {total_found} | Saved: {total_saved} | Skipped (watermarked): {skipped}")
    print(f"Watermark: {WATERMARK_FILE}")


if __name__ == "__main__":
    main()

