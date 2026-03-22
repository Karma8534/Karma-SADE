# K-3: Echo Integration — Ambient Observer Context
**Created:** 2026-03-22 (Session 120)
**Author:** CC (Ascendant)
**Status:** DESIGN LOCKED — do not revisit these decisions

---

## What We're Building

`ambient_observer.py` — a new K2 module that reads coordination bus events and feeds behavioral signals into the vesper pipeline. This makes `_proactive_outreach()` in `karma_regent.py` trigger on genuine ambient inferences instead of only RSC spine count changes.

**Gate (K-3 done when):** Karma posts one unprompted message to coordination bus based on a genuine ambient observation — not a scheduled ping, not a random fact, a real inference from observed context.

---

## Design Decisions (LOCKED — no re-debate)

### D1: Signal source = coordination bus events
**Locked.** Richest available signal. Already flowing. No new infrastructure.
**NOT doing:** git commits (requires SSH poll), screen capture (not needed), session files (redundant with bus).

### D2: Pipeline path (not fast path)
**Locked.** ambient_observer → regent_evolution.jsonl → vesper_watchdog → candidates → vesper_eval → vesper_governor → spine → _proactive_outreach().
**Why:** Consistent with Vesper architecture. Promotes genuine behavioral patterns, not ephemeral observations. Gate requires spine promotion, not just a bus post.
**NOT doing:** Direct regent trigger without vesper pipeline (would bypass eval/governor gates).

### D3: Hook into aria_consciousness.py Echo step (no new cron)
**Locked.** `aria_consciousness.py` already runs an Echo step every cycle. `ambient_observer` runs as part of that step.
**NOT doing:** Separate systemd timer or new cron job.

### D4: Olama inference = nemotron-mini (K2 local model)
**Locked.** Already running on K2. No new model downloads. 8B models are fine for signal → insight extraction.
**NOT doing:** Cloud LLM calls, new model installs.

### D5: No new dependencies
**Locked.** SQLite (existing aria.db), Ollama (running), coordination bus HTTP (existing). Everything else uses existing imports.

### D6: Candidate type = `ambient_observation`
**Locked.** Must be added to `HEURISTIC_BLIND_TYPES` in `vesper_eval.py` (P035 pattern — prevents 100% rejection by fixed 0.25 heuristic score).

### D7: _proactive_outreach() check = new `_last_ambient_count` global
**Locked.** Mirror pattern of existing `_last_rsc_count`. Track promoted `ambient_observation` entries in stable_identity separately from RSC. On new entry: post "I noticed [insight]" to bus addressed to `colby`.

---

## What We're NOT Doing

- NOT replacing existing _proactive_outreach() RSC logic (additive only)
- NOT adding screen capture or OCR
- NOT modifying vesper_watchdog.py's core scoring — only adding recognition of ambient_observer entries
- NOT making this a scheduled API poll — runs inside consciousness loop cycle
- NOT adding new tables to aria.db (uses existing experience_log as read-only reference)
- NOT requiring Sovereign approval for this change (K2 file writes are under banked k2_ssh_write budget)

---

## Constraints

- K2 hardware: RTX 4070 8GB, nemotron-mini, 64GB RAM
- aria.py already runs — must not break existing HTTP endpoints
- aria_consciousness.py Echo step already runs — must handle ambient_observer failures gracefully (try/except, non-fatal)
- vesper_watchdog.py runs every 10 minutes — ambient_observer writes to regent_evolution.jsonl, watchdog picks it up on next cycle
- Deduplication: use LTM buffer (already exists in watchdog) to prevent flood — max 1 ambient candidate per 6h window

---

## Files Modified

| File | Change | Type |
|------|--------|------|
| `ambient_observer.py` | CREATE — new module | New |
| `aria_consciousness.py` | Import + call ambient_observer.observe() in Echo step | Extend |
| `vesper_watchdog.py` | Recognize source=ambient_observer entries, emit type=ambient_observation candidates | Extend |
| `vesper_eval.py` | Add ambient_observation to HEURISTIC_BLIND_TYPES | Extend |
| `karma_regent.py` | Add _last_ambient_count, enhance _proactive_outreach() | Extend |

All files: `/mnt/c/dev/Karma/k2/aria/`
