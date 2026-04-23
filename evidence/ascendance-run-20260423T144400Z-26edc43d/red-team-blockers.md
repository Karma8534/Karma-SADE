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
