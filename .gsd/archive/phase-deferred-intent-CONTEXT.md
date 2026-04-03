# Deferred Intent Engine — Design Context

**Phase:** Milestone 8, Phase 4
**Date:** 2026-03-10
**Status:** APPROVED — spec locked, ready to implement

---

## What We're Building

A behavioral intent scheduling system for Karma. Karma (or Colby) creates intents — named behavioral rules with triggers and fire modes — that persist in the vault ledger and surface at request time. The system closes the feedback loop between conversations: Karma can now "remember to check X next time Y is mentioned" and have that intent reliably surface.

---

## Design Decisions (LOCKED)

### Intent Schema
```json
{
  "intent": "verify redis-py function signatures before asserting",
  "trigger": {"type": "topic", "value": "redis-py"},
  "action": "surface_before_responding",
  "fire_mode": "once",
  "created_by": "karma",
  "status": "active"
}
```

### Fire Modes
- `once` — surface once, auto-complete after first surfacing
- `once_per_conversation` — surface once per session (hub-bridge tracks which have fired this session)
- `recurring` — stay active until Colby explicitly closes via /v1/feedback

### Trigger Types (Phase 1 — keyword only, no semantic search)
- `topic` — keyword check: does `trigger.value` appear in user message (case-insensitive)?
- `phase` — session phase: `start` or `end`
- `always` — surface every request regardless of query

### Creation Paths
- **Karma-created (deep mode):** `defer_intent` tool → `pending_intents` Map (same TTL as pending_writes) → Colby 👍 at /v1/feedback → vault ledger (approved:true, status:active)
- **Colby-created (conversational):** hub-bridge detects natural language pattern → writes directly to vault ledger (no gate)

### Approval Gate
- Same `/v1/feedback` endpoint, adds `intent_id` field alongside `write_id`
- 👍 → write to vault ledger as `type:"log", tags:["deferred-intent"]`, approved:true, status:active
- 👎 → discard from pending_intents Map

### Active Intent Loading
- Hub-bridge queries vault `/v1/memory` for `tags:["deferred-intent"]` at request time
- Cached in-process for 5 minutes (mirrors `_memoryMdCache` pattern)
- Cache invalidated on new intent approval (immediate refresh)

### Injection Point
- Active matched intents injected into `buildSystemText()` as new 6th param `activeIntentsText`
- Injected AFTER `selfKnowledge` line, BEFORE `base` karmaCtx — Karma sees her intents before reasoning

### once_per_conversation Reset
- Hub-bridge tracks `fired_this_session` Set (in-process, scoped to server lifetime)
- `once_per_conversation` intents added to Set after surfacing; prevented from firing again this session
- Set cleared on server restart (acceptable — sessions are scoped to server lifetime)

---

## What We're NOT Building

- Semantic trigger matching (keyword-only for Phase 4; DSL deferred to Phase 3+)
- Intent type taxonomy (error-prevention vs ritual vs reminder — Phase 3+)
- Cross-session `pending_intents` persistence (TTL Map only; lost on restart)
- Consciousness-loop auto-intent creation (requires Phase 2b pattern detection)
- A `/v1/intents` management endpoint (not needed for MVP; use /v1/feedback for approval)

---

## File Architecture

```
hub-bridge/lib/deferred_intent.js  — NEW: pure logic, no I/O
hub-bridge/app/server.js           — MODIFY: pending_intents Map, tools, buildSystemText, /v1/feedback
hub-bridge/tests/test_deferred_intent.js  — NEW: 8-10 unit tests
Memory/00-karma-system-prompt-live.md     — MODIFY: coaching section for defer_intent
```

---

## Integration Points in server.js

| What | Where | Change |
|------|-------|--------|
| `pending_intents` Map | Line 157 (after `pending_writes`) | New Map + TTL cleanup |
| `fired_this_session` Set | Line 157 area | New Set for once_per_conversation tracking |
| Active intents cache | After env setup (~line 365) | `_activeIntentsCache`, `_activeIntentsCacheTs` |
| `loadActiveIntents()` | After `fetchKarmaContext()` | New async function, queries vault |
| `buildSystemText()` signature | Line 424 | Add 6th param `activeIntentsText = null` |
| Injection in `buildSystemText` | Line 440 area | Inject after selfKnowledge |
| Call site `/v1/chat` | Line 1370 | Compute activeIntentsText before buildSystemText call |
| `defer_intent` tool | TOOL_DEFINITIONS line 801 | New entry |
| `get_active_intents` tool | TOOL_DEFINITIONS line 801 | New entry |
| `executeToolCall` | Line 888 | New handlers for both tools |
| `/v1/feedback` handler | Line 1553 | Add intent_id branch |

---

## Known Constraints

- Vault API accepts types: `["fact","preference","project","artifact","log","contact"]` — use `type:"log"` with `tags:["deferred-intent"]`
- Vault query for active intents: GET with filter params — check exact vault API query format
- `buildVaultRecord()` required for all vault writes
- `vaultPost()` must check status >= 300 and throw

---

*Context authored: 2026-03-10 — Session 78*
