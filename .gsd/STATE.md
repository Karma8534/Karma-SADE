# STATE: Karma Peer — Decisions, Blockers, Progress

**Last updated:** 2026-03-03T19:30:00Z
**Session:** 57 (Blocker Analysis + Doc Correction)
**Canonical source:** This file. Read at session start.

---

## Current Status (Verified 2026-03-03)

| Component | Status | Notes |
|-----------|--------|-------|
| **Consciousness Loop** | ✅ WORKING | 60s OBSERVE-only cycles. Zero LLM calls confirmed in source. |
| **Hub Bridge API** | ✅ WORKING | /v1/chat, /v1/ambient, /v1/context, /v1/cypher operational. |
| **Voice & Persona** | ✅ DEPLOYED | Peer-level voice verified. No service-desk closers. gpt-4o default. |
| **FalkorDB Graph** | 🔴 FROZEN | 1570 nodes. batch_ingest NOT running. Graph not growing. |
| **Ledger** | ✅ GROWING | 3980 entries. Git commits + session-end hooks capturing actively. |
| **Work-Loss Prevention** | ✅ GATES LIVE | Pre-commit hook + session-end hook both active and verified. |
| **Ambient Tier 1 Hooks** | ✅ WORKING | Git + session-end captures verified in ledger (2026-03-03). |
| **Ambient Tier 2 Endpoint** | ✅ DEPLOYED | /v1/context endpoint working. |
| **GSD File Structure** | ✅ ADOPTED | All .gsd/ files in place and being used. |
| **Chrome Extension** | ❌ SHELVED | Never worked reliably. Removed from all docs. Legacy data only. |
| **Conversation Capture** | 🔴 BROKEN | No reliable path to capture human conversations into memory. |
| **batch_ingest Schedule** | 🔴 MISSING | No auto-scheduler. Graph will stay frozen without manual runs. |

---

## Active Blockers (Priority Order)

### Blocker #1 — CRITICAL: FalkorDB Frozen (batch_ingest not running)
**Problem:** Graph stuck at 1570 nodes. Karma's long-term memory is not growing. The consciousness loop observes new episodes but cannot ingest them (OBSERVE-only by design). batch_ingest is the only path from ledger → FalkorDB.

**Impact:** Karma cannot recall sessions, decisions, or conversations from after the last manual batch run. Every /v1/chat query that pulls FalkorDB context is returning stale data.

**Fix:**
1. Run batch_ingest now: `docker exec -d karma-server sh -c 'LEDGER_PATH=/opt/seed-vault/memory_v1/ledger/memory.jsonl python3 /app/batch_ingest.py > /tmp/batch.log 2>&1'`
2. Verify: `ssh vault-neo "tail -f /tmp/batch.log"` and check node count after
3. Configure cron to auto-run (unlocks Blocker #3)

**Unlocks:** Blocker #3 (auto-schedule), and enables Karma to actually use recent memory.

---

### Blocker #2 — CRITICAL: No Conversation Capture Path
**Problem:** Chrome extension was shelved. No mechanism captures Colby↔Karma conversations into the ledger. The 1521 existing /v1/chat entries are from when hub-bridge was logging chats — unclear if that's still happening.

**Last /v1/chat entry:** 2026-03-03T18:22:33 — this may be a recent test or Karma still self-logging.

**What's needed:**
1. Verify: Is /v1/chat still writing to ledger? Check `ssh vault-neo "grep 'chat' /opt/seed-vault/memory_v1/ledger/memory.jsonl | tail -3 | python3 -c 'import sys,json; [print(json.loads(l).get(\"created_at\",\"?\")[:19], json.loads(l).get(\"content\",{}).get(\"user_message\",\"?\")[:60]) for l in sys.stdin]'"`
2. If yes: Verify what triggers it and document the capture path
3. If no: Design replacement — options: CLI wrapper for /v1/chat, karma-terminal revival, or server-side auto-log

**Unlocks:** Karma can actually learn from conversations (the entire point of the system).

---

### Blocker #3 — HIGH: No Auto-Schedule for batch_ingest
**Problem:** Even when batch_ingest runs successfully, without a scheduler the graph will freeze again within hours/days.

**Fix (after Blocker #1):**
```bash
ssh vault-neo "crontab -l > /tmp/ct && echo '0 */6 * * * docker exec karma-server sh -c \"LEDGER_PATH=/opt/seed-vault/memory_v1/ledger/memory.jsonl python3 /app/batch_ingest.py >> /tmp/batch.log 2>&1\"' >> /tmp/ct && crontab /tmp/ct"
```

**Unlocks:** Karma's memory grows continuously without manual intervention.

---

### Blocker #4 — MEDIUM: karma-server Restart Loop
**Problem:** `cycle: 1` on every LOG_GROWTH event indicates karma-server container restarts periodically. Metrics reset on restart. Cycle counter never advances past first active cycle.

**Impact:** Consciousness loop metrics unreliable. If restarting due to OOM or crash, stability risk.

**Fix:**
1. `ssh vault-neo "docker logs anr-karma-server --tail=50 2>&1 | grep -i 'exit\|error\|crash\|oom'"` — find restart cause
2. Fix root cause (OOM → reduce memory usage; crash → fix error; intentional → document)

**Unlocks:** Reliable consciousness loop metrics, stable awareness substrate.

---

### Blocker #5 — LOW: MODEL_DEEP gpt-5-mini vs gpt-4o-mini Drift
**Problem:** hub.env shows `MODEL_DEEP=gpt-5-mini` but docs and Decision #2 say gpt-4o-mini.

**Fix:**
1. Verify: `ssh vault-neo "grep MODEL_DEEP /opt/seed-vault/memory_v1/hub_bridge/config/hub.env"`
2. If gpt-5-mini: Is this intentional upgrade or typo? gpt-5-mini does not appear in OpenAI's public model list.
3. If typo: Correct to gpt-4o-mini and rebuild hub-bridge

**Unlocks:** Model configuration matches documentation.

---

## Blocker Dependency Chain

```
#1 batch_ingest fix
  → #3 auto-schedule (graph stays growing permanently)
    → Karma memory actually works (FalkorDB context in /v1/chat is current)

#2 conversation capture fix
  → Karma accumulates new knowledge from sessions
    → DPO preference pairs start accumulating
      → Fine-tuning becomes possible (20+ pairs needed)

#4 karma-server restart fix
  → Reliable consciousness loop
    → Accurate metrics for growth monitoring

#5 MODEL_DEEP drift fix
  → Documentation matches live system
    → No silent model surprises
```

---

## Key Decisions (Locked)

### Decision #1: Droplet Primacy (2026-02-23, LOCKED)
Droplet (vault-neo) is Karma's permanent home. K2 is a worker that syncs back. All state on droplet.

### Decision #2: Dual-Model Routing (2026-02-27, LOCKED)
GLM-4.7-Flash (primary, free via Z.ai) + gpt-4o-mini fallback for tool-calling. MODEL_DEFAULT=gpt-4o for persona quality.

### Decision #3: Consciousness Loop OBSERVE-Only (2026-02-28, LOCKED)
K2 consciousness loop does NOT autonomously call LLM. OBSERVE → rule-based DECIDE → LOG only. Verified in source code (zero LLM calls).

### Decision #4: GSD Workflow Adoption (2026-03-03, LOCKED)
GSD file structure adopted: PROJECT.md, REQUIREMENTS.md, STATE.md, ROADMAP.md, phase-CONTEXT/PLAN/SUMMARY per major feature.

### Decision #5: Honesty Contract (2026-03-03, RENEWED)
Brutal honesty always. Evidence before assertions. Never claim done without proof.

### Decision #6: Chrome Extension Shelved (2026-03-03, LOCKED)
Chrome extension never worked reliably. Removed from all documentation. Legacy ledger entries (750 claude, 436 openai, 68 gemini) are historical only. New capture path needed.

### Decision #7: PowerShell for Git Ops (2026-03-03, LOCKED)
Git Bash has persistent index.lock issue on Windows. All git operations via PowerShell.

---

## Progress Tracking

### Session 57 Accomplishments
- [x] Analyzed consciousness loop source — OBSERVE-only contract confirmed
- [x] Identified CYCLE_REFLECTION is a log type, not a behavioral mode (false drift)
- [x] Discovered FalkorDB frozen (batch_ingest not running)
- [x] Confirmed Chrome extension shelved — updated all docs
- [x] Updated architecture.md, MEMORY.md, STATE.md with verified state
- [ ] Run batch_ingest to unfreeze FalkorDB (Blocker #1)
- [ ] Verify conversation capture path (Blocker #2)
- [ ] Configure auto-schedule for batch_ingest (Blocker #3)

---

## Known Limitations
- **Chrome extension:** Shelved permanently (never worked)
- **batch_ingest:** Must be run manually until auto-schedule configured
- **K2 not online:** Consciousness loop runs on droplet only
- **No fine-tuning yet:** Need 20+ DPO preference pairs (blocked on conversation capture)
- **Ambient Tier 3:** Screen capture daemon not built

---

**Last updated:** 2026-03-03T19:30:00Z (Session 57)
**Owner:** Claude Code (writes on Colby approval)
**Canonical location:** C:\Users\raest\Documents\Karma_SADE\.gsd\STATE.md
