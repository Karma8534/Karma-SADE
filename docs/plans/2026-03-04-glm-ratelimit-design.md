# GLM Rate Limiter — Design Document

**Date:** 2026-03-04
**Status:** APPROVED
**Phase:** glm-ratelimit (Phase F of drift-fix series)
**Decision authority:** Colby / Claude Code

---

## Problem

Z.ai free tier enforces strict per-key RPM limits (~20 RPM maximum optimal). Hub-bridge has no
internal guard. Under high load or multi-chunk PDF ingest, the process can exhaust the quota,
causing Z.ai 429s to surface as uncaught errors upstream. The system must never silently fail
over to a paid tier when the GLM limit is hit.

---

## Constraints (locked)

1. GLM quota is measured per API key, not per route — the limit is **global across /v1/chat and /v1/ingest**.
2. Hard limit: **20 RPM** (env: `GLM_RPM_LIMIT`, default 20). This is the maximum optimal for Z.ai free tier.
3. On limit hit: **never** silently route to gpt-4o-mini or any paid model.
4. `/v1/chat` limit hit → immediate **HTTP 429** to the caller.
5. `/v1/ingest` chunk loop → **block and wait** up to `GLM_INGEST_SLOT_TIMEOUT_MS` (default 60 000 ms) per chunk before continuing. If slot never opens within the ceiling, return **HTTP 503** (`glm_slot_timeout`).
6. Brief generation (internal callLLM inside /v1/ingest) → **skip gracefully** if limit hit; log warn, non-fatal.
7. No new npm dependencies. Node.js is single-threaded; no mutex needed.

---

## Architecture

### GlmRateLimiter class — `lib/routing.js`

Sliding-window implementation. Maintains an in-process array of request timestamps.

```
state:
  timestamps: number[]   — wall-clock ms of each consumed GLM slot
  rpm: number            — window size cap (from env)
  windowMs: 60_000       — fixed: one minute

checkAndConsume() → { allowed: boolean, retryAfterMs: number }
  prune timestamps older than (now - windowMs)
  if timestamps.length < rpm:
    push now
    return { allowed: true, retryAfterMs: 0 }
  else:
    oldest = timestamps[0]
    retryAfterMs = (oldest + windowMs) - now   // ms until oldest slot expires
    return { allowed: false, retryAfterMs }

waitForSlot(timeoutMs) → Promise<void>
  deadline = now + timeoutMs
  loop:
    result = checkAndConsume()
    if result.allowed → return
    if now >= deadline → throw Error("glm_slot_timeout")
    await sleep(min(result.retryAfterMs, deadline - now))
```

### Global instance — `server.js`

```js
const glmLimiter = new GlmRateLimiter({
  rpm: Number(process.env.GLM_RPM_LIMIT || "20"),
});
```

Single instance created at module load. All routes share the same window.

---

## Callsite Map

| Callsite | Location | Method | On limit |
|---|---|---|---|
| /v1/chat pre-LLM | server.js (chat handler) | `checkAndConsume()` | Return 429 `glm_rate_limit` + `retry_after` |
| /v1/ingest chunk loop | server.js (ingest handler, per-chunk) | `waitForSlot(60_000)` | Block up to 60s; 503 on timeout |
| Brief generation | server.js (inside ingest handler) | `checkAndConsume()` | Skip brief, log `[RATELIMIT] brief skipped` |

The limiter only activates when `model.startsWith("glm-")` — i.e., when the request is actually
routed to Z.ai. Deep-mode requests (gpt-4o-mini) are not counted and are never affected.

---

## Response Shapes

**429 from /v1/chat:**
```json
{
  "ok": false,
  "error": "glm_rate_limit",
  "retry_after": 12
}
```
(`retry_after` is seconds, rounded up from retryAfterMs)

**503 from /v1/ingest (timeout):**
```json
{
  "ok": false,
  "error": "glm_slot_timeout",
  "filename": "example.pdf",
  "chunks_processed": 2,
  "chunks_total": 5
}
```

---

## Environment Variables

| Var | Default | Notes |
|---|---|---|
| `GLM_RPM_LIMIT` | `20` | Z.ai free tier maximum optimal. Set lower for safety margin. |
| `GLM_INGEST_SLOT_TIMEOUT_MS` | `60000` | Per-chunk wait ceiling for /v1/ingest. |

Both added to hub.env on vault-neo. Neither affects routing decisions (GLM vs gpt-4o-mini).

---

## Test Plan (B5 — 7 cases)

| ID | Test | Pass condition |
|---|---|---|
| B5-a | 20 rapid `checkAndConsume()` calls | All return `{allowed: true}` |
| B5-b | 21st `checkAndConsume()` call | Returns `{allowed: false, retryAfterMs > 0}` |
| B5-c | `retryAfterMs` accuracy | ≈ (oldest_ts + 60_000) - now (within 50ms tolerance) |
| B5-d | After 60s, 21st call allowed | Returns `{allowed: true}` (fake-clock test) |
| B5-e | `waitForSlot` resolves on slot open | Resolves without throwing |
| B5-f | `waitForSlot` timeout | Throws `glm_slot_timeout` when no slot opens within ceiling |
| B5-g | Single exported instance | `import { glmLimiter } from routing` × 2 → same object reference |

---

## What This Is NOT

- Not a distributed rate limiter (single process, no Redis)
- Not a retry queue (caller retries; we just block briefly for ingest)
- Not an auto-failover to paid tier (explicitly prohibited)
- Not applied to gpt-4o-mini deep-mode calls
- Not applied to ambient/capture endpoints (/v1/ambient, /v1/context, /v1/cypher)

---

## Deployment

Standard workflow:
1. Edit on P1 → git commit → git push
2. `ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"`
3. Sync lib/ to build context: `cp -r hub-bridge/lib /opt/seed-vault/memory_v1/hub_bridge/`
4. `cd /opt/seed-vault/memory_v1/hub_bridge && ./build_hub.sh`
5. `docker compose -f compose.hub.yml up -d hub-bridge`

No karma-server rebuild required (rate limiter is hub-bridge only).

---

## Verification Matrix

| Check | Command | Pass |
|---|---|---|
| V1 | 21 rapid curl → /v1/chat (no deep header) | 1-20: 200, 21: 429 glm_rate_limit |
| V2 | x-karma-deep: true during GLM limit | 200 (gpt-4o-mini, unthrottled) |
| V3 | /v1/ingest during GLM limit | Blocks, then resolves when slot opens |
| V4 | spend after 20 GLM requests | usd_spent unchanged |
| V5 | Startup logs | No ERROR from limiter init |
