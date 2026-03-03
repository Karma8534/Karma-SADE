# Universal AI Memory — Current State

## Session 57 (2026-03-03) — Current State

**Status:** 🔴 CRITICAL BLOCKERS IDENTIFIED — FalkorDB frozen, conversation capture broken

### Verified System State (2026-03-03)

| Component | Status | Evidence |
|-----------|--------|----------|
| Hub Bridge API | ✅ WORKING | /v1/chat, /v1/ambient, /v1/context, /v1/cypher operational |
| Consciousness Loop | ✅ WORKING | 60s OBSERVE-only cycles confirmed, zero LLM calls |
| Ledger | ✅ GROWING | 3980 entries, git commits + session-end hooks capturing |
| FalkorDB Graph | 🔴 FROZEN | 1570 nodes — batch_ingest NOT running, no growth |
| Conversation Capture | 🔴 BROKEN | No new /v1/chat entries from human conversations since 2026-02-27 |
| Chrome Extension | ❌ SHELVED | Never worked reliably. Legacy data only (last: 2026-02-26) |
| batch_ingest | 🔴 NOT RUNNING | No scheduler configured. Manual run required. |
| Ambient Tier 1 | ✅ WORKING | Git + session-end hooks → /v1/ambient → ledger confirmed |
| Karma Terminal | ⚠️ STALE | Last capture 2026-02-27 |
| GSD Workflow | ✅ ADOPTED | .gsd/ structure in place, phase-tier1 complete |

### Active Blockers (Priority Order)

**#1 CRITICAL: FalkorDB frozen — batch_ingest not running**
- Graph stuck at 1570 nodes since last manual run
- Karma cannot recall recent work, sessions, or decisions from memory
- Fix: Run batch_ingest + configure auto-schedule
- Command: `docker exec karma-server sh -c 'LEDGER_PATH=/ledger/memory.jsonl python3 /app/batch_ingest.py > /tmp/batch.log 2>&1'`
- Auto-schedule: cron configured on vault-neo (every 6h, installed 2026-03-03)

**#2 CRITICAL: No conversation capture path**
- Chrome extension SHELVED (never worked)
- /v1/chat conversations reaching hub-bridge but last human conversation captured was 2026-02-27
- Karma has no way to accumulate conversation memory without a capture mechanism
- Fix: Design and implement replacement capture path (karma-terminal, CLI wrapper, or direct /v1/chat logging)

**#3 HIGH: No auto-schedule for batch_ingest**
- Even if batch_ingest runs now, the graph will freeze again
- Fix: Configure cron job or consciousness-loop-triggered ingest

**#4 MEDIUM: karma-server restart loop**
- `cycle: 1` on every LOG_GROWTH event = container restarting
- Metrics reset on restart = no reliable cycle tracking
- Fix: Investigate restart cause (OOM? crash? intentional?)

**#5 LOW: gpt-5-mini vs gpt-4o-mini drift**
- hub.env shows `MODEL_DEEP=gpt-5-mini` but docs say gpt-4o-mini
- Verify: Is gpt-5-mini a real model or a typo?

### Session 56 Accomplishments
- ✅ GSD documentation framework adopted (.gsd/ directory)
- ✅ Ambient Tier 1 verified end-to-end (git hooks → ledger confirmed)
- ✅ Consciousness loop analyzed: OBSERVE-only contract confirmed, no LLM calls
- ✅ Discovered Chrome extension is shelved — docs updated
- ✅ Discovered FalkorDB frozen — batch_ingest not running
- ✅ PowerShell required for git ops (Git Bash has persistent lock issue on Windows)

### Next Session Actions (Priority)
1. Run batch_ingest manually — unfreeze FalkorDB NOW
2. Verify batch_ingest results (check /tmp/batch.log, node count before/after)
3. Configure auto-schedule for batch_ingest (cron on vault-neo)
4. Design conversation capture replacement (what replaces the Chrome extension?)
5. Investigate karma-server restart loop

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

# currentDate
Today's date is 2026-03-03.
