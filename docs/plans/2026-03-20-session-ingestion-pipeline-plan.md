# Session Ingestion Pipeline Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extract all 108+ Claude desktop sessions from IndexedDB, review with qwen3:8b, write PITFALLs/DECISIONs to claude-mem, and synthesize recurring patterns into skill files.

**Architecture:** Claude-in-Chrome JS extracts raw sessions → K2 Python script reviews chunks with local Ollama → CC writes observations to claude-mem → Haiku synthesizes skill files for patterns seen 3+ sessions.

**Tech Stack:** Claude-in-Chrome MCP (JS injection), K2 Ollama qwen3:8b (localhost:11434), claude-mem MCP, Anthropic Haiku API, Python 3.x.

**Budget:** $10 approved. Expected spend: <$0.10.

---

## Task 1: Discover IndexedDB Schema

**Goal:** Map the actual database/store names in Claude desktop before writing extraction code.

**Files:**
- No files created yet — this is discovery only.

**Step 1: Open Claude desktop tab in Chrome**

Use Claude-in-Chrome to list all open tabs, identify the Claude desktop app tab.

**Step 2: Run schema discovery JS**

```javascript
const dbs = await indexedDB.databases();
return JSON.stringify(dbs, null, 2);
```

Expected: List of DB names like `["claude-desktop", ...]`

**Step 3: For each DB, list object stores**

```javascript
const req = indexedDB.open('DBNAME');
req.onsuccess = (e) => {
  const db = e.target.result;
  return Array.from(db.objectStoreNames);
};
```

**Step 4: Sample one record to see schema**

```javascript
const tx = db.transaction('conversations', 'readonly');
const store = tx.objectStore('conversations');
const cursor = await new Promise(resolve => {
  store.openCursor().onsuccess = e => resolve(e.target.result);
});
return JSON.stringify(cursor?.value, null, 2).slice(0, 3000);
```

**Step 5: Document findings** — note DB name, store name, key field names (id, createdAt, turns, title, etc.)

---

## Task 2: Write IndexedDB Extraction Script

**Goal:** Extract all sessions from IndexedDB and save to `Logs/sessions_raw/`.

**Files:**
- Create: `Scripts/session_extract.js` (JS to run via Claude-in-Chrome)
- Create: `Logs/sessions_raw/.gitkeep`

**Step 1: Create output directory**

```bash
mkdir -p Logs/sessions_raw
```

**Step 2: Write extraction JS based on Task 1 schema findings**

```javascript
// Scripts/session_extract.js
// Run via Claude-in-Chrome javascript_tool against Claude desktop tab
(async () => {
  const DB_NAME = 'REPLACE_WITH_ACTUAL_DB';  // from Task 1
  const STORE   = 'REPLACE_WITH_ACTUAL_STORE';

  const db = await new Promise((res, rej) => {
    const r = indexedDB.open(DB_NAME);
    r.onsuccess = e => res(e.target.result);
    r.onerror   = e => rej(e);
  });

  const all = await new Promise((res) => {
    const tx = db.transaction(STORE, 'readonly');
    const req = tx.objectStore(STORE).getAll();
    req.onsuccess = e => res(e.target.result);
  });

  // Sort newest-first, return structured JSON
  const sessions = all
    .sort((a, b) => new Date(b.createdAt || b.updatedAt || 0) - new Date(a.createdAt || a.updatedAt || 0))
    .map(s => ({
      id:       s.id || s.uuid,
      date:     s.createdAt || s.updatedAt,
      title:    s.title || s.name || '(untitled)',
      turns:    (s.turns || s.messages || []).map(t => ({
        role: t.role || t.sender,
        text: (t.text || t.content || '').slice(0, 6000)  // cap per turn
      }))
    }))
    .filter(s => s.turns.length > 0);

  return JSON.stringify({ count: sessions.length, sessions }, null, 2);
})();
```

**Step 3: Run the JS via Claude-in-Chrome against Claude desktop tab**

Expected: JSON with `count: N` where N is 108+.

**Step 4: Save output**

Write each session to `Logs/sessions_raw/YYYY-MM-DD-NNN.json` (split by date from session.date field).

**Step 5: Commit**

```bash
git add Scripts/session_extract.js Logs/sessions_raw/.gitkeep
git commit -m "feat: session ingestion pipeline — extraction script"
```

---

## Task 3: Write K2 Review Script

**Goal:** Python script that reads sessions_raw, chunks turns into 20-turn windows, calls qwen3:8b, outputs structured events.

**Files:**
- Create: `Scripts/session_review.py`

**Step 1: Write the script**

```python
#!/usr/bin/env python3
"""
session_review.py — Phase 2 of session ingestion pipeline.
Reads sessions_raw/*.json, reviews with local Ollama qwen3:8b,
writes structured events to sessions_reviewed/*.json.
Run on K2 (localhost:11434) or P1 (localhost:11434).
"""
import json, os, glob, pathlib, urllib.request, urllib.error

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

Return ONLY valid JSON array. Example:
[{{"type":"PITFALL","title":"hub-bridge sync misses lib/ files","body":"..."}}]
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
        return f"[]  # error: {e}"


def chunk_turns(turns):
    """Split turns list into overlapping CHUNK_SIZE windows."""
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
    for chunk in chunk_turns(turns):
        prompt   = REVIEW_PROMPT.format(turns=format_turns(chunk))
        raw      = call_ollama(prompt)
        # Parse JSON — handle markdown code fences
        raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        try:
            chunk_events = json.loads(raw)
            if isinstance(chunk_events, list):
                events.extend(chunk_events)
        except Exception:
            pass  # skip malformed chunks
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

        with open(path) as f:
            data = json.load(f)

        # data may be a list of sessions or a single session
        sessions = data if isinstance(data, list) else [data]
        all_events = []
        for s in sessions:
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
        print(f"OK {path.name} → {len(all_events)} events")


if __name__ == "__main__":
    main()
```

**Step 2: Create output directory**

```bash
mkdir -p Logs/sessions_reviewed
```

**Step 3: Test with one session file**

```bash
OLLAMA_URL=http://localhost:11434 python3 Scripts/session_review.py
```

Expected: `OK YYYY-MM-DD-001.json → N events`

**Step 4: Verify output**

```bash
cat Logs/sessions_reviewed/YYYY-MM-DD-001.json | python3 -m json.tool | head -50
```

Expected: Valid JSON with `event_count` > 0 and typed events.

**Step 5: Commit**

```bash
git add Scripts/session_review.py Logs/sessions_reviewed/.gitkeep
git commit -m "feat: session ingestion pipeline — K2 review script"
```

---

## Task 4: CC Writes Observations to claude-mem

**Goal:** Read all reviewed event files, deduplicate, write to claude-mem via MCP.

**Files:**
- Create: `Scripts/session_obs_writer.py` (generates the observation text; CC calls the MCP tool)

**Note:** claude-mem MCP (`save_observation`) is only available in Claude Code context, not from standalone Python. This task runs WITH CC as the executor — CC reads the script output and makes the MCP calls.

**Step 1: Write dedup-aware observation collector**

```python
#!/usr/bin/env python3
"""
session_obs_writer.py — Phase 3 prep.
Reads sessions_reviewed/*.json, outputs observations to write.
CC reads this output and calls claude-mem MCP save_observation for each.
"""
import json, pathlib, sys

REVIEWED_DIR = pathlib.Path("Logs/sessions_reviewed")
MAX_EMIT     = int(sys.argv[1]) if len(sys.argv) > 1 else 30  # cap per run

all_events = []
for path in sorted(REVIEWED_DIR.glob("*.json")):
    data = json.load(open(path))
    for e in data.get("events", []):
        e["_source_file"] = path.name
        all_events.append(e)

# Sort: PITFALLs first (highest value), then DECISIONs
priority = {"PITFALL": 0, "DECISION": 1, "PROOF": 2, "DIRECTION": 3}
all_events.sort(key=lambda e: priority.get(e.get("type", ""), 9))

print(f"Total events: {len(all_events)}, emitting top {MAX_EMIT}")
print("---")
for e in all_events[:MAX_EMIT]:
    print(json.dumps({
        "type":    e.get("type"),
        "title":   f"[{e['type']}] {e['title']}",
        "text":    f"{e['body']}\n\nSession: {e.get('session_date','')} — {e.get('session_title','')}",
        "project": "Karma_SADE"
    }, indent=2))
    print("---")
```

**Step 2: Run the collector**

```bash
python3 Scripts/session_obs_writer.py 20
```

**Step 3: CC processes output — for each emitted observation:**

1. Search claude-mem for near-duplicate:
   ```
   mcp__plugin_claude-mem_mcp-search__search(title_keywords, project="Karma_SADE", limit=5)
   ```
2. If no match with similarity > 0.8: call save_observation
3. If duplicate found: skip and log

**Step 4: Verify writes**

```
mcp__plugin_claude-mem_mcp-search__search("PITFALL session ingestion", project="Karma_SADE", limit=10)
```

Expected: New observations appear with today's date.

**Step 5: Commit**

```bash
git add Scripts/session_obs_writer.py
git commit -m "feat: session ingestion pipeline — observation writer"
```

---

## Task 5: Haiku Skill Synthesis

**Goal:** Group events by topic, call Haiku for any pattern appearing 3+ sessions, write `.claude/skills/` files.

**Files:**
- Create: `Scripts/session_skill_synth.py`

**Step 1: Write the skill synthesizer**

```python
#!/usr/bin/env python3
"""
session_skill_synth.py — Phase 4.
Groups reviewed events by topic cluster, calls Haiku for patterns
seen 3+ sessions, outputs skill file content to stdout.
Requires ANTHROPIC_API_KEY env var.
"""
import json, pathlib, os, collections, urllib.request

REVIEWED_DIR    = pathlib.Path("Logs/sessions_reviewed")
SKILLS_DIR      = pathlib.Path(".claude/skills")
MIN_SESSION_HIT = 3
ANTHROPIC_KEY   = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL           = "claude-haiku-4-5-20251001"

SYNTH_PROMPT = """Given these {n} confirmed observations about '{topic}' across {sessions} sessions, write a Claude Code skill file.

Format:
---
name: {slug}
description: <one-line — when Claude should use this skill>
type: feedback
---

## Rule
<the pattern as a single, concrete rule>

**Why:** <root cause from the evidence>
**How to apply:** <exact trigger conditions>

## Evidence
<bullet list of session evidence, one per session>

Observations:
{observations}

Return only the skill file content, no preamble."""


def group_by_topic(events):
    """Naive keyword grouping — good enough for clustering pitfalls."""
    groups = collections.defaultdict(list)
    for e in events:
        title = e.get("title", "").lower()
        # Extract topic keyword (first meaningful noun phrase)
        words = [w for w in title.split() if len(w) > 4 and w not in
                 {"using", "after", "before", "during", "found", "fixed", "added"}]
        topic = words[0] if words else "misc"
        groups[topic].append(e)
    return groups


def call_haiku(prompt):
    payload = json.dumps({
        "model": MODEL, "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["content"][0]["text"]


def main():
    if not ANTHROPIC_KEY:
        print("ERROR: ANTHROPIC_API_KEY not set"); return

    all_events = []
    for path in sorted(REVIEWED_DIR.glob("*.json")):
        data = json.load(open(path))
        for e in data.get("events", []):
            if e.get("type") in ("PITFALL", "DECISION"):
                e["_source"] = path.stem
                all_events.append(e)

    groups = group_by_topic(all_events)
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    for topic, events in sorted(groups.items(), key=lambda x: -len(x[1])):
        sessions = len(set(e["_source"] for e in events))
        if sessions < MIN_SESSION_HIT:
            continue

        slug     = topic.replace(" ", "-").lower()
        out_path = SKILLS_DIR / f"karma-pitfall-{slug}.md"
        if out_path.exists():
            print(f"SKIP {slug} (skill already exists)")
            continue

        obs_text = "\n\n".join(
            f"- [{e['_source']}] {e['title']}: {e['body']}" for e in events[:10]
        )
        prompt = SYNTH_PROMPT.format(
            n=len(events), topic=topic, sessions=sessions,
            slug=slug, observations=obs_text
        )
        print(f"Synthesizing '{topic}' ({sessions} sessions, {len(events)} events)...")
        skill_content = call_haiku(prompt)
        out_path.write_text(skill_content)
        print(f"  → {out_path}")


if __name__ == "__main__":
    main()
```

**Step 2: Dry-run (see what would be synthesized)**

```bash
python3 Scripts/session_skill_synth.py 2>&1 | grep "Synthesizing\|SKIP"
```

Expected: List of topics with session counts.

**Step 3: Run full synthesis**

```bash
ANTHROPIC_API_KEY=$(grep ANTHROPIC_API_KEY /etc/karma-regent.env | cut -d= -f2-) \
  python3 Scripts/session_skill_synth.py
```

Expected: New `.claude/skills/karma-pitfall-*.md` files created.

**Step 4: Verify skill files**

```bash
ls .claude/skills/karma-pitfall-*.md
cat .claude/skills/karma-pitfall-$(ls .claude/skills/karma-pitfall-*.md | head -1 | xargs basename)
```

Expected: Valid frontmatter + Rule + Why + How to apply + Evidence sections.

**Step 5: Commit all**

```bash
git add Scripts/session_skill_synth.py .claude/skills/karma-pitfall-*.md Logs/
git commit -m "feat: session ingestion pipeline — Haiku skill synthesis + generated skills"
```

---

## Task 6: Deploy Review Script to K2 + Nightly Cron

**Goal:** K2 runs Phase 2 nightly on new sessions; CC picks up reviewed events at next session start.

**Files:**
- Modify: K2 crontab (via SSH relay)

**Step 1: Copy review script to K2**

```bash
ssh vault-neo "scp -P 2223 -o StrictHostKeyChecking=no /path/to/session_review.py karma@localhost:/mnt/c/dev/Karma/k2/scripts/"
```

**Step 2: Test script on K2**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'cd /mnt/c/dev/Karma && python3 k2/scripts/session_review.py'"
```

**Step 3: Add nightly cron (K2)**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'crontab -l > /tmp/ct.txt && echo \"0 3 * * * cd /mnt/c/dev/Karma && python3 k2/scripts/session_review.py >> k2/cache/session_review.log 2>&1\" >> /tmp/ct.txt && crontab /tmp/ct.txt'"
```

**Step 4: Verify cron added**

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'crontab -l | grep session_review'"
```

Expected: `0 3 * * * ...session_review.py`

**Step 5: Update services.md**

Add entry to `Karma2/map/services.md` K2 Cron Agents table:
```
| session_review.py | Every night 3am | Reviews new sessions with qwen3:8b, writes to sessions_reviewed/ |
```

**Step 6: Commit**

```bash
git add Karma2/map/services.md
git commit -m "feat: session ingestion pipeline — nightly K2 review cron"
```

---

## Execution Order

1. **Task 1** (discovery) — must complete first; determines DB/store names for Task 2
2. **Task 2** (extraction) — depends on Task 1 schema
3. **Task 3** (review script) — can write in parallel with Task 2; needs Task 2 output to test
4. **Task 4** (claude-mem writes) — depends on Task 3 output
5. **Task 5** (Haiku synthesis) — depends on Task 3 output; can run in parallel with Task 4
6. **Task 6** (K2 cron) — depends on Task 3 working correctly

## Acceptance Criteria

- [ ] 108+ sessions extracted from IndexedDB
- [ ] All sessions reviewed by qwen3:8b (events in sessions_reviewed/)
- [ ] 50+ new observations written to claude-mem (after dedup)
- [ ] 10+ skill files generated in `.claude/skills/karma-pitfall-*.md`
- [ ] K2 nightly cron running session_review.py at 3am
- [ ] Total Haiku API spend < $1 of $10 budget
