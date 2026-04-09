# PHASE_SIMULATIONS

## Phase 0 Simulation

### Initial Simulation
1. Run inventory and line-audit generation.
2. Build contradiction ledger.
3. Run runtime probes.

### What Broke
1. Initial TSV generation used literal `\t`, producing unusable inventory tables.
2. Runtime probe serialization initially too deep/noisy for direct contradiction use.

### Hidden Dependencies Found
1. Audit tooling itself must be validated before trusting outputs.
2. Runtime probes need concise summary extraction, not raw full JSON only.

### False Assumptions Found
1. “Any generated inventory file is valid by default.”

### Premature Expansion Found
1. None.

### Fix Applied
1. Regenerated manifests using real tab delimiters.
2. Added summary probes (`surface_keys`, `spine_error`) to runtime artifact.

### Re-run Result
Phase 0 artifacts became parseable and contradiction-ready.

---

## Phase 1 Simulation

### Initial Simulation
1. Define continuity schema.
2. Check for required keys.

### What Broke
1. No explicit invalid-version handling test at first draft.

### Hidden Dependencies Found
1. Contract correctness depends on explicit negative-case policy.

### False Assumptions Found
1. “Presence of schema file implies enforceable continuity.”

### Premature Expansion Found
1. Attempt to include advanced compaction semantics too early.

### Fix Applied
1. Added explicit negative continuity tests in `TEST_STRATEGY.md`.
2. Added executable negative-case script `MINIMAL_HARNESS/tests/break_check.js`.
3. Deferred compaction behavior to futurework gates.

### Re-run Result
Continuity phase now has binary fail conditions, executable negative checks, and rollback semantics.

---

## Phase 2 Simulation

### Initial Simulation
1. Expose preload bridge for runtime/session methods.
2. Define parity tests.

### What Broke
1. Risk of preload scope creep into non-foundation capabilities.

### Hidden Dependencies Found
1. Need proof script checks to prevent accidental capability expansion.

### False Assumptions Found
1. “If preload exists, it is automatically minimal and safe.”

### Premature Expansion Found
1. Temptation to add shell/code-edit IPC.

### Fix Applied
1. Added `proof_check.js` assertion that forbids shell capability in scaffold.
2. Locked parity semantics in test strategy.

### Re-run Result
Bridge remained minimal and auditable.

---

## Phase 3 Simulation

### Initial Simulation
1. Build Electron scaffold targeting hub.
2. Add fallback page.
3. Add proof and contract checks.

### What Broke
1. Potential overclaim risk: scaffold could be mistaken for full merged app.

### Hidden Dependencies Found
1. Need explicit scaffold honesty language in README and fallback UI.

### False Assumptions Found
1. “If Electron launches hub URL, merged workspace is complete.”

### Premature Expansion Found
1. Integrating runtime mutation or orchestration controls.

### Fix Applied
1. Added explicit “foundation-only mode” messaging in fallback UI.
2. Added README honesty section and forbidden capability list.

### Re-run Result
Scaffold is minimal, testable, and non-deceptive.

---

## Phase 4 Simulation

### Initial Simulation
1. Treat watcher/governor layer as control plane.

### What Broke
1. Historical evidence includes watcher-chaos and unresolved blocker churn despite watcher presence.

### Hidden Dependencies Found
1. Closure authority must be separated from watcher telemetry.

### False Assumptions Found
1. “Watcher running => foundation safe to advance.”

### Premature Expansion Found
1. Assigning watcher autonomous gate-close authority.

### Fix Applied
1. Demoted watcher role to advisory in `FOUNDATION_DECISION.md`.
2. Added watcher failure tests in `TEST_STRATEGY.md`.

### Re-run Result
Governance model now resists watcher false positives.

---

## Phase 5 Simulation

### Initial Simulation
1. Evaluate 15 ground-truth conditions.

### What Broke
1. None after prior phase hardening; all conditions had explicit evidence links.

### Hidden Dependencies Found
1. Certification quality depends on continuous re-run discipline.

### False Assumptions Found
1. “Certification is permanent.” (false; must be revalidated on drift)

### Premature Expansion Found
1. Starting futurework before certification complete.

### Fix Applied
1. Kept `futurework.md` generation behind explicit PASS in certification section.

### Re-run Result
Certification completed with evidence-backed PASS.
