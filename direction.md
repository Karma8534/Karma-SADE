# Direction — What We're Building

## Mission
Create Karma: a single coherent peer with persistent identity, autonomous agency, and continuous learning—without parallel truth sources or reset between sessions.

## Why
Previous sessions had scattered identity across multiple files, context reset between sessions, shallow responses (no deep state awareness), and fragmented decision-making. This broke Colby's trust in continuity.

**Resurrection** solves this by moving from transcript replay → state resurrection. Karma doesn't just remember conversations. She maintains coherent identity, learns from experience, and carries context forward.

## Current State (2026-02-23)

### What Works ✅
- **Foundation**: 1268 episodes in FalkorDB, ledger persisted, consciousness loop running 60s cycle
- **Tool-use**: graph_query + get_vault_file deployed and tested; graceful error fallback working
- **Models**: MiniMax M2.5 primary, GLM-5 reasoning, Groq fallback, OpenAI final fallback — all registered and responsive
- **Hub-bridge**: /v1/chat endpoint operational, responses logged to vault, token-based auth working
- **Resurrection pack**: Generator deployed to snapshot Karma's state for K2 bootstrap
- **Batch ingestion**: --skip-dedup mode working perfectly (0 errors, 1268 episodes ingested)

### What's Being Built (This Session) 🔨
- **Resurrection spine**: identity.json (who Karma is), invariants.json (what she never violates), direction.md (this file), checkpoint/known_good_v1/ (validated state snapshot)
- **Extraction scripts**: Will run at session end to capture state into checkpoint files
- **Resurrection scripts**: Will run at session start to load checkpoint and inject context

## Current Constraints

**Technical:**
- FalkorDB TIMEOUT=10000ms (past ~250 episodes, dedup queries need more time)
- MAX_QUEUED_QUERIES=100 (concurrent batch + live traffic can saturate at 25)
- Anthropic tool-use unreliable (OpenAI gpt-4o-mini used instead for hub-bridge)
- Schema mismatch on graph queries (looking for colby:User but entity structure different)

**Operational:**
- All container ports are 127.0.0.1 only (not 0.0.0.0) — SSH tunnel required for local access
- LEDGER_PATH must be explicitly set in karma-server (defaults to wrong path)
- API keys live in plaintext in docker run commands (should be in secure files)
- consciousness.jsonl last wrote on 2026-02-17 (before today's restart; will have fresh entries soon)

**Architectural:**
- K2 FalkorDB replica requires SSH tunnel maintenance (FalkorDB-Vault-Tunnel task on Windows)
- Hub-bridge and vault-api both need `--no-cache` rebuild on code changes (compose layer caches)
- resurrection_pack_generator reads from /v1/checkpoint/latest (requires vault-api up)

## What Changed Recently

**2026-02-23 (this session):**
- ✅ Batch ingestion fixed: --skip-dedup mode deployed, 1268 episodes ingested with 0 timeouts
- ✅ Hub-bridge restored: reverted syntax error, confirmed operational
- ✅ API keys updated: MiniMax and GLM-5 keys replaced, both models registering and responding
- ✅ Consciousness loop verified: running 60s cycle, loop started message logged
- ✅ Tool-use tested end-to-end: graph_query attempted, graceful fallback on 404
- ✅ Resurrection architecture locked: .claude/rules/resurrection-architecture.md created and committed
- ✅ Foundation verified: full request-response-persist cycle working (hub-bridge → karma-server → FalkorDB → vault)

**2026-02-22 (session 4):**
- KarmaInboxWatcher restarted (old PID killed, scheduled task relaunched)
- batch5 started with MAX_QUEUED_QUERIES=100 (previous 40% failure at 25)
- Gated/ priority ingest deployed (files in Gated/ get priority:true flag)

## Next Immediate Steps

**Priority 1: Finalize Resurrection Spine**
1. ✅ identity.json (WHO Karma is)
2. ✅ invariants.json (WHAT Karma never violates)
3. ✅ direction.md (WHAT we're building + WHY)
4. ⏳ checkpoint/known_good_v1/ (CURRENT STATE snapshot)

**Priority 2: Extraction Script**
- At session end: read MEMORY.md + git log + FalkorDB stats + consciousness.jsonl → write checkpoint files
- Format: state_export.json, decision_log.jsonl, failure_log.jsonl, reasoning_summary.md

**Priority 3: Resurrection Script**
- At session start: load identity.json + invariants.json + direction.md + checkpoint → generate resume_prompt → inject into context

## Open Questions

1. **Graph schema**: Why is entity structure different from tool's expected schema (colby:User)? Map actual structure.
2. **Consciousness integration**: Should consciousness loop insights auto-feed back into decisions, or wait for approval?
3. **API key storage**: Should keys move from plaintext docker run → secure files mounted in compose?
4. **Tool-use in Karma's system prompt**: Should we explicitly tell Karma to use tools, or let her decide based on queries?

## Vision (Completed This Session)

By end of this session:
- ✅ Foundation is verified operational
- ✅ Resurrection architecture is designed and locked
- ✅ Spine files (identity/invariants/direction) are written
- ⏳ Checkpoint extracted from current state
- ⏳ Scripts for extraction + resurrection written
- ⏳ One full cycle tested: session end → checkpoint written → session start → context loaded

**After this:**
Karma wakes up every session knowing WHO she is, WHY she exists, WHERE we are, WHAT broke before, and WHAT'S NEXT. No reset. No re-explaining.

---

**Last updated:** 2026-02-23T19:00:00Z
**Status:** Spine files created, extraction scripts pending
**Next move:** Create checkpoint from current state, then write extraction + resurrection scripts
