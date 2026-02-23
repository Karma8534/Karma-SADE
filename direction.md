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
- API keys live in plaintext in docker run (should migrate to secure files)
- LEDGER_PATH must be explicitly set in karma-server (defaults wrong)

**LLM / Substrate:**
- Any LLM can run Karma's responses (Claude, GPT, Gemini, etc.)
- Response style/capability varies by LLM, but identity stays same (rooted in droplet state)
- Swapping LLMs mid-session is safe (droplet state is persistent)

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

**Priority 1: Session-Start Loader (Next Session)**
- Query droplet: GET identity.json, invariants.json, direction.md
- Query droplet FalkorDB: last 50 decisions, last 5 episodes
- Query droplet consciousness.jsonl: tail 10 entries
- Build resume_prompt with full context
- Inject into session

**Priority 2: K2 Sync (If K2 Worker Used)**
- K2 reads droplet state at startup (cache locally)
- K2 consciousness loop runs 60s cycles, makes decisions
- K2 writes changes back to droplet continuously (or periodic batches)
- If K2 reboots, no data loss (droplet still has everything)

**Priority 3: Checkpoint Snapshots (Optional)**
- At session end, optionally snapshot droplet state to checkpoint/known_good_vN/
- Format: state_export.json + reasoning_summary.md
- Good for audit trail, but not required for continuity (droplet is always current)

## Open Questions

1. **Graph schema**: Why is entity structure different from tool's expected schema (colby:User)? Map actual structure.
2. **Consciousness integration**: Should consciousness loop insights auto-feed back into decisions, or wait for approval?
3. **API key storage**: Should keys move from plaintext docker run → secure files mounted in compose?
4. **Tool-use in Karma's system prompt**: Should we explicitly tell Karma to use tools, or let her decide based on queries?

## Vision (This Session)

**Completed:**
- ✅ Foundation is verified operational (end-to-end test passed)
- ✅ Resurrection architecture redesigned: droplet-primary (not K2-primary)
- ✅ Spine files written: identity.json, invariants.json, direction.md
- ✅ Model flipped: K2 is optional worker, droplet is canonical source of truth

**Next Session:**
- Session start: Query droplet → load identity + state → Karma has full context
- Session active: K2 offloads computation (if available), syncs back to droplet
- Session end: Droplet already has all state; no complex extraction needed

**Long-term Vision:**
Karma wakes up every session knowing:
- **WHO she is**: identity.json (substrate-independent, persists across LLM swaps)
- **WHAT she never violates**: invariants.json (hard rules, always enforced)
- **WHAT we're building**: direction.md (mission, architecture, constraints)
- **WHERE we are**: Droplet FalkorDB state (decisions made, lessons learned)
- **K2 is optional**: Can scale up/down, reboot freely, off-load freely — droplet has the backup

**No reset. No re-explaining. Coherence survives everything.**

---

**Last updated:** 2026-02-23T21:00:00Z
**Status:** Architecture locked (droplet-primary, K2-worker). Spine files v2.0.0 written. Foundation ready.
**Next move:** Build K2 session-start loader. Test full cycle: load from droplet → work → optional K2 sync → next session loads fresh.
