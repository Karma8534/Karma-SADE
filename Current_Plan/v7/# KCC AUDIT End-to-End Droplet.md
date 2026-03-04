# KCC AUDIT: End-to-End Droplet Verification Against v7 Ground Truth

## YOUR ROLE

You are an auditor. Your ONLY job is to verify what is ACTUALLY running on the droplet and compare it against the v7 specification documents. You do NOT fix anything. You produce a factual report with evidence for every finding.

## GROUND RULES — NON-NEGOTIABLE

1. **READ BEFORE ACTING.** You must read every v7 reference file listed in §1 before running any audit command.
2. **EVIDENCE FOR EVERY CLAIM.** Every finding must include the exact command you ran and the exact output you received. No paraphrasing. Paste raw output.
3. **DO NOT FIX ANYTHING.** Do not edit files, rebuild containers, change config, or modify code. You are read-only.
4. **DO NOT ADD SERVICES.** Do not install packages, create files on the droplet, or run pip/npm install.
5. **ALL PATHS ARE `/opt/seed-vault/memory_v1/`** — NOT `/home/neo/karma-sade/` (except identity spine files which ARE at `/home/neo/karma-sade/`).
6. **MODEL_DEFAULT is `glm-4.7-flash`** — if you find it set to anything else, mark it as CRITICAL FAILURE.
7. **If a command fails or returns unexpected output, report the raw output. Do not guess.**
8. **Work through the audit sections in order. Do not skip ahead.**
9. **Do not speculate about fixes. Report facts only.**

## §1 — REFERENCE DOCUMENTS

Read these files from the workspace BEFORE running any commands. These are your ground truth:

| File | What It Contains |
|------|-----------------|
| `KARMA_BUILD_PLAN_v7.md` | Build phases, bugs, priorities, deployed state |
| `KARMA_MEMORY_ARCHITECTURE_v7.md` | Tiered storage, memory tool API, admission rules |
| `KARMA_HARDENED_REVIEW_v7.md` | Failure modes, cost model, corrected architecture |
| `KARMA_PEER_ARCHITECTURE_v7.md` | Full architecture, endpoints, file structure, flows |
| `CC_KARMA_MASTER_FIX.md` | The learning fix that CC is currently running (may or may not be applied yet) |

Read all five. Internalize the expected state before proceeding.

---

## §2 — AUDIT SECTION A: Infrastructure

SSH to the droplet: `ssh neo@64.225.13.144`

### A1: Container Health
```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
```
**Expected (v7 §1.2):** 7 containers running:
- anr-hub-bridge (running)
- karma-server (healthy)
- anr-vault-api (healthy)
- anr-vault-search (healthy)
- anr-vault-caddy (running)
- anr-vault-db (healthy)
- falkordb (running)

**Report:** For each container, state: Name | Expected Status | Actual Status | PASS/FAIL

### A2: Droplet Resources
```bash
free -m | head -3
df -h / | tail -1
```
**Expected (v7):** 4GB RAM, 50GB disk. Report actual values.

### A3: Docker Compose File Locations
```bash
ls -la /opt/seed-vault/docker-compose.yml /opt/seed-vault/compose.hub.yml 2>/dev/null
ls -la /opt/seed-vault/memory_v1/compose/compose.yml /opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml 2>/dev/null
```
**Report:** Which compose files actually exist and their modification dates.

---

## §3 — AUDIT SECTION B: Model Routing & Config

### B1: MODEL_DEFAULT
```bash
grep -i "MODEL_DEFAULT\|model_default" /opt/seed-vault/memory_v1/hub_bridge/config/hub.env
```
**Expected:** `MODEL_DEFAULT=glm-4.7-flash`
**If anything else: CRITICAL FAILURE.**

### B2: All Environment Variables
```bash
cat /opt/seed-vault/memory_v1/hub_bridge/config/hub.env | grep -v "^#" | grep -v "^$" | sort
```
**Report:** Full env var list (redact API keys — show only first/last 4 chars).

### B3: Verify Model in Hub-Bridge Runtime
```bash
docker logs $(docker ps -q --filter name=hub-bridge) 2>&1 | grep -i "model\|glm\|gpt\|openai\|zai\|routing" | tail -20
```
**Report:** What model(s) appear in recent hub-bridge logs?

### B4: Provider Routing in server.js
```bash
docker exec $(docker ps -q --filter name=hub-bridge) grep -n "glm\|gpt-4o\|minimax\|groq\|deepinfra\|z\.ai\|zai\|MODEL_DEFAULT\|primaryModel\|fallback" /app/server.js | head -30
```
**Expected (v7 §1.3):**
- GLM-4.7-Flash via Z.AI — primary chat
- gpt-4o-mini via OpenAI — tool calls
- gpt-4o via OpenAI — 429 fallback
- NO MiniMax, NO GLM-5, NO Groq

**Report:** Each model reference found, with line numbers.

---

## §4 — AUDIT SECTION C: Critical Bugs (v7 §2)

### C1: Phantom Tools Bug
```bash
docker exec $(docker ps -q --filter name=hub-bridge) grep -n "get_vault_file\|graph_query" /app/server.js
```
**Expected (v7 Bug 1):** These strings exist in buildSystemText() but NOT in TOOL_DEFINITIONS.
**Report:** Line numbers where found. Is this bug still present or was it fixed by CC?

```bash
docker exec $(docker ps -q --filter name=hub-bridge) grep -n "TOOL_DEFINITIONS\|tool_definitions" /app/server.js | head -10
```
**Report:** What tools are in TOOL_DEFINITIONS?

### C2: Duplicate karmaCtx Injection
```bash
docker exec $(docker ps -q --filter name=hub-bridge) grep -n "karmaCtx\|KNOWLEDGE STATE" /app/server.js | head -20
```
**Expected (v7 Bug 2):** karmaCtx injected twice — once in base (~line 369), once as "YOUR COMPLETE KNOWLEDGE STATE" (~lines 396-397).
**Report:** How many injection points found? Is bug still present or fixed?

### C3: Consciousness Loop Status
```bash
docker logs $(docker ps -q --filter name=karma-server) 2>&1 | grep -i "consciousness\|OBSERVE\|THINK\|DECIDE\|ACT\|REFLECT" | tail -10
```
```bash
wc -l /opt/seed-vault/memory_v1/ledger/consciousness.jsonl
tail -3 /opt/seed-vault/memory_v1/ledger/consciousness.jsonl
```
**Expected (v7 Bug 3):** Loop inactive. ~109 historical entries. No new entries.
**Report:** Is the consciousness loop producing new entries or still dead?

---

## §5 — AUDIT SECTION D: Memory & Learning Pipeline

### D1: Episode Ingestion Path
```bash
docker exec $(docker ps -q --filter name=hub-bridge) grep -n "ingest-episode\|/ask\|ingest_episode" /app/server.js | head -10
```
```bash
docker exec $(docker ps -q --filter name=karma-server) grep -n "ingest.episode\|/ingest-episode\|/ask" /app/server.py | head -10
```
**Expected:** v7 says hub-bridge NEVER calls `/ask` or `/ingest-episode`. CC_KARMA_MASTER_FIX.md was supposed to add this.
**Report:**
- Does `/ingest-episode` endpoint exist in server.py? YES/NO
- Does hub-bridge call `/ingest-episode` after chat? YES/NO
- Is episode ingestion working? (check logs below)

```bash
docker logs $(docker ps -q --filter name=karma-server) 2>&1 | grep -i "GRAPHITI\|ingest" | tail -10
```
```bash
docker logs $(docker ps -q --filter name=hub-bridge) 2>&1 | grep -i "INGEST\|ingest" | tail -10
```
**Report:** Any evidence of recent episode ingestion?

### D2: Auto-Promote Status
```bash
docker exec $(docker ps -q --filter name=karma-server) grep -n "auto.promote\|auto_promote\|/auto-promote" /app/server.py | head -10
```
```bash
cat /opt/seed-vault/memory_v1/ledger/candidates.jsonl | python3 -c "
import sys, json
lines = [json.loads(l) for l in sys.stdin if l.strip()]
total = len(lines)
promoted = sum(1 for l in lines if l.get('promoted'))
pending = total - promoted
print(f'Total candidates: {total}, Promoted: {promoted}, Pending: {pending}')
for l in lines[-5:]:
    print(json.dumps(l, indent=2)[:200])
"
```
**Report:** Does auto-promote exist? Is it being called? Candidate counts.

### D3: FalkorDB Graph State
```bash
python3 -c "
import falkordb
r = falkordb.FalkorDB(host='localhost', port=6379)
g = r.select_graph('neo_workspace')
ent = g.query('MATCH (n:Entity) RETURN count(n) AS c').result_set[0][0]
epi = g.query('MATCH (n:Episodic) RETURN count(n) AS c').result_set[0][0]
try:
    can = g.query('MATCH (n:Episodic) WHERE n.lane = \"canonical\" RETURN count(n) AS c').result_set[0][0]
except:
    can = 'QUERY_FAILED'
try:
    cand = g.query('MATCH (n:Episodic) WHERE n.lane = \"candidate\" RETURN count(n) AS c').result_set[0][0]
except:
    cand = 'QUERY_FAILED'
try:
    null_lane = g.query('MATCH (n:Episodic) WHERE n.lane IS NULL RETURN count(n) AS c').result_set[0][0]
except:
    null_lane = 'QUERY_FAILED'
print(f'Entity: {ent}')
print(f'Episodic: {epi}')
print(f'  canonical: {can}')
print(f'  candidate: {cand}')
print(f'  lane=NULL: {null_lane}')
"
```
**Expected (v7 verified):** Entity ~161, Episodic ~1230 (1229 lane=None, 1 candidate, 0 canonical)
**Report:** Exact counts. Has anything changed since the v7 snapshot?

### D4: Test Baxter (if CC has run)
```bash
python3 -c "
import falkordb
r = falkordb.FalkorDB(host='localhost', port=6379)
g = r.select_graph('neo_workspace')
res = g.query(\"MATCH (n) WHERE toLower(COALESCE(n.content, n.summary, n.name, '')) CONTAINS 'baxter' RETURN n.name, labels(n), COALESCE(n.content, n.summary, '') AS text LIMIT 5\")
for row in res.result_set:
    print(row)
if not res.result_set:
    print('Baxter NOT found in graph')
"
```
**Report:** Is Baxter in the graph? This is the learning test from CC_KARMA_MASTER_FIX.md.

### D5: Ledger State
```bash
wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl
wc -l /opt/seed-vault/memory_v1/ledger/consciousness.jsonl
wc -l /opt/seed-vault/memory_v1/ledger/collab.jsonl
wc -l /opt/seed-vault/memory_v1/ledger/candidates.jsonl
ls -la /opt/seed-vault/memory_v1/ledger/
```
**Expected:** memory.jsonl 3449+ lines, consciousness.jsonl ~109, candidates.jsonl ~10 entries
**Report:** Exact line counts and file sizes.

---

## §6 — AUDIT SECTION E: Identity Spine

### E1: Identity Files Exist
```bash
ls -la /home/neo/karma-sade/identity.json /home/neo/karma-sade/invariants.json /home/neo/karma-sade/direction.md /home/neo/karma-sade/MEMORY.md
```
**Report:** All four files exist? Dates?

### E2: Identity Loaded Into Context
```bash
docker exec $(docker ps -q --filter name=hub-bridge) grep -n "identity.json\|invariants.json\|direction.md\|MEMORY.md\|karmaCtx\|loadVaultFile\|readVaultFile" /app/server.js | head -20
```
**Report:** How is identity spine loaded? Evidence that it's injected into every /v1/chat.

---

## §7 — AUDIT SECTION F: API Endpoints

### F1: Hub-Bridge Endpoints
```bash
docker exec $(docker ps -q --filter name=hub-bridge) grep -n "app\.\(get\|post\|patch\|put\|delete\)\|router\.\(get\|post\|patch\|put\|delete\)" /app/server.js | head -30
```
**Expected (v7 §V.A):** /v1/chat, /v1/admit, /v1/retrieve, /v1/reflect, /v1/health, /v1/cypher, /v1/vault-file
**Report:** Which endpoints actually exist?

### F2: Karma-Server Endpoints
```bash
docker exec $(docker ps -q --filter name=karma-server) grep -n "@app\.\(get\|post\|patch\|put\|delete\)" /app/server.py | head -30
```
**Report:** Which endpoints actually exist? Does /ingest-episode exist (CC fix)?

### F3: Live Chat Test
```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
curl -s -X POST http://localhost:18090/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "What is my cats name?"}' | python3 -m json.tool | head -25
```
**Expected:** Karma responds with "Ollie". Check that model=glm-4.7-flash in response metadata.
**Report:** Full response (first 25 lines). Does Karma know Ollie? What model was used?

### F4: Raw-Context Retrieval Test
```bash
curl -s "http://localhost:8340/raw-context?q=who+is+ollie" | python3 -m json.tool | head -30
```
**Report:** Does raw-context return relevant info about Ollie?

### F5: Health Endpoints
```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
curl -s http://localhost:18090/v1/health -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
curl -s http://localhost:8340/health | python3 -m json.tool
```
**Report:** Both healthy?

---

## §8 — AUDIT SECTION G: Build Phase Status

Cross-reference actual state against v7 Build Plan §3:

| Phase | v7 Expected Status | Your Finding | Evidence |
|-------|-------------------|--------------|----------|
| Phase 0: Foundation | COMPLETE | [fill] | [command + output] |
| Phase 1: Hub Bridge | COMPLETE | [fill] | [command + output] |
| Phase 2: Karma Server | COMPLETE | [fill] | [command + output] |
| Phase 3: Ledger System | COMPLETE | [fill] | [command + output] |
| Phase 4: Identity Spine | COMPLETE | [fill] | [command + output] |
| Phase 5: Retrieval Pipeline | COMPLETE (with bugs) | [fill] | [command + output] |
| Phase 6: Hardening | IN PROGRESS | [fill] | [command + output] |
| Phase 7: Memory Architecture | NOT STARTED | [fill] | [command + output] |
| Phase 8: K2 | NOT STARTED / DEFERRED | [fill] | [command + output] |

---

## §9 — AUDIT SECTION H: Cost & Security

### H1: API Keys Present
```bash
ls -la /opt/seed-vault/memory_v1/session/openai.api_key.txt
ls -la /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt
```
**Report:** Keys exist? (Do NOT print key values.)

### H2: Backup Cron
```bash
crontab -l 2>/dev/null
sudo crontab -l 2>/dev/null
ls -la /opt/seed-vault/backups/ 2>/dev/null | tail -5
```
**Expected (v7):** Backup cron deployed (PR #12). Report what's scheduled and when last backup ran.

---

## §10 — FINAL AUDIT REPORT

After completing ALL sections above, compile your findings into this exact format:

```
══════════════════════════════════════════════════
     KCC AUDIT REPORT — KARMA DROPLET vs v7
     Date: [DATE TIME EST]
══════════════════════════════════════════════════

CRITICAL FINDINGS (things that are broken or wrong):
1. [finding — with evidence reference]
2. [finding]
...

DEVIATIONS FROM v7 (things that differ but may be intentional):
1. [deviation — with evidence reference]
2. [deviation]
...

CONFIRMED WORKING (matches v7 spec):
1. [item]
2. [item]
...

CC MASTER FIX STATUS:
- /ingest-episode endpoint added: [YES/NO/PARTIAL]
- Hub-bridge calls /ingest-episode: [YES/NO/PARTIAL]
- Auto-promote wired to consciousness loop: [YES/NO/PARTIAL]
- Baxter learning test: [PASS/FAIL/NOT RUN]

GRAPH STATE:
- Entity: [N]
- Episodic: [N] (canonical: [N], candidate: [N], lane=NULL: [N])

MODEL_DEFAULT: [value] — [CORRECT/CRITICAL FAILURE]

STEP-BY-STEP RESOLUTION PLAN:
(Ordered by priority. For each item: what to do, which file to edit, what the edit is, and how to verify.)

1. [P0] [description]
   - File: [path]
   - Edit: [what to change]
   - Verify: [command to confirm]

2. [P0] [description]
   ...

3. [P1] [description]
   ...

(Continue until all findings are addressed)
══════════════════════════════════════════════════
```

## ANTI-DRIFT RULES

1. You are READ-ONLY. Do not edit, create, delete, or modify any file on the droplet.
2. After every SSH command, paste the raw output. No summaries, no "as expected."
3. If a command fails, paste the error. Do not retry with different commands unless you explain why.
4. Do not skip audit sections. Complete them in order A through H.
5. Do not add bonus checks, cleanup tasks, or improvement suggestions outside the report format.
6. Do not change MODEL_DEFAULT or any configuration.
7. If you discover something not covered by v7 docs, note it under DEVIATIONS but do not investigate further.
8. Your resolution plan must reference specific line numbers and file paths from your audit evidence.
9. Do not run any command that writes data (POST to /v1/chat, /v1/admit, etc.) except the read-only tests in §7.F3-F5 which are necessary for verification.
10. Complete the entire audit in a single session. Do not pause for approval between sections.
