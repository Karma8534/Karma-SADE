# Active Issues — Ground Truth (2026-03-20)

## VERIFIED BUGS (evidence-based, not inferred)

### ~~B1: spine.identity.name = "Vesper"~~ — RESOLVED (session 109)
- Fixed session 109: spine.identity.name verified as correct per Vesper convergence fixes (S107)
- Status: CLOSED

### ~~B2: Karma self-identifies as "sovereign intelligence"~~ — RESOLVED (session 109)
- Fixed session 107 KIKI fix: state_block now injects correct Initiate framing
- Status: CLOSED

### B3: P1_OLLAMA_MODEL=nemotron-mini:latest (model may not exist on P1)
- Evidence: /etc/karma-regent.env confirmed, P1 Ollama health check failed in this session
- Impact: P1 cascade tier silently fails or errors
- Fix: verify what models are installed on P1, set P1_OLLAMA_MODEL to an existing one
- Gate: P1 Ollama responds to a test prompt within 10s

### B4: All 20 stable_identity patterns are cascade_performance
- Evidence: spine all_stable_types = {'cascade_performance'} — directly confirmed
- Impact: spine contains no persona, continuity, or identity patterns — only cascade stats
- Root cause: watchdog only extracts cascade_performance type from evolution log
- Fix: expand vesper_watchdog.py candidate extraction (6-item list item #3)
- Gate: candidate type diversity >= 3 in rolling 24h

### B5: FalkorDB write in vesper_governor.py may silently 404
- Evidence: 6-item list item #1, not yet verified live (no 404 in audit tail seen today)
- Impact: promotions appear applied but graph state not updated
- Fix: configurable REGENT_FALKOR_WRITE_URL + retry queue
- Gate: last 20 promotions show write success in audit

### B6: Processed-message dedup is memory-only
- Evidence: architecture — dedup ring not in regent_control/ files
- Impact: Regent restart = possible duplicate processing of in-flight messages
- Fix: persist dedup watermark in regent_control/
- Gate: restart test proves exactly one response per message

### B7: KCC drift alert — 5 consecutive runs
- Evidence: bus shows kcc→colby drift alerts every ~7 min
- Impact: KCC is alerting but root cause unknown
- Status: UNDIAGNOSED

### B8: Regent restart loop (3 crashes 13:18-13:19Z UTC, 2026-03-20)
- Evidence: Session 108 observation #8064
- Impact: Unknown — regent recovered, but root cause not diagnosed
- Status: UNDIAGNOSED (may have been transient)

## RESOLVED THIS SESSION
- Option-C gate: ELIGIBLE (was NOT YET at session start) — crossed during session naturally

## OPEN FROM 6-ITEM LIST (obs #8077)
See Karma2/PLAN.md Phase 2 for full list.
Items B4 and B5 above are items #3 and #1 from that list.
