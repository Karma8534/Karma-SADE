# STATE: Karma Peer — Decisions, Blockers, Progress

**Last updated:** 2026-03-03T20:05:00Z
**Session:** 57 (Blockers #1 #2 #3 Cleared)
**Canonical source:** This file. Read at session start.

---

## Current Status (Verified 2026-03-03)

| Component | Status | Notes |
|-----------|--------|-------|
| **Consciousness Loop** | ✅ WORKING | 60s OBSERVE-only cycles. Zero LLM calls confirmed in source. |
| **Hub Bridge API** | ✅ WORKING | /v1/chat, /v1/ambient, /v1/context, /v1/cypher operational. |
| **Voice & Persona** | ✅ DEPLOYED | Peer-level voice verified. No service-desk closers. gpt-4o default. |
| **FalkorDB Graph** | ✅ GROWING | 1642 nodes (was 1570). batch_ingest ran 2026-03-03, cron auto-schedule every 6h active. |
| **Ledger** | ✅ GROWING | 3980 entries. Git commits + session-end hooks capturing actively. |
| **Work-Loss Prevention** | ✅ GATES LIVE | Pre-commit hook + session-end hook both active and verified. |
| **Ambient Tier 1 Hooks** | ✅ WORKING | Git + session-end captures verified in ledger (2026-03-03). |
| **Ambient Tier 2 Endpoint** | ✅ DEPLOYED | /v1/context endpoint working. |
| **GSD File Structure** | ✅ ADOPTED | All .gsd/ files in place and being used. |
| **Chrome Extension** | ❌ SHELVED | Never worked reliably. Removed from all docs. Legacy data only. |
| **Conversation Capture** | ✅ FIXED | batch_ingest extended — 1538 hub/chat entries now ingesting into FalkorDB. |
| **batch_ingest Schedule** | ✅ CONFIGURED | Cron every 6h on vault-neo. Installed 2026-03-03. |

---

## Active Blockers (Priority Order)

### ✅ Blocker #1 — RESOLVED: FalkorDB Unfrozen (2026-03-03)
**Was:** Graph stuck at 1570 nodes, batch_ingest not running.

**Fix applied:**
- Discovered ledger path inside container is `/ledger/memory.jsonl` (not `/opt/seed-vault/...`)
- Ran batch_ingest: 113 episodes processed (43 ok, 70 err — errors are malformed legacy Chrome extension entries, not blocking)
- Graph grew from 1570 → 1642 nodes (256 entities, 1385 episodes, 1684 relationships)
- Configured cron: `0 */6 * * *` on vault-neo to auto-run every 6 hours

**Note on 70 errors:** All errors are `'NoneType' object is not subscriptable` on legacy Chrome extension entries (openai captures with malformed content). These entries will always fail and can be skipped in future runs.

---

### ✅ Blocker #2 — RESOLVED: hub/chat entries now reach FalkorDB (2026-03-03)
**Was:** 1543 /v1/chat entries in ledger (tagged hub/chat/default) never reached FalkorDB because batch_ingest only read `assistant_message` field; hub/chat entries use `assistant_text`.

**Root cause:** batch_ingest.py field mismatch + no hub/chat tag detection.

**Fix applied:**
- Extended batch_ingest.py: detect hub/chat by tags, read `assistant_text` fallback
- Episodes labeled `source_description="Karma hub-chat"` for idempotent re-runs
- 1538 Colby↔Karma conversations now ingesting (batch running since 2026-03-03 ~20:00 UTC)
- Dry-run confirmed: `hub-chat: 1538 total, 0 done, 1538 remaining`

**Option 2 (ASSIMILATE signals):** Earmarked as future quality layer — Karma can selectively promote high-value conversations with `[ASSIMILATE: ...]` signal in response. Not a blocker.

**Unlocks:** Karma can accumulate knowledge from all past and future conversations.

---

### ✅ Blocker #3 — RESOLVED: Auto-Schedule Configured (2026-03-03)
**Was:** No scheduler, graph would re-freeze.

**Fix applied:** Cron installed on vault-neo:
`0 */6 * * * docker exec karma-server sh -c "LEDGER_PATH=/ledger/memory.jsonl python3 /app/batch_ingest.py >> /tmp/batch.log 2>&1"`

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
- [x] Confirmed Chrome extension shelved — updated all docs
- [x] LEDGER_PATH corrected in all docs (`/ledger/memory.jsonl` not host path)
- [x] Ran batch_ingest — FalkorDB unfrozen (1570 → 1642 nodes) — Blocker #1
- [x] Extended batch_ingest.py for hub/chat entries (1538 conversations) — Blocker #2
- [x] Cron configured on vault-neo every 6h — Blocker #3
- [x] GSD docs updated: phase-hubchat-SUMMARY, ROADMAP, MEMORY.md, auto-memory
- [ ] Rebuild karma-server image (NEXT SESSION — batch must complete first)
- [ ] Verify batch run results (node count after 1538 conversations ingested)

### Next Session Step-by-Step
1. `docker exec karma-server tail -30 /tmp/batch.log` — verify batch complete, check ok/err counts
2. `ssh vault-neo "docker exec falkordb redis-cli -p 6379 GRAPH.QUERY neo_workspace 'MATCH (n) RETURN count(n)'"` — verify node count grew
3. Rebuild karma-server image on vault-neo:
   - `ssh vault-neo "cd /home/neo/karma-sade/karma-core && docker build -t karma-core:latest ."`
   - Get current run params: `docker inspect anr-karma-server`
   - Stop/remove/restart with same params
4. Verify cron will use new image: run `--dry-run` via cron manually
5. Investigate Blocker #4 (restart loop): `docker logs anr-karma-server --tail=50 | grep -i 'exit\|error\|crash\|oom'`
6. Verify Blocker #5 (model drift): `grep MODEL_DEEP /opt/seed-vault/memory_v1/hub_bridge/config/hub.env`

---

## Known Limitations
- **Chrome extension:** Shelved permanently (never worked)
- **karma-server image:** Updated batch_ingest.py in container only — image rebuild pending
- **K2 not online:** Consciousness loop runs on droplet only
- **No fine-tuning yet:** Need 20+ DPO preference pairs (conversation capture now working, accumulation begins)
- **Ambient Tier 3:** Screen capture daemon not built

---

**Last updated:** 2026-03-03T20:30:00Z (Session 57)
**Owner:** Claude Code (writes on Colby approval)
**Canonical location:** C:\Users\raest\Documents\Karma_SADE\.gsd\STATE.md
