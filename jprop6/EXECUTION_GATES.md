# EXECUTION_GATES

All gates are binary: PASS or FAIL.
No partial credit.

## Phase Gates

### Phase 0 Gates
| Gate | Condition | PASS Evidence | Status |
|---|---|---|---|
| P0-G1 | `nexus.md` fully line-audited | `artifacts/nexus_line_audit.tsv` has 915 lines | PASS |
| P0-G2 | `STATE.md` fully line-audited | `artifacts/state_line_audit.tsv` has 650 lines | PASS |
| P0-G3 | Contradiction ledger complete | `FORENSIC_AUDIT.md` contradiction table | PASS |
| P0-G4 | Runtime probes captured | `artifacts/runtime_checks.txt` | PASS |
| P0-G5 | Path-reference drift inventory captured | `artifacts/referenced_paths.tsv` | PASS |

### Phase 1 Gates
| Gate | Condition | PASS Evidence | Status |
|---|---|---|---|
| P1-G1 | Continuity schema exists | `MINIMAL_HARNESS/session_contract.schema.json` | PASS |
| P1-G2 | Contract-required keys explicit | Schema required fields present | PASS |
| P1-G3 | Negative continuity tests defined | `TEST_STRATEGY.md` continuity section | PASS |
| P1-G4 | Rollback condition explicit | `jprop6.md` Phase 1 rollback criteria | PASS |
| P1-G5 | Negative continuity checks executable | `MINIMAL_HARNESS/tests/break_check.js` + `command_log.txt` | PASS |

### Phase 2 Gates
| Gate | Condition | PASS Evidence | Status |
|---|---|---|---|
| P2-G1 | Secure preload bridge only | `MINIMAL_HARNESS/preload.js` API surface | PASS |
| P2-G2 | No forbidden capabilities in bridge | `scripts/proof_check.js` constraints | PASS |
| P2-G3 | Browser↔Electron parity tests defined | `TEST_STRATEGY.md` parity section | PASS |
| P2-G4 | Break scenarios documented | `PHASE_SIMULATIONS.md` + `BREAK_REPORT.md` | PASS |

### Phase 3 Gates
| Gate | Condition | PASS Evidence | Status |
|---|---|---|---|
| P3-G1 | Harness main process scaffold exists | `MINIMAL_HARNESS/main.js` | PASS |
| P3-G2 | Hub load target explicit | `main.js` uses `https://hub.arknexus.net` default | PASS |
| P3-G3 | Fallback path honest | `renderer/fallback.html` | PASS |
| P3-G4 | Syntax checks pass | `artifacts/command_log.txt` | PASS |
| P3-G5 | Proof check passes | `PASS: proof_check` in command log | PASS |
| P3-G6 | Contract check passes | `PASS: contract_check` in command log | PASS |
| P3-G7 | Break check passes | `PASS: break_check` in command log | PASS |

### Phase 4 Gates
| Gate | Condition | PASS Evidence | Status |
|---|---|---|---|
| P4-G1 | Watcher failure explicitly audited | `FORENSIC_AUDIT.md` + `watcher_failure_evidence.tsv` | PASS |
| P4-G2 | Watcher authority demoted | `FOUNDATION_DECISION.md` watcher decision | PASS |
| P4-G3 | Watcher break tests defined | `TEST_STRATEGY.md` watcher failure tests | PASS |

### Phase 5 Gates
| Gate | Condition | PASS Evidence | Status |
|---|---|---|---|
| P5-G1 | Ground-truth certification completed | `PROOF.md` certification section | PASS |
| P5-G2 | Future work created only after PASS | `PROOF.md` Gate R ordering evidence + `futurework.md` | PASS |

## Mission Gates A-R

| Gate | Requirement | Status |
|---|---|---|
| A | `nexus.md` fully audited line by line | PASS |
| B | `STATE.md` fully audited line by line | PASS |
| C | Inbox files audited for relevant primitives | PASS |
| D | Contradiction ledger complete | PASS |
| E | Foundation extracted and defended | PASS |
| F | `jprop6.md` created | PASS |
| G | Every phase has objective/scope/dependencies/anti-goals/deliverables/proof/break-tests/exit criteria | PASS |
| H | Minimal Electron harness scaffold created | PASS |
| I | Scaffold honesty preserved | PASS |
| J | Every phase simulated | PASS |
| K | Every phase attacked and fixed | PASS |
| L | Watcher failure explicitly audited | PASS |
| M | `PRIMITIVES.md` exhaustive for audited corpus | PASS |
| N | `BREAK_REPORT.md` exhaustive for jprop6 phases | PASS |
| O | `PROOF.md` complete | PASS |
| P | No obvious architectural contradiction remains in jprop6 | PASS |
| Q | `GROUND-TRUTH VERIFIED 100% = YES` | PASS |
| R | `futurework.md` created only after Gate Q | PASS |

## Gate Enforcement Rule
If any gate flips to FAIL on re-run, mark foundation as uncertified and roll back to the earliest failing phase.
