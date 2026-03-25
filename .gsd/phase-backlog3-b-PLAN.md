# Phase Backlog-3-B — P0-B FalkorDB Write Verification PLAN
**Created:** 2026-03-25 | **Session:** 145

## Tasks

### Task 1 — Read vesper_governor.py `_apply_to_spine()`
**What:** Understand current FalkorDB write logic — HTTP method, endpoint, error handling
<verify>
- vesper_governor.py: locate `_apply_to_spine()`, confirm it calls hub-bridge `/v1/cypher`
- Confirm no retry logic exists currently
</verify>
<done>[ ] governor write logic understood; current failure mode confirmed</done>

### Task 2 — Add retry queue to `_apply_to_spine()`
**What:** Wrap the HTTP POST in a retry loop: 3 attempts, 5s sleep between, log each failure
- On all 3 failures: write PITFALL entry to governor audit log
- On success on attempt 2 or 3: log recovery event
<verify>
- Syntax check: `python3 -c "import vesper_governor"` passes
- Dry-run: mock a 503 response, confirm 3 retry attempts appear in logs
</verify>
<done>[ ] retry queue live on K2 in vesper_governor.py</done>

### Task 3 — Verify end-to-end: trigger a promotion, confirm FalkorDB write with retry telemetry
**What:** Wait for governor cycle, check audit log for retry telemetry on next promotion
<verify>
- governor audit log shows promotion event with `"attempts": 1` (or higher if vault briefly unreachable)
- No silent failures — every promotion attempt is logged
</verify>
<done>[ ] P0-B verified — retry telemetry visible in governor audit log</done>
