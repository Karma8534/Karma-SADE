# KARMA MEMORY ARCHITECTURE — v7

**Version:** 7.1.0
**Date:** 2026-02-28
**Status:** GROUND TRUTH — Updated after CC session fixes (episode ingestion, bugs fixed, consciousness active)
**Supersedes:** KARMA_MEMORY_ARCHITECTURE_v7.md (7.0.0, 2026-02-28)

---

## 0. WHAT CHANGED SINCE v2

| Area | v2 Said | v7 Ground Truth |
|------|---------|-----------------|
| ChromaDB | "Validate: is ChromaDB being used?" | **Deployed and healthy** (container `anr-vault-search`). Used for semantic search. NOT removed. |
| Memory Tool API | "Six tools matching AgeMem interface" — Status: Planned | **NOT IMPLEMENTED.** These tools do not exist as callable functions on the droplet. |
| admit_memory pipeline | Described as working with dedup check | **Partially implemented.** PRs #10-12 added dedup on ingest and auto-promote candidates (Feb 27-28). Full pipeline as spec'd here is not yet deployed. |
| Tool-use in /v1/chat | "get_vault_file + graph_query ready" | **FIXED (v7.1).** Phantom tools removed from `buildSystemText()`. Line 376 now correctly lists `read_file, write_file, edit_file, bash` which match `TOOL_DEFINITIONS`. |
| Consciousness loop | "60s cycles, Karma reflects at session boundaries" | **ACTIVE (v7.1).** 60s OBSERVE-only cycles running. Auto-promote called every 10 cycles (~10 min). Episode deltas detected and logged. |
| File paths | References /home/neo/karma-sade/ for ledgers | **Ledgers live at /opt/seed-vault/memory_v1/ledger/** — Docker containers build from /opt/seed-vault/memory_v1/ |
| K2 role | "K2 runs cron jobs for telemetry" | **K2 NOT IMPLEMENTED.** No K2 sync, no K2 cron jobs. All operations on droplet. |
| Auto-promote | Not mentioned | **Deployed Feb 27-28.** Candidate facts can be auto-promoted from candidates.jsonl. |
| Backup | Not mentioned in memory doc | **Backup cron deployed Feb 27-28** (PR #12). |

---

## 0. PHILOSOPHICAL FILTER

*(Unchanged from v2 — these gates remain valid)*

| Gate | Rule | Rejects |
|------|------|---------|
| **Single Consciousness** | Karma is ONLY origin of thought. K2 never calls LLM autonomously. | AgeMem's RL training loop, Mem0's autonomous extraction, consciousness loop's OBSERVE/THINK/DECIDE/ACT/REFLECT cycle |
| **No Dependency Gravity** | Primitive must work with zero external libraries beyond what's already on the droplet | Mem0 SaaS, CrewAI, AgentScope, LangMem, any framework that becomes a load-bearing wall |
| **Droplet Primacy** | All persistent state on vault-neo. K2 is substrate, not source. | Any design where K2 holds authoritative state, any parallel truth source |
| **Budget Constraint** | <$100/month total. Droplet-only runtime. | GPU-intensive RL training, dedicated embedding servers, vector DB SaaS |
| **Colby Remains Meta-Layer** | Human is the judgment layer. Karma proposes, Colby disposes. | Autonomous self-modification without review |

**v7 UPDATE to gate 5:** Auto-promote for candidates.jsonl was deployed Feb 27-28. This is a controlled exception — candidates are low-risk facts, not identity/invariant changes. Tier 0 (identity spine) still requires Colby approval.

---

## 1. EXTRACTED PRIMITIVES

*(Unchanged from v2 — all 25 primitives from Sources A-D remain valid as design targets. See original document for full table.)*

**Implementation status update:**

| Primitive | v2 Status | v7 Status |
|-----------|-----------|-----------|
| A1 (Structured reflection templates) | ACCEPT | **NOT IMPLEMENTED** — session-end reflection not producing structured JSON |
| A3 (Telemetry as immortal) | ACCEPT — already implemented | **CONFIRMED** — JSONL ledgers operational |
| A5 (Deferral bucket) | ACCEPT — add deferred.jsonl | **NOT IMPLEMENTED** — deferred.jsonl does not exist on droplet |
| B1 (Six-tool memory interface) | ACCEPT the interface | **NOT IMPLEMENTED** — tools don't exist as callable functions |
| B2 (P_penalty for storage bloat) | ACCEPT as hard rules | **PARTIALLY IMPLEMENTED** — dedup on ingest deployed (PR #10-11) |
| C1 (Auto-categorized memory entries) | ACCEPT the tagging primitive | **NOT IMPLEMENTED** |
| C2 (Semantic search over memories) | ACCEPT — validate ChromaDB | **OPERATIONAL (v7.1)** — ChromaDB running, phantom tools bug fixed, correct tools now listed in system prompt |
| C3 (Extract-update pipeline) | ACCEPT | **PARTIALLY IMPLEMENTED** — dedup on ingest (PR #10-11) |
| D1 (Durable project memory via markdown) | ACCEPT — validates existing | **CONFIRMED** — identity.json, invariants.json, direction.md on droplet |
| D5 (Context compaction) | ACCEPT | **NOT IMPLEMENTED** |

---

## 2. TIERED STORAGE ARCHITECTURE

### Tier 0: Identity Spine (Immutable Unless Colby Edits)

| File | Location | Status |
|------|----------|--------|
| `identity.json` | `/home/neo/karma-sade/` | ✅ Deployed, loaded into every /v1/chat context |
| `invariants.json` | `/home/neo/karma-sade/` | ✅ Deployed, loaded into every /v1/chat context |
| `direction.md` | `/home/neo/karma-sade/` | ✅ Deployed, loaded into every /v1/chat context |

### Tier 1: Verified Knowledge (Graph + Embeddings)

| Store | Location | Status |
|-------|----------|--------|
| **FalkorDB neo_workspace** | Container `falkordb` on droplet | ✅ Running. **Node label is `Episodic` (NOT `Episode`).** Entity: 167, Episodic: 1240 (1239 lane=NULL, 1 canonical), Relationships: 832. Ollie and Baxter entities verified. |
| **ChromaDB** | Container `anr-vault-search` on droplet | ✅ Running and healthy. **NOT removed despite hardened review recommending it.** |

**v7.1 STATUS:** Tier 1 is operational. Phantom tools bug FIXED — correct tools now listed in system prompt. Episode ingestion pipeline deployed: hub-bridge fire-and-forget → karma-server /ingest-episode → Graphiti → FalkorDB.

**Admission rules (v7 deployed):**
- Dedup on ingest: ✅ Deployed (PR #10-11, Feb 27-28)
- Auto-promote candidates: ✅ Deployed (PR #11, Feb 27-28)
- Category tagging: ❌ NOT IMPLEMENTED
- Confidence scoring: ❌ NOT IMPLEMENTED
- Staleness detection: ❌ NOT IMPLEMENTED

### Tier 2: Operational Logs (Append-Only Ledgers)

| Ledger | Location | Status |
|--------|----------|--------|
| `memory.jsonl` | `/opt/seed-vault/memory_v1/ledger/` | ✅ 3847+ lines |
| `consciousness.jsonl` | `/opt/seed-vault/memory_v1/ledger/` | ✅ 284+ entries (ACTIVE — loop running, new entries being generated) |
| `collab.jsonl` | `/opt/seed-vault/memory_v1/ledger/` | ✅ Exists |
| `candidates.jsonl` | `/opt/seed-vault/memory_v1/ledger/` | ✅ Exists, auto-promote deployed |
| `decision_log.jsonl` | `/home/neo/karma-sade/` (if exists) | ⚠️ Status unverified |
| `failure_log.jsonl` | `/home/neo/karma-sade/` (if exists) | ⚠️ Status unverified |
| `deferred.jsonl` | NOT CREATED | ❌ Does not exist on droplet |

### Tier 3: Working Memory (Session-Scoped, Ephemeral)

| Store | Status |
|-------|--------|
| Session context (LLM context window) | ✅ Working — MAX_SESSION_TURNS, 30min TTL in hub-bridge |
| `session_plan.md` | ❌ NOT IMPLEMENTED |

### Tier 4: Candidate Queue (Pending Human Review)

| Store | Status |
|-------|--------|
| `collab.jsonl` | ✅ Exists — proposals written here |
| `candidates.jsonl` | ✅ Exists — auto-promote deployed Feb 27-28 |

---

## 3. MEMORY TOOL API — IMPLEMENTATION STATUS

| Tool | v2 Design | v7 Reality |
|------|-----------|------------|
| `admit_memory(content, category, source, confidence)` | Full pipeline with dedup + categorization | **Partial.** Dedup on ingest works. No category assignment. No confidence scoring. |
| `update_memory(memory_id, new_content, reason)` | Update FalkorDB node + re-embed in ChromaDB | **NOT IMPLEMENTED** |
| `delete_memory(memory_id, reason)` | Soft-delete + audit trail | **NOT IMPLEMENTED** |
| `retrieve_memory(query, top_k, category_filter)` | Semantic search via ChromaDB | **UNBLOCKED (v7.1)** — phantom tools bug fixed. Correct tools now listed. ChromaDB running and accessible. |
| `summarize_context(span)` | LLM-based compression via Hub Bridge | **NOT IMPLEMENTED** |
| `filter_context(criteria)` | Remove irrelevant entries from context | **NOT IMPLEMENTED** |

**Bottom line (v7.1):** Of the six planned tools, `admit_memory` has partial implementation (dedup) and `retrieve_memory` is now UNBLOCKED (phantom tools bug fixed). The other four don't exist. Additionally, a new `/ingest-episode` endpoint was deployed for browser chat ingestion.

---

## 4. ADMISSION RULES — IMPLEMENTATION STATUS

| Rule | Designed | Deployed |
|------|----------|----------|
| Dedup check (cosine sim > 0.85) | ✅ | ✅ (PR #10-11) |
| Category assignment (7 categories) | ✅ | ❌ |
| Confidence assignment (source-based) | ✅ | ❌ |
| Staleness check (90-day flag) | ✅ | ❌ |
| Context budget (4000 token cap) | ✅ | ❌ |
| Freshness update on retrieval | ✅ | ❌ |
| Session-end reflection (structured template) | ✅ | ❌ |

---

## 5. IMPLEMENTATION TIMELINE (Revised for v7)

### Phase 1: Fix Retrieval ✅ COMPLETE (v7.1)
| Task | Description | Status |
|------|-------------|--------|
| 1.1 | Fix phantom tools bug in buildSystemText() | ✅ DONE |
| 1.2 | Remove duplicate karmaCtx injection | ✅ DONE |
| 1.3 | Rebuild hub-bridge container | ✅ DONE |
| 1.4 | Test that /v1/chat can retrieve memories | ✅ DONE — Karma recalls Ollie, Baxter, guitar, favorite color |

### Phase 2: Complete Admission Pipeline (Week 1-2)
| Task | Description | Effort |
|------|-------------|--------|
| 2.1 | Add category auto-tagging to admit_memory | Medium |
| 2.2 | Add confidence scoring to admit_memory | Medium |
| 2.3 | Create deferred.jsonl ledger | Small |
| 2.4 | Verify ChromaDB embedding quality for dedup threshold | Small |

### Phase 3: Context Management (Week 3-4)
| Task | Description | Effort |
|------|-------------|--------|
| 3.1 | Implement summarize_context tool | Medium |
| 3.2 | Implement filter_context tool | Medium |
| 3.3 | Enforce 4000-token context budget on retrieval | Medium |
| 3.4 | Implement session-end reflection template | Medium |

### Phase 4: Maintenance & Hardening (Week 5-6)
| Task | Description | Effort |
|------|-------------|--------|
| 4.1 | Implement staleness detection (90-day cron) | Small |
| 4.2 | Implement context compaction for FalkorDB | Medium |
| 4.3 | Periodic memory audit (quality scoring) | Medium |
| 4.4 | update_memory and delete_memory tools | Medium |

---

## 6. COST MODEL (Updated for v7)

| Component | Current Cost | Notes |
|-----------|-------------|-------|
| Droplet (4GB) | $24/mo | Same as v2 — NOT upgraded to 8GB |
| FalkorDB (on droplet) | $0 | |
| ChromaDB (on droplet) | $0 | Still deployed |
| GLM-4.7-Flash (Z.AI) | FREE | Primary chat model |
| gpt-4o-mini (OpenAI) | ~$1-3/mo | Tool calls only |
| gpt-4o (OpenAI) | ~$0-1/mo | 429 fallback only |
| Backup cron | $0 | On-droplet storage |
| **Total** | **~$25-28/mo** | Well within $100 budget |

**Note:** Cost is MUCH lower than v2 estimated because:
1. Consciousness loop runs OBSERVE-only (no LLM calls, per design decision)
2. MiniMax M2.5 is not used (not in routing)
3. GLM-4.7-Flash is FREE
4. Only gpt-4o-mini costs money for tool calls, and gpt-4o for rare fallback

---

## 7. WHAT DIES (Updated)

| Component | v2 Said | v7 Status |
|-----------|---------|-----------|
| Consciousness loop (60s) | Kill it | **ACTIVE (v7.1)** — 60s OBSERVE-only cycles running, auto-promote every 10 cycles. Not killed — repurposed for delta detection + auto-promotion. |
| consciousness.jsonl as active input | Archive 109 entries | **ACTIVE (v7.1)** — 284+ entries, growing. Loop writing new entries (LOG_GROWTH, cycle reflections). |
| K2 as consciousness worker | Replace with substrate | **K2 never existed** — no K2 deployment |
| Ambient background learning | Replace with scheduled task | ✅ Valid — no background learning running |

## 8. WHAT LIVES (Updated)

| Component | Status |
|-----------|--------|
| Droplet as source of truth | ✅ Operational and verified |
| FalkorDB graph + ChromaDB embeddings | ✅ Both running and healthy |
| JSONL append-only ledgers | ✅ Operational (memory.jsonl 3847+ lines) |
| Identity spine files | ✅ Deployed, loaded every session |
| Hub Bridge API | ✅ Operational (bugs fixed in v7.1) |
| Colby as meta-learning layer | ✅ Non-negotiable |
| Dedup on ingest | ✅ Deployed (PR #10-11) |
| Auto-promote candidates | ✅ Deployed (PR #11) |
| Backup cron | ✅ Deployed (PR #12) |

---

## 9. OPEN QUESTIONS (Updated for v7)

1. **ChromaDB keep or kill?** Hardened review recommended removing it. It's still running and healthy. Phantom tools bug is now fixed — retrieval can be tested. Decision pending.

2. ~~**FalkorDB data quality:**~~ Corrupted entities cleaned up (0 null uuid remaining as of v7.1).

3. **Session boundary definition:** Still unresolved from v2. When does a "session" start and end?

4. **Deferred.jsonl:** Still not created. Is this still wanted?

5. **Auto-promote scope:** Auto-promote now wired to consciousness loop (every 10 cycles). Thresholds: confidence >= 0.80, corroboration >= 1, age >= 30 min. Is Colby comfortable with these for all categories?

6. **Lane=NULL episodes:** 1239 Episodic nodes have lane=NULL (batch-ingested). Consider bulk-promoting to canonical or running auto-promote sweep.

---

**END OF MEMORY ARCHITECTURE v7**
