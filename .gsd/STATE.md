# STATE: Karma Peer — Decisions, Blockers, Progress

**Last updated:** 2026-03-05T14:00:00Z
**Session:** 66 (GLM tool-calling + system prompt honesty + K2_PASSWORD cleanup merged)
**Canonical source:** This file. Read at session start.

---

## Current Status (Verified 2026-03-05)

| Component | Status | Notes |
|-----------|--------|-------|
| **Consciousness Loop** | ✅ WORKING | 60s OBSERVE-only cycles. Zero LLM calls confirmed in source. RestartCount=0. |
| **Hub Bridge API** | ✅ WORKING | /v1/chat, /v1/ambient, /v1/context, /v1/cypher, /v1/ingest operational. |
| **Voice & Persona** | ✅ DEPLOYED | Peer-level voice verified. gpt-4o-mini confirmed (MODEL_DEEP verified 2026-03-04). |
| **FalkorDB Graph** | ✅ FULLY CAUGHT UP | 3621 nodes (3049 Episodic + 571 Entity + 1 Decision). batch_ingest cron every 6h. |
| **Ledger** | ✅ GROWING | 4000+ entries. Git commits + session-end hooks capturing actively. |
| **Work-Loss Prevention** | ✅ GATES LIVE | Pre-commit hook + session-end hook both active and verified. |
| **Ambient Tier 1 Hooks** | ✅ WORKING | Git + session-end captures verified in ledger. |
| **Ambient Tier 2 Endpoint** | ✅ DEPLOYED | /v1/context endpoint working. |
| **GSD File Structure** | ✅ ADOPTED | All .gsd/ files in place and being used. |
| **Chrome Extension** | ❌ SHELVED | Never worked reliably. Legacy data only. |
| **Conversation Capture** | ✅ WORKING | All 3049 hub/chat episodes ingested via --skip-dedup. |
| **batch_ingest Schedule** | ✅ CONFIGURED | Cron every 6h on vault-neo. --skip-dedup mode. |
| **karma-server image** | ✅ REBUILT | Session-66: graph_query handler + hooks.py whitelist fix. |
| **Routing/Pricing (Decision #2)** | ✅ CORRECTED | GLM=$0, tool-use respects deep_mode, MODEL_DEEP default fixed. Session-60. |
| **GLM Rate Limiter** | ✅ LIVE | 40 RPM (raised from 20 in Session 66). /v1/chat=429, /v1/ingest=waitForSlot. V1-V5 verified. |
| **Config Validation Gate** | ✅ LIVE | MODEL_DEFAULT + MODEL_DEEP allow-lists. [CONFIG ERROR] + exit(1) on bad config. 27/27 tests. |
| **OpenAI API key** | ✅ SECURED | File-based read (mounted volume), not env var (docker inspect clean). |
| **PDF Watcher** | ✅ WORKING | Rate-limit backoff + jam notification + time-window scheduling. |
| **System Prompt Accuracy** | ✅ CORRECT | Memory/00-karma-system-prompt-live.md wired via KARMA_IDENTITY_PROMPT. Session-62. Session-66: honesty fixes (tool list, context size, rate-limit behavior). |
| **FAISS Semantic Retrieval** | ✅ LIVE | fetchSemanticContext() in hub-bridge. karmaCtx + semanticCtx via Promise.all. 4073 entries indexed. Session-62. |
| **Correction Capture Protocol** | ✅ LIVE | Memory/corrections-log.md + CC Session End step 2. Session-62. |
| **FalkorDB lane backfill** | ✅ DONE | 3040 Episodic nodes with lane=NULL → lane="episodic". 0 remaining. Session-62. |
| **anr-vault-search** | ✅ FAISS | Custom search_service.py (NOT ChromaDB). FAISS + text-embedding-3-small. Auto-reindex on ledger change. |
| **Entity Relationships** | ✅ LIVE | RELATES_TO edges surfaced in karmaCtx. query_relevant_relationships() per-message. Session-64. |
| **Recurring Topics** | ✅ LIVE | Top-10 entities by episode count. _pattern_cache refreshed every 30min at startup. Session-64. |
| **Graphiti Watermark** | ✅ LIVE | batch_ingest watermark mode (Session 63). New episodes get entity extraction. :MENTIONS edges grow. |
| **batch_ingest cron** | ✅ Graphiti mode | WATERMARK_PATH set. No --skip-dedup. Entity extraction enabled for incremental. |
| **GLM Tool-Calling** | ✅ LIVE | callGPTWithTools() now handles all non-Anthropic models (line 868 fix). Session-66. |
| **graph_query tool** | ✅ LIVE | Karma can run Cypher against FalkorDB neo_workspace in standard GLM mode. End-to-end verified. Session-66. |
| **get_vault_file tool** | ✅ LIVE | Karma can read canonical files by alias (MEMORY.md, system-prompt, etc.). Handled in hub-bridge. Session-66. |
| **hooks.py whitelist** | ✅ UPDATED | graph_query + get_vault_file added to ALLOWED_TOOLS. Session-66. |
| **TOOL_NAME_MAP** | ✅ FIXED | Pre-existing bug: was mapping read_file→file_read (wrong names). Now empty dict = identity passthrough. Session-66. |
| **K2_PASSWORD secret** | ✅ SECURED | Removed plaintext from docker-compose.karma.yml → ${K2_PASSWORD} env var. Value in hub.env. Session-66. |
| **Main branch protection** | ✅ ENABLED | allow_force_pushes=false, allow_deletions=false. Session-66. |

---

## Active Blockers

**None.**

---

## Key Decisions (Locked)

### Decision #1: Droplet Primacy (2026-02-23, LOCKED)
Droplet (vault-neo) is Karma's permanent home. K2 is a worker that syncs back. All state on droplet.

### Decision #2: Dual-Model Routing (2026-02-27, LOCKED)
GLM-4.7-Flash (primary, ~80%) + gpt-4o-mini fallback (~20%). Verified MODEL_DEEP=gpt-4o-mini on 2026-03-04.

### Decision #3: Consciousness Loop OBSERVE-Only (2026-02-28, LOCKED)
K2 consciousness loop does NOT autonomously call LLM. OBSERVE → rule-based DECIDE → LOG only.

### Decision #4: GSD Workflow Adoption (2026-03-03, LOCKED)
GSD file structure adopted: PROJECT.md, REQUIREMENTS.md, STATE.md, ROADMAP.md, phase-CONTEXT/PLAN/SUMMARY per major feature.

### Decision #5: Honesty Contract (2026-03-03, RENEWED)
Brutal honesty always. Evidence before assertions. Never claim done without proof.

### Decision #6: Chrome Extension Shelved (2026-03-03, LOCKED)
Chrome extension never worked reliably. Removed from all documentation.

### Decision #7: PowerShell for Git Ops (2026-03-03, LOCKED)
Git Bash has persistent index.lock issue on Windows. All git operations via PowerShell.

### Decision #8: --skip-dedup is Standard batch_ingest Mode (2026-03-03, LOCKED)
Graphiti dedup queries time out at scale (85% error rate). Direct Cypher write via --skip-dedup: 899 eps/s, 0 errors. Cron uses --skip-dedup by default.

### Decision #9: OpenAI API Key File-Based (2026-03-03, LOCKED)
API key read from mounted volume file, not injected as env var. docker inspect stays clean.

### Decision #10: KARMA_IDENTITY_PROMPT file-loaded at startup (2026-03-04, LOCKED)
Hub-bridge reads Memory/00-karma-system-prompt-live.md via KARMA_SYSTEM_PROMPT_PATH env var at startup.
Injected as identityBlock at top of buildSystemText(). File is volume-mounted read-only.
Future persona changes require only: git pull on vault-neo + docker restart anr-hub-bridge. No rebuild.

### Decision #11: anr-vault-search is FAISS (confirmed 2026-03-04)
anr-vault-search container runs custom search_service.py — FAISS + OpenAI text-embedding-3-small.
NOT ChromaDB. Endpoint: POST localhost:8081/v1/search. All ChromaDB references removed from all docs.

### Decision #12: Semantic context injected in parallel (2026-03-04, LOCKED)
karmaCtx (FalkorDB recency) + semanticCtx (FAISS top-5) fetched via Promise.all before every /v1/chat.
4s timeout on FAISS call — graceful null if service unavailable. No serial dependency.

### Decision #13: callGPTWithTools routes ALL non-Anthropic models (2026-03-05, LOCKED)
Line 868 in server.js changed from `return callLLM()` → `return callGPTWithTools()`. GLM-4.7-Flash
natively supports function calling via Z.ai OpenAI-compatible API. No provider switch needed.

### Decision #14: TOOL_NAME_MAP is identity passthrough (2026-03-05, LOCKED)
Pre-existing bug found: TOOL_NAME_MAP had file_read/file_write/file_edit/shell_exec (wrong names —
karma-server uses read_file/write_file/edit_file/bash). Fixed to empty dict `{}` which falls through to
`|| toolName` in the mapping code. Empty dict = correct. Any non-empty mapping = likely wrong.

### Decision #15: get_vault_file handled in hub-bridge, not karma-server (2026-03-05, LOCKED)
Hub-bridge has /karma/ volume mount access (read-only). karma-server ALLOWED_PATHS doesn't cover /karma/ paths.
graph_query stays proxied to karma-server (needs FalkorDB access). Architecture split by access path.

---

## Session History

### Session 57 Accomplishments
- FalkorDB unfrozen (Blocker #1)
- hub/chat entries now reach FalkorDB (Blocker #2)
- Cron configured every 6h (Blocker #3)
- GSD docs updated

### Session 58 Accomplishments
- OpenAI API key secured (file-based, not env var)
- karma-server restart loop fixed (gpt-5-mini → gpt-4o-mini)
- GLM rate-limit handling redesigned (throttle, never paid fallback)
- karma-server image rebuilt with all fixes
- K2 sync worker deprecated
- 10 stale remote branches deleted
- compose credentials externalized

### Session 59 Accomplishments
- --skip-dedup added to batch_ingest (899 eps/s, 0 errors)
- FalkorDB datetime() fix (ISO strings only, no datetime() function)
- OPENAI_API_KEY env propagation fixed (os.environ.setdefault())
- Full backfill complete: 3049 episodes ingested (was 1749)
- karma-server image rebuilt with all fixes
- Cron updated to --skip-dedup

---

## Known Limitations
- **Chrome extension:** Shelved permanently
- **K2 not online:** Consciousness loop runs on droplet only
- **No fine-tuning yet:** Need 20+ DPO preference pairs (accumulation in progress)
- **Ambient Tier 3:** Screen capture daemon not built
- **Entity graph growth lag:** Graphiti runs every 6h via cron. New episodes take up to 6h before entity nodes appear in FalkorDB.
- **Per-episode Graphiti failures:** Watermark advances past failed episodes — silently lost at high error rates. Acceptable at low error rates.
- **graph_query 100-row cap:** query_relevant_relationships() returns max 100 rows. Dense graphs may miss edges. Acceptable for now.
- **get_vault_file 20KB cap:** Large files truncated at 20,000 chars. Acceptable for current vault files.
- **hooks.py legacy aliases:** file_read, shell_exec still in ALLOWED_TOOLS but unused (pre-existing, harmless).

---

## Next Session Agenda (Session 67)

1. **v9 Phase 2 — Full Persona Iteration**: System prompt still needs deeper update to teach Karma HOW to use Entity Relationships + Recurring Topics data when she sees them in karmaCtx. Session 66 fixed honesty (what she can/can't do). Still pending: what should she say/do when she sees relationship data?
2. **MENTIONS gap assessment** — confirm :MENTIONS edge counts growing since Session 63 watermark.
3. **DPO mechanism design** — only if Colby approves.

---

### Session 60 Accomplishments
- drift-fix Phase complete: pricing, routing, MODEL_DEEP defaults, ANALYSIS_MODEL all corrected
- Stage 3 build_hub.sh: safeguarded build script, app/ guard verified
- Phase F GLM Rate Limiter: GlmRateLimiter class, 25/25 tests GREEN, wired into server.js
- F4 deployed + V1-V5 all verified in production: 429 on burst, deep unaffected, ingest normal, $0 delta
- Two injection attempts caught + flagged (security posture verified)

---

### Session 61 Accomplishments
- Phase G Config Validation Gate: MODEL_DEFAULT allow-list + [CONFIG ERROR] structured log + process.exit(1)
- 27/27 tests GREEN (up from 25/25); two commits RED→GREEN per TDD discipline
- Production verified: docker exit_code=1 on bad MODEL_DEFAULT confirmed
- hub.env inline allowed-value comments added on vault-neo

---

### Session 64 Accomplishments (2026-03-05)
- Entity Relationships: query_relevant_relationships() — bulk RELATES_TO edge query using r.fact
- Recurring Topics: _pattern_cache + _refresh_pattern_cache() — top-10 by episode count, 30min refresh
- Both wired into build_karma_context() + startup loop; 9 new tests, 27/28 suite (1 pre-existing)
- Deployed + verified: 20 edges for Karma query; Karma:357, User:315, Colby:138 in recurring topics
- v9 direction set: persona iteration first (cheap + highest leverage)
- Corrected: Session 63 Graphiti watermark WAS deployed (cc-session-brief only showed top-5 commits)

### Session 63 Accomplishments (2026-03-04)
- Graphiti watermark deployed to vault-neo: entity extraction enabled for new episodes
- batch_ingest.py: watermark logic + Graphiti as default + 200 episode cap
- Cron: --skip-dedup removed, WATERMARK_PATH=/ledger/.batch_watermark set
- corrections-log.md updated

### Session 62 Accomplishments (v8 — 2026-03-04)

**v8 Phase 1: Fix self-knowledge**
- Audited live system prompt — confirmed it was describing Open WebUI/Ollama from Feb 2026, not actual hub-bridge system
- Rewrote Memory/00-karma-system-prompt-live.md: accurate arch, Brave Search, FAISS, 5 data model corrections
- Discovered: hub-bridge was NOT loading the system prompt file — buildSystemText() was fully hardcoded
- Wired KARMA_IDENTITY_PROMPT via fs.readFileSync at startup, injected as identityBlock in buildSystemText()
- Future system prompt updates: git pull + docker restart only (no rebuild needed)
- 4/4 acceptance tests pass: tools list, .verdict.txt location, batch_ingest direction, GLM-4.7-Flash identity

**v8 Phase 3: Correction capture**
- Memory/corrections-log.md created with format template + 6 backlog corrections (all INCORPORATED)
- CLAUDE.md Session End Protocol step 2 added: scan session for Karma errors → corrections-log.md

**v8 Phase 2: Semantic retrieval**
- Discovered: anr-vault-search is NOT ChromaDB — it is custom search_service.py using FAISS + OpenAI text-embedding-3-small
- 4073 entries indexed, auto-reindex on ledger FileSystemWatcher + every 5min periodic
- Added fetchSemanticContext() to hub-bridge (4s timeout, POST localhost:8081/v1/search, top-5)
- karmaCtx + semanticCtx now fetched in parallel via Promise.all before each /v1/chat response
- Tasks 2.2 (new indexer) and 2.4 (cron sync) NOT NEEDED — service already handles these
- All architecture.md, system prompt, MEMORY.md references corrected from ChromaDB → FAISS

**v8 Phase 4: v7 cleanup**
- MONTHLY_USD_CAP=35.00 — already in hub.env (no change needed)
- x-karma-deep capability gate — already in server.js (no change needed)
- lane=NULL backfill: 3040 Episodic nodes set to lane="episodic" via Cypher. 0 remaining.

### Session 66 Accomplishments (2026-03-05)

**Promise Loop Fix — Phases 1 & 2:**
- RC1 fix: Line 413 (buildSystemText) false tool declaration corrected — accurate tool list with deep-mode gate
- RC2 fix: Line 868 `callLLMWithTools()` — changed `callLLM()` → `callGPTWithTools()` for all non-Anthropic models
- RC3 fix: System prompt context size corrected "~1800 chars" → "~12,000 chars (KARMA_CTX_MAX_CHARS)"
- RC4 fix: GLM_RPM_LIMIT raised from 20 → 40 in hub.env; honest 429 behavior documented in system prompt
- graph_query + get_vault_file added to TOOL_DEFINITIONS + TOOL_NAME_MAP + executeToolCall() in server.js
- graph_query handler added to karma-core/server.py execute_tool_action()
- graph_query + get_vault_file added to hooks.py ALLOWED_TOOLS whitelist (pre-existing pitfall: whitelist gates ALL tools)
- TOOL_NAME_MAP pre-existing bug fixed: file_read/file_write/file_edit/shell_exec → empty dict (identity passthrough)
- K2_PASSWORD moved from plaintext in docker-compose.karma.yml → ${K2_PASSWORD} env var + hub.env on vault-neo
- End-to-end verified: hub-bridge logs show callGPTWithTools → finish_reason=tool_calls → execute → finish_reason=stop
- 25 stale remote branches deleted; main branch protection enabled (no force push, no deletion)
- PR #14 squash-merged to main (squash commit: 357bcb9)

### Decision #10: KARMA_IDENTITY_PROMPT file-loaded at startup (2026-03-04, LOCKED)
Hub-bridge reads Memory/00-karma-system-prompt-live.md via KARMA_SYSTEM_PROMPT_PATH env var at startup.
Injected as identityBlock at top of buildSystemText(). File is volume-mounted read-only.
Future persona changes require only: git pull on vault-neo + docker restart anr-hub-bridge. No rebuild.

### Decision #11: anr-vault-search is FAISS (confirmed 2026-03-04)
anr-vault-search container runs custom search_service.py — FAISS + OpenAI text-embedding-3-small.
NOT ChromaDB. Endpoint: POST localhost:8081/v1/search. All ChromaDB references removed from all docs.

### Decision #12: Semantic context injected in parallel (2026-03-04, LOCKED)
karmaCtx (FalkorDB recency) + semanticCtx (FAISS top-5) fetched via Promise.all before every /v1/chat.
4s timeout on FAISS call — graceful null if service unavailable. No serial dependency.

---

**Last updated:** 2026-03-05T14:00:00Z (Session 66 — Promise loop fixed, GLM tool-calling live)
**Owner:** Claude Code (writes on Colby approval)
**Canonical location:** C:\Users\raest\Documents\Karma_SADE\.gsd\STATE.md
