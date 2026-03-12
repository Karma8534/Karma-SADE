#!/usr/bin/env python3
"""
promote_shadow.py — Extract durable facts from shadow.md and POST to Aria /api/facts.
Runs on K2 via cron. Uses local Ollama (qwen3-coder:30b). Zero Anthropic cost.
"""

import json
import sys
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

# --- Config ---
SHADOW_PATH = Path("/mnt/c/dev/Karma/k2/cache/shadow.md")
WATERMARK_PATH = Path("/mnt/c/dev/Karma/k2/scripts/.shadow_watermark")
SERVICE_KEY_PATH = Path("/mnt/c/dev/Karma/k2/scripts/.aria_service_key")

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
OLLAMA_MODEL = "qwen3-coder:30b"
ARIA_FACTS_URL = "http://localhost:7890/api/facts"

EXTRACTION_PROMPT = """You are a fact extractor for a software project called Karma.
Given a block of developer notes from shadow.md, extract ONLY durable facts worth remembering long-term.

Focus on:
- Architectural decisions (e.g., "K2 uses Ollama for local inference")
- Direction changes (e.g., "Switched from ChromaDB to FAISS for search")
- Project facts (e.g., "FalkorDB graph name is neo_workspace")
- Preferences (e.g., "Never use paid API for extraction tasks")

Do NOT extract:
- Ephemeral session notes or todos
- Debugging steps or temporary workarounds
- Obvious facts that any developer would know
- Duplicate information already well-documented

For each fact, output a JSON object on its own line with these fields:
- "content": the fact (1-2 sentences, precise)
- "fact_type": one of "project", "decision", "architecture", "preference"

Output ONLY valid JSON lines, one per fact. No markdown, no commentary.
If there are no extractable facts, output nothing.

--- NOTES ---
{content}
--- END ---"""


def log(msg):
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[{ts}] {msg}")


def read_service_key():
    if not SERVICE_KEY_PATH.exists():
        log(f"ERROR: Service key file not found at {SERVICE_KEY_PATH}")
        sys.exit(1)
    return SERVICE_KEY_PATH.read_text().strip()


def read_watermark():
    if not WATERMARK_PATH.exists():
        return 0
    try:
        return int(WATERMARK_PATH.read_text().strip())
    except (ValueError, OSError):
        return 0


def write_watermark(offset):
    WATERMARK_PATH.write_text(str(offset))


def read_new_content(watermark):
    if not SHADOW_PATH.exists():
        log(f"shadow.md not found at {SHADOW_PATH}")
        return "", watermark

    file_size = SHADOW_PATH.stat().st_size
    if file_size < watermark:
        log(f"shadow.md truncated (size {file_size} < watermark {watermark}), resetting to 0")
        watermark = 0

    if file_size == watermark:
        log(f"No new content (size={file_size})")
        return "", watermark

    with open(SHADOW_PATH, "r", encoding="utf-8") as f:
        f.seek(watermark)
        content = f.read()

    log(f"Read {len(content)} new chars from offset {watermark}")
    return content, file_size


def extract_facts(content):
    prompt = EXTRACTION_PROMPT.format(content=content)
    try:
        resp = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_predict": 2048}
        }, timeout=120)
        resp.raise_for_status()
        raw = resp.json().get("response", "")
    except Exception as e:
        log(f"ERROR calling Ollama: {e}")
        return []

    facts = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if "content" in obj and "fact_type" in obj:
                if obj["fact_type"] not in ("project", "decision", "architecture", "preference"):
                    obj["fact_type"] = "project"
                facts.append(obj)
        except json.JSONDecodeError:
            continue

    log(f"Extracted {len(facts)} facts from Ollama")
    return facts


def post_fact(service_key, fact):
    payload = {
        "content": fact["content"],
        "fact_type": fact["fact_type"],
        "confidence": 0.8,
        "source": "shadow-promotion",
        "tags": ["shadow", "promoted", fact["fact_type"]]
    }
    headers = {
        "Content-Type": "application/json",
        "X-Aria-Service-Key": service_key
    }
    try:
        resp = requests.post(ARIA_FACTS_URL, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            result = resp.json()
            log(f"Posted fact #{result.get('fact_id', '?')}: {fact['content'][:60]}...")
            return True
        else:
            log(f"ERROR posting fact: HTTP {resp.status_code} — {resp.text[:200]}")
            return False
    except Exception as e:
        log(f"ERROR posting fact: {e}")
        return False


def main():
    log("promote_shadow.py starting")

    service_key = read_service_key()
    watermark = read_watermark()
    content, new_watermark = read_new_content(watermark)

    if not content.strip():
        write_watermark(new_watermark)
        log("Nothing to process. Done.")
        return

    facts = extract_facts(content)

    if not facts:
        write_watermark(new_watermark)
        log(f"No facts extracted. Watermark advanced to {new_watermark}.")
        return

    posted = 0
    for fact in facts:
        if post_fact(service_key, fact):
            posted += 1
            time.sleep(0.5)

    write_watermark(new_watermark)
    log(f"Done. Posted {posted}/{len(facts)} facts. Watermark: {new_watermark}")


if __name__ == "__main__":
    main()
