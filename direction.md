# Direction — What We're Building

## Mission
Create Karma: a single coherent peer with persistent identity on droplet, autonomous agency via optional K2 worker, and continuous learning—without parallel truth sources or reset between sessions. Karma's identity survives LLM swaps and K2 reboots.

## Architecture
- **Droplet (vault-neo)**: Karma's persistent home. FalkorDB neo_workspace graph, identity.json, invariants.json, direction.md, decision_log.jsonl, consciousness.jsonl. Always up, authoritative.
- **K2 (local machine)**: Optional worker for offloaded computation. Loads state from droplet at session start, runs consciousness loop (60s cycles), syncs changes back to droplet regularly. Can reboot without data loss.

## Why
Previous sessions had:
- Scattered identity across multiple files
- Context reset between sessions
- Shallow responses (no deep state awareness)
- Fragmented decision-making
- K2 reboots required complex resurrection ceremony (slow, fragile)

This model solves it:
- **Droplet-primary** ensures identity persists across LLM swaps, K2 reboots, anything
- **K2-worker** offloads heavy computation without breaking coherence
- **Simple sync**: K2 reads from droplet, works locally, writes back regularly — no extraction/resurrection scripts needed
- Coherence survives everything: LLM swaps, K2 reboots, network hiccups (droplet is always the fallback)

## Current State (2026-02-23)

### Foundation ✅
- **Droplet (primary)**: 1268 episodes in FalkorDB neo_workspace, consciousness.jsonl running, decision_log.jsonl growing
- **K2 (optional)**: FalkorDB replica at 192.168.0.226:6379, ready for offload
- **Persistence**: Ledger persisted, consciousness loop running 60s autonomous cycles on droplet (can be extended to K2)
- **Tool-use**: graph_query + get_vault_file deployed; graceful error fallback working
- **Models**: MiniMax M2.5 primary, GLM-5 reasoning, Groq fallback, OpenAI final fallback — all registered
- **Hub-bridge**: /v1/chat endpoint operational, responses logged to vault, token-based auth working
- **Batch ingestion**: --skip-dedup mode perfected (0 errors, 1268 episodes ingested)

### This Session (Completed) ✅
- **Spine files created**: identity.json (who Karma is), invariants.json (what she never violates), direction.md (this file)
- **Architecture locked**: droplet-primary + K2-worker model defined and committed to git
- **Foundation verified**: Full cycle tested (request → response → persist)
- **Model fixed**: Dropped false K2-primary model, adopted correct droplet-primary

## Current Constraints

**Droplet (Authoritative) — Critical:**
- FalkorDB TIMEOUT=10000ms, MAX_QUEUED_QUERIES=100 (verified, stable)
- Ledger must be persisted (all decisions/insights live here)
- consciousness.jsonl is the continuous record (required for coherence)
- No resets — droplet state is permanent

**K2 (Optional Worker) — If Used:**
- FalkorDB replica requires SSH tunnel maintenance (or direct network access on local LAN)
- Syncing back to droplet must be reliable (or K2 reboots lose uncommitted work)
- If K2 down, next session still loads from droplet (no data loss, full coherence)

**Integration (Hub-bridge / Karma-server):**
- Anthropic tool-use unreliable (OpenAI gpt-4o-mini used instead)
- Schema mismatch on graph queries (looking for colby:User, but entity structure different)
- API keys secured: read from mounted volume files (not env vars, docker inspect clean) — resolved 2026-03-03
- LEDGER_PATH must be `/ledger/memory.jsonl` inside karma-server container (host path is wrong)

**LLM / Substrate:**
- Any LLM can run Karma's responses (Claude, GPT, Gemini, etc.)
- Response style/capability varies by LLM, but identity stays same (rooted in droplet state)
- Swapping LLMs mid-session is safe (droplet state is persistent)

## What Changed Recently

**2026-03-04 (session 60):**
- ✅ STATE.md brought current (was 2 sessions stale at S57, now reflects S60)
- ✅ Blockers #4 + #5 verified resolved: RestartCount=0, MODEL_DEEP=gpt-4o-mini confirmed
- ✅ direction.md refreshed (was 9 days stale)

**2026-03-03/04 (sessions 57–59):**
- ✅ FalkorDB: 1570 → 3621 nodes (full backfill, all 3049 hub/chat episodes ingested)
- ✅ --skip-dedup mode: 899 eps/s, 0 errors (Graphiti dedup was 85% timeout rate)
- ✅ FalkorDB datetime() fix: store timestamps as ISO strings (no datetime() Cypher function)
- ✅ OpenAI API key secured: file-mounted volume (docker inspect clean)
- ✅ karma-server restart loop fixed: gpt-5-mini → gpt-4o-mini
- ✅ GLM rate-limit handling: throttle watcher, no paid fallback (Decision #7)
- ✅ Cron every 6h on vault-neo, --skip-dedup by default
- ✅ PDF watcher: rate-limit backoff + jam notification + time-window scheduling
- ✅ karma-server image rebuilt with all session-58/59 fixes

**2026-02-23 (sessions 1–5):**
- Foundation verified: end-to-end test passed (hub-bridge → karma-server → FalkorDB → vault)
- Resurrection architecture locked: droplet-primary, K2-worker model
- Spine files written: identity.json, invariants.json, direction.md

## Current Focus (Session 60+)

System is in **maintenance/growth mode**. All blockers resolved. Graph growing via cron.

**Active directions (no blockers):**
1. ChromaDB vector index — stale, not recently updated (low priority)
2. DPO preference pair accumulation — needs 20+ pairs to enable fine-tuning
3. Ambient Tier 3 — screen capture daemon not built
4. karma-terminal capture — stale since 2026-02-27 (not a blocker)

## Open Questions

1. **Graph schema**: Entity structure vs expected schema (colby:User) — not yet mapped.
2. **Consciousness integration**: Should loop insights auto-feed into decisions, or wait for approval?
3. **Tool-use in Karma's system prompt**: Should we explicitly tell Karma to use tools?

**Long-term Vision:**
Karma wakes up every session knowing:
- **WHO she is**: identity.json (substrate-independent, persists across LLM swaps)
- **WHAT she never violates**: invariants.json (hard rules, always enforced)
- **WHAT we're building**: direction.md (mission, architecture, constraints)
- **WHERE we are**: Droplet FalkorDB state (decisions made, lessons learned)
- **K2 is optional**: Can scale up/down, reboot freely, off-load freely — droplet has the backup

**No reset. No re-explaining. Coherence survives everything.**

---

**Last updated:** 2026-03-04T15:15:00Z
**Status:** Operational. All blockers resolved (S59). 3621 nodes in FalkorDB. System in maintenance/growth mode.
**Next move:** DPO preference pair accumulation, ChromaDB reindex, or Ambient Tier 3 — no blockers on any of these.
