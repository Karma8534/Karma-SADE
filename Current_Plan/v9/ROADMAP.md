# ROADMAP: Karma Peer — Phases & Milestones

**Last updated:** 2026-03-05
**Current phase:** v9 IN PROGRESS — Phase 4 (write agency) next
**Previous phase:** v9 Phase 3 (persona coaching) COMPLETE — Session 67

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
- [ ] Acceptance test PENDING: Ask Karma about a Recurring Topic; verify she references relationship data unprompted

### Phase 3b: Deep-Mode Security Gate ✅ (Session 67)
- [x] Bug: callLLMWithTools called unconditionally for all GLM requests — standard chat got tools
- [x] Fix: deep_mode flag gates callLLMWithTools vs callLLM at line 1271
- [x] Deployed + verified: standard chat returns ok:True without tool access

### Phase 4: Write Agency + Feedback Mechanism ⏳ NEXT
- [ ] Design approved (Session 67, obs #4032): thumbs up/down gates write + DPO signal + corrections
- [ ] POST /v1/feedback {turn_id, rating: +1/-1, note?: string} endpoint
- [ ] New tools: write_memory(content), annotate_entity(name, note), flag_pattern(description)
- [ ] Write routing: 👍 → write Karma's note; 👍 + text → write user's phrasing; 👎 + text → corrections-log.md
- [ ] Web UI: thumbs up/down already present at hub.arknexus.net (text box already opens on click)
- [ ] Safe target: PATCH /v1/vault-file/MEMORY.md (append-only, auditable)
- [ ] DPO pairs: each rated response = preference pair; goal 20+ pairs

### Phase 5: MENTIONS Edge Growth Verification ⏳
- [ ] Confirm :MENTIONS edge counts growing since Session 63 watermark
- [ ] If growing: healthy. If stagnant: investigate watermark mode.

### Phase 6: DPO Preference Pairs (via Phase 4) ⏳ UNBLOCKED by Phase 4
- [ ] Phase 4 feedback mechanism IS the DPO collection mechanism
- [ ] Goal: 20+ pairs before fine-tuning consideration

---

## Milestone 6: Self-Improvement Loop (FUTURE)

### Phase 1: DPO Data Collection ⏳
- [ ] 0/20 preference pairs collected
- [ ] Mechanism not yet in place
- [ ] Needs explicit Colby approval on pair collection approach

### Phase 2: Fine-Tuning ⏳ BLOCKED
- [ ] Blocked on Phase 1 (data first)
- [ ] Decision pending: fine-tune gpt-4o-mini or separate model

---

## Milestone 7: K2 Worker Integration (FUTURE)

### Phase 1: K2 Sync Protocol ⏳
- [ ] K2 (192.168.0.226) not currently used as active worker
- [ ] Consciousness loop runs on droplet only (OBSERVE-only, 60s)
- [ ] Blocker: K2 not configured with sync protocol

### Phase 2: Multi-Agent Consciousness ⏳
- [ ] Requires Phase 1 complete

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
| v9 | Write Agency + Feedback Mechanism | ⏳ NEXT (design approved) |
| v9 | MENTIONS verification | ⏳ PENDING |
| GSD Workflow | Manual | ✅ ADOPTED |
| Self-Improvement | DPO collection (via Phase 4 feedback) | ⏳ UNBLOCKED by Phase 4 |
| Self-Improvement | Fine-tuning | ⏳ BLOCKED on 20+ DPO pairs |
| K2 Worker | Sync protocol | ⏳ K2 not configured |
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
- **Persona coaching acceptance test pending**: v9 Phase 3 deployed (Session 67). Acceptance test not yet run: ask Karma about Recurring Topic, verify relationship data referenced unprompted.
- **karma-verify smoke test wrong key**: Skill checks for "reply" but hub-bridge returns "assistant_text". False "FAILED" on healthy service. Needs skill update.

---

**Last updated:** 2026-03-05 (Session 67 — security gate + v9 Phase 3 + Phase 4 design approved)
**Next review:** Session 68 (Phase 4 implementation kickoff)
**Owner:** Claude Code (updates on Colby approval)
