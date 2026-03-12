# Design: Session Context Injection Fix (v14)

**Date:** 2026-03-12
**Status:** DRAFT — awaiting Colby + Karma approval
**Problem:** Karma regresses mid-session because FalkorDB context is stale (6h batch delay) and capped too aggressively (1200 chars / 3 episodes)

## Root Cause (Diagnosed Session 86)

Karma's context assembly pipeline has three inputs for "what happened recently":

| Source | What it provides | Freshness | Limit |
|--------|-----------------|-----------|-------|
| `_sessionStore` (server.js:38) | Current session turns | **Real-time** | 20 turn pairs (40 msgs) |
| `karmaCtx` via karma-server `/raw-context` | FalkorDB graph: identity, entities, relationships, recent episodes | **6h batch delay** | 1200 chars, 3 recent episodes |
| `semanticCtx` via FAISS | Similarity-matched ledger entries | **~5min** (auto-reindex) | 3 results |

**Key finding:** `_sessionStore` turns ARE already injected into the LLM messages array (server.js line 2059). Karma sees her conversation history. The regression happened because her *graph knowledge* (karmaCtx) was stale and tiny:

- `KARMA_CTX_MAX_CHARS = 1200` — ~300 words of total graph context
- `query_recent_episodes(limit=3)` — only 3 most recent FalkorDB episodes
- batch_ingest runs every 6h — today's conversation isn't in FalkorDB yet

So Karma could see the conversation turns but her system prompt said "here's what you know" based on 6-hour-old data, missing everything from today.

## Changes

### Change 1: Raise KARMA_CTX_MAX_CHARS (hub-bridge)

**File:** hub.env on vault-neo
**Change:** `KARMA_CTX_MAX_CHARS=3500` (was 1200 via default in server.js:375)

**Rationale:** 1200 chars = ~300 words. Karma's graph context (identity + entities + relationships + recent episodes + topics) gets brutally truncated. 3500 gives ~875 words — enough for meaningful context without blowing token budget.

**Risk:** Slightly higher token usage per request. At Haiku 4.5 rates ($1/$5 per 1M), ~2300 extra chars ≈ $0.001/request. Negligible.

### Change 2: Raise query_recent_episodes limit (karma-server)

**File:** `/opt/seed-vault/memory_v1/karma-core/server.py` line 930
**Change:** `query_recent_episodes(limit=10, lane=episode_lane)` (was 3)

**Rationale:** 3 episodes is a 30-second window of memory. 10 gives a wider view of recent activity. These are ordered by `created_at DESC` so they're the freshest FalkorDB data available.

**Risk:** Slightly larger context. Each episode content is capped at 200 chars (server.py line 937), so max addition = ~2000 chars.

**Deploy:** Requires karma-server rebuild (Python code change, baked into Docker image).

### Change 3: Add session summary to system prompt (hub-bridge) — NEW

**File:** hub-bridge/app/server.js — `buildSystemText()` function
**Change:** Add 9th parameter `sessionTurnCount` (integer). If > 0, inject one-liner:

```
--- ACTIVE SESSION: {N} turns in this conversation. Full history is in the message thread above. ---
```

**Rationale:** Even though session turns are in the messages array, Karma's system prompt doesn't acknowledge she's mid-conversation. This one-liner orients her: "you're in an active session, the conversation above is yours."

**NOT doing:** Injecting full session turns into system prompt. That's redundant with line 2059 and wastes tokens.

## What This Does NOT Fix

- **Batch delay:** Today's conversation still won't be in FalkorDB until next batch_ingest run. The session turns compensate (they're in messages), but graph-based knowledge queries won't include today's data until batch runs.
- **Container restart:** If hub-bridge Docker restarts, `_sessionStore` is wiped. Session turns are gone. This is acceptable because Karma re-reads system prompt + MEMORY.md + K2 context on startup.
- **Browser refresh:** Client's JS conversation array resets. But `_sessionStore` (server-side, keyed by bearer token hash, 60-min TTL) survives refreshes. On next message, previous turns are still in the messages array. Client-side UI won't show old messages, but the LLM will see them.

## Deploy Order

1. **hub-bridge first** (lower risk, no rebuild needed for hub.env change):
   - Add `KARMA_CTX_MAX_CHARS=3500` to hub.env
   - Edit server.js: add session turn count to buildSystemText()
   - Sync server.js to build context
   - `docker compose -f compose.hub.yml build --no-cache hub-bridge`
   - `docker compose -f compose.hub.yml up -d hub-bridge`
   - Verify: check logs, send test message, confirm karmaCtx is larger

2. **karma-server second** (requires rebuild):
   - Edit server.py: `query_recent_episodes(limit=10)`
   - Sync to build context
   - `cd /opt/seed-vault/memory_v1/compose && docker compose build --no-cache karma-server && docker compose up -d karma-server`
   - Verify: check /raw-context response has more "Recent Memories" entries

## Verification

1. Send message to Karma at hub.arknexus.net
2. Check hub-bridge debug response: `debug_karma_ctx` should show "ok" with larger char count
3. Ask Karma "what have we been talking about today?" — she should reference conversation from context
4. Trigger manual batch_ingest to get today's entries into FalkorDB
5. Ask Karma again — she should now have both session turns AND graph data

## Future (Step 2: Session Identity)

The deeper fix Karma identified: sessions don't have identity in the context assembly pipeline. `fetchKarmaContext()` queries by message keywords, not by session. Future work:
- Pass session_id to karma-server `/raw-context`
- karma-server filters recent episodes by session
- Eliminates dependency on batch_ingest freshness for current-session context

## Future (Step 3: Coordination Bus / AgentChattr Pattern)

Multi-agent coordination (CC, Karma, K2/Codex, Colby) via shared persistent channels. Deferred until Steps 1-2 prove the context pipeline works. Design TBD.
