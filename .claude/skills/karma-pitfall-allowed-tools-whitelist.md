---
name: karma-pitfall-allowed-tools-whitelist
description: Use when adding new tools to hub-bridge TOOL_DEFINITIONS. hooks.py ALLOWED_TOOLS gates ALL tool calls — missing entry = silent rejection with no error in Karma's UI.
type: feedback
---

## Rule

When adding a new tool to `TOOL_DEFINITIONS` in server.js, you MUST also add it to `ALLOWED_TOOLS` in `karma-core/hooks.py` AND rebuild karma-server. Tools not in ALLOWED_TOOLS are rejected silently before reaching `execute_tool_action()`.

**Why:** Session 66: Added new tools to TOOL_DEFINITIONS. Tools returned `{"ok":false,"error":"Unknown tool: X"}` with no visible error in the UI. Debugging took hours. Root cause: `hooks.py` line-level whitelist checked tool name BEFORE routing to handler. Any non-whitelisted tool name = rejected, no log entry.

**How to apply:**
Two categories:
1. **hub-bridge-native tools** (get_vault_file, write_memory, fetch_url, get_library_docs, aria_local_call, shell_run): Do NOT need hooks.py update — handled in hub-bridge before karma-server.
2. **karma-server-proxied tools** (graph_query): REQUIRE `ALLOWED_TOOLS` update in hooks.py + `karma-server rebuild`.

TOOL_NAME_MAP must be `{}` (empty = identity passthrough). Any alias mapping = broken routing.

## Evidence

- Session 66: New tools added, all rejected with "Unknown tool" — ALLOWED_TOOLS whitelist discovered
- Session 66: TOOL_NAME_MAP had pre-existing wrong aliases (read_file→file_read etc.) — broken
- CLAUDE.md Known Pitfalls section
