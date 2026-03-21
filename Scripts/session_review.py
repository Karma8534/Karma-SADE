#!/usr/bin/env python3
"""
session_review.py — Karma session ingestion pipeline, Phase 2.

Reads sessions from Logs/sessions_raw/ (JSON from IndexedDB) or
docs/ccSessions/ (Markdown transcripts), reviews each with a local
Ollama model, writes structured events to Logs/sessions_reviewed/.

Usage:
  python3 Scripts/session_review.py [--source md|json|both] [--limit N] [--force]

Env vars:
  OLLAMA_URL    default: http://localhost:11434
  REVIEW_MODEL  default: qwen3:8b
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.request
import urllib.error
import re

RAW_DIR      = pathlib.Path("Logs/sessions_raw")
CC_DIR       = pathlib.Path("docs/ccSessions")
REVIEWED_DIR = pathlib.Path("Logs/sessions_reviewed")

OLLAMA_URL   = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL        = os.environ.get("REVIEW_MODEL", "qwen3:8b")
CHUNK_SIZE   = 25
OVERLAP      = 2

REVIEW_PROMPT = """Review this Claude Code session excerpt. Extract ONLY high-signal events.

Return a JSON array of objects. Each object MUST have:
- "type": one of PITFALL, DECISION, PROOF, DIRECTION
- "title": short title under 80 chars
- "body": 2-3 sentences describing what happened, root cause (PITFALL), or what changed

Only extract events where losing this would force reconstruction later.
PITFALL = something broke, root cause identified
DECISION = architectural or process choice that closed an open question
PROOF = tested and confirmed working end-to-end
DIRECTION = course change with a reason that matters

Skip: status narration, routine file reads, progress updates, repeated summaries.

SESSION EXCERPT:
{turns}

Return ONLY valid JSON array, no preamble, no markdown fences.
If no high-signal events: []"""


def call_ollama(prompt: str) -> str:
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 2048}
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["response"].strip()
    except urllib.error.URLError as e:
        print(f"  [ollama] connection error: {e}", file=sys.stderr)
        return "[]"
    except Exception as e:
        print(f"  [ollama] error: {e}", file=sys.stderr)
        return "[]"


def parse_events(raw: str) -> list:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except Exception:
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass
        return []


def chunk_items(items: list, size: int, overlap: int) -> list:
    if len(items) <= size:
        return [items]
    chunks, i = [], 0
    while i < len(items):
        chunks.append(items[i:i + size])
        i += size - overlap
    return chunks


# ── JSON sessions (IndexedDB export) ─────────────────────────────────────────

def review_json_session(session: dict) -> list:
    turns = session.get("turns", session.get("messages", []))
    events = []
    for chunk in chunk_items(turns, CHUNK_SIZE, OVERLAP):
        lines = []
        for t in chunk:
            role = (t.get("role") or t.get("sender") or "unknown").upper()
            text = (t.get("text") or t.get("content") or "").strip()[:2500]
            lines.append(f"[{role}]: {text}")
        raw = call_ollama(REVIEW_PROMPT.format(turns="\n\n".join(lines)))
        events.extend(parse_events(raw))
    return events


def process_json_file(path: pathlib.Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    sessions = data if isinstance(data, list) else [data]
    all_events = []
    for s in sessions:
        ev    = review_json_session(s)
        date  = s.get("date", s.get("createdAt", ""))
        title = s.get("title", s.get("name", path.stem))
        for e in ev:
            e.setdefault("session_date", date)
            e.setdefault("session_title", title)
        all_events.extend(ev)
    return {"source": path.name, "event_count": len(all_events), "events": all_events}


# ── Markdown sessions (docs/ccSessions/ format) ───────────────────────────────

def parse_markdown_session(text: str) -> list:
    blocks = re.split(r"\n-{4,}\n", text)
    return [b.strip() for b in blocks if b.strip()]


def review_markdown_session(path: pathlib.Path) -> list:
    text   = path.read_text(encoding="utf-8")
    blocks = parse_markdown_session(text)
    events = []
    for chunk in chunk_items(blocks, CHUNK_SIZE, OVERLAP):
        turns_text = "\n\n---\n\n".join(chunk)
        raw = call_ollama(REVIEW_PROMPT.format(turns=turns_text[:12000]))
        events.extend(parse_events(raw))
    return events


def process_markdown_file(path: pathlib.Path) -> dict:
    events = review_markdown_session(path)
    m      = re.search(r"(\d{6,8})", path.stem)
    date   = m.group(1) if m else ""
    for e in events:
        e.setdefault("session_date", date)
        e.setdefault("session_title", path.stem)
    return {"source": path.name, "event_count": len(events), "events": events}


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Session ingestion pipeline — review step")
    parser.add_argument("--limit",  type=int, default=0,       help="Max files (0=all)")
    parser.add_argument("--source", choices=["json", "md", "both"], default="both")
    parser.add_argument("--force",  action="store_true",       help="Re-process already-reviewed files")
    args = parser.parse_args()

    REVIEWED_DIR.mkdir(parents=True, exist_ok=True)

    files_to_process = []
    if args.source in ("json", "both") and RAW_DIR.exists():
        files_to_process += [(p, "json") for p in sorted(RAW_DIR.glob("*.json"))]
    if args.source in ("md", "both") and CC_DIR.exists():
        files_to_process += [(p, "md") for p in sorted(CC_DIR.glob("*.md"))]

    if not files_to_process:
        print(f"No input files. Checked: {RAW_DIR}, {CC_DIR}")
        return

    if args.limit:
        files_to_process = files_to_process[:args.limit]

    total_events = 0
    for path, ftype in files_to_process:
        out_path = REVIEWED_DIR / (path.stem + ".json")
        if out_path.exists() and not args.force:
            print(f"SKIP {path.name} (already reviewed)")
            continue

        print(f"Processing {path.name} [{ftype}]...", end=" ", flush=True)
        result = process_json_file(path) if ftype == "json" else process_markdown_file(path)
        out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        total_events += result["event_count"]
        print(f"{result['event_count']} events → {out_path.name}")

    print(f"\nDone. Total events extracted: {total_events}")


if __name__ == "__main__":
    main()
