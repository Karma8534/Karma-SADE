# K2 MCP Server — Evolve aria.py into Karma's Structured Tool Surface

**Date:** 2026-03-12
**Session:** 86
**Status:** APPROVED — incremental TDD, 1 step at a time
**Decision:** Evolve aria.py (not replace, not separate service)

---

## Problem

Karma has `shell_run` — a single tool that POSTs raw shell commands to K2's `/api/exec`. This funnels ALL K2 interaction through one unstructured pipe:

- `MAX_TOOL_ITERATIONS = 5` — Karma runs out of turns before finishing multi-step work
- Each call returns raw stdout text — no typing, no error structure, no schemas
- `karma` user has no sudo — can't restart services after code changes
- No structured tool discovery — Karma doesn't know what K2 can do without manually exploring

K2 is a full machine (i9-185H, 64GB RAM, RTX 4070, Python, Ollama, filesystem, network) but Karma accesses it through a keyhole.

## Solution: 3 Immediate Blockers + MCP Evolution

### Phase 1: Fix 3 Blockers (immediate relief)

1. **`MAX_TOOL_ITERATIONS` 5 → 12** — one-line change in `hub-bridge/app/server.js` line 1448. Cost: zero for normal chat (most use 1-2 iterations). Only raises ceiling for complex tasks.

2. **sudoers entry for `karma` on K2** — `karma ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart aria, /usr/bin/systemctl status aria, /usr/bin/systemctl restart ollama, /usr/bin/systemctl status ollama`. Karma can deploy her own code changes.

3. **Batch command guidance in system prompt** — teach Karma to combine commands: `shell_run("cat /path/a && echo '---SEP---' && cat /path/b")` instead of 3 separate calls.

### Phase 2: MCP Tool Registry on aria.py

Add structured tool definitions to aria.py that Karma can discover and call. Each tool does one thing, returns typed JSON.

**New endpoints (added to existing Flask app):**

```
POST /api/tools/list          → {tools: [{name, description, input_schema, output_schema}...]}
POST /api/tools/execute       → {tool: "name", input: {...}} → {ok, result: {...}}
```

**Initial tool set:**

| Tool | Input | Output | Replaces |
|------|-------|--------|----------|
| `file_read` | `{path}` | `{content, size, modified, exists}` | `shell_run("cat file")` |
| `file_write` | `{path, content}` | `{ok, bytes_written}` | `shell_run("echo '...' > file")` |
| `file_list` | `{path, pattern?}` | `{entries: [{name, type, size}...]}` | `shell_run("ls -la")` |
| `file_search` | `{path, pattern}` | `{matches: [{file, line, text}...]}` | `shell_run("grep -rn ...")` |
| `python_exec` | `{code}` | `{stdout, stderr, exit_code, result?}` | `shell_run("python3 -c '...'")` |
| `service_status` | `{name}` | `{active, uptime, memory, pid}` | `shell_run("systemctl status ...")` |
| `service_restart` | `{name}` | `{ok, new_pid}` | (blocked today — no sudo) |
| `ollama_query` | `{prompt, model?, tools?}` | `{response, tokens, latency}` | `aria_local_call(mode="chat")` |
| `scratchpad_read` | `{}` | `{content, modified}` | `shell_run("cat scratchpad.md")` |
| `scratchpad_write` | `{content, mode: "append"|"replace"}` | `{ok, size}` | `shell_run("echo >> scratchpad")` |
| `beads_query` | `{state?, category?}` | `{beads: [...]}` | (new capability) |
| `beads_write` | `{bead}` | `{ok, id}` | (new capability) |

### Phase 3: Hub-bridge MCP Client

Hub-bridge discovers K2 tools via `/api/tools/list` at startup. Registers them as TOOL_DEFINITIONS dynamically (prefixed `k2.`). Karma calls `k2.file_read` instead of `shell_run("cat ...")`.

**Key design choices:**
- Tool definitions cached at startup, refreshed on demand (`k2.refresh_tools`)
- Each K2 tool = one hub-bridge tool iteration (structured in, structured out)
- `shell_run` kept as escape hatch (raw access when no structured tool exists)
- Auth: same `X-Aria-Service-Key` header

### Phase 4: Self-Modification

With Phases 1-3, Karma can:
1. Read her own aria.py code (`k2.file_read`)
2. Write new tool definitions (`k2.file_write`)
3. Restart aria service (`k2.service_restart`)
4. Discover her new tools (`k2.refresh_tools`)
5. Use them immediately

**Gate:** Colby approves via existing thumbs-up mechanism before any self-modification executes. Karma proposes changes, Colby 👍/👎, then Karma applies.

---

## What This Is NOT

- Not a full MCP protocol implementation (JSON-RPC transport layer is overkill for single-client use)
- Not a replacement for hub-bridge tools (vault-neo tools stay in hub-bridge)
- Not Codex/KCC integration (those are available but Karma doesn't need them for self-modification)

## Cost

- Phase 1: 0 additional cost (config changes only)
- Phase 2-3: 0 additional infra cost (aria.py already running on K2)
- Token cost: REDUCED — structured tools use fewer iterations than shell_run chains

## Reminder (from Colby)

After this work: **reevaluate session-end and resurrect session-start prompts** for alignment with new K2 MCP capabilities.
