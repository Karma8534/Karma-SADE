# Phase: drift-fix — Atomic Task Plan

**Created:** 2026-03-04T15:30:00Z
**Context:** See phase-drift-fix-CONTEXT.md
**Status:** IN PROGRESS

---

## Pre-Phase Tasks

- [x] Write CONTEXT.md (design decisions locked)
- [x] Write PLAN.md (this file)
- [x] Phase A preflight complete (file paths, live state, GLM probe, STATE SNAPSHOT)

---

## Phase B — RED (write failing tests)

### B0 — Test scaffolding
- [ ] Create `hub-bridge/tests/routing.test.js` (Node built-in test runner — no Jest dep needed)
- [ ] Create `karma-core/tests/test_drift_fix.py`
- <verify> Test files exist and runner can discover them </verify>
- <done> Both files committed with empty/scaffold content </done>

### B1 — Pricing correctness tests
- [ ] Test: GLM model → pricePer1M() returns 0 for both input and output
- [ ] Test: gpt-4o-mini → pricePer1M() returns PRICE_GPT_4O_MINI_* values (not GPT_5_2)
- [ ] Test: Simulated spend near cap with GLM → cap NOT triggered
- [ ] Test: Simulated spend near cap with gpt-4o-mini → cap IS triggered
- <verify> All 4 tests FAIL (red) against current code </verify>
- <done> Tests written, confirmed failing </done>

### B2 — MODEL_DEEP default validity tests
- [ ] Test: env.MODEL_DEEP unset → resolved value is "gpt-4o-mini" (not "gpt-5-mini")
- [ ] Test: MODEL_DEEP="gpt-5-mini" in env → startup validation rejects it
- <verify> Both tests FAIL against current server.js </verify>
- <done> Tests written, confirmed failing </done>

### B3 — Routing correctness tests (chat + tool-use)
- [ ] Test: request without x-karma-deep header → model is glm-4.7-flash
- [ ] Test: request with x-karma-deep:true → model is gpt-4o-mini
- [ ] Test: tool-use request without deep header → uses glm-4.7-flash (not hardcoded gpt-4o-mini)
- [ ] Test: tool-use request with x-karma-deep:true → uses gpt-4o-mini
- <verify> Tests B3-a and B3-b pass (routing already correct for chat); B3-c FAILS (tool hardcoded) </verify>
- <done> All 4 routing tests written </done>

### B4 — ANALYSIS_MODEL default tests (Python)
- [ ] Test: config.ANALYSIS_MODEL default (no env) → "glm-4.7-flash" (not "gpt-4o-mini")
- [ ] Test: existing --skip-dedup path does NOT call create_graphiti()
- <verify> B4-a FAILS against current config.py; B4-b passes (skip-dedup is correct) </verify>
- <done> Tests written, B4-a confirmed failing </done>

**Gate: Commit all failing tests before Phase C.**

---

## Phase C — GREEN (implement fixes)

### C1 — Pricing authority (server.js)
- [ ] Replace pricePer1M() with model-keyed table
- [ ] GLM entry: { input: 0, output: 0 } — hardcoded
- [ ] gpt-4o-mini entry: reads PRICE_GPT_4O_MINI_INPUT/OUTPUT_PER_1M from env
- [ ] Add startup validation: if openai model and price env vars missing → fail-fast with clear error
- [ ] Remove PRICE_GPT_5_MINI_* and PRICE_GPT_5_2_* from hub.env
- <verify> B1 tests pass </verify>
- <done> B1 green + hub.env cleaned </done>

### C2 — MODEL_DEEP fallback (server.js)
- [ ] server.js:677: change `|| "gpt-5-mini"` → `|| "gpt-4o-mini"`
- [ ] Add startup validation: MODEL_DEEP not in ["gpt-4o-mini"] → log error + process.exit(1)
- <verify> B2 tests pass </verify>
- <done> B2 green </done>

### C3 — Tool routing (server.js)
- [ ] Remove line 883 model replacement (`model.startsWith("gpt") ? model : "gpt-4o-mini"`)
- [ ] Extract choose_model(deep_mode) function: returns MODEL_DEEP if deep_mode, else MODEL_DEFAULT
- [ ] Tool-use entry point uses choose_model() instead of hardcoded logic
- [ ] Verify tool call correctly reaches Z.ai client when model=glm-4.7-flash
- <verify> B3-c test passes (tool-use routes to GLM without deep header) </verify>
- <done> B3 green </done>

### C4 — ANALYSIS_MODEL default (karma-server)
- [ ] config.py:42: change default from "gpt-4o-mini" → "glm-4.7-flash"
- [ ] Add comment: "Note: create_graphiti() uses OpenAIClient; for GLM to work, GLM_BASE_URL must be set in env (already set in compose)"
- [ ] Verify --skip-dedup path still works (create_graphiti not called)
- <verify> B4-a test passes; no regression on B4-b </verify>
- <done> B4 green </done>

**Gate: All B1-B4 tests green before Phase D.**

---

## Phase D — Deploy + Verify

### D1 — Commit
- [ ] Full test suite green locally
- [ ] Commit: "phase-drift-fix: C1-C4 pricing/routing/defaults corrected [RED→GREEN]"
- [ ] Use PowerShell for git

### D2 — Deploy
- [ ] git push origin main
- [ ] vault-neo: git pull
- [ ] hub-bridge: cp server.js to build context → docker compose build --no-cache → up -d
- [ ] karma-server: cp config.py + batch_ingest.py to build context → build --no-cache → up -d

### D3 — Runtime verification (6 checks)
- [ ] /healthz returns 200
- [ ] Default chat → glm-4.7-flash in response
- [ ] x-karma-deep:true → gpt-4o-mini in response
- [ ] Tool-use without deep header → GLM (check logs for tool_router_override absent)
- [ ] GLM request → spend state $0 delta
- [ ] Cron still shows --skip-dedup

### D4 — Drift Resolution Report
- [ ] Per drift item: file:line changed, test name, runtime proof, commit SHA

---

## Phase F — GLM Rate Limiter (approved 2026-03-04)

**Context:** See CONTEXT.md Addendum §6 + `docs/plans/2026-03-04-glm-ratelimit-design.md`

### F0 — Design doc written + docs locked
- [x] `docs/plans/2026-03-04-glm-ratelimit-design.md` written
- [x] CONTEXT.md addendum appended
- [x] PLAN.md Phase F appended
- <done> Committed with `phase-glm-ratelimit: A — design locked` </done>

### F1 — RED: test_ratelimit.js (7 tests)
- [ ] B5-a: first 20 `checkAndConsume()` → all `{allowed: true}`
- [ ] B5-b: 21st call → `{allowed: false, retryAfterMs > 0}`
- [ ] B5-c: `retryAfterMs` ≈ (oldest_ts + 60_000) − now (±50ms)
- [ ] B5-d: after fake 60s advance, 21st call → `{allowed: true}`
- [ ] B5-e: `waitForSlot` resolves when slot opens
- [ ] B5-f: `waitForSlot` throws `glm_slot_timeout` on timeout
- [ ] B5-g: exported `glmLimiter` instance is same object reference across imports
- <verify> `node --test tests/test_ratelimit.js` → 7/7 FAIL </verify>
- <done> Tests written and confirmed RED </done>

### F2 — GREEN: GlmRateLimiter in lib/routing.js
- [ ] Add `GlmRateLimiter` class (sliding window, `checkAndConsume`, `waitForSlot`)
- [ ] Export `glmLimiter` singleton instance
- [ ] Export `GLM_INGEST_SLOT_TIMEOUT_MS` constant (default 60 000)
- <verify> `node --test tests/test_ratelimit.js` → 7/7 PASS </verify>
- <done> F1 + existing 18 routing/pricing tests all GREEN </done>

### F3 — GREEN: wire into server.js
- [ ] Import `glmLimiter`, `GLM_INGEST_SLOT_TIMEOUT_MS` from `./lib/routing.js`
- [ ] Instantiate with `rpm: Number(process.env.GLM_RPM_LIMIT || "20")` at startup
- [ ] /v1/chat: `checkAndConsume()` before `callLLMWithTools` when `!deep_mode` (GLM path)
  - On denied: `return json(res, 429, { ok: false, error: "glm_rate_limit", retry_after: Math.ceil(retryAfterMs/1000) })`
- [ ] /v1/ingest chunk loop: `await glmLimiter.waitForSlot(GLM_INGEST_SLOT_TIMEOUT_MS)` before each `callLLM`
  - Catch `glm_slot_timeout`: `return json(res, 503, { ok: false, error: "glm_slot_timeout", ... })`
- [ ] Brief generation: `checkAndConsume()` before `callLLM`; if denied, skip and log warn
- [ ] hub.env: add `GLM_RPM_LIMIT=20` and `GLM_INGEST_SLOT_TIMEOUT_MS=60000`
- <verify> `node --test tests/test_pricing.js tests/test_routing.js tests/test_ratelimit.js` → 25/25 PASS </verify>
- <done> All 25 tests GREEN, committed `phase-glm-ratelimit: C — implemented [RED→GREEN]` </done>

### F4 — Deploy + Verify (V1-V5)
- [ ] git push → vault-neo git pull → cp lib/ to build context → `./build_hub.sh` → compose up -d
- [ ] V1: 21 rapid curl → /v1/chat → 1-20: 200, 21: 429 `glm_rate_limit`
- [ ] V2: x-karma-deep:true during GLM limit → 200 (gpt-4o-mini unaffected)
- [ ] V3: /v1/ingest during GLM limit → blocks, resolves on slot
- [ ] V4: spend delta after 20 GLM requests → $0
- [ ] V5: startup logs → no ERROR from limiter init
- <done> All V1-V5 PASS, committed `phase-glm-ratelimit: D — verified in production` </done>

### F5 — Docs + Close
- [ ] MEMORY.md updated
- [ ] STATE.md updated
- [ ] claude-mem observations saved (PROOF F4, PITFALL any)
- [ ] session-end-verify.sh passes

**Gate: All 25 tests GREEN + V1-V5 PASS before close.**

---

## Phase E — Documentation + Session Close

- [ ] CLAUDE.md Known Pitfalls: add tool routing note (GLM tool-capable; unified router)
- [ ] .claude/rules/architecture.md: Decision #2 — exact routing rules + pricing table
- [ ] hub-bridge/config/hub.env: stale vars removed, correct vars documented
- [ ] .gsd/STATE.md: drift-fix phase complete
- [ ] MEMORY.md: session-60 summary updated
- [ ] save_observation for Phase B, C, D milestones
- [ ] Write phase-drift-fix-SUMMARY.md
- [ ] Commit all doc changes + push + vault-neo sync
- [ ] Regenerate cc-session-brief.md
- [ ] Run session-end-verify.sh
