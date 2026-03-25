# Phase Backlog-3-B — P0-B FalkorDB Write Verification CONTEXT
**Created:** 2026-03-25 | **Session:** 145

## What We're Solving

vesper_governor.py writes promoted patterns to FalkorDB via hub-bridge `/v1/cypher`. No retry on failure. If vault-neo is momentarily unreachable, the write silently drops — pattern is lost, no error logged, no re-attempt.

## P0-B: FalkorDB Write Verification

**Problem:** `_apply_to_spine()` in vesper_governor.py makes a single HTTP POST to hub-bridge `/v1/cypher`. Fire-and-forget. If the request fails (timeout, 502, network blip), the promotion is silently discarded. Pattern was evaluated, approved, but never stored.

**What:** Add configurable retry queue (3 attempts, 5s backoff) to governor's `_apply_to_spine()`.

**Files to read:**
- K2: `/mnt/c/dev/Karma/k2/aria/vesper_governor.py` — locate `_apply_to_spine()`, understand current write logic

## What We're NOT Doing

- Not changing the watchdog or evaluator
- Not changing the FalkorDB schema
- Not adding retry to other endpoints (only `_apply_to_spine`)
- Not adding persistent disk queue (in-memory retry is sufficient)

## Architecture Decisions

- 3 retries max, 5s between attempts (low enough to not block governor cycle, high enough to handle transient failures)
- Log each retry attempt with attempt number + error
- If all 3 fail: log PITFALL-level error, write to governor audit log (already exists at regent_governor_audit.jsonl)
- No silent failures — every failed promotion must be logged
