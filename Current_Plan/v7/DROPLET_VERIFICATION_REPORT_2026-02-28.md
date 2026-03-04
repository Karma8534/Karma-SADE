# DROPLET VERIFICATION REPORT
**Date:** 2026-02-28
**Verified by:** KCC (Claude Code)
**Droplet:** 64.225.13.144 (vault-neo)

---

## CONTAINERS
- [x] **7 containers running:**
  - anr-hub-bridge (Up 54 minutes)
  - karma-server (Up 19 hours, healthy)
  - anr-vault-api (Up 19 hours, healthy)
  - anr-vault-caddy (Up 44 hours)
  - anr-vault-db (Up 44 hours, healthy)
  - anr-vault-search (Up 44 hours, healthy)
  - falkordb (Up 3 days)

**Status:** ✅ All expected containers present and running

---

## BUGS CONFIRMED

### Bug 1: Phantom Tools Bug (CONFIRMED)
- **Location:** `/opt/seed-vault/memory_v1/hub_bridge/app/server.js` line 376
- **Issue:** buildSystemText() advertises tools that don't exist in TOOL_DEFINITIONS
- **Text:** `"Tools: get_vault_file(alias) | graph_query(cypher) — use for questions about your memory/graph."`
- **Actual TOOL_DEFINITIONS (line 725-850):**
  - read_file
  - write_file
  - edit_file
  - bash
- **NOT found:** get_vault_file, graph_query
- **Impact:** LLM may attempt to call non-existent tools, leading to confusion/errors

### Bug 2: Duplicate karmaCtx Injection (CONFIRMED)
- **Location:** `/opt/seed-vault/memory_v1/hub_bridge/app/server.js`
- **Issue:** karmaCtx appears in TWO locations, causing redundant context injection
- **First injection (line 368-369):** `const base = karmaCtx` (used in initial system prompt)
- **Second injection (line 396-397):** Injected AGAIN as `=== YOUR COMPLETE KNOWLEDGE STATE (INJECTED) ===`
- **Impact:** Redundant context, potentially confusing LLM, wasted tokens

---

## CODE

### server.js
- [x] **Line count:** 1872 lines (expected ~1872) ✅ **MATCHES**
- **Location:** `/opt/seed-vault/memory_v1/hub_bridge/app/server.js`
- **Container path:** `/app/server.js`

### server.py
- [x] **Line count:** 2629 lines (expected ~2629) ✅ **MATCHES**
- **Location:** `/opt/seed-vault/memory_v1/karma-core/server.py`

---

## FALKORDB (neo_workspace graph)

### Graph State
- [ ] **Episodes: 0** (expected >= 1488) ❌ **MAJOR DISCREPANCY**
- [ ] **Entities: 162** (expected >= 3401) ❌ **MAJOR DISCREPANCY** (5% of expected)
- [ ] **Relationships: 791** (expected >= 5847) ❌ **MAJOR DISCREPANCY** (13% of expected)

### Entity Status
- [x] **Ollie entity: FOUND** (Pet type, multiple entries) ✅
- [ ] **Corrupted entities (null uuid): 1** ⚠️ **NEEDS CLEANUP**

**Critical Finding:** The FalkorDB graph is nearly empty despite memory.jsonl having 3821 lines.
This indicates either:
1. Batch ingest never ran successfully
2. Graph was cleared after ingestion
3. Different graph name is being queried
4. Graph data migration issue

---

## LEDGERS

### memory.jsonl
- [x] **Line count:** 3821 lines (expected >= 3449) ✅ **EXCEEDS EXPECTED**
- **Location:** `/opt/seed-vault/memory_v1/ledger/memory.jsonl`
- **Status:** Healthy, contains expected data

### consciousness.jsonl
- [ ] **Line count:** 2907 lines (expected ~109) ❌ **MAJOR DISCREPANCY** (27x larger)
- **Location:** `/opt/seed-vault/memory_v1/ledger/consciousness.jsonl`
- **Last entries:**
  ```
  {"timestamp": "2026-02-28T18:45:11.814429+00:00", "type": "CYCLE_REFLECTION", "cycle": 1153, "is_idle": true, "action": "IDLE"}
  {"timestamp": "2026-02-28T18:46:11.826095+00:00", "type": "CYCLE_REFLECTION", "cycle": 1154, "is_idle": true, "action": "IDLE"}
  {"timestamp": "2026-02-28T18:47:11.837388+00:00", "type": "CYCLE_REFLECTION", "cycle": 1155, "is_idle": true, "action": "IDLE"}
  ```

**Finding:** Consciousness loop is actively running IDLE cycles (currently at cycle 1155).
The v7 plan expected ~109 lines and "old entries only," but the loop is clearly active.

### collab.jsonl
- [x] **Status:** EXISTS ✅
- **Size:** 1,145,022 bytes
- **Last modified:** Feb 27 17:46

### candidates.jsonl
- [x] **Status:** EXISTS ✅
- **Size:** 3,517 bytes
- **Last modified:** Feb 21 13:38

---

## IDENTITY SPINE

### Files Status
- [x] **identity.json: EXISTS** ✅
- [x] **invariants.json: EXISTS** ✅
- [x] **direction.md: EXISTS** ✅

### identity.json Details
- [ ] **Version:** 2.1.0 (expected 2.0.0) ⚠️ **VERSION DRIFT**
- [x] **Name:** Karma ✅
- **Location:** `/home/neo/karma-sade/identity.json`
- **Last modified:** Feb 26 20:32

**Finding:** Identity version is 2.1.0, not 2.0.0 as expected in v7 plan.

---

## MODEL ROUTING

### Configuration Verified
- [x] **GLM models: FOUND** ✅
  - Z.ai client configured (lines 706-712, 876-886, 952-964)
  - GLM models route via Z.ai endpoint (when ZAI_API_KEY available)
  - Fallback to OpenAI (gpt-4o) on 429 errors
  - GLM-4.7-Flash is the model mentioned in routing

- [x] **gpt-4o-mini: FOUND** ✅
  - Default fallback model (line 883)
  - Used when model validation fails

- [x] **gpt-4o fallback: FOUND** ✅
  - Z.ai 429 fallback (line 971)
  - Used when Z.ai returns rate limit errors

- [x] **MiniMax M2.5: NOT FOUND** ✅ (no MiniMax routing active)
- [x] **GLM-5: NOT FOUND** ✅ (only GLM models via Z.ai, not GLM-5)
- [x] **Groq: NOT FOUND** ✅ (no Groq routing active)

**Code Evidence:**
```javascript
// Line 706-712: Z.ai client setup
// Line 879: const isZaiModel = actualModel.startsWith("glm-");
// Line 880: const providerName = (isZaiModel && zai) ? "zai" : "openai";
// Line 886: const client = (isZaiModel && zai) ? zai : openai;
// Line 964: Fallback to gpt-4o on Z.ai 429
```

---

## CONSCIOUSNESS LOOP

### Status
- [x] **Status: ACTIVE** ✅ (running IDLE cycles)
- [x] **Last entry timestamp:** 2026-02-28T18:47:11+00:00 ✅ (current, within last minute)
- [x] **Current cycle:** 1155

### Activity
- Last 3 cycles are IDLE (no new ledger activity)
- Cycle duration: 1-9ms (very fast, no actual thinking)
- Loop is healthy but not generating new insights

**Finding:** Consciousness loop is active as expected, but the v7 plan expectation of ~109 lines in consciousness.jsonl does not match the actual state (2907 lines, 1155 cycles).

---

## INFRASTRUCTURE

### Backup Configuration
- [x] **Backup cron: CONFIGURED** ✅ (8 jobs in user crontab)

**Cron Jobs:**
```
15 3 * * *   /home/neo/.local/bin/anr_rotate_memory_ledger.sh
25 3 * * *   /opt/seed-vault/memory_v1/resurrection/cron.sh capture
35 3 * * 0   /opt/seed-vault/memory_v1/resurrection/cron.sh prune
*/5 * * * *   /usr/bin/python3 /home/neo/karma-sade/Scripts/gen-cc-brief.py
0 4 * * *     /opt/seed-vault/memory_v1/karma-core/scripts/nightly_backup.sh
*/5 * * * *   /opt/seed-vault/memory_v1/tools/watchdog.sh
0 3 1 * *     /opt/seed-vault/memory_v1/tools/ledger_rotate.sh
0 6 * * 1     /opt/seed-vault/memory_v1/karma-core/reflection_directives.sh
*/30 * * * *  /opt/seed-vault/memory_v1/tools/vault_sync.sh
```

- [x] **Backups directory: EXISTS** ✅
  - Location: `/opt/seed-vault/backups/`
  - Contains: consciousness_archive_20260227.jsonl (1.8MB)
  - Contains: ledger_archive/ directory

- [ ] **Root crontab:** Not configured (no root crontab)

### System Resources
- [x] **RAM:** 2449/3915 MB available ⚠️ ~62% available, ~37% used
  - Used: 1466 MB
  - Cached: 2029 MB
  - Status: Healthy

- [x] **Disk:** 25G/48G used (52%) ✅
  - Available: 23 GB
  - Status: Healthy

### Authentication
- [x] **Bearer token: EXISTS** ✅
  - Location: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt`
  - Size: 65 bytes
  - Permissions: rw-rw-r- (neo:neo)

---

## DISCREPANCIES FROM v7 PLAN

### CRITICAL DISCREPANCIES (P0 - Blockers)

#### 1. FalkorDB Graph State Mismatch
**Expected:** >=1488 episodes, >=3401 entities, >=5847 relationships
**Actual:** 0 episodes, 162 entities, 791 relationships

**Analysis:**
- Graph is 0% of expected episodes, 5% of expected entities, 13% of expected relationships
- Memory.jsonl has 3821 lines (exceeds expected 3449)
- **Possible causes:**
  1. Batch ingest.py never ran successfully
  2. Graph was cleared after ingestion
  3. Wrong graph name being queried (verify `neo_workspace` vs `karma`)
  4. Graph data migration/restore issue
  5. FalkorDB container was recreated without volume mount

**Impact:** Knowledge graph is essentially empty, RAG queries will return no results
**Priority:** P0 - Critical

#### 2. Consciousness Ledger Size Mismatch
**Expected:** ~109 lines (old entries only)
**Actual:** 2907 lines (27x larger than expected)

**Analysis:**
- Consciousness loop is actively running (current cycle 1155)
- Last entries show IDLE cycles with recent timestamps
- v7 plan expected "old entries only" but loop is clearly active
- This may be expected behavior if v7 plan documentation is outdated

**Impact:** None - consciousness loop is working correctly
**Priority:** P0 - Clarification needed (is this expected?)

---

### HIGH PRIORITY DISCREPANCIES (P1 - Important)

#### 3. Phantom Tools Bug
**Location:** `/opt/seed-vault/memory_v1/hub_bridge/app/server.js` line 376

**Issue:** buildSystemText() advertises tools that don't exist in TOOL_DEFINITIONS

**Evidence:**
```javascript
// Line 376 - advertises these tools:
"Tools: get_vault_file(alias) | graph_query(cypher) — use for questions about your memory/graph."

// But TOOL_DEFINITIONS (line 725) only has:
- read_file
- write_file
- edit_file
- bash
```

**Impact:**
- LLM may attempt to call `get_vault_file` or `graph_query`
- Tool call will fail, confusing the LLM
- Wastes tokens and degrades user experience

**Fix:** Change line 376 to advertise only existing tools, or remove tool list from buildSystemText entirely (already in TOOL_DEFINITIONS)

**Priority:** P1

#### 4. Duplicate karmaCtx Injection
**Location:** `/opt/seed-vault/memory_v1/hub_bridge/app/server.js` lines 368-397

**Issue:** Karma context is injected twice in system prompt

**Evidence:**
```javascript
// Line 368-369 - First injection:
const base = karmaCtx
  ? `You are Karma — Colby's thinking partner with persistent memory backed by a knowledge graph.\n\n${karmaCtx}\n\nMemory rules:...`

// Line 396-397 - Second injection:
if (karmaCtx) {
  text += `\n\n=== YOUR COMPLETE KNOWLEDGE STATE (INJECTED) ===\n${karmaCtx}\n=== END KNOWLEDGE STATE ===\n\nYou have your full graph above. Answer questions directly from this context. You are not missing any data.`;
}
```

**Impact:**
- Redundant context in system prompt
- Increases token usage without benefit
- Potentially confuses LLM with duplicate context
- If karmaCtx is large, wastes significant tokens

**Fix:** Remove one of the two injections (keep whichever is intended)

**Priority:** P1

#### 5. Corrupted Entity with Null UUID
**Location:** FalkorDB neo_workspace graph

**Issue:** 1 entity exists with `uuid = NULL`

**Evidence:**
```
MATCH (e:Entity) WHERE e.uuid IS NULL RETURN COUNT(e)
Result: 1
```

**Impact:**
- Queries may fail or return unexpected results
- Cannot track or clean up this entity properly
- May indicate data quality issues

**Fix:**
```cypher
MATCH (e:Entity) WHERE e.uuid IS NULL DELETE e
```

**Priority:** P1

#### 6. Identity Version Drift
**Location:** `/home/neo/karma-sade/identity.json`

**Issue:** identity.json has version 2.1.0 instead of 2.0.0

**Evidence:**
```json
{
  "version": "2.1.0",
  "name": "Karma",
  ...
}
```

**Impact:**
- v7 plan expects version 2.0.0
- May indicate version upgrade not reflected in build plan
- Could cause confusion about which version is deployed

**Fix:** Either update v7 plan to reflect 2.1.0 or verify 2.1.0 is intended

**Priority:** P1

---

### LOW PRIORITY DISCREPANCIES (P2 - Nice to Have)

#### 7. Hub Bridge Path Naming
**Issue:** Directory is named `hub_bridge` (underscore) but v7 plan references `hub-bridge` (hyphen)

**Evidence:**
- Actual path: `/opt/seed-vault/memory_v1/hub_bridge/`
- Expected: `/opt/seed-vault/memory_v1/hub-bridge/`

**Impact:** Documentation mismatch only, no functional issue

**Fix:** Update v7 plan to use correct path name

**Priority:** P2

---

## RECOMMENDED FIXES (Priority Order)

### P0 (Critical - Blockers)

#### Fix 1: Investigate FalkorDB Graph State
**Action Required:** Determine why graph is empty despite memory.jsonl having data

**Steps:**
1. Verify correct graph name is being used:
   ```bash
   docker exec falkordb redis-cli GRAPH.LIST
   ```
2. Check batch_ingest.py execution history:
   ```bash
   grep -r "batch_ingest" /opt/seed-vault/memory_v1/karma-core/logs/
   ```
3. Verify FalkorDB volume mount:
   ```bash
   docker inspect falkordb | grep -A 20 Mounts
   ```
4. Check if graph was recently cleared:
   ```bash
   docker logs falkordb 2>&1 | grep -i "flushall\|clear\|delete"
   ```
5. Re-run batch ingest if needed:
   ```bash
   docker exec karma-server sh -c 'LEDGER_PATH=/opt/seed-vault/memory_v1/ledger/memory.jsonl python3 /app/batch_ingest.py > /tmp/batch.log 2>&1'
   ```

**Expected Outcome:** Graph should have >=1488 episodes, >=3401 entities, >=5847 relationships

---

#### Fix 2: Clarify Consciousness Loop State Expectations
**Action Required:** Determine if active consciousness loop with 1155+ cycles is expected

**Steps:**
1. Review v7 plan documentation for consciousness loop requirements
2. Verify if 2907 lines in consciousness.jsonl is expected
3. Update documentation or stop loop if needed

**Expected Outcome:** Documentation matches actual system state

---

### P1 (High - Important)

#### Fix 3: Remove Phantom Tools from buildSystemText()
**Action Required:** Fix line 376 in server.js

**Steps:**
1. Edit `/opt/seed-vault/memory_v1/hub_bridge/app/server.js`
2. Change line 376 from:
   ```javascript
   "Tools: get_vault_file(alias) | graph_query(cypher) — use for questions about your memory/graph.\n\nGovernance:\n- Colby is the final authority..."
   ```
   To:
   ```javascript
   "Tools: read_file, write_file, edit_file, bash — use for file operations and shell commands.\n\nGovernance:\n- Colby is the final authority..."
   ```
3. Or remove tool list entirely (already in TOOL_DEFINITIONS):
   ```javascript
   "Governance:\n- Colby is the final authority..."
   ```
4. Restart hub-bridge:
   ```bash
   docker restart anr-hub-bridge
   ```

**Expected Outcome:** LLM only attempts to call existing tools

---

#### Fix 4: Remove Duplicate karmaCtx Injection
**Action Required:** Fix buildSystemText() in server.js

**Steps:**
1. Edit `/opt/seed-vault/memory_v1/hub_bridge/app/server.js`
2. Review lines 367-397
3. Remove one of the two karmaCtx injections:
   - Option A: Remove lines 396-397 (keep initial base injection)
   - Option B: Remove karmaCtx from base variable, keep lines 396-397
4. Verify only one injection remains
5. Restart hub-bridge:
   ```bash
   docker restart anr-hub-bridge
   ```

**Expected Outcome:** Single karmaCtx injection, no redundant context

---

#### Fix 5: Clean Up Corrupted Entity
**Action Required:** Remove entity with null uuid from FalkorDB

**Steps:**
```bash
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (e:Entity) WHERE e.uuid IS NULL RETURN e" --compact
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (e:Entity) WHERE e.uuid IS NULL DELETE e"
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (e:Entity) WHERE e.uuid IS NULL RETURN COUNT(e) as remaining"
```

**Expected Outcome:** 0 corrupted entities

---

#### Fix 6: Sync Identity Version
**Action Required:** Update v7 plan or verify version is correct

**Steps:**
1. Review identity.json version history
2. Determine if 2.1.0 is intended
3. Either:
   - Update v7 plan to reflect 2.1.0
   - Or downgrade identity.json to 2.0.0 if 2.1.0 was unintentional

**Expected Outcome:** Documentation matches deployed version

---

### P2 (Low - Nice to Have)

#### Fix 7: Update Path Documentation
**Action Required:** Update v7 plan to use `hub_bridge` instead of `hub-bridge`

**Expected Outcome:** Documentation matches actual file paths

---

## SUMMARY

### Overall Status
- **Containers:** ✅ 7/7 running
- **Code:** ✅ Line counts match expectations
- **Ledgers:** ⚠️ consciousness.jsonl 27x larger than expected
- **FalkorDB:** ❌ CRITICAL - Graph nearly empty (0% episodes, 5% entities)
- **Bugs:** ❌ 2 confirmed bugs (phantom tools, duplicate karmaCtx)
- **Infrastructure:** ✅ Healthy (RAM, disk, backups, cron)

### Critical Issues Requiring Immediate Attention
1. **FalkorDB graph is empty** - RAG functionality broken
2. **Phantom tools bug** - LLM may call non-existent tools
3. **Duplicate karmaCtx** - Wasted tokens, potential confusion

### Verification Methodology
- All 15 checks executed as specified
- No fixes applied (verification only)
- Evidence collected for all discrepancies
- Recommendations prioritized by severity

---

**Report Generated:** 2026-02-28
**Next Review:** After P0 fixes applied
**Contact:** karma-peer (Claude Code)
