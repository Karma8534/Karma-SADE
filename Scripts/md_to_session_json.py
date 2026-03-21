#!/usr/bin/env python3
"""
md_to_session_json.py — Converts docs/ccSessions/*.md transcripts to
sessions_raw JSON format compatible with session_review.py.

Usage: python3 Scripts/md_to_session_json.py docs/ccSessions/CCSession032026A.md
Output: Logs/sessions_raw/CCSession032026A.json
"""
import json, re, sys, pathlib, datetime

RAW_DIR = pathlib.Path("Logs/sessions_raw")

def parse_md_transcript(path):
    text = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    turns = []
    current_role = None
    current_lines = []

    # Detect role headers: "Human:", "Assistant:", or markdown H2/H3 headers
    role_patterns = [
        (re.compile(r'^#{1,3}\s*(Human|User)\s*:?\s*$', re.I), 'user'),
        (re.compile(r'^#{1,3}\s*(Assistant|Claude|CC)\s*:?\s*$', re.I), 'assistant'),
        (re.compile(r'^\*\*(Human|User)\*\*\s*:?', re.I), 'user'),
        (re.compile(r'^\*\*(Assistant|Claude|CC)\*\*\s*:?', re.I), 'assistant'),
    ]

    def flush():
        if current_role and current_lines:
            text_block = "\n".join(current_lines).strip()
            if text_block:
                turns.append({"role": current_role, "text": text_block[:6000]})

    for line in lines:
        detected = None
        for pattern, role in role_patterns:
            if pattern.match(line):
                detected = role
                break

        if detected:
            flush()
            current_role = detected
            current_lines = []
        else:
            if current_role is not None:
                current_lines.append(line)

    flush()

    # Fallback: if no turns detected, split on blank-line boundaries and alternate roles
    if not turns:
        chunks = re.split(r'\n{3,}', text)
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if chunk:
                turns.append({
                    "role": "user" if i % 2 == 0 else "assistant",
                    "text": chunk[:6000]
                })

    return turns


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 Scripts/md_to_session_json.py <path_to_md>")
        sys.exit(1)

    input_path = pathlib.Path(sys.argv[1])
    if not input_path.exists():
        print(f"File not found: {input_path}")
        sys.exit(1)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    turns = parse_md_transcript(input_path)
    out_name = input_path.stem + ".json"
    out_path = RAW_DIR / out_name

    session = {
        "id": input_path.stem,
        "date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "title": input_path.stem,
        "turns": turns
    }

    out_path.write_text(json.dumps([session], indent=2))
    print(f"OK: {len(turns)} turns -> {out_path}")


if __name__ == "__main__":
    main()
