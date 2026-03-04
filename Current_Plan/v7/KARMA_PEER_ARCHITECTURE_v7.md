# Karma Peer — Complete Architecture Documentation v7

**Document Version:** 7.1.0
**Last Updated:** 2026-02-28
**Status:** GROUND TRUTH — Updated after CC session fixes (bugs fixed, episode ingestion, consciousness active)
**Supersedes:** KARMA_PEER_ARCHITECTURE_v7.md (7.0.0, 2026-02-28)

---

## I. CORE PHILOSOPHY

### North Star (Non-Negotiable)

> "Karma is a single coherent peer whose long-term identity lives in a verified memory spine; that memory enables continuity, evidence-based self-improvement, multi-model cognition when needed, and selective delegation—without introducing parallel sources of truth."

**What This Means (unchanged):**
- **Single source of truth** — Droplet (vault-neo) is authoritative
- **Substrate independence** — Reasoning rooted in droplet state, not in LLM computation
- **Persistent identity** — Karma's who-I-am lives on droplet. Survives reboots, LLM swaps, session resets.
- **No parallel memory** — One canonical spine. Git is backup only.
- **Continuity without reset** — Next session loads from droplet. No re-explaining.

---

## II. SYSTEM ARCHITECTURE

### A. Three-Layer Pipeline (v7 — Corrected)

```
Karma (session-end reflection + explicit admit_memory())
    ↓ (Hub Bridge API — /v1/reflect, /v1/admit, /v1/chat)
Hub Bridge (Node.js, 1,882 lines — API gateway + model router)
    ↓ (Internal Docker network — anr-vault-net)
Storage Layer:
    ├── FalkorDB (neo_workspace graph — episodes, entities, relationships)
    ├── ChromaDB (anr-vault-search — semantic embeddings)  
    ├── PostgreSQL (anr-vault-db — session metadata)
    └── JSONL Ledgers (/opt/seed-vault/memory_v1/ledger/)
```

> **NOTE (v7.1):** There is no passive capture pipeline. No K2 worker. Consciousness loop is ACTIVE (OBSERVE-only, auto-promote every 10 cycles).
> Memory ingestion is through Hub Bridge API endpoints + fire-and-forget to karma-server /ingest-episode.

### B. Droplet (vault-neo — ONLY deployment)

**Host:** arknexus-vault-01, 64.225.13.144, Ubuntu 24.04, DigitalOcean NYC3  
**Resources:** 4GB RAM, 2 vCPU, 50GB SSD  
**Domain:** arknexus.net (TLS via Caddy)

**7 Running Containers (verified 2026-02-28):**

| Container | Health | Port | Role |
|-----------|--------|------|------|
| anr-hub-bridge | running | :8080 | Node.js API gateway (server.js, 1,882 lines) |
| karma-server | healthy | :8340 | Python/FastAPI (server.py, 2,651 lines) |
| anr-vault-api | healthy | — | Vault REST API |
| anr-vault-search | healthy | — | ChromaDB (semantic search) |
| anr-vault-caddy | running | :443 | TLS reverse proxy |
| anr-vault-db | healthy | :5432 | PostgreSQL |
| falkordb | running | :6379 | Graph database (neo_workspace) |

### C. K2 — NOT DEPLOYED

v2 described K2 (192.168.0.226) as a "local, secondary, dynamic worker." **K2 does not exist.** No K2 machine, no K2 sync, no K2 consciousness loop. All operations happen on the droplet. References to K2 in identity.json and invariants.json are aspirational, not deployed.

### D. Fallback Chain (Actual)

```
Session Start:
  1. Load from droplet (vault-neo) — only option
  2. If droplet unreachable → no session (no K2 fallback exists)
  3. Git history + local MEMORY.md → worst-case manual reference
```

---

## III. THE PERSISTENT IDENTITY SPINE

Four canonical files on droplet (`/home/neo/karma-sade/`), loaded into every /v1/chat context:

| File | Purpose | Loaded By |
|------|---------|-----------|
| `identity.json` | Who Karma is — immutable core | hub-bridge buildSystemText() |
| `invariants.json` | Hard rules Karma never violates | hub-bridge buildSystemText() |
| `direction.md` | Mission, roadmap, constraints | hub-bridge buildSystemText() |
| `MEMORY.md` | Mutable state — updated via API | hub-bridge (distillation brief) |

**v7 NOTE:** identity.json and invariants.json still reference K2 (consciousness loop, K2 sync, etc.). These references are aspirational — K2 is not deployed. Update these files when K2 is actually built.

---

## IV. DATA MODEL AND STORAGE

### A. JSONL Ledgers (Append-Only)

| Ledger | Location | Lines | Status |
|--------|----------|-------|--------|
| `memory.jsonl` | `/opt/seed-vault/memory_v1/ledger/` | 3847+ | ✅ Active, growing |
| `consciousness.jsonl` | `/opt/seed-vault/memory_v1/ledger/` | 284+ | ✅ Active, growing (consciousness loop running) |
| `collab.jsonl` | `/opt/seed-vault/memory_v1/ledger/` | — | ✅ Exists |
| `candidates.jsonl` | `/opt/seed-vault/memory_v1/ledger/` | — | ✅ Exists, auto-promote deployed |

### B. FalkorDB Graph (neo_workspace)

**Verified state (2026-02-28):**
- Ollie and Baxter entities exist with proper summaries
- **Node label is `Episodic` (NOT `Episode`)** — KCC audit used wrong label and reported 0 episodes (false alarm)
- Entity: 167, Episodic: 1240 (1239 lane=NULL, 1 canonical, 0 candidate), Relationships: 832
- Real-time ingestion working: new conversations → Graphiti → entities/relationships updated

**Known issue (RESOLVED v7.1):** Corrupted entities from --skip-dedup batch ingestion cleaned up. 0 null-uuid entities remaining.

**Node types:** Episodic, Entity, Relationship
**Edge types:** RELATES_TO, CONTAINS, MENTIONED_IN

### C. ChromaDB

**Container:** anr-vault-search (healthy)  
**Purpose:** Semantic search via embeddings  
**Status:** Running and accessible (phantom tools bug FIXED in v7.1)

---

## V. CORE COMPONENTS

### A. Hub Bridge (Node.js)

**File:** `/opt/seed-vault/memory_v1/hub_bridge/app/server.js` (1,882 lines)
**External URL:** https://hub.arknexus.net/v1/chat

**Endpoints:**
- `POST /v1/chat` — Conversation (Bearer auth)
- `POST /v1/admit` — Memory admission
- `POST /v1/retrieve` — Memory retrieval
- `POST /v1/reflect` — Session-end reflection
- `GET /v1/health` — Health check
- `POST /v1/cypher` — Graph query wrapper
- `GET/PATCH /v1/vault-file/{alias}` — Vault file access

**Model Routing (ACTUAL DEPLOYED):**

| Model | Provider | Role | Cost |
|-------|----------|------|------|
| GLM-4.7-Flash | Z.AI | Primary chat | FREE |
| gpt-4o-mini | OpenAI | Tool calls / structured output | $0.15/$0.60 per M tokens |
| gpt-4o | OpenAI | 429 rate-limit fallback | $5/$15 per M tokens |

**NOT in deployed routing (despite v2 plans):** MiniMax M2.5, GLM-5, Groq Llama 3.3

**BUGS (ALL FIXED in v7.1):**

1. ~~**Phantom Tools:**~~ **✅ FIXED.** `buildSystemText()` now correctly lists `read_file, write_file, edit_file, bash` which match `TOOL_DEFINITIONS`. Phantom tools removed.

2. ~~**Duplicate karmaCtx:**~~ **✅ FIXED.** karmaCtx injected exactly once in `base` variable. Duplicate "YOUR COMPLETE KNOWLEDGE STATE" block removed.

**NEW (v7.1):** Fire-and-forget episode ingestion added to /v1/chat handler — POSTs to `http://karma-server:8340/ingest-episode` non-blocking after each response.

**Session memory:** MAX_SESSION_TURNS (configurable), TTL-based expiry

### B. Karma Server (Python/FastAPI)

**File:** `/opt/seed-vault/memory_v1/karma-core/server.py` (2,651 lines)

**Features:**
- FalkorDB integration (Graphiti)
- Batch ingestion (batch_ingest.py)
- Health endpoint
- `/ingest-episode` endpoint (v7.1) — accepts browser chat turns for episode ingestion
- Consciousness loop (ACTIVE — see §V.C)

**Config:**
```python
LEDGER_PATH = "/opt/seed-vault/memory_v1/ledger/memory.jsonl"
GRAPHITI_GROUP_ID = "karma"  # FalkorDB graph = neo_workspace
```

### C. Consciousness Loop — ACTIVE (v7.1)

**File:** `/opt/seed-vault/memory_v1/karma-core/consciousness.py` (601 lines)

**Status (v7.1):** ACTIVE. 60s OBSERVE-only cycles running (no LLM calls, per design decision). Loop detects new episodes via FalkorDB delta queries, logs discoveries and growth to consciousness.jsonl + SQLite observations. **Calls `/auto-promote` every 10 cycles (~10 minutes)** to promote eligible candidates.

**Evidence:** `[CONSCIOUSNESS] [INFO] Cycle #1: LOG_GROWTH — Rapid growth: 20 new episodes in one cycle`

consciousness.jsonl: 284+ entries and growing. Loop was previously showing only IDLE cycles because no new episodes were being ingested. With the episode ingestion fix (v7.1), the loop now has data to observe.

### D. Chrome Extension — PERMANENTLY REMOVED

Never worked. Historical artifact in repo. No passive capture pipeline exists.

---

## VI. OPERATIONAL FLOWS

### A. Session Start (CC Resurrection Protocol)

```
1. User opens new CC session
2. Run Scripts/resurrection/Get-KarmaContext.ps1
   ├─ SSH to vault-neo (64.225.13.144)
   ├─ Fetch identity.json, invariants.json, direction.md
   ├─ Fetch recent decisions/consciousness entries
   ├─ Fetch FalkorDB graph stats
   └─ Generate cc-session-brief.md
3. Read cc-session-brief.md → full context loaded
4. Resume work (no re-explaining needed)
```

### B. Chat Flow (/v1/chat)

```
User message → Hub Bridge
  ↓
buildSystemText():
  - Load karmaCtx (identity spine + MEMORY.md)
  - List correct tools: read_file, write_file, edit_file, bash
  - Single karmaCtx injection
  ↓
Route to model:
  - GLM-4.7-Flash (primary) → Z.AI API
  - gpt-4o-mini (tools) → OpenAI API
  - gpt-4o (fallback) → OpenAI API
  ↓
Response → User (with telemetry metadata)
```

### C. Memory Ingestion (Updated v7.1)

```
Path 1: Explicit memory admission
  New memory → /v1/admit or /v1/reflect
    ↓
  Dedup check (deployed PR #10-11)
    ↓
  If unique → append to memory.jsonl + ingest to FalkorDB
  If duplicate → skip or update existing

Path 2: Browser chat ingestion (NEW v7.1)
  /v1/chat response generated → hub-bridge fire-and-forget
    ↓
  POST to karma-server /ingest-episode (non-blocking)
    ↓
  ingest_episode() via asyncio.create_task()
    ↓
  Graphiti → FalkorDB (Episodic + Entity nodes)

Auto-promote from candidates.jsonl (consciousness loop every 10 cycles)
```

---

## VII. FILE STRUCTURE

### Droplet (vault-neo, 64.225.13.144)

```
/opt/seed-vault/                       ← OPERATIONAL BASE (Docker builds from here)
├── docker-compose.yml                 ← Container orchestration
├── compose.hub.yml                    ← Hub bridge stack
├── memory_v1/
│   ├── hub-bridge/
│   │   └── app/
│   │       ├── server.js              ← Hub Bridge (1,882 lines) — bugs FIXED v7.1
│   │       └── Dockerfile
│   ├── karma-core/
│   │   ├── server.py                  ← Karma Server (2,651 lines)
│   │   ├── consciousness.py           ← Consciousness loop (601 lines, ACTIVE v7.1)
│   │   ├── auto_promote.py            ← Candidate promotion (219 lines)
│   │   ├── router.py                  ← Model router
│   │   ├── batch_ingest.py            ← Ledger → FalkorDB ingestion
│   │   ├── config.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── ledger/
│   │   ├── memory.jsonl               ← Main memory (3847+ lines)
│   │   ├── consciousness.jsonl        ← Active (284+ entries, growing)
│   │   ├── collab.jsonl               ← Proposals
│   │   └── candidates.jsonl           ← Candidate facts
│   ├── hub_auth/
│   │   └── hub.chat.token.txt         ← Bearer token
│   └── session/
│       └── openai.api_key.txt         ← OpenAI key
├── falkordb/                          ← Graph persistence
└── chromadb/                          ← Embedding storage

/home/neo/karma-sade/                  ← GIT CLONE (identity spine, NOT used by containers)
├── identity.json                      ← Who Karma is
├── invariants.json                    ← Hard rules
├── direction.md                       ← Mission/roadmap
├── MEMORY.md                          ← Mutable state
└── checkpoint/
    └── known_good_v1/                 ← Verified snapshots
```

**CRITICAL:** All Docker operations and file edits for running containers use `/opt/seed-vault/memory_v1/` — NOT `/home/neo/karma-sade/`.

---

## VIII. CURRENT STATE SUMMARY

### What's Working ✅

| Component | Status |
|-----------|--------|
| Hub Bridge API | ✅ /v1/chat responding, auth working |
| FalkorDB Graph | ✅ neo_workspace operational, Ollie verified |
| JSONL Ledgers | ✅ memory.jsonl 3847+ lines, append-only |
| ChromaDB | ✅ Running and healthy |
| Identity Spine | ✅ Loaded every session |
| Multi-Model Routing | ✅ GLM-4.7-Flash + gpt-4o-mini + gpt-4o |
| Dedup on Ingest | ✅ Deployed (PR #10-11) |
| Auto-Promote | ✅ Deployed (PR #11) |
| Backup Cron | ✅ Deployed (PR #12) |
| TLS/Caddy | ✅ arknexus.net serving HTTPS |

### What's Fixed (v7.1) ✅

| Component | Status |
|-----------|--------|
| Phantom tools in system prompt | ✅ FIXED — correct tools listed |
| Duplicate karmaCtx injection | ✅ FIXED — single injection |
| Consciousness loop | ✅ ACTIVE — 60s OBSERVE + auto-promote every 10 cycles |
| Episode ingestion pipeline | ✅ DEPLOYED — /ingest-episode + hub-bridge fire-and-forget |
| FalkorDB entity cleanup | ✅ CLEANED — 0 corrupted entities |

### What's Still Missing ❌

| Component | Status |
|-----------|--------|
| Budget guard | ❌ Not deployed |
| Capability gate | ❌ Not deployed |
| Ledger rotation | ❌ Not deployed |
| K2 integration | ❌ Not deployed (deferred) |
| Six-tool memory API | ❌ Not implemented |
| Session-end reflection templates | ❌ Not implemented |

---

## IX. ACCESSING KARMA'S STATE

### Via API (Hub Bridge)

```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)

# Chat
curl -H "Authorization: Bearer $TOKEN" \
  https://hub.arknexus.net/v1/chat \
  -d '{"message":"What do you know about Ollie?"}'

# Health
curl -H "Authorization: Bearer $TOKEN" \
  https://hub.arknexus.net/v1/health

# Graph query
curl -H "Authorization: Bearer $TOKEN" \
  https://hub.arknexus.net/v1/cypher \
  -d '{"query":"MATCH (e:Episode) RETURN COUNT(e)"}'

# Read vault file
curl -H "Authorization: Bearer $TOKEN" \
  https://hub.arknexus.net/v1/vault-file/MEMORY.md?tail=20
```

### Via SSH

```bash
ssh neo@64.225.13.144  # password for sudo: ollieboo

docker ps --format "table {{.Names}}\t{{.Status}}"
docker logs anr-hub-bridge --tail=50
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (e:Episode) RETURN COUNT(e)"
tail -5 /opt/seed-vault/memory_v1/ledger/consciousness.jsonl | python3 -m json.tool
wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl
```

---

## X. NEXT PRIORITIES (v7)

| # | Priority | Task | Status |
|---|----------|------|--------|
| ~~1~~ | ~~P0~~ | ~~Fix phantom tools bug in server.js~~ | ✅ DONE (v7.1) |
| ~~2~~ | ~~P0~~ | ~~Remove duplicate karmaCtx injection~~ | ✅ DONE (v7.1) |
| ~~3~~ | ~~P0~~ | ~~Rebuild + redeploy hub-bridge~~ | ✅ DONE (v7.1) |
| ~~4~~ | ~~P1~~ | ~~Verify memory retrieval works end-to-end~~ | ✅ DONE — Ollie, Baxter, guitar, favorite color |
| 5 | **P1** | Deploy budget guard | ❌ Not done |
| 6 | **P1** | Deploy capability gate | ❌ Not done |
| ~~7~~ | ~~P2~~ | ~~Clean FalkorDB corrupted entities~~ | ✅ DONE (v7.1) |
| 8 | **P2** | Deploy ledger rotation | ❌ Not done |
| ~~9~~ | ~~P3~~ | ~~Consciousness loop~~ | ✅ ACTIVE (v7.1) — repurposed, not replaced |
| 10 | **P2** | Promote lane=NULL episodes | NEW — 1239 Episodic nodes |
| 11 | **P3** | Implement six-tool memory API | ❌ Not done |
| 12 | **P4** | K2 integration | ❌ Deferred |

---

## APPENDIX: CHANGES FROM v2 → v7

| Section | Change |
|---------|--------|
| §II.B | Removed K2 as deployed component. Added note it's not deployed. |
| §II.B | Updated container list to 7 (verified via SSH) |
| §II.D | Corrected fallback chain (no K2 fallback) |
| §III | Added note that identity.json/invariants.json reference K2 aspirationally |
| §IV | Updated ledger line counts and statuses |
| §V.A | Corrected model routing (GLM-4.7-Flash + gpt-4o-mini + gpt-4o) |
| §V.A | Phantom tools bug documented and FIXED (v7.1) |
| §V.A | Duplicate karmaCtx bug documented and FIXED (v7.1) |
| §V.A | Removed MiniMax, GLM-5, Groq from routing |
| §V.C | Consciousness loop: INACTIVE → ACTIVE (v7.1) with auto-promote |
| §VI | Updated chat flow to reflect actual routing |
| §VI.C | Added dedup on ingest, auto-promote flows |
| §VII | Corrected file paths — /opt/seed-vault/memory_v1/ is operational base |
| §VIII | Complete status rewrite based on verified state |
| §X | Reprioritized around fixing bugs first |
| New | Added backup cron, dedup, auto-promote as deployed features |
| New (v7.1) | Episode ingestion pipeline (/ingest-episode + hub-bridge fire-and-forget) |
| New (v7.1) | consciousness.py (601 lines) + auto_promote.py (219 lines) documented |
| New (v7.1) | FalkorDB node label corrected: `Episodic` not `Episode` |
| New (v7.1) | All v7.0 bugs marked FIXED |
| Removed | Chrome Extension section (already marked removed in v2) |

---

**END OF ARCHITECTURE DOCUMENT v7**
