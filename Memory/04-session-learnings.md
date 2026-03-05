# Karma SADE - Session Learnings

This file contains learnings extracted from chat sessions.
It is automatically updated by Karma when important information is shared.

---

## [2026-03-05] SESSION 66 LEARNINGS (high)

**Pattern: hooks.py is a hidden whitelist gate**
Every new tool added to TOOL_DEFINITIONS in server.js must ALSO be added to `ALLOWED_TOOLS` in karma-core/hooks.py. The failure mode is silent: `{"ok":false,"error":"Unknown tool: X"}` with no hint that the whitelist is the issue. Any time tool calls fail unexpectedly, check hooks.py first.

**Pattern: TOOL_NAME_MAP must stay empty**
`const TOOL_NAME_MAP = {};` is the correct value. The pre-existing bug had name remapping that silently broken tools. Empty dict = identity passthrough. Never add entries.

**Pattern: docker restart vs compose up -d**
`docker restart` reuses existing env. `compose up -d` re-reads env_file. For any hub.env change (env vars, new keys), must use `compose up -d`. Silent failure if you use restart — hub starts but uses stale env.

**Pattern: squash merge causes vault-neo divergence**
After a squash merge to main, vault-neo needs `git fetch origin && git reset --hard origin/main` (not `git pull`). Squash creates non-linear history that git can't fast-forward through.

**Pattern: callGPTWithTools parameter order differs**
`callLLMWithTools(model, messages, maxTokens)` but `callGPTWithTools(messages, maxTokens, model)`. The `model` parameter moves to the end. This is easy to get wrong when refactoring the routing line.

**Pattern: system prompt self-model accuracy matters for behavior**
When Karma's system prompt described non-existent tools, she promised to use them and then looped indefinitely when they failed. Accurate self-knowledge (what tools exist, what mode is active, what context size she has) directly determines whether she makes accurate or false promises. System prompt honesty is not cosmetic — it changes runtime behavior.

---

## [2026-02-09 21:17:02] FACT (high)
Neo successfully set up the Karma persistent memory system on February 10, 2026

## [2026-02-09 21:18:17] DECISION (high)
Memory system test successful. Karma correctly recalled user facts, preferences, and context from persistent storage.

## [2026-02-09 21:27:49] AUTO-EXTRACTED
{'key': 'change_management_rules', 'value': '1. Architect proposes specific text to add or change.\n2. The human (Neo) reviews and edits the actual file.\n3. The updated file is re-uploaded or re-indexed into Open WebUI Knowledge.'}

## [2026-02-09 21:29:25] AUTO-EXTRACTED
Implement Docker Compose for service orchestration

## [2026-02-09 21:29:25] AUTO-EXTRACTED
Introduce secrets management with Hashicorp Vault

## [2026-02-12 01:12:59] SYSTEM (high)
requested system optimizations

## [2026-02-12 01:48:36] CONTEXT (normal)
The last timestamp mentioned in the conversation is 2026-02-12
