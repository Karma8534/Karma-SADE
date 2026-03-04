# KCC DROPLET VERIFICATION PROMPT
# Paste this entire block into a new Claude Code (CC/KCC) session.
# It will verify the droplet matches the v7 build plan and report discrepancies.
# No Asher/Computer credits needed — runs entirely in CC.

---

## TASK: Verify droplet state matches KARMA v7 build plan

You are verifying that the deployed state on the droplet (64.225.13.144) matches the v7 build plans. Run EVERY check below, collect results, then produce a single summary report at the end. Do NOT fix anything — only report.

**SSH:** `ssh neo@64.225.13.144` (sudo password: `ollieboo`)
**All file edits and Docker operations use /opt/seed-vault/memory_v1/ — NOT /home/neo/karma-sade/**

### CHECK 1: Containers (expect 7 running)
```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | sort
```
**Expected:** anr-hub-bridge, karma-server (healthy), anr-vault-api (healthy), anr-vault-search (healthy), anr-vault-caddy, anr-vault-db (healthy), falkordb

### CHECK 2: Hub Bridge server.js — Phantom Tools Bug (FIXED v7.1)
```bash
grep -n "get_vault_file\|graph_query" /opt/seed-vault/memory_v1/hub_bridge/app/server.js
```
**Expected (v7.1):** No results — phantom tools have been removed. Line 376 should now list `read_file, write_file, edit_file, bash`.
```bash
grep -n "TOOL_DEFINITIONS\|tool_definitions\|tools:" /opt/seed-vault/memory_v1/hub-bridge/app/server.js | head -20
```
**Verify:** TOOL_DEFINITIONS should contain read_file, write_file, edit_file, bash — NOT get_vault_file or graph_query.

### CHECK 3: Hub Bridge server.js — Duplicate karmaCtx (FIXED v7.1)
```bash
grep -n "karmaCtx\|COMPLETE KNOWLEDGE STATE" /opt/seed-vault/memory_v1/hub_bridge/app/server.js
```
**Expected (v7.1):** karmaCtx appears ONLY in `base` variable. "COMPLETE KNOWLEDGE STATE" should NOT appear — duplicate block removed.

### CHECK 4: Hub Bridge server.js — Line Count
```bash
wc -l /opt/seed-vault/memory_v1/hub_bridge/app/server.js
```
**Expected:** ~1,882 lines (v7.1 — increased from 1,872 due to episode ingestion code)

### CHECK 5: Karma Server server.py — Line Count
```bash
wc -l /opt/seed-vault/memory_v1/karma-core/server.py
```
**Expected:** ~2,651 lines (v7.1 — increased from 2,629 due to /ingest-episode endpoint)

### CHECK 6: FalkorDB — Graph State
```bash
# IMPORTANT: Node label is Episodic, NOT Episode (Graphiti convention)
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (e:Episodic) RETURN COUNT(e) as episodic_nodes"
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (e:Entity) RETURN COUNT(e) as entities"
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH ()-[r]->() RETURN COUNT(r) as relationships"
```
**Expected:** Episodic >= 1240, entities >= 167, relationships >= 832

### CHECK 7: FalkorDB — Ollie Entity
```bash
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (e:Entity) WHERE e.name CONTAINS 'Ollie' OR e.name CONTAINS 'ollie' RETURN e.name, e.entity_type LIMIT 5"
```
**Expected:** Ollie exists with entries

### CHECK 8: FalkorDB — Corrupted Entities
```bash
docker exec falkordb redis-cli GRAPH.QUERY neo_workspace "MATCH (e:Entity) WHERE e.uuid IS NULL RETURN COUNT(e) as corrupted"
```
**Report:** If count > 0, note as "corrupted entities need cleanup"

### CHECK 9: JSONL Ledgers
```bash
wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl
wc -l /opt/seed-vault/memory_v1/ledger/consciousness.jsonl
ls -la /opt/seed-vault/memory_v1/ledger/collab.jsonl
ls -la /opt/seed-vault/memory_v1/ledger/candidates.jsonl
```
**Expected:** memory.jsonl >= 3847 lines, consciousness.jsonl >= 284 lines (active, growing), collab.jsonl and candidates.jsonl exist

### CHECK 10: Identity Spine Files
```bash
ls -la /home/neo/karma-sade/identity.json /home/neo/karma-sade/invariants.json /home/neo/karma-sade/direction.md
cat /home/neo/karma-sade/identity.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('version:', d.get('version','MISSING'), 'name:', d.get('name','MISSING'))"
```
**Expected:** All 3 files exist. identity.json has name=Karma, version=2.1.0

### CHECK 11: Model Routing — Verify Actual Models
```bash
grep -n "GLM\|gpt-4o\|minimax\|MiniMax\|groq\|Groq\|ZHIPU\|zhipu\|openai\|OPENAI" /opt/seed-vault/memory_v1/hub-bridge/app/server.js | grep -i "model\|api\|endpoint\|url\|provider" | head -30
```
**Expected:** GLM-4.7-Flash (Z.AI), gpt-4o-mini (OpenAI), gpt-4o (OpenAI fallback). Should NOT find active MiniMax, GLM-5, or Groq routing.

### CHECK 12: Consciousness Loop Status
```bash
tail -3 /opt/seed-vault/memory_v1/ledger/consciousness.jsonl | python3 -c "import sys; [print(line.strip()[:200]) for line in sys.stdin]"
docker logs karma-server --tail=20 2>&1 | grep -i "consciousness\|cycle\|observe\|think"
```
**Expected (v7.1):** consciousness.jsonl has RECENT entries (loop is ACTIVE). Consciousness cycle output should show in logs with OBSERVE, LOG_GROWTH, and auto-promote entries.

### CHECK 13: Backup Cron
```bash
crontab -l 2>/dev/null || echo "no user crontab"
sudo crontab -l 2>/dev/null || echo "no root crontab"
ls -la /opt/seed-vault/backups/ 2>/dev/null || echo "no backups directory"
```
**Report:** Whether backup cron is configured and backups directory exists with recent files.

### CHECK 14: Disk and Memory
```bash
free -m | head -2
df -h / | tail -1
```
**Report:** Available RAM and disk usage.

### CHECK 15: Bearer Token Accessible
```bash
ls -la /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt
wc -c /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt
```
**Expected:** File exists, non-empty.

---

## OUTPUT FORMAT

After running ALL checks, produce a report in this exact format:

```
# DROPLET VERIFICATION REPORT
Date: [current date/time]
Verified by: KCC (Claude Code)

## CONTAINERS
- [ ] 7 containers running: [list names and health status]

## BUGS CONFIRMED
- [ ] Phantom tools bug: [CONFIRMED/NOT FOUND] — line number and text
- [ ] Duplicate karmaCtx: [CONFIRMED/NOT FOUND] — line numbers

## CODE
- [ ] server.js: [line count] lines (expected ~1872)
- [ ] server.py: [line count] lines (expected ~2629)

## FALKORDB
- [ ] Episodes: [count] (expected >= 1488)
- [ ] Entities: [count] (expected >= 3401)  
- [ ] Relationships: [count] (expected >= 5847)
- [ ] Ollie entity: [FOUND/NOT FOUND]
- [ ] Corrupted entities (null uuid): [count]

## LEDGERS
- [ ] memory.jsonl: [line count] (expected >= 3449)
- [ ] consciousness.jsonl: [line count] (expected ~109)
- [ ] collab.jsonl: [EXISTS/MISSING]
- [ ] candidates.jsonl: [EXISTS/MISSING]

## IDENTITY SPINE
- [ ] identity.json: [EXISTS/MISSING] — version: [version]
- [ ] invariants.json: [EXISTS/MISSING]
- [ ] direction.md: [EXISTS/MISSING]

## MODEL ROUTING
- [ ] GLM-4.7-Flash: [FOUND/NOT FOUND in routing]
- [ ] gpt-4o-mini: [FOUND/NOT FOUND in routing]
- [ ] gpt-4o fallback: [FOUND/NOT FOUND in routing]
- [ ] MiniMax M2.5: [FOUND/NOT FOUND — should NOT be active]
- [ ] GLM-5: [FOUND/NOT FOUND — should NOT be active]
- [ ] Groq: [FOUND/NOT FOUND — should NOT be active]

## CONSCIOUSNESS LOOP
- [ ] Status: [ACTIVE/INACTIVE]
- [ ] Last entry timestamp: [date or N/A]

## INFRASTRUCTURE
- [ ] Backup cron: [CONFIGURED/NOT CONFIGURED]
- [ ] RAM: [available]/[total] MB
- [ ] Disk: [used]/[total]
- [ ] Bearer token: [EXISTS/MISSING]

## DISCREPANCIES FROM v7 PLAN
[List ANY differences between what the checks found and what v7 plans say]

## RECOMMENDED FIXES (Priority Order)
[List fixes needed, ordered P0/P1/P2]
```

Run all checks. Report everything. Fix nothing.
