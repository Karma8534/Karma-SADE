# Phase Ascendance 1 Context — Design Decisions (Persona-on-Boot)

Date: 2026-04-18
Workspace: C:\Users\raest\Documents\Karma_SADE
Scope: Locked decisions for Phase 1 only
Sovereign approval: Colby (Session 171)

---

## DESIGN DECISION #1: Source of Truth for Persona Identity

**Where it lives:**
- **Primary source:** K2 `/mnt/c/dev/Karma/k2/cache/vesper_identity_spine.json` (dynamic persona)
- **Fallback source:** `Memory/00-karma-system-prompt-live.md` (vault-neo, canonical defaults)
- **Runtime representation:** `cc_identity_spine.json` on P1 (synced from K2, 5min TTL)

Boot must: show source chosen (K2 cache hit / vault fallback / offline→defaults).

---

## DESIGN DECISION #2: Source of Truth for Session History

**Where it lives:**
- **Primary source:** `GET /v1/session/{session_id}` (P1 server, in-memory)
- **Fallback source:** `GET /memory/session` (vault ledger query)
- **Proof source:** Vault ledger entries with `session_id` (immutable audit trail)

Boot must: fetch in parallel, log endpoint + turn_ids + count + timestamps.

---

## DESIGN DECISION #3: Frontend Boot Hydration Architecture

**Phases:**
1. DOMContentLoaded → blank frame with spinner
2. Parallel fetch: /memory/wakeup, /v1/session/{id}, /memory/session, cc_identity_spine
3. Select persona: K2 spine → vault defaults → generic Karma
4. Paint: persona + last 3 turns (or fewer)
5. Interactive: chat input ready

**Constraints:**
- No sequential waits (all parallel)
- No fake data (degrade gracefully only)
- Paint after all fetches complete
- Total paint < 2000ms from DOMContentLoaded

---

## DESIGN DECISION #4: Persona Identity Rendering

**What renders:**
- Name: "Karma" (static)
- Status: [ONLINE] if K2 reachable, [OFFLINE] if vault fallback
- Line: one-sentence from spine["philosophy"] or vault defaults
- Example: "[ONLINE] I am Karma. Reasoning rooted in persistent spine."

**Not rendered:** Model choice, user name, stats, avatar, voice.

Boot trace must show: exact rendered text + source (K2 spine path or vault path).

---

## DESIGN DECISION #5: Deterministic Last 3 Turns

**Algorithm:**
1. Fetch turns from /v1/session or /memory/session
2. If < 3: return all turns
3. If >= 3: return turns.slice(-3) (newest last)
4. Sort by timestamp ascending (oldest first in display)
5. Include turn_id + timestamp in DOM

MUST be deterministic. Boot trace must log: turns.length, slice operation, final count, each turn_id.

---

## DESIGN DECISION #6: Fallback Degradation Levels

**Level 1:** K2 spine [ONLINE] + 3 turns from /v1/session, paint < 2000ms
**Level 2:** K2 spine [ONLINE] + "History unavailable", paint < 2000ms
**Level 3:** vault defaults [OFFLINE] + 3 turns from /memory/session, paint < 2500ms
**Level 4:** "Karma" + defaults, no history, paint < 500ms, UI: "Offline mode"

Hard constraint: NEVER render fake data or placeholders.

Boot trace must show: level achieved, why (timeout/404/success), paint_ms.

---

## DESIGN DECISION #7: Timing Instrumentation

**Metrics (no persistence):**
- window.karmaBootStart (DOMContentLoaded)
- window.karmaFetchStart (parallel fetch begins)
- window.karmaFetchEnd (Promise.all resolved)
- window.karmaPaintMs (persona+history painted)
- window.karmaRenderSource ("k2_spine" | "vault_defaults" | "offline")
- window.karmaHistorySource ("v1_session" | "memory_session" | "none")

Storage: window.karma* only. No localStorage/ledger/vault.
Exposure: window.karmaBootMetrics() → {startMs, fetchMs, paintMs, source, ...}

---

## DESIGN DECISION #8: Exception Handling

- Timeouts → treat as 404, move to fallback (no retry)
- Network error → log, fallback
- Parse error → log, fallback
- 5xx → log, fallback
- 404 /v1/session → normal (new), try /memory/session

No retry loops. Fail fast, degrade gracefully.

Boot trace must log: exception type, endpoint, fallback chosen.

---

## DESIGN DECISION #9: Canonical Endpoints (No New)

Persona: GET /memory/wakeup (if exists), fallback K2/vault
History: GET /v1/session/{id} (primary), GET /memory/session (fallback)
Optional: GET /v1/runtime/truth (offline detection)
Optional: GET http://127.0.0.1:37782/search (claude-mem, Phase 2)

If /memory/wakeup or /v1/runtime/truth missing: bootstrap without them.

---

## DESIGN DECISION #10: Success Criteria

**PASS requires:**
1. Boot persona renders < 2000ms
2. Persona source visible in boot trace (K2 or vault)
3. Last 3 turns (or fewer) render with turn_ids
4. Degradation level correct (no fake data)
5. All 4 evidence files exist + committed

**FAIL if:**
- Any fake persona or placeholder data
- Paint > 2000ms without reason
- Boot trace missing endpoint/fallback info
- Evidence files incomplete/contradictory

**Retry limit:** 3 full attempts max.

---

## LOCKED DECISIONS

| # | Decision | Implication |
|---|----------|------------|
| 1 | K2 spine primary, vault fallback | Boot trace shows source |
| 2 | /v1/session primary, /memory/session fallback | Parallel fetch |
| 3 | Parallel fetch + serial paint | Max 2000ms |
| 4 | Name + status + one-liner only | No avatar/voice Phase 1 |
| 5 | Deterministic last-3 | Reproducible turns |
| 6 | Degrade to Level 4 (no fake) | Hard constraint |
| 7 | Window-scoped metrics | No state pollution |
| 8 | Fail fast, no retries | Move to fallback |
| 9 | No new endpoints | Use existing only |
| 10 | 4 evidence files = PASS | Proof-based |

---

## Ready to Code

Implement Task 1 per phase-ascendance-1-PLAN.md:
"Build deterministic boot hydration path (frontend)."

All design decisions locked.
