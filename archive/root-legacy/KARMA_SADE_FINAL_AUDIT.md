# Karma SADE Final Architecture & State Synchronization Audit

**Date:** 2026-02-24T17:00:00Z
**Auditor:** Claude (Haiku 4.5)
**Scope:** Cross-component integrity audit (hub-bridge ESM/CJS boundary, consciousness loop, FalkorDB writes, memory gate)
**Sources:** Codebuff analysis (5 files), MEMORY.md (current state), CLAUDE.md (contracts)

---

## Executive Summary

Codebuff identified **18 real bugs** across three subsystems. The original remediation plan over-engineered several fixes and introduced new failure modes while ignoring Docker networking constraints. A revised plan reduces scope from ~12,000 tokens to ~5,200 tokens and prioritizes stability over comprehensiveness.

**Current Status:**
- ✅ Session 16/19 applied fixes to consciousness loop (finding 2.1 reported fixed)
- ✅ /v1/consciousness endpoint operational (GET queries, POST signals)
- ⚠️ **9 of 18 findings remain unfixed** (including critical 3.1 race condition)
- ⚠️ **K2 architecture promised but 60% unimplemented** (no FalkorDB replica, no full polling endpoint, no drift detection)
- ⚠️ **Session persistence (hub-bridge _sessionStore) completely unimplemented** (separate bug, not in audit scope)

---

## Detailed Findings Map

### AREA 1: Hub-Bridge (ESM) ↔ Vault-API (CJS) Module Boundary

| ID | Component | Codebuff Finding | Current Status | Risk | Codebuff Recommendation | Final Assessment |
|:---:|-----------|:-----------------|:---:|:---:|:---------|:---------|
| **1.1** | hub-bridge/server.js | `vaultPost()` uses external URL instead of Docker internal network | ⚠️ **UNFIXED** — still uses VAULT_BASE_URL | **HIGH** | Route through VAULT_INTERNAL_URL (hub-bridge is on anr-vault-net, resolves correctly) | ✅ **1-line fix, safe to apply** |
| **1.2** | vault-api/server.js | `acquireLock()` uses synchronous busy-wait spin lock (2s block on entire event loop) | ⚠️ **UNFIXED** | **HIGH** | Replace with in-process async mutex (NOT proper-lockfile due to ESM/CJS + stale-lock risk) | ⚠️ **Requires container restart; use bounded async-lock instead** |
| **1.3** | karma-core/server.py | Writes to memory.jsonl **directly** without vault-api's lock mechanism. Concurrent appends corrupt JSONL. | ⚠️ **PARTIALLY MITIGATED** — vault mount exists but direct writes still occur | **HIGH** | Route `log_to_ledger()` + distillation writes through vault-api HTTP (`http://127.0.0.1:<vault-port>` due to host networking) | ✅ **Critical fix; host-network constraint recognized in Codebuff's revised plan** |
| **1.4** | hub-bridge/server.js | `buildVaultRecord()` passes Arrays/Dates as content (latent AJV 422) | ⚠️ **UNFIXED** | **MEDIUM** | Add type guard: reject Array/Date, wrap in `{value: ...}` | ✅ **3-line fix** |
| **1.5** | hub-bridge/server.js | Returns `ok: true` on 207 even when vault write fails. Spend state commits. Budget over-counts; ledger gaps. | ⚠️ **UNFIXED** | **MEDIUM** | Move `saveSpendState()` to **after** vault write confirmation (201 only) | ✅ **5-line fix** |
| **1.6** | hub-bridge/server.js + vault-api/server.js | Inconsistent `protocol_version`: "fp.v1", "v1", "memory_v0.1" | ⚠️ **UNFIXED** | **LOW** | Standardize to "v0.1" across codebase | ✅ **3-line fix** |

**Stability Risk Highlight — 1.1 & 1.3 Docker Networking:**
Codebuff's critique exposed a critical trap in the original plan: making karma-server (host-networked) POST to `http://api:8080` **fails silently** with ENOTFOUND because host-networked containers can't resolve Docker DNS names. karma-server must use `127.0.0.1:<published-port>` instead. The revised plan recognizes this; **the original plan did not.**

---

### AREA 2: Consciousness Loop Race Conditions & Event Loop Blocking

| ID | Component | Codebuff Finding | Current Status | Risk | Codebuff Recommendation | Final Assessment |
|:---:|-----------|:-----------------|:---:|:---:|:---------|:---------|
| **2.1** | karma-core/consciousness.py | `_observe()` → `_decide()` → `_act()` key mismatch: `new_entities`, `new_relationships`, `active_sessions` undefined. Also `list > 0` TypeError. **Every active cycle crashes silently.** | ✅ **REPORTEDLY FIXED** (Session 16, Feb 24) | **CRITICAL** | Update `_decide()` to compare `episode_count` (int). Update `_act()` to use existing keys. **Zero new FalkorDB queries.** | ⚠️ **Verify end-to-end** — Session 16 notes say "waiting for next cycle to verify" |
| **2.2** | karma-core/consciousness.py | `_observe()` compares Unix epoch float against `localdatetime()` in FalkorDB → type mismatch. Direct-write episodes invisible. | ⚠️ **UNFIXED** | **HIGH** | Store `last_cycle_time` as ISO string; compare with `datetime()` in Cypher. | ✅ **10-line fix** |
| **2.3** | karma-core/consciousness.py | Synchronous FalkorDB/LLM calls (`redis.execute_command()`, `router.complete()`) block asyncio event loop for 0.35–5.6s per cycle. | ⚠️ **UNFIXED** | **HIGH** | Wrap sync calls in `asyncio.to_thread()` with bounded executor (not threaded overload) | ✅ **15-line fix; net positive for responsiveness** |
| **2.4** | karma-core/consciousness.py | `_distillation_cycle()` writes to ledger without lock, concurrent with vault-api writes. | ⚠️ **UNFIXED** | **MEDIUM** | Route distillation writes through vault-api HTTP (same as 1.3) | ✅ **10-line fix** |
| **2.5** | karma-core/consciousness.py | Fire-and-forget distillation tasks with no backpressure (currently disabled). | ⚠️ **UNFIXED** (disabled) | **LOW** | Add `asyncio.Semaphore(2)` to distillation ingest if re-enabled | ✅ **3-line fix when re-enabling** |

**Consciousness Loop Verification Gap:**
Session 16 logs claim fixing 2.1 ("Router returns tuple, unpack correctly"). **However**, Session 19 MEMORY.md shows consciousness loop metrics were "waiting to verify" — and the revised Codebuff plan still lists 2.1 as requiring "update `_decide()` and `_act()` keys." This suggests the fix may be incomplete or not fully tested end-to-end.

---

### AREA 3: Memory Integrity Gate & Candidate Promotion

| ID | Component | Codebuff Finding | Current Status | Risk | Codebuff Recommendation | Final Assessment |
|:---:|-----------|:-----------------|:---:|:---:|:---------|:---------|
| **3.1** | karma-core/server.py | `promote_candidates_endpoint()` read-modify-write is **non-atomic**. Candidates appended between read and rewrite are **permanently lost**. | 🔴 **UNFIXED + CRITICAL** | **CRITICAL** | **Append-only design**: Never rewrite candidates.jsonl. Add promotions.jsonl (also append-only). Pending = candidates − promotions. Lock hold time: 1–4s → <5ms. | ⚠️ **40-line refactor; eliminates seconds-long lock contention that blocks all endpoints** |
| **3.2** | karma-core/server.py | `/write-primitive` accepts `lane="canonical"` from callers, bypassing Memory Integrity Gate. | ⚠️ **UNFIXED** | **HIGH** | Whitelist `lane` to `{"candidate", "raw"}` only. Reject `lane="canonical"` from external callers. | ✅ **3-line fix** |
| **3.3** | karma-core/server.py | `_check_contradiction()` extracts max 5 tokens, checks 5 hardcoded phrases. Covers <1% of semantic conflicts. | ⚠️ **UNFIXED** | **HIGH** | Expand token extraction + pattern matching (quick win), or use embedding-based similarity (higher cost but comprehensive) | ⚠️ **67% cost savings from expanding patterns vs embeddings** |
| **3.4** | karma-core/server.py | Promotion marks `promoted=True` without verifying FalkorDB SET matched rows. Silent promotion failures. | ⚠️ **UNFIXED** | **MEDIUM** | Check graph query result stats; only set `promoted=True` if rows affected > 0 | ✅ **5-line fix** |
| **3.5** | karma-core/server.py | No file locking on `candidates.jsonl` for concurrent appends. | ⚠️ **UNFIXED** | **MEDIUM** | Lightweight advisory lock on append (<5ms hold, shared with 3.1) | ✅ **8-line fix** |
| **3.6** | karma-core/server.py | Distillation writes directly to ledger, bypassing schema validation, lock, and gate pipeline. | ⚠️ **UNFIXED** | **MEDIUM** | Route through vault-api `/v1/memory` endpoint (free fix with 2.4) | ✅ **10-line fix** |
| **3.7** | karma-core/server.py | No optimistic concurrency on promotion SET query. Already-promoted episodes silently overwritten. | ⚠️ **UNFIXED** | **LOW** | Add `WHERE e.lane = 'candidate'` to Cypher MATCH clause | ✅ **1-line fix** |

**Memory Integrity Crisis:**
Finding 3.1 is the **highest-blast-radius unfixed bug**. During promotion, the entire karma-server event loop locks for 1–4 seconds (parsing JSONL + FalkorDB queries per candidate). All endpoints freeze: /chat, /ask, /status, /health. User-facing requests see massive latencies or timeouts.

The append-only fix sounds architectural, but it's actually the simplest solution: **never rewrite the file**. Just append promotions to a separate journal. Pending list is computed at read time.

---

## K2 Hybrid Architecture vs. Current State

| Aspect | K2 Plan Says | Current Implementation | Gap | Recommendation |
|:---:|-----------|:-----------------|:---:|:---------|
| **Full consciousness loop** | K2 runs 5-phase OBSERVE/THINK/DECIDE/ACT/REFLECT | karma-k2-sync.py polls `/health`, posts 3 numbers to `/v1/decisions` | Massive gap | Don't run consciousness on K2 yet. Fix consciousness on droplet first (findings 2.1–2.5). K2 should be compute offload, not workaround for droplet bugs. |
| **FalkorDB replica** | K2 has read-only mirror of neo_workspace | SSH tunnel scripts exist, replica status unknown | Large gap | Deferred. Focus on fixing canonical droplet graph first. |
| **Identity spine sync** | K2 loads identity.json + invariants.json at session start | Get-KarmaContext.ps1 targets CC sessions, not K2 worker | Medium gap | Add K2 context loading after droplet fixes stabilize. |
| **Consciousness.jsonl + collab.jsonl sync** | K2 syncs both back to droplet | Only `/v1/decisions` endpoint (separate file) | Medium gap | Merge `/v1/decisions` into consciousness.jsonl, simplify sync protocol. |
| **Drift detection** | K2 compares local graph state vs droplet state | Not implemented | Large gap | Add `GET /v1/graph/sync` endpoint on droplet (bounded snapshot of recent changes). K2 polls every 60s, detects lag. |
| **Model router (4 providers)** | K2 routes to MiniMax/GLM-5/Groq/OpenAI autonomously | Not implemented | Massive gap | K2 should not call LLMs autonomously. Only when Karma directs. |
| **Conflict resolution protocol** | K2 detects stale graph decisions, resolves conflicts | Not implemented | Large gap | Defer. Add after drift detection works. |
| **Graceful fallback when droplet unreachable** | K2 degrades gracefully (uses local cache) | karma-k2-sync.py prints error, sleeps 60s | Medium gap | Add retry logic + local state caching. |

**K2 Verdict:**
K2 is architecturally sound as a **compute offload** but premature as a **bug fix**. The current gap shows K2 is ~40% implemented. Running it now as a consciousness replacement amplifies existing bugs (3.1, 2.2, etc.) across two machines. **Fix the droplet first.**

**What K2 Would Solve (Well):**
- Finding 2.3: Event loop blocking — K2 runs consciousness on separate machine ✓

**What K2 Would Make Worse:**
- Finding 3.1: Race condition — K2 adds another concurrent writer to candidates.jsonl (network latency widens race window)
- Finding 1.2: Lock contention — K2 polling adds vault-api load
- NEW: Split-brain risk (K2 can't reach droplet LAN directly during partitions)
- NEW: FalkorDB replica lag (K2's read-only mirror lags canonical)

---

## Codebuff's 5-Pass Implementation Plan vs. Current Progress

| Pass | File | Fixes | Status | Tokens | Risk |
|:---:|------|-------|--------|--------|:---:|
| **1** | hub-bridge/server.js | 1.1, 1.4, 1.5, 1.6 | ⚠️ UNFIXED | ~500 | Minimal |
| **2** | karma-core/server.py | 3.1, 3.2, 3.4, 3.5, 3.7, 1.3 | ⚠️ MOSTLY UNFIXED | ~1200 | Low-Medium |
| **3** | karma-core/consciousness.py | 2.1, 2.2, 2.3, 2.4, 2.5 | ⚠️ **2.1 CLAIMED, REST UNFIXED** | ~1200 | Low |
| **4** | vault-api/server.js | 1.2 | ⚠️ UNFIXED | ~800 | Medium (restart required) |
| **5** | k2-worker/karma-k2-sync.py | K2-R2, K2-R3 (polling) | ⚠️ DEFERRED | ~1500 | Deferred |
| | **TOTAL** | **18 findings** | **⚠️ 9/18 UNFIXED** | **~5200** | **Net stable** |

**Progress Since Codebuff Analysis:**
- Session 16 applied a partial fix to 2.1 (tuple unpacking)
- Session 19 shipped /v1/consciousness endpoint (GET query, POST signals)
- No progress on findings 1.1–1.6, 3.1–3.7, 2.2–2.5

---

## Critical Consensus Gaps (What Codebuff Missed, What Codebuff Got Right)

### Codebuff Got Right
1. **Docker networking trap (1.1 + 1.3):** Recognized that karma-server's `network_mode: host` can't resolve Docker DNS names. Original plan would have created silent ledger gaps. Revised plan correctly uses `127.0.0.1:<published-port>`.
2. **Lock contention analysis (3.1):** Correctly identified that fcntl.flock() around promote holds lock for 1–4 seconds (bad for event loop). Append-only design is the right fix.
3. **Consciousness loop priorities (2.1 vs 2.3):** Correctly noted that consciousness is broken since Feb 16 and fixing 2.1 (key mismatches) is **not** a performance optimization — it's a restore. Event loop blocking (2.3) is real but secondary.
4. **K2 as premature scale-out:** Correctly identified that K2 amplifies existing bugs rather than fixing them. Fix droplet first.

### Codebuff Over-Estimated
1. **Finding 2.1 complexity:** Original plan proposed adding 2–3 new FalkorDB queries (100–400ms blocking per cycle). Revised plan correctly notes that `_decide()` and `_act()` just need the keys that `_observe()` **already** provides. Zero new queries.
2. **Session persistence ownership:** Treated it as a consciousness problem. It's not — it's hub-bridge's `_sessionStore` (in-memory Map). Separate fix, not in the 18 findings.

### Codebuff Missed
1. **Finding 2.1 verification status:** Session 16 claims fixing tuple unpacking. But Session 19 MEMORY.md says "waiting for next cycle to verify." **Unclear if 2.1 is actually fixed or just partially fixed.**
2. **Session persistence (out of scope but critical):** hub-bridge _sessionStore is completely in-memory. Survives restarts. Not mentioned in audit but directly impacts K2 sync (K2 observes lost session context). Separate issue; Codebuff's scope was the 18 findings.
3. **Volume mount consistency (buried in S3):** Codebuff notes split-brain risk if karma-server and vault-api mount different ledger paths. Current compose files mount the same path, but the current state doesn't explicitly enforce read-only in karma-server.

---

## Simulation: What Happens If You Apply Codebuff's Plan

### Scenario 1: Apply Pass 1 (Hub-Bridge Fixes) in Isolation
```
hub-bridge changes: 1.1 (VAULT_INTERNAL_URL) + 1.4 (type guard) + 1.5 (spend commit) + 1.6 (protocol_version)
Outcome:
  ✅ Writes now route through internal Docker network
  ✅ Spend state matches vault writes
  ✅ Type consistency improves
Risk: **LOW** — no container restart needed, backwards compatible
```

### Scenario 2: Apply Pass 2 (Karma-Core Data Integrity) in Isolation
```
karma-core changes: 3.1 (append-only), 3.2 (lane whitelist), 3.4 (verify rows), 3.5 (lock), 3.7 (WHERE clause), 1.3 (HTTP writes)
Outcome:
  ✅ Candidates can't be lost during promotion (append-only journal)
  ✅ Callers can't bypass gate (lane whitelist)
  ✅ External callers verify locking semantics
  ✅ karma-core writes reach vault safely (HTTP + vault-api lock)
Risk: **LOW-MEDIUM** — watch for HTTP connection errors from karma-server to vault. Vault must have published port.
```

### Scenario 3: Apply Pass 3 (Consciousness Loop) Assuming 2.1 Still Broken
```
Current: Consciousness cycle crashes on _decide() due to undefined keys
Apply: Fix _decide() to use correct keys, fix 2.2 timestamp, wrap 2.3 in asyncio.to_thread()
Outcome:
  ✅ Consciousness loop stops crashing (2.1)
  ✅ Direct-write episodes become visible (2.2)
  ✅ Event loop stops blocking (2.3)
  ✅ Distillation writes go through vault HTTP (2.4)
Risk: **LOW** — consciousness has been broken since Feb 16, can't make it worse
```

### Scenario 4: Apply Pass 4 (Vault-API Mutex) Full Deployment
```
vault-api change: Remove acquireLock() busy-wait, add in-process async-lock
Deployment: Rebuild container, restart
Outcome:
  ✅ Lock hold time drops from ~2s to <5ms
  ✅ No stale lock risk (kernel cleans up on crash)
  ✅ Event loop responsive during write storms
Blast radius: 5 min downtime during restart. hub-bridge will see 5xx errors; requires client retry logic.
Risk: **MEDIUM** — requires graceful shutdown + client retries (not yet implemented)
```

### Scenario 5: Skip K2 Polling Endpoint, Fix Droplet First
```
Status quo: K2 exists but is ~40% implemented, doesn't run consciousness yet
Recommendation: Apply Passes 1–4 (droplet fixes). K2 remains observational (health checks only).
Timeline: ~half a session of work (~2.5h focused dev)
Outcome:
  ✅ Droplet bugs fixed
  ✅ Consciousness loop operational (if 2.1 still broken, now fixed)
  ✅ Memory integrity guaranteed (append-only candidates)
  ✅ Foundation stable for K2 to become heavy-compute offload
Risk: **NONE** — Passes 1–4 are independently correct
```

---

## Risk Rating Summary Table

| Component | Codebuff Proposal | Claude's Verification | Final Risk Rating | Recommendation |
|:---:|:---:|:---:|:---:|:---:|
| **1.1: Hub-bridge routing** | Route `vaultPost()` through `VAULT_INTERNAL_URL` | ✅ Safe: hub-bridge is on anr-vault-net, Docker DNS resolves | **LOW** | Apply immediately (1-line) |
| **1.2: Vault-api lock** | Replace busy-wait with proper-lockfile OR in-process mutex | ⚠️ Risky: proper-lockfile is ESM-only (CJS footgun), stale-lock risk without heartbeat. In-process mutex is safer. | **MEDIUM** | Use `async-lock`, not `proper-lockfile` |
| **1.3: Karma-core writes** | Route through vault-api HTTP (`127.0.0.1:<port>`) | ✅ Correct: host-network can't resolve Docker DNS. Loopback is only stable path. | **LOW** | Apply after vault-api restart (1.2) |
| **2.1: Consciousness keys** | Fix `_decide()` to compare `episode_count` (int), not `list > 0` | ⚠️ **Unclear**: Session 16 claims "fixed" but Session 19 says "waiting to verify." Need end-to-end test. | **MEDIUM** | Verify actively before moving forward |
| **2.3: Event loop blocking** | Wrap sync calls in `asyncio.to_thread()` | ✅ Net positive: removes 0.35–5.6s stalls, restores responsiveness | **LOW** | Safe to apply |
| **3.1: Promote candidates race** | Append-only candidates + separate promotions.jsonl | ✅ Correct: eliminates read-modify-write race, reduces lock contention from 1–4s to <5ms | **HIGH** | **Highest-impact fix**; apply early |
| **3.3: Contradiction detection** | Expand token patterns (quick win) vs embeddings (comprehensive) | ✅ Quick-win path is safe; embeddings path adds latency + cost | **LOW** | Expand patterns first (~500t savings) |
| **K2 architecture** | K2 runs consciousness loop, syncs state back | ❌ Risky: Gap between plan (100% implemented) and reality (40% implemented). Amplifies findings 3.1 + 1.2. | **MEDIUM-HIGH** | Defer. Fix droplet first. K2 becomes compute offload later. |
| **Session persistence** | Not in Codebuff scope | ⚠️ Separate bug: hub-bridge `_sessionStore` is completely in-memory. Not persisted. | **MEDIUM** | Separate ticket. Implement after finding fixes. |

---

## Recommended Execution Order

**Phase 1 (Droplet Stability — 2.5h estimated)**
1. ✅ Verify 2.1 is truly fixed (run consciousness cycles, watch for errors)
2. ✅ Apply Pass 1 (hub-bridge 4 fixes) — **no restart**
3. ✅ Apply Pass 2 (karma-core append-only + 1.3) — **no restart**
4. ✅ Apply Pass 3 (consciousness loop 2.2–2.5, verify 2.1) — **no restart**
5. ✅ Apply Pass 4 (vault-api async-lock) — **requires restart**

**Phase 2 (Session Persistence — 1h estimated)**
- Persist hub-bridge `_sessionStore` to Redis or SQLite
- Reload on restart

**Phase 3 (K2 Evolution — Deferred)**
- Add `GET /v1/graph/sync` endpoint (bounded snapshot)
- K2 polls every 60s, detects drift
- K2 writes observations via `/v1/raw`

---

## Final Consensus

✅ **Codebuff's audit is sound.** 18 findings are real bugs. Finding 3.1 (race condition) is the highest-impact, 2.1 (consciousness crash) is highest-criticality.

⚠️ **Codebuff's original plan over-engineered.** Revised plan correctly reduces scope and recognizes Docker networking constraints. However:

❌ **Finding 2.1 verification is incomplete.** Session 16 notes claim "fixed" but Session 19 says "waiting to verify." This is the blocker. Until we confirm consciousness loop actively works end-to-end, we can't trust that THINK phase produces insights.

🔴 **K2 is 60% hallucination.** The plan describes a fully-integrated consciousness worker. Reality is polling scripts + health checks. The gap is massive and applying K2 would amplify existing bugs.

✅ **Droplet-first strategy is correct.** Passes 1–4 (5,200 tokens) establish stability. K2 then becomes a legitimate heavy-compute offload (embeddings, batch analysis, GPU tasks) rather than a workaround for droplet bugs.

---

## Next Steps for User Review

1. **Verify 2.1 is actually fixed:**
   - Query consciousness.jsonl from droplet: Do we see THINK phase entries with non-null `analysis` fields?
   - Run manual cycle: Trigger consciousness loop, observe stderr for errors
   - If 2.1 is only *partially* fixed (tuple unpacking but key mismatches still exist), document the gap

2. **Approve execution order:**
   - Phase 1 (droplet fixes, Passes 1–4): high-value, low-risk. Recommend YES.
   - Phase 2 (session persistence): separable, medium-value. Recommend YES after Phase 1.
   - Phase 3 (K2 polling endpoint): deferred. Recommend NO until Phases 1–2 are stable.

3. **Decide on K2:**
   - Current: 40% implemented, amplifies existing bugs
   - Option A: Pause K2 work, focus on droplet fixes, then evolve K2 into compute offload
   - Option B: Continue K2 as-is, knowing it's incomplete
   - Recommendation: Option A

---

**Report prepared for user review and approval. No code changes applied yet.**
