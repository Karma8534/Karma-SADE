#!/usr/bin/env python3
"""
session_review.py — Phase 2 of session ingestion pipeline.
Reads sessions_raw/*.json, reviews with local Ollama qwen3:8b,
writes structured events to sessions_reviewed/*.json.
Run on K2 (http://100.75.109.92:11434) or P1 (http://localhost:11434).
"""
import json, os, glob, pathlib, urllib.request, urllib.error, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

RAW_DIR      = pathlib.Path("Logs/sessions_raw")
REVIEWED_DIR = pathlib.Path("Logs/sessions_reviewed")
OLLAMA_URL   = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL        = os.environ.get("REVIEW_MODEL", "qwen3:8b")
CHUNK_SIZE   = 20  # turns per chunk
OVERLAP      = 2   # overlap between chunks

REVIEW_PROMPT = """Review this Claude Code session excerpt. Extract ONLY high-signal events.

Return a JSON array of objects. Each object must have:
- "type": one of PITFALL, DECISION, PROOF, DIRECTION
- "title": short title (under 80 chars)
- "body": 2-3 sentences — what happened, root cause (if pitfall), what changed

Only extract events where losing this would force reconstruction later.
Skip: status narration, routine file reads, progress updates.

SESSION EXCERPT:
{turns}

Return ONLY valid JSON array, no explanation, no markdown fences.
Example: [{{"type":"PITFALL","title":"hub-bridge sync misses lib/ files","body":"When syncing hub-bridge code, only server.js was copied but lib/*.js files were missed, causing stale code in the container. The build context is at /opt/seed-vault/.../hub_bridge/ and requires explicit per-file copies. cp -r does NOT overwrite existing files in dest/."}}]
If no high-signal events: return []"""


def call_ollama(prompt):
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
    except Exception as e:
        print(f"    -> ollama error: {e}")
        return "[]"


def chunk_turns(turns):
    if len(turns) <= CHUNK_SIZE:
        return [turns]
    chunks = []
    i = 0
    while i < len(turns):
        chunks.append(turns[i:i + CHUNK_SIZE])
        i += CHUNK_SIZE - OVERLAP
    return chunks


def format_turns(turns):
    lines = []
    for t in turns:
        role = (t.get("role") or "unknown").upper()
        text = (t.get("text") or "").strip()[:2000]
        lines.append(f"[{role}]: {text}")
    return "\n\n".join(lines)


def review_session(session):
    turns  = session.get("turns", [])
    events = []
    for i, chunk in enumerate(chunk_turns(turns)):
        print(f"  chunk {i+1}/{len(chunk_turns(turns))} ({len(chunk)} turns)...")
        prompt   = REVIEW_PROMPT.format(turns=format_turns(chunk))
        raw      = call_ollama(prompt)
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        try:
            chunk_events = json.loads(raw)
            if isinstance(chunk_events, list):
                events.extend(chunk_events)
                print(f"    -> {len(chunk_events)} events")
        except Exception as ex:
            print(f"    -> parse error: {ex}")
    return events


def main():
    REVIEWED_DIR.mkdir(parents=True, exist_ok=True)
    raw_files = sorted(RAW_DIR.glob("*.json"))
    if not raw_files:
        print(f"No files in {RAW_DIR}")
        return

    for path in raw_files:
        out_path = REVIEWED_DIR / path.name
        if out_path.exists():
            print(f"SKIP {path.name} (already reviewed)")
            continue

        print(f"Reviewing {path.name}...")
        with open(path) as f:
            data = json.load(f)

        sessions = data if isinstance(data, list) else [data]
        all_events = []
        for s in sessions:
            print(f"  session: {s.get('title','')} ({len(s.get('turns',[]))} turns)")
            events = review_session(s)
            for e in events:
                e["session_date"] = s.get("date", "")
                e["session_title"] = s.get("title", "")
            all_events.extend(events)

        out_path.write_text(json.dumps({
            "source": path.name,
            "event_count": len(all_events),
            "events": all_events
        }, indent=2))
        print(f"DONE {path.name} -> {len(all_events)} events")


if __name__ == "__main__":
    main()
