# Phase: drift-fix — Design Context

**Locked:** 2026-03-04T15:30:00Z
**Owner:** Claude Code / Colby
**Scope:** Fix 4 architecture drift items in hub-bridge + karma-server. No Aria changes. No vault structure changes.

---

## Problem Statement

Decision #2 (GLM-4.7-Flash primary ~80%, gpt-4o-mini fallback ~20%) was documented but not fully implemented. 4 drift items found during session-60 audit.

---

## Design Decisions (Locked Before Code)

### 1. Routing Rules — What Triggers Fallback

| Trigger | Model | Rationale |
|---------|-------|-----------|
| Default (no header) | glm-4.7-flash | Decision #2 primary |
| `x-karma-deep: true` | gpt-4o-mini | Explicit deep mode |
| GLM error/timeout | NOT auto-falling back | Out of scope this phase; add as future task |
| Tool-use requests | glm-4.7-flash | GLM tool-calling PROVEN SUPPORTED (A3 probe) |

**GLM auto-fallback on error is explicitly NOT in scope.** Current behavior (error bubbles up) is acceptable. Adding auto-fallback requires health-check state management — separate phase.

### 2. Pricing Authority Approach

**Decision: Model-keyed table in pricePer1M(), not ad-hoc conditionals.**

```
pricingTable = {
  "glm-4.7-flash": { input: 0, output: 0 },  // hardcoded: Z.ai free tier
  "gpt-4o-mini": {
    input:  env.PRICE_GPT_4O_MINI_INPUT_PER_1M,   // already in live env
    output: env.PRICE_GPT_4O_MINI_OUTPUT_PER_1M   // already in live env
  }
}
```

- GLM is hardcoded $0 — no env var needed, no risk of misconfiguration
- gpt-4o-mini reads from already-correctly-named env vars (live env confirmed: 0.15 input, 0.60 output)
- Stale vars PRICE_GPT_5_MINI_* and PRICE_GPT_5_2_* removed from hub.env
- Fail-fast at startup if OpenAI is in use and price vars are missing/non-numeric

### 3. Tool-Use Routing Decision

**GLM-4.7-Flash tool-calling is SUPPORTED.** (Proven: A3 probe → finish_reason=tool_calls)

Current code (server.js:883) discards requested model and hardcodes gpt-4o-mini for tool-use. Fix:
- Remove the `model.startsWith("gpt") ? model : "gpt-4o-mini"` replacement
- Tool-use respects the same routing rule as chat: default=GLM, deep_mode=gpt-4o-mini
- Routing is unified: `choose_model(deep_mode)` returns the model; same function for chat and tool-use

### 4. MODEL_DEEP Fallback

Change code default: `|| "gpt-5-mini"` → `|| "gpt-4o-mini"`. Add allowed-set validation at startup.
Allowed set: `["gpt-4o-mini"]` — only known valid fallback for now.

### 5. ANALYSIS_MODEL Default (batch_ingest)

**Context:** `create_graphiti()` (which uses ANALYSIS_MODEL) is only called in non-skip-dedup mode. Default cron uses `--skip-dedup`, so this path is effectively inactive in production. Fix the default anyway for correctness.

Change `config.py` default from `"gpt-4o-mini"` → `"glm-4.7-flash"`.

**BUT:** `batch_ingest.py` passes ANALYSIS_MODEL to `graphiti_core.llm_client.OpenAIClient`. That client uses the OpenAI SDK. GLM works on an OpenAI-compatible endpoint (Z.ai). For Graphiti to use GLM, `LLMConfig` would need `base_url` set. If `LLMConfig` doesn't support `base_url`, this fix only changes the default; the client initialization would still point to OpenAI's API with a model name it doesn't recognize.

**Resolution:** Change the default. If LLMConfig doesn't support base_url, add a comment noting this and create a follow-up task. Do NOT break the existing Graphiti initialization path. This is a LOW severity fix and must not regress --skip-dedup mode.

---

## What We Are NOT Doing

- Not touching Aria, her files, or her system
- Not changing vault structure, ledger, or FalkorDB
- Not implementing GLM error auto-fallback (future phase)
- Not migrating Graphiti to a custom GLM client (if LLMConfig doesn't support base_url, document and defer)
- Not changing consciousness loop, batch_ingest skip-dedup logic, or cron config
- Not changing the hub.env `ZAI_API_KEY` or any auth tokens

---

## Confirmed File Paths (A1 verified)

| File | P1 Path | Droplet Build Context |
|------|---------|----------------------|
| server.js | hub-bridge/app/server.js | /opt/seed-vault/memory_v1/hub_bridge/app/server.js |
| hub.env | hub-bridge/config/hub.env | deployed via compose env_file |
| config.py | karma-core/config.py | /opt/seed-vault/memory_v1/karma-core/config.py |
| batch_ingest.py | karma-core/batch_ingest.py | /opt/seed-vault/memory_v1/karma-core/batch_ingest.py |
| hub-bridge tests | hub-bridge/tests/ (to create) | N/A |
| karma-server tests | karma-core/tests/ (exists) | N/A |

---

---

## Addendum: Phase F — GLM Rate Limiter (approved 2026-03-04)

**Problem:** Z.ai free tier hard cap ~20 RPM per key. No internal guard exists. System can
exhaust quota silently. Must never failover to paid tier on GLM limit hit.

### 6. GLM Rate Limiter Design Decisions (Locked)

| Decision | Value | Rationale |
|---|---|---|
| Limit | 20 RPM (`GLM_RPM_LIMIT` env, default 20) | Z.ai free tier maximum optimal |
| Scope | Global — single window across ALL routes | Provider measures per API key, not per route |
| Window | Sliding 60s (timestamp array, prune on each check) | Accurate; no fixed-interval reset artifacts |
| Implementation | `GlmRateLimiter` class in `lib/routing.js` | Isolated, testable, no callLLM pollution |
| Instance | Single export, shared at server.js module level | One counter = one truth |
| /v1/chat behavior | Immediate HTTP 429 `{error: "glm_rate_limit", retry_after: N}` | User can see and retry |
| /v1/ingest behavior | `waitForSlot(60_000)` per chunk — block up to 60s, then 503 | Watcher has retry logic; don't fail mid-PDF |
| Brief generation | `checkAndConsume()` — skip gracefully on limit, log warn | Non-fatal internal call |
| Deep-mode calls | NOT counted — limiter skips gpt-4o-mini | Z.ai limit is GLM-specific |
| Ingest slot timeout var | `GLM_INGEST_SLOT_TIMEOUT_MS` default 60 000 | Per-chunk ceiling |

### What Phase F Is NOT Doing

- Not a distributed rate limiter (single process, no Redis)
- Not an auto-failover to gpt-4o-mini on limit hit (explicitly prohibited)
- Not applied to /v1/ambient, /v1/context, /v1/cypher
- Not a retry queue — callers handle retry via Retry-After / watcher backoff

**Full design:** `docs/plans/2026-03-04-glm-ratelimit-design.md`

---

## Live State at Design Lock (A2 + A3)

- Spend state: $0.117369 accumulated (2026-03-03) — charged at wrong rates
- GLM tool-capability: **SUPPORTED** (finish_reason=tool_calls confirmed)
- Live env: PRICE_GPT_4O_MINI_INPUT/OUTPUT_PER_1M already present in container (0.15/0.60)
- PRICE_GPT_5_MINI and GPT_5_2 vars also present — to be removed from hub.env
- MODEL_DEEP env=gpt-4o-mini (overrides bad code default of gpt-5-mini)
- ANALYSIS_MODEL env=gpt-4o-mini (in karma-server container)
