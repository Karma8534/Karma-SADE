# ARKNEXUS ASCENDANCE = 100 — MERGED BUILD + VERIFY PLAN v2 (>97% unconditional ship)

PLAN_VERSION: v2
PLAN_SHA256: <computed by init script from this file on disk; mismatch mid-run = INVALID>
DIRECTIVE_VERSION_BOUND: v3
DIRECTIVE_SHA256_EXPECTED: <recorded by init script at Phase 0>

## 0) Scope, terminal state, target

Terminal state = SHIPPED, emitted ONLY by Scripts/ascendance-final-gate.ps1 exit 0 with every field true and banned_label_hits=0.

Target success rate: >= 97% per fresh start. Achieved by preflight battery, flake-aware retry, dual-write queue fallback, checkpoint/resume, canary deploys, and pre-authorized auto-auth for narrow fix classes.

Residual <=3% risk: genuine infra outages (DigitalOcean down, Anthropic down, ISP cut) beyond local + P1 recovery. These force BLOCKED/resume; they do NOT produce false SHIPPED.

Canonical surfaces only (CLAUDE.md). No new truth stores.

Binary labels only (P113): VERIFIED | FAIL | BLOCKED. Banned list:
  INFERRED, likely, should, probably, close enough, done-ish, implied, assumed,
  effectively, essentially, in practice, approximately, basically, mostly, seems,
  appears to, close to, near enough.
Banned-label lint scope: evidence/** and MEMORY.md "## Ascendance Run" section ONLY.
Whitelist: the exact quoted-literal occurrences of the above tokens inside fenced code blocks of docs/ForColby/ascendance-directive-v3.md and this plan file — dictionary references, not assertions.

Invariants: P027, P059/P060, P064, P089, P113, CLAUDE.md honesty contract.

## 1) Budget, breakers, concurrency

- Hard turn cap: 120 execution turns after Phase 0 start. 121st turn = Sovereign escalate.
- Per-task fail cap: 3 logic-error FAILs on same task = STOP + PITFALL + bus escalation.
- Flake retry: network/CDP/ssh timeout or 5xx = retry up to 3x with 2/4/8s backoff before counting as a FAIL attempt.
- Phase wall-clock cap: 120 minutes each; exceed = ESCALATE.
- Artifact budget: <= 200 MB under evidence/.
- Parallelism declared: tasks in Phase 3 (3.1..3.5) can run in interleaved tool batches; tasks in Phase 6 serial (infra).

## 2) Auto-auth ledger (pre-approved fix classes)

Sovereign pre-authorizes these mid-run without further prompt:
  AA1: Harness typo / param error fix (single-file edit in Scripts/phase*-harness.ps1 or Scripts/ascendance-*.ps1).
  AA2: Flaky external endpoint retry (network/CDP/ssh timeout only, NOT semantic error).
  AA3: Frontend rollback to prior tag on smoke fail.
  AA4: Docker container restart on unhealthy status (single container).
  AA5: LevelDB scraper fallback to secondary reader.
  AA6: Dual-write queue drain on MCP/bus recovery.
  AA7: ESCALATION email via cc_gmail.send_to_colby(subject="ESCALATION: ...") on Section 8 trigger; enter active-poll mode (check_inbox every 5 min for up to 30 min) for Sovereign reply; resume inline on directive received.
Anything outside AA1..AA7 = full escalation (Section 8).

## 3) Preflight health battery (Phase 0.0, MANDATORY first action)

Scripts/ascendance-preflight.ps1 runs checks, auto-remediates where safe, emits evidence/plan-run-{run_id}/preflight.json:

PF01 ssh vault-neo echo ok                              auto-remed: ssh -o ConnectTimeout=10 retry 3x
PF02 MCP claude-mem save_observation roundtrip          auto-remed: restart local claude-mem worker once
PF03 POST /v1/coordination/post roundtrip via vault-neo auto-remed: retry 3x; if down, enable queue mode
PF04 hub chat token presence + age (< 7 days)           auto-remed: none; BLOCKED with owner=Sovereign
PF05 NTP clock skew vault-neo <-> P1 (< 5s)             auto-remed: w32tm /resync; BLOCKED if still > 5s
PF06 Chromium executable + CDP port free (9222)         auto-remed: kill orphan chrome; else BLOCKED
PF07 ffmpeg on PATH, gdigrab listable                   auto-remed: winget install Gyan.FFmpeg; else BLOCKED
PF08 node + npm present, frontend/node_modules warm     auto-remed: npm ci; else BLOCKED
PF09 cargo + rustc present                              auto-remed: none; BLOCKED with owner=Sovereign
PF10 docker reachable on vault-neo                      auto-remed: ssh restart docker once; else BLOCKED
PF11 Anthropic API 200 on /v1/models                    auto-remed: retry 3x; else BLOCKED
PF12 Disk free on P1 (>= 10 GB under Karma_SADE)        auto-remed: none; BLOCKED
PF13 Git remote reachable (git ls-remote origin HEAD)   auto-remed: retry 3x; else BLOCKED
PF14 Single-run lock free (evidence/.ascendance.lock)   auto-remed: abort if held; single-instance enforced
PF15 Gmail creds readable + IMAP/SMTP reachable         auto-remed: retry 3x; if down, AA7 degraded (chat-only mode)

Preflight result required: every check = PASS or explicit degraded mode. Any BLOCKED halts plan with explicit owner + remediation instruction. On re-run, checkpoint resumes at same phase.

## 4) Checkpoint / resume

Every phase completion writes: evidence/plan-run-{run_id}/phase-{N}-DONE.marker
  { phase: N, completed_utc, sha256_of_work_products, run_id, session_id }

On resume:
  1. Preflight re-runs (checkpoint does NOT bypass preflight).
  2. Read existing markers; skip phases whose marker validates.
  3. Reopen EVIDENCE_INDEX.json append mode.
  4. SESSION_ID is REGENERATED on resume; artifacts from prior session are not counted for final. Only phase markers persist (gate probes must re-run in new SESSION_ID unless marker is for build-phase work not tied to session nonce).

Build phases (0..6) are session-agnostic; their markers survive. Directive-v3 execution phases (7..8) are session-bound; always re-run in current SESSION_ID.

## 5) Dual-write queue (resilient ledger)

evidence/plan-run-{run_id}/dual-write-queue.jsonl — append-only, fsync after each line.

Every DECISION/PROOF/PITFALL/DIRECTION:
  1. Append to queue: { utc, type, gate, title, text, session_id, obs_id?, bus_id?, state }
  2. Best-effort attempt MCP + bus roundtrip. Success → update queue line state=confirmed with ids.
  3. Failure → queue line state=pending.

Drain:
  - Before FINAL_GATE, Scripts/ascendance-drain-queue.ps1 retries every pending line.
  - If MCP+bus still unreachable at FINAL_GATE → gate G9 BLOCKED. SHIPPED prohibited.
  - Successful drain with all lines state=confirmed → G9 eligible for VERIFIED.

## 6) Phase breakdown (build → ship)

All sequential unless marked parallel. Each phase: goal, tasks, acceptance, rollback, auto-remed.

### PHASE 0 — freeze, archive, bootstrap (budget: 5 turns)
0.0 Preflight battery (Section 3). Any BLOCKED halts here.
0.1 git stash push --include-untracked -m "pre-ascendance-drift-{utc}" for non-whitelist M-files. `git status --porcelain` empty.
0.2 Archive old Karma2/PLAN.md → Karma2/PLAN-ARCHIVED-{utc}.md. Rewrite Karma2/PLAN.md = pointer to this file.
0.3 Verify ffmpeg; install if needed.
0.4 Snapshot sha256: Scripts/phase*-harness.ps1, Scripts/ascendance-*.ps1, .claude/settings.local.json, .git/hooks/pre-commit, Karma2/cc-scope-index.md. Store in plan.session.json.snapshots.
0.5 Snapshot vault-neo compose.hub.yml sha256 + container list + docker ps Status.
0.6 Snapshot vault-neo git HEAD SHA (drift baseline).
0.7 Pause vault-neo batch_ingest cron: ssh vault-neo `crontab -l > /tmp/cron.bak && crontab -r` (restore at Phase 8.end).
0.8 Create evidence/plan-run-{run_id}/ + plan.session.json + phase-0-DONE.marker.
0.9 Dual-write DIRECTION.
Acceptance: preflight all PASS; tree clean; PLAN.md is pointer; snapshots present; cron paused.
Rollback: `git stash pop`; restore PLAN.md; ssh vault-neo `crontab /tmp/cron.bak`.

### PHASE 0.5 — architectural pre-flight audit (budget: 3 turns)
Scripts/ascendance-arch-audit.ps1 grep+probe:
  A01 grep frontend/src for data-hydration-state, data-session-id, data-picker-open. Absent is OK (Phase 2 adds); presence of conflicting attrs = BLOCKED.
  A02 grep Scripts/cc_server_p1.py for rename() call pattern; missing atomic path = auto-remed by Phase 2; note for targeted edit.
  A03 probe Tauri LevelDB format: run a 3-line sentinel parse; format change = BLOCKED with fix path.
  A04 probe hub.arknexus.net proxy route /v1/session/{id} 404 vs 200 matrix; if routing broken = escalate to Sovereign.
  A05 read frontend/package.json + Cargo.toml for known-broken version pins; flag.
Acceptance: audit report attached; zero BLOCKED structural findings OR every BLOCKED has documented fix owner.

### PHASE 1 — red tests + verifier/init skeletons (budget: 8 turns, parallel where marked)
1.1 Scripts/ascendance-init-run.ps1 (skeleton).
1.2 Scripts/ascendance-final-gate.ps1 (skeleton that exits 2).
1.3 Scripts/ascendance-dual-write.ps1 wrapper with queue mode.
1.4 Scripts/ascendance-drain-queue.ps1.
1.5 Scripts/ascendance-preflight.ps1 (if not built earlier; Phase 0.0 uses an interim version, Phase 1 consolidates).
1.6 Tests/ascendance/*.ps1 red tests (16 total):
   test_init_creates_files.ps1
   test_final_gate_detects_banned_label.ps1
   test_final_gate_detects_missing_sha256.ps1
   test_final_gate_detects_stale_verified_utc.ps1
   test_final_gate_self_synthetic_pass.ps1
   test_final_gate_self_synthetic_fail.ps1
   test_dual_write_roundtrip.ps1
   test_dual_write_queue_drain.ps1
   test_precommit_scope_whitelist.ps1
   test_precommit_secret_scan.ps1
   test_precommit_memory_md_schema.ps1
   test_leveldb_scraper_reads_latest.ps1
   test_leveldb_format_canary.ps1
   test_stress_40_parallel_no_loss.ps1
   test_fresh_browser_profile_unique.ps1
   test_ritual_recorder_monotonic.ps1
1.7 [PARALLEL] Phase 1.5 test-of-tests: broken-stub harness that INTENTIONALLY violates each predicate; assert corresponding red test FAILs against it.
1.8 Commit atomic "phase-ascendance-build 1: skeletons + 16 red tests + test-of-tests". Tag ascendance-build-p1.
Acceptance: all 16 red tests FAIL on real stubs, PASS on broken stubs (test-of-tests).
Rollback: `git reset --hard ascendance-build-p1~1`.

### PHASE 2 — code repairs (budget: 18 turns, parallel where marked)
[PARALLEL BATCH A — frontend]
2.1 data-hydration-state on <html>.
2.2 data-session-id on <html> from Tauri env NEXUS_SESSION_ID.
2.3 data-picker-open on SlashCommandPicker root.
2.4 __bootMetrics schema: session_id + boot_started_utc, persist to localStorage + window.__bootMetrics.
2.5 First-paint history pre-hydration from /v1/session/{id}.
[PARALLEL BATCH B — backend + tooling]
2.6 cc_server_p1.py atomic write-tmp + fsync + rename; marker comment; Scripts/test_cc_server_atomic_rename.py.
2.7 .claude/hooks/arknexus-tracker.py rewrite: compute from evidence/; cache banned; cache file deleted at every run start.
2.8 Scripts/leveldb_latest.ps1: returns LATEST entry for key, tested vs format canary.
[SERIAL — deploy]
2.9 npm run build in frontend/; tag frontend-out-{sha}.
2.10 cargo tauri build --no-bundle; tag binary-{sha}; record in evidence/plan-run-{run_id}/phase2-binary.json.
2.11 Smoke: launch Julian.exe, CDP read <html> attrs, confirm all three present, confirm __bootMetrics has session_id.
2.12 Every Phase 1 test mapped to this phase flips red → green.
Acceptance: all mapped red tests GREEN; binary smoke PASS; frontend rebuild exit 0.
Auto-remed: if cargo build fails, clean target/ once and retry.
Rollback: checkout previous frontend-out tag; restore prior julian.exe from backup dir.

### PHASE 3 — harnesses (budget: 14 turns, parallel)
[PARALLEL — each harness independent]
3.1 Scripts/phase1-cold-boot-harness.ps1 rewrite: SESSION_ID injection, leveldb_latest, independent verify.
3.2 Scripts/phase2-parity-harness.ps1 rewrite: diagnose prior history-match FAIL (systematic-debugging Phase 1-3); add SESSION_ID probe.
3.3 Scripts/phase2-stress-harness.ps1 new: 40 concurrent.
3.4 Scripts/phase3-family-harness.ps1 rewrite: CDP keyboard G5 + fresh browser G6 + CDP Network capture G3.
3.5 Scripts/ritual-recorder.ps1 new: mp4 OR pngseq; monotonic timestamps.
3.6 Scripts/ascendance-ritual-harness.ps1 rewrite: SESSION_ID in probe; wired to recorder; fresh browser.
3.7 Scripts/ascendance-independent-verify.ps1: different-tool-family cross-check per gate.
3.8 Every harness declares `# HARNESS_GATE: G#` header; verifier enforces mapping.
Acceptance: every harness -WhatIf dry-run prints its planned probe; every Phase 1 test for harnesses GREEN; independent verifier differs from harness by ZERO for the same input.
Rollback: `git revert ascendance-build-p3`.

### PHASE 4 — verifier + hooks + lint (budget: 10 turns)
4.1 Implement Scripts/ascendance-final-gate.ps1:
  - reads session.json, EVIDENCE_INDEX.json, PROBE_LOG.md, GAP_MATRIX.md, queue jsonl.
  - recomputes sha256; enforces SESSION_ID-in-artifact.
  - banned-label scan (scope pinned to evidence/** + MEMORY.md Ascendance section).
  - asserts harness_sha + settings_sha unchanged vs plan.session.json.snapshots.
  - re-probes binary-fixed gates (G11, G13) live.
  - checks tracker regenerated in-session.
  - emits FINAL_GATE block per directive v3 Section 9.2; exit 0 only when every field true.
4.2 .git/hooks/pre-commit:
  - scope whitelist (directive v3 G10).
  - two-pass secret scan, scope excludes tests/fixtures/ and Logs/.
  - ascendance-run commits require MEMORY.md staged + contains current SESSION_ID.
  - banned-label check in evidence/** and MEMORY.md Ascendance section.
4.3 Scripts/install-ascendance-hooks.ps1 idempotent installer.
4.4 [self-test] Scripts/ascendance-verifier-self-test.ps1: runs verifier against synthetic PASS fixture (expect exit 0) and 5 synthetic FAIL fixtures (expect exit 1 with specific reason each). All must pass self-test.
4.5 Lock verifier: sha256 verifier file into plan.session.json AFTER 4.4 passes.
Acceptance: verifier self-test PASS; pre-commit rejects all 4 mis-shaped commits (outside whitelist, secret, missing SESSION_ID, banned label).
Rollback: `git revert ascendance-build-p4`; hooks uninstalled via -Uninstall.

### PHASE 5 — end-to-end dry-run (budget: 8 turns)
5.1 Init dry run: Scripts/ascendance-init-run.ps1 --dry.
5.2 Reverse pass: planning stubs for all 14 gates.
5.3 Forward pass attempt_n=1 for every gate. Collect.
5.4 Drain dual-write queue.
5.5 Scripts/ascendance-final-gate.ps1 --dry. Exit code captured.
5.6 Any FAIL/BLOCKED: PITFALL dual-write; record in phase5-residual.md; return to Phase 2/3 as needed; loop.
Acceptance: dry verifier exit 0; zero banned-label hits; every gate VERIFIED in dry index.
Rollback: clear dry run dir; remediate; re-run.

### PHASE 6 — deploy pre-work (budget: 6 turns)
6.1 Token freshness re-probe (< 7 days).
6.2 scp frontend/out to vault-neo build-context path; karma-hub-deploy skill flow; tag prior image `hub-bridge:pre-{run_id}`.
6.3 Canary: bring up new hub-bridge, curl /health + /v1/chat. Bad = AA3 rollback to prior tag.
6.4 compose.hub.yml sha equality enforced; sync if drift (P004 — explicit per-file cp, never cp -r).
6.5 Re-probe vault-neo HEAD SHA; unchanged vs Phase 0 snapshot.
6.6 Smoke battery: /health 200, /v1/chat 200, container healthchecks all healthy.
Acceptance: local sha == remote sha for compose; containers Up+healthy; canary green.
Rollback: AA3 deploy prior tag image; ssh vault-neo docker compose up -d --force-recreate hub-bridge.

### PHASE 7 — directive v3 REAL execution (budget: 25 turns)
7.0 NTP re-check, token re-check.
7.1 Verify directive_sha256 of docs/ForColby/ascendance-directive-v3.md matches plan.session.json expected.
7.2 Scripts/ascendance-init-run.ps1 --real → fresh SESSION_ID + evidence/ascendance-run-{run_id}/.
7.3 Reverse pass + forward pass per directive v3 Section 10. Flake distinction applied; auto-auth AA1/AA2/AA4/AA5/AA6 permitted inline.
7.4 Circuit breaker per gate_id 3x logic-error FAIL = STOP + Sovereign escalate (AA7 email + chat).
7.5 Any SECTION_8_ESCALATION line in PROBE_LOG blocks further work on that gate until SOVEREIGN_AUTH line appears.
7.6 All 14 gates latest VERIFIED → drain queue → run ascendance-final-gate.ps1.
Acceptance: verifier exit 0; FINAL_GATE block all true; banned_label_hits = 0.
Rollback: reset to `ascendance-build-p6` tag; re-assess residuals; retry Phase 5 then 7.

### PHASE 8 — ship + persist (budget: 6 turns)
8.1 Write MEMORY.md `## Ascendance Run {run_id}` per directive v3 Section 9.1 schema.
8.2 Stage whitelist only; pre-commit hook enforces; commit `feat(ascendance-run): {run_id} shipped — 14 gates VERIFIED`.
8.3 Push origin/main; `git ls-remote origin main` == local HEAD.
8.4 ssh vault-neo `cd /home/neo/karma-sade && git pull && git log -1 --format=%H` == local HEAD; 3x retry with 5s backoff.
8.5 Restore vault-neo cron: ssh vault-neo `crontab /tmp/cron.bak` (reversing Phase 0.7).
8.6 Run arknexus-tracker.py; confirm SHIPPED + last_run within 120s.
8.7 Final dual-write PROOF "Ascendance run {run_id} SHIPPED; verifier exit 0; session_digest={hex}".
8.8 Re-probe G11 + G13 live; append fresh entries.
8.9 Release single-run lock.
Acceptance: porcelain empty; local==origin==vault-neo HEAD; tracker SHIPPED in-session; final dual-write confirmed; G11/G13 re-probe verified within 600s; cron restored.
Rollback: `git revert` ship commit; ssh vault-neo `git reset --hard HEAD^`; restore prior tracker state; restore cron if re-failed.

## 7) Failure mode → handling matrix

Flake (network/CDP/ssh 5xx/timeout)     → retry 3x with backoff; attempt_n not incremented.
Logic error in probe                    → FAIL counted; systematic-debugging Phase 1-3 before retry.
MCP/bus outage                          → queue fallback; G9 BLOCKED until drained.
Token expired                           → BLOCKED with owner=Sovereign; AA7 email.
Chromium hang                           → kill+retry.
Frontend smoke fail                     → AA3 rollback to prior tag.
Container unhealthy                     → AA4 restart single container.
LevelDB format change                   → AA5 fallback scraper; if still fail = BLOCKED.
Verifier tamper                         → INVALID; halt immediately.
Plan sha mismatch                       → INVALID.
Architectural break                     → Section 8 escalate, SOVEREIGN_AUTH required.
Session death / context compaction      → checkpoint markers allow resume; preflight re-runs.
vault-neo HEAD drift                    → Phase 8 predicate fails; retry pull; if persistent, BLOCKED.
>120 turn cap                           → Sovereign escalate.
Batch cron interferes                   → paused at Phase 0.7, restored Phase 8.5.

## 8) Escalation matrix (narrow)

SOVEREIGN_AUTH REQUIRED for:
  - Any change outside directive v3 Section 5 whitelist.
  - Any commit outside commit-scope whitelist.
  - Any token refresh.
  - Any Docker image change beyond AA3/AA4.
  - Any break surfaced by Phase 0.5 architectural audit.
  - Any plan_sha256 / directive_sha256 change.

Auto-handled (AA1..AA7):
  - Harness typos, flake retries, canary rollback, container restart, scraper fallback, queue drain, ESCALATION email + active-poll.

## 9) File map (complete, plan-produced)

Scripts/ (new or rewritten):
  ascendance-init-run.ps1
  ascendance-final-gate.ps1
  ascendance-dual-write.ps1
  ascendance-drain-queue.ps1
  ascendance-preflight.ps1
  ascendance-arch-audit.ps1
  ascendance-independent-verify.ps1
  ascendance-verifier-self-test.ps1
  install-ascendance-hooks.ps1
  leveldb_latest.ps1
  phase1-cold-boot-harness.ps1            (rewrite)
  phase2-parity-harness.ps1               (rewrite)
  phase2-stress-harness.ps1               (new)
  phase3-family-harness.ps1               (rewrite; G3+G5+G6)
  ritual-recorder.ps1                      (new)
  ascendance-ritual-harness.ps1           (rewrite)
  test_cc_server_atomic_rename.py         (new)

Tests/ascendance/ — 16 red tests + test-of-tests broken-stub suite.

Frontend: karma.ts, layout.tsx, MessageInput.tsx, page.tsx (DOM attrs + __bootMetrics + first-paint history).

Backend: cc_server_p1.py (atomic rename + marker comment).

Tracker: .claude/hooks/arknexus-tracker.py (cache-banned; evidence-computed).

Hooks: .git/hooks/pre-commit (scope + secret + MEMORY.md + banned-label).

Evidence: evidence/plan-run-{run_id}/, evidence/ascendance-run-{run_id}/.

Docs: docs/ForColby/ascendance-directive-v3.md, .gsd/phase-ascendance-build-CONTEXT.md, .gsd/phase-ascendance-build-PLAN.md (this file), .gsd/phase-ascendance-build-SUMMARY.md (post-run), Karma2/PLAN.md (pointer), Karma2/PLAN-ARCHIVED-{utc}.md.

## 10) Acceptance (plan-level binary)

Plan complete only when ALL true:
  - Every phase acceptance predicate VERIFIED (markers present and valid).
  - Phase 7 directive v3 verifier exit code 0; FINAL_GATE all-true; banned_label_hits=0.
  - Phase 8 acceptance VERIFIED.
  - Queue drained; every event obs_roundtrip_confirmed && bus_roundtrip_confirmed.
  - PROBE_LOG per phase has >=1 PROOF and >=1 DECISION.
  - SHIPPED emitted exclusively by directive v3 verifier stdout.
  - turn_count <= 120.

PLAN_FINAL_GATE block (printed verbatim from ascendance-final-gate.ps1 post Phase 8):

PLAN_FINAL_GATE:
- directive_v3_verifier_exit:   0
- all_14_directive_gates:       VERIFIED
- plan_phase_acceptance:        VERIFIED (all 9 phases)
- preflight_all_pass:           true
- arch_audit_clean:             true
- verifier_self_test:           PASS
- queue_drained:                true
- banned_label_hits:            0
- session_digest:               {hex}
- plan_sha256:                  {hex}
- directive_sha256:             {hex}
- turn_count:                   <= 120
- memory_md_schema_valid:       true
- git_clean_and_pushed:         true
- vault_parity_verified:        true
- tracker_shipped_in_session:   true
- cron_restored:                true

Any field false → plan INVALID → Section 8 escalation.

## 11) Post-plan doctrine

- Karma2/PLAN.md stays pointed at this file until Sovereign adopts next plan.
- Directive v3 unmodified; change bumps DIRECTIVE_VERSION and re-binds.
- New harness = matching red test + HARNESS_GATE header + verifier mapping.
- New banned label = both directive v3 Section 2 AND verifier scanner.
- Resume-capable: any crash/compact triggers preflight + checkpoint-read; never loses committed state.

## 12) Communication (AA7 detail)

ESCALATION email contract:
- Sender: CC (via cc_gmail.send_to_colby).
- Subject format: `ESCALATION: {phase}/{gate_or_task} — {brief_reason}`.
- Body: full PITFALL payload + evidence pointers + options for Sovereign response.

Sovereign reply contract:
- Subject: `Re: ESCALATION: ...`.
- First non-quoted line = directive text parsed by cc_email_daemon.py → queued to tmp/sovereign_email_inbox/ → posted to coordination bus.
- CC active-poll via cc_gmail.check_inbox every 5 min for up to 30 min after ESCALATION sent.
- If no reply within 30 min: repeat ESCALATION with second email AND post bus "ESCALATION_REPEAT" marker. Pause plan until directive received.
