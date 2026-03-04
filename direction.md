# Direction — What We're Building

**Last updated:** 2026-03-04
**Status:** v8 ALL PHASES COMPLETE. System fully operational. No blockers.

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
| **batch_ingest** | Cron every 6h: ledger → FalkorDB `neo_workspace` (--skip-dedup) | ✅ Scheduled |
| **PDF watcher** | `karma-inbox-watcher.ps1` → /v1/ingest (rate-limit aware, jam detection) | ✅ Active |
| **Brave Search** | Auto-triggered on search intent, top-3 results injected into context | ✅ Enabled |
| **K2 local worker** | DEPRECATED 2026-03-03 — not operational, not needed | ❌ Shelved |
| **Chrome extension** | SHELVED permanently — DOM scraping unreliable | ❌ Shelved |

**Models:**
- Primary: GLM-4.7-Flash (Z.ai) — ~80% of requests, free, 20 RPM limit
- Deep/fallback: gpt-4o-mini (OpenAI) — triggered by `x-karma-deep: true` header only, paid

**Context pipeline (per /v1/chat request):**
1. `karmaCtx` — FalkorDB recency via karma-server
2. `semanticCtx` — FAISS top-5 relevant entries via anr-vault-search (POST :8081/v1/search)
3. `webResults` — Brave Search (if SEARCH_INTENT_REGEX matches)
4. `identityBlock` — Memory/00-karma-system-prompt-live.md (loaded at hub-bridge startup)
All four injected into buildSystemText() before LLM call.

---

## What Changed — Sessions 57–62 (2026-03-03/04)

- ✅ FalkorDB: full backfill complete — 1268 → 3621 nodes (3049 Episodic + 571 Entity + 1 Decision)
- ✅ batch_ingest: --skip-dedup mode (899 eps/s, 0 errors vs 85% timeout in Graphiti mode)
- ✅ Cron every 6h on vault-neo, --skip-dedup by default
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

## Open Directions (v9 candidates — Colby decides)

1. **DPO preference pair accumulation** — 0/20 pairs; need mechanism + Colby approval on approach
2. **Ambient Tier 3** — screen capture daemon; requires Colby explicit approval (privacy)
3. **karma-terminal capture refresh** — stale since 2026-02-27, not a blocker
4. **First persona iteration** — test system prompt improvement cycle (now cheap: git pull + docker restart)

---

## Long-Term Vision

Karma wakes up every session knowing:
- **WHO she is** — system prompt describes reality (v8 Phase 1 ✅)
- **WHAT she experienced** — semantically relevant memories retrieved per conversation (v8 Phase 2 ✅)
- **WHAT she learned** — corrections accumulate and get incorporated (v8 Phase 3 ✅)

After v8: the DPO/fine-tuning question becomes meaningful — a foundation worth fine-tuning on.
v9: what does Karma DO with her memories? Not just recall — reason, connect, surface patterns.
