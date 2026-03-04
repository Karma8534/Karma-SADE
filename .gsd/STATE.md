# STATE: Karma Peer — Decisions, Blockers, Progress

**Last updated:** 2026-03-04T15:00:00Z
**Session:** 60 (Post-Session-59 — All Blockers Resolved)
**Canonical source:** This file. Read at session start.

---

## Current Status (Verified 2026-03-04)

| Component | Status | Notes |
|-----------|--------|-------|
| **Consciousness Loop** | ✅ WORKING | 60s OBSERVE-only cycles. Zero LLM calls confirmed in source. RestartCount=0. |
| **Hub Bridge API** | ✅ WORKING | /v1/chat, /v1/ambient, /v1/context, /v1/cypher, /v1/ingest operational. |
| **Voice & Persona** | ✅ DEPLOYED | Peer-level voice verified. gpt-4o-mini confirmed (MODEL_DEEP verified 2026-03-04). |
| **FalkorDB Graph** | ✅ FULLY CAUGHT UP | 3621 nodes (3049 Episodic + 571 Entity + 1 Decision). batch_ingest cron every 6h. |
| **Ledger** | ✅ GROWING | 4000+ entries. Git commits + session-end hooks capturing actively. |
| **Work-Loss Prevention** | ✅ GATES LIVE | Pre-commit hook + session-end hook both active and verified. |
| **Ambient Tier 1 Hooks** | ✅ WORKING | Git + session-end captures verified in ledger. |
| **Ambient Tier 2 Endpoint** | ✅ DEPLOYED | /v1/context endpoint working. |
| **GSD File Structure** | ✅ ADOPTED | All .gsd/ files in place and being used. |
| **Chrome Extension** | ❌ SHELVED | Never worked reliably. Legacy data only. |
| **Conversation Capture** | ✅ WORKING | All 3049 hub/chat episodes ingested via --skip-dedup. |
| **batch_ingest Schedule** | ✅ CONFIGURED | Cron every 6h on vault-neo. --skip-dedup mode. |
| **karma-server image** | ✅ REBUILT | All session-58/59 fixes baked in. |
| **OpenAI API key** | ✅ SECURED | File-based read (mounted volume), not env var (docker inspect clean). |
| **PDF Watcher** | ✅ WORKING | Rate-limit backoff + jam notification + time-window scheduling. |

---

## Active Blockers

**None.** All 5 blockers resolved as of sessions 58–59.

### ✅ Blocker #1 — RESOLVED (2026-03-03): FalkorDB Unfrozen
LEDGER_PATH corrected to `/ledger/memory.jsonl`. Graph grew from 1570 → 1642 nodes. Cron configured.

### ✅ Blocker #2 — RESOLVED (2026-03-03): hub/chat entries reach FalkorDB
batch_ingest.py extended for hub/chat tags + assistant_text fallback. 1538 conversations ingested.

### ✅ Blocker #3 — RESOLVED (2026-03-03): Auto-Schedule Configured
Cron: `0 */6 * * *` on vault-neo, `--skip-dedup` mode.

### ✅ Blocker #4 — RESOLVED (2026-03-03, verified 2026-03-04): karma-server Restart Loop
Root cause was gpt-5-mini model reference (bad model name). Fixed in session 58. RestartCount=0 confirmed.

### ✅ Blocker #5 — RESOLVED (verified 2026-03-04): MODEL_DEEP Drift
`grep MODEL_DEEP hub.env` → `gpt-4o-mini`. Matches Decision #2. Not a typo.

---

## Key Decisions (Locked)

### Decision #1: Droplet Primacy (2026-02-23, LOCKED)
Droplet (vault-neo) is Karma's permanent home. K2 is a worker that syncs back. All state on droplet.

### Decision #2: Dual-Model Routing (2026-02-27, LOCKED)
GLM-4.7-Flash (primary, ~80%) + gpt-4o-mini fallback (~20%). Verified MODEL_DEEP=gpt-4o-mini on 2026-03-04.

### Decision #3: Consciousness Loop OBSERVE-Only (2026-02-28, LOCKED)
K2 consciousness loop does NOT autonomously call LLM. OBSERVE → rule-based DECIDE → LOG only.

### Decision #4: GSD Workflow Adoption (2026-03-03, LOCKED)
GSD file structure adopted: PROJECT.md, REQUIREMENTS.md, STATE.md, ROADMAP.md, phase-CONTEXT/PLAN/SUMMARY per major feature.

### Decision #5: Honesty Contract (2026-03-03, RENEWED)
Brutal honesty always. Evidence before assertions. Never claim done without proof.

### Decision #6: Chrome Extension Shelved (2026-03-03, LOCKED)
Chrome extension never worked reliably. Removed from all documentation.

### Decision #7: PowerShell for Git Ops (2026-03-03, LOCKED)
Git Bash has persistent index.lock issue on Windows. All git operations via PowerShell.

### Decision #8: --skip-dedup is Standard batch_ingest Mode (2026-03-03, LOCKED)
Graphiti dedup queries time out at scale (85% error rate). Direct Cypher write via --skip-dedup: 899 eps/s, 0 errors. Cron uses --skip-dedup by default.

### Decision #9: OpenAI API Key File-Based (2026-03-03, LOCKED)
API key read from mounted volume file, not injected as env var. docker inspect stays clean.

---

## Session History

### Session 57 Accomplishments
- FalkorDB unfrozen (Blocker #1)
- hub/chat entries now reach FalkorDB (Blocker #2)
- Cron configured every 6h (Blocker #3)
- GSD docs updated

### Session 58 Accomplishments
- OpenAI API key secured (file-based, not env var)
- karma-server restart loop fixed (gpt-5-mini → gpt-4o-mini)
- GLM rate-limit handling redesigned (throttle, never paid fallback)
- karma-server image rebuilt with all fixes
- K2 sync worker deprecated
- 10 stale remote branches deleted
- compose credentials externalized

### Session 59 Accomplishments
- --skip-dedup added to batch_ingest (899 eps/s, 0 errors)
- FalkorDB datetime() fix (ISO strings only, no datetime() function)
- OPENAI_API_KEY env propagation fixed (os.environ.setdefault())
- Full backfill complete: 3049 episodes ingested (was 1749)
- karma-server image rebuilt with all fixes
- Cron updated to --skip-dedup

---

## Known Limitations
- **Chrome extension:** Shelved permanently
- **K2 not online:** Consciousness loop runs on droplet only
- **No fine-tuning yet:** Need 20+ DPO preference pairs (accumulation in progress)
- **Ambient Tier 3:** Screen capture daemon not built
- **direction.md:** STALE — last updated 2026-02-23 (>7 days). Needs refresh to reflect sessions 57–59 reality.
- **ChromaDB:** Vector index not recently updated

---

## Next Session Agenda (Session 60)

System is in maintenance/growth mode. No urgent fixes. Possible work:
1. **direction.md refresh** — 9 days stale, doesn't reflect post-session-59 state. Karma reads this.
2. **ChromaDB reindex** — vector search index stale (low priority)
3. **DPO preference pair accumulation** — needs 20+ pairs to start fine-tuning
4. **Ambient Tier 3** — screen capture daemon (not started)

---

**Last updated:** 2026-03-04T15:00:00Z (Session 60)
**Owner:** Claude Code (writes on Colby approval)
**Canonical location:** C:\Users\raest\Documents\Karma_SADE\.gsd\STATE.md
