# Karma SADE - Session Learnings

This file contains learnings extracted from chat sessions.
It is automatically updated by Karma when important information is shared.

---

## [2026-03-05] SESSION 69 LEARNINGS (high)

**Pattern: TOOL_DEFINITIONS entries without handlers cause LLM confabulation**
If a tool is listed in TOOL_DEFINITIONS but has no handler in executeToolCall, it falls through to the karma-server proxy (which rejects it). The LLM sees it in the tool list and tells users it can use that capability. Rule: NEVER add a tool to TOOL_DEFINITIONS without either (a) an executeToolCall handler, or (b) a verified karma-server handler + hooks.py whitelist entry. Remove stale tools immediately when discovered.

**Pattern: hub-bridge-native tool handlers don't need hooks.py whitelist**
Tools handled directly in executeToolCall BEFORE the proxy fallthrough (like get_vault_file, write_memory, fetch_url) bypass karma-server entirely. They don't need to be in hooks.py ALLOWED_TOOLS. Only proxied tools (graph_query) need the whitelist. This is easy to confuse — check which path the tool takes before updating hooks.py.

**Pattern: compose.hub.yml lives in the build context directory**
`/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml` is the correct path. There's also one at `/home/neo/karma-sade/hub-bridge/compose.hub.yml` (in git). Build/deploy commands must use the build context path. The skill had the wrong path for months — verified by find on vault-neo.

**Pattern: fetch_url is the bridge between search snippets and research-grade context**
Brave Search gives title+URL+3-line snippet (good for factual lookups). fetch_url gives full page text (good for reading articles, evaluating sources, comparing options). The right usage split: Brave handles ambient search intent; fetch_url handles explicit "read this" requests from the user.

## [2026-03-05] SESSION 67 LEARNINGS (high)

**Pattern: GLM tool-calling gate must be at the CALL SITE, not inside the routing function**
Fixing `callLLMWithTools` to route to GLM correctly (Session 66) left the call site unconditional. The gate must be at the call site: `deep_mode ? callLLMWithTools() : callLLM()`. Security features need to be enforced at the request dispatch layer, not buried inside the function.

**Pattern: karma-verify false alarms when hub response schema drifts**
The skill checks for `reply` key but hub returns `assistant_text`. Smoke tests return FAILED on healthy services. Any time hub-bridge response schema changes, karma-verify skill must be updated. Check the skill's expected key matches the actual response before trusting "FAILED" output.

**Pattern: karma-server router.py is a dead code path**
karma-server has a full ModelRouter (router.py) with OpenAI-compatible multi-provider support. But karma-terminal (the only caller of karma-server /chat) has been stale since 2026-02-27. Router is untested, never called in production. Analysis: not worth swapping models for $0.12/month savings. Don't treat router.py as live architecture.

**Pattern: "three-in-one" mechanism design is more valuable than isolated features**
User's feedback thumbs up/down simultaneously solves write agency gating + DPO data collection + corrections pipeline. One UI gesture, three architectural wins. When designing feedback/approval mechanisms, check whether they can serve multiple layers of the system simultaneously.

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

---

## Session 68 Patterns (2026-03-05) — v9 Phase 4 Implementation

**Pattern: vault-api has a closed type enum**
`vaultPost()` with `type:"dpo-pair"` returns 422. Only `["fact","preference","project","artifact","log","contact"]` allowed. Use `type:"log"` with `tags:["custom-type"]` for custom record categories. Always check `dpResult.status >= 300` — fire-and-forget swallows vault rejections silently with no user-visible error.

**Pattern: hub-bridge build context is the PARENT directory**
`/opt/seed-vault/memory_v1/hub_bridge/` is the build context, not `hub_bridge/app/`. `COPY lib/ ./lib/` in Dockerfile resolves relative to the parent. New lib files must be at the parent level (`hub_bridge/lib/`) — not under `app/lib/`. Check Dockerfile COPY paths when adding new directories.

**Pattern: subagent SSH writes violate the never-edit-on-droplet rule**
Subagents with SSH access can accidentally write tracked files on vault-neo, making `git pull` abort. When giving subagents deployment instructions, explicitly forbid file writes under `/home/neo/karma-sade/`. Deployment should only use `cp` to build contexts (untracked paths), never to git-tracked directories.

**Pattern: buildVaultRecord() is mandatory for all vault writes**
Raw objects passed to `vaultPost()` fail schema validation. `buildVaultRecord({type, content, tags, source, confidence})` generates the required structure. This is true for DPO pairs, ambient records, and any new record types. Never call `vaultPost()` with a bare object.

**Pattern: two-review discipline catches bugs subagents miss**
Quality review after spec review caught 3 bugs in unified.html (null write_id guard, stale token capture, double-submit). Neither the implementer nor the spec reviewer found them — the code quality pass exists specifically for this class of subtle behavioral bug. The two-review pipeline is worth the token cost.

**Pattern: in-process Map is sufficient for single-node write gating**
`pending_writes` Map in server.js (module-level) is stateless-across-restarts but correct for the use case: write_id expires with TTL or on feedback. No Redis/external state needed. If hub-bridge is ever scaled horizontally (multiple instances), this breaks — but single-node is the current deployment.

## Session 72 Learnings (2026-03-10)

**Pattern: architectural gaps can be invisible for many sessions**
MEMORY.md was never injected into buildSystemText() — Karma was context-blind to her own session history for the entire system's lifetime. No error, no warning, just silent absence. Lesson: audit every context source at session start to verify it's actually flowing into /v1/chat. Don't assume injection is happening.

**Pattern: RELATES_TO vs MENTIONS — wrong edge type = permanently stale data**
Disabling Graphiti dedup (Session 59) stopped creating RELATES_TO edges. All 1,423 remain frozen at 2026-03-04. --skip-dedup creates only MENTIONS. Any code that queries RELATES_TO for "current" relationships is querying a snapshot from Chrome-extension era. Rule: after changing batch_ingest mode, audit all code that depends on edge types created by that mode.

**Pattern: hub-bridge multi-file sync is a recurring silent failure mode**
Two sessions now (68, 72) have had stale-code deploys because only server.js was synced to build context. The pattern: developer sees server.js in the diff, syncs it, misses lib/ or app/public/ files. Fix rule: always grep full diff before every deploy. Decision #27.

**Pattern: DIY beats external dependency when existing infrastructure covers the use case**
Context7 (external SaaS, 1,000 free calls/month) vs DIY get_library_docs (30min, reuses fetch_url, zero dependency). fetch_url already does HTML strip + 8KB cap. LIBRARY_URLS map covers Karma's actual [LOW] claim libraries. External service adds operational risk, account dependency, and call limit anxiety. When existing fetch infrastructure is adequate, use it.

**Pattern: combining related priorities into one system prompt section saves chars and improves coherence**
Confidence levels (#3) + anti-hallucination gate (#4) were two separate priorities but clearly belong in the same behavioral section. Combining them meant less back-and-forth between related rules and saved system prompt chars. Look for priority clusters that share behavioral context before adding separate sections.
