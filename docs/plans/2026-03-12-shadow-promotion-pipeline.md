# Shadow.md Promotion Pipeline — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a K2 cron job that extracts durable facts from shadow.md using local Ollama and POSTs them to Aria's /api/facts, making them visible in Karma's context via the existing memory graph pipeline.

**Architecture:** Python script on K2 reads shadow.md incrementally (watermark-based), sends new content to Ollama qwen3-coder:30b for fact extraction, POSTs extracted facts to Aria's /api/facts endpoint with X-Aria-Service-Key auth. Cron runs every 30 minutes. Zero Anthropic cost.

**Tech Stack:** Python 3.12, requests library, Ollama API (http://host.docker.internal:11434), Aria API (localhost:7890)

---

## Verified Environment (K2)

- Python 3.12 at `/usr/bin/python3`, `requests 2.31.0` installed
- Ollama at `http://host.docker.internal:11434` with `qwen3-coder:30b` available
- Aria at `localhost:7890`, auth via `X-Aria-Service-Key` header
- shadow.md at `/mnt/c/dev/Karma/k2/cache/shadow.md` (75 lines, 3712 bytes)
- Scripts dir: `/mnt/c/dev/Karma/k2/scripts/`
- Logs dir: `/mnt/c/dev/Karma/k2/logs/`
- ARIA_SERVICE_KEY: in running aria process env — script reads from `/mnt/c/dev/Karma/k2/scripts/.aria_service_key`

## API Details

**Ollama** — `POST http://host.docker.internal:11434/api/generate`
```json
{"model": "qwen3-coder:30b", "prompt": "...", "stream": false}
```
Returns: `{"response": "...", ...}`

**Aria /api/facts** — `POST http://localhost:7890/api/facts`
```json
{
  "content": "fact text here",
  "fact_type": "project|decision|architecture|preference",
  "confidence": 0.8,
  "source": "shadow-promotion",
  "tags": ["shadow", "promoted"]
}
```
Headers: `Content-Type: application/json`, `X-Aria-Service-Key: <key>`
Returns: `{"fact_id": N, "success": true, "actor_id": "..."}`

---

### Task 1: Create the service key file on K2

**Files:**
- Create: `/mnt/c/dev/Karma/k2/scripts/.aria_service_key` (on K2, via SSH)

**Step 1: Write the key file**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'cat /proc/29921/environ | tr \"\\0\" \"\\n\" | grep ARIA_SERVICE_KEY | cut -d= -f2 > /mnt/c/dev/Karma/k2/scripts/.aria_service_key && chmod 600 /mnt/c/dev/Karma/k2/scripts/.aria_service_key && echo DONE'"
```

Note: PID 29921 may change after aria restarts. More robust: read from systemd env or hardcode extraction. If PID changed, find it with `ps aux | grep aria.py`.

**Step 2: Verify**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'wc -c /mnt/c/dev/Karma/k2/scripts/.aria_service_key'"
```
Expected: `44` (43 chars + newline)

---

### Task 2: Write promote_shadow.py

**Files:**
- Create: `C:\Users\raest\Documents\Karma_SADE\scripts\promote_shadow.py` (local, then scp to K2)

**Step 1: Write the script**

```python
#!/usr/bin/env python3
"""
promote_shadow.py — Extract durable facts from shadow.md and POST to Aria /api/facts.
Runs on K2 via cron. Uses local Ollama (qwen3-coder:30b). Zero Anthropic cost.
"""

import json
import os
import sys
import time
import requests
from pathlib import Path
from datetime import datetime, timezone

# --- Config ---
SHADOW_PATH = Path("/mnt/c/dev/Karma/k2/cache/shadow.md")
WATERMARK_PATH = Path("/mnt/c/dev/Karma/k2/scripts/.shadow_watermark")
SERVICE_KEY_PATH = Path("/mnt/c/dev/Karma/k2/scripts/.aria_service_key")
LOG_PREFIX = f"[{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}]"

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


def read_service_key():
    if not SERVICE_KEY_PATH.exists():
        print(f"{LOG_PREFIX} ERROR: Service key file not found at {SERVICE_KEY_PATH}", file=sys.stderr)
        sys.exit(1)
    return SERVICE_KEY_PATH.read_text().strip()


def read_watermark():
    if not WATERMARK_PATH.exists():
        return 0
    try:
        val = int(WATERMARK_PATH.read_text().strip())
        return val
    except (ValueError, OSError):
        return 0


def write_watermark(offset):
    WATERMARK_PATH.write_text(str(offset))


def read_new_content(watermark):
    if not SHADOW_PATH.exists():
        print(f"{LOG_PREFIX} shadow.md not found at {SHADOW_PATH}")
        return "", watermark

    file_size = SHADOW_PATH.stat().st_size
    if file_size < watermark:
        # File was truncated/replaced — reset
        print(f"{LOG_PREFIX} shadow.md truncated (size {file_size} < watermark {watermark}), resetting to 0")
        watermark = 0

    if file_size == watermark:
        print(f"{LOG_PREFIX} No new content (size={file_size})")
        return "", watermark

    with open(SHADOW_PATH, "r", encoding="utf-8") as f:
        f.seek(watermark)
        content = f.read()

    print(f"{LOG_PREFIX} Read {len(content)} new chars from offset {watermark}")
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
        print(f"{LOG_PREFIX} ERROR calling Ollama: {e}", file=sys.stderr)
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

    print(f"{LOG_PREFIX} Extracted {len(facts)} facts from Ollama")
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
            print(f"{LOG_PREFIX} Posted fact #{result.get('fact_id', '?')}: {fact['content'][:60]}...")
            return True
        else:
            print(f"{LOG_PREFIX} ERROR posting fact: HTTP {resp.status_code} — {resp.text[:200]}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"{LOG_PREFIX} ERROR posting fact: {e}", file=sys.stderr)
        return False


def main():
    print(f"{LOG_PREFIX} promote_shadow.py starting")

    service_key = read_service_key()
    watermark = read_watermark()
    content, new_watermark = read_new_content(watermark)

    if not content.strip():
        write_watermark(new_watermark)
        print(f"{LOG_PREFIX} Nothing to process. Done.")
        return

    facts = extract_facts(content)

    if not facts:
        write_watermark(new_watermark)
        print(f"{LOG_PREFIX} No facts extracted. Watermark advanced to {new_watermark}.")
        return

    posted = 0
    for fact in facts:
        if post_fact(service_key, fact):
            posted += 1
            time.sleep(0.5)  # gentle rate limiting

    write_watermark(new_watermark)
    print(f"{LOG_PREFIX} Done. Posted {posted}/{len(facts)} facts. Watermark: {new_watermark}")


if __name__ == "__main__":
    main()
```

**Step 2: Verify syntax locally**

Run: `python3 -c "import ast; ast.parse(open('scripts/promote_shadow.py').read()); print('SYNTAX OK')"`
Expected: `SYNTAX OK`

**Step 3: Commit**

```bash
git add scripts/promote_shadow.py
git commit -m "feat: add shadow.md promotion pipeline script for K2"
```

---

### Task 3: Deploy script to K2

**Step 1: SCP script to K2**

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
ssh vault-neo "scp -P 2223 /home/neo/karma-sade/scripts/promote_shadow.py karma@localhost:/mnt/c/dev/Karma/k2/scripts/promote_shadow.py"
```

**Step 2: Verify on K2**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'ls -la /mnt/c/dev/Karma/k2/scripts/promote_shadow.py && head -3 /mnt/c/dev/Karma/k2/scripts/promote_shadow.py'"
```
Expected: file exists, shows shebang line

**Step 3: Make executable**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'chmod +x /mnt/c/dev/Karma/k2/scripts/promote_shadow.py'"
```

---

### Task 4: Test the script manually

**Step 1: Dry run — check Ollama connectivity**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'curl -s http://host.docker.internal:11434/api/generate -d \"{\\\"model\\\": \\\"qwen3-coder:30b\\\", \\\"prompt\\\": \\\"Say hello\\\", \\\"stream\\\": false}\" | python3 -c \"import sys,json; print(json.load(sys.stdin).get(\\\"response\\\",\\\"\\\")[:50])\"'"
```
Expected: Some text response from Ollama

**Step 2: Run the script**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'cd /mnt/c/dev/Karma/k2/scripts && python3 promote_shadow.py 2>&1'"
```
Expected: Log lines showing content read, facts extracted, facts posted with IDs

**Step 3: Verify facts appeared in Aria**

```bash
ssh vault-neo "ARIA_KEY=\$(ssh -p 2223 -l karma localhost 'cat /mnt/c/dev/Karma/k2/scripts/.aria_service_key') && curl -s 'http://100.75.109.92:7890/api/facts?source=shadow-promotion' -H \"X-Aria-Service-Key: \$ARIA_KEY\" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(f\"Count: {d[\\\"count\\\"]}\"); [print(f\"  #{f[\\\"id\\\"]}: {f[\\\"content\\\"][:80]}\") for f in d[\\\"facts\\\"][:5]]'"
```
Expected: Facts with source=shadow-promotion visible

**Step 4: Verify facts reach memory graph**

```bash
ssh vault-neo "ARIA_KEY=\$(ssh -p 2223 -l karma localhost 'cat /mnt/c/dev/Karma/k2/scripts/.aria_service_key') && curl -s 'http://100.75.109.92:7890/api/memory/graph?query=shadow+promotion+architecture' -H \"X-Aria-Service-Key: \$ARIA_KEY\" | python3 -c 'import sys,json; d=json.load(sys.stdin); ctx=d.get(\"graph_context\",{}); print(f\"Seed: {len(ctx.get(\\\"seed_facts\\\",[])) }, Related: {len(ctx.get(\\\"related_facts\\\",[])) }\")'"
```
Expected: seed_facts > 0

**Step 5: Verify watermark advanced**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'cat /mnt/c/dev/Karma/k2/scripts/.shadow_watermark'"
```
Expected: A number matching shadow.md file size (3712 or current)

---

### Task 5: Set up cron on K2

**Step 1: Add cron entry**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'crontab -l 2>/dev/null; echo \"*/30 * * * * /usr/bin/python3 /mnt/c/dev/Karma/k2/scripts/promote_shadow.py >> /mnt/c/dev/Karma/k2/logs/promote_shadow.log 2>&1\"' | ssh vault-neo 'ssh -p 2223 -l karma localhost crontab -'"
```

Simpler alternative if piping is problematic:
```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'echo \"*/30 * * * * /usr/bin/python3 /mnt/c/dev/Karma/k2/scripts/promote_shadow.py >> /mnt/c/dev/Karma/k2/logs/promote_shadow.log 2>&1\" >> /tmp/cron_promote && crontab -l 2>/dev/null >> /tmp/cron_promote && crontab /tmp/cron_promote && rm /tmp/cron_promote'"
```

**Step 2: Verify cron registered**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'crontab -l | grep promote_shadow'"
```
Expected: `*/30 * * * * /usr/bin/python3 /mnt/c/dev/Karma/k2/scripts/promote_shadow.py >> /mnt/c/dev/Karma/k2/logs/promote_shadow.log 2>&1`

**Step 3: Ensure logs dir exists**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'mkdir -p /mnt/c/dev/Karma/k2/logs && echo OK'"
```

**Step 4: Commit cron documentation**

Update design doc or MEMORY.md with cron status.

---

### Task 6: End-to-end verification

**Step 1: Wait for next cron run or trigger manually**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'python3 /mnt/c/dev/Karma/k2/scripts/promote_shadow.py 2>&1'"
```

**Step 2: Check log output**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'tail -20 /mnt/c/dev/Karma/k2/logs/promote_shadow.log'"
```

**Step 3: Verify in Karma's context**

Send a test message to Karma via hub.arknexus.net and check if promoted facts appear in the `--- ARIA K2 MEMORY GRAPH ---` context block. Or check via API:

```bash
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What do you know about the shadow promotion pipeline?"}' | python3 -c 'import sys,json; r=json.load(sys.stdin); print(r.get("assistant_text","")[:300])'
```

**Step 4: Commit and push final state**

```bash
git add -A
git commit -m "feat: shadow.md promotion pipeline — deployed and verified on K2"
git push origin main
```
