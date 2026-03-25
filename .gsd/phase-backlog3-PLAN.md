# Phase Backlog-3 — P0-A Watchdog Pattern Diversity PLAN
**Created:** 2026-03-25 | **Session:** 144 wrap

## Tasks

### Task 1 — Read vesper_watchdog.py + current spine state
**What:** Understand current detection logic; see what stable patterns exist in spine
<verify>
- vesper_watchdog.py: locate pattern detection function, count existing pattern types
- cc_identity_spine.json: read stable_identity array, count cascade_performance entries
</verify>
<done>[ ] watchdog detection logic understood; current patterns catalogued</done>

### Task 2 — Read bus log sample for pattern signal
**What:** Pull 20 recent bus entries to identify concrete signals for new pattern types
- `decision_quality`: DECISION/PROOF tagged messages
- `error_recovery`: PITFALL followed by PROOF within same session
- `tool_usage`: tool_used=True entries from watchdog structured scan
<verify>Recent bus entries show at least 2 candidate signals per new pattern type</verify>
<done>[ ] signal candidates identified</done>

### Task 3 — Add 3 new pattern type detectors to vesper_watchdog.py
**What:** Add `decision_quality`, `error_recovery`, `tool_usage` alongside existing `cascade_performance`
- Each detector: same output schema as cascade_performance (type, excerpt, confidence, session_ts)
- decision_quality: look for [DECISION] or [PROOF] prefixes in structured entries
- error_recovery: find PITFALL + subsequent fix evidence in same scan window
- tool_usage: count tool_used=True vs False ratio, flag sessions with high tool accuracy
<verify>
- `python3 vesper_watchdog.py --dry-run` (or equivalent) shows all 4 types in output
- OR: restart watchdog service, wait one cycle, check spine candidate_patterns for new types
</verify>
<done>[ ] 3 new pattern detectors live on K2</done>

### Task 4 — Verify non-cascade pattern promoted to stable
**What:** After 2+ watchdog cycles with new detectors, check spine for non-cascade_performance stable patterns
<verify>cc_identity_spine.json stable_identity contains at least 1 entry with type != "cascade_performance"</verify>
<done>[ ] AC3 criterion approaching — non-cascade pattern visible in spine</done>
