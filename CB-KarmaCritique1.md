# Karma SADE — Cross-Component Critique & Refined Implementation Roadmap

## Executive Self-Critique

The original risk report correctly identified 18 real findings across three subsystems. However, **the proposed remediation plan itself introduces new failure modes** that, in some cases, are worse than the bugs it fixes. This critique evaluates the remediation through three lenses — Stability, Performance, Cost — and produces a revised roadmap that prioritizes *safe, cheap, high-impact* changes first.

**Key verdict:** 8 of 18 findings are fixable in under 10 lines each. The original plan over-engineers several fixes (particularly 2.1 and 3.1) and under-estimates Docker networking constraints. The revised roadmap consolidates 18 individual fixes into **5 batched edit passes** and eliminates the most dangerous proposed changes.

---

## I. Stability Critique — Where Proposed Fixes Introduce Silent Failures

### S1. Fix [1.1] / [1.3]: Docker `network_mode: host` Makes Internal DNS Resolution Impossible

**Original proposal:** Route `vaultPost()` and karma-core writes through `VAULT_INTERNAL_URL` (`http://api:8080`).

**Problem:** `karma-server` runs with `network_mode: host` (confirmed in both `docker-compose.karma.yml` and `compose.karma-server.yml`). Host-networked containers **cannot resolve Docker DNS names** like `api` — they use the host's DNS resolver. This means:

- **hub-bridge** (bridge-networked on `anr-vault-net`) → `http://api:8080` **works** ✓
- **karma-server** (host-networked) → `http://api:8080` **fails silently** ✗ — `ENOTFOUND api`

If fix [1.3] makes karma-core POST to `http://api:8080`, every `log_to_ledger()` and distillation write fails. The consciousness loop logs errors but continues — creating **silent ledger gaps**.

**Revised approach:**
- For **hub-bridge**: `VAULT_INTERNAL_URL = http://api:8080` (already works)
- For **karma-server**: `VAULT_WRITE_URL = http://127.0.0.1:<host-mapped-vault-port>` (must use loopback)
- Add a **startup connectivity preflight** — fail loudly if unreachable

### S2. Fix [1.2]: `proper-lockfile` in vault-api Risks Permanent Write Outage on Crash

**Original proposal:** Replace busy-wait `acquireLock()` with `proper-lockfile`.

**Problem:** If vault-api crashes mid-lock (OOM kill, container restart), a stale `.lock` file blocks **all subsequent writes indefinitely**. vault-api appears healthy (`/healthz` 200) but writes are dead. Additionally, `proper-lockfile` is ESM-only in recent versions — vault-api is CJS. Importing it via `require()` crashes with `ERR_REQUIRE_ESM` at boot.

**Revised approach:** vault-api is a **single instance**. Use an **in-process async mutex** (Promise queue or `async-mutex` package). No lockfiles, no stale locks, no ESM/CJS footgun. Kernel cleans up automatically on crash.

### S3. Volume Mount Mismatch Risk

Even with HTTP-mediated writes, karma-core still *reads* `memory.jsonl`. If containers mount different volumes to the same host path → split-brain. Certain filesystem stacking (overlayfs, NFS) makes advisory locks unreliable across containers.

**Revised approach:** Mount ledger **`rw` in vault-api only**, **`ro` everywhere else**. Add periodic ledger integrity metrics.

### S4. Container Restart During [1.2] Deployment

In-flight requests get `ECONNRESET`. hub-bridge returns 207 "ok" for failed vault writes — client sees success, ledger has a gap.

**Revised approach:** Add graceful shutdown to vault-api. Require hub-bridge callers to retry on 5xx with idempotency.

---

## II. Performance Critique — Latency Spikes from Proposed Locks

### P1. `fcntl.flock()` Around Promote Is the Highest Performance Risk

**Original proposal:** Wrap `promote_candidates_endpoint()` in `fcntl.flock()`.

**Problem:** Promote holds the lock for the full read→iterate→FalkorDB-query-per-candidate→rewrite cycle:
- Parse thousands of JSONL lines: **100–800ms**
- Per-candidate FalkorDB SET (20 approvals × 10-30ms): **200–600ms**
- Full file rewrite: **10–100ms**
- **Total lock hold time: 1–4 seconds typical, 5–10s+ worst case**

During this window, every `/write-primitive` call's `_append_candidate()` blocks on the same lock. Since `fcntl.flock()` is a **blocking syscall**, it blocks the **entire FastAPI event loop** — freezing all endpoints (WebSocket `/chat`, `/ask`, `/status`, `/health`).

**Revised approach — Append-Only Design:**
- **Never rewrite** `candidates.jsonl`. It's append-only.
- Record promotions in a separate `promotions.jsonl` (also append-only).
- Pending list = candidates − promotions (computed at read time).
- Lock hold time drops from **seconds to <5ms** (single append syscall).
- Periodic compaction prevents unbounded growth.

### P2. Adding 3 New FalkorDB Queries Per Consciousness Cycle

**Original proposal (fix 2.1):** Add entity-delta and relationship-delta Cypher queries to `_observe()`.

**Problem:** FalkorDB is **single-threaded**. Each new COUNT query takes 50–200ms. Adding 2 queries means **100–400ms of extra head-of-line blocking** every 60 seconds. User-facing queries that land in this window see **+100–400ms p95/p99 spikes**.

**Revised approach:** `_decide()` and `_act()` don't *need* entity/relationship deltas — they crash because they reference keys that don't exist, not because they need the data. **Just update `_decide()` and `_act()` to use the keys `_observe()` already provides** (`episode_count`, `new_episodes`, `time_delta_seconds`). Zero new queries. Same outcome: consciousness loop stops crashing. Entity awareness can be added later using `GRAPH.INFO` (sub-ms metadata) instead of COUNT scans.

### P3. `asyncio.to_thread()` — Net Win, Needs Executor Control

Moving sync calls to threads is a **net positive** (removes 0.35–5.6s event loop stalls per cycle). Risk: default `ThreadPoolExecutor` has ~5-8 workers on a small VPS. Long LLM calls (200ms–5s) can starve other work.

**Revised approach:** Use a **dedicated executor** with bounded concurrency for consciousness work. Or better: `redis.asyncio.Redis` for true-async FalkorDB calls (no threads needed).

### P4. O(n) Candidates Growth

With rewrite-on-promote: 1K lines = fine, 10K = noticeable, 100K = unusable. The append-only design from P1 eliminates this — writes are O(1), compaction runs offline.

---

## III. Cost Critique — Token-Efficient Implementation

### Most Over-Engineered Fixes

| Fix | Original Estimate | Minimal Estimate | Savings |
|-----|:---:|:---:|:---:|
| 2.1 (consciousness keys) | ~1500 tokens (3 new queries) | ~800 tokens (update _decide/_act only) | 47% |
| 3.1 (atomic promote) | ~800 tokens (fcntl + rewrite) | ~600 tokens (append-only design) | 25% |
| K2-R2 (polling endpoint) | ~3000 tokens (new endpoint + client) | ~1500 tokens (poll existing endpoints) | 50% |
| 3.3 (contradiction detection) | ~1500 tokens (embeddings) | ~500 tokens (expand token patterns) | 67% |

### Impact/Cost Ranking (All 18 Findings + K2)

| Rank | ID | Impact | Cost (tokens) | Ratio | One-liner? |
|:---:|:---|:---:|---:|---:|:---:|
| 1 | 1.1 | 4 | ~100 | **40.0** | ✓ |
| 2 | 3.2 | 4 | ~200 | **20.0** | ✓ |
| 3 | 3.5 | 3 | ~150 | **20.0** | ✓ |
| 4 | 3.7 | 2 | ~100 | **20.0** | ✓ |
| 5 | 3.4 | 3 | ~200 | **15.0** | ✓ |
| 6 | 2.2 | 4 | ~300 | **13.3** | — |
| 7 | 1.4 | 2 | ~150 | **13.3** | ✓ |
| 8 | 1.5 | 3 | ~300 | **10.0** | — |
| 9 | 1.3 | 4 | ~500 | **8.0** | — |
| 10 | 2.3 | 3 | ~400 | **7.5** | — |
| 11 | 1.6 | 1 | ~150 | **6.7** | ✓ |
| 12 | **2.1** | **5** | **~800** | **6.25** | — |
| 13 | **3.1** | **5** | **~600** | **8.3** | — |
| 14 | 2.4 | 3 | ~500 | **6.0** | — |
| 15 | 1.2 | 4 | ~800 | **5.0** | — |
| 16 | 2.5 | 1 | ~200 | **5.0** | ✓ |
| 17 | 3.3 | 3 | ~500 | **6.0** | — |
| 18 | 3.6 | 2 | ~0 | **∞** | ✓ (free with 2.4) |
| 19 | K2-R3 | 2 | ~800 | **2.5** | — |
| 20 | K2-R2 | 3 | ~1500 | **2.0** | — |

**8 of 18 findings are fixable in <10 lines each.**

### Combinable Edit Passes

| Pass | File | Fixes | Tokens |
|:---:|------|-------|---:|
| 1 | hub-bridge/server.js | 1.1, 1.4, 1.5, 1.6 | ~500 |
| 2 | karma-core/server.py | 3.1, 3.2, 3.4, 3.5, 3.7, 1.3 | ~1200 |
| 3 | karma-core/consciousness.py | 2.1, 2.2, 2.3, 2.4, 2.5 | ~1200 |
| 4 | vault-api/server.js | 1.2 | ~800 |
| 5 | k2-worker/karma-k2-sync.py | K2-R2, K2-R3 | ~1500 |
| | **Total** | | **~5200** |

Down from ~12,000+ if implemented individually.

---

## IV. Refined Implementation Roadmap

Ordered by: **stability first** (least likely to introduce silent failures), then performance, then cost.

### Pass 1 — Hub-Bridge Quick Wins (Safest, Highest Ratio)
**File:** `hub-bridge/server.js` | **~500 tokens** | **Risk: Minimal**

| Fix | Change | Lines |
|-----|--------|:---:|
| 1.1 | `vaultPost()` uses `VAULT_INTERNAL_URL` instead of `VAULT_BASE_URL` (hub-bridge is on bridge network, `api` resolves correctly) | 1 |
| 1.4 | Guard `buildVaultRecord()`: reject Array/Date content | 3 |
| 1.5 | Move `saveSpendState()` after vault write confirmation | 5 |
| 1.6 | Standardize `protocol_version` to `"v0.1"` | 3 |

**Validation:** `/v1/chat` → vault write returns 201, spend state matches.

### Pass 2 — Karma-Core Data Integrity (Critical Bugs, Append-Only)
**File:** `karma-core/server.py` | **~1200 tokens** | **Risk: Low-Medium**

| Fix | Change | Lines |
|-----|--------|:---:|
| 3.1 | **Append-only candidates**: never rewrite. Add `promotions.jsonl`. Pending = candidates − promotions. | ~40 |
| 3.2 | Whitelist `lane` to `{"candidate", "raw"}` only | 3 |
| 3.4 | Verify FalkorDB SET matched rows before marking promoted | 5 |
| 3.5 | Lightweight advisory lock on append (<5ms hold) | 8 |
| 3.7 | Add `WHERE e.lane = 'candidate'` to promotion Cypher | 1 |
| 1.3 | `log_to_ledger()` uses `http://127.0.0.1:<vault-port>` (NOT Docker DNS) | 15 |

**Why second:** Fixes both CRITICALs. Append-only eliminates the seconds-long lock contention. `127.0.0.1` avoids Docker DNS trap.

**Validation:** Concurrent `/write-primitive` + `/promote-candidates` — verify zero candidate loss. Verify `/write-primitive` with `lane=canonical` returns 400.

### Pass 3 — Consciousness Loop (The Blocker)
**File:** `karma-core/consciousness.py` | **~1200 tokens** | **Risk: Low**

| Fix | Change | Lines |
|-----|--------|:---:|
| 2.1 | Update `_decide()` to use `episode_count` (int). Update `_act()` to use existing keys. **No new FalkorDB queries.** | 20 |
| 2.2 | `last_cycle_time` as ISO string + `localdatetime()` Cypher comparison | 10 |
| 2.3 | Wrap sync calls in `asyncio.to_thread()` with dedicated executor | 15 |
| 2.4 | Distillation writes via vault-api HTTP (`127.0.0.1`) | 10 |
| 2.5 | `asyncio.Semaphore(2)` on distillation ingest | 3 |

**Why third (not first despite CRITICAL):** Consciousness has been broken since Feb 16 — not an active regression. Fixing data integrity first (Pass 2) ensures consciousness writes don't corrupt the ledger when it starts working.

**Validation:** After deploy, check `/status` — `active_cycles` should increment, `errors` should stop climbing. Verify event loop isn't blocked: `/health` responds in <50ms during consciousness cycle.

### Pass 4 — Vault-API Event Loop Safety
**File:** `vault-api/server.js` | **~800 tokens** | **Risk: Medium (requires restart)**

| Fix | Change | Lines |
|-----|--------|:---:|
| 1.2 | Replace `acquireLock()` with **in-process async mutex** + graceful shutdown | ~40 |

**Why fourth:** Only fix requiring container restart. Do it last so the system is otherwise stable. In-process mutex (not lockfile) avoids stale-lock and ESM/CJS risks.

**Validation:** Load test vault-api under concurrent writes — verify no event loop blocking. Kill -9 vault-api, restart — verify writes resume immediately (no stale lock).

### Pass 5 — K2 Bridge (Deferred, Budget-Dependent)
**Files:** `k2-worker/karma-k2-sync.py`, `karma-core/config.py` | **~1500 tokens**

| Requirement | Change |
|-----|--------|
| K2-R2 (simplified) | Poll **existing** endpoints (`/status`, `/candidates/list`, `/raw-context`, `/v1/checkpoint/latest`) — no new server-side endpoint needed |
| K2-R3 | Write observations via `POST /write-primitive` with `lane=raw`, `source=k2-observer`, rate-limited 1/cycle |

**Why last:** K2 is additive infrastructure with no impact on existing stability. Simplified polling eliminates the most expensive item (~3000 → ~1500 tokens) by reusing existing endpoints.

---

## V. Summary

| Metric | Original Plan | Revised Plan |
|--------|:---:|:---:|
| Total edit passes | 18+ individual | **5 batched** |
| Estimated tokens | ~12,000+ | **~5,200** |
| New FalkorDB queries added | 5 | **0** |
| New endpoints | 1 (`/v1/graph/sync`) | **0** |
| Stale-lock risk | Yes (proper-lockfile) | **None** (in-process mutex) |
| Max lock contention | 1–10s (fcntl around promote) | **<5ms** (append-only) |
| Docker DNS failure risk | High (karma-server can't resolve `api`) | **None** (uses `127.0.0.1`) |
| Consciousness queries/cycle | 3 (150–600ms blocking) | **1** (50–200ms, threaded) |
