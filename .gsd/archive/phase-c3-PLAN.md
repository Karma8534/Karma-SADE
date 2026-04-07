# Phase C3 — WebMCP Tool Completion
**Created:** 2026-03-25 | **Session:** 143
**Spec:** docs/plans/2026-03-25-webmcp-julian-persistence-vision.md

## Ground Truth (verified 2026-03-25)

Proxy chain: `hub.arknexus.net/memory/* → hub-bridge (CLAUDEMEM_URL=P1:37778) → claude-mem`

### Status per tool
| # | Tool | Route | Status |
|---|------|-------|--------|
| 1 | `search_memory` | POST /memory/search | ✅ VERIFIED end-to-end |
| 2 | `save_observation` | POST /memory/save | ✅ IMPLEMENTED (untested e2e) |
| 3 | `get_observations` | POST /memory/observations | ❌ NOT IMPLEMENTED |
| 4 | `read_cognitive_state` | GET /memory/cognitive | ❌ NOT IMPLEMENTED |
| 5 | `write_cognitive_state` | POST /memory/cognitive | ❌ NOT IMPLEMENTED |
| 6 | `read_identity_spine` | GET /memory/context | ✅ IMPLEMENTED (returns resume_block+patterns) |
| 7 | `get_session_id` | GET /memory/session | ❌ NOT IMPLEMENTED |
| 8 | `proactive_check` | POST /memory/proactive | ❌ NOT IMPLEMENTED |

### Claude-mem HTTP endpoints (confirmed)
- `GET /health` → `{"status":"ok"}`
- `GET /api/search?query=...` → markdown results (MCP format)
- `POST /api/memory/save` → `{"success":true,"id":N}`
- No HTTP endpoint for get_observations by ID (MCP tool only)

---

## Tasks

### Task 1 — Verify /memory/save e2e
<verify>POST https://hub.arknexus.net/memory/save with auth → 200 + id</verify>
<done>[ ] /memory/save returns 200 with observation ID</done>

### Task 2 — Implement /memory/observations in cc_server_p1.py
**What:** Add GET /memory/observations?ids=1,2,3 → reads claude-mem SQLite directly
**Path:** claude-mem SQLite at `~/.claude-mem/memory.db` — observations table (id, title, narrative, etc.)
**Alternative:** use `/api/search` with id filters if claude-mem supports it
<verify>GET http://localhost:7891/memory/observations?ids=6620 → returns observation JSON</verify>
<done>[ ] cc_server_p1.py returns observation by ID</done>

### Task 3 — Add /memory/observations proxy in hub-bridge
**What:** Forward GET /memory/observations → cc_server_p1.py:7891/memory/observations
<verify>GET https://hub.arknexus.net/memory/observations?ids=6620 with auth → 200</verify>
<done>[ ] hub.arknexus.net/memory/observations returns observation data</done>

### Task 4 — Implement /memory/cognitive (read/write K2 scratchpad)
**What:** Add GET/POST /memory/cognitive routes in hub-bridge
- GET: Aria /api/exec → cat /mnt/c/dev/Karma/k2/cache/cc_scratchpad.md
- POST: Aria /api/exec → write content to cc_scratchpad.md
<verify>GET https://hub.arknexus.net/memory/cognitive with auth → 200 + scratchpad content</verify>
<done>[ ] hub-bridge /memory/cognitive read/write working</done>

### Task 5 — Implement /memory/session
**What:** GET /memory/session → cc_server_p1.py reads ~/.cc_server_session_id
**Add to cc_server_p1.py do_GET:** return session_id from load_session_id()
**Add to hub-bridge:** GET /memory/session → CC_SERVER_URL/memory/session
<verify>GET https://hub.arknexus.net/memory/session with auth → 200 + session_id</verify>
<done>[ ] session_id returned from hub endpoint</done>

### Task 6 — Deploy hub-bridge + cc_server_p1.py
- Sync cc_server_p1.py edits to cc_server_p1.py on P1 (restart service/process)
- Sync server.js changes to vault-neo build context → rebuild hub-bridge
<verify>All container logs clean, no SyntaxError</verify>
<done>[ ] hub-bridge deployed and healthy</done>

### Task 7 — Verify all 8 WebMCP tools e2e
<verify>All 7 implemented tools return 200 from hub.arknexus.net/memory/* with valid auth</verify>
<done>[ ] 7/8 tools verified (proactive_check is AC10 — deferred)</done>

