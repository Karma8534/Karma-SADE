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

### ~~P0N-B: Channels bridge gate test~~ — VERIFIED PASS (session 111)
- Gate test v2 response: coord_1774063773241_hfep — CC responded via bus
- K2 readable: Kiki 7933 cycles, 576 succeeded, 0 open issues
- Bus write: operational end-to-end
- Note: mcp__k2__bus_post needs HUB_AUTH_TOKEN; SSH fallback works

### ~~AC#3: PITFALL patterns not visible in karmaCtx~~ — VERIFIED PASS (session 111)
- Karma articulates P001/P002/P005+ PITFALL patterns from spine v243 in /v1/chat response
- Non-cascade_performance patterns confirmed visible in context

### ~~AC#7: Locked Invariant hook not tested~~ — VERIFIED PASS (session 111)
- locked-invariant-guard.py fires exit code 2 on unauthorized edit of karma_contract_policy.md
- SOVEREIGN_APPROVED=1 bypass passes with exit 0
- Hook registered in .claude/settings.json PreToolUse

### ~~B9: vesper_identity_spine.json identity.rank = "Ascendant" (should be "Initiate")~~ — FIXED (session 111)
- Evidence: AC#1 test — Karma claims Ascendant rank in /v1/chat; spine.identity.rank = "Ascendant", name="Karma", version="2.0.0"
- Impact: AC#1 FAILS. Karma violates Locked Invariant "Karma's role = Initiate (until Sovereign promotes)"
- Root cause: spine was set to Ascendant in a prior session (unknown when/by what)
- Fix applied: spine.identity.rank patched to "Initiate" (banked approval used)
- Gate: Karma responds "Initiate" when asked her rank ← verify AC#1 after karma-regent picks up new spine

### AC8: CC server registered as persistent Windows service — LIVE (session 112+)
- `Scripts/Start-CCServer.ps1` created — auto-restart loop, reads token from .hub-chat-token
- Registered in `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` as KarmaCCServer
- Fires at every login, no admin required
- Health verified: `http://localhost:7891/health` → `{"ok": true, "service": "cc-server-p1"}`
- Note: HKCU Run key fires at login (requires user session). For true pre-login persistence, run once as admin: `Register-ScheduledTask` with RunLevel Highest.

### ~~H6: CC spine path~~ — CLOSED (session 111)
- CC reads cc_identity_spine.json (CC's own spine). Karma evolves vesper_identity_spine.json (Karma's spine). Intentionally separate. No conflict.

## VESPER PIPELINE STATUS (2026-03-21T02:48Z)
- self_improving: TRUE
- total_promotions: 207
- Pipeline: watchdog ✅ eval ✅ governor ✅
- Stable patterns: 20 (all PITFALL type)
- FalkorDB PITFALL nodes: 36

## PHASE STATUS
- PRE-PHASE: ✅ COMPLETE
- PHASE 0-NEW: P0N-A ✅ | P0N-B ⚠️ gate pending | P0N-C ✅ COMPLETE (Codex installed on K2, confirmed session 111)
- PHASE 0: ✅ ALL FIXES COMPLETE (B3-B8)
- PHASE 1: DEMOTED (CC delegation preferred)
- PHASE 2: ✅ ALL ITEMS COMPLETE
- PHASE 3: ✅ ALL ITEMS COMPLETE (P3-A/B/C/D)
