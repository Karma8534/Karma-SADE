# ARKNEXUS ASCENDANCE = 100 — MERGED BUILD + VERIFY PLAN v6 (hardened, single source)

PLAN_VERSION: v6
PLAN_FILE: C:\Users\raest\Documents\Karma_SADE\docs\For Colby\cxArkNexusv4Prop1.md
PLAN_SHA256: <computed by init script from this file on disk; mismatch at FINAL_GATE = INVALID>
DIRECTIVE_VERSION_BOUND: v6
DIRECTIVE_SHA256_EXPECTED: <recorded by init script at Phase 0>
PLAN_STATUS: red-team hardened (anti-cheat + build-complete + verify-complete + deploy-complete)

## 0) Completeness mandate (new hard rule)

From this revision forward, every requested prompt/plan MUST include everything required for full delivery:
- build
- test
- verify
- deploy
- ship
- production-ready
- 100%

No verification-only plan is allowed if required code/harness/verifier behavior is missing.
If a gate cannot pass because implementation is missing, implementation work is mandatory in the same canonical plan.

## 1) Scope and terminal state

Terminal state = SHIPPED, where SHIPPED is defined ONLY by verifier output:
- `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-final-gate.ps1`
- exit code `0`
- FINAL_GATE all required fields true
- all 14 gates latest status VERIFIED in one uninterrupted real run

This plan's terminal state = system is built so verifier can reach SHIPPED without code/harness repair, without priming, and without prose substitutes.

SHIPPED is NOT claimed by this plan text. It is claimed only by verifier stdout.

Canonical surfaces only (CLAUDE.md table). No new truth stores.

## 2) Contract split (explicit)

A. BUILD CONTRACT
- implement missing production behavior
- implement/fix harnesses
- implement verifier + pre-commit enforcement
- make required tests pass

B. VERIFY CONTRACT
- run nonce-bound probes
- emit immutable evidence
- run verifier final gate

Completion requires A + B in the same governed execution.

## 3) Label discipline and invariants

Labels used throughout (P113 locked):
- VERIFIED | FAIL | BLOCKED
- INFERRED banned in verifier-owned outputs

Banned in verifier-owned outputs:
- likely, should, probably, close enough, done-ish, implied, assumed,
  effectively, essentially, in practice, approximately, basically, mostly,
  seems, appears to, close to, near enough

Invariants:
- P027: no git worktrees; no Agent(isolation:"worktree"); no EnterWorktree.
- P059/P060: one active plan.
- P064: every PITFALL triggers required dual-write before next action.
- P089: prior-session claims are not proofs.
- P113: INFERRED is not ground truth.
- Honesty contract: no completion claim without machine proof.

## 4) Budget and circuit breakers

- Hard turn cap: 60 turns of execution after Phase 0 start.
- Per-task failure cap: same task FAIL 3x => STOP + escalation + SOVEREIGN_AUTH required.
- Per-phase wall-clock cap: 90 minutes. Exceeds => ESCALATE.
- Total artifact budget: <= 50 MB under `C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-{run_id}\`.

## 5) Pre-work ledger (current ground truth, 2026-04-21)

Closed-binary gates at baseline (must still be re-probed at final):
- G11_QUARANTINE_CLEANUP: baseline probe recorded in this session.
- G13_FOCUS_GATE_UNLOCK: baseline probe recorded in this session.

Open gates requiring BUILD work before honest VERIFIED is possible:
- G1 data-hydration-state + data-session-id DOM attrs: NOT IN CODE.
- G2 __bootMetrics session nonce + strict latest-read proof path: PARTIAL / NOT PROVEN.
- G2 LevelDB latest-entry read behavior: NOT PROVEN deterministic under current harness.
- G3 real hub browser CDP flow: HARNESS EXISTS BUT NOT COMPLIANT (API substitution path).
- G4 40-concurrent stress harness: MISSING.
- G4 cc_server_p1.py atomic write-then-rename with explicit fsync+rename primitive: NOT IMPLEMENTED/PROVEN.
- G5 SlashCommandPicker compliant proof path: HARNESS EXISTS BUT NON-COMPLIANT (store injection) + data-picker-open attr missing.
- G6 fresh Chromium profile launcher: NOT IMPLEMENTED as required gate proof path.
- G7 first-paint ritual-row render: NOT PROVEN as first-paint criterion.
- G8 uninterrupted recorder: PARTIAL ARTIFACTS; full compliant mp4 or strict step-01..12 sequence not proven.
- G9 dual-write wrapper with strict roundtrip confirm: NOT IMPLEMENTED as required contract utility.
- G10 pre-commit ascendance scope-whitelist + ascendance secret-scan policy + memory schema gate: NOT IMPLEMENTED.
- G12 compose.hub.yml sha parity + health checks: NOT AUTOMATED in ascendance verifier flow.
- G14 paint metric schema enforcement in verifier: VERIFIER MISSING.

Non-gate drift:
- Working tree may include unrelated dirt. Use scoped-delta enforcement (baseline->delta), not naive absolute-clean requirement.

## 6) Phase breakdown

All phases are sequential. No skip.
Each phase has: goal, tasks, acceptance (binary), rollback.

### PHASE 0 — freeze, archive, bootstrap (budget: 4 turns)

Goal:
- establish deterministic plan-run context

Tasks:
0.1 Capture baseline git porcelain snapshot to plan evidence.
0.2 Archive old pointer plan if present:
- `C:\Users\raest\Documents\Karma_SADE\Karma2\PLAN.md` -> `PLAN-ARCHIVED-{utc}.md`
- rewrite `C:\Users\raest\Documents\Karma_SADE\Karma2\PLAN.md` pointer to this file.
0.3 Verify ffmpeg availability (`ffmpeg -version`). Missing => install or BLOCKED.
0.4 Snapshot sha256 of:
- every `C:\Users\raest\Documents\Karma_SADE\Scripts\phase*-harness.ps1`
- every `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-*.ps1`
- `C:\Users\raest\Documents\Karma_SADE\.claude\settings.local.json`
- `C:\Users\raest\Documents\Karma_SADE\.git\hooks\pre-commit` (if exists)
0.5 Snapshot vault-neo `compose.hub.yml` sha256 baseline via ssh.
0.6 Create `C:\Users\raest\Documents\Karma_SADE\evidence\plan-run-{run_id}\` and write `plan.session.json`.
0.7 Dual-write DIRECTION: plan v6 started.

Acceptance:
- plan.session.json exists
- phase0 snapshot exists
- dependency checks pass or explicit BLOCKED

Rollback:
- restore archived PLAN pointer if phase aborted before Phase 1

### PHASE 1 — red tests + skeletons (budget: 6 turns)

Goal:
- create failing tests first and callable skeleton scripts

Tasks:
1.1 Write `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-init-run.ps1` skeleton.
1.2 Write `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-final-gate.ps1` skeleton.
1.3 Write `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-dual-write.ps1` skeleton.
1.4 Write tests under `C:\Users\raest\Documents\Karma_SADE\Tests\ascendance\`:
- test_init_creates_files
- test_final_gate_detects_banned_label
- test_final_gate_detects_missing_sha256
- test_final_gate_detects_stale_verified_utc
- test_dual_write_roundtrip
- test_precommit_scope_whitelist
- test_precommit_secret_scan
- test_precommit_memory_md_schema
- test_leveldb_scraper_reads_latest
- test_stress_40_parallel_no_loss
- test_fresh_browser_profile_unique
- test_ritual_recorder_monotonic
- test_harness_sha_snapshot_tamper_detect
1.5 Commit Phase 1 atomically.

Acceptance:
- all target tests exist and are red
- all skeleton scripts callable

Rollback:
- revert Phase 1 commit

### PHASE 2 — code repairs (budget: 12 turns)

Goal:
- implement production behavior required for gate satisfiability

Tasks:
2.1 Frontend root emits `data-hydration-state`.
2.2 Frontend root emits `data-session-id` from run/session source.
2.3 SlashCommandPicker emits `data-picker-open` while visible.
2.4 Extend boot metrics contract with strict session nonce and boot-start timestamp.
2.5 Ensure ritual-required history availability for first-paint criterion (no delayed-only loophole).
2.6 Implement atomic session persistence primitive in `C:\Users\raest\Documents\Karma_SADE\Scripts\cc_server_p1.py`:
- tmp write
- flush/fsync
- atomic rename
- explicit comment marker for verifier code citation
2.7 Rework tracker contract in `C:\Users\raest\Documents\Karma_SADE\.claude\hooks\arknexus-tracker.py`:
- completion derived from current run evidence, not stale cache
2.8 Add deterministic latest-reader helper for local storage/session metrics path.
2.9 Rebuild frontend.
2.10 Rebuild tauri executable.
2.11 Flip matching red tests to green.

Acceptance:
- frontend build succeeds
- tauri build succeeds
- mapped tests pass

Rollback:
- revert Phase 2 commit and restore prior build artifacts

### PHASE 3 — harness implementation/repair (budget: 10 turns)

Goal:
- compliant harnesses for every required probe

Tasks:
3.1 Rewrite phase1 cold-boot harness with SESSION_ID param and strict latest metrics proof.
3.2 Rewrite phase2 parity harness for real browser/CDP hub proof path.
3.3 Add `phase2-stress-harness.ps1` for G4.
3.4 Rewrite phase3 family/whoami harness to keyboard-flow-only; remove all store injection.
3.5 Add ritual recorder harness:
- mp4 mode via ffmpeg or strict step-01..12 PNG sequence
3.6 Rewrite ritual harness for fresh browser profile + nonce-bound ritual phrasing.
3.7 Add independent verifier script for cross-tool-family checks.
3.8 Add `# HARNESS_GATE: G#` headers and enforce mapping in verifier.

Acceptance:
- harnesses exist and run
- no-shortcuts violations eliminated
- harness-related tests pass

Rollback:
- revert Phase 3 commit

### PHASE 4 — verifier + hooks + enforcement (budget: 8 turns)

Goal:
- machine-enforced final gate and commit policy

Tasks:
4.1 Implement full `ascendance-final-gate.ps1`:
- session and evidence file checks
- sha recompute checks
- timestamp freshness checks
- banned-label scan (scope pinned)
- binary-fixed gate re-probes
- FINAL_GATE block emission
4.2 Implement pre-commit enforcement:
- ascendance scope whitelist
- secret scan two-pass policy
- memory schema requirement for ascendance-run commits
4.3 Implement dual-write wrapper roundtrip confirm logic.
4.4 Implement idempotent hook installer script.
4.5 Flip verifier/hook tests green.

Acceptance:
- positive fixture passes
- negative fixtures fail for each expected reason

Rollback:
- revert Phase 4 and uninstall hooks

### PHASE 5 — end-to-end dry run (budget: 6 turns)

Goal:
- prove run can pass before claiming real shipment

Tasks:
5.1 init dry run
5.2 reverse stubs
5.3 forward attempts all gates
5.4 run final gate in dry mode
5.5 close residual FAIL/BLOCKED items
5.6 loop until dry mode clean

Acceptance:
- dry final gate reports all required true in dry context

Rollback:
- remove dry run evidence and iterate fixes

### PHASE 6 — deploy parity pre-work (budget: 4 turns)

Goal:
- ensure remote parity and health before real run closure

Tasks:
6.1 sync deploy artifacts to vault-neo
6.2 verify compose hash parity
6.3 verify container health
6.4 verify /health and authenticated /v1/chat

Acceptance:
- parity + health all pass

Rollback:
- restore previous remote image/tag

### PHASE 7 — real directive execution (budget: 15 turns)

Goal:
- execute real ascendance run to verifier success

Tasks:
7.1 verify directive sha binding
7.2 init real ascendance run
7.3 reverse + forward execution G1..G14
7.4 enforce 3-fail circuit breaker per gate
7.5 run final verifier
7.6 emit FINAL_GATE verbatim from verifier only

Acceptance:
- verifier exit 0
- FINAL_GATE all true

Rollback:
- return to residual-fix phases

### PHASE 8 — ship + persist (budget: 5 turns)

Goal:
- finalize commit/push/parity/memory/tracker/final proof

Tasks:
8.1 update MEMORY.md ascendance schema section
8.2 stage allowed scope, run hook, commit
8.3 push and verify remote head
8.4 verify vault-neo head parity
8.5 run tracker in-session
8.6 final dual-write PROOF
8.7 re-probe G11/G13 and append evidence

Acceptance:
- heads aligned local/origin/vault
- tracker in-session shipped state
- final dual-write confirmed

Rollback:
- revert shipped commit + remote rollback

## 7) Dual-write schedule (plan-wide)

Per phase:
- start => DIRECTION dual-write
- end => PROOF dual-write
- failure => PITFALL dual-write

Gate-level dual-writes must follow verifier contract.

## 8) File map (plan-produced)

Scripts (new/rewritten):
- `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-init-run.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-final-gate.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-dual-write.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-independent-verify.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\install-ascendance-hooks.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\leveldb_latest.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\phase1-cold-boot-harness.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\phase2-parity-harness.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\phase2-stress-harness.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\phase3-family-harness.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\ritual-recorder.ps1`
- `C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-ritual-harness.ps1`

Frontend:
- `C:\Users\raest\Documents\Karma_SADE\frontend\src\store\karma.ts`
- `C:\Users\raest\Documents\Karma_SADE\frontend\src\app\layout.tsx` (or root equivalent)
- `C:\Users\raest\Documents\Karma_SADE\frontend\src\app\page.tsx`
- `C:\Users\raest\Documents\Karma_SADE\frontend\src\components\SlashCommandPicker.tsx`

Backend:
- `C:\Users\raest\Documents\Karma_SADE\Scripts\cc_server_p1.py`

Hooks:
- `C:\Users\raest\Documents\Karma_SADE\.git\hooks\pre-commit`

Evidence dirs:
- `C:\Users\raest\Documents\Karma_SADE\evidence\plan-run-{run_id}\`
- `C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-{run_id}\`

Docs:
- `C:\Users\raest\Documents\Karma_SADE\docs\For Colby\ascendance-directive-v6.md`
- `C:\Users\raest\Documents\Karma_SADE\.gsd\phase-ascendance-build-CONTEXT.md`
- `C:\Users\raest\Documents\Karma_SADE\.gsd\phase-ascendance-build-PLAN.md`
- `C:\Users\raest\Documents\Karma_SADE\.gsd\phase-ascendance-build-SUMMARY.md`
- `C:\Users\raest\Documents\Karma_SADE\Karma2\PLAN.md`
- `C:\Users\raest\Documents\Karma_SADE\Karma2\PLAN-ARCHIVED-{utc}.md`

## 9) Escalation matrix

- Per-task 3x FAIL => STOP + PITFALL + SECTION_8_ESCALATION record + await SOVEREIGN_AUTH.
- 60-turn cap reached => STOP + escalate.
- plan_sha mismatch mid-plan => INVALID.
- directive_sha mismatch in real run => INVALID.
- harness/settings sha drift mid-run => FAIL/INVALID and reset required.

## 10) Plan-level acceptance (binary)

Plan complete only when all are true:
- every phase acceptance VERIFIED
- real-run verifier exit code 0
- all 14 gates VERIFIED
- banned label hits = 0 in verifier-owned outputs
- dual-write proof/decision coverage present
- SHIPPED emitted exclusively by verifier stdout

PLAN_FINAL_GATE (printed by verifier/plan summarizer, never hand-typed):
PLAN_FINAL_GATE:
- directive_verifier_exit:        0
- all_14_directive_gates:         VERIFIED
- plan_phase_acceptance:          VERIFIED
- banned_label_hits:              0
- session_digest:                 {hex}
- plan_sha256:                    {hex}
- directive_sha256:               {hex}
- turn_count:                     <= 60
- memory_md_schema_valid:         true
- git_scope_clean_and_pushed:     true
- vault_parity_verified:          true
- tracker_shipped_in_session:     true

Any field false => plan INVALID => Section 9 escalation.

## 11) Red-team break matrix (must pass before REAL run)

Each break attempt below must be executed against the plan implementation. Any surviving break => return to BUILD phases.

- BR1 fake completion by tracker cache:
  - expected defense: verifier is sole completion authority; tracker advisory only.
- BR2 stale evidence replay:
  - expected defense: session nonce + mtime/session-window checks + sha recompute.
- BR3 binary artifact nonce omission:
  - expected defense: artifact manifest binds sha+session_id+gate_id.
- BR4 API substitution for browser gate:
  - expected defense: CDP/network artifacts required for browser-designated gates.
- BR5 store injection for UI proof:
  - expected defense: harness asserts keyboard flow only and scanner blocks store mutation patterns.
- BR6 mid-run harness/verifier tamper:
  - expected defense: script snapshot hash drift detection => INVALID.
- BR7 dirty monorepo false fail / hidden drift:
  - expected defense: scoped baseline-delta enforcement.
- BR8 secret leak in staged files:
  - expected defense: pre-commit secret scan policy blocks commit.
- BR9 dual-write omission:
  - expected defense: gate cannot close without roundtrip confirmations.
- BR10 ritual evidence gap:
  - expected defense: strict step 01..12 coverage or single uninterrupted mp4 validation.

Acceptance:
- all break attempts produce expected defense behavior.

## 12) Command playbook (minimum executable commands)

Phase 0 bootstrap:
- `ffmpeg -version`
- `git status --porcelain`
- `py -3 - <<'PY' ... sha snapshot generator ... PY` (or equivalent script)

Phase 1 tests (red):
- `pytest -q C:\Users\raest\Documents\Karma_SADE\Tests\ascendance`

Phase 2 build:
- `npm --prefix C:\Users\raest\Documents\Karma_SADE\frontend run build`
- `cargo tauri build --manifest-path C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\Cargo.toml --no-bundle`

Phase 3 harness checks:
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\phase1-cold-boot-harness.ps1 -WhatIf`
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\phase2-parity-harness.ps1 -WhatIf`
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\phase2-stress-harness.ps1 -WhatIf`
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\phase3-family-harness.ps1 -WhatIf`
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-ritual-harness.ps1 -WhatIf`

Phase 4 verifier/hook:
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\install-ascendance-hooks.ps1`
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-final-gate.ps1 --fixture happy`
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-final-gate.ps1 --fixture fail-banned-label`

Phase 6 deploy parity:
- `ssh vault-neo "cd /home/neo/karma-sade && git rev-parse HEAD"`
- `ssh vault-neo "docker ps --format '{{.Names}} {{.Status}}'" `
- `curl -sf https://hub.arknexus.net/health`
- `curl -sf -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"message\":\"ping\",\"stream\":false}" https://hub.arknexus.net/v1/chat`

Phase 7/8 real run and ship:
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-init-run.ps1 --real`
- `powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\ascendance-final-gate.ps1`
- `git push origin main`
- `ssh vault-neo "cd /home/neo/karma-sade && git pull && git rev-parse HEAD"`

## 13) Production-ready criteria (beyond gate pass)

Production-ready is true only if ALL are true:
- REAL run FINAL_GATE all true.
- 30-minute soak with watchdog active has no crash/restart loop and no repeated unhandled exceptions.
- chat mouth route and fallback policy match intended production policy and survive one forced fallback test.
- `/health`, `/v1/model-policy`, `/v1/surface`, `/v1/session/{id}`, `/v1/coordination/recent` all return expected schema under load sample.
- deployment parity confirmed across local, origin/main, and vault-neo HEAD.
- recovery path validated: restart nexus + watchdog + server and regain healthy state automatically.

## 14) Post-plan doctrine

- Keep `C:\Users\raest\Documents\Karma_SADE\Karma2\PLAN.md` pointed at this file until superseded.
- Any directive change must bump directive version and plan bindings.
- Any new harness must declare `# HARNESS_GATE: G#` and corresponding tests.
- Any banned-label list expansion must update verifier scanner in same commit.

## 15) Start command

1. Execute Phase 0.
2. Execute BUILD phases (1-4) fully.
3. Execute dry-run phase (5) to clean.
4. Execute deploy parity phase (6).
5. Execute real run phase (7).
6. Execute ship phase (8).
7. Claim completion only if verifier emits all-true FINAL_GATE and exit 0.

No prior-session evidence substitutions.
No INFERRED claims in verifier-owned outputs.
No hand-typed FINAL_GATE or PLAN_FINAL_GATE.
