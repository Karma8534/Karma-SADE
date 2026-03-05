# Karma SADE - Stable Decisions and Conventions

This file lists decisions that should remain stable over time.
Karma SADE Architect should treat these as authoritative unless explicitly changed here.

## 1. Naming Conventions

- Main project name: "Karma SADE".
- Local folders:
  - Design: C:\Users\raest\Documents\Karma_SADE\Design
  - Memory: C:\Users\raest\Documents\Karma_SADE\Memory
  - Logs: C:\Users\raest\Documents\Karma_SADE\Logs
- Use underscores in Windows folder names when needed (e.g., Karma_SADE).

## 2. Safety and Change Management

- No destructive changes (deleting data, changing production configs) should be done directly by any agent.
- All risky changes must go through:
  1) Proposal in a chat,
  2) Written config/script in a file,
  3) Manual review and approval by the human (Neo),
  4) Then applied to the system.
- Karma SADE Architect should never assume it has direct shell access; it must always describe steps for the user to run.

## 3. Documentation and Memory

- Architecture and design docs live in the Design folder.
- Long-term facts and decisions live in the Memory folder and are synced into Open WebUI Knowledge.
- Logs and exported reports live in the Logs folder.
- When a decision becomes "how we do things now", it should be added or updated in this file.

## 4. Tools and Assistants

- Karma SADE Architect is the primary assistant for infrastructure and architecture planning.
- Perplexity Max is used for high-level research and external knowledge.
- Local tools (scripts, Sentinel, etc.) should be documented in Memory before being used by agents.

## 5. Future Extensions

- When new services (e.g., APIs, agents, databases) are added, their stable names, ports, and responsibilities should be recorded here.
- Any new "never do X" rule must be added to this file so it becomes part of persistent memory.

---

## Session 66 Decisions (2026-03-05) — Locked

### Decision #13: callGPTWithTools routes ALL non-Anthropic models
`callLLMWithTools()` line 868 in server.js must route non-Anthropic models to `callGPTWithTools(messages, maxTokens, model)` — note different param order than `callLLMWithTools(model, messages, maxTokens)`. GLM-4.7-Flash supports native function calling via Z.ai. This is now standard.

### Decision #14: TOOL_NAME_MAP must always be empty dict
`const TOOL_NAME_MAP = {};` in server.js is correct. Any entries remap tool names to wrong values (discovered pre-existing bug: `read_file → file_read` caused silent failure). Empty dict = identity passthrough via `|| toolName` fallback. Never add entries.

### Decision #15: Tool architecture split — get_vault_file in hub-bridge, graph_query in karma-server
- `get_vault_file`: handled directly in hub-bridge `executeToolCall()` — hub has `/karma/` volume mount (read-only)
- `graph_query`: proxied to karma-server — karma-server has FalkorDB access via `get_falkor()`
- karma-server `ALLOWED_PATHS` does NOT cover `/karma/` paths — any file-system tools for vault files must stay in hub-bridge

### Decision #16: hooks.py ALLOWED_TOOLS is mandatory whitelist — new tools must be added
Adding a tool to TOOL_DEFINITIONS in server.js + handler in karma-server is NOT sufficient. Must also add to `karma-core/hooks.py` `ALLOWED_TOOLS` set or the tool will be silently rejected with `{"ok":false,"error":"Unknown tool: X"}` before reaching the handler. Requires karma-server rebuild.

### Decision #17: vault-neo git pull strategy after squash merge
After a squash merge to main, vault-neo local branch diverges (non-linear history). Standard pull fails. Use: `git fetch origin && git reset --hard origin/main`. This is safe because vault-neo is deployment-only (no local-only commits per CLAUDE.md). Consider making this the standard vault-neo pull command permanently.

### Decision #18: compose up -d required to re-read hub.env
`docker restart anr-hub-bridge` reuses existing container environment and does NOT re-read env_file entries from compose. Any hub.env change requires `docker compose -f compose.hub.yml up -d` (recreates container). This is a Docker behavior, not a bug.
