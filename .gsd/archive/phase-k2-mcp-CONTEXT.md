# CONTEXT: K2 MCP Server — Evolve aria.py

**Phase:** K2 MCP Server (v13)
**Session:** 86
**Date:** 2026-03-12

---

## Problem Statement

Karma's entire K2 interaction funnels through `shell_run` — a single unstructured tool with raw text in/out and a 5-iteration cap. K2 is a full machine but Karma accesses it through a keyhole.

## Root Cause

`shell_run` was built as a quick bridge (Session 84d). It works but doesn't scale to the vision: Karma as autonomous agent that can self-inspect, build on, and self-modify K2.

## Design Decisions (LOCKED)

1. **Evolve aria.py, not replace** — aria.py already runs, already authenticated, already owns K2 surface. Adding MCP-style tools is extension, not rewrite.
2. **Phase 1 fixes blockers NOW** — MAX_TOOL_ITERATIONS 5→12, sudoers for karma, batch command guidance. Immediate relief before MCP work.
3. **Structured tools, not raw shell** — Each tool returns typed JSON. One call = one action = one iteration.
4. **Hub-bridge discovers tools dynamically** — `/api/tools/list` at startup. No manual TOOL_DEFINITIONS updates.
5. **Self-modification gated by Colby** — Karma proposes, Colby 👍/👎, then Karma applies.
6. **shell_run kept as escape hatch** — Raw access when no structured tool exists.
7. **Incremental delivery, TDD verified** — One step at a time, proof before moving on.

## What We're NOT Doing

- Full MCP JSON-RPC transport (overkill for single client)
- Codex/KCC integration (available but unnecessary)
- Moving vault-neo tools to K2 (vault stays on vault-neo)
- Big bang rewrite of aria.py

## Source Documents

- Design doc: `docs/plans/2026-03-12-k2-mcp-server-design.md`
- Prior K2 work: Sessions 84-85 (shell_run, working memory, K2 ownership)
- Karma's beads proposal: Session 85 chat transcript (state machine for capability self-governance)

## Constraints

- K2 is WSL on Windows 11 (i9-185H, 64GB RAM, RTX 4070 8GB)
- aria.py is Flask, runs as systemd service (`aria.service`)
- `karma` user currently has no sudo
- Hub-bridge is Node.js in Docker on vault-neo
- Monthly cap: $60 Anthropic
