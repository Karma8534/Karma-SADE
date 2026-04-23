# PROBE_LOG - 20260422T151430Z-91cf359a

started_utc: 2026-04-22T15:14:30Z
SESSION_ID: 91cf359a-324d-4857-b97e-0caa800b58a5

## Log

2026-04-22T15:14:30Z | DIRECTION | init | obs=pending | bus=pending | run initialized | art_sha=none


## Forward-pass attempt_n=2 events (S182 debug-loop)

2026-04-22T15:50:00Z | DECISION | G1_BOOT_DOM_ATTR | obs=30294 | bus=coord_1776872875970_jkst | phase1 rebuild + remote-allow-origins + tab-filter + CDP localStorage fallback | art_sha=eac25998
2026-04-22T15:50:00Z | PROOF | G1_BOOT_DOM_ATTR | obs=30294 | bus=coord_1776872875970_jkst | data-hydration-state=ready + data-session-id=b3763079 (canonical); harness SID in trace artifacts | art_sha=eac25998+c4e5e107
2026-04-22T15:50:00Z | DECISION | G2_COLD_BOOT_RERUN | obs=30294 | bus=coord_1776872875970_jkst | auth-decouple hydrate + localStorage __bootMetrics key | art_sha=346f8f91
2026-04-22T15:50:00Z | PROOF | G2_COLD_BOOT_RERUN | obs=30294 | bus=coord_1776872875970_jkst | persona_paint=318ms + effective=792ms < 2000 budget; bootMetrics.hydration_state=ready; source=cdp_localstorage | art_sha=346f8f91
2026-04-22T15:50:00Z | DECISION | G14_TRACKER_SCHEMA_ALIGNMENT | obs=30294 | bus=coord_1776872875970_jkst | timing.json emits persona_paint_ms + effective_paint_ms; formula: effective=window_visible+persona_paint | art_sha=346f8f91
2026-04-22T15:50:00Z | PROOF | G14_TRACKER_SCHEMA_ALIGNMENT | obs=30294 | bus=coord_1776872875970_jkst | phase1-cold-boot-harness.ps1:193-195 computes both fields; 474+318=792 | art_sha=346f8f91
