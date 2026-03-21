# K2 as MCP Server — Design

**Date:** 2026-03-16
**Session:** 100
**Status:** APPROVED
**Builds on:** `2026-03-12-k2-mcp-server-design.md` (Phases 1+2 already deployed)

---

## What Already Exists

- `/api/tools/list` + `/api/tools/execute` live in aria.py (Phase 2 complete)
- `k2_tools.py`: 9 typed tools — file_read/write/list/search, python_exec, service_status/restart, scratchpad_read/write
- Kiki: cycle 884+, 91% success rate, 10-tool autonomous agent
- Ollama: qwen3:8b, qwen3.5:4b, nomic-embed-text at 100.75.109.92:11434
- Tailscale: P1=100.124.194.102, K2=100.75.109.92 (direct HTTP accessible)

## What This Design Adds

### Prerequisites (must complete first)
1. **B1**: Fix kiki JSON truncation — LLM sometimes returns 182-char truncated response missing `}`. Add repair logic so kiki doesn't drop valid tasks.
2. **B2**: Fix vault sync 401 — ambient POST missing Authorization header. Add `HUB_AUTH_TOKEN` bearer token.

### Phase 3a: 5 New K2 Tools (k2_tools.py)

| Tool | What it enables |
|---|---|
| `kiki_inject` | CC pushes tasks into kiki's autonomous queue |
| `kiki_status` | CC reads kiki state, open issues, recent journal |
| `kiki_journal` | CC reads last N kiki journal entries |
| `bus_post` | CC posts DIRECTION/INSIGHT to coordination bus from tool calls |
| `ollama_embed` | Semantic embeddings via nomic-embed-text — free vector ops |

**Decision**: No `k2.think()` — qwen3:8b over Tailscale vs Haiku 4.5 direct is not a compelling ROI. Add when K2 gets a 30B+ model or model routing requires it.

### Phase 3b: MCP Stdio Proxy on P1 (`Scripts/k2_mcp_proxy.py`)

- Python stdio process implementing MCP JSON-RPC 2.0 protocol
- Proxies to K2 HTTP API at `http://100.75.109.92:7890` via Tailscale
- Auth: `X-Aria-Service-Key` from `Scripts/k2_mcp.key` (gitignored)
- Registered in `.claude/settings.local.json` as `mcpServers.k2`
- CC gets native `k2.*` tool calls — no SSH, no shell_run, typed schemas

### Phase 3c: Hub-bridge Lazy K2 Tool Routing (server.js)

- No startup discovery — avoids hub-bridge→K2 hard dependency at boot
- `k2ToolsCache`: fetched on first k2.* call, cached 10 minutes
- Tool names prefixed `k2.` in TOOL_DEFINITIONS for Karma
- Execution: strip `k2.` → POST to K2 `/api/tools/execute`
- Auth: `ARIA_SERVICE_KEY` env var in hub.env

## Architecture After This Design

```
CC (P1) ──MCP stdio──▶ k2_mcp_proxy.py ──HTTP──▶ K2:7890/api/tools/execute
                                                          │
Karma ──hub-bridge k2.*──▶ server.js lazy call ──────────┘
                                                          │
                                               k2_tools.py (14 tools)
                                                     │         │
                                               kiki queue   Ollama embed
                                               bus post     file ops
                                               kiki status  exec
```

## What Stays the Same

- `shell_run` kept as escape hatch for raw exec
- aria.service auth unchanged (`ARIA_SERVICE_KEY`)
- K2 git repo, kiki service, KCC — unchanged
- hub-bridge startup: no new dependencies

## Files Changed

| File | Location | Change |
|------|----------|--------|
| `karma_kiki_v5.py` | K2 | B1: JSON repair + B2: vault auth |
| `k2_tools.py` | K2 | +5 tools |
| `k2_mcp_proxy.py` | P1 `Scripts/` | New MCP proxy |
| `k2_mcp.key` | P1 `Scripts/` | New (gitignored) |
| `.claude/settings.local.json` | P1 | Add mcpServers.k2 |
| `server.js` | P1 `hub-bridge/app/` | Lazy k2.* tool routing |
| `CLAUDE.md` | P1 | K2 MCP co-processor section |
| `resurrect` skill | P1 | Use k2.kiki_status |
| `STATE.md` | P1 `.gsd/` | Update K2 MCP row |

## TDD Verification Gates

1. **B1**: Kiki closes an issue without `Unparseable LLM response` in log
2. **B2**: Vault sync returns HTTP 200 (check kiki log)
3. **k2_tools**: `curl /api/tools/list` shows 14 tools; `curl /api/tools/execute kiki_status` returns kiki state
4. **MCP proxy**: `echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python3 Scripts/k2_mcp_proxy.py` returns tool list
5. **MCP in CC**: CC session sees k2.* tools natively
6. **hub-bridge**: Karma can call `k2.kiki_status` and get structured response
