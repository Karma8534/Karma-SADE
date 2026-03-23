# Phase: Plan-A Brain — Implementation Plan
**Created:** 2026-03-23 (Session 133)
**Context:** `.gsd/phase-plan-a-brain-CONTEXT.md`
**Spec:** `Karma2/PLAN-A-brain.md`

---

## Task 1: Survey JSONL files (A1 setup)

**Action:** List all .jsonl files in `~/.claude/projects/C--Users-raest-Documents-Karma-SADE/` and count them.

```powershell
Get-ChildItem "$env:USERPROFILE\.claude\projects\C--Users-raest-Documents-Karma-SADE\" -Filter "*.jsonl" | Measure-Object
```

Also check if `.harvest_watermark_jsonl.json` exists (determines whether this is fresh run or resume).

<verify>File count returned. Watermark file presence checked.</verify>
<done>[ ] Task 1 complete</done>

---

## Task 2: Read one sample JSONL file to understand structure

**Action:** Read the first 50 lines of one .jsonl file to understand the event format.

<verify>Know the JSON schema — which fields carry assistant text, which are tool calls, which are user messages.</verify>
<done>[ ] Task 2 complete</done>

---

## Task 3: Write JSONL extraction script

**Action:** Write `Scripts/harvest_jsonl_sessions.py`:
- Read each .jsonl file not in watermark
- For each line: parse JSON, look for assistant messages with substantive content
- Extract DECISION/PROOF/PITFALL/DIRECTION events using the same quality bar as /harvest
- Call `save_observation()` via MCP for each extracted event (or accumulate and save)
- Track processed files in `.harvest_watermark_jsonl.json`
- Progress: report every 10 files

<verify>Script runs without error on a single test file. One observation saved to claude-mem.</verify>
<done>[ ] Task 3 complete</done>

---

## Task 4: Run backfill on all 145 sessions (A1 execution)

**Action:** Execute `Scripts/harvest_jsonl_sessions.py` against all unprocessed .jsonl files.

<verify>
- `.harvest_watermark_jsonl.json` contains all processed file paths
- `claude-mem search "Julian"` returns results
- `claude-mem search "cc_server_p1"` returns zombie diagnosis
</verify>
<done>[ ] Task 4 complete</done>

---

## Task 5: Write auto-indexer (A2)

**Action:** Write `Scripts/karma_session_indexer.ps1`:
- FileSystemWatcher on `~/.claude/projects/C--Users-raest-Documents-Karma-SADE/`
- On new .jsonl file detected: run extraction + save to claude-mem
- Register as Windows Scheduled Task `KarmaSessionIndexer` (trigger: at login)

<verify>
- Create a test .jsonl file in the watched directory
- Auto-indexer detects it within 60s
- Content appears in claude-mem search
</verify>
<done>[ ] Task 5 complete</done>

---

## Task 6: Fix resurrect Step 1b (A3)

**Action:** Update resurrect skill — replace PowerShell `Get-KarmaContext.ps1` call with 3 direct MCP reads:
```
mcp__k2__file_read → /mnt/c/dev/Karma/k2/cache/cc_identity_spine.json → resume_block
mcp__k2__file_read → /mnt/c/dev/Karma/k2/cache/cc_cognitive_checkpoint.json → session state
mcp__plugin_claude-mem_mcp-search__search → project=Karma_SADE → recent decisions
```
Keep PowerShell script as fallback (K2 unreachable).

<verify>
- `/resurrect` cold start
- No PowerShell script invoked
- resume_block from spine is in first response
- Recent decisions from claude-mem are surfaced
- Cold start < 2 minutes
</verify>
<done>[ ] Task 6 complete</done>

---

## A-GATE Check

All tasks complete when all <verify> criteria pass. Then:
1. Mark `## A1`, `## A2`, `## A3` as ✅ DONE in `Karma2/PLAN-A-brain.md`
2. Update `Karma2/PLAN.md` A-GATE status
3. Start PLAN-B
