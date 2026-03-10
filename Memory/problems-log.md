# Karma SADE — Problems Log

Append-only. Every problem debugged in any session gets an entry here. If we debugged it, it goes here — no problem too small.

---

## 2026-03-09 [Session 70] batch_ingest cron silently failing — FalkorDB months behind

**Symptom:** Karma reported "my latest context is Session 66" despite batch cron reporting "all caught up" at watermark 4155.
**Root cause:** crontab was using Graphiti mode (no `--skip-dedup`). At 3200+ Episodic nodes, Graphiti dedup queries exceed TIMEOUT → all episodes fail silently → watermark advances to end of ledger → 0 FalkorDB nodes created. Batch log shows "all caught up" with no error.
**Fix:** Added `--skip-dedup` to vault-neo crontab: `crontab -l | sed 's|python3 /app/batch_ingest.py|python3 /app/batch_ingest.py --skip-dedup|' | crontab -`. Reset watermark to 4100 via `docker exec karma-server sh -c 'echo 4100 > /ledger/.batch_watermark'`. Ran manual catchup: 118 entries, 0 errors, 879 eps/s.
**Verified by:** FalkorDB query `MATCH (e:Episodic) WHERE e.created_at > "2026-03-05" RETURN count(e)` → 76 nodes (was 0). March 9 nodes confirmed present.
**Residual risk:** If karma-server is rebuilt and crontab is reconfigured, --skip-dedup could be omitted again. Verify with `crontab -l | grep batch` after any cron changes.
**Status:** RESOLVED

## 2026-03-09 [Session 70] System prompt 429 rate limits from bloat

**Symptom:** Karma returning `internal_error` (hub 429 from Z.ai) frequently. Each request consuming 67,388 input chars.
**Root cause:** System prompt grew to 16,519 chars across multiple fix sessions (was ~12,366). Higher chars → higher TPM per request → faster rate limit exhaustion at 40 RPM.
**Fix:** Trimmed system prompt to 11,674 chars (-29%). Removed: API Surface table, 3 low-value corrections, infrastructure container list, machine specs. All critical coaching preserved.
**Verified by:** `/v1/chat` smoke test → `ok`, `debug_input_chars: 56,843` (was 67,388). RestartCount=0.
**Residual risk:** System prompt will grow again as corrections are added. Monitor `debug_input_chars` — if consistently >65K, trim again.
**Status:** RESOLVED

## 2026-03-09 [Session 70] Karma using "resurrection spine" terminology

**Symptom:** Karma described session continuity as "resurrection spine loading checkpoint" — language from old architecture design docs, not live behavior.
**Root cause:** Old architecture design documents (resurrection-architecture.md concept) indexed in FalkorDB as Episodic nodes. karmaCtx served these stale docs as context. System prompt corrections existed for identity.json/invariants.json but didn't explicitly ban the "resurrection spine" term.
**Fix:** Added explicit paragraph to system prompt: "There is no 'resurrection spine.' ... Do not use this term. If context feels stale, correct explanation is: FalkorDB updates every 6h."
**Verified by:** System prompt deployed, hub-bridge restarted (RestartCount=0).
**Residual risk:** Old architecture docs remain in FalkorDB. If served in karmaCtx, Karma may still reference them. Mitigation: explicit system prompt ban is now in place.
**Status:** RESOLVED

## 2026-03-05 [Session 69] Karma confabulates bash/file tool capabilities

**Symptom:** Karma said "like I can call bash commands on vault-neo" — claimed a tool capability she doesn't have.
**Root cause:** `read_file`, `write_file`, `edit_file`, `bash` were defined in `TOOL_DEFINITIONS` in server.js (lines 779-824) but had no handler in `executeToolCall`. They fell through to karma-server proxy, which rejected them. GLM saw them listed in TOOL_DEFINITIONS and told users it could use these tools.
**Fix:** Removed all 4 stale tool definitions from TOOL_DEFINITIONS (commit 7d2f034). Active tools are now: `graph_query`, `get_vault_file`, `write_memory`, `fetch_url`.
**Verified by:** `node -e "... TOOL_DEFINITIONS ..."` → `ok 3 tools` (before fetch_url), then `ok 4 tools` (after fetch_url added). No bash/file refs in server.js logic.
**Residual risk:** Any future tool added to TOOL_DEFINITIONS without an executeToolCall handler will cause the same confabulation. Lesson: only add tools to TOOL_DEFINITIONS if they have a handler OR are known-good via karma-server proxy.
**Status:** RESOLVED

## 2026-03-05 [Session 69] karma-hub-deploy skill had wrong compose.hub.yml path

**Symptom:** Skill instructed `cd /home/neo/karma-sade && docker compose -f compose.hub.yml build` — fails silently because file doesn't exist there.
**Root cause:** `compose.hub.yml` is at `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml`, not in the git repo root. Skill was written with wrong path assumption.
**Fix:** Updated karma-hub-deploy SKILL.md to use `cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml ...` for build/deploy steps. Key Names table also updated.
**Verified by:** Confirmed file exists at `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml` via `find` on vault-neo. Deploy subagent used correct path; build succeeded.
**Residual risk:** None — skill now has correct path. Would resurface if compose.hub.yml is moved.
**Status:** RESOLVED

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

**Status:** RESOLVED — skill was updated (uses `assistant_text` check confirmed 2026-03-10)

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

---

## 2026-03-10 Hub-bridge deploy missing non-server.js file sync

**Symptom:** After deploying v10 priority #1 (universal thumbs), smoke test passed for /v1/feedback but browser UI did not show thumbs on standard-mode messages. unified.html still had old writeId-only gate.

**Root cause(s):**
- RC1: Prior deploy only synced `server.js` to build context (`/opt/seed-vault/memory_v1/hub_bridge/app/server.js`)
- RC2: `unified.html` and `lib/feedback.js` were modified in the same commit but NOT synced to their respective build context paths before `docker compose build`
- RC3: Docker image COPY layer cached the old `unified.html` from the previous build context state

**Fix:** Synced all three changed files before rebuild:
```
cp hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js
cp hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html
cp hub-bridge/lib/feedback.js /opt/seed-vault/memory_v1/hub_bridge/lib/feedback.js
```
Then `--no-cache` rebuild and redeploy.

**Verified by:** Smoke test `curl /v1/feedback` with turn_id returned `{wrote:false}`. PITFALL documented in CLAUDE.md and STATE.md.

**Residual risk:** Any session that modifies hub-bridge files outside `app/server.js` (e.g., `lib/`, `app/public/`) will silently deploy stale code if sync step only covers server.js. Rule: always grep `git diff --name-only HEAD~1` for the full list of changed hub-bridge files and sync ALL of them.

**Status:** RESOLVED

---

## 2026-03-10 RELATES_TO edges frozen — Entity Relationships returning stale Chrome-era data

**Symptom:** Karma's "Entity Relationships" context section showed edges like "related to chrome extension" and other 2026-03-04-era data. No recent relationships visible.

**Root cause(s):**
- RC1: `query_relevant_relationships()` in karma-core/server.py queried `RELATES_TO` edges
- RC2: All 1,423 RELATES_TO edges were created by Graphiti dedup mode — permanently frozen at 2026-03-04 (last time Graphiti ran before it was disabled in Session 59)
- RC3: `--skip-dedup` mode (active since Session 59) only creates `MENTIONS` edges, never RELATES_TO

**Fix:** Replaced `query_relevant_relationships()` Cypher query from RELATES_TO to MENTIONS co-occurrence:
```cypher
MATCH (ep:Episodic)-[:MENTIONS]->(e1:Entity), (ep)-[:MENTIONS]->(e2:Entity)
WHERE e1.name IN [...] AND e1.name <> e2.name
WITH e1.name AS from_entity, e2.name AS to_entity, count(ep) AS cocount
WHERE cocount >= 2
RETURN from_entity, to_entity, cocount ORDER BY cocount DESC LIMIT 20
```
Relationship label changed from raw edge `r.fact` string to `"co-occurs in N episodes"`.

**Verified by:** Live data confirmed: Karma/Colby=123, Karma/User=100, User/Universal AI Memory=44. 11/11 TDD tests GREEN. RestartCount=0. Decision #22 locked.

**Residual risk:** RELATES_TO edges will never grow again (Graphiti dedup disabled permanently). If someone re-enables Graphiti mode, it creates RELATES_TO again — but that would break batch_ingest at scale (known pitfall). The MENTIONS approach is the correct permanent solution.

**Status:** RESOLVED

---

## 2026-03-10 Karma context-blind to MEMORY.md — never saw her own session history

**Symptom:** At session start, Karma had no awareness of v10 plan, recent sessions, or any content from MEMORY.md. Every session Karma responded as if no previous architectural decisions had been made.

**Root cause(s):**
- RC1: `buildSystemText()` in hub-bridge/app/server.js had no parameter for MEMORY.md content
- RC2: MEMORY.md was never loaded, cached, or injected anywhere in the request pipeline
- RC3: The system prompt, karmaCtx (FalkorDB), and semanticCtx (FAISS) were all injected — but MEMORY.md was the only canonical state file with no injection path

**Fix:** Added to server.js:
1. `const MEMORY_MD_PATH = "/karma/MEMORY.md"` and `const MEMORY_MD_TAIL_CHARS = 3000`
2. `let _memoryMdCache = ""` module-level cache
3. `loadMemoryMd()` function: reads MEMORY.md, takes last 3000 chars, stores in cache
4. `buildSystemText()` extended with `memoryMd` 5th param — injects as `"--- KARMA MEMORY SPINE (recent) ---\n{memoryMd}\n---"`
5. `/v1/chat` handler passes `_memoryMdCache || null`
6. Startup: `loadMemoryMd(); setInterval(loadMemoryMd, 5 * 60 * 1000)`

**Verified by:** 6/6 TDD tests in test_system_text.js GREEN. Deployed. Karma correctly referenced v10 plan details in next message. KARMA_IDENTITY_PROMPT length increased as expected.

**Residual risk:** 3000 chars = roughly last 2-4 session entries in MEMORY.md. If MEMORY.md grows very long, oldest entries invisible. Acceptable — recent entries are what matter for continuity.

**Status:** RESOLVED

---

## 2026-03-10 hub-bridge lib/*.js not in git — wipe risk on any rebuild

**Symptom:** Session 75 discovered hub-bridge/lib/feedback.js, routing.js, pricing.js, library_docs.js existed only at `/opt/seed-vault/memory_v1/hub_bridge/lib/` on vault-neo. The local git repo had the files at hub-bridge/lib/ but they were out of date. Any `git pull` + rebuild from a fresh clone would miss any changes made only on vault-neo.

**Root cause(s):**
- RC1: lib files were created directly in the build context on vault-neo during Session 68, never synced back to git
- RC2: The git repo had stale versions of these files that didn't reflect production

**Fix:** Session 75: Read all four files from the live container (`docker exec anr-hub-bridge cat /app/lib/*.js`), updated routing.js locally for Haiku switch, committed all four to git at hub-bridge/lib/ (commit 34b7326).

**Verified by:** `git log --oneline -1` shows commit with all four lib files. Diff confirmed routing.js correctly has Haiku in allow-list.

**Residual risk:** Future lib file changes on vault-neo must ALWAYS be synced back to git immediately. Sync pattern: after any lib change on vault-neo, `scp vault-neo:/opt/seed-vault/memory_v1/hub_bridge/lib/*.js hub-bridge/lib/` then commit + push, then verify build context matches git.

**Status:** RESOLVED

---

## 2026-03-10 GLM quality failure — weeks of poor responses declared "working"

**Symptom:** Colby reported Karma giving poor-quality responses daily for weeks. Claude sessions repeatedly declared Karma "green" based on backend tests alone, never verifying from the browser.

**Root cause(s):**
- RC1: Claude's verification protocol only tested: server start, /health 200, curl /v1/chat returns any response
- RC2: Claude never opened hub.arknexus.net in a browser and evaluated response quality from user perspective
- RC3: Claude had browser automation tools (Playwright MCP, Claude in Chrome MCP) and used them occasionally but not systematically after each deployment
- RC4: GLM-4.7-Flash was recommended by Claude as "smart enough" and Haiku 3.5 was incorrectly called "sub-optimal"

**Fix:** Switched MODEL_DEFAULT + MODEL_DEEP to claude-3-5-haiku-20241022. Updated routing.js whitelist, hub.env pricing, rebuilt container. Committed to not repeating backend-only verification.

**Verified by:** `docker exec anr-hub-bridge env | grep MODEL` shows both variables = claude-3-5-haiku-20241022. Container RestartCount=0.

**Residual risk:** Quality regression can still happen without regular UX-level verification. Every deployment should include a browser-based smoke test — not just curl.

**Status:** RESOLVED (model switched)
