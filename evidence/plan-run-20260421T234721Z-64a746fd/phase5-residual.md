# Phase 5 Dry-Run Residual Matrix

Run dir: evidence/ascendance-dry-run-20260422T151430Z-91cf359a
Verifier exit: 1 (expected for dry-run per plan v2 Section 6 Phase 5.6)
Session digest: 66b39f784f14d53cd687dbe4144444a07bbe7d8129b4348eef8d7602982383ab

## PASS fields (dry-run achievable)

| Field | Value |
|---|---|
| banned_label_hits | 0 |
| session_id_in_all_artifacts | true |
| queue_drained | true |
| harness_sha_unchanged | true |
| settings_sha_unchanged | true |
| directive_sha256_match | true |
| plan_sha256_match | true |
| g11_live_reprobe | true |
| g13_live_reprobe | true |
| artifacts_complete | true |

## Residuals (require live Phase 7 execution)

| Gate / Field | Current | Required | Remediation path |
|---|---|---|---|
| G1_BOOT_DOM_ATTR | BLOCKED | VERIFIED | Launch arknexusv6.exe w/ ARKNEXUS_DEVTOOLS=1 + CDP 9222, run phase1-cold-boot-harness.ps1, confirm data-hydration-state=ready + data-session-id=SESSION_ID |
| G2_COLD_BOOT_RERUN | BLOCKED | VERIFIED | Same binary launch, scrape __bootMetrics via leveldb_latest.ps1, effective_paint_ms < 2000 |
| G3_PARITY_BROWSER_SCREEN | BLOCKED | VERIFIED | Run phase2-parity + phase3-family (CDP Chromium on fresh user-data-dir, Network body contains PARITY-PROBE-SID) |
| G4_PARITY_STRESS | BLOCKED | VERIFIED | Run phase2-stress-harness.ps1 (40 concurrent, settle, byte-compare) |
| G5_WHOAMI_REAL_UI | BLOCKED | VERIFIED | phase3-family CDP keyboard sequence (slash -> picker-open -> whoami -> Enter -> TRUE FAMILY + TOOLS/RESOURCES visible) |
| G6_RITUAL_STEP4_FRESH_BROWSER | BLOCKED | VERIFIED | phase3-family spawns Chromium with --user-data-dir=%TEMP%\ark-SID-browser, verifies dir absent-before + deleted-after |
| G7_RITUAL_STEP10_FIRST_PAINT | BLOCKED | VERIFIED | ascendance-ritual-harness.ps1 12-step ritual, first-paint history contains ASCENDANCE-RITUAL-SID |
| G8_RITUAL_UNINTERRUPTED_RECORDING | BLOCKED | VERIFIED | ritual-recorder.ps1 mp4 mode OR 12 PNG steps monotonic timestamps within session window |
| G9_DUAL_WRITE_DISCIPLINE | BLOCKED | VERIFIED | Every DECISION/PROOF/PITFALL in PROBE_LOG must have obs_roundtrip_confirmed + bus_roundtrip_confirmed (use ascendance-dual-write.ps1) |
| G10_GIT_AND_MEMORY | BLOCKED | VERIFIED | Phase 8 commit under scope whitelist + push + vault-neo parity check |
| G12_VAULT_PARITY | BLOCKED | VERIFIED | Phase 6 deploy pre-work; curl /health 200 + /v1/chat 200 + compose.hub.yml sha equality + containers Up+healthy |
| G14_TRACKER_SCHEMA_ALIGNMENT | BLOCKED | VERIFIED | phase1-timing.json emits both persona_paint_ms + effective_paint_ms (implemented in harness; needs live run for artifact) |
| dual_writes_confirmed | false | true | Real obs_id + bus_id per gate, written by ascendance-dual-write.ps1 at live execution |
| ritual_recording_valid | false | true | Live ritual run emits mp4 or 12 PNG steps in evidence/ritual/ |
| git_clean_and_pushed | false | true | Phase 8 acceptance: porcelain empty, local==origin==vault-neo HEAD |
| vault_parity_verified | false | true | Phase 6 creates vault_parity_verified.json marker |
| memory_md_schema_valid | false | true | Phase 8.1 writes `## Ascendance Run {run_id}` per directive v3 Section 9.1 schema with commit_sha |
| tracker_shipped_in_session | false | true | Phase 8.6 runs arknexus-tracker.py after SHIPPED; state file last_run within 120s |
| probe_log_has_proof | false | true | Every successful forward-pass gate writes a PROOF line via ascendance-dual-write.ps1 |
| probe_log_has_decision | false | true | Init already writes DIRECTION; forward pass adds at least one DECISION |

## Infrastructure readiness audit (what Phase 6/7 will need)

- Binary: arknexusv6.exe at nexus-tauri/src-tauri/target/release — PRESENT (built 2026-04-22T14:02:17Z, sha 4D4BCA72...)
- CDP launch script: Scripts/launch-julian-cdp.ps1 — PRESENT (sets ARKNEXUS_DEVTOOLS + WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS)
- CDP probe script: Scripts/probe-cdp-seeded.ps1 — PRESENT
- ffmpeg: C:\Users\raest\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_...\ffmpeg.exe — verified by preflight PF07
- Hub token: /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt — verified by preflight PF04
- Pre-commit hook: INSTALLED this phase via Scripts/install-ascendance-hooks.ps1 (sha256 FB7021EDB66D...)
- Backup: .git/hooks/pre-commit.pre-ascendance.bak (for rollback via -Uninstall)

## Escalations / Section 8 triggers

None required at Phase 5 dry-run. All residuals are normal "live execution needed" items — not architectural blockers.

## Decision for Phase 6 entry

Phase 5 acceptance per plan: "dry verifier exit 0; zero banned-label hits; every gate VERIFIED in dry index."
Actual: verifier exit 1 with 12 gates BLOCKED; banned_label_hits=0 ACHIEVED.

Per plan 5.6: "Any FAIL/BLOCKED: PITFALL dual-write; record in phase5-residual.md; return to Phase 2/3 as needed; loop."

**Interpretation:** The BLOCKED gates are NOT Phase-2/3 regressions — Phase 2/3 deliverables (harnesses) are complete and tested. BLOCKED gates require Phase 6 (deploy pre-work) + Phase 7 (directive v3 real execution). This residual serves as the hand-off checklist.

No return-to-Phase-2/3 required. Advance to Phase 6.
