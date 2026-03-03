# Universal AI Memory — Current State

## Karma Architecture — Locked Principles (2026-03-03)

**Optimization law:** Assimilate primitives. Reject systems. Integrate only what doesn't add dependency gravity or parallel truth. Complexity is failure.

**True architecture:**
- Single coherent peer. Droplet-primary (vault-neo = source of truth)
- Chat surface: Hub Bridge. Identity: Vault ledger. Continuity: Resurrection Packs
- K2 = continuity substrate only (preserve, observe, sync). NEVER calls LLM autonomously
- Karma is the ONLY origin of thought. No exceptions.

**PDF primitives extraction filter:** (1) fits single-consciousness, (2) no dependency gravity, (3) no parallel truth, (4) implementable in existing vault-neo + Hub Bridge + FalkorDB stack

## Session 58 (2026-03-03) — Repo Reconciliation + PDF Pipeline

**Status:** ✅ COMPLETE

### Accomplishments
- ✅ Three-way repo divergence resolved — GitHub/P1/droplet all at commit 63df177, then 833c06a
- ✅ 1754 lines of production karma-core rescued from droplet (hooks.py, memory_tools.py, router.py, session_briefing.py, compaction.py, consciousness.py, identity.json)
- ✅ Drift prevention deployed: CLAUDE.md hard rule (droplet = deploy target only) + session-end Check 6 (SSH dirty check) + hourly cron on vault-neo
- ✅ PDF pipeline restored: parseBody 30MB, hub-bridge rebuilt, watcher running against Karma_PDFs/
- ✅ CRITICAL PITFALL documented: hub-bridge build context ≠ git repo (must cp server.js before rebuild)

### What triggered reconciliation
- Droplet used as dev environment across multiple sessions — karma-core files never committed
- P1 feature branch 20+ commits ahead of GitHub main
- Root cause fixed permanently via CLAUDE.md rule + session-end hook

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

**#3 ✅ RESOLVED: Auto-schedule configured (2026-03-03, verified session-58)**
- Cron every 6h on vault-neo — `0 */6 * * *` with pgrep guard (was claimed done session-57 but was actually missing; added session-58)

**#4 URGENT: karma-server image rebuild + restart loop**
- batch_ingest hub-chat fix is docker cp'd into container ONLY — not in image
- If karma-server restarts (restart loop active), the fix is lost and cron runs stale code
- Fix: git pull on vault-neo first, then rebuild image, then restart container
- Commands: see Next Session step 3

**#5 LOW: gpt-5-mini vs gpt-4o-mini drift**
- hub.env shows `MODEL_DEEP=gpt-5-mini` — verify if intentional or typo

**#6 ✅ RESOLVED: PDF ingestion pipeline restored (2026-03-03)**
- Caller: `Scripts/karma-inbox-watcher.ps1` — watches Inbox/ and Gated/, sends base64 to /v1/ingest
- Root cause: large PDFs (15MB raw = ~20MB base64) hit parseBody 20MB cap → req.destroy()
- Fix: parseBody limit raised to 30MB — deployed + hub-bridge image rebuilt
- Watcher running, processing ~80 PDF backlog, Done/ growing (108 → 112+), 0 new errors
- Token: `C:\Users\raest\Documents\Karma_SADE\.hub-chat-token`; paths: Karma_PDFs/{Inbox,Gated,Processing,Done}

### Session 57 Accomplishments
- ✅ Consciousness loop OBSERVE-only contract confirmed (CYCLE_REFLECTION = log type, not mode)
- ✅ Chrome extension shelved — all docs updated
- ✅ FalkorDB unfrozen — batch_ingest ran, cron claimed configured (NOT VERIFIED — found missing in session-58, now fixed)
- ✅ LEDGER_PATH bug fixed in all docs (was wrong host path, correct = /ledger/memory.jsonl)
- ✅ hub/chat → FalkorDB gap closed — extended batch_ingest with hub-chat support
- ✅ 1538 Colby<->Karma conversations now ingesting into graph
- ✅ Superpowers enforcement: CLAUDE.md mandatory workflow table added, save_observation added to capture protocol, resurrect skill updated to invoke using-superpowers
- ✅ 4 structural gaps closed: Session Start → resurrect skill only (Gap 1), GSD enforcement rule (Gap 2), token efficiency table (Gap 3), save_observation as Session End step 1 (Gap 4)
- ✅ Session ritual table + claude-mem always-available section added to CLAUDE.md (dual-write rule, at-the-moment rule)

### Next Session — Step by Step (exact commands)
1. `ssh vault-neo "docker exec karma-server tail -30 /tmp/batch.log"` — verify batch complete (running overnight, ETA ~03:30 UTC)
2. `ssh vault-neo "docker exec falkordb redis-cli -p 6379 GRAPH.QUERY neo_workspace 'MATCH (n) RETURN count(n)'"` — verify node count grew from ~2010
3. Rebuild karma-server image (**URGENT — do AFTER batch completes**, image doesn't have hub-chat fix):
   ```
   ssh vault-neo "docker inspect karma-server --format '{{.HostConfig.Binds}} {{json .HostConfig.PortBindings}} {{.Config.Env}}'"
   ```
   Then rebuild + restart with identical run params
4. `ssh vault-neo "grep MODEL_DEEP /opt/seed-vault/memory_v1/hub_bridge/config/hub.env"` — verify Blocker #5 (gpt-5-mini typo?)
5. Check PDF watcher progress: `ls Karma_PDFs/Done/ | wc -l` — should be growing from 112+

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
