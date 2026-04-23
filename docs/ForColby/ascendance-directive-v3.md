# ARKNEXUS ASCENDANCE = 100 — SINGLE CANONICAL DIRECTIVE v3 (GROUND-TRUTH HARDENED)

DIRECTIVE_VERSION: v3
DIRECTIVE_SHA256: <computed by verifier from this canonical file on disk; mismatch at FINAL_GATE = run INVALID>
BINDING_PLAN: .gsd/phase-ascendance-build-PLAN.md (v2 or higher)

## 0) Mission and hard constraint

Achieve binary Ascendance = 100 using live-state evidence captured in the current session.

The ONLY valid claim is "SHIPPED" emitted by the verifier script after every gate in Section 9 returns Yes from fresh, in-session, nonce-bound probes.

No prose substitutes. No hand-typed FINAL_GATE values. No prior-session evidence.

## 1) Session identity and canonical surfaces

At run start, write:
- SESSION_ID = <UUID v4>
- session_start_utc = <ISO-8601 UTC>
- run_id = session_start_utc + "-" + first 8 chars of SESSION_ID

Persist to: evidence/ascendance-run-{run_id}/session.json (created first, never rewritten).

Workspace root: C:\Users\raest\Documents\Karma_SADE

Read-before-edit (missing file = BLOCKED):
- CLAUDE.md
- Karma2/cc-scope-index.md  (authoritative ledger; P089, P113 binding)
- .gsd/phase-ascendance-1-SUMMARY.md
- .gsd/phase-ascendance-2-SUMMARY.md
- .gsd/phase-ascendance-3-SUMMARY.md
- evidence/ascendance-ritual.json  (prior ritual record, audit-only)

Canonical surfaces only (CLAUDE.md table authoritative). Probe hitting URL outside the table = gate FAIL.

## 2) Claim protocol — binary only (P113 locked)

Every gate status is exactly one of:
- VERIFIED — probe executed in this session, expected == actual, artifact sha256 stored, SESSION_ID nonce present in artifact, dual-write IDs round-tripped.
- FAIL     — probe executed, predicate did not hold. Reason recorded.
- BLOCKED  — probe cannot execute. Concrete blocker + owner.

Banned labels/phrasings (presence in any artifact, log, or gate cell = run INVALID):
INFERRED, likely, should, probably, close enough, done-ish, implied, assumed,
effectively, essentially, in practice, approximately, basically, mostly, seems,
appears to, close to, near enough.

Lint scope for banned-label enforcement: evidence/** and MEMORY.md "## Ascendance Run" section only.
Whitelist: exact quoted-literal occurrences of the above tokens inside fenced code blocks of docs/ForColby/ascendance-directive-v3.md and .gsd/phase-ascendance-build-PLAN.md — these are dictionary references, not assertions.

Ambiguous probe output → add follow-up probe that resolves Yes/No. Never label around ambiguity.

Binding invariants:
- P089: prior-session claims and truth tables are NOT proofs.
- P113 (CRITICAL L1): INFERRED is not ground truth.
- P059/P060: one active plan; no archived-plan chasing.
- P064: every PITFALL fires three-writes (claude-mem + cc-scope-index + bus) before next action.
- P027: no git worktrees; no Agent(isolation:"worktree"); no EnterWorktree.

## 3) No-shortcuts rule

Disallowed, enforced by verifier:
- window.__karmaStore.addMessage (or any store write) used as evidence.
- Curl/API substitution for a gate that specifies browser/UI.
- Reusing any artifact whose content does not contain SESSION_ID or whose mtime < session_start_utc.
- Partial-credit completion.
- Editing a harness or verifier script mid-run without FAIL reset and harness-sha re-snapshot.
- Overriding banned-label list via synonyms.

On violation: STOP, run P064 three-writes with PITFALL title, mark run INVALID, do not re-enter without Sovereign re-authorization.

## 4) Evidence contract

Run root: evidence/ascendance-run-{run_id}/

Required files (created at Section 10 Step 1, before any gate work):
- session.json         { SESSION_ID, session_start_utc, directive_sha256, snapshots }
- EVIDENCE_INDEX.json  append-only log of attempts
- GAP_MATRIX.md        grid: gate_id | status | attempt_n | verified_utc | artifact
- PROBE_LOG.md         one line per event: utc | type | gate | obs_id | bus_id | title | hashes

EVIDENCE_INDEX entry (all fields required):
{
  "attempt_id": "<ULID>",
  "gate_id":    "G1_BOOT_DOM_ATTR" | ... | "G14_...",
  "attempt_n":   1+,
  "status":     "VERIFIED" | "FAIL" | "BLOCKED",
  "probe_command":            "<exact shell string>",
  "independent_verify_command":"<second command, different tool family>",
  "predicate":  "<binary expression>",
  "expected":   "<string or literal>",
  "actual":     "<string or literal>",
  "artifacts":  ["<abs path>", ...],
  "sha256":     {"<abs path>": "<hex>", ...},
  "session_id_present_in_artifact": true | false,
  "verified_utc": "<ISO-8601 UTC>",
  "obs_id":     "<claude-mem observation id>",
  "obs_roundtrip_confirmed": true | false,
  "bus_id":     "<coordination post id>",
  "bus_roundtrip_confirmed":  true | false,
  "reason_if_not_pass": "<string or null>"
}

Append-only: every attempt retained. Gate closes only when latest attempt is VERIFIED and no unresolved FAIL newer than that record.

No artifact path + no sha256 + no SESSION_ID presence = not counted.

Each artifact path appears in exactly one gate's artifacts array (no cross-gate reuse).

## 5) Gap list (ground-truth, per-gate predicates)

All gates must reach VERIFIED. Predicates are binary.

Already closed at plan start (must still be VERIFIED at FINAL_GATE via re-probe):

- G11_QUARANTINE_CLEANUP:
    predicate:
      NOT exists(config/permission_rules.json.broken-bak)
      AND NOT exists(evidence/invalidated-synthetic-s174/)

- G13_FOCUS_GATE_UNLOCK:
    predicate:
      `python .claude/hooks/arknexus-focus.py status` prints "No lock engaged"
      AND NOT exists(.claude/hooks/.arknexus-focus-lock.json)

Open gates:

- G1_BOOT_DOM_ATTR:
    predicate:
      CDP DOM readback of <html> or <body> has attribute data-hydration-state="ready"
      WITHIN 2000 ms of window visible
      AND artifact HTML contains SESSION_ID string
      (posted by harness into data-session-id attr before hydration).
    independent_verify:
      separate CDP Runtime.evaluate returning document.documentElement.dataset.hydrationState
      AND matching value captured in log.

- G2_COLD_BOOT_RERUN:
    predicate:
      phase1-cold-boot-harness.ps1 exit 0
      AND __bootMetrics.timestamp >= session_start_utc
      AND __bootMetrics.session_id == SESSION_ID
      AND effective_paint_ms < 2000
      AND independent scraper (non-harness) reports same __bootMetrics value.

- G3_PARITY_BROWSER_SCREEN:
    predicate:
      Real browser (Chromium via CDP, fresh user-data-dir per G6) navigates to hub.arknexus.net,
      authenticates with hub chat token,
      screenshot PNG shows chat feed containing probe PARITY-PROBE-{SESSION_ID}.
      CDP Network log records /v1/chat or /v1/session/{id} GET whose response body contains the probe.
      No Runtime.evaluate DOM mutations between auth and screenshot.

- G4_PARITY_STRESS:
    predicate:
      40 concurrent POSTs (20 per side, parallel) containing unique ids STRESS-{SESSION_ID}-{n}.
      After 5s settle, GET both sides. Both payloads byte-identical in turn order and content.
      Code inspection of cc_server_p1.py session store confirms atomic write-then-rename (fsync + rename)
      (cite file:line in EVIDENCE_INDEX).

- G5_WHOAMI_REAL_UI:
    predicate:
      CDP Input.dispatchKeyEvent sequence:
        "/" → confirm DOM has [data-picker-open="true"]
        → type "whoami" → confirm filtered list shows whoami row
        → Enter key → capture response block containing "TRUE FAMILY" + "TOOLS / RESOURCES".
      Per-step timestamps logged; no store injection.

- G6_RITUAL_STEP4_FRESH_BROWSER:
    predicate:
      Chromium launched with --user-data-dir=%TEMP%\ark-{SESSION_ID}-browser
      AND dir did not exist before this session
      AND command line logged to PROBE_LOG.md
      AND dir deleted at run close.

- G7_RITUAL_STEP10_FIRST_PAINT:
    predicate:
      After 60s-wait + Julian.exe relaunch, first-paint DOM contains a chat row with text
      matching ASCENDANCE-RITUAL-{SESSION_ID}.
      If absent: gate = FAIL. Honest re-score. Do not mask with prose.

- G8_RITUAL_UNINTERRUPTED_RECORDING:
    predicate:
      Before run: evidence/ritual/ wiped (verifier asserts empty at step 0).
      Capture EITHER:
        (a) ONE mp4 via `ffmpeg -f gdigrab -framerate 5 -i desktop` spanning steps 1..12, OR
        (b) 12 sequential PNGs named step-NN.png, each with mtime monotonically increasing,
            max gap between consecutive steps = 180s (step 8 allowed 60s wait only).
      All timestamps within [session_start_utc, session_start_utc + 30min].

- G9_DUAL_WRITE_DISCIPLINE:
    predicate:
      For every DECISION/PROOF/PITFALL/DIRECTION event in PROBE_LOG.md:
        obs_roundtrip_confirmed == true AND bus_roundtrip_confirmed == true.
      MCP or bus unavailable during event = BLOCKED (never VERIFIED bypass).

- G10_GIT_AND_MEMORY:
    predicate:
      Commit scope whitelist (only these paths may be in the commit):
        evidence/ascendance-run-{run_id}/**
        MEMORY.md
        .gsd/phase-ascendance-*-SUMMARY.md
        Karma2/cc-scope-index.md
        Scripts/phase*-harness.ps1
        Scripts/ascendance-*.ps1
        Scripts/ascendance-final-gate.ps1
      Any other staged path = reject commit.
      Secret-scan two-pass:
        (1) pre-commit hook returns 0.
        (2) `git diff origin/main..HEAD` scanned for Bearer/token/password/api_key/private_key;
            zero hits.
      MEMORY.md contains new section exactly matching schema in 9.1.
      After push: `ssh vault-neo git fetch && git log -1 origin/main --format=%H` == local HEAD SHA,
      retry 3x with 5s backoff; third fail = BLOCKED.

- G12_VAULT_PARITY:
    predicate:
      sha256(local compose.hub.yml) == sha256(vault-neo:/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml).
      ssh vault-neo `docker ps --format '{{.Names}} {{.Status}}'` — every container listed in
      compose.hub.yml and compose.yml present AND Status contains "Up" (and "(healthy)" if
      healthcheck defined).
      curl -sf https://hub.arknexus.net/health returns 200.
      curl -sf -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/chat -d '{"message":"ping","stream":false}' returns 200.

- G14_TRACKER_SCHEMA_ALIGNMENT:
    predicate:
      phase1-timing.json contains both persona_paint_ms and effective_paint_ms.
      Phase 1 paint-budget predicate uses effective_paint_ms.
      Written justification in GAP_MATRIX.md cites:
        (i) file:line in Scripts/phase1-cold-boot-harness.ps1 where both are computed,
        (ii) measured values this run,
        (iii) formula: effective_paint_ms = window_visible_ms + persona_paint_ms.
      Verifier reads timing.json and asserts paint_within_deadline == (effective_paint_ms < 2000).

## 6) Dual-write obligation (G9 enforcement)

For every DECISION, PROOF, PITFALL, DIRECTION in this run, before the next tool call:

1. claude-mem: save_observation(text, title="[TYPE] <gate|topic>", project="Karma_SADE")
   → capture obs_id
   → immediately get_observations(ids=[obs_id]) → confirm text/title match → obs_roundtrip_confirmed=true.
2. bus: POST /v1/coordination/post via vault-neo
   → capture bus_id
   → immediately GET /v1/coordination/recent → confirm bus_id present → bus_roundtrip_confirmed=true.
3. Append PROBE_LOG.md line:
     <utc> | <TYPE> | <gate_or_topic> | obs=<id> | bus=<id> | <title> | art_sha=<hex or none>

Either roundtrip false = event not counted = gate cannot close on evidence of this event.

If MCP or bus unreachable: dual-write queue fallback per .gsd/phase-ascendance-build-PLAN.md Section 5. Queue must be fully drained with every entry state=confirmed before FINAL_GATE.

## 7) Execution algorithm

1. Reverse pass — for every gate in Section 5, write probe_command, independent_verify_command,
   binary predicate, expected value into EVIDENCE_INDEX.json as planning stub
   (attempt_n=0, status=BLOCKED, reason="planned"). Dual-write reverse-pass DECISION.

2. Forward pass — one gate at a time:
   a. Run probe_command (attempt_n=1).
   b. Run independent_verify_command.
   c. Compute sha256 of all artifacts.
   d. Assert SESSION_ID string present in each artifact (text grep, or filename for binary).
   e. Append entry to EVIDENCE_INDEX.json with status VERIFIED | FAIL.
   f. Flip GAP_MATRIX.md cell.
   g. Dual-write PROOF (if VERIFIED) or PITFALL (if FAIL).
   h. If FAIL: systematic-debugging (Phase 1-3) before retry.

3. First-try metric: gate "first-try-passed" iff attempt_n == 1 and status == VERIFIED.
   Any retry invalidates first-try for that gate for this session.

4. Circuit breaker — keyed by gate_id:
     attempt_n == 3 with status == FAIL → STOP.
     Append PROBE_LOG line: SECTION_8_ESCALATION:{gate_id} before any further action on that gate.
     Post blocker observation + bus message. Await Sovereign.
     No attempt #4 without explicit re-authorization line SOVEREIGN_AUTH:{gate_id}:{utc} in PROBE_LOG.

5. Scope discipline (P059): no unrelated plans or refactors. Out-of-scope finding → Section 8.

6. Tool unavailability (MCP down, ssh fail, CDP unreachable) → gate status = BLOCKED. Never VERIFIED.

7. Language discipline: every gate cell and every PROBE_LOG line uses ONLY VERIFIED | FAIL | BLOCKED.
   User-facing summary lines one per gate, format: <gate_id>: <STATUS>.

## 8) Escalation for architectural blockers

Gate exposes deeper issue:
- Write PROBE_LOG line SECTION_8_ESCALATION:{gate_id}:{utc}.
- Save PITFALL observation with: broken assumption, gate blocked, failing predicate,
  honest fix scope (tasks + estimated turn count).
- Post bus message with same content.
- Also fire AA7 email escalation per plan v2 Section 2.
- Stop further work on that gate until Sovereign re-authorization line SOVEREIGN_AUTH:{gate_id} present in PROBE_LOG.

No silent patch. No workaround that hides the blocker.

## 9) Definition of done (binary, machine-verified)

All must be true simultaneously, computed by Scripts/ascendance-final-gate.ps1 at session end:

Pre-conditions:
- session.json exists and directive_sha256 matches canonical directive file on disk.
- EVIDENCE_INDEX.json, GAP_MATRIX.md, PROBE_LOG.md created within session window.
- sha256 of every harness under Scripts/ matches its session-start snapshot.
- sha256 of .claude/settings.local.json matches its session-start snapshot.

Gate conditions (per gate_id G1..G14 from Section 5):
- latest EVIDENCE_INDEX entry: status == VERIFIED.
- artifact sha256 recomputed, still matches.
- SESSION_ID present in artifact.
- obs_roundtrip_confirmed && bus_roundtrip_confirmed.
- verified_utc >= session_start_utc AND (current_utc - verified_utc) <= 600s for non-binary-fixed gates
  (binary-fixed gates — quarantine, focus gate state, harness sha256, settings sha256 — re-probed by verifier).

Session conditions:
- tracker re-run in this session writes ASCENDANCE = 100 (SHIPPED) AND last_run within 120s.
- git working tree porcelain output empty (on main).
- local HEAD SHA == origin/main HEAD SHA == vault-neo HEAD SHA.
- MEMORY.md contains section matching schema 9.1 with commit_sha field.
- focus gate unlocked, no lock file.
- G8 artifact present and valid.
- PROBE_LOG.md contains >=1 PROOF and >=1 DECISION with both roundtrips confirmed.
- first_try count recorded; no bypass.

### 9.1 MEMORY.md schema (exact)

## Ascendance Run {run_id}
- session_id: {SESSION_ID}
- started_utc: {session_start_utc}
- ended_utc:   {session_end_utc}
- commit_sha:  {git HEAD SHA}
- directive_sha256: {DIRECTIVE_SHA256}
- gates:
  - G1_BOOT_DOM_ATTR:        VERIFIED (attempt_n=N, first_try=BOOL)
  - G2_COLD_BOOT_RERUN:      VERIFIED (...)
  - ... all 14 ...
- dual_writes: proofs={count}, decisions={count}, pitfalls={count}, directions={count}
- vault_parity_sha: {local_sha}=={remote_sha}
- tracker_state: ASCENDANCE = 100 (SHIPPED)
- final_gate_exit: 0
- session_digest: {SHA256 over session.json || sorted artifact sha256s}

### 9.2 FINAL_GATE block (printed verbatim from verifier stdout)

FINAL_GATE:
- all_14_verified:             true|false
- any_fail_remaining:          true|false
- any_blocked_remaining:       true|false
- banned_label_hits:           0
- artifacts_complete:          true|false
- session_id_in_all_artifacts: true|false
- dual_writes_confirmed:       true|false
- ritual_recording_valid:      true|false
- git_clean_and_pushed:        true|false
- vault_parity_verified:       true|false
- harness_sha_unchanged:       true|false
- settings_sha_unchanged:      true|false
- memory_md_schema_valid:      true|false
- tracker_shipped_in_session:  true|false
- session_digest:              {hex}
- directive_sha256:            {hex}
- verifier_exit_code:          0

Any field false OR verifier_exit_code != 0 OR banned_label_hits > 0 → SHIPPED claim prohibited.
State is NOT SHIPPED. Resume forward pass.

### 9.3 Re-SHIP Hostile Audit Checklist (production enforcement)

This checklist is mandatory after verifier exit 0 and before any `PRODUCTION_READY_100` claim.
Every line is binary and must be probed live in-session.

- [ ] Every GET route in `proxy.js`: live 200.
- [ ] Every POST route in `proxy.js`: auth-valid live 200.
- [ ] Every static asset referenced by HTML in `public/`: present on disk.
- [ ] Every watcher service: successful run within last 10 minutes.
- [ ] Every mounted volume: SHA equals expected.
- [ ] End-to-end chat: user prompt -> assistant text returned.
- [ ] End-to-end memory: write -> restart -> read-back exact match.
- [ ] End-to-end slash command: actual UI invocation returns content.
- [ ] Hostile red-team probe completed by a separate tool family.

If any item is false, state is NOT `PRODUCTION_READY_100`.

### 9.4 Language Discipline (claim boundary)

`VERIFIER_PASS` and `PRODUCTION_READY_100` are separate labels:

- `VERIFIER_PASS` = Section 9.2 final gate all true with verifier exit 0.
- `PRODUCTION_READY_100` = `VERIFIER_PASS` plus Section 9.3 hostile audit checklist all true.

Never use `VERIFIER_PASS` as a synonym for `PRODUCTION_READY_100`.

## 10) Start command

1. Create evidence/ascendance-run-{run_id}/ and write session.json.
2. Compute DIRECTIVE_SHA256 of this canonical file; store in session.json.
3. Snapshot sha256 of every Scripts/phase*-harness.ps1, Scripts/ascendance-*.ps1, and .claude/settings.local.json into session.json.snapshots.
4. Create EVIDENCE_INDEX.json (array), GAP_MATRIX.md (table stub), PROBE_LOG.md (header only).
5. Wipe evidence/ritual/ (G8 precondition).
6. Delete .claude/hooks/.arknexus-tracker-state.json (tracker must regenerate in-session).
7. Dual-write DIRECTION: "Ascendance run {run_id} started under directive v3".
8. Reverse pass (Section 7.1): write planning stubs for all 14 gates.
9. Forward pass (Section 7.2): close gates; smallest-cost order recommended but verifier is order-agnostic.
10. When all 14 show latest status VERIFIED: run Scripts/ascendance-final-gate.ps1.
11. Only if verifier exit 0: paste FINAL_GATE block verbatim, update MEMORY.md per 9.1, commit under G10 whitelist, push, vault-neo pull + SHA check, tracker run, dual-write final PROOF, claim SHIPPED.
12. Run Section 9.3 hostile audit checklist and record binary results.
13. If verifier exit != 0 OR any Section 9.3 line is false: return to Section 7.2. Do not claim completion.

No prior-session evidence. No INFERRED. No hand-typed FINAL_GATE. No prose substitutes for probes.
