# A1: JSONL Backfill — Plan
**Created:** 2026-03-23 (Session 134)

Execute one task at a time. Mark `<done>` only after `<verify>` passes.

---

## Task 1: Write JSONL event extractor script
<verify>Script `Scripts/jsonl_backfill.py` runs without error on a single test file. Prints count of events found.</verify>
<done>true — 2026-03-23 Session 134</done>

**PROOF:** Dry-run on session 09af07c2 found 17+ events (PROOF, DECISION, DIRECTION, INSIGHT types). Unicode print fix applied (P040 — PYTHONUTF8 not set, use ASCII in prints).

Script logic:
- Input: path to JSONL file
- Parse each line as JSON
- For `type:"assistant"` entries: extract `message.content[].text` (type="text" blocks)
- Check text for keywords: DECISION, PROOF, PITFALL, DIRECTION, INSIGHT, DIRECTION
- If keyword found: extract surrounding context (±200 chars), save as observation
- Output: list of (title, text) pairs found

---

## Task 2: Run backfill on all top-level session files
<verify>Script processes all UUID.jsonl files (not subagents). Watermark file written. Returns total observations saved count.</verify>
<done>false</done>

- Glob: `~/.claude/projects/C--Users-raest-Documents-Karma-SADE/*.jsonl` (top-level only)
- Skip subagent files (path contains "/subagents/")
- Track processed in `.harvest_watermark_jsonl.json`
- Call `save_observation()` via claude-mem MCP for each event found

---

## Task 3: Verify search returns session content
<verify>`search("Julian")` returns results from session history. `search("cc_server_p1")` returns zombie bug diagnosis. Both must return ≥1 result each.</verify>
<done>false</done>

---

## Summary Gate
A1 COMPLETE when Task 3 verify passes.
Mark A1 ✅ DONE in PLAN.md Done Inventory.
Next: A2 (auto-indexer).
