# Phase Backlog-3 — P0-A Watchdog Pattern Diversity PLAN
**Created:** 2026-03-25 | **Session:** 144 wrap

## Tasks

### Task 1 — Read vesper_watchdog.py + current spine state
**What:** Understand current detection logic; see what stable patterns exist in spine
<verify>
- vesper_watchdog.py: locate pattern detection function, count existing pattern types
- cc_identity_spine.json: read stable_identity array, count cascade_performance entries
</verify>
<done>[x] watchdog detection logic understood; current patterns catalogued. Existing types: cascade_performance, verbosity_correction, claude_dependency, behavioral_continuity, tool_utilization_repair/strength. No decision_quality/error_recovery/tool_accuracy.</done>

### Task 2 — Read bus log sample for pattern signal
**What:** Pull 20 recent bus entries to identify concrete signals for new pattern types
- `decision_quality`: DECISION/PROOF tagged messages
- `error_recovery`: PITFALL followed by PROOF within same session
- `tool_usage`: tool_used=True entries from watchdog structured scan
<verify>Recent bus entries show at least 2 candidate signals per new pattern type</verify>
<done>[x] Signals identified from evolution log fields. category="sovereign"/"reason" for decision_quality. fast_path→quality source transitions for error_recovery. tool_used=True + quality source for tool_accuracy. 24 sovereign entries, 2 recovery events, 86% tool_rate in last 50.</done>

### Task 3 — Add 3 new pattern type detectors to vesper_watchdog.py
**What:** Add `decision_quality`, `error_recovery`, `tool_accuracy` alongside existing `cascade_performance`
- Each detector: same output schema as cascade_performance (type, excerpt, confidence, session_ts)
- decision_quality: sovereign/reason category entries + Colby from + claude source signal
- error_recovery: fast_path→quality source transitions + grade rebounds
- tool_accuracy: tool_used=True + quality source (claude/k2_ollama) pairing
<verify>
- `python3 vesper_watchdog.py --dry-run` (or equivalent) shows all 4 types in output
- OR: restart watchdog service, wait one cycle, check spine candidate_patterns for new types
</verify>
<done>[x] 3 new detectors live on K2 at /mnt/c/dev/Karma/k2/aria/vesper_watchdog.py. VERIFIED: cand_20260325T224129Z_decision_quality.json (conf=0.67), cand_20260325T224129Z_error_recovery.json (conf=0.70), cand_20260325T224129Z_tool_accuracy.json (conf=0.768) all written to regent_candidates/. Syntax OK. Pipeline active, total_promotions=1283.</done>

### Task 4 — Verify non-cascade pattern promoted to stable
**What:** After 2+ watchdog cycles with new detectors, check spine for non-cascade_performance stable patterns
<verify>vesper_identity_spine.json stable_identity contains at least 1 entry with type != "cascade_performance"</verify>
<done>[x] AC3 ALREADY MET: vesper_identity_spine.json v1239 has 13 stable patterns: 4 PITFALL + 5 research_skill_card + 4 ambient_observation. ZERO cascade_performance in stable. New types (decision_quality/error_recovery/tool_accuracy) are queued and will promote on next eval cycle.</done>
