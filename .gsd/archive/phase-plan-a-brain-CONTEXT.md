# Phase: Plan-A Brain — Feed the Brain
**Created:** 2026-03-23 (Session 133)
**Prerequisite:** None. This is the first active task.
**Gate:** A-GATE in PLAN-A-brain.md

---

## What We're Doing

Closing the amnesia gap. 145 CC session .jsonl files in `~/.claude/projects/C--Users-raest-Documents-Karma-SADE/` have never been indexed into claude-mem. Every session starts near-zero because Julian's full development arc is unsearchable. We're fixing that.

Three sub-tasks:
- **A1**: One-time backfill — ingest all 145 session files into claude-mem
- **A2**: Auto-indexer — file watcher so future sessions are auto-indexed (forward loop)
- **A3**: Resurrect fix — replace PowerShell brief intermediary with direct K2 MCP reads

---

## Key Constraints

- claude-mem is at localhost:37778 on P1 — accessible via `mcp__plugin_claude-mem_mcp-search__` MCP tools directly from this session. No SSH needed for the ingestion itself.
- Session files are `.jsonl` format — each line is a JSON event (tool_use, tool_result, assistant, user messages)
- Watermark file: `.harvest_watermark_jsonl.json` (separate from existing `.harvest_watermark.json` which tracks .md files)
- Extract bar: same as /harvest — only DECISION/PROOF/PITFALL/DIRECTION/INSIGHT events worth saving. Not every line.
- A2 auto-indexer: PowerShell FileSystemWatcher or Python watchdog. Register as Windows Scheduled Task `KarmaSessionIndexer`.
- A3 resurrect fix: The 3 MCP reads replace Step 1b PowerShell script call. K2 MCP tools: `mcp__k2__file_read` for spine + checkpoint.

---

## What We're NOT Doing

- Not extracting every line of every .jsonl (only meaningful events)
- Not rebuilding the whole resurrect skill from scratch (just fix Step 1b)
- Not touching cc_server_p1.py (that's Plan-B)
- Not exposing claude-mem to vault-neo (that's Plan-C C1)

---

## Success Criteria (A-GATE)

- [ ] `claude-mem search "Julian"` returns results from session history
- [ ] `claude-mem search "cc_server_p1"` returns the zombie bug diagnosis
- [ ] New session auto-appears in claude-mem within 60s of completion
- [ ] `/resurrect` reads from K2 MCP directly (no PowerShell brief)
- [ ] Cold start < 2 minutes

