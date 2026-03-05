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

---

## 2026-03-05 Standard GLM chat requests got full tool-calling access (security)

**Symptom:** Any standard chat request to /v1/chat (deep_mode=false) could trigger tool calls. Session 66's GLM tool-calling fix enabled tools for ALL requests, not just deep-mode ones.

**Root cause:** In Session 66, `callLLMWithTools()` was wired correctly for non-Anthropic models. But the call site at line 1271 called `callLLMWithTools()` unconditionally — no check of `deep_mode`. Standard requests with `deep_mode=false` went through the full tool execution path.

**Fix:** Branched at the call site (hub-bridge server.js line 1269-1272):
```javascript
const llmResult = deep_mode
  ? await callLLMWithTools(model, messages, max_output_tokens)
  : await callLLM(model, messages, max_output_tokens);
```
Also removed stale DIAGNOSTIC log that was left in from Session 66 debugging.

**Verified by:** Smoke test: `curl -s -X POST localhost:18090/v1/chat -d '{"message":"ping"}'` returned `ok:True` with no tool execution. `deep_mode` was false in response telemetry.

**Residual risk:** Any future routing changes at the callLLMWithTools call site must preserve the deep_mode gate.

**Status:** RESOLVED (commit 41b2c06)

---

## 2026-03-05 karma-verify smoke test returns FAILED on healthy hub-bridge

**Symptom:** karma-verify skill smoke test command returned "FAILED" even though hub-bridge was healthy and returning valid responses.

**Root cause:** karma-verify skill checks `/v1/chat` response for `r.get("reply")`. But hub-bridge returns `assistant_text`, not `reply`. The key name drifted at some point without updating the skill.

**Fix:** For this session, rewrote the check inline: `r["ok"] and bool(r.get("assistant_text"))`. The skill file itself still uses the wrong key.

**Verified by:** Manual smoke test with corrected check showed ok:True, assistant_text returned.

**Residual risk:** karma-verify skill will continue to false-alarm on every smoke test until the skill is updated. Action: update `C:\Users\raest\.claude\skills\karma-verify\SKILL.md` to check `assistant_text` instead of `reply`.

**Status:** OPEN — skill not yet updated

---

## 2026-03-05 DPO vault record missing required buildVaultRecord structure

**Symptom:** `/v1/feedback` endpoint logged "DPO pair stored successfully" but `grep "dpo-pair" /opt/seed-vault/memory_v1/ledger/memory.jsonl` returned zero results.

**Root cause:** `vaultPost()` was called with a bare object `{ type: "dpo-pair", content: {signal, note, write_content}, ... }`. Vault-api schema requires: (a) `buildVaultRecord()` wrapper that adds `confidence`, `verification`, `source` as `{kind, ref}` object, and converts `content` to a nested object. (b) vault only accepts types `["fact","preference","project","artifact","log","contact"]` — not `"dpo-pair"`. (c) `vaultPost()` was fire-and-forget — no status check, so 422 errors were swallowed silently.

**Fix (2 iterations):**
- Fix 1 (commit 69f061b): switched to `buildVaultRecord({type:"dpo-pair",...})` — got closer but vault still rejected unknown type
- Fix 2 (commit cf63957): `type:"log"` with `tags:["dpo-pair"]`; added `if (dpResult.status >= 300) throw new Error(...)` status check

**Verified by:** `grep dpo-pair /opt/.../memory.jsonl` returned 1 hit with `type:log, tags:["dpo-pair"], content.signal:"down"`. Ledger count went from 4118→4119.

**Residual risk:** Any future custom record types must be checked against vault-api's allowed-type enum. The enum is not visible from hub-bridge — must test or read vault-api source. Fire-and-forget vaultPost pattern is dangerous — always add status check.

**Status:** RESOLVED

---

## 2026-03-05 hub-bridge lib/ directory missing from build context

**Symptom:** After Task 6 deployment, hub-bridge failed to start — `Cannot find module '/app/lib/feedback.js'`.

**Root cause:** Build context for hub-bridge is `/opt/seed-vault/memory_v1/hub_bridge/` (parent). The Dockerfile has `COPY lib/ ./lib/`. But `lib/` directory never existed in the build context — only `app/` was there. Copying `feedback.js` to `/opt/.../hub_bridge/app/lib/` (wrong path) didn't fix it.

**Fix:** `ssh vault-neo "mkdir -p /opt/seed-vault/memory_v1/hub_bridge/lib/ && cp /opt/.../hub_bridge/app/lib/feedback.js /opt/.../hub_bridge/lib/feedback.js"`. Rebuild then succeeded.

**Verified by:** Hub-bridge started cleanly, smoke test returned ok:True.

**Residual risk:** Any new file added under `hub-bridge/lib/` on local must also be copied to `/opt/.../hub_bridge/lib/` on vault-neo (NOT under `app/lib/`). This is a non-obvious two-location requirement.

**Status:** RESOLVED

---

## 2026-03-05 vault-neo MEMORY.md dirty from subagent SSH writes

**Symptom:** `git pull origin main` on vault-neo aborted with "Your local changes to the following files would be overwritten by merge: MEMORY.md".

**Root cause:** Subagent SSH sessions during Session 68 Tasks 5/6 appended directly to `/home/neo/karma-sade/MEMORY.md` on vault-neo. This violates CLAUDE.md's "never edit files directly on vault-neo" rule. The droplet is a deployment target only — MEMORY.md must be updated via PATCH /v1/vault-file or via git locally then pull.

**Fix:** `ssh vault-neo "cd /home/neo/karma-sade && git checkout -- MEMORY.md && git pull origin main"`. Overwrote droplet changes with local canonical version.

**Verified by:** `git status` on vault-neo showed clean; `git log --oneline -1` matched local HEAD.

**Residual risk:** Any subagent that SSHes to vault-neo and runs commands may accidentally write to tracked files. Subagent prompts must explicitly forbid SSH file writes to /home/neo/karma-sade/. Best fix: NEVER give subagents SSH access to vault-neo for deployment steps.

**Status:** RESOLVED

---

## 2026-03-05 Bare newline in fs.appendFileSync template literal (subagent CRLF injection)

**Symptom:** Code review flagged `fs.appendFileSync(filePath, \`\n[${timestamp}]...\`)` as having a "bare newline" inside the template literal. Subagent fix attempt replaced it with CRLF bytes rather than the `\n` escape sequence.

**Root cause:** Subagent wrote the fix by SSH heredoc, which converts literal `\n` in the shell string to actual newline bytes (0x0a). JavaScript string literal then contained a raw newline character inside the string — not the `\n` escape. This is the same known pitfall documented in CLAUDE.md (heredoc + JS escape sequences).

**Fix:** Direct Edit tool on local file, changing the literal newline to the `\n` escape: `\`\n[${timestamp}] [KARMA-WRITE] ${write_content}\``. Verified with grep showing single-line output.

**Verified by:** `grep "KARMA-WRITE" server.js | wc -l` returned 1 (single line, no split across lines). Commit b002b5b.

**Residual risk:** Any time a subagent generates JS file content via SSH heredoc, escape sequences may become literal bytes. Always verify after subagent edits to JS files with `grep -P '\x0a' targetString` or `wc -l` cross-check.

**Status:** RESOLVED
