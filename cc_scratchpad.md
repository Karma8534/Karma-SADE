# CC Scratchpad — cognitive trail for resume

Last update: 2026-04-22T14:10Z (session 181-cont wrap)

## Active Plan

Ascendance Build + Verify Plan v2 (`.gsd/phase-ascendance-build-PLAN.md`) binding directive v3 (`docs/ForColby/ascendance-directive-v3.md`). Anchor tag `pre-ascendance-build-v2-20260421T204928Z`. plan_run_id `plan-run-20260421T234721Z-64a746fd`.

## Phases Complete This Arc

- Phase 0 (freeze/archive/bootstrap) — 10/10 sub-phases VERIFIED
- Phase 0.5 (arch audit) — 5/5 VERIFIED; major find: DOM attrs + atomic rename already in source
- Phase 1 (red tests + skeletons) — 5 scripts + 16 tests + test-of-tests; tag ascendance-build-p1
- Phase 2 (code repairs + rebuild) — 11/11 VERIFIED after P115 debug loop

## Cognitive Trail (last 3 reasoning threads)

1. **Phase 2.11 CDP resolution** — Tauri 2 release builds strip CDP unless Cargo.toml `features = ["devtools"]` + lib.rs `use tauri::Manager` + `win.open_devtools()` + ARKNEXUS_DEVTOOLS=1 env + WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS. All four required. Fix committed 540fbe77.
2. **karma.ts nonce priority** — `/memory/session` endpoint returns stored session_id which overrode seeded nonce. Fix: `const ascendanceNonce = localStorage.getItem('karma-ark-session-nonce') || ''; if (fetchedSessionId && !ascendanceNonce) sessionId = fetchedSessionId;` in hydrateBootFrame.
3. **P115 defer-banned** — prior tendency to push FAIL across phase boundaries as "deferred". Sovereign corrected. Standing phrase locked as audit trigger.

## Phase 3 Prep

6 harnesses to rewrite + 1 independent verifier. Each needs:
- `# HARNESS_GATE: G#` header
- SESSION_ID nonce injection via `localStorage.setItem('karma-ark-session-nonce', $SESSION_ID)` pre-seed via CDP
- Julian launch via `Scripts/launch-julian-cdp.ps1` (sets ARKNEXUS_DEVTOOLS + WEBVIEW2 env)
- DOM readback via `Scripts/probe-cdp-seeded.ps1` pattern
- Evidence emission to `evidence/plan-run-{run_id}/` in EVIDENCE_INDEX schema

### Per-harness scope
- phase1-cold-boot-harness: rewrite to use leveldb_latest.ps1 + CDP-seed nonce + __bootMetrics scrape
- phase2-parity-harness: diagnose existing history-match FAIL (systematic-debugging first)
- phase2-stress-harness: 40 concurrent POSTs byte-diff (already partially exists)
- phase3-family-harness: CDP keyboard G5 + fresh browser G6 + CDP Network capture G3
- ritual-recorder: ffmpeg gdigrab mode + 12-PNG mode
- ascendance-ritual-harness: wire recorder + fresh-browser profile + SESSION_ID in probe
- ascendance-independent-verify: cross-tool-family diff (Python leveldb vs PS leveldb_latest)

## Pitfall Budget

P113 + P114 + P115 all locked this arc. P114 mitigation: atomic commit per phase boundary — DO NOT skip.

## Watch-outs

- External auto-stash actor (P114) fires at unknown intervals; any uncommitted edit may vanish. Commit within same turn of edit.
- `nexus-tauri/src-tauri/.gitignore` excludes `/target/` — source files tracked (Cargo.toml, lib.rs, tauri.conf.json) but binary not committed.
- `/memory/session` endpoint side-effects session state; if harness pre-seeds nonce, patch already prevents override but any future hydration refactor must preserve ascendanceNonce priority check.

## Standing Order

"No defer. Binary only. If blocked beyond AA1-AA7, AA7 ESCALATION email + wait for auth. No silent defer permitted." — Sovereign.
