#!/usr/bin/env python3
"""
extract_cc_sessions.py — Extract CC session JSONL files into reviewable text.
Reads ~/.claude/projects/C--Users-raest-Documents-Karma-SADE/*.jsonl
Outputs one JSON file per session to Logs/sessions_raw/
"""
import ast
import json
import pathlib
import sys
from datetime import datetime

SESSIONS_DIR = pathlib.Path.home() / ".claude/projects/C--Users-raest-Documents-Karma-SADE"
OUTPUT_DIR   = pathlib.Path("Logs/sessions_raw")
LIMIT        = int(sys.argv[1]) if len(sys.argv) > 1 else 0  # 0 = all
MIN_TURNS    = int(sys.argv[2]) if len(sys.argv) > 2 else 3  # skip tiny sessions


def parse_message_field(raw):
    """Parse the 'message' field which is a Python repr string."""
    if isinstance(raw, dict):
        return raw
    try:
        return ast.literal_eval(str(raw))
    except Exception:
        return {}


def extract_text_from_content(content):
    """Extract plain text from content (string or list of blocks)."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                t = block.get("type", "")
                if t == "text":
                    parts.append(block.get("text", "").strip())
                elif t == "thinking":
                    pass  # skip thinking blocks
                # Skip tool_use, tool_result
        return "\n".join(p for p in parts if p)
    return ""


def parse_session(path):
    turns = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception:
                continue

            mtype = msg.get("type", "")
            if mtype not in ("user", "assistant"):
                continue

            raw_msg = msg.get("message", "")
            parsed  = parse_message_field(raw_msg)
            role    = parsed.get("role", mtype)
            content = parsed.get("content", "")
            text    = extract_text_from_content(content)

            if not text or len(text) < 15:
                continue

            turns.append({
                "role": role,
                "text": text[:4000],
                "ts":   msg.get("timestamp", "")
            })
    except Exception as e:
        return None, str(e)
    return turns, None


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(SESSIONS_DIR.glob("*.jsonl"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    if LIMIT:
        files = files[:LIMIT]

    processed = skipped = tiny = 0
    for path in files:
        out = OUTPUT_DIR / (path.stem + ".json")
        if out.exists():
            skipped += 1
            continue

        turns, err = parse_session(path)
        if err or not turns:
            tiny += 1
            continue
        if len(turns) < MIN_TURNS:
            tiny += 1
            continue

        date = ""
        if turns and turns[0].get("ts"):
            date = turns[0]["ts"][:10]
        else:
            date = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d")

        session = {
            "id":    path.stem,
            "date":  date,
            "title": f"CC Session {date} ({len(turns)} turns)",
            "turns": turns
        }
        out.write_text(json.dumps(session, indent=2, ensure_ascii=False), encoding="utf-8")
        processed += 1

    print(f"Processed: {processed}, Skipped (done): {skipped}, Too small: {tiny}, Total: {len(files)}")


if __name__ == "__main__":
    main()
