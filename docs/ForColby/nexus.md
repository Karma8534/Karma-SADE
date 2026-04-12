# NEXUS — CANONICAL CURRENT PLAN (041126E)

Truth policy: fail-closed. Every status claim below is backed by current-pass command/probe/test evidence.

## CURRENT GROUND-TRUTH BASELINE

### VERIFIED CURRENT STATE
- Workspace root: `C:\Users\raest\Documents\Karma_SADE`.
- P1 runtime is healthy:
  - `http://127.0.0.1:7891/health` -> 200.
  - `http://127.0.0.1:7893/health` -> 200.
  - `http://127.0.0.1:37778/health` -> 200.
- K2/cortex health:
  - `http://192.168.0.226:7892/health` -> 200.
  - `http://100.75.109.92:7892/health` -> 200.
- Hub runtime/deploy surface:
  - `https://hub.arknexus.net/cc/health` -> 200.
  - `https://hub.arknexus.net/cc/v1/status` -> 200 (`p1.healthy=true`, `k2.healthy=true`).
  - `https://hub.arknexus.net/cc/v1/chat` -> 200 with authenticated response.
- vault-neo runtime spine is live (`anr-hub-bridge`, `karma-server`, vault stack all up/healthy).

### VERIFIED EMERGENCY INDEPENDENCE (ANTHROPIC-OUTAGE SURVIVAL)
- OpenRouter emergency key persisted at `C:\Users\raest\Documents\Karma_SADE\.openrouter-api-key`.
- P1 server emergency launcher now enforces Anthropic-independent mode:
  - `KARMA_EMERGENCY_INDEPENDENT=1`
  - `KARMA_DISABLE_ANTHROPIC=1`
- Local server stream probe confirms provider routing:
  - `POST http://127.0.0.1:7891/cc/stream` returned `provider: openrouter`.
- Local batch probe succeeds under emergency mode:
  - `POST http://127.0.0.1:7891/cc` returned exact expected response.
- Electron emergency smoke confirms Anthropic-independent operation:
  - `tmp/electron-smoke-emergency-ship-041126.json` has `ok=true`, `directResult.provider=openrouter`, `uiResult.ok=true`, memory hit present.

### VERIFIED BUILD / TEST / SHIP GATES
- Frontend build: `npm run build` passed (`frontend`).
- Deterministic tests passed:
  - `python -m pytest -q tests/test_palace_precompact.py tests/test_cc_email_daemon.py tests/test_cc_server_harness.py tests/test_electron_memory_autosave.py` -> `58 passed`.
- Emergency fallback regression coverage includes OpenRouter-first cascade and fallback order assertions.

### PARTIALLY VERIFIED
- Full browser/electron parity matrix beyond smoke+memory gate remains incomplete (core path verified; full exhaustive parity suite still future work).

## REVERSE-ENGINEERED BUILD CHAIN (GOAL -> BOOTSTRAP)
1. Goal state: one merged workspace/session across browser + Electron with continuity and tooling.
2. Runtime spine: hub proxy + P1 harness + K2 support + vault services must be healthy.
3. Primary/fallback contract: primary may be unavailable; emergency-independent OpenRouter-first route must keep app alive.
4. App surfaces: frontend build artifact + Electron harness must both execute chat/memory loops.
5. Persistence controls: server launcher + persistent loop + watchdog/startup semantics must keep runtime recoverable.
6. Verification floor: deterministic tests + authenticated endpoint probes + smoke artifact must all pass in same run.

## HOST BOUNDARIES

### P1
- Local harness (`cc_server_p1.py`), Electron runtime, startup scripts, emergency inference control.

### K2
- Cortex/synthesis support and fallback support host.

### vault-neo
- Deployed hub/vault runtime spine.

## PRIMARY VS FALLBACK PATHS

### Design Contract
- Primary identity path remains `CC --resume` when available.

### Emergency Runtime Contract (Verified)
- When Anthropic path is unavailable or disabled, system must survive via OpenRouter-first cascade, then Groq/Ollama/K2.
- This emergency contract is now deployed and verified in both P1 server and Electron harness.

## IMPLEMENTATION STATUS (041126E)

### VERIFIED CURRENT STATE
- OpenRouter emergency fallback deployed in `Scripts/cc_server_p1.py` and `electron/main.js`.
- Startup script hardened to load/persist OpenRouter key and force emergency-independent mode.
- Server process redeployed and verified healthy after patch.
- Hub path verified live after deployment.

### REQUIRED FUTURE WORK
1. Run and archive a full browser/electron parity matrix (beyond smoke) for all critical workflows.
2. Continue hardening startup/task governance if privilege boundaries change.
3. Keep test coverage aligned with cascade ordering and lock behavior.

## VERIFICATION CONTRACT

### Pass Conditions
- Build + deterministic tests pass.
- Local `/cc/stream` explicitly reports `provider=openrouter` during emergency mode.
- Hub chat remains operational with auth.
- Electron smoke artifact confirms direct provider and UI+memory success.

### Fail Conditions
- Any claim of emergency independence without a current `provider=openrouter` probe.
- Any lock/cascade regression that causes repeated 429 deadlock or non-recovering request flow.

## ANTI-DRIFT RULES
- Never claim Anthropic independence without current-pass openrouter-provider evidence.
- Never infer runtime health from code presence.
- Keep fallback order tested whenever routing logic changes.
- Keep host attribution explicit for all runtime claims.

## DEFINITION OF DONE
A Nexus emergency-shippable milestone is done only when:
1. Runtime survives Anthropic path loss via verified non-Anthropic provider.
2. Frontend build, deterministic tests, and Electron smoke all pass in same run.
3. Hub deployed path remains healthy and responsive.
4. Plan/audit status labels match current-pass evidence.