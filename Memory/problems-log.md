# Karma SADE — Problems Log

Append-only. Every problem debugged in any session gets an entry here. If we debugged it, it goes here — no problem too small.

---

## 2026-03-05 Promise Loop — Karma says "Let me query that now" then never completes

**Symptom:** Karma responds with "Let me query the graph now" / "Let me check that" and then produces no result, forcing Colby to wait 20–30 minutes with no output. Loops indefinitely.

**Root cause(s):**
- RC1 (server.js line 413): `buildSystemText()` injected `"Tools: get_vault_file(alias) | graph_query(cypher)"` into the system prompt for ALL modes — but these tools don't exist in `TOOL_DEFINITIONS`. Karma called non-existent tools, failed silently, returned placeholder text.
- RC2 (server.js line 868): `callLLMWithTools()` gated at `if (!isAnthropicModel(model)) return callLLM(model, messages, maxTokens)` — bypassing tool definitions entirely for GLM (~80% of traffic). GLM never received tool definitions, couldn't call any tool.
- RC3 (system prompt): Claimed context was "~1800 chars" when `KARMA_CTX_MAX_CHARS` was already 12,000 in hub.env. Karma made confident claims based on wrong self-model.
- RC4 (hub.env): `GLM_RPM_LIMIT` defaulted to 20 from routing.js. Rate limit silently dropped requests at scale.

**Fix:**
- RC1: Line 413 text replaced with accurate deep-mode-gated tool description. Old: `"Tools: get_vault_file(alias) | graph_query(cypher)"` → New: `"Tools available in deep mode only: graph_query(cypher), get_vault_file(alias), ... In standard GLM mode: NO tools."`
- RC2: Line 868 changed `callLLM(model, messages, maxTokens)` → `callGPTWithTools(messages, maxTokens, model)` (note different param order)
- RC3: System prompt corrected to "~12,000 chars (controlled by KARMA_CTX_MAX_CHARS env var)"
- RC4: `GLM_RPM_LIMIT=40` added to hub.env on vault-neo; deployed via `docker compose up -d` (NOT docker restart — see below)

**Verified by:** Hub-bridge logs showed `callGPTWithTools, model: glm-4.7-flash` → `finish_reason="tool_calls"` → tool executed → `finish_reason="stop"`. Karma returned actual FalkorDB query results in same response. Session 66 end-to-end verified.

**Residual risk:** If GLM_RPM_LIMIT is not set in hub.env, defaults back to 20 RPM (routing.js line 94). If hub.env is recreated from compose template, the custom value is lost.

**Status:** RESOLVED

---

## 2026-03-05 graph_query tool rejected with "Unknown tool" error

**Symptom:** After wiring graph_query into TOOL_DEFINITIONS in server.js and the handler in karma-core/server.py, Karma's tool call returned `{"ok":false,"error":"Unknown tool: graph_query","hook":"pre_tool_use"}`.

**Root cause:** `karma-core/hooks.py` has an `ALLOWED_TOOLS` set that gates ALL incoming tool calls BEFORE reaching `execute_tool_action()`. New tools are rejected at the hook layer unless explicitly added to the whitelist.

**Fix:** Added `"graph_query"` and `"get_vault_file"` to `ALLOWED_TOOLS` in hooks.py:
```python
ALLOWED_TOOLS = {"read_file", "write_file", "edit_file", "bash",
                 "shell_exec", "file_read", "file_write", "file_edit",
                 "graph_query", "get_vault_file"}
```

**Verified by:** Subsequent tool call returned actual FalkorDB rows. Hub-bridge logs showed tool execution path followed normally.

**Residual risk:** Every new tool added to TOOL_DEFINITIONS MUST also be added to hooks.py ALLOWED_TOOLS. This is a hidden requirement — no error from TOOL_DEFINITIONS, no error from server.py handler. The only failure signal is the hook rejection. Easy to forget.

**Status:** RESOLVED

---

## 2026-03-05 TOOL_NAME_MAP pre-existing bug — tool names mapped to wrong names

**Symptom:** (Latent) Anthropic deep-mode tool calls for read_file, write_file, edit_file, bash may have been silently broken for months. The bug was present before Session 66.

**Root cause:** `TOOL_NAME_MAP` in server.js was `{ "read_file": "file_read", "write_file": "file_write", "edit_file": "file_edit", "bash": "shell_exec" }`. But karma-server's `ALLOWED_TOOLS` and `execute_tool_action()` use the original names (`read_file`, not `file_read`). Every tool call was being remapped to the WRONG name and then rejected by hooks.py.

**Fix:** Replaced TOOL_NAME_MAP with empty dict `{}` which falls through to `|| toolName` identity passthrough in the mapping code. All tool names now pass through unchanged, matching karma-server's expectations.

**Verified by:** graph_query and get_vault_file worked correctly post-fix. Existing read_file/bash tools theoretically now work correctly too (not explicitly re-tested this session).

**Residual risk:** If TOOL_NAME_MAP is ever repopulated (e.g. someone thinks it should have entries), it will silently break all tool calls again. The correct value is always `{}`. Document: empty dict = correct.

**Status:** RESOLVED

---

## 2026-03-05 docker restart does not re-read hub.env env_file entries

**Symptom:** Added `GLM_RPM_LIMIT=40` to hub.env. Ran `docker restart anr-hub-bridge`. Hub-bridge startup logs still showed "GLM rate limiter: 20 RPM".

**Root cause:** `docker restart` reuses the existing container's cached environment. It does NOT re-read `env_file` entries from compose. New env vars are silently ignored.

**Fix:** Must use `docker compose -f compose.hub.yml up -d` to recreate the container and re-read env_file. This takes slightly longer but ensures all hub.env changes are picked up.

**Verified by:** After `compose up -d`, hub-bridge startup logs showed "GLM rate limiter: 40 RPM".

**Residual risk:** This is a permanent Docker behavior. Any time a hub.env entry is added or changed, `compose up -d` is required, not `docker restart`. Must be documented in CLAUDE.md (done Session 66) and communicated to anyone operating the system.

**Status:** RESOLVED (behavior documented)

---

## 2026-03-05 vault-neo divergent branch after squash merge

**Symptom:** `git pull origin main` on vault-neo failed with "divergent branches" error after the Session 66 squash merge landed on GitHub main.

**Root cause:** Squash merge creates a new commit that has no linear history relationship to vault-neo's local main branch (which had the original feature branch commits). Git can't fast-forward.

**Fix:** `git rebase --abort` (to undo failed rebase attempt) then `git reset --hard origin/main`. This discards vault-neo's local commits in favor of origin. Safe because vault-neo is deployment-only (no local-only commits should ever exist per CLAUDE.md rules).

**Verified by:** `git log --oneline -3` on vault-neo showed correct squash commit hash after reset.

**Residual risk:** This pattern will recur with every squash merge. Vault-neo will always need `reset --hard` rather than `pull` when a squash merge lands. Alternative: configure vault-neo with `git config pull.rebase false` (merge strategy) or use `git fetch && git reset --hard origin/main` as the standard pull command.

**Status:** RESOLVED (workaround documented — consider making `reset --hard` the standard pull command on vault-neo)
