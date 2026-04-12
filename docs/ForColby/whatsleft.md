# WHAT'S LEFT — NEXUS FORENSIC CLOSEOUT (2026-04-11)

## Scope
- Workspace: `C:\Users\raest\Documents\Karma_SADE`
- Focus: post-ship forensic reverse of deployed Nexus, non-emergency blockers/gaps only.
- Truth rule: only current-pass command/probe/test evidence.

## Reverse-Engineered Working Build (Goal -> Start)
1. Goal surface: single merged Nexus across browser + Electron with continuity and tool use.
2. Required runtime spine: P1 harness (`:7891`), P1 cortex (`:7893`), mem worker (`:37778`), K2 cortex (`:7892`), hub route, vault-neo containers.
3. Inference survivability contract:
   - Primary path can fail (Anthropic quota/outage).
   - Emergency fallback must keep app alive independently (OpenRouter-first now deployed and verified).
4. App build + runtime contract:
   - `frontend` static build must pass.
   - Electron harness must pass smoke with UI + memory hit.
5. Deterministic verification contract:
   - Python test suite (`tests/`) and proxy node test must pass.
   - Local and hub endpoint probes must pass.

## Current Ground Truth (Verified This Pass)
- `python -m pytest -q tests` -> `121 passed`
- `node --test tests/test_proxy_routing.mjs` -> pass
- `npm run build` (`frontend`) -> pass
- Local health and emergency provider:
  - `GET http://127.0.0.1:7891/health` -> 200
  - `POST http://127.0.0.1:7891/cc/stream` -> `provider: openrouter`
- Hub deployed path:
  - `POST https://hub.arknexus.net/cc/v1/chat` -> 200 (`ok=true`)
- Electron ship smoke:
  - `tmp/electron-smoke-final-041126.json` -> `ok=true`, `directResult.provider=openrouter`, `uiResult.ok=true`, memory hit present

## Break/Fix Loops Run (Can We Break It?)

### Break Attempt 1 — Concurrent `/cc` requests
- Method: parallel batch requests against `:7891/cc`.
- Observed:
  - one request served 200
  - competing requests returned explicit 429 "Another request is in progress"
  - post-run `lock_held=false`
- Verdict: expected single-flight behavior; no stale lock defect.

### Break Attempt 2 — Cancel while request in-flight
- Method: start stream request, issue `/cancel`, then probe recovery request.
- Observed:
  - `/cancel` returned 200 (`cancelled=true`)
  - `lock_held=false` after cancel
  - follow-up `/cc` returned 200 with expected content
- Verdict: recovery path works; stale lock cleared.

### Break Attempt 3 — Burst load (5 requests)
- Method: 5 near-simultaneous batch requests.
- Observed:
  - first request succeeded
  - remaining requests rejected with explicit 429 single-flight message
  - `lock_held=false` after burst
- Verdict: system remains stable; no deadlock/regression observed.

## Remaining Non-Emergency Blockers / Gaps

### 1) Full browser↔electron parity matrix is incomplete
- Status: PARTIALLY VERIFIED
- Evidence: smoke + core routes pass, but exhaustive parity scenarios are not yet executed in one deterministic matrix.
- Why it matters: merged-workspace claim is strong but not fully proven across all workflows.
- What remains:
  - Define and run a parity matrix for at least: chat transcript continuity, file ops parity, memory recall/write parity, cancel/retry parity, and startup recovery parity.

### 2) Startup hardening shape still differs from ideal scheduled-task target
- Status: PARTIALLY VERIFIED
- Evidence:
  - current continuity uses watchdog task + HKCU Run entries and works
  - previous `KarmaSovereignHarness` creation remained privilege-constrained
- Why it matters: operationally works, but control-plane shape isn’t fully normalized under one task primitive.
- What remains:
  - either obtain required privilege and create canonical task form, or codify current startup path as canonical and retire old task expectation explicitly.

### 3) Single-flight throughput bottleneck (design tradeoff)
- Status: KNOWN LIMIT (not a correctness defect)
- Evidence: concurrent requests intentionally return 429 under load.
- Why it matters: prevents parallel user requests on one harness instance.
- What remains:
  - if higher concurrency is required, introduce queueing/multiplexing semantics and update tests/contracts accordingly.

## No Longer Blockers
- Anthropic outage/limit as hard stop: resolved via deployed OpenRouter-first emergency path.
- Lock recovery deadlock risk from disconnect/cancel: patched and verified in break loops.

## Recommended Next Concrete Pass (Non-Emergency)
1. Implement and run full browser/electron parity matrix with archived artifacts.
2. Normalize startup control-plane (privileged task vs documented run-key/watchdog canonicalization).
3. Decide whether to keep strict single-flight or add queueing; encode as explicit product behavior.