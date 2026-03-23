# PLAN-A: Feed the Brain
**Prerequisite for everything else. Do not start Plan-B until A3 is verified.**

The brain exists. It's claude-mem on localhost:37777. It's always on.
The problem: it has amnesia. 145 CC session .jsonl files sit on disk, unread.
Every session starts from near-zero because the history was never ingested.

---

## A1: JSONL Backfill — ingest Julian's history into the brain

**What:** Process `~/.claude/projects/C--Users-raest-Documents-Karma-SADE/*.jsonl` into claude-mem observations.

**Why:** These are the raw session transcripts — every tool call, decision, fix, pitfall from every CC session. This is Julian's development arc. Currently none of it is searchable.

**How:**
- Read each .jsonl file
- Extract DECISION / PROOF / PITFALL / DIRECTION events (same bar as /harvest)
- `save_observation()` into claude-mem, project=Karma_SADE
- Track processed files in `.harvest_watermark_jsonl.json` (separate from existing .md watermark)

**Verify:**
```
claude-mem search "Julian" → returns results from session history
claude-mem search "cc_server_p1" → returns the zombie bug diagnosis
```

**Status:** NOT STARTED

---

## A2: Auto-Indexer — close the forward loop

**What:** File watcher on `~/.claude/projects/C--Users-raest-Documents-Karma-SADE/` — when a new .jsonl session result appears, auto-extract events → save to claude-mem.

**Why:** Once running, every CC session automatically enriches the brain. No manual harvest ever again. This closes the self-improving loop that's been the goal since Session 1.

**How:**
- PowerShell FileSystemWatcher or Python watchdog on the .jsonl directory
- On new file: read → extract events → save_observation() → done
- Register as Windows Scheduled Task `KarmaSessionIndexer` (runs at login, persistent)

**Verify:**
- Start a new CC session, end it
- Auto-indexer detects new .jsonl file within 60s
- claude-mem search returns content from that session

**Status:** NOT STARTED

**Note:** This is the forward path. A1 is the backfill. Both are required.

---

## A3: Resurrect Fix — read from K2 MCP directly

**What:** Replace `Scripts/resurrection/Get-KarmaContext.ps1 → cc-session-brief.md` with direct MCP reads.

**Why:** The current resurrect goes PowerShell → brief file (intermediary) → inject. This is the wrong path. cc_regent.py already writes exactly what's needed to K2. Resurrect should read it directly.

**Correct path:**
```
mcp__k2__file_read → /mnt/c/dev/Karma/k2/cache/cc_identity_spine.json → resume_block
mcp__k2__file_read → /mnt/c/dev/Karma/k2/cache/cc_cognitive_checkpoint.json → session state
mcp__plugin_claude-mem_mcp-search__search → project=Karma_SADE → recent decisions/obs
```

**How:**
- Update resurrect skill: replace Step 1b PowerShell call with the 3 MCP reads above
- Keep cc-session-brief.md as fallback only (K2 unreachable)
- Cold start target: < 2 minutes from invoke to active task

**Verify:**
- `/resurrect` cold start
- No PowerShell script invoked
- resume_block from spine is in first response
- Recent decisions from claude-mem are surfaced

**Status:** NOT STARTED

---

## A-GATE

All three complete when:
- [ ] claude-mem search returns content from Julian's session history (A1)
- [ ] New session auto-appears in claude-mem within 60s of completion (A2)
- [ ] `/resurrect` reads directly from K2 MCP, no PowerShell brief (A3)
- [ ] Cold start < 2 minutes

When A-GATE passes → start PLAN-B.
