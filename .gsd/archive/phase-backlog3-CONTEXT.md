# Phase Backlog-3 — P0 Vesper Pipeline Improvements CONTEXT
**Created:** 2026-03-25 | **Session:** 144 wrap pre-create

## What We're Solving

The Vesper self-improvement pipeline (watchdog → evaluator → governor) is live and functional, but has known behavioral gaps that limit the quality of pattern extraction and spine evolution.

## P0-A: Watchdog Pattern Diversity

**Problem:** vesper_watchdog.py currently detects only `cascade_performance` type patterns. All spine stable patterns are `cascade_performance`. The governor can only write what the watchdog finds. Result: spine accumulates one-dimensional behavioral data.

**What:** Expand watchdog to detect at least 3–4 pattern types:
- `cascade_performance` (already works — keep)
- `decision_quality` — tracks when CC makes a decision (DECISION/PROOF tags in bus)
- `error_recovery` — detects PITFALL + fix pair within a session
- `tool_usage` — detects which tools are called and with what success rate

**Files to read:**
- K2: `/mnt/c/dev/Karma/k2/aria/vesper_watchdog.py`
- K2: `/mnt/c/dev/Karma/k2/cache/cc_identity_spine.json` (see current stable patterns)

## P0-B: FalkorDB Write Verification

**Problem:** vesper_governor.py writes patterns to FalkorDB via hub-bridge `/v1/cypher`. No retry on failure. If vault-neo is momentarily unreachable, the write silently drops.

**What:** Add configurable retry queue (3 attempts, 5s backoff) to governor's `_apply_to_spine()`.

## Scope for This Phase

Start with P0-A only. P0-B through P0-G are separate tasks — sequence after P0-A verified.

## What We're NOT Doing

- Not changing the evaluator or governor logic (just the watchdog input)
- Not adding new pattern types to the governor schema (watchdog outputs existing schema)
- Not touching hub-bridge or vault-neo for P0-A
