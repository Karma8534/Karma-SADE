# jprop6 (Canonical Plan)

## Plan Contract
This plan is foundation-first and binary-gated.
No phase advances without PASS evidence.

## Phase 0 — Truth Substrate (Gate-First)

### Objective
Establish canonical runtime truth rails so documentation cannot self-certify completion.

### Exact Scope
1. Build line-level audit artifacts for `nexus.md` and `STATE.md`.
2. Build contradiction ledger and claim classification model.
3. Build runtime probe packet (`/health`, `/v1/surface`, `/v1/spine`, Electron shell evidence).
4. Define single source of truth for closure decisions.

### Dependencies
None.

### Anti-Goals
1. No feature shipping.
2. No watcher trust assumptions.
3. No architecture expansion.

### Concrete Deliverables
1. `FORENSIC_AUDIT.md`
2. `FOUNDATION_DECISION.md`
3. `artifacts/nexus_line_audit.tsv`
4. `artifacts/state_line_audit.tsv`
5. `artifacts/runtime_checks.txt`

### Proof Requirements
1. Line counts for both canonical docs logged.
2. Contradictions listed with line evidence.
3. Runtime probe outputs captured with timestamp.

### Break Tests
1. Inject a “shipped” claim without command proof -> must fail phase.
2. Remove contradiction evidence links -> must fail phase.
3. Probe unavailable dependency and still mark healthy -> must fail phase.

### Failure Modes
1. Truth source drift (status prose used as proof).
2. Missing runtime probes.
3. Contradiction suppression.

### Exit Criteria
PASS only if all deliverables exist and each contradiction has evidence references.

### Rollback Criteria
If any contradiction is found later without ledger entry, roll back to Phase 0.

### Not Allowed Yet
1. Continuity implementation changes.
2. Electron feature expansion.
3. Watcher redesign claims without evidence.

### Minute-Granular Steps
1. P0.1 (10m): Inventory canonical files and line counts.
2. P0.2 (20m): Build line-audit artifacts.
3. P0.3 (25m): Extract claim lines and path references.
4. P0.4 (20m): Run runtime probes and capture outputs.
5. P0.5 (30m): Build contradiction ledger.
6. P0.6 (15m): Gate check + rollback test.

---

## Phase 1 — Continuity Substrate

### Objective
Define and prove minimum session continuity contract independent of status prose.

### Exact Scope
1. Specify continuity envelope schema.
2. Define read/write/invalid-state behavior.
3. Define browser↔Electron contract boundaries.
4. Define failure handling and rollback rules.

### Dependencies
Phase 0 PASS.

### Anti-Goals
1. No full UX claims.
2. No transport expansion.
3. No multi-agent orchestration feature growth.

### Concrete Deliverables
1. `MINIMAL_HARNESS/session_contract.schema.json`
2. `TEST_STRATEGY.md` continuity tests section
3. `EXECUTION_GATES.md` continuity gates

### Proof Requirements
1. Contract schema exists and parses.
2. Contract sample validates via local check script.
3. Invalid contract scenarios are documented as FAIL.

### Break Tests
1. Missing `session_id` -> FAIL.
2. Unknown `schema_version` -> FAIL.
3. Invalid timestamp format -> FAIL.

### Failure Modes
1. Implicit session assumptions.
2. Ambiguous ownership of continuity state.
3. No rollback trigger.

### Exit Criteria
PASS only with contract tests + negative-case behavior documented.

### Rollback Criteria
Any continuity key ambiguity forces return to Phase 1 step P1.1.

### Not Allowed Yet
1. Watcher authority changes.
2. Plugin integration.
3. Voice or remote-control expansion.

### Minute-Granular Steps
1. P1.1 (15m): Define continuity envelope fields.
2. P1.2 (20m): Define invalid-state semantics.
3. P1.3 (20m): Implement local contract checks.
4. P1.4 (25m): Attack with malformed envelopes.
5. P1.5 (15m): Freeze PASS criteria.

---

## Phase 2 — Browser↔Electron Shared Session Contract

### Objective
Prove parity contract between browser and Electron harness seams.

### Exact Scope
1. Define common session envelope ownership model.
2. Define runtime parity checks (same required keys, same semantics).
3. Define stale-read and write-conflict handling rules.

### Dependencies
Phase 1 PASS.

### Anti-Goals
1. No broad UI redesign.
2. No assumption that merged workspace is complete.

### Concrete Deliverables
1. `MINIMAL_HARNESS/preload.js` bridge with session read/write methods.
2. Parity test cases in `TEST_STRATEGY.md`.
3. Phase simulation and break cases in `PHASE_SIMULATIONS.md` + `BREAK_REPORT.md`.

### Proof Requirements
1. Preload exposes only minimal continuity/runtime APIs.
2. No shell/code-edit privileges in scaffold.
3. Contract checks pass.

### Break Tests
1. Simulated browser writes envelope A while Electron reads stale B.
2. Missing preload bridge call path.
3. Node integration accidentally enabled.

### Failure Modes
1. Divergent envelope semantics.
2. Security boundary collapse.
3. Implicit concurrency assumptions.

### Exit Criteria
PASS only if parity + security checks are explicit and passing.

### Rollback Criteria
If preload surface expands beyond scope, rollback to P2.1.

### Not Allowed Yet
1. Deep feature wiring inside hub app.
2. Agent/watcher authority coupling.

### Minute-Granular Steps
1. P2.1 (15m): Define parity matrix.
2. P2.2 (20m): Implement preload bridge.
3. P2.3 (20m): Implement contract check script.
4. P2.4 (20m): Run break scenarios.
5. P2.5 (15m): Freeze boundary constraints.

---

## Phase 3 — Minimal Electron Harness Foundation @ hub.arknexus.net

### Objective
Create smallest honest Electron harness that is extendable and testable.

### Exact Scope
1. Electron main process with secure BrowserWindow.
2. Hub URL load path with fallback page.
3. Session envelope persistence seam.
4. Foundation-only README and proof checks.

### Dependencies
Phase 2 PASS.

### Anti-Goals
1. No “full app complete” claims.
2. No watcher-driven closure.
3. No plugin/voice/transport expansion.

### Concrete Deliverables
1. `MINIMAL_HARNESS/main.js`
2. `MINIMAL_HARNESS/preload.js`
3. `MINIMAL_HARNESS/renderer/fallback.html`
4. `MINIMAL_HARNESS/scripts/proof_check.js`
5. `MINIMAL_HARNESS/tests/contract_check.js`
6. `MINIMAL_HARNESS/tests/break_check.js`
7. `MINIMAL_HARNESS/README.md`

### Proof Requirements
1. JS syntax checks pass.
2. Proof script passes.
3. Contract test passes.
4. Break-check test passes.
5. Runtime contract documented without overclaim.

### Break Tests
1. Disable hub connectivity -> fallback must explain honest state.
2. Enable forbidden capability in scaffold -> proof script must fail.
3. Remove required continuity key -> contract test must fail.

### Failure Modes
1. Overclaiming capability.
2. Security boundary drift.
3. Missing continuity seam.

### Exit Criteria
PASS only when all scaffold checks pass and honesty constraints are explicit.

### Rollback Criteria
Any claim beyond tested scaffold behavior rolls back to Phase 3.

### Not Allowed Yet
1. Full merged workspace declaration.
2. Multi-agent orchestration UI.
3. Runtime mutation tools.

### Minute-Granular Steps
1. P3.1 (20m): Scaffold files.
2. P3.2 (20m): Add secure preload surface.
3. P3.3 (15m): Add fallback and honesty banner.
4. P3.4 (15m): Add proof scripts.
5. P3.5 (15m): Run checks and capture logs.

---

## Phase 4 — Watcher/Governor Governance Decision (Foundation Control)

### Objective
Decide watcher role under strict proof authority.

### Exact Scope
1. Forensic watcher failure audit.
2. Authority boundary decision.
3. Guardrails against watcher-based false closure.

### Dependencies
Phase 3 PASS.

### Anti-Goals
1. No watcher feature expansion.
2. No autonomous closure privileges.

### Concrete Deliverables
1. Watcher decision in `FOUNDATION_DECISION.md`.
2. Watcher tests and guardrails in `TEST_STRATEGY.md`.
3. Watcher break/fix entries in `BREAK_REPORT.md`.

### Proof Requirements
1. Explicit watcher failure evidence references.
2. Explicit closure authority policy.

### Break Tests
1. Simulate watcher says PASS while runtime gate fails.
2. Simulate stale watcher output used as closure evidence.

### Failure Modes
1. Authority inversion.
2. Governance ambiguity.

### Exit Criteria
PASS only if watchers are demoted to advisory role in closure logic.

### Rollback Criteria
Any phase closure by watcher prose triggers rollback.

### Not Allowed Yet
1. Re-promoting watchers to closure authority.

### Minute-Granular Steps
1. P4.1 (20m): Extract watcher failure evidence.
2. P4.2 (20m): Define authority policy.
3. P4.3 (15m): Add break tests.
4. P4.4 (10m): Gate lock.

---

## Phase 5 — Ground-Truth Certification Gate

### Objective
Certify `GROUND-TRUTH VERIFIED 100%` with explicit PASS/FAIL by criterion.

### Dependencies
Phase 0-4 PASS.

### Deliverables
1. `PROOF.md` certification section.
2. If and only if YES: `futurework.md`.

### Not Allowed Yet
No expansion planning before certification.

### Minute-Granular Steps
1. P5.1 (20m): Evaluate each criterion.
2. P5.2 (10m): Record PASS/FAIL with evidence.
3. P5.3 (15m): Create or withhold `futurework.md` accordingly.
