# PLAN: K2 MCP Server — Evolve aria.py

**Phase:** K2 MCP Server (v13)
**Session:** 86
**Approach:** Incremental, TDD verified, 1 step at a time

---

## Phase 1: Fix 3 Immediate Blockers

### Task 1.1: Raise MAX_TOOL_ITERATIONS 5 → 12
- **File:** `hub-bridge/app/server.js` line 1448
- **Change:** `const MAX_TOOL_ITERATIONS = 5;` → `const MAX_TOOL_ITERATIONS = 12;`
- **Also:** Same change in `callGPTWithTools` (line ~1530s) and `callK2WithTools` (line ~1590s)
- <verify> Deploy to vault-neo. Karma can chain 6+ tool calls in one response without `(tool_loop_exceeded)`. </verify>
- <done> Change deployed, Karma tested with multi-step shell_run chain. </done>

### Task 1.2: Add sudoers entry for karma on K2
- **Where:** K2 WSL, `/etc/sudoers.d/karma-services`
- **Content:** `karma ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart aria, /usr/bin/systemctl status aria, /usr/bin/systemctl restart ollama, /usr/bin/systemctl status ollama`
- <verify> `ssh k2 "sudo systemctl status aria"` works without password prompt. </verify>
- <done> Karma can restart aria via shell_run("sudo systemctl restart aria"). </done>

### Task 1.3: Add batch command guidance to system prompt
- **File:** `Memory/00-karma-system-prompt-live.md`
- **Add:** Section under K2 tools: "Combine multiple operations in one shell_run call using && and echo separators to conserve tool iterations."
- <verify> System prompt deployed. Karma uses batched commands in next deep-mode interaction. </verify>
- <done> Guidance in system prompt, deployed via docker restart. </done>

## Phase 2: Structured Tool Registry on aria.py

### Task 2.1: Add /api/tools/list endpoint to aria.py
- **File:** aria.py on K2 (`/mnt/c/dev/Karma/k2/aria/aria.py`)
- **Returns:** JSON array of tool definitions (name, description, input_schema, output_schema)
- **Initial tools:** file_read, file_write, file_list, python_exec, service_status, service_restart, scratchpad_read, scratchpad_write
- <verify> `curl localhost:7890/api/tools/list` returns valid JSON with 8+ tools. </verify>
- <done> Endpoint returns discoverable tool registry. </done>

### Task 2.2: Add /api/tools/execute endpoint to aria.py
- **Input:** `{tool: "name", input: {...}}`
- **Output:** `{ok: true, result: {...}}` or `{ok: false, error: "message"}`
- **Dispatches** to handler functions per tool name
- <verify> Each tool callable via curl. file_read returns content+size+modified. service_restart returns new PID. </verify>
- <done> All initial tools execute correctly via /api/tools/execute. </done>

### Task 2.3: Implement file operation tools
- `file_read(path)` → `{content, size, modified, exists}`
- `file_write(path, content)` → `{ok, bytes_written}`
- `file_list(path, pattern?)` → `{entries: [{name, type, size}...]}`
- `file_search(path, pattern)` → `{matches: [{file, line, text}...]}`
- <verify> Read, write, list, search all return structured JSON. Edge cases: missing file, permission denied, binary file. </verify>
- <done> File tools working with error handling. </done>

### Task 2.4: Implement service and execution tools
- `python_exec(code)` → `{stdout, stderr, exit_code, result?}`
- `service_status(name)` → `{active, uptime, memory, pid}`
- `service_restart(name)` → `{ok, new_pid}` (requires sudo from Task 1.2)
- <verify> Python code executes and returns result. Service restart returns new PID. </verify>
- <done> Service and execution tools working. </done>

### Task 2.5: Implement scratchpad + beads tools
- `scratchpad_read()` → `{content, modified}`
- `scratchpad_write(content, mode)` → `{ok, size}`
- `beads_query(state?, category?)` → `{beads: [...]}`
- `beads_write(bead)` → `{ok, id}`
- <verify> Scratchpad round-trip. Beads CRUD with state filtering. </verify>
- <done> Working memory tools operational. </done>

## Phase 3: Hub-bridge MCP Client

### Task 3.1: Hub-bridge discovers K2 tools at startup
- **File:** `hub-bridge/app/server.js`
- At startup: fetch `/api/tools/list` from K2, register as TOOL_DEFINITIONS with `k2.` prefix
- Fallback: if K2 unreachable, keep existing shell_run only
- <verify> Hub-bridge logs discovered tools at startup. `k2.file_read` appears in TOOL_DEFINITIONS. </verify>
- <done> Dynamic tool discovery working. </done>

### Task 3.2: Route k2.* tool calls to K2
- In `executeToolCall()`: detect `k2.*` prefix, POST to `/api/tools/execute` with tool name + input
- Return structured result directly (no stdout parsing)
- <verify> Karma calls `k2.file_read`, gets structured JSON back. One iteration. </verify>
- <done> K2 tools callable from Karma chat. </done>

### Task 3.3: Add k2.refresh_tools meta-tool
- Tool that re-fetches `/api/tools/list` and updates TOOL_DEFINITIONS
- Karma calls this after self-modifying aria.py to discover new capabilities
- <verify> Add a test tool to aria.py, call refresh, new tool appears. </verify>
- <done> Self-discovery loop complete. </done>

## Phase 4: Self-Modification (requires Phases 1-3)

### Task 4.1: Karma self-modification workflow
- Karma reads aria.py → proposes change → Colby 👍 → Karma writes change → restarts aria → refreshes tools
- Gate: uses existing `/v1/feedback` thumbs mechanism
- <verify> End-to-end: Karma adds a test tool, restarts, discovers it, uses it. </verify>
- <done> Self-modification loop verified with Colby gate. </done>
