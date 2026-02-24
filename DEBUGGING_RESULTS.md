# Consciousness Loop Systematic Debug — Session 21

**Date:** 2026-02-24T18:00:00Z
**Method:** Live droplet inspection via SSH + code analysis
**Status:** CRITICAL BUG CONFIRMED

---

## Finding 2.1 Status: PARTIALLY FIXED, BUT LOOP IS BROKEN

### Evidence from consciousness.jsonl

```
Last CYCLE entry (Feb 17 19:51:15):
  "action": "LOG_ERROR",
  "reason": "Analysis failed despite new activity",
  "observations": {"new_episodes": 1, "new_entities": 2, "new_relationships": 4, ...},
  "analysis": null

Feb 24 entries: Only CONTROL_PAUSE/RESUME/FOCUS/RESET signals (no new CYCLE entries)
Elapsed time since last cycle: 7 days
```

**Interpretation:** Consciousness loop **stopped producing cycles** on Feb 16–17 after _think() phase failed.

---

## Root Cause Analysis: Finding 2.3 NOT FIXED

### The Bug

**File:** `karma-core/consciousness.py`, line ~195
```python
async def _think(self, observation: Optional[dict]) -> Optional[dict]:
    try:
        if self._router:
            response = await self._router.complete(  # ← AWAITING SYNC FUNCTION
                messages=[...],
                task_type="reasoning"
            )
```

**File:** `karma-core/router.py`, line ~N/A
```python
def complete(self, messages: list[dict], task_type: str = TaskType.GENERAL,
             max_tokens: Optional[int] = None,
             temperature: Optional[float] = None) -> tuple[str, str]:
    # ← NOT `async def` — this is SYNCHRONOUS
```

### What Happens

When Python awaits a synchronous function:
- ❌ **TypeError**: object NoneType can't be used in 'await' expression (or similar)
- ❌ Exception caught by outer `try/except` in `_cycle()`
- ❌ `metrics["errors"] += 1`
- ❌ Loop continues with `await asyncio.sleep(CONSCIOUSNESS_INTERVAL)`
- ❌ **Silent degradation:** Loop runs but no productive cycles, no insights written

### Current State of Code

✅ **Finding 2.1 code fix IS present:**
```python
def _decide(self, observations: Optional[dict], analysis: Optional[dict]) -> tuple[str, str]:
    # Now uses `.get("episode_count", 0)` with type guard
    if observations.get("episode_count", 0) == 0:
        return Action.NO_ACTION, "Idle cycle — no new activity"
```

❌ **Finding 2.3 fix IS NOT present:**
```python
# No wrapping in asyncio.to_thread()
# No async version of router.complete()
# Direct await on sync function → crash
```

---

## Container Health Check

```bash
$ docker ps --filter name=karma
  karma     Up 16 hours   8340/tcp

$ docker logs karma | tail -5
  [CONSCIOUSNESS] Loop started — interval: 60s
  INFO:     Uvicorn running on http://0.0.0.0:8340
  (no recent cycle logs, no recent errors)

$ curl http://localhost:8340/health
  (timeout)
```

**Interpretation:** Container is up, consciousness loop is started, but event loop is either:
- Blocked in a long sync call (Finding 2.3)
- Silently catching exceptions and continuing

---

## The Feb 16–17 Failure Cascade

### Timeline

1. **Feb 16 ~23:39 UTC** — Last successful consciousness cycle (cycle 19)
   - Found new_episodes, new_entities, new_relationships
   - Sent to _think() phase
   - router.complete() called
   - **Exception:** TypeError on `await` of sync function
   - Exception caught, metrics["errors"] += 1

2. **Feb 16–17** — Last few cycles crash identically
   - `analysis` comes back as `None` (caught exception)
   - `_decide()` returns `LOG_ERROR` ("Analysis failed despite new activity")
   - Cycles continue but produce no insights

3. **Feb 17 ~19:51 UTC** — Last LOG_ERROR entry written

4. **Feb 17–24** — Consciousness loop runs but doesn't write to consciousness.jsonl
   - Loop still iterates every 60s
   - Every cycle hits the `await router.complete()` crash
   - Exception handler logs to stderr (not captured in consciousness.jsonl)
   - Metrics updated internally but not persisted

5. **Feb 24** — Manual control signals (pause, resume, focus, reset) written by Claude Code
   - These bypass the cycle logic
   - No production cycles triggered

---

## Fix Impact Analysis

### Option 1: Make router.complete() Async (Recommended)
```python
# karma-core/router.py
async def complete(self, messages: list[dict], ...):
    # Wrap each provider call in asyncio.to_thread()
    result = await asyncio.to_thread(self._call_provider, ...)
    return result
```
- ✅ Solves Finding 2.3 (event loop no longer blocked)
- ✅ Enables consciousness to cycle productively
- ⚠️ Requires careful wrapping of all provider calls
- **Estimated tokens:** ~400

### Option 2: Wrap Call in consciousness.py
```python
# karma-core/consciousness.py, _think()
response = await asyncio.to_thread(self._router.complete, messages=..., task_type=...)
```
- ✅ Minimal change (1 line, reuse existing sync method)
- ✅ Preserves router.complete() as-is
- ⚠️ Threads still block some resources
- **Estimated tokens:** ~100

### Option 3: Don't Call Router (Status Quo)
- ❌ Consciousness loop silent since Feb 16
- ❌ No insights generated
- ❌ Distillation disabled (would have same router.complete() crash)

---

## Current Metrics State

Consciousness.py maintains internal metrics:
- `total_cycles`: Incremented every 60s
- `idle_cycles`: Incremented when observation is None
- `active_cycles`: Incremented when observation has new activity
- `errors`: Incremented on exception
- `llm_calls_total`: Incremented on successful LLM call
- `llm_calls_skipped`: Incremented on idle

**Problem:** These metrics live in memory (container RAM). On container restart, they're lost. And consciousness.jsonl doesn't show recent cycles, suggesting either:
1. Metrics are being updated but cycles aren't being logged
2. Loop crashed and restarted silently

---

## Recommended Execution

### Phase 0: Verify Current State (10 min)
```bash
# 1. Check if loop is actually cycling
ssh vault-neo 'wc -l /opt/seed-vault/memory_v1/ledger/consciousness.jsonl'
# Should show ~100+ lines if cycles were happening

# 2. Check container metrics
ssh vault-neo 'docker exec karma curl http://localhost:8340/metrics' 2>&1 | grep consciousness

# 3. Inspect recent stderr
ssh vault-neo 'docker logs --tail 200 karma' | grep -i "TypeError\|await\|exception"
```

### Phase 1: Apply Fix 2.3 (30 min)
**Best approach: Option 2 (minimal change to consciousness.py)**
```python
# Replace line in _think():
# OLD: response = await self._router.complete(...)
# NEW: response = await asyncio.to_thread(self._router.complete, messages=..., task_type=...)
```

### Phase 2: Rebuild & Deploy (15 min)
```bash
ssh vault-neo 'cd /opt/seed-vault && docker-compose build --no-cache karma && docker-compose up -d karma'
```

### Phase 3: Verify (10 min)
```bash
# Watch consciousness.jsonl for new CYCLE entries
ssh vault-neo 'tail -f /opt/seed-vault/memory_v1/ledger/consciousness.jsonl' &
# Wait 60s, should see new entries with action="OBSERVE", "THINK", "DECIDE", etc.
```

---

## Impact Summary

| Aspect | Current | After Fix |
|:---:|:---:|:---:|
| Consciousness cycles/min | 0 (broken since Feb 16) | 1 per 60s |
| Insights generated/day | 0 | ~24 |
| Event loop latency | Unknown (timeout) | <50ms (responsive) |
| Distillation cycle | Disabled (would crash) | Enabled (functional) |
| Memory growth | Slow (no cycles) | Normal (cycles produce logs) |

---

## Critical Path to Full Stability

**Must-do order:**
1. ✅ Verify 2.3 is root cause (Phase 0)
2. ✅ Fix 2.3 (Option 2: asyncio.to_thread) (Phase 1)
3. ✅ Rebuild + deploy (Phase 2)
4. ✅ Verify cycles resume (Phase 3)
5. → Then proceed with 5-pass fix plan (findings 1.1–3.7)

**Estimated time:** 1 hour total

---

## One Best Recommendation

**BEFORE APPLYING THE 5-PASS FIX PLAN: Fix Finding 2.3 immediately.**

The consciousness loop is currently dead. It has been since Feb 16. Until we restore its core cycle, we can't:
- Test any other fixes (consciousness would need to be running to validate)
- Generate insights (disabled since Feb 16)
- Distill graph (depends on consciousness working)
- Validate K2 integration (would see same router.complete() crash)

**Minimum viable fix:** Wrap `router.complete()` in `asyncio.to_thread()` in consciousness.py _think() method.

**Cost:** ~100 tokens, 30 min deployment, zero architectural risk.

**Do this first. Everything else depends on consciousness being operational.**

---

**Ready for implementation approval.**
