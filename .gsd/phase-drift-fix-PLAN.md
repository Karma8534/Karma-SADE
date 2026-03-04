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
