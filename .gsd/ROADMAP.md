# ROADMAP: Karma Peer — Phases & Milestones

**Last updated:** 2026-03-04
**Current phase:** v8 COMPLETE — all phases done
**Next major phase:** v9 (TBD — see Decision Points below)

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
| GSD Workflow | Manual | ✅ ADOPTED |
| Self-Improvement | DPO collection | ⏳ 0/20 pairs |
| Self-Improvement | Fine-tuning | ⏳ BLOCKED |
| K2 Worker | Sync protocol | ⏳ K2 not configured |
| K2 Worker | Multi-agent | ⏳ FUTURE |

---

## Decision Points (Open)

### v9 Direction
**Question:** What is v9? Possible directions:
- Ambient Tier 3 (screen capture daemon)
- DPO preference pair accumulation mechanism
- karma-terminal capture refresh (stale since 2026-02-27)
- K2 worker integration
**Next step:** Colby decides priority.

### K2 Availability
**Question:** Is K2 (192.168.0.226) intended as active worker anytime soon?
**Implication:** Unlocks K2 sync protocol, multi-agent consciousness, potential Tier 3.

---

## Known Quality Gaps (Active)

- **--skip-dedup = no entity extraction**: batch_ingest in --skip-dedup mode writes Episodic nodes directly via Cypher, bypassing Graphiti. This means NO entity/relationship extraction for bulk-ingested episodes. Only Episodic nodes exist for those 3049 episodes — no cross-session Entity nodes derived from them. Acceptable for now (entities come from real-time Graphiti for new episodes), but long-term the bulk episodes have no entity graph.
- **karma-terminal capture stale**: last capture 2026-02-27. Not a blocker but gap in capture continuity.
- **DPO pairs**: 0/20 collected. Fine-tuning loop not started.
- **Brave Search**: auto-triggered by regex on message content. No manual override or session-level toggle. Low priority.

---

**Last updated:** 2026-03-04 (Session 62 — v8 complete)
**Next review:** When v9 direction is decided
**Owner:** Claude Code (updates on Colby approval)
