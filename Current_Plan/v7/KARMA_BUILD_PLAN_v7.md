# KARMA BUILD PLAN — v7

**Version:** 7.1.0
**Date:** 2026-02-28
**Status:** GROUND TRUTH — Updated after CC session fixes (episode ingestion, auto-promote, bug fixes)
**Supersedes:** KARMA_BUILD_PLAN_v7.md (7.0.0, 2026-02-28)

---

## 0. WHAT CHANGED SINCE v2

| Area | v2 Said | v7 Ground Truth |
|------|---------|-----------------|
| LLM Routing | GLM-4.7-Flash (~80%) + gpt-4o-mini (~20%) | GLM-4.7-Flash (chat primary) + gpt-4o-mini (tool calls) + gpt-4o (429 fallback) |
| Consciousness Loop | 60s autonomous cycles running | **ACTIVE.** 60s OBSERVE-only cycles running. Auto-promote called every 10 cycles (~10 min). Episode deltas detected and logged. |
| ChromaDB | "May have been removed" / "Remove ChromaDB" | **Still deployed.** Container `anr-vault-search` is running and healthy. |
| Tool-Use in /v1/chat | "Infrastructure built, not wired" | **FIXED (v7.1).** Phantom tool bug resolved — `buildSystemText()` now correctly lists `read_file, write_file, edit_file, bash` which match `TOOL_DEFINITIONS`. |
| karmaCtx injection | Single injection | **FIXED (v7.1).** Single injection in `base` (line 369). Duplicate "YOUR COMPLETE KNOWLEDGE STATE" block removed. |
| Build Phases 0-5 | Status: "Planned" | **COMPLETE.** All deployed and operational. |
| Recent work | Ends at 2026-02-26 | PRs #10-12 merged Feb 27-28: retrieval fix, dedup, auto-promote candidates, backup cron. **CC session Feb 28:** episode ingestion pipeline, /ingest-episode endpoint, consciousness loop auto-promote, bug fixes. |
| Containers | 5-6 listed | **7 running:** anr-hub-bridge, karma-server (healthy), anr-vault-api (healthy), anr-vault-search (healthy), anr-vault-caddy, anr-vault-db (healthy), falkordb |
| Operational path | /home/neo/karma-sade/ | **Docker builds from /opt/seed-vault/memory_v1/** — NOT /home/neo/karma-sade/ |
| Ollie (test entity) | Not mentioned | **Exists in FalkorDB** with 3 entity entries and proper summary |
| MiniMax M2.5 | Listed as primary chat model | **Not in deployed routing.** Hub-bridge uses GLM-4.7-Flash via Z.AI, gpt-4o-mini via OpenAI, gpt-4o as fallback. |
| GLM-5 | Listed as reasoning model | **Not in deployed routing.** Reasoning calls go through the same GLM-4.7-Flash → gpt-4o-mini chain. |
| Groq | Listed as speed fallback | **Not in deployed routing.** No Groq provider calls in hub-bridge server.js. |

---

## 1. CURRENT DEPLOYED STATE (as of 2026-02-28)

### 1.1 Infrastructure

| Component | Status | Details |
|-----------|--------|---------|
| Droplet | arknexus-vault-01, 4GB RAM, 50GB disk, Ubuntu 24.04, NYC3 | IP: 64.225.13.144 |
| Docker containers | 7 running | See §1.2 |
| SSH access | Key-based, user `neo` | sudo password: `ollieboo` |
| GitHub repo | `Karma8534/Karma-SADE` (private) | Connected via github_mcp_direct |
| Domain | arknexus.net | TLS via Caddy (anr-vault-caddy container) |

### 1.2 Running Containers

| Container | Health | Role |
|-----------|--------|------|
| anr-hub-bridge | running | Node.js API gateway (server.js, 1,872 lines) |
| karma-server | healthy | Python/FastAPI (server.py, 2,629 lines) |
| anr-vault-api | healthy | Vault REST API |
| anr-vault-search | healthy | ChromaDB (semantic search) |
| anr-vault-caddy | running | TLS reverse proxy |
| anr-vault-db | healthy | PostgreSQL |
| falkordb | running | Graph database (neo_workspace) |

### 1.3 LLM Routing (Actual Deployed)

```
/v1/chat request arrives at hub-bridge
  ↓
buildSystemText() constructs system prompt
  - Injects identity spine (karmaCtx) [BUG: injected twice]
  - Advertises phantom tools [BUG: tools don't exist in TOOL_DEFINITIONS]
  ↓
Model selection:
  1. GLM-4.7-Flash via Z.AI — PRIMARY for chat
  2. gpt-4o-mini via OpenAI — for tool calls / structured output
  3. gpt-4o via OpenAI — 429 rate-limit fallback
  ↓
Response returned with telemetry (debug_stop_reason, token counts)
```

**NOT deployed (despite plans saying so):**
- MiniMax M2.5 — not in server.js routing
- GLM-5 — not in server.js routing  
- Groq (Llama) — not in server.js routing

### 1.4 FalkorDB State

- Graph: `neo_workspace`
- **Node label is `Episodic` (NOT `Episode`)** — KCC audit v7.0 used wrong label and reported 0 episodes (false alarm)
- Entity: 167, Episodic: 1240 (1239 lane=NULL, 1 canonical, 0 candidate), Relationships: 832
- Ollie entity exists with proper summary
- Baxter entity exists (golden retriever, adopted by Colby) — verified via learning test
- Real-time ingestion working: new conversations → Graphiti → entities/relationships updated

### 1.5 File Paths (CRITICAL)

| Purpose | Path | Notes |
|---------|------|-------|
| Docker builds, operational code | `/opt/seed-vault/memory_v1/` | **THIS IS WHAT CONTAINERS USE** |
| Git clone (reference only) | `/home/neo/karma-sade/` | **NOT used by containers** |
| Ledgers | `/opt/seed-vault/memory_v1/ledger/` | memory.jsonl, consciousness.jsonl, collab.jsonl, candidates.jsonl |
| Hub auth | `/opt/seed-vault/memory_v1/hub_auth/` | hub.chat.token.txt |
| FalkorDB data | `/opt/seed-vault/falkordb/` | Persistent graph storage |

---

## 2. BUGS STATUS (Updated v7.1 — 2026-02-28)

### Bug 1: Phantom Tools in buildSystemText() — ✅ FIXED

**Status:** RESOLVED. The `get_vault_file(alias)` and `graph_query(cypher)` references have been removed from `buildSystemText()`. Line 376 now correctly lists `read_file | write_file | edit_file | bash` which match `TOOL_DEFINITIONS`.

### Bug 2: Duplicate karmaCtx Injection — ✅ FIXED

**Status:** RESOLVED. karmaCtx is now injected exactly once in the `base` variable (line 369). The duplicate "YOUR COMPLETE KNOWLEDGE STATE" block has been removed.

### Bug 3: Consciousness Loop Inactive — ✅ FIXED

**Status:** RESOLVED. The consciousness loop is now ACTIVE:
- 60s OBSERVE-only cycles running (no LLM calls, per Decision #3)
- Detects new episodes via FalkorDB delta queries
- Logs discoveries and growth to consciousness.jsonl + SQLite observations
- **Calls `/auto-promote` every 10 cycles (~10 minutes)** to promote eligible candidates
- Memory decay and self-model prune running on schedule
- Evidence: `[CONSCIOUSNESS] [INFO] Cycle #1: LOG_GROWTH — Rapid growth: 20 new episodes in one cycle`

The loop was previously showing only IDLE cycles because no new episodes were being ingested. With the episode ingestion fix (see §2A below), the loop now has data to observe.

### NEW: Episode Ingestion Pipeline — ✅ DEPLOYED (v7.1)

**Problem (pre-v7.1):** Browser chat path (hub-bridge → karma-server) never called `ingest_episode()`. The function only fired on the `/ask` endpoint, which hub-bridge never calls. Result: conversations through the browser were never ingested as episodes.

**Fix deployed:**
1. **`/ingest-episode` endpoint added** to karma-server (server.py line 1454) — accepts `user_msg`, `assistant_msg`, `source`, calls `ingest_episode()` via `asyncio.create_task()`
2. **Hub-bridge fire-and-forget** added to `/v1/chat` handler (server.js line 1305) — after generating response, POSTs to `http://karma-server:8340/ingest-episode` non-blocking
3. **Auto-promote wired** to consciousness loop (consciousness.py line 177) — calls `/auto-promote` every 10 cycles

**Verified working:** Taught Karma "Baxter" (golden retriever) → episode ingested → entity created in graph → recalled on demand.

---

## 3. BUILD PHASES — STATUS

### Phase 0: Foundation Infrastructure ✅ COMPLETE
- Droplet provisioned and operational
- Docker stack running (7 containers)
- FalkorDB with neo_workspace graph
- PostgreSQL for metadata
- Caddy for TLS
- SSH access configured

### Phase 1: Hub Bridge API ✅ COMPLETE
- /v1/chat endpoint operational
- Bearer token auth working
- Multi-model routing (GLM-4.7-Flash + gpt-4o-mini + gpt-4o fallback)
- Session memory (MAX_SESSION_TURNS, TTL)
- Identity spine injection (karmaCtx loaded from vault files)

### Phase 2: Karma Server ✅ COMPLETE
- FastAPI server running (2,629 lines)
- FalkorDB integration (Graphiti)
- Batch ingestion (batch_ingest.py) — 1488+ episodes
- Health endpoint

### Phase 3: Memory Ledger System ✅ COMPLETE
- memory.jsonl (3449+ lines)
- consciousness.jsonl (109 entries)
- collab.jsonl (proposals)
- candidates.jsonl (candidate facts)
- Append-only, persistent on droplet

### Phase 4: Identity Spine ✅ COMPLETE
- identity.json on droplet
- invariants.json on droplet
- direction.md on droplet
- Loaded into every /v1/chat context

### Phase 5: Memory Retrieval Pipeline ✅ COMPLETE (with bugs)
- ChromaDB deployed (anr-vault-search, healthy)
- FalkorDB graph queries operational
- **BUT:** Phantom tools bug means LLM can't actually invoke retrieval tools (see Bug 1)
- **BUT:** karmaCtx duplication wastes tokens (see Bug 2)

### Phase 6: Hardening 🔄 IN PROGRESS
**Completed (PRs #10-12, Feb 27-28):**
- Retrieval fix
- Dedup on ingest
- Auto-promote candidates
- Backup cron

**Remaining:**
- Fix phantom tools bug (Bug 1)
- Fix duplicate karmaCtx (Bug 2)
- Budget guard (not deployed)
- Capability gate (not deployed)
- Ledger rotation (not deployed)

### Phase 7: Memory Architecture Upgrade ❌ NOT STARTED
- Six-tool memory API (admit_memory, update_memory, delete_memory, retrieve_memory, summarize_context, filter_context)
- Admission rules (dedup, categorization, confidence scoring, staleness)
- Tiered storage (Hot/Warm/Cold)
- Session-end reflection templates
- Context budget enforcement (4000 token cap)

### Phase 8: K2 Integration ❌ NOT STARTED / DEFERRED
- K2 as substrate (cron-based telemetry only, no LLM calls)
- K2 → droplet sync
- K2 polling endpoint

---

## 4. IMMEDIATE PRIORITIES (Ordered — Updated v7.1)

| # | Task | Status | Notes |
|---|------|--------|-------|
| ~~1~~ | ~~Fix phantom tools in buildSystemText()~~ | ✅ DONE | Resolved pre-v7.1 — correct tools now listed |
| ~~2~~ | ~~Remove duplicate karmaCtx injection~~ | ✅ DONE | Resolved pre-v7.1 — single injection |
| ~~3~~ | ~~Rebuild hub-bridge container~~ | ✅ DONE | Rebuilt with all fixes |
| ~~4~~ | ~~Verify memory retrieval works~~ | ✅ DONE | Karma recalls Ollie, Baxter, guitar, favorite color |
| 5 | **Deploy budget guard** | ❌ NOT DONE | Spend tracking exists in hub-bridge (usd_estimate, spend object) but no hard enforcement. Medium effort. |
| 6 | **Deploy capability gate** | ❌ NOT DONE | Write operations have no permission checking. Medium effort. |
| 7 | **Promote lane=NULL episodes** | NEW | 1239 Episodic nodes have lane=NULL (batch-ingested). Consider bulk-promoting to canonical or running auto-promote sweep. |

---

## 5. FILE REFERENCE

| File | Lines | Location | Purpose |
|------|-------|----------|---------|
| hub-bridge server.js | 1,882 | /opt/seed-vault/memory_v1/hub_bridge/app/server.js | API gateway, chat routing, system prompt, fire-and-forget ingestion |
| karma server.py | 2,651 | /opt/seed-vault/memory_v1/karma-core/server.py | FastAPI, graph ops, /ingest-episode endpoint |
| consciousness.py | 601 | /opt/seed-vault/memory_v1/karma-core/consciousness.py | 60s OBSERVE loop + auto-promote every 10 cycles |
| auto_promote.py | 219 | /opt/seed-vault/memory_v1/karma-core/auto_promote.py | Candidate promotion (threshold=0.80, min_corr=1) |
| compose.yml | — | /opt/seed-vault/memory_v1/compose/compose.yml | karma-server + vault stack |
| compose.hub.yml | — | /opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml | hub-bridge stack |
| memory.jsonl | 3,847 | /opt/seed-vault/memory_v1/ledger/memory.jsonl | Main memory ledger |
| consciousness.jsonl | 284 | /opt/seed-vault/memory_v1/ledger/consciousness.jsonl | Consciousness loop output (active, growing) |
| collab.jsonl | — | /opt/seed-vault/memory_v1/ledger/collab.jsonl | Proposals for human review |
| candidates.jsonl | 10 | /opt/seed-vault/memory_v1/ledger/candidates.jsonl | Candidate facts (all promoted) |
| identity.json | — | /home/neo/karma-sade/identity.json | Identity spine v2.1.0 (read by containers) |
| invariants.json | — | /home/neo/karma-sade/invariants.json | Hard rules |
| direction.md | — | /home/neo/karma-sade/direction.md | Mission/roadmap |

---

**END OF BUILD PLAN v7**
