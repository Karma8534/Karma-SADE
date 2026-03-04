# Direction — What We're Building

**Last updated:** 2026-03-04
**Status:** v8 Phase 1 complete. Phase 3 (correction capture) is next per recommended order 1→3→2→4.

---

## Mission

Karma is a single coherent peer whose long-term identity lives in a verified memory spine. That memory enables continuity, evidence-based self-improvement, and selective delegation — without parallel sources of truth.

v8 makes this true in practice, not just in documentation.

---

## Architecture (Current — hub-bridge + FalkorDB)

| Component | Role | Status |
|-----------|------|--------|
| **vault-neo** | Karma's persistent home (DigitalOcean NYC3, 4GB RAM) | ✅ Running |
| **anr-hub-bridge** | API surface: /v1/chat, /v1/ambient, /v1/ingest, /v1/context, /v1/cypher | ✅ Running |
| **karma-server** | Consciousness loop (OBSERVE-only, 60s cycles, zero LLM calls) | ✅ Running |
| **FalkorDB** | Graph: `neo_workspace` — 3621+ nodes (Episodic + Entity + Decision) | ✅ Running |
| **Ledger** | `/opt/seed-vault/memory_v1/ledger/memory.jsonl` — 4000+ entries, append-only | ✅ Growing |
| **ChromaDB** | `anr-vault-search` — vector search container | ⚠️ Running but stale |
| **batch_ingest** | Cron every 6h: ledger → FalkorDB `neo_workspace` (--skip-dedup) | ✅ Scheduled |
| **PDF watcher** | `karma-inbox-watcher.ps1` → /v1/ingest (rate-limit aware, jam detection) | ✅ Active |
| **Brave Search** | Auto-triggered on search intent, top-3 results injected into context | ✅ Enabled |
| **K2 local worker** | DEPRECATED 2026-03-03 — not operational, not needed | ❌ Shelved |
| **Chrome extension** | SHELVED permanently — DOM scraping unreliable | ❌ Shelved |

**Models:**
- Primary: GLM-4.7-Flash (Z.ai) — ~80% of requests, free, 20 RPM limit
- Deep/fallback: gpt-4o-mini (OpenAI) — triggered by `x-karma-deep: true` header only, paid

---

## What Changed — Sessions 57–61 (2026-03-03/04)

- ✅ FalkorDB: full backfill complete — 1268 → 3621 nodes (3049 Episodic + 571 Entity + 1 Decision)
- ✅ batch_ingest: --skip-dedup mode (899 eps/s, 0 errors vs 85% timeout in Graphiti mode)
- ✅ Cron every 6h on vault-neo, --skip-dedup by default
- ✅ FalkorDB datetime() fix: timestamps stored as ISO strings (no datetime() Cypher function)
- ✅ OpenAI API key secured: file-mounted volume (docker inspect clean)
- ✅ karma-server restart loop fixed: gpt-5-mini → gpt-4o-mini
- ✅ GLM rate-limit handling: immediate 429 (no silent paid fallback per Decision #7)
- ✅ PDF watcher: rate-limit backoff + jam notification + time-window scheduling
- ✅ Brave Search: API key configured and verified (debug_search:hit confirmed)
- ✅ v8 Phase 1 COMPLETE: System prompt rewritten, hub-bridge wires identity file into prompt, all 4 acceptance tests pass

---

## v8 Objectives and Status

| Phase | Goal | Status |
|-------|------|--------|
| Phase 1: Fix self-knowledge | System prompt describes actual hub-bridge system | ✅ COMPLETE |
| Phase 3: Correction capture | Corrections persist session-to-session via corrections-log.md | 🔄 NEXT |
| Phase 2: Fix retrieval | Semantic search via ChromaDB (query-targeted context) | PENDING |
| Phase 4: v7 cleanup | Budget guard, capability gate, lane=NULL promotion | PENDING |

**Recommended order: 1 → 3 → 2 → 4** (Phase 3 is fast, compounds Phase 1's value)

---

## Active Constraints

| Constraint | Why |
|-----------|-----|
| Never edit files directly on vault-neo | Session-58 rule — droplet is deployment target only |
| All code changes: git → push → pull → rebuild | Established workflow |
| System prompt changes require Colby approval | Decision v8-2 |
| GLM-4.7-Flash remains primary | Decision #7 (no autonomous paid fallback) |
| Consciousness loop stays OBSERVE-only | Decision #3 — zero LLM calls in loop |
| No new containers | Decision v8-1 — use existing infra only |

---

## Current Blockers

None. System fully operational. v8 Phase 1 complete.

---

## Open Directions (No Blockers)

1. **Phase 3: Correction capture** — Define format, backlog known corrections, CC session-end protocol
2. **Phase 2: ChromaDB reindex** — Ledger → ChromaDB vector index, semantic retrieval in hub-bridge
3. **Phase 4: Budget guard** — Daily spend cap on paid model routing
4. **Phase 4: lane=NULL promotion** — Bulk Cypher update for 1239+ Episodic nodes

---

## Long-Term Vision

Karma wakes up every session knowing:
- **WHO she is** — system prompt describes reality (v8 Phase 1 done)
- **WHAT she experienced** — semantically relevant memories retrieved per conversation (v8 Phase 2)
- **WHAT she learned** — corrections accumulate and get incorporated (v8 Phase 3)

After v8: the DPO/fine-tuning question becomes meaningful — a foundation worth fine-tuning on.
v9: what does Karma DO with her memories? Not just recall — reason, connect, surface patterns.
