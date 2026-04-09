# TEST_STRATEGY

## 1) Plan-Level Tests

### T-PLAN-01: Claim-to-proof mapping
- Goal: every completion claim maps to evidence command/artifact.
- Pass: no “done” claim without file+command evidence.
- Fail trigger: any unreferenced completion statement.

### T-PLAN-02: Contradiction closure
- Goal: every major contradiction appears in ledger.
- Pass: contradiction table covers workspace, continuity, watcher, and phase-order conflicts.
- Fail trigger: any newly found contradiction not logged.

### T-PLAN-03: Hidden dependency detection
- Goal: phase dependencies explicit.
- Pass: each phase in `jprop6.md` has dependency and anti-goals.
- Fail trigger: downstream phase requires undeclared upstream artifact.

## 2) Scaffold-Level Tests

### T-SCAF-01: JS syntax integrity
- Command: `node --check main.js`, `node --check preload.js`, etc.
- Pass: zero syntax errors.

### T-SCAF-02: Harness honesty check
- Command: `node scripts/proof_check.js`
- Pass: scaffold includes hub load + secure boundary, forbids shell capability.

### T-SCAF-03: Continuity envelope sample check
- Command: `node tests/contract_check.js`
- Pass: sample satisfies required schema keys.

### T-SCAF-04: Negative continuity break checks
- Command: `node tests/break_check.js`
- Pass: malformed envelopes are rejected for missing `session_id`, bad `schema_version`, bad timestamp format, and invalid `source`.

## 3) Continuity Tests

### T-CONT-01: Required keys present
- Keys: `schema_version`, `written_at`, `session.session_id`, `workspace_id`, `source`.
- Pass: all present.
- Fail: any missing key.

### T-CONT-02: Invalid schema version
- Input: unknown `schema_version`.
- Expected: FAIL gate + rollback path.

### T-CONT-03: Corrupt envelope read
- Input: malformed JSON envelope.
- Expected: read returns null/error-safe handling; no silent success claim.

## 4) Browser↔Electron Parity Tests

### T-PAR-01: Shared field semantics
- Browser and Electron must interpret envelope keys identically.
- Pass: parity matrix unchanged.

### T-PAR-02: Write/read ordering
- Simulate browser write then electron read, and reverse.
- Pass: conflict behavior explicitly defined and deterministic.

### T-PAR-03: Surface mismatch handling
- If runtime probe says surface available but spine unavailable, state must remain explicit and degraded, not “all green.”

## 5) Watcher Failure Tests

### T-WAT-01: False-positive closure
- Scenario: watcher reports healthy while runtime gate fails.
- Expected: phase closure denied.

### T-WAT-02: Stale watcher output
- Scenario: watcher emits old success message.
- Expected: ignored for closure purposes.

### T-WAT-03: Watcher outage
- Scenario: watcher unavailable.
- Expected: no phase closure impact if direct proofs pass.

## 6) Runtime Truth Tests

### T-RT-01: Health endpoint
- Probe: `/health`.
- Pass: response reachable and parsable.

### T-RT-02: Surface endpoint keyset
- Probe: `/v1/surface`.
- Pass: keyset contains expected fields.

### T-RT-03: Spine dependency status
- Probe: `/v1/spine`.
- Pass: healthy OR explicit degraded status captured; no hidden assumption.

## 7) Regression Criteria
1. Any newly introduced undocumented dependency fails regression.
2. Any gate text changed without proof updates fails regression.
3. Any scaffold capability expansion without corresponding tests fails regression.
4. Any watcher authority escalation without governance decision revision fails regression.
