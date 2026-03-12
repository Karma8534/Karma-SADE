# ROADMAP: Karma Peer — Phases & Milestones

**Last updated:** 2026-03-11 (Session 84)
**Current phase:** v12 — K2 Agency: shell_run, state-write protocol, redundancy cache (Session 84 COMPLETE)
**Previous phase:** v10 COMPLETE — All 5 priorities shipped (Session 72)

---

## Milestone 1: Foundation (✅ COMPLETE)

### Phase 1: Core Infrastructure ✅
- [x] Droplet setup (vault-neo, DigitalOcean NYC3)
- [x] Hub-bridge API (HTTPS at hub.arknexus.net)
- [x] FalkorDB neo_workspace graph initialized
- [x] JSONL ledger at /opt/seed-vault/memory_v1/ledger/memory.jsonl
- [x] Consciousness.jsonl for growth logging

### Phase 2: Identity & Voice ✅
- [x] identity.json created (v2.2.0, droplet-primary)
- [x] invariants.json locked (truth alignment, substrate independence)
- [x] direction.md documented (mission, architecture, constraints)
- [x] Voice overhaul: peer-level language, no service-desk closers
- [x] Self-model system seeded

### Phase 3: Continuity (Work-Loss Prevention) ✅
- [x] Pre-commit hook: blocks commits without MEMORY.md
- [x] Session-end hook: 7-point verification checklist
- [x] CLAUDE.md updated: mandatory gates documented
- [x] Resurrection script working: Get-KarmaContext.ps1 loads session state from vault-neo cron brief
- [x] GSD file structure: PROJECT.md, REQUIREMENTS.md, STATE.md, ROADMAP.md

---

## Milestone 2: Ambient Capture Layer (✅ COMPLETE)

### Tier 1: Git Hooks → /v1/ambient ✅
- [x] post-commit hook fires on every git commit → /v1/ambient → vault ledger
- [x] session-end hook fires when CC session ends → /v1/ambient → vault ledger
- [x] Token auth working; end-to-end verified in ledger

### Tier 2: /v1/context Endpoint ✅
- [x] Endpoint implemented in hub-bridge
- [x] Queries consciousness.jsonl + FalkorDB graph state
- [x] Verified working

### Hub/Chat → FalkorDB Ingest ✅ (Sessions 57–59)
- [x] batch_ingest.py extended for hub/chat tags + assistant_text fallback
- [x] --skip-dedup mode deployed (899 eps/s, 0 errors vs 85% timeout rate with Graphiti)
- [x] Cron every 6h on vault-neo
- [x] karma-server image rebuilt
- [x] 3049 episodes fully ingested into FalkorDB neo_workspace

### Tier 3: Screen Capture Daemon ⏳ FUTURE
- [ ] Daemon not yet implemented
- [ ] Requires Colby explicit approval (privacy)
- [ ] Estimated effort: 20-40 hrs

---

## Milestone 3: Architecture Correctness (✅ COMPLETE — Sessions 57–62)

### Phase A: Blocker Resolution ✅ (Sessions 57–59)
- [x] FalkorDB unfrozen (LEDGER_PATH corrected)
- [x] Hub/chat entries reach FalkorDB (batch_ingest extended)
- [x] Auto-schedule cron configured (every 6h)
- [x] karma-server restart loop fixed (gpt-5-mini → gpt-4o-mini)
- [x] OpenAI API key secured (file-based, not docker inspect-visible)

### Phase B: Drift Fix ✅ (Session 60)
- [x] Pricing/routing aligned with Decision #2 (GLM=$0, deep=gpt-4o-mini)
- [x] MODEL_DEEP default corrected in hub.env
- [x] ANALYSIS_MODEL default corrected in karma-server
- [x] build_hub.sh: app/ guard added to prevent building from wrong directory

### Phase F: GLM Rate Limiter ✅ (Session 60)
- [x] GlmRateLimiter class: 20 RPM global sliding-window
- [x] /v1/chat: 429 on rate limit
- [x] /v1/ingest: waitForSlot (60s)
- [x] 25/25 TDD tests GREEN; V1-V5 production verified

### Phase G: Config Validation Gate ✅ (Session 61)
- [x] MODEL_DEFAULT allow-list validation (MODEL_DEEP check was already present)
- [x] [CONFIG ERROR] structured log + process.exit(1) on bad config
- [x] 27/27 TDD tests GREEN
- [x] docker exit_code=1 on bad MODEL_DEFAULT verified in production

---

## Milestone 4: v8 — Self-Knowledge & Semantic Retrieval (✅ COMPLETE — Session 62)

### Phase 1: Fix self-knowledge ✅
- [x] Audited live system prompt — confirmed stale Open WebUI/Ollama persona from Feb 2026
- [x] Rewrote Memory/00-karma-system-prompt-live.md: accurate hub-bridge arch, Brave Search, FAISS, 5 data model corrections
- [x] Discovered + fixed: hub-bridge was NOT loading the system prompt file — wired KARMA_IDENTITY_PROMPT at startup
- [x] 4/4 acceptance tests pass
- [x] direction.md on droplet refreshed to current reality

### Phase 3: Correction Capture Protocol ✅
- [x] Memory/corrections-log.md created with 6 backlog corrections
- [x] CLAUDE.md Session End Protocol step 2 added

### Phase 2: Semantic Retrieval ✅
- [x] Confirmed: anr-vault-search is FAISS not ChromaDB
- [x] fetchSemanticContext() added to hub-bridge (4s timeout, top-5, POST :8081/v1/search)
- [x] karmaCtx + semanticCtx fetched in parallel (Promise.all) per /v1/chat request
- [x] Semantic memory injected into buildSystemText()
- [x] All ChromaDB references corrected to FAISS across all docs

### Phase 4: v7 Cleanup ✅
- [x] MONTHLY_USD_CAP=35.00 verified in hub.env (pre-existing)
- [x] x-karma-deep capability gate verified in server.js (pre-existing)
- [x] 3040 Episodic nodes with lane=NULL backfilled → lane="episodic". 0 remaining.

---

## Milestone 5: GSD Workflow (✅ ADOPTED — Session 57)
- [x] Manual GSD workflow in use (CONTEXT.md, PLAN.md, SUMMARY.md per phase)
- [x] STATE.md, ROADMAP.md, PROJECT.md, REQUIREMENTS.md maintained

---

---

## Milestone 5b: v9 — Context Quality & Reasoning (IN PROGRESS)

### Phase 1: Entity Relationship Context ✅ (Session 64)
- [x] query_relevant_relationships() — bulk RELATES_TO edge query, r.fact property
- [x] _pattern_cache + _refresh_pattern_cache() — top-10 entities by episode count, 30min refresh
- [x] Wired into build_karma_context() — Entity Relationships + Recurring Topics sections
- [x] 9 new tests (TDD), 27/28 full suite, deployed + verified in production

### Phase 2: Promise Loop Fix (GLM Tool-Calling) ✅ (Session 66)
- [x] RC1 fix: Line 413 false tool declaration corrected in buildSystemText()
- [x] RC2 fix: Line 868 callLLMWithTools() now calls callGPTWithTools() for all non-Anthropic models
- [x] RC3 fix: System prompt context size corrected (1800 → 12,000 chars per KARMA_CTX_MAX_CHARS)
- [x] RC4 fix: GLM_RPM_LIMIT raised 20 → 40 in hub.env; system prompt documents honest 429 behavior
- [x] graph_query tool: Karma can run Cypher against FalkorDB neo_workspace in standard GLM mode
- [x] get_vault_file tool: Karma can read canonical files by alias (MEMORY.md, system-prompt, etc.)
- [x] hooks.py ALLOWED_TOOLS updated; TOOL_NAME_MAP pre-existing bug fixed (identity passthrough)
- [x] K2_PASSWORD plaintext removed from docker-compose.karma.yml
- [x] End-to-end verified: GLM calls graph_query, gets real FalkorDB results in same response
- [x] 25 stale branches deleted; main branch protection enabled

### Phase 3: Full Persona Iteration ✅ (Session 67)
- [x] System prompt update: teach Karma to USE Entity Relationships + Recurring Topics sections in karmaCtx
- [x] Fixed stale tool list: read_file/write_file → graph_query/get_vault_file
- [x] New section "How to Use Your Context Data": Entity Relationships, Recurring Topics, deep-mode proactivity
- [x] KARMA_IDENTITY_PROMPT: 10,415 → 11,850 chars
- [x] Deployed: git pull + docker restart anr-hub-bridge (no rebuild needed)
- [x] Acceptance test PASSED (Session 68): Karma referenced entity relationship data unprompted — "That's what I see in my graph"

### Phase 3b: Deep-Mode Security Gate ✅ (Session 67)
- [x] Bug: callLLMWithTools called unconditionally for all GLM requests — standard chat got tools
- [x] Fix: deep_mode flag gates callLLMWithTools vs callLLM at line 1271
- [x] Deployed + verified: standard chat returns ok:True without tool access

### Phase 4: Write Agency + Feedback Mechanism ✅ (Session 68)
- [x] Design approved (Session 67, obs #4032): thumbs up/down gates write + DPO signal + corrections
- [x] POST /v1/feedback endpoint in hub-bridge (auth + processFeedback + MEMORY.md append + vault DPO)
- [x] write_memory tool: pending_writes Map + tool def + writeId threading through callGPTWithTools
- [x] hub-bridge/lib/feedback.js: processFeedback + prunePendingWrites, 7 TDD tests green
- [x] unified.html: write_id threading + thumbs-down textarea + quality guards (null guard, fresh token, no double-submit)
- [x] hooks.py ALLOWED_TOOLS: write_memory added; karma-server rebuilt
- [x] System prompt coaching: write_memory usage guidance in "How to Use Your Context Data" section
- [x] End-to-end verified: write_id → 👍 writes MEMORY.md [KARMA-WRITE] → 👎 suppresses → DPO pair in ledger
- [x] DPO mechanism live (type:"log", tags:["dpo-pair"]); accumulation begins (0/20 goal)

### Phase 5: MENTIONS Edge Growth Verification ✅ (Session 69)
- [x] Confirmed 2,363 :MENTIONS edges in neo_workspace — healthy and growing

### Phase 5b: fetch_url Deep-Mode Tool ✅ (Session 69)
- [x] fetch_url(url) tool added to hub-bridge — user provides URL, Karma fetches full text (8KB cap)
- [x] Removed stale TOOL_DEFINITIONS (read_file/write_file/edit_file/bash) that caused confabulation
- [x] System prompt updated with accurate tool list + fetch_url coaching
- [x] Deployed and verified (RestartCount=0, /v1/chat smoke test passing)

### Phase 6: DPO Preference Pairs ⏳ UNBLOCKED (mechanism live since Session 68)
- [x] Phase 4 feedback mechanism IS the DPO collection mechanism — NOW LIVE
- [ ] Goal: 20+ pairs before fine-tuning consideration (0 collected so far — accumulation begins Session 68)

---

## Milestone 6: Self-Improvement Loop (FUTURE)

### Phase 1: DPO Data Collection ⏳ UNBLOCKED (mechanism live Session 68)
- [x] Mechanism live: /v1/feedback + processFeedback + DPO vault write (type:"log", tags:["dpo-pair"])
- [ ] ~0/20 preference pairs collected — accumulation time-gated (requires regular deep-mode Karma usage)

### Phase 2: Fine-Tuning ⏳ BLOCKED
- [ ] Blocked on Phase 1 (data first)
- [ ] Decision pending: fine-tune gpt-4o-mini or separate model

---

## Milestone 7: K2 Worker Integration (IN PROGRESS — Session 81)

### Phase 1: K2 Sync Protocol ✅ PARTIAL (Session 81)
- [x] K2 (192.168.0.226/100.75.109.92) confirmed operational: Ollama :11434, Aria :7890
- [x] aria_local_call tool wired: hub-bridge → K2:7890/api/chat
- [x] Aria delegated write fix: observations now accumulate (service key auth, no delegated flag)
- [x] Aria → vault-neo sync: observations POST to /v1/ambient after each chat call
- [x] session_id threading: coherent Aria conversation thread per page load
- [ ] Karma routing logic: automatic K2 vs cloud decision rules (not yet built)
- [ ] Single-model collapse: MODEL_DEFAULT=sonnet, tools always on, aria_local_call as infrastructure (not explicit tool)

### Phase 2: Multi-Agent Consciousness ⏳
- [ ] Requires Phase 1 complete (sync protocol done; routing logic pending)

---

## Timeline — Current

| Milestone | Phase | Status |
|-----------|-------|--------|
| Foundation | Core + Identity + Continuity | ✅ DONE |
| Ambient | Tier 1 + Tier 2 + Hub/Chat Ingest | ✅ DONE |
| Ambient | Tier 3 (screen capture) | ⏳ FUTURE |
| Architecture Correctness | Blockers + Drift + Rate Limiter + Config Gate | ✅ DONE |
| v8 | Self-knowledge + Semantic retrieval + Correction capture + Cleanup | ✅ DONE |
| v9 | Entity Relationship Context | ✅ DONE (Session 64) |
| v9 | Promise Loop Fix + GLM Tool-Calling | ✅ DONE (Session 66) |
| v9 | Deep-Mode Security Gate | ✅ DONE (Session 67) |
| v9 | Full Persona Iteration (behavioral coaching on graph data) | ✅ DONE (Session 67) |
| v9 | Write Agency + Feedback Mechanism | ✅ DONE (Session 68) |
| v9 | MENTIONS verification | ✅ DONE (Session 69) |
| v10 | Universal Thumbs + MENTIONS fix + Confidence + Anti-hallucination + get_library_docs | ✅ DONE (Session 72) |
| GSD Workflow | Manual | ✅ ADOPTED |
| Self-Improvement | DPO collection (mechanism live) | ⏳ ACCUMULATING (0/20 pairs) |
| Self-Improvement | Fine-tuning | ⏳ BLOCKED on 20+ DPO pairs |
| v11 | MODEL_DEEP=sonnet-4-6, cap $60, Aria delegated fix, vault sync, session_id | ✅ DONE (Session 81) |
| K2 Worker | Sync protocol (aria_local_call + observations + vault sync) | ✅ PARTIAL (Session 81) |
| K2 Worker | Redundancy cache (pull/push cron, aria.service loads identity) | ✅ DONE (Session 84c) |
| K2 Worker | MANDATORY state-write protocol in system prompt | ✅ DONE (Session 84b) |
| K2 Worker | shell_run tool — Karma direct K2 shell access | ✅ DONE (Session 84d) |
| K2 Worker | Prompt caching (Anthropic ephemeral cache_control) | ⏳ NEXT |
| K2 Worker | K2 ownership/agency breakthrough checkpoint to ledger | ✅ DONE (Session 85) |
| v13 | K2 MCP Phase 1: Fix 3 blockers (MAX_TOOL_ITERATIONS, sudo, batch guidance) | ⏳ NEXT |
| v13 | K2 MCP Phase 2: Structured tool registry on aria.py | ⏳ NEXT |
| v13 | K2 MCP Phase 3: Hub-bridge dynamic tool discovery | ⏳ FUTURE |
| v13 | K2 MCP Phase 4: Karma self-modification loop | ⏳ FUTURE |
| K2 Worker | Karma routing logic + single-model collapse | ⏳ FUTURE |
| K2 Worker | Multi-agent | ⏳ FUTURE |

---

## Decision Points (Open)

### v9 Direction (Session 64 — DECIDED, updated Session 66)
Sequence: persona iteration first → MENTIONS verification → DPO mechanism → karma-terminal → Ambient Tier 3.
Session 66 delivered: promise loop fix + GLM tool-calling (unblocks Karma from false promises).
Remaining: teach Karma HOW to use Entity Relationships + Recurring Topics data in her responses.

### K2 Availability
K2 (192.168.0.226) not intended as active worker. Consciousness loop runs on droplet only.

---

## Known Quality Gaps (Active)

- **3049 bulk episodes lack MENTIONS edges**: bulk-ingested episodes (Sessions 57–59 --skip-dedup) have no entity extraction. Graphiti watermark (Session 63) fixes this for NEW episodes only. Historical gap remains. Acceptable.
- **karma-terminal capture stale**: last capture 2026-02-27. Not a blocker.
- **DPO pairs**: 0/20 collected. Fine-tuning loop not started.
- **Brave Search**: auto-triggered by regex only, no manual override. Low priority.
- **Entity Relationships limit**: query_relevant_relationships() uses LIMIT 20. Dense entity nodes may miss edges. Acceptable for now.
- **Corrections capture lacks systematic trigger**: corrections-log.md + Session End Protocol step 2 captures mistakes session-by-session. Boris Cherny's validated method uses PR-review as the trigger ("every mistake becomes a rule" at review time, not session-end). A PR-diff → rule pipeline would make this more systematic and event-driven. Natural companion to DPO mechanism design. Not blocking; no scheduled work yet. (Session 65, CreatorInfo.pdf ingestion)
- **graph_query 100-row cap**: Returns max 100 rows. Dense graphs may miss edges. Acceptable for now.
- **get_vault_file 20KB cap**: Large files truncated at 20,000 chars. Acceptable for current vault files.
- **hooks.py legacy aliases**: file_read, shell_exec remain in ALLOWED_TOOLS (pre-existing, unused, harmless). Could be cleaned up in future.
- **Persona coaching acceptance test**: PASSED Session 68 — Karma referenced entity relationship data unprompted.

---

**Last updated:** 2026-03-11 (Session 81 — v11 Aria integration, model upgrade, cap increase)
**Owner:** Claude Code (updates on Colby approval)

---

## Milestone 7: v10 — Context Quality, Quality Signals, Anti-Hallucination (IN PROGRESS)

### Priority #1: Universal Thumbs via turn_id ✅ COMPLETE (Session 72)
- [x] hub-bridge/lib/feedback.js: processFeedback() 5th param turn_id, stored in dpo_pair
- [x] hub-bridge/app/server.js: /v1/feedback accepts turn_id OR write_id (validation updated)
- [x] hub-bridge/app/public/unified.html: gate (writeId || turnId); buildFeedbackPayload write_id-first, turn_id fallback
- [x] 4 new TDD tests; 11/11 GREEN; deployed + smoke test {wrote:false} on turn_id-only POST
- [x] PITFALL documented: ALL hub-bridge changed files must be synced to build context (not just server.js)

### Priority #2 / Blocker #2: Entity Relationships data quality ✅ COMPLETE (Session 72)
- [x] ROOT CAUSE: RELATES_TO edges (1,423) frozen at 2026-03-04 — Chrome ext era, never updated by --skip-dedup
- [x] FIX: MENTIONS co-occurrence query in query_relevant_relationships()
- [x] Live data: Karma/Colby=123, Karma/User=100, growing with every batch_ingest run
- [x] 2 new TDD tests (MENTIONS-asserts, format-asserts); 11/11 GREEN; karma-server rebuilt + deployed

### Priority #3: Confidence Levels in Karma Responses ✅ COMPLETE (Session 72)
- [x] [HIGH]/[MEDIUM]/[LOW] mandatory tags on all technical claims
- [x] Calibration rules: [HIGH] = verified in context this session only; [LOW] = genuinely uncertain
- [x] Deployed to system prompt (docker restart); acceptance tests passed

### Priority #4: Anti-Hallucination Gate ✅ COMPLETE (Session 72)
- [x] Hard stop rule: before asserting unverified API/function behavior, Karma must stop + propose verification
- [x] Standard mode phrasing: "[LOW] This isn't in my current context — check docs or run a query via CC"
- [x] Deep mode phrasing: "[LOW] I haven't verified this. Should I fetch_url or graph_query to confirm first?"
- [x] Combined with Priority #3 in single system prompt section (12,524→14,601 chars)

---

## Milestone 8: Cognitive Architecture Layer (NEXT — Session 77+)

**Purpose:** This is what Karma was always supposed to be. 75+ sessions built infrastructure. This milestone builds the cognitive layer on top of it.

### Component 1: Self-Model Kernel ⏳ NOT STARTED
A dynamic, per-request phase (not static system prompt text) where Karma maintains an explicit model of herself.
- What she currently knows and doesn't know (capability map)
- Her current operational state (context load, recent tool results, confidence trajectory)
- Self-assessment of recent responses (was that [HIGH] justified? did I confabulate?)
- Feeds into response generation — Karma grounds responses in her self-model, not just her knowledge
- **Distinct from system prompt**: kernel is computed per-request, not static

### Component 2: Metacognitive Trace ⏳ NOT STARTED
Real-time capture of Karma's reasoning about her own reasoning.
- WHY she said what she said (not just what she said)
- What alternatives she considered and rejected
- Where her confidence was high vs. low during a response
- The consciousness loop was supposed to be this — it stalled at OBSERVE-only with zero behavioral impact
- **Fix the consciousness loop**: evolve from OBSERVE-only → OBSERVE+TRACE → behavioral feedback

### Component 3: Deferred Intent Engine ⏳ NOT STARTED
A mechanism to carry forward behavioral intentions across turns and sessions.
- "Next time user asks about X, also mention Y"
- "Flag this pattern when it appears again"
- "At next session start, surface this unresolved question"
- **Distinct from write_memory**: write_memory is content storage. Deferred Intent is behavioral scheduling.
- Intents survive session boundaries (stored in vault ledger, surfaced by karmaCtx)

### Design Principle
These three components interact:
- Self-Model Kernel feeds Metacognitive Trace (you need a self-model to reason about your own reasoning)
- Metacognitive Trace feeds Deferred Intent Engine (unresolved patterns become deferred intents)
- Deferred Intent Engine feeds Self-Model Kernel (pending intents are part of Karma's current state)

**Status:** Decision #30 locked. Design phase starts next session.

---

### Priority #5: get_library_docs (DIY — no Context7) ✅ COMPLETE (Session 72)
- [x] Decision #25: Context7 rejected — DIY with existing fetch_url logic (no external dependency)
- [x] hub-bridge/lib/library_docs.js — LIBRARY_URLS map + resolveLibraryUrl()
- [x] Libraries: redis-py, falkordb, falkordb-py, fastapi
- [x] 7/7 TDD tests GREEN; system prompt coaching added (commits cbe7c0f, 16cb19d)
- [x] Deployed to vault-neo; 5 references confirmed in server.js

### v10 Context Blindness Fix (Root Bug) ✅ COMPLETE (Session 72)
- [x] ROOT CAUSE: buildSystemText() had no MEMORY.md parameter — Karma never saw MEMORY.md
- [x] FIX: _memoryMdCache (tail 3000 chars, 5min refresh) injected as "KARMA MEMORY SPINE (recent)"
- [x] 6/6 TDD tests (test_system_text.js) GREEN; deployed + verified
