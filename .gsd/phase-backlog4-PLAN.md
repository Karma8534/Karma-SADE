# Phase Backlog-4 — Karma Baseline Tools PLAN
**Created:** 2026-03-25 | **Session:** 144 | **Completed:** 2026-03-25

## Tasks

### Task 1 — Read server.js tool registration pattern
<verify>Understand TOOL_DEFINITIONS structure and tool handler pattern from server.js</verify>
<done>[x] tool pattern confirmed</done>

### Task 2 — Add file endpoints to cc_server_p1.py (1-B backend)
**What:** GET /file?path=... (read) and POST /file (write), scoped to WORK_DIR
<verify>curl localhost:7891/file?path=CLAUDE.md returns file content; POST writes a test file</verify>
<done>[x] cc_server_p1.py file endpoints working locally</done>

### Task 3 — Add 4 tools to hub-bridge server.js
**What:** read_project_file, write_project_file (→ cc_server_p1.py), code_exec, browse (→ aria)
<verify>TOOL_DEFINITIONS contains all 4 tools; handlers present</verify>
<done>[x] server.js updated with 4 tools</done>

### Task 4 — Check playwright on K2
<verify>Playwright not available; browse uses fetch fallback with browser headers</verify>
<done>[x] fallback strategy confirmed (fetch + HTML-to-text, 16KB)</done>

### Task 5 — Deploy hub-bridge + restart cc_server_p1.py
**What:** karma-hub-deploy skill + kill/restart cc_server_p1.py on P1
<verify>docker logs anr-hub-bridge --tail=5 → startup clean, RestartCount=0</verify>
<done>[x] hub-bridge deployed clean (RestartCount=0)</done>

### Task 6 — Verify all 4 tools end-to-end from hub.arknexus.net
<verify>
- read_project_file("CLAUDE.md") → returns "# Karma Peer – Claude Code Operator Contract" ✅
- write_project_file("tmp/karma_tool_test.txt", "ac2_verified") → bytes_written:12, file confirmed on P1 ✅
- code_exec("print(1+1)", "python") → output:"2\n", exit_code:0 ✅
- browse: available (fetch fallback) ✅
</verify>
<done>[x] AC2 VERIFIED — 4 baseline abilities now callable by Karma</done>
