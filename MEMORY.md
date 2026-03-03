# Universal AI Memory — Current State

## Karma Architecture — Locked Principles (2026-03-03)

**Optimization law:** Assimilate primitives. Reject systems. Integrate only what doesn't add dependency gravity or parallel truth. Complexity is failure.

**True architecture:**
- Single coherent peer. Droplet-primary (vault-neo = source of truth)
- Chat surface: Hub Bridge. Identity: Vault ledger. Continuity: Resurrection Packs
- K2 = continuity substrate only (preserve, observe, sync). NEVER calls LLM autonomously
- Karma is the ONLY origin of thought. No exceptions.

**PDF primitives extraction filter:** (1) fits single-consciousness, (2) no dependency gravity, (3) no parallel truth, (4) implementable in existing vault-neo + Hub Bridge + FalkorDB stack

## Session 58 (2026-03-03) — Repo Reconciliation

**Status:** 🔴 CRITICAL RECONCILIATION — GitHub, droplet, and P1 were in three different states

### Reconciliation (in progress)
- **Root cause found:** Droplet used as dev environment — karma-core files written directly on vault-neo, never committed
- **Droplet uncommitted:** hooks.py (334 lines), memory_tools.py (704 lines), router.py (292 lines), session_briefing.py, compaction.py, consciousness.py, identity.json
- **P1 feature branch:** 20+ commits ahead of main (session-57 docs, batch_ingest, GSD workflow, ambient hooks)
- **GitHub main:** stale at b778ef2 Phase 4.4 — predates all of the above
- **Action:** SCP'd droplet files to P1, committing here, then merging feature branch → main → push → droplet pull

### Prevention being implemented this session
- CLAUDE.md hard rule: droplet is deploy target only, never edit directly
- Session-end hook: SSH to droplet, fail if dirty git status
- Droplet cron: hourly dirty-check alert

## Session 57 (2026-03-03) — Current State

**Status:** 🟡 BLOCKERS CLEARING — FalkorDB unfrozen, hub/chat ingestion now running

### Verified System State (2026-03-03)

| Component | Status | Evidence |
|-----------|--------|----------|
| Hub Bridge API | ✅ WORKING | /v1/chat, /v1/ambient, /v1/context, /v1/cypher operational |
| Consciousness Loop | ✅ WORKING | 60s OBSERVE-only cycles confirmed, zero LLM calls |
| Ledger | ✅ GROWING | ~4000 entries, git commits + session-end hooks capturing |
| FalkorDB Graph | ✅ GROWING | 1642+ nodes — batch_ingest running, cron every 6h |
| Conversation Capture | ✅ FIXED | hub/chat entries now ingested via extended batch_ingest |
| Chrome Extension | ❌ SHELVED | Never worked reliably. Legacy data only. |
| batch_ingest | ✅ RUNNING | Cron every 6h + extended to process hub/chat entries |
| Ambient Tier 1 | ✅ WORKING | Git + session-end hooks → /v1/ambient → ledger confirmed |
| Karma Terminal | ⚠️ STALE | Last capture 2026-02-27 |
| GSD Workflow | ✅ ADOPTED | .gsd/ structure in place |

### Active Blockers (Priority Order)

**#1 ✅ RESOLVED: FalkorDB unfrozen (2026-03-03)**
- batch_ingest ran: 1570 → 1642 nodes
- LEDGER_PATH corrected: `/ledger/memory.jsonl` (container mount)
- Cron installed: `0 */6 * * *` on vault-neo

**#2 ✅ RESOLVED: hub/chat entries now reach FalkorDB (2026-03-03)**
- Root cause: batch_ingest only checked `assistant_message`; hub/chat uses `assistant_text`
- Fix: extended batch_ingest.py — detects hub/chat by tags, reads `assistant_text` fallback
- 1538 Colby<->Karma conversations now being ingested (running now)
- Option 2 (ASSIMILATE signals) earmarked for future quality/curation layer

**#3 ✅ RESOLVED: Auto-schedule configured (2026-03-03)**
- Cron every 6h on vault-neo

**#4 URGENT: karma-server image rebuild + restart loop**
- batch_ingest hub-chat fix is docker cp'd into container ONLY — not in image
- If karma-server restarts (restart loop active), the fix is lost and cron runs stale code
- Fix: git pull on vault-neo first, then rebuild image, then restart container
- Commands: see Next Session step 3

**#5 LOW: gpt-5-mini vs gpt-4o-mini drift**
- hub.env shows `MODEL_DEEP=gpt-5-mini` — verify if intentional or typo

**#6 IN PROGRESS: PDF ingestion pipeline — fixing now**
- Caller script: `Scripts/karma-inbox-watcher.ps1` — watches Inbox/ and Gated/, sends base64 PDF to /v1/ingest
- Inbox/ failures: "connection forcibly closed" — large PDFs (up to 15MB raw = ~20MB base64) hit parseBody 20MB cap → req.destroy()
- FIX: increased parseBody limit to 30MB in hub-bridge/app/server.js — deployed and rebuilt
- Gated/ failures: old error from pre-reconciliation image (body destructure bug) — current code is correct
- Token file: `C:\Users\raest\Documents\Karma_SADE\.hub-chat-token` (exists)
- Script paths: run with -InboxPath and -GatedPath pointing to Karma_PDFs/Inbox/ and Karma_PDFs/Gated/
- After rebuild: delete .error.txt files, run watcher to reprocess all PDFs

### Session 57 Accomplishments
- ✅ Consciousness loop OBSERVE-only contract confirmed (CYCLE_REFLECTION = log type, not mode)
- ✅ Chrome extension shelved — all docs updated
- ✅ FalkorDB unfrozen — batch_ingest ran, cron configured
- ✅ LEDGER_PATH bug fixed in all docs (was wrong host path, correct = /ledger/memory.jsonl)
- ✅ hub/chat → FalkorDB gap closed — extended batch_ingest with hub-chat support
- ✅ 1538 Colby<->Karma conversations now ingesting into graph
- ✅ Superpowers enforcement: CLAUDE.md mandatory workflow table added, save_observation added to capture protocol, resurrect skill updated to invoke using-superpowers
- ✅ 4 structural gaps closed: Session Start → resurrect skill only (Gap 1), GSD enforcement rule (Gap 2), token efficiency table (Gap 3), save_observation as Session End step 1 (Gap 4)
- ✅ Session ritual table + claude-mem always-available section added to CLAUDE.md (dual-write rule, at-the-moment rule)

### Next Session — Step by Step (exact commands)
1. `ssh vault-neo "docker exec karma-server tail -30 /tmp/batch.log"` — verify batch complete, check ok/err
2. `ssh vault-neo "docker exec falkordb redis-cli -p 6379 GRAPH.QUERY neo_workspace 'MATCH (n) RETURN count(n)'"` — verify node count grew from 1642
3. Rebuild karma-server image (URGENT — restart loop will kill docker cp'd fix):
   `ssh vault-neo "cd /home/neo/karma-sade/karma-core && git pull && docker build -t karma-core:latest ."`
   Then: `docker inspect anr-karma-server` → stop/remove/restart with same params
4. `ssh vault-neo "docker logs anr-karma-server --tail=50 2>&1 | grep -i 'exit\|error\|crash\|oom'"` — diagnose Blocker #4
5. `ssh vault-neo "grep MODEL_DEEP /opt/seed-vault/memory_v1/hub_bridge/config/hub.env"` — verify Blocker #5
6. Triage Karma_PDFs pipeline — find caller script, fix Inbox + Gated failure modes

---

## Infrastructure
- P1 + K2: i9-185H, 64GB RAM, RTX 4070 8GB
- Tailscale: P1=100.124.194.102, K2=100.75.109.92, droplet=100.92.67.70
- SSH alias: vault-neo
- API keys: C:\Users\raest\OneDrive\Documents\Aria1\NFO\mylocks1.txt
- Git ops: Use PowerShell (Git Bash has persistent index.lock issue on Windows)
- FalkorDB graph name: `neo_workspace` (NOT `karma`)
- Hub token path: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt`

## Known Pitfalls (active)
- `python3` not available in Git Bash — use SSH for Python ops
- Docker compose service: `hub-bridge` (container name: `anr-hub-bridge`)
- batch_ingest requires `LEDGER_PATH` override (see CLAUDE.md)
- karma-server built from Docker image — source file edits require rebuild
- FalkorDB requires both env vars: `FALKORDB_DATA_PATH=/data` and `FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 100'`
- **hub-bridge build context ≠ git repo**: build uses `/opt/seed-vault/memory_v1/hub_bridge/app/`, NOT `/home/neo/karma-sade/hub-bridge/app/`. After any git pull, sync first: `cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js`

# currentDate
Today's date is 2026-03-03.
