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

---

## Session 72 Decisions (2026-03-10) — Locked

### Decision #22: MENTIONS co-occurrence replaces stale RELATES_TO in query_relevant_relationships()
RELATES_TO edges (1,423) are permanently frozen at 2026-03-04 — created only by Graphiti dedup mode which was disabled Session 59. --skip-dedup (permanent mode) creates only MENTIONS edges. Correct Cypher: Episodic→Entity cross-join via MENTIONS edges, cocount >= 2, ORDER BY cocount DESC LIMIT 20. Relationship label: "co-occurs in N episodes". Never use RELATES_TO for live relationship data again.

### Decision #23: Confidence level tags [HIGH]/[MEDIUM]/[LOW] mandatory on technical claims in Karma system prompt
[HIGH] = verified in current context this session. [MEDIUM] = reasonable inference from adjacent evidence. [LOW] = unverified. Tag goes on specific claim, not every sentence. [HIGH] must be rare — value comes from rarity. Applied in system prompt section "Confidence Levels — Mandatory for Technical Claims".

### Decision #24: Anti-hallucination hard stop before [LOW] claims
Before asserting unverified API behavior, function signatures, or endpoint paths: Karma must STOP and write "[LOW] I haven't verified this. Should I fetch_url, get_library_docs, or graph_query to confirm first?" Do not proceed with the unverified claim. In standard mode: "[LOW] This isn't in my current context — check docs or run a query via CC."

### Decision #25: Context7 rejected — DIY get_library_docs with URL map using existing fetch_url logic
Context7 free tier (1,000/month) covers estimated usage (60-750/month) but adds external dependency + account. DIY: lib/library_docs.js with LIBRARY_URLS map (redis-py, falkordb, falkordb-py, fastapi) + resolveLibraryUrl() pure function. handler reuses existing fetch_url HTML strip + 8KB cap pattern. No new dependencies.

### Decision #26: Universal thumbs on all Karma messages via turn_id fallback
Every Karma response shows 👍/👎 regardless of write_memory presence. /v1/feedback accepts turn_id OR write_id — write_id takes priority. General quality signal + DPO pair accumulation in standard mode. Thumbs-down + note feeds correction pipeline. Backward compatible — existing write_memory gate unchanged.

### Decision #27: hub-bridge file sync must cover ALL changed files, not just server.js
Build context is /opt/seed-vault/memory_v1/hub_bridge/ (parent). lib/ files sync to parent/lib/, app/public/ files sync to parent/app/public/, server.js syncs to parent/app/server.js. Before any --no-cache rebuild, grep changed files: `git diff --name-only HEAD~1 | grep hub-bridge` and sync every one to build context. Syncing only server.js is the #1 cause of stale hub-bridge deploys.
