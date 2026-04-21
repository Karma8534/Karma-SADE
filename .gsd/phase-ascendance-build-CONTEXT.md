# Phase Ascendance Build — CONTEXT (design locks)

**Version:** plan v2
**Created:** 2026-04-21
**Author:** CC (Ascendant)
**Sovereign approval:** pending manual review before Phase 0 start
**Binds:** docs/ForColby/ascendance-directive-v3.md

---

## 1) Why this plan exists

Prior Ascendance runs (phase 1/2/3/ritual SUMMARIES) reached passing tracker state using evidence that later failed adversarial re-verification against stricter predicates. Ground-truth gap list G1..G14 (directive v3 Section 5) cannot all reach VERIFIED without:
- frontend code changes (DOM attrs, __bootMetrics schema, first-paint history)
- backend verification (cc_server_p1.py atomic write-then-rename)
- new harnesses (stress, recorder, fresh-browser, CDP keyboard)
- verifier + pre-commit hook + lint enforcement
- dual-write queue fallback + preflight battery

Plan v2 closes those build gaps, then executes directive v3 to ship.

## 2) Non-negotiable invariants

- **P113:** INFERRED banned. Labels = VERIFIED | FAIL | BLOCKED only.
- **P089:** prior-session claims are not proofs.
- **P059/P060:** one active plan; Karma2/PLAN.md must point here during run.
- **P064:** every PITFALL = three-writes (claude-mem + cc-scope-index + bus) before next action.
- **P027:** no git worktrees; no `Agent(isolation:"worktree")`; no `EnterWorktree`.
- **CLAUDE.md honesty contract:** VERIFIED vs FAIL/BLOCKED; never fabricate; never silently patch.
- **Canonical surfaces only:** every read/write goes through CLAUDE.md table; no new truth stores.
- **Dual-write obligation:** every DECISION/PROOF/PITFALL/DIRECTION fires both writes inline, never batched.

## 3) Attack surface map (red-team results)

Threats enumerated during plan review and patched in v2:

| # | Threat | Patch |
|---|--------|-------|
| T1 | "This session" undefined → prior-session reuse | SESSION_ID UUID + session_start_utc; every artifact embeds SESSION_ID |
| T2 | Probe outputs stale data | Every probe emits SESSION_ID nonce into observable; independent verifier uses different tool family |
| T3 | sha256 doesn't prove freshness | Artifact must contain SESSION_ID string or filename |
| T4 | Retry-until-pass | EVIDENCE_INDEX append-only; first_try metric tracked per gate |
| T5 | Dual-write ID spoofing | Roundtrip confirm (get_observations / recent) logged |
| T6 | Ritual "uninterrupted" ambiguous | Monotonic mtimes, 180s max gap (step 8 = 60s exact) |
| T7 | "Fresh browser" ambiguous | New `%TEMP%\ark-{SESSION_ID}-browser` dir, command logged, deleted at close |
| T8 | Banned labels via synonyms | Expanded list; lint scope pinned to evidence/** + MEMORY.md Ascendance section |
| T9 | Circuit breaker bypass via rephrase | Counted per gate_id |
| T10 | FINAL_GATE hand-typed | Verifier computes; exit code pasted verbatim |
| T11 | Tracker state editable | Tracker computes from evidence/; cache deleted at run start |
| T12 | Commit without MEMORY update | Pre-commit hook checks MEMORY.md staged + contains SESSION_ID |
| T13 | Secret scan weak | Two-pass (hook + diff origin/main..HEAD) |
| T14 | Subagent worktree bypass | Explicitly banned (P027) |
| T15 | Harness tamper mid-run | sha256 snapshot at session start, re-verified at FINAL_GATE |
| T16 | Tauri LevelDB format drift | Canary test + AA5 fallback scraper |
| T17 | MCP/bus flake breaks dual-write | Queue fallback; G9 BLOCKED until drained |
| T18 | Anthropic API outage | Checkpoint/resume; preflight PF11 |
| T19 | Single-session cap too tight | 120-turn cap + parallelism + checkpoint/resume |
| T20 | Token expiry mid-run | PF04 + re-check at Phase 6/7 |
| T21 | Multi-run collision | evidence/.ascendance.lock single-instance sentinel |
| T22 | vault-neo drift during plan | HEAD sha snapshot at Phase 0, re-verified at Phase 8 |
| T23 | Directive file tamper | DIRECTIVE_SHA256 pinned in session.json |
| T24 | Plan file tamper | PLAN_SHA256 computed at init, verified at FINAL_GATE |
| T25 | Lint false-positive on dictionary-reference banned words | Whitelist quoted-literal occurrences inside fenced code blocks of directive + plan |

## 4) Auto-auth (AA) scope — pre-cleared by Sovereign

| ID | Class | Notes |
|----|-------|-------|
| AA1 | Harness typo / param error fix | single-file edit under Scripts/phase*-harness.ps1 or Scripts/ascendance-*.ps1 |
| AA2 | Flake retry on external endpoint | network/CDP/ssh timeout or 5xx only — NOT semantic errors |
| AA3 | Frontend rollback on smoke fail | prior hub-bridge:pre-{run_id} tag restore |
| AA4 | Docker container restart | single container unhealthy; escalate if second restart fails |
| AA5 | LevelDB scraper fallback | primary no data → secondary reader |
| AA6 | Dual-write queue drain on recovery | MCP/bus came back → flush pending |
| AA7 | ESCALATION email + active-poll mode | on Section 8 trigger: send_to_colby(subject="ESCALATION: ...") then check_inbox every 5 min up to 30 min |

Outside AA1..AA7 = Sovereign escalation required. Examples: scope change, architectural deviation, token refresh, non-whitelisted file edit, shipping commit rollback.

## 5) Session-preservation design

Checkpoint files under `evidence/plan-run-{run_id}/phase-N-DONE.marker` survive:
- context compaction
- session death
- machine reboot

Build phases (0..6) are session-agnostic — markers reusable on resume.
Directive-v3 execution phases (7..8) are session-bound — SESSION_ID regenerates; gate probes re-run.

Resume flow: `/resurrect` → preflight battery → read markers → skip DONE phases → continue.

## 6) Communication channels (multi-session)

| Direction | Primary | Fallback |
|-----------|---------|----------|
| CC → Sovereign escalation | chat (if session live) | AA7 email via `cc_gmail.send_to_colby(subject="ESCALATION: ...")` |
| Sovereign → CC directive | chat (zero-latency) | reply to ESCALATION email; daemon queues to `tmp/sovereign_email_inbox/` + bus; CC active-poll via `check_inbox()` every 5 min |
| CC → system log | claude-mem + bus (dual-write) | local queue jsonl fsync fallback |

Email subject contract: `ESCALATION: {phase}/{gate_or_task} — {brief}`. Sovereign reply with `Re: ESCALATION` + first non-quoted line = directive text.

## 7) Rollback contract per phase

Every phase declares a rollback command (see plan Section 6 phase blocks). Tags pinned on commits:
- `ascendance-build-p1` — post-skeleton
- `ascendance-build-p2` — post-code-repairs
- `ascendance-build-p3` — post-harnesses
- `ascendance-build-p4` — post-verifier
- `ascendance-build-p5` — post-dry-run
- `ascendance-build-p6` — post-deploy-prework
- `pre-ascendance-build-v2-{utc}` — anchor before Phase 0 (written by anchor step 4 in this commit)

## 8) Explicit NOT-in-scope (YAGNI)

- Codex or KCC delegation of gate work.
- New UI features.
- New bus endpoints.
- New claude-mem categories.
- Refactoring CLAUDE.md.
- Anything the 40 non-Ascendance modified files in working tree touch (stash + commit separately per Phase 0.1).

## 9) Acceptance of this CONTEXT

This CONTEXT is considered accepted when:
1. Sovereign reads it and gives explicit go.
2. Plan v2 (.gsd/phase-ascendance-build-PLAN.md) and directive v3 (docs/ForColby/ascendance-directive-v3.md) are written to disk and committed.
3. Anchor step 4 tag (`pre-ascendance-build-v2-{utc}`) exists on origin/main.
4. Checkpoint `ascendance-build-checkpoint.json` written with `phase: 0, status: pending`.

Then and only then: Phase 0.0 preflight may execute.
