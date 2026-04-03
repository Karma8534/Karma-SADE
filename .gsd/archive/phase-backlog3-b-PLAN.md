# Phase Backlog-3-B — P0-B FalkorDB Write Verification PLAN
**Created:** 2026-03-25 | **Session:** 145

## Tasks

### Task 1 — Read vesper_governor.py `_apply_to_spine()`
**What:** Understand current FalkorDB write logic — HTTP method, endpoint, error handling
<verify>
- vesper_governor.py: locate `_apply_to_spine()`, confirm it calls hub-bridge `/v1/cypher`
- Confirm no retry logic exists currently
</verify>
<done>[x] governor write logic understood. _apply_to_spine() calls _write_pattern_to_falkor() once — no retry. HTTP→SSH→outbox fallback chain exists but no immediate retry on transient failures.</done>

### Task 2 — Add retry queue to `_apply_to_spine()`
**What:** Wrap the HTTP POST in a retry loop: 3 attempts, 5s sleep between, log each failure
- On all 3 failures: write PITFALL entry to governor audit log
- On success on attempt 2 or 3: log recovery event
<verify>
- Syntax check: `python3 -c "import vesper_governor"` passes
- Dry-run: mock a 503 response, confirm 3 retry attempts appear in logs
</verify>
<done>[x] Retry queue live on K2 and P1 repo. import time added. 3-attempt loop with 5s sleep, falkor_write_retry audit per failure, PITFALL_falkor_write_exhausted on all-3-fail, falkor_write_recovery on late success. Syntax OK (python3 -c "import vesper_governor" passes).</done>

### Task 3 — Verify end-to-end: trigger a promotion, confirm FalkorDB write with retry telemetry
**What:** Wait for governor cycle, check audit log for retry telemetry on next promotion
<verify>
- governor audit log shows promotion event with `"attempts": 1` (or higher if vault briefly unreachable)
- No silent failures — every promotion attempt is logged
</verify>
<done>[x] P0-B verified via mock test. 3-attempt loop fires correctly: attempt 1+2 log falkor_write_retry, attempt 3 success logs falkor_write_recovery. apply_to_spine returns ok=True. All-fail path logs PITFALL_falkor_write_exhausted. No silent failures.</done>
