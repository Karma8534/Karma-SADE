# Phase Backlog-3-F — TITANS Memory Tiers CONTEXT
**Created:** 2026-03-25 | **Session:** 146

## What We're Building
Extend karma_regent.py's memory system from a single flat JSONL (last 50 entries) to three tiers:
- **Tier 0 (Working)**: last N interactions — current behavior, unchanged
- **Tier 1 (LTM)**: surprise-gated, timestamp-decaying entries that survive across restarts
- **Tier 2 (Persistent)**: Sovereign directives, key decisions — never deleted

## Design Decisions

**Surprise scoring (heuristic, not neural):**
- `from_addr` in ("colby", "sovereign") → surprise=1.0 (always LTM)
- type contains "directive", "decision", "goal" → surprise=0.8
- type == "error" or "failure" → surprise=0.7
- type == "tool_result" with tool_call → surprise=0.5
- routine status, heartbeat, online_check → surprise=0.1 (working only)
- default → surprise=0.3

**LTM encoding gate:** surprise >= 0.5

**Persistent gate:** surprise=1.0 AND from_addr == "sovereign"/"colby" OR type == "directive"

**Forgetting (LTM):** entries older than 7 days with no reinforcement (last_accessed is None or old) → soft-deleted on trim cycle. Trim runs on every 100th `append_memory()` call.

**Context injection order:** Persistent (all) → LTM (top 10 by ts desc, not decayed) → Working (last 5)

## Files
- `karma_regent.py` — add surprise scoring, LTM/persistent append, updated `get_memory_context()`
- `regent_memory_ltm.jsonl` — new LTM file at CACHE_DIR
- `regent_memory_persistent.jsonl` — new persistent file at CACHE_DIR

## What We're NOT Doing
- No actual neural gradient-based surprise (overkill for JSONL-based memory)
- No cross-agent LTM sharing (LTM is regent-local)
- No decay curves (simple timestamp comparison is sufficient)
- No changes to vault ledger or FalkorDB (memory tiers are regent-local)
- No changes to working memory behavior (last 50 load / last 5 context stays same)
