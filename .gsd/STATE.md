# STATE: Karma Peer — Decisions, Blockers, Progress

**Last updated:** 2026-03-04T23:30:00Z
**Session:** 64 (Entity Relationship Context deployed)
**Canonical source:** This file. Read at session start.

---

## Current Status (Verified 2026-03-04)

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
| **karma-server image** | ✅ REBUILT | Session-60 drift-fix: ANALYSIS_MODEL default corrected. |
| **Routing/Pricing (Decision #2)** | ✅ CORRECTED | GLM=$0, tool-use respects deep_mode, MODEL_DEEP default fixed. Session-60. |
| **GLM Rate Limiter** | ✅ LIVE | 20 RPM global sliding-window. /v1/chat=429, /v1/ingest=waitForSlot. 25/25 tests. V1-V5 verified. |
| **Config Validation Gate** | ✅ LIVE | MODEL_DEFAULT + MODEL_DEEP allow-lists. [CONFIG ERROR] + exit(1) on bad config. 27/27 tests. |
| **OpenAI API key** | ✅ SECURED | File-based read (mounted volume), not env var (docker inspect clean). |
| **PDF Watcher** | ✅ WORKING | Rate-limit backoff + jam notification + time-window scheduling. |
| **System Prompt Accuracy** | ✅ CORRECT | Memory/00-karma-system-prompt-live.md wired via KARMA_IDENTITY_PROMPT. 4/4 acceptance tests pass. Session-62. |
| **FAISS Semantic Retrieval** | ✅ LIVE | fetchSemanticContext() in hub-bridge. karmaCtx + semanticCtx via Promise.all. 4073 entries indexed. Session-62. |
| **Correction Capture Protocol** | ✅ LIVE | Memory/corrections-log.md + CC Session End step 2. Session-62. |
| **FalkorDB lane backfill** | ✅ DONE | 3040 Episodic nodes with lane=NULL → lane="episodic". 0 remaining. Session-62. |
| **anr-vault-search** | ✅ FAISS | Custom search_service.py (NOT ChromaDB). FAISS + text-embedding-3-small. Auto-reindex on ledger change. |
| **Entity Relationships** | ✅ LIVE | RELATES_TO edges surfaced in karmaCtx. query_relevant_relationships() per-message. Session-64. |
| **Recurring Topics** | ✅ LIVE | Top-10 entities by episode count. _pattern_cache refreshed every 30min at startup. Session-64. |

---

## Active Blockers

**None.** All 5 blockers resolved as of sessions 58–59.

### ✅ Blocker #1 — RESOLVED (2026-03-03): FalkorDB Unfrozen
LEDGER_PATH corrected to `/ledger/memory.jsonl`. Graph grew from 1570 → 1642 nodes. Cron configured.

### ✅ Blocker #2 — RESOLVED (2026-03-03): hub/chat entries reach FalkorDB
batch_ingest.py extended for hub/chat tags + assistant_text fallback. 1538 conversations ingested.

### ✅ Blocker #3 — RESOLVED (2026-03-03): Auto-Schedule Configured
Cron: `0 */6 * * *` on vault-neo, `--skip-dedup` mode.

### ✅ Blocker #4 — RESOLVED (2026-03-03, verified 2026-03-04): karma-server Restart Loop
Root cause was gpt-5-mini model reference (bad model name). Fixed in session 58. RestartCount=0 confirmed.

### ✅ Blocker #5 — RESOLVED (verified 2026-03-04): MODEL_DEEP Drift
`grep MODEL_DEEP hub.env` → `gpt-4o-mini`. Matches Decision #2. Not a typo.

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

---

## Next Session Agenda (Session 60)

System is in maintenance/growth mode. No urgent fixes. Possible work:
1. **direction.md refresh** — 9 days stale, doesn't reflect post-session-59 state. Karma reads this.
2. **ChromaDB reindex** — vector search index stale (low priority)
3. **DPO preference pair accumulation** — needs 20+ pairs to start fine-tuning
4. **Ambient Tier 3** — screen capture daemon (not started)

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

---

## Next Session Agenda (v9)

**What v8 unblocked:**
1. **System prompt iteration is now cheap**: git pull + `docker restart anr-hub-bridge` only. No rebuild needed. First meaningful persona iteration cycle can begin.
2. **Semantic memory gives Karma recall**: 4073 entries indexed; Karma can now draw on relevant past episodes in every response. First real continuity-in-conversation mechanism.
3. **Correction capture is operational**: When Karma says something wrong and is corrected, that goes to corrections-log.md → eventually into system prompt. Self-improvement cycle is now closed.
4. **FalkorDB lane consistency**: All 3049 Episodic nodes now have lane="episodic". Graph queries by lane now return correct results.

**Open quality gap (pre-existing, not new):**
- --skip-dedup = no entity extraction for bulk-ingested 3049 episodes. Only Episodic nodes. No cross-session Entity/relationship graph derived from historical episodes. New episodes (post-cron) get Graphiti entity extraction. Gap exists but acceptable.

**v9 candidates (Colby decides):**
1. DPO preference pair accumulation mechanism (0/20, needs Colby decision on how to collect)
2. Ambient Tier 3 screen capture daemon
3. karma-terminal capture refresh (stale 2026-02-27)
4. First persona iteration: test system prompt improvement cycle now that it's cheap

---

### Session 63 Accomplishments (2026-03-04)
- Discovered entity graph frozen since Session 59 (--skip-dedup bypasses Graphiti entirely)
- Implemented watermark-based Graphiti mode for forward-only entity extraction
- Deployed: watermark at line 4075, cron updated (--skip-dedup removed), karma-server rebuilt
- Karma's knowledge graph now grows with every new conversation (6h lag via cron)

---

**Last updated:** 2026-03-04T22:15:00Z (Session 63 — Graphiti watermark deployed)
**Owner:** Claude Code (writes on Colby approval)
**Canonical location:** C:\Users\raest\Documents\Karma_SADE\.gsd\STATE.md
