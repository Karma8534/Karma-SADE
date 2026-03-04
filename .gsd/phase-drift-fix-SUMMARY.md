# Phase: drift-fix — Summary

**Completed:** 2026-03-04T16:00:00Z
**Session:** 60
**Status:** ✅ ALL 4 DRIFT ITEMS CORRECTED + VERIFIED

---

## What Was Built

4 architecture drift items corrected to match Decision #2 (GLM-4.7-Flash primary, gpt-4o-mini fallback).

### Files Changed

| File | Change |
|------|--------|
| hub-bridge/lib/pricing.js | NEW — model-keyed pricing authority (GLM=$0, gpt-4o-mini=env vars) |
| hub-bridge/lib/routing.js | NEW — routing authority (chooseModel, validateModelEnv) |
| hub-bridge/app/server.js | Imports from lib; removes inline pricePer1M/estimateUsd; fixes MODEL_DEEP default; fixes tool-use model; adds startup validation |
| hub-bridge/app/Dockerfile | Build context expanded to hub-bridge/ root to include lib/ |
| hub-bridge/compose.hub.yml | context: ./app → context: . / dockerfile: app/Dockerfile |
| karma-core/config.py | ANALYSIS_MODEL default: gpt-4o-mini → glm-4.7-flash |
| hub-bridge/config/hub.env (vault-neo) | Removed stale PRICE_GPT_5_MINI_* and PRICE_GPT_5_2_* vars |

### Tests Written (22 total)
- hub-bridge/tests/test_pricing.js — 9 tests (B1 pricing correctness)
- hub-bridge/tests/test_routing.js — 9 tests (B2/B3 routing correctness)
- karma-core/tests/test_drift_fix.py — 4 tests (B4 ANALYSIS_MODEL)

### Runtime Verification (6-point)
- D1: GLM default chat → provider=zai, usd=0 ✅
- D2: Deep mode → gpt-4o-mini, provider=openai, cost charged ✅
- D3: Startup validation passes without error ✅
- D4: GLM spend delta = $0 (was $0.001608/request before fix) ✅
- D5: karma-server rebuilt, RestartCount=0 ✅
- D6: All containers healthy ✅

---

## Pitfalls Discovered

1. **hub-bridge Dockerfile build context = ./app**: Adding lib/ imports to server.js required expanding the compose.hub.yml build context from `context: ./app` to `context: .` (hub-bridge root). Without this, Docker COPY can't reach lib/ which is at the same level as app/. Then Dockerfile changed to `COPY app/server.js ./` + `COPY lib/ ./lib/`.

2. **server.js import path vs test import path**: In the container, server.js is at /app/server.js → imports lib as `./lib/pricing.js`. Tests are at hub-bridge/tests/ → import lib as `../lib/pricing.js`. Both are correct but different.

3. **compose .env overrides config.py default**: `ANALYSIS_MODEL=gpt-4o-mini` is set in compose .env, overriding the config.py default fix. This is intentional — the Graphiti OpenAI client can't route to Z.ai for GLM without base_url support. Production correctly uses gpt-4o-mini for the (inactive) Graphiti analysis path. Config.py default fix applies when env var is absent.

4. **callGPTWithTools is dead code**: The function at line 866 is never called (chat route uses callLLMWithTools which for non-Anthropic falls back to callLLM). Fixed line 883 model override anyway since it represents architectural drift.

---

## What's Pending (Follow-up Tasks)

1. **GLM auto-fallback on error** — explicitly deferred. If Z.ai times out, error bubbles up. Future phase with health-check state management.
2. **Graphiti GLM routing** — if LLMConfig gets base_url support, update ANALYSIS_MODEL path to use Z.ai GLM. For now, compose .env keeps gpt-4o-mini for the inactive path.
3. **Spend state accuracy** — accumulated $0.12 was charged at wrong rates (GLM as paid). State is a running total and can't be retroactively corrected without manual edit to spend.state.json. Current state frozen; new charges will be correct.

---

## Evidence

- Tests: 22/22 GREEN (committed in session)
- Runtime: D1-D6 all PASS (verified live on vault-neo)
- Commits: 658d40e (C1-C4 fixes), ff01914 (Dockerfile build context)
- Observations: claude-mem #3447 (PROOF), #3448 (PITFALL)
