# futurework

## 1) Purpose of Future Work
Extend the proven `jprop6` foundation without re-opening foundational ambiguity.
All expansion work must preserve binary gates, runtime-truth evidence, and continuity contracts.

## 2) Why Future Work Is Now Permitted
Future work is unlocked because `PROOF.md` certifies:
`GROUND-TRUTH VERIFIED 100% = YES`.

Prerequisite mission gates already passed:
- A through R in `EXECUTION_GATES.md` are PASS.

## 3) Phase-by-Phase Expansion Rail

### Expansion Phase F1 — Authenticated Runtime Truth Pack
Why allowed now:
- Prerequisite gates passed: P0-G1..P0-G5, P5-G1.

Exact next steps:
1. Add an authenticated runtime probe script under `jprop6/MINIMAL_HARNESS/scripts/` that reads auth from explicit env vars only.
2. Capture `/v1/surface` and `/v1/spine` with explicit auth/no-auth result separation.
3. Add gate rule requiring both auth and unauth probe records.

Files likely to change:
1. `jprop6/MINIMAL_HARNESS/scripts/runtime_probe.js`
2. `jprop6/TEST_STRATEGY.md`
3. `jprop6/EXECUTION_GATES.md`
4. `jprop6/PROOF.md`

Proof commands:
1. `node scripts/runtime_probe.js`
2. `node scripts/runtime_probe.js --no-auth`

Failure risks:
1. Secret leakage in logs.
2. False PASS from cached credentials.

Rollback trigger:
1. Any probe output containing raw secret/token.

What NOT to expand yet:
1. No new product features.
2. No watcher authority changes.

Anti-drift guardrail:
1. Probe outputs must be artifacted with timestamp and auth mode labels.

---

### Expansion Phase F2 — Deterministic Session Conflict Policy
Why allowed now:
- Prerequisite gates passed: P1-G1..P1-G5, P2-G1..P2-G4.

Exact next steps:
1. Define write-conflict resolution policy (`last-write-wins` or explicit rejection) as a versioned contract document.
2. Add deterministic conflict tests for browser-first and electron-first ordering.
3. Add rollback behavior for incompatible schema/version writes.

Files likely to change:
1. `jprop6/MINIMAL_HARNESS/session_contract.schema.json`
2. `jprop6/MINIMAL_HARNESS/tests/break_check.js`
3. `jprop6/TEST_STRATEGY.md`
4. `jprop6/jprop6.md`

Proof commands:
1. `npm run check:contract`
2. `npm run check:break`

Failure risks:
1. Ambiguous conflict semantics leading to silent state loss.

Rollback trigger:
1. Any non-deterministic result across repeated conflict tests.

What NOT to expand yet:
1. No multi-agent writes.
2. No cross-device sync claims.

Anti-drift guardrail:
1. Conflict policy version must be explicit and backward-compatible.

---

### Expansion Phase F3 — Harness Startup/Recovery Contract
Why allowed now:
- Prerequisite gates passed: P3-G1..P3-G7.

Exact next steps:
1. Add startup recovery flow with explicit decision states: `resume`, `reset`, `degraded`.
2. Add invalid-envelope recovery tests.
3. Add user-visible degraded banner for recovery failure cases.

Files likely to change:
1. `jprop6/MINIMAL_HARNESS/main.js`
2. `jprop6/MINIMAL_HARNESS/renderer/fallback.html`
3. `jprop6/MINIMAL_HARNESS/tests/break_check.js`
4. `jprop6/MINIMAL_HARNESS/README.md`

Proof commands:
1. `npm run check:syntax`
2. `npm run check:break`

Failure risks:
1. Recovery loop traps.
2. False resume claims.

Rollback trigger:
1. Any startup path that cannot deterministically reach a known state.

What NOT to expand yet:
1. No tool execution APIs.
2. No code-edit pipeline activation.

Anti-drift guardrail:
1. Recovery states are finite and enumerated; unknown state is automatic FAIL.

---

### Expansion Phase F4 — Watcher Redesign as Telemetry-Only
Why allowed now:
- Prerequisite gates passed: P4-G1..P4-G3.

Exact next steps:
1. Define watcher output schema with severity and evidence pointers.
2. Enforce watcher output cannot mutate gate status.
3. Add tests where watcher reports PASS while gate evidence FAILs.

Files likely to change:
1. `jprop6/FOUNDATION_DECISION.md`
2. `jprop6/TEST_STRATEGY.md`
3. `jprop6/BREAK_REPORT.md`
4. `jprop6/EXECUTION_GATES.md`

Proof commands:
1. `rg -n "watcher" jprop6/*.md jprop6/artifacts/*.tsv`
2. Targeted watcher false-positive simulation script (to be added in this phase).

Failure risks:
1. Authority creep back into watcher outputs.

Rollback trigger:
1. Any text or code path that allows watcher output to close a phase.

What NOT to expand yet:
1. No autonomous watcher remediation.
2. No watcher-driven deployment actions.

Anti-drift guardrail:
1. Closure authority remains proof artifacts only.

---

### Expansion Phase F5 — Security Patch Track for Electron Baseline
Why allowed now:
- Prerequisite gates passed: P3-G1..P3-G7, P5-G1.

Exact next steps:
1. Evaluate latest safe Electron version compatible with current scaffold.
2. Update pinned Electron version and lockfile.
3. Re-run all harness checks and verify no boundary regression.

Files likely to change:
1. `jprop6/MINIMAL_HARNESS/package.json`
2. `jprop6/MINIMAL_HARNESS/package-lock.json`
3. `jprop6/PROOF.md`

Proof commands:
1. `npm install`
2. `npm audit --json > ../artifacts/npm_audit.json`
3. `npm run check:syntax && npm run check:proof && npm run check:contract && npm run check:break`

Failure risks:
1. Electron upgrade changes webPreferences behavior.

Rollback trigger:
1. Any failed proof or contract check after upgrade.

What NOT to expand yet:
1. No new capabilities bundled with security bump.

Anti-drift guardrail:
1. Version bumps are security-only and must be isolated.

## 4) Explicit Boundary (Still Deferred / Forbidden)
Still deferred:
1. Plugin ecosystem growth.
2. Voice stack expansion.
3. Multi-transport runtime expansion beyond browser/Electron foundation.
4. Multi-agent autonomy and orchestration product surface.

Still forbidden until later certified phases:
1. Any claim that full merged workspace behavior is complete.
2. Any watcher-based phase closure.
3. Any feature launch that bypasses PASS/FAIL gate evidence.

Invalidation warning:
1. If future expansions skip binary gates or override continuity contracts, foundation certification is invalid and must roll back to Phase 0.
