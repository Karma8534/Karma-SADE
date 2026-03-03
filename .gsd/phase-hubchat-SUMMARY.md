# SUMMARY: Hub/Chat FalkorDB Ingest — Execution Report

**Phase:** hub-chat (Session 57 — Blocker #2 Resolution)
**Session:** 57
**Status:** ✅ COMPLETE (batch running in background, verification pending)
**Date:** 2026-03-03T20:05:00Z

---

## Problem Solved

1543 /v1/chat entries (all Colby↔Karma conversations) were in the ledger but **never reached FalkorDB**.
Karma had no memory of any conversation she'd had.

Root cause: `batch_ingest.py` checked `content.assistant_message` — hub/chat entries store the response in `content.assistant_text`. Field mismatch meant every conversation was silently skipped.

Secondary: no hub/chat tag detection — entries weren't identified as a distinct provider.

---

## What Was Done

### Discovery
- Verified /v1/chat IS writing to ledger (last entry: 2026-03-03T18:22)
- Read `server.js` — found `debug_ingest: ingestVerdict` only fires on `[ASSIMILATE/DEFER/DISCARD]` signal
- Confirmed 1543 hub/chat entries in ledger, 0 in FalkorDB
- Compared hub/chat entry schema vs standard provider schema — found `assistant_text` vs `assistant_message` discrepancy

### Fix Applied (`karma-core/batch_ingest.py`)
1. `read_conversation_pairs()`: `assistant_text` accepted as fallback
2. `filter_unprocessed()`: hub/chat tag detection (`"hub" in tags and "chat" in tags`) → provider `"hub-chat"`
3. `filter_unprocessed()`: `"Karma hub-chat"` mapped back to `done_counts` (idempotency)
4. `ingest_one()`: hub-chat path uses `source_desc="Karma hub-chat"`, episode format `[karma-chat] User/Karma`
5. `ingest_one()`: `captured_at` falls back to `entry.created_at` (hub/chat uses top-level timestamp)

### Deployment
- docker cp into karma-server container for immediate use
- Committed + pushed to GitHub (`0edb755`)
- Local, GitHub, vault-neo all in sync

### Verification
- Dry-run output: `hub-chat: 1538 total, 0 done, 1538 remaining` ✅
- Full run launched: 1607 total (1538 hub-chat + 69 legacy openai)
- Wave 1/54 confirmed processing

---

## Decisions Made

**Option 1 (batch_ingest extension) chosen over:**
- Option 2 (ASSIMILATE signals in runtime) — earmarked as future quality/curation layer
- Option 3 (server-side auto-ingest on every /v1/chat call) — too much runtime coupling risk

Rationale: retroactive (captures 1538 existing entries), decoupled, deterministic, zero runtime risk.

---

## What's Still Pending

- [ ] Batch run completion (~190min from launch at 20:00 UTC)
- [ ] Node count verification (expected: 1642 → ~2500+)
- [ ] karma-server image rebuild (so cron picks up updated batch_ingest.py)

---

## Key Learnings

1. **Hub/chat schema differs from extension schema** — `assistant_text` not `assistant_message`. Any new ingest work must check both.
2. **batch_ingest is now the canonical ETL path** — all ledger entry types must be handled here. Each new capture source needs a corresponding provider branch.
3. **Option 2 (ASSIMILATE signals) has future value** — Karma could selectively promote high-quality conversations with `[ASSIMILATE: topic]` in her response. Not wired yet.

---

## Tokens & Cost

- Analysis + implementation: ~15K tokens (efficient — no re-reads, parallel ops)
- Batch run cost: OpenAI API (Graphiti calls gpt-4o-mini for entity extraction per episode)

---

**Signed:** Claude Code (Session 57)
**Next:** Verify batch complete → node count → image rebuild
