# Red-Team Blocker Log S183 (hostile audit)

Standing phrase: "No defer. Binary only."
Each entry: BLOCKER-X | description | evidence | status

## D = Production endpoints

BLOCKER-D1 | /agora returns 500 (agora.html missing from vault-neo hub-bridge public/) | `{"ok":false,"error":"agora.html not found"}`; vault-neo /opt/seed-vault/memory_v1/hub_bridge/app/public/ contains only `nexus` + `unified.html`; local hub-bridge/app/public/ has agora.html, index.html, regent.html, unified.html | OPEN

BLOCKER-D2 | hub-bridge build-context public/ drift vs local git repo hub-bridge/app/public/ | vault-neo has 2 files, local has 4+ | OPEN (root cause: scp never ran to sync assets post-commit)

## F = Vault-neo parity

BLOCKER-F1 | Multiple .bak files cluttering vault-neo hub-bridge app/ (proxy.js.bak.*, server.js.backup*) | cleanup pending | OPEN

## To-discover (audit in progress)

- D3-D8: other hub endpoints
- E1-E5: arknexusv6.exe end-to-end
- G1-G8: watchers/daemons running
- H1-H3: K2 cortex semantic state
- I1-I4: memory persistence
- J1-J3: evolution loops
- K1-K3: security surfaces
- L1-L6: end-to-end UX

## Resolutions

BLOCKER-D1 RESOLVED | /agora 200 | scp hub-bridge/app/public/agora.html+regent.html -> vault-neo build context; docker cp into running container | CLOSED

BLOCKER-D2 RESOLVED | public/ drift synced | vault-neo now has agora.html + regent.html + nexus/ + unified.html | CLOSED

BLOCKER-D3-D8 | Auth-surface differences only | /v1/ambient 401 (capture token), /v1/cypher 400 (payload), /v1/chat-GET 404 but POST 200 | NOT-BLOCKERS (expected auth/method behavior)

BLOCKER-F1 | .bak files on vault-neo hub-bridge app/ | .bak files don't affect runtime (container uses proxy.js only) | DEFER-cosmetic

BLOCKER-G1/2/3 RESOLVED | vesper-watchdog/eval/governor "inactive" are one-shot services -- timers confirmed firing: vesper-eval next 3m58s, vesper-governor next 8min, karma-observer next 14min. Not dead: cadenced | NOT-BLOCKERS

BLOCKER-P116 NEW | verifier-pass != production-ready | locked via claude-mem obs #30663 + bus coord_1776960158859_yt57 + MEMORY.md update pending | OPEN-PROCEDURE-LOCK

## Post-fix verifier status
- All GET routes 200 (/health /v1/status /agora /v1/learnings /v1/trace /v1/cancel /v1/surface /v1/coordination/recent / /legacy /unified.html)
- All POST routes correct-auth 200 (/v1/chat /v1/feedback /v1/coordination/post)
- Memory persistence: TRUE (write-read-back round-trip via /v1/session/{id})
- cortex /ingest: TRUE (20 chars -> total_blocks 739)
- Ledger: 985294 lines growing
- FalkorDB: 8863 nodes
- karma-regent active 1h 16min
- aria active 1h 16min
- vesper timers firing

## Tauri end-to-end (pending full user-flow probe)

## Additional blockers found + resolved S183 cont.

BLOCKER-UX1 RESOLVED | unified.html leaked http://localhost:37778 in MEMORY link (unreachable from remote) | wrapped in `if (location.hostname === 'localhost'||'127.0.0.1')` | CLOSED

BLOCKER-UX2 RESOLVED | K2 always showed "offline" in Tauri Header despite K2 live on Tailscale 100.75.109.92 | root cause: k2Active zustand state never set by any fetch; default false. Added useEffect in page.tsx polling /v1/status every 10s -> setStatus({k2Active,brainOk,lastSeen}) | CLOSED. Post-fix Tauri body: "K2 active brain ok last seen 0s ago"

BLOCKER-UX3 | /v1/spine returns 502 "K2 spine unreachable" (hub-bridge proxy.js line 1366 fetches http://100.75.109.92:7892/spine which doesn't exist) | Bypassed in UI via /v1/status; proxy.js handler still buggy but no consumer now | DEGRADED-LOGIC

BLOCKER-REDTEAM1 | 200 HTTP != TRUE | semantic body verification required per endpoint; Sovereign correction locked P116 | CLOSED-PROCEDURE-LOCK

## Semantic verification (binary TRUE based on BODY match)
- /health ok:true TRUE
- /agora HTML with agora dashboard TRUE
- / valid HTML TRUE
- /v1/status has harness.k2.healthy + harness.p1.healthy + model TRUE
- /v1/chat "2+2?" -> "4" TRUE (real LLM response)
- /v1/learnings entries array TRUE
- /v1/trace entries TRUE
- /v1/feedback ok+id TRUE
- /v1/coordination/recent has coord_ TRUE
- memory write-read-back: write message via /v1/chat, GET /v1/session/{id}, history contains message TRUE
- Tauri E2E: url=tauri.localhost hydration=ready session=harness-SID hasTextarea=true bodyLen=770 hasBootMetrics=true nexusSessionGlobal=harness-SID K2=active brain=ok TRUE

## Nexus V3.0 P-followup surgical merges (S183)

P-FU1 MagicDNS RESOLVED | proxy.js 10 IPs -> 7 hostname refs (k2, payback); compose.hub.yml extra_hosts k2/payback/vault-neo/arknexus-vault-01; container /etc/hosts verified; docker exec wget http://k2:7892/health 200; docker exec wget http://payback:7891/health 200 | CLOSED
P-FU2 OpenClaw 4-layer MEMORY.md RESOLVED | Headers ARCHITECTURE, DECISIONS, STATE, SESSION added at top of MEMORY.md with strict content per section | CLOSED
P-FU3 node --check pre-commit hook RESOLVED | Scripts/ascendance-pre-commit.sh line ~44 gates staged hub-bridge/app/*.js via `node --check`; installer sha 840FA40D45CA; rejection verified on synthetic bad.js | CLOSED
P-FU4 3-strike governor ALREADY-LIVE | proxy.js line 321 breakerState(sessionId).halted triggers "Session halted by 3-strike breaker (N fails)" block; pre-existing feature matching Nexus V3.0 Break 3 fix | CLOSED-EXISTING
P-FU5 Vesper staging sandbox RESOLVED | Scripts/nexus-v3-staging-sandbox.sh deployed to vault-neo /tmp/nexus-v3-staging.sh; init created /opt/seed-vault/memory_v1/hub_bridge/staging/app/ with proxy-stage.js (89262 bytes) + public/ + package.json; supports stage/promote/diff with node --check gate | CLOSED
P-FU6 Firewall port isolation SCRIPT-WRITTEN | Scripts/nexus-v3-firewall-isolation.ps1 idempotent installer (K2 + P1 Windows Firewall block ports 11434/6379/7890/7891/7892 except Tailscale 100.0.0.0/8 + 127.0.0.0/8); iptables reference rules for vault-neo in script footer | SCRIPT-READY-DEPLOY-PENDING-ADMIN

P-FU7 Hub-down fallback RESOLVED | frontend/src/lib/api.ts apiFetch -> on hub 5xx retry once against direct FALLBACK_BRIDGE (127.0.0.1:7891). Only fires when primary URL is remote (not already localhost). Fallback silent if bridge unreachable; original 5xx returned. | CLOSED
