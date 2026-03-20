# Session Ingestion Pipeline — Design Document

**Date:** 2026-03-20
**Status:** Approved — $10 budget, min 30 sessions, all 108+ preferred
**Author:** CC Ascendant

---

## Problem

108+ Claude desktop sessions contain verified PITFALLs, DECISIONs, and recurring mistakes that CC has re-learned in each session from scratch. This causes:
- Regressions CC has fixed 3-5 times in different sessions
- Architectural decisions relitigated repeatedly
- No structured skill files for high-frequency failure patterns
- claude-mem has 8000+ observations but no session-level synthesis

## Goal

Extract every session, review for high-signal events, write them into claude-mem and skill files so the resurrection path permanently eliminates known failure modes.

---

## Architecture

Four phases, run as a pipeline. Phases 1-3 are automated; Phase 4 uses Haiku for synthesis.

```
Claude Desktop IndexedDB
        │
        ▼ (Phase 1 — JS extraction via Claude-in-Chrome)
sessions_raw/YYYY-MM-DD-*.json   (one file per session)
        │
        ▼ (Phase 2 — Local model review via K2 qwen3:8b)
sessions_reviewed/YYYY-MM-DD-*.json  (filtered, structured events)
        │
        ▼ (Phase 3 — claude-mem writes)
claude-mem observations (PITFALL, DECISION, PROOF, DIRECTION)
        │
        ▼ (Phase 4 — Haiku skill synthesis)
.claude/skills/<topic>.md  (generated for any pattern seen 3+ sessions)
```

---

## Phase 1: IndexedDB Extraction

**Tool:** `mcp__Claude_in_Chrome__javascript_tool` executed against Claude desktop app context.

**Why IndexedDB:** Claude desktop stores all conversation history in IndexedDB. No file parsing, no Playwright gymnastics. Direct JS query returns full conversation JSON including turns, timestamps, and project context.

**Extraction script (pseudo):**
```javascript
// Opens Claude desktop app tab, queries IndexedDB
const db = await openDB('claude-desktop-db');
const tx = db.transaction('conversations', 'readonly');
const all = await tx.store.getAll();
// Sort by date descending, return structured JSON
return all.map(c => ({
  id: c.id,
  date: c.createdAt,
  title: c.title,
  turns: c.turns.map(t => ({ role: t.role, text: t.text.slice(0, 8000) }))
}));
```

**Output:** `Logs/sessions_raw/` — one JSON file per session, named `YYYY-MM-DD-NNN.json`.

**Scope:** Last 30 sessions first (validation pass), then all 108+.

---

## Phase 2: Local Model Review (K2 qwen3:8b)

**Why local model:** $0 cost. K2 is always running. Chunked 20-turn windows fit within 8B context.

**Review protocol per session:**
1. Read session JSON
2. Split into 20-turn chunks with 2-turn overlap
3. For each chunk, prompt qwen3:8b:
   ```
   Review this Claude Code session excerpt. Extract only HIGH-SIGNAL events:
   - PITFALL: something broke, root cause confirmed
   - DECISION: architectural or design decision made
   - PROOF: something verified working end-to-end
   - DIRECTION: course change with a clear reason

   Format: one JSON object per event.
   Skip: status updates, progress narration, routine actions.
   ```
4. Aggregate structured events per session
5. Write to `Logs/sessions_reviewed/YYYY-MM-DD-NNN.json`

**Deduplication gate:** Before writing any observation, search claude-mem for near-duplicate (same topic + same file). Skip if similarity > 0.85.

---

## Phase 3: claude-mem Observation Writes

**Tool:** `mcp__plugin_claude-mem_mcp-search__save_observation`

**Per reviewed event:**
- `title`: `[TYPE] <short title>` (e.g., "PITFALL hub-bridge sync stale image")
- `text`: Event body + session date + "Confirmed across N sessions"
- `project`: `Karma_SADE`

**Batch cap:** 20 writes per pipeline run to avoid flooding the index.

**Frequency:** Run pipeline after Phase 2 completes; observations saved incrementally.

---

## Phase 4: Skill File Generation (Haiku)

**Trigger:** Any PITFALL or DECISION pattern appearing in 3+ distinct sessions.

**Why Haiku:** Synthesis across multiple raw observations into a coherent skill file. ~$0.05 per 100 patterns. Well within $10 budget.

**Output location:** `.claude/skills/<topic>.md`

**Format per skill:**
```markdown
---
name: <topic>
description: <one-line — when to use>
type: feedback
---

## Rule
<the pattern, stated as a rule>

**Why:** <root cause from session evidence>
**How to apply:** <concrete trigger conditions>

## Evidence
- Session YYYY-MM-DD: <what happened>
- Session YYYY-MM-DD: <what happened>
```

**Haiku prompt:**
```
Given these N confirmed session observations about [topic], write a skill file that codifies the lesson as an actionable rule. Be concise. Include evidence citations.
```

---

## Data Flow Details

| Stage | Input | Output | Tooling |
|-------|-------|--------|---------|
| Extract | Claude desktop IndexedDB | `Logs/sessions_raw/*.json` | Claude-in-Chrome JS |
| Review | sessions_raw JSON | `Logs/sessions_reviewed/*.json` | K2 qwen3:8b via Ollama |
| Write | sessions_reviewed events | claude-mem observations | claude-mem MCP |
| Synthesize | grouped observations | `.claude/skills/*.md` | Haiku API |

---

## Budget

| Phase | Cost |
|-------|------|
| Phase 1 (extraction) | $0 |
| Phase 2 (qwen3:8b review) | $0 |
| Phase 3 (claude-mem writes) | $0 |
| Phase 4 (Haiku synthesis, est. 100 patterns) | ~$0.05 |
| **Total** | **<$1** |

$10 budget provides ~20x headroom for reruns and edge cases.

---

## Nightly Cron (Post-Pipeline)

After initial backfill, a nightly K2 cron job:
1. Checks for new sessions since last watermark
2. Runs Phase 2-3 on new sessions only
3. Re-evaluates skill generation if pattern count increases

---

## Success Criteria

- All 108+ sessions extracted with no data loss
- claude-mem grows by 50-200 net new observations (after dedup)
- At minimum 10 skill files generated covering highest-frequency patterns
- Resurrect skill loads relevant skill files at session start (via using-superpowers → skill check)
- Session 110+ CC does not repeat a PITFALL documented by this pipeline

---

## What This Is NOT

- Not a replacement for real-time observation writing (which continues during sessions)
- Not a full transcript replay into context
- Not a training data pipeline (no fine-tuning)
- Not dependent on any external service except Haiku for synthesis

---

## Constraints

- Claude-in-Chrome JS must run against the Claude desktop app tab (not a browser tab)
- K2 qwen3:8b times out on 33K+ token prompts — chunking is mandatory
- claude-mem dedup must run before each write — 8000+ observations already in index
- Skills go in `.claude/skills/` only — not in CLAUDE.md (CLAUDE.md is a constitution)
