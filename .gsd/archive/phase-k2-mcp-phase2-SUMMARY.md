# SUMMARY: K2 MCP Phase 2 — Structured Tool Registry + Hub-Bridge Routing

**Session:** 86
**Date:** 2026-03-12
**Duration:** ~45 minutes
**Status:** ✅ COMPLETE — deployed + end-to-end verified

---

## What Was Built

### k2_tools.py — Structured Tool Registry
- **Location:** K2 at `/mnt/c/dev/Karma/k2/aria/k2_tools.py`
- **9 registered tools:** file_read, file_write, file_list, file_search, python_exec, service_status, service_restart, scratchpad_read, scratchpad_write
- **Pattern:** `_register(name, description, input_schema, handler)` — each handler returns `{ok: bool, result?: dict, error?: str}`
- **TDD:** 23 tests (test_k2_tools.py), all GREEN

### aria.py — New Flask Endpoints
- `GET /api/tools/list` — returns all tool schemas (auth: X-Aria-Service-Key)
- `POST /api/tools/execute` — dispatches `{tool, input}` to handler (auth: X-Aria-Service-Key)
- Patched after line 5878 via Python script (not heredoc — avoids escape issues)

### hub-bridge server.js — K2 Tool Routing
- **TOOL_DEFINITIONS:** 9 new `k2_*` prefixed tools added (k2_file_read, k2_file_write, k2_python_exec, etc.)
- **executeToolCall():** New `k2_*` routing block before karma-server proxy — strips `k2_` prefix, POSTs to `${ARIA_URL}/api/tools/execute` with auth
- **TDD:** 10 tests (test_k2_tool_routing.js), all GREEN

## Verification (Production)

| Check | Result |
|-------|--------|
| RestartCount | 0 |
| Startup logs | Clean — hub-bridge v2.11.0 listening on :18090 |
| /v1/chat with k2_scratchpad_read | ✅ Karma returned first line of scratchpad |
| Hub-bridge logs | `[TOOL-API] k2.* routing: k2_scratchpad_read → scratchpad_read` |
| K2 /api/tools/list | ✅ Returns all 9 tools with schemas |
| K2 /api/tools/execute | ✅ All tested tools return correct results |

## What Was Learned

1. **Anthropic API rejects dots in tool names** — pattern is `^[a-zA-Z0-9_-]{1,128}$}`. Changed `k2.file_read` → `k2_file_read` (obs #5424)
2. **ARIA_SERVICE_KEY lives in aria.service drop-in** (`10-aria-env.conf`) — not visible in `systemctl show` Environment line but IS in the running process environment
3. **Integration testing from vault-neo works** — curl to K2's Tailscale IP (100.75.109.92:7890) with the key from hub-bridge container

## Pitfalls

- **Dots in tool names:** First deployment returned 400 from Anthropic API. Fixed within minutes but required a second deploy cycle.

## What's Next

Phase 3: Hub-bridge discovers K2 tools dynamically at startup via `/api/tools/list` (instead of hardcoded TOOL_DEFINITIONS). This makes K2 tools self-describing — add a tool to k2_tools.py, restart aria, hub-bridge picks it up automatically.
