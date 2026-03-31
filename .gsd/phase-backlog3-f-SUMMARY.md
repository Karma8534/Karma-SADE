# Phase Backlog-3-F — TITANS Memory Tiers SUMMARY
**Completed:** 2026-03-26 | **Sessions:** 146 + 147

## What Was Built

Extended karma_regent.py from a flat 200-entry JSONL to a 3-tier memory system:

- **Tier 0 (Working)**: Last 50 entries loaded at startup, last 5 interactions in context — unchanged
- **Tier 1 (LTM)**: Surprise-gated (>=0.5) entries in `regent_memory_ltm.jsonl`. 7-day decay. Trim every 100 appends.
- **Tier 2 (Persistent)**: Sovereign/Colby messages + directive/decision types in `regent_memory_persistent.jsonl`. Never deleted.

## Files Changed

- `/mnt/c/dev/Karma/k2/aria/regent_memory_titans.py` — new file: all helpers (`_surprise_score`, `_ltm_trim`, `append_memory_ltm`, `append_memory_persistent`, `get_memory_context_tiered`)
- `/mnt/c/dev/Karma/k2/aria/karma_regent.py` — `append_memory()` now dual-writes to tiers; `get_memory_context()` delegates to `get_memory_context_tiered(_memory)`

## Verification (Session 147)

- `import karma_regent` passes on K2
- Regent log at startup: `memory loaded: 50 entries`
- Service running TITANS-enabled code (file modified 21:13, service started 21:14)
- `regent_memory_ltm.jsonl` and `regent_memory_persistent.jsonl` will be created on first qualifying message

## Pitfalls

- GSD `<done>` tags were empty at session 147 start — code was fully implemented in 146 but markers not updated (B002 pattern). Verified via direct K2 file read.
- LTM/persistent files don't pre-exist — they're created lazily on first qualifying append. This is correct behavior, not a missing file.

## Next

Backlog-3 P0-G: Wire `callWithK2Fallback` to main chat route (K2_INFERENCE_ENABLED flag in hub.env).
