# Direction — What We're Building

**Last updated:** 2026-03-05
**Status:** v9 IN PROGRESS — Phase 4 write_memory gate COMPLETE (Session 68). Next: karma-verify fix + Phase 5 MENTIONS verification.

---

## Mission

Karma is a single coherent peer whose long-term identity lives in a verified memory spine. That memory enables continuity, evidence-based self-improvement, and selective delegation — without parallel sources of truth.

v8 made this true in practice, not just in documentation.

---

## Architecture (Current — hub-bridge + FalkorDB)

| Component | Role | Status |
|-----------|------|--------|
| **vault-neo** | Karma's persistent home (DigitalOcean NYC3, 4GB RAM) | ✅ Running |
| **anr-hub-bridge** | API surface: /v1/chat, /v1/ambient, /v1/ingest, /v1/context, /v1/cypher | ✅ Running |
| **karma-server** | Consciousness loop (OBSERVE-only, 60s cycles, zero LLM calls) | ✅ Running |
| **FalkorDB** | Graph: `neo_workspace` — 3621 nodes (Episodic + Entity + Decision) | ✅ Running |
| **Ledger** | `/opt/seed-vault/memory_v1/ledger/memory.jsonl` — 4000+ entries, append-only | ✅ Growing |
| **anr-vault-search (FAISS)** | Custom search_service.py — FAISS + text-embedding-3-small, 4073+ entries, auto-reindex | ✅ Live |
| **batch_ingest** | Cron every 6h: Graphiti watermark mode (entity extraction for new episodes) | ✅ Scheduled |
| **PDF watcher** | `karma-inbox-watcher.ps1` → /v1/ingest (rate-limit aware, jam detection) | ✅ Active |
| **Brave Search** | Auto-triggered on search intent, top-3 results injected into context | ✅ Enabled |
| **K2 local worker** | DEPRECATED 2026-03-03 — not operational, not needed | ❌ Shelved |
| **Chrome extension** | SHELVED permanently — DOM scraping unreliable | ❌ Shelved |

**Models:**
- Primary: GLM-4.7-Flash (Z.ai) — ~80% of requests, free, 40 RPM self-imposed limit (raised Session 66)
- Deep/fallback: gpt-4o-mini (OpenAI) — triggered by `x-karma-deep: true` header only, paid

**Context pipeline (per /v1/chat request):**
1. `karmaCtx` — FalkorDB recency via karma-server (includes Entity Relationships + Recurring Topics as of Session 64)
2. `semanticCtx` — FAISS top-5 relevant entries via anr-vault-search (POST :8081/v1/search)
3. `webResults` — Brave Search (if SEARCH_INTENT_REGEX matches)
4. `identityBlock` — Memory/00-karma-system-prompt-live.md (loaded at hub-bridge startup)
All four injected into buildSystemText() before LLM call.

**karmaCtx sections (build_karma_context output):**
- User Identity, Relevant Knowledge, Entity Relationships (RELATES_TO edges), Recurring Topics (top-10 by episode count), Recent Memories, Recently Learned, What I Know About The User

---

## What Changed — Sessions 57–64 (2026-03-03/05)

- ✅ FalkorDB: full backfill complete — 1268 → 3621 nodes (3049 Episodic + 571 Entity + 1 Decision)
- ✅ batch_ingest: --skip-dedup bulk backfill (899 eps/s); then watermark Graphiti mode for incremental
- ✅ Graphiti watermark deployed (Session 63): new episodes get entity extraction; :MENTIONS edges growing
- ✅ FalkorDB datetime() fix: timestamps stored as ISO strings (no datetime() Cypher function)
- ✅ OpenAI API key secured: file-mounted volume (docker inspect clean)
- ✅ karma-server restart loop fixed: gpt-5-mini → gpt-4o-mini
- ✅ GLM rate-limit handling: immediate 429 (no silent paid fallback per Decision #7)
- ✅ PDF watcher: rate-limit backoff + jam notification + time-window scheduling
- ✅ Brave Search: API key configured and verified (debug_search:hit confirmed)
- ✅ v8 Phase 1: System prompt rewritten and wired into hub-bridge — 4/4 acceptance tests pass
- ✅ v8 Phase 3: corrections-log.md created, CC session-end step 2 added
- ✅ v8 Phase 2: FAISS semantic retrieval live — fetchSemanticContext() in hub-bridge, parallel fetch
- ✅ v8 Phase 4: Budget guard + capability gate verified; 3040 lane=NULL nodes → lane="episodic"
- ✅ Session 64: Entity Relationships (RELATES_TO r.fact) + Recurring Topics (top-10 by episode count) live in karmaCtx

---

## v8 — COMPLETE

| Phase | Goal | Status |
|-------|------|--------|
| Phase 1: Fix self-knowledge | System prompt describes actual hub-bridge system | ✅ COMPLETE |
| Phase 3: Correction capture | Corrections persist via corrections-log.md + CC protocol | ✅ COMPLETE |
| Phase 2: Fix retrieval | FAISS semantic search — 4073 entries, parallel context injection | ✅ COMPLETE |
| Phase 4: v7 cleanup | Budget guard verified, capability gate verified, lane=NULL fixed | ✅ COMPLETE |

---

## Active Constraints

| Constraint | Why |
|-----------|-----|
| Never edit files directly on vault-neo | Session-58 rule — droplet is deployment target only |
| All code changes: git → push → pull → rebuild | Established workflow |
| System prompt changes: git pull + docker restart only | KARMA_IDENTITY_PROMPT is file-loaded |
| GLM-4.7-Flash remains primary | Decision #7 (no autonomous paid fallback) |
| Consciousness loop stays OBSERVE-only | Decision #3 — zero LLM calls in loop |
| No new containers | Decision v8-1 — use existing infra only |

---

## Current Blockers

None. System fully operational. v8 complete.

---

## v9 — IN PROGRESS

**Priority order (Session 64 decision):**
1. **Persona iteration** ← NEXT — system prompt must learn to USE entity relationships + recurring topics in karmaCtx. Cheap: git pull + docker restart only. Zero infra changes.
2. **MENTIONS edge growth** — 3049 bulk episodes lack MENTIONS. New episodes get extraction via watermark cron. Acceptable for now; historical gap won't be addressed until explicit backfill decision.
3. **DPO preference pairs** — 0/20; needs mechanism design + Colby approval on approach.
4. **karma-terminal refresh** — stale since 2026-02-27, low priority.
5. **Ambient Tier 3** — screen capture daemon; blocked on Colby privacy approval.

---

## External Validation (Session 65 — CreatorInfo.pdf)

Boris Cherny (Claude Code creator) published his CLAUDE.md workflow in Jan 2026. It went viral.
Key principles that independently validate Karma's architecture:

| Cherny's Principle | Karma's Implementation |
|-------------------|----------------------|
| Two-tier: global (`~/.claude/CLAUDE.md` = who you are) + project-level (= what we're building) | `identity.json` (global identity) + `direction.md` (project-specific) |
| "Every mistake becomes a rule" — PR mistake → CLAUDE.md permanent correction | `Memory/corrections-log.md` + CC Session End Protocol step 2 |
| Constitution not manual — ~2,500 token sweet spot; long explanations → separate skill files | CLAUDE.md behavioral rules; long procedures in `.claude/skills/` |
| Slash commands = workflow triggers that enforce CLAUDE.md standards | `.claude/skills/` + superpowers workflow |

**Gap identified (Session 65):** Cherny's method uses PR-review as the systematic trigger for corrections capture. Karma's current capture is session-based (session-end protocol step 2). A more systematic trigger mechanism would close this gap. Documented as Known Quality Gap — not blocking v9.

---

## Long-Term Vision

Karma wakes up every session knowing:
- **WHO she is** — system prompt describes reality (v8 Phase 1 ✅)
- **WHAT she experienced** — semantically relevant memories retrieved per conversation (v8 Phase 2 ✅)
- **WHAT she learned** — corrections accumulate and get incorporated (v8 Phase 3 ✅)

After v8: the DPO/fine-tuning question becomes meaningful — a foundation worth fine-tuning on.
v9: what does Karma DO with her memories? Not just recall — reason, connect, surface patterns.
Session 64 answered this partially: entity relationships and topic patterns are now in every response context. The persona must now be taught to USE them.
Session 65: external validation confirms architecture is sound. Gap: corrections capture needs systematic trigger (currently session-based, not event-driven).
Session 66: promise loop fixed — Karma no longer makes false promises. GLM-4.7-Flash now has real tool-calling (graph_query, get_vault_file). System prompt corrected for honesty (tool list, context size, rate-limit behavior). Next: behavioral coaching — teach Karma WHAT TO DO when she sees Entity Relationships + Recurring Topics data in karmaCtx.
Session 67: behavioral coaching deployed (v9 Phase 3) — Karma now has explicit instructions to USE Entity Relationships + Recurring Topics data. Security fix: deep-mode tool gate prevents standard chat from accessing tools. v9 Phase 4 design approved: write agency via thumbs up/down (write_memory tool + POST /v1/feedback). Not yet implemented.
Session 68: v9 Phase 4 COMPLETE — write_memory tool + POST /v1/feedback gate + unified.html thumbs UI + DPO pairs in vault ledger (type:"log", tags:["dpo-pair"]). All 10 tasks implemented, tested, deployed. Acceptance test passed (5/5). 0/20 DPO pairs accumulated so far — mechanism now live. Next: karma-verify skill fix + Phase 5 MENTIONS edge growth verification.
