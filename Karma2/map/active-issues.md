# Active Issues — Ground Truth (2026-03-21)

## CLOSED BUGS

### ~~B1: spine.identity.name = "Vesper"~~ — RESOLVED (session 109)
### ~~B2: Karma self-identifies as "sovereign intelligence"~~ — RESOLVED (session 109)
### ~~B3: P1_OLLAMA_MODEL=nemotron-mini:latest~~ — RESOLVED (session 110)
- nemotron-mini:latest IS installed on P1, responds in 738ms
### ~~B4: All stable_identity patterns are cascade_performance~~ — RESOLVED (session 110)
- PITFALL fast-path + TYPE_THRESHOLDS deployed; 20 stable patterns (PITFALL type)
### ~~B5: FalkorDB write silently 404~~ — RESOLVED (session 110)
- SSH fallback works; 36 PITFALL nodes in graph; smoke test 4/4 PASS
### ~~B6: Dedup ring memory-only~~ — RESOLVED (session 110)
- Watermark persisted to regent_control/dedup_watermark.json
### ~~B8: Regent restart loop~~ — RESOLVED (session 110)
- Diagnosed as 3 clean Stopping events from manual session 107 restarts (not crashes)
### ~~H3: cc_scratchpad.md two copies~~ — RESOLVED (session 110)
- K2 (135 lines, Mar 20) synced to vault-neo (was 47 lines, Mar 14). K2 is canonical.

## OPEN ISSUES

### B7: KCC drift alert — no ack path
- Evidence: kcc→colby drift alerts posted every ~5 min with no ack path
- Impact: bus noise, Sovereign attention required for every alert
- Fix applied (session 110): family_watch() 30-min cooldown added to karma_regent.py
- Remaining: KCC scope manifest written at k2/aria/docs/kcc-scope.md
- Gate: drift alerts appear ≤ once per 30 min, and only when condition is NEW
- Status: COOLDOWN APPLIED — monitor for next 30 min

### H5: B7 KCC drift cleared — awaiting confirmation
- Status: cc_anchor confirmation pending

### P0N-B: Channels bridge gate test inconclusive
- Evidence: CC server on port 7891 times out on /cc requests (claude CLI slow startup)
- Impact: coordination bus → CC routing not verified end-to-end
- Root cause: cc_server_p1.py spawns `claude -p` subprocess which takes >15s to start
- Fix needed: increase HTTP timeout in channels_bridge.py, or pre-warm claude CLI
- Gate: bus message to cc gets response within 30s

## VESPER PIPELINE STATUS (2026-03-21T02:48Z)
- self_improving: TRUE
- total_promotions: 207
- Pipeline: watchdog ✅ eval ✅ governor ✅
- Stable patterns: 20 (all PITFALL type)
- FalkorDB PITFALL nodes: 36

## PHASE STATUS
- PRE-PHASE: ✅ COMPLETE
- PHASE 0-NEW: P0N-A ✅ | P0N-B ⚠️ gate pending | P0N-C ✅ approved (needs Codex Installer.exe)
- PHASE 0: ✅ ALL FIXES COMPLETE (B3-B8)
- PHASE 1: DEMOTED (CC delegation preferred)
- PHASE 2: ✅ ALL ITEMS COMPLETE
- PHASE 3: ✅ ALL ITEMS COMPLETE (P3-A/B/C/D)
