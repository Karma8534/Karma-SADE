# BREAK_REPORT

Recursive break/fix log for `jprop6` hardening.

| ID | Phase/Scenario Attacked | How It Broke | Why It Broke | Failure Class | Fix Applied | New Guardrail |
|---|---|---|---|---|---|---|
| B-01 | Phase 0 inventory parsing | TSV was not machine-parseable | Delimiter written as literal `\t` | Proof | Regenerated with true tab delimiters | Parseability check in simulation notes |
| B-02 | Phase 0 runtime packet | Surface probe output too noisy/truncated | Raw JSON dump without summary keys | Runtime | Added concise summary probes (`surface_keys`, `spine_error`) | Runtime summary required in proof |
| B-03 | Contradiction extraction | Claim tables alone missed non-claim contradictions | Over-reliance on keyword extraction | Architectural | Added manual contradiction ledger with line refs | Contradiction ledger mandatory gate |
| B-04 | Phase 1 continuity contract | Contract lacked explicit invalid-version failure behavior | Positive-path bias | Continuity | Added invalid schema tests in strategy | Negative continuity tests required |
| B-05 | Phase 2 preload boundary | Risk of adding non-foundation IPC methods | Scope creep pressure | Governance | Added proof check asserting forbidden shell capability | Preload capability whitelist |
| B-06 | Phase 3 scaffold messaging | Scaffold could be mistaken for full app | Missing honesty banner | UX/Proof | Added fallback honesty warning + README constraints | “No overclaim” explicit gate |
| B-07 | Watcher control assumption | Watchers implied closure authority | Historic docs over-ascribed watcher reliability | Governance | Demoted watchers to advisory-only for phase closure | Watcher false-positive tests |
| B-08 | Plan sequencing | Expansion concepts leaked into foundation | Inherited plan sprawl | Sequencing | Reordered to strict Phase 0→1→2→3 foundation chain | “Not allowed yet” blocks each phase |
| B-09 | Runtime truth trust | Status tables could still self-certify | Legacy “live/deployed” language density | Runtime/Proof | Forced command artifact references in PROOF | Claim-to-proof mapping test |
| B-10 | Inbox primitive ingestion | Existing `.error.txt` implied failed ingest path | Prior transport failure unresolved | Runtime | Performed direct PDF extraction into artifacts | Ingestion-failure evidence retained |
| B-11 | Futurework timing | Risk of writing future phases before certification | Process shortcut tendency | Governance | Locked futurework behind explicit certification PASS | Gate R enforcement |
| B-12 | Hidden dependency risk | Missing references in canonical docs remained implicit | No explicit path drift ledger | Architectural | Added referenced path manifest with missing tokens | Path-drift audit in Phase 0 |
| B-13 | Phase 1 continuity negatives | Contract checks initially validated only positive sample | Negative-path under-specification | Continuity/Proof | Added executable `tests/break_check.js` and integrated npm script | Negative envelope checks required for certification |

## Regression Hooks Added
1. Re-run parseability check for generated artifacts.
2. Re-run proof script for scaffold capability boundaries.
3. Re-run continuity contract negative-case checks.
4. Re-run watcher false-positive scenario checks.
5. Re-run runtime probe packet before certification refresh.
