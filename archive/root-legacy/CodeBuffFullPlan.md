# Karma SADE Cross-Component Integrity Audit & Remediation Plan

## Audit Summary

**Audited Sources:** `hub-bridge/server.js`, `vault-api/server.js`, `karma-core/server.py`, `karma-core/consciousness.py`, `karma-core/router.py`, `karma-core/config.py`

**Severity Scale:** CRITICAL / HIGH / MEDIUM / LOW

---

## Findings

### AREA 1 — Hub-Bridge (ESM) ↔ Vault-API (CJS) Serialization & Module-Boundary Failures

| ID | Finding | Severity |
|----|---------|----------|
| 1.1 | `vaultPost()` routes all writes through external URL (`VAULT_BASE_URL` = `https://vault.arknexus.net`) instead of Docker internal network (`VAULT_INTERNAL_URL` = `http://api:8080`). Creates split-brain risk when proxy is degraded. | HIGH |
| 1.2 | `acquireLock()` in vault-api uses synchronous busy-wait spin lock (`while(Date.now() < end){}`) that blocks the entire Node.js event loop for up to 2s. | HIGH |
| 1.3 | karma-core writes to `memory.jsonl` directly in `log_to_ledger()` and `_distillation_cycle()` WITHOUT vault-api's `.lock` file mechanism. Concurrent appends can produce corrupted JSONL lines. | HIGH |
| 1.4 | `buildVaultRecord()` passes Arrays and Dates through as `content` (latent AJV 422 — no current caller triggers it). | MEDIUM |
| 1.5 | Hub-bridge returns `ok: true` on 207 when vault write fails, but spend state is already committed. Budget over-counts; ledger has gaps. | MEDIUM |
| 1.6 | Inconsistent `protocol_version` across code paths: `"fp.v1"`, `"v1"`, `"memory_v0.1"`. | LOW |

### AREA 2 — Consciousness Loop Race Conditions with FalkorDB Write-Primitive

| ID | Finding | Severity |
|----|---------|----------|
| 2.1 | `_decide()` and `_act()` reference keys (`new_entities`, `new_relationships`, `active_sessions`) that `_observe()` never provides. Also compares `list > 0` (TypeError). **Every active cycle crashes silently.** Consciousness loop is completely non-functional. | **CRITICAL** |
| 2.2 | `_observe()` compares Unix epoch float against `localdatetime()` in FalkorDB — type mismatch makes all direct-write episodes invisible to consciousness. | HIGH |
| 2.3 | Synchronous FalkorDB/LLM calls in asyncio context block the FastAPI event loop. | HIGH |
| 2.4 | `_distillation_cycle()` writes to ledger without lock, concurrent with vault-api. | MEDIUM |
| 2.5 | Fire-and-forget distillation tasks with no backpressure (currently disabled). | LOW |

### AREA 3 — Memory Integrity Gate: Candidate-to-Canonical Promotion Corruption

| ID | Finding | Severity |
|----|---------|----------|
| 3.1 | `promote_candidates_endpoint()` has non-atomic read-modify-write on `candidates.jsonl`. New candidates appended between read and rewrite are **permanently lost**. | **CRITICAL** |
| 3.2 | `/write-primitive` accepts `lane="canonical"` from callers, bypassing the entire Memory Integrity Gate and Colby's approval. | HIGH |
| 3.3 | `_check_contradiction()` extracts max 5 tokens, checks only 5 hardcoded phrase patterns. Covers <1% of semantic conflicts. | HIGH |
| 3.4 | Promotion marks `promoted=True` without verifying FalkorDB SET matched any rows. Silent promotion failures. | MEDIUM |
| 3.5 | No file locking on `candidates.jsonl` for concurrent appends. | MEDIUM |
| 3.6 | Distillation writes directly to ledger bypassing schema validation, lock, and gate pipeline. | MEDIUM |
| 3.7 | No optimistic concurrency control on promotion SET query. | LOW |

---

## Remediation Plan

### CRITICAL — Fix Immediately

#### [2.1] Fix consciousness.py `_observe()`/`_decide()`/`_act()` key mismatches

- `_observe()` must return all keys that `_decide()` and `_act()` expect: `new_entities`, `new_relationships`, `active_sessions` (query from FalkorDB graph stats delta)
- `_decide()` must compare `observations["episode_count"]` (int) instead of `observations["new_episodes"] > 0` (list vs int TypeError)
- `_act()` must use the same corrected keys consistently
- After fix: verify consciousness metrics show `active_cycles > 0` and `errors` stops incrementing

#### [3.1] Make `promote_candidates_endpoint()` atomic

- Use a file lock (`candidates.jsonl.lock` via `fcntl.flock` or equivalent) around the full read-modify-write cycle
- `_append_candidate()` must acquire the same lock before appending
- Alternative approach: write to `.tmp` file, then `os.replace()` for atomic swap
- After fix: test concurrent `/write-primitive` + `/promote-candidates` to verify no data loss

### HIGH — Fix Next

#### [1.1] Route `vaultPost()` through `VAULT_INTERNAL_URL`

- Change `vaultPost()` to use `VAULT_INTERNAL_URL` (`http://api:8080`) instead of `VAULT_BASE_URL` (`https://vault.arknexus.net`), matching `fetchCheckpointLatestFromVault()`

#### [1.2] Replace `acquireLock()` busy-wait with async-safe locking

- Replace synchronous spin lock in vault-api with `proper-lockfile`, `async-lock`, or at minimum a non-blocking retry with `setTimeout` instead of `while(Date.now() < end){}`

#### [1.3] Karma-core must use vault-api's lock (or write via vault-api HTTP)

- Either: (a) `log_to_ledger()` and `_distillation_cycle()` POST to vault-api `/v1/memory` instead of direct file write, or (b) implement the same `.lock` file protocol that vault-api uses

#### [2.2] Fix `_observe()` timestamp type mismatch

- Store `last_cycle_time` as ISO datetime string and use `datetime()` comparison in the Cypher query, or convert `localdatetime` to epoch in the query

#### [2.3] Wrap synchronous FalkorDB/LLM calls in `asyncio.to_thread()`

- All `redis.execute_command()` and `router.complete()` calls in consciousness.py must run via `await asyncio.to_thread(...)` to avoid blocking the event loop

#### [3.2] Enforce allowed lanes in `/write-primitive`

- Whitelist `lane` to `{"candidate", "raw"}` only
- Reject or ignore `lane="canonical"` from external callers
- Distillation can use an internal code path

#### [3.3] Improve contradiction detection

- At minimum, use embedding-based similarity (via existing OpenAI client) on candidate content against recent canonical episodes
- Flag conflicts above a cosine similarity threshold
- Quick-win: expand token extraction and pattern matching to cover entity-value pairs more broadly

### MEDIUM — Fix Soon

#### [1.4] Guard `buildVaultRecord()` against non-plain-object content

- Add `!Array.isArray(content) && !(content instanceof Date)` check; wrap non-objects in `{ value: ... }`

#### [1.5] Move spend state commit after vault write success

- Only call `saveSpendState()` after confirming `vaultPost()` returned 201

#### [2.4] Distillation ledger writes must go through vault-api

- Same fix as 1.3 — POST to `/v1/memory` instead of direct file append

#### [3.4] Verify FalkorDB SET matched rows before marking promoted

- Check graph query result stats for rows affected; only set `entry["promoted"] = True` if > 0 rows matched

#### [3.5] Add file locking to `_append_candidate()`

- Acquire lock on `candidates.jsonl.lock` before appending (same lock as 3.1)

#### [3.6] Distillation writes should go through vault-api with proper ID generation

- Use vault-api's `/v1/memory` endpoint which handles `nanoid` IDs and AJV validation

### LOW — Fix When Convenient

#### [1.6] Standardize `protocol_version`

- Pick one value (e.g. `"v0.1"`) and use consistently across `buildVaultRecord()`, `/v1/chatlog`, and PROMOTE

#### [2.5] Add semaphore to distillation episode ingestion

- If `_ingest_episode` is re-enabled, limit concurrency with `asyncio.Semaphore(2)`

#### [3.7] Add optimistic concurrency on promotion SET

- Add `WHERE e.lane = 'candidate'` to the MATCH clause so already-promoted or conflict episodes aren't silently overwritten

---

## Notes

- Fixes to vault-api (1.2) require restarting the Docker container after deployment
- Fixes 1.3, 2.4, and 3.6 can all be unified by establishing a rule: **only vault-api writes to `memory.jsonl`** — all other services POST to `/v1/memory`
- Fix 2.1 is the highest-impact single change: it will bring the consciousness loop from non-functional to operational
- Fixes 3.1 + 3.5 share the same lock; implement the lock utility once and reuse
- Testing: After fixing 2.1, verify consciousness metrics show `active_cycles > 0` and `errors` stops incrementing. After 3.1, test concurrent `/write-primitive` + `/promote-candidates`

## Relevant Files

| File | Findings |
|------|----------|
| `hub-bridge/server.js` | 1.1, 1.4, 1.5, 1.6 |
| `vault-api/server.js` | 1.2, 1.3, 1.6 |
| `karma-core/consciousness.py` | 2.1, 2.2, 2.3, 2.4, 2.5 |
| `karma-core/server.py` | 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 1.3 |
| `karma-core/config.py` | Lock path constants |
| `karma-core/router.py` | Reference for sync call patterns (2.3) |
