# Phase Backlog-4 — Karma Baseline Tools PLAN
**Created:** 2026-03-25 | **Session:** 144

## Tasks

### Task 1 — Read server.js tool registration pattern
<verify>Understand TOOL_DEFINITIONS structure and tool handler pattern from server.js</verify>
<done>[ ] tool pattern confirmed</done>

### Task 2 — Add file endpoints to cc_server_p1.py (1-B backend)
**What:** GET /file?path=... (read) and POST /file (write), scoped to WORK_DIR
<verify>curl localhost:7891/file?path=CLAUDE.md returns file content; POST writes a test file</verify>
<done>[ ] cc_server_p1.py file endpoints working locally</done>

### Task 3 — Add 4 tools to hub-bridge server.js
**What:** read_project_file, write_project_file (→ cc_server_p1.py), code_exec, browser_open (→ aria)
<verify>TOOL_DEFINITIONS contains all 4 tools; handlers present</verify>
<done>[ ] server.js updated with 4 tools</done>

### Task 4 — Check playwright on K2
<verify>ssh K2 → python3 -c "from playwright.sync_api import sync_playwright; print('ok')" → ok</verify>
<done>[ ] playwright available or fallback strategy confirmed</done>

### Task 5 — Deploy hub-bridge + restart cc_server_p1.py
**What:** karma-hub-deploy skill + kill/restart cc_server_p1.py on P1
<verify>docker logs anr-hub-bridge --tail=5 → startup clean, no SyntaxError; GET /health → 200</verify>
<done>[ ] both services running with new code</done>

### Task 6 — Verify all 3 tools end-to-end from hub.arknexus.net
<verify>
- read_project_file("CLAUDE.md") → returns content
- write_project_file("tmp/tool_test.txt", "ok") → writes file, confirmed on P1
- code_exec("print(1+1)", "python") → returns "2"
- browser_open("https://hub.arknexus.net/health") → returns page text
</verify>
<done>[ ] AC2 verified — 3 new tools + memory = 4 baseline abilities</done>
