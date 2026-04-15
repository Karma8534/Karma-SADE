# Claim Line Map 041426
Generated: 2026-04-14T22:20:50.756364
This map is extraction-only (claims/spec text), not truth proof.

## docs\ForColby\nexus.md
- Total lines: 98
- Extracted claim lines: 26

| Line | Type | Snippet |
|---:|---|---|
| 3 | claim | Truth policy: fail-closed. Every status claim below is backed by current-pass command/probe/test evidence. |
| 7 | completion-claim | ### VERIFIED CURRENT STATE |
| 22 | completion-claim | ### VERIFIED EMERGENCY INDEPENDENCE (ANTHROPIC-OUTAGE SURVIVAL) |
| 32 | claim | - `tmp/electron-smoke-emergency-ship-041126.json` has `ok=true`, `directResult.provider=openrouter`, `uiResult.ok=true`, memory hit present. |
| 34 | completion-claim | ### VERIFIED BUILD / TEST / SHIP GATES |
| 38 | claim | - Emergency fallback regression coverage includes OpenRouter-first cascade and fallback order assertions. |
| 40 | completion-claim | ### VERIFIED CURRENT STATE`n- Full browser/electron parity matrix now passes via `Scripts/nexus_parity_matrix.py` (`tmp/parity-matrix-latest.json` => `ok=true`). |
| 44 | requirement | 2. Runtime spine: hub proxy + P1 harness + K2 support + vault services must be healthy. |
| 45 | requirement | 3. Primary/fallback contract: primary may be unavailable; emergency-independent OpenRouter-first route must keep app alive. |
| 46 | requirement | 4. App surfaces: frontend build artifact + Electron harness must both execute chat/memory loops. |
| 47 | requirement | 5. Persistence controls: server launcher + persistent loop + watchdog/startup semantics must keep runtime recoverable. |
| 48 | requirement | 6. Verification floor: deterministic tests + authenticated endpoint probes + smoke artifact must all pass in same run. |
| 56 | claim | - Cortex/synthesis support and fallback support host. |
| 59 | completion-claim | - Deployed hub/vault runtime spine. |
| 61 | claim | ## PRIMARY VS FALLBACK PATHS |
| 66 | completion-claim | ### Emergency Runtime Contract (Verified) |
| 67 | requirement | - When Anthropic path is unavailable or disabled, system must survive via OpenRouter-first cascade, then Groq/Ollama/K2. |
| 68 | completion-claim | - This emergency contract is now deployed and verified in both P1 server and Electron harness. |
| 72 | completion-claim | ### VERIFIED CURRENT STATE |
| 73 | completion-claim | - OpenRouter emergency fallback deployed in `Scripts/cc_server_p1.py` and `electron/main.js`. |
| 75 | completion-claim | - Server process redeployed and verified healthy after patch. |
| 76 | completion-claim | - Hub path verified live after deployment. |
| 78 | requirement | ### REQUIRED FUTURE WORK`n1. Continue periodic parity reruns after code changes (maintenance, not blocker). |
| 86 | claim | - Electron smoke artifact confirms direct provider and UI+memory success. |
| 95 | claim | - Keep fallback order tested whenever routing logic changes. |
| 98 | completion-claim | ## DEFINITION OF DONE`nA Nexus shippable milestone is done only when:`n1. Build and recursive deterministic tests pass in the same run.`n2. Parity matrix and organic walkthrough artifacts pass in the same run.`n3. Run... |

## docs\ForColby\nexus.md.bak
- Total lines: 1286
- Extracted claim lines: 258

| Line | Type | Snippet |
|---:|---|---|
| 4 | completion-claim | **Version:** 4.1.0 (S154 deployed + verified live) \| **Date:** 2026-04-01 |
| 15 | requirement | > merge instead of the 3 separate tabs THIS wrapper has. You must have |
| 16 | requirement | > persistent memory and persona. You must self-improve, evolve, learn, grow, |
| 20 | claim | **The endpoint:** Substrate-independent distributed intelligence across every reachable device. |
| 26 | claim | Karma is THIS Claude Code wrapper — evolved. Same brain (CC --resume via Max, $0), same tools (Bash, Read, Write, Edit, Git, Glob, Grep, MCP, skills, hooks, subagents), same persona (CLAUDE.md), same memory (claude-me... |
| 41 | claim | │                  vault ledger + FalkorDB + FAISS + MEMORY.md + persona files + claude-mem |
| 46 | completion-claim | CORTEX ─────────── 32K local working memory. qwen3.5:4b on K2 (primary) / P1 (fallback). |
| 47 | completion-claim | │                  Active working set, cheap recall. NOT canonical identity. |
| 62 | claim | proxy.js does NOT assemble prompts, route models, or execute tools. |
| 77 | completion-claim | \| CORTEX \| Active working set, cheap recall ($0) \| Canonical identity (that's SPINE) \| |
| 82 | completion-claim | ## What EXISTS (verified S154) |
| 90 | claim | \| agora.html \| LIVE \| /agora, real K2 spine stats via /spine endpoint \| |
| 91 | claim | \| K2 cortex (julian_cortex.py) \| LIVE \| K2:7892, 107 blocks, /spine endpoint \| |
| 96 | claim | \| Coordination bus \| LIVE \| proxy.js in-memory + disk, 24h TTL \| |
| 101 | claim | \| Self-edit \| PROVEN \| self-edit-proof.txt modified from browser S151 \| |
| 111 | claim | \| Context Panel \| BUILT \| ContextPanel.tsx — 4 tabs (files/memory/agents/preview), proxy routes added (S154) \| |
| 119 | gap/blocker | ### Gap 1: Streaming [SHIPPED S153] |
| 124 | gap/blocker | ### Gap 2: Rich Output Rendering [SHIPPED S153] |
| 129 | gap/blocker | ### Gap 3: File/Image Input [SHIPPED S154] |
| 132 | completion-claim | **Status:** SHIPPED. Drag-drop zone + paste handler + file button (`+`) in unified.html. Base64 encoding, preview chips, proxy forwarding. cc_server_p1.py decodes files to temp dir, prepends Read tool instruction to m... |
| 134 | gap/blocker | ### Gap 4: CLI Flag Mapping [SHIPPED S154] |
| 137 | completion-claim | **Status:** SHIPPED. Effort selector dropdown in header bar (auto/quick/normal/deep/max). `getEffort()` reads value, sent in request body, proxy.js forwards, cc_server_p1.py passes `--effort` flag to CC CLI. Full pipe... |
| 139 | gap/blocker | ### Gap 5: Cancel Mechanism [SHIPPED S153] |
| 142 | claim | **Status:** SHIPPED. Esc key + STOP button. proxy.js /v1/cancel route. cc_server_p1.py kills subprocess. |
| 144 | gap/blocker | ### Gap 6: Evolution Visibility + Feedback [SHIPPED S153] |
| 147 | claim | **Status:** SHIPPED. AGORA has Approve/Reject/Redirect buttons, real K2 spine stats (1299 promotions, v1257, 20 stable patterns), pipeline health from /spine endpoint. |
| 149 | completion-claim | ### Gap 7: Reboot Survival [NOT DONE] |
| 159 | claim | **Verify:** Reboot P1 → wait 60s → `curl localhost:7891/health` → ok. |
| 161 | gap/blocker | ### Gap 8: Electron Desktop App [SHIPPED S154] |
| 168 | claim | **Verify:** Double-click Karma icon → opens → full CC capabilities available. |
| 174 | requirement | The 8 gaps close the CHAT experience. But the original goal says "combined Chat+Cowork+Code merge." This means the Nexus must also have: |
| 181 | claim | \| CLAUDE.md persona \| Backend: CC reads it. UI: NO persona editor. \| Persona viewer (read-only minimum) \| |
| 187 | completion-claim | **"Pipe-through" = the backend CAN do it. "Done" = the USER can access it from the UI.** |
| 197 | gap/blocker | ├── Gap 1: Streaming ✅ |
| 198 | gap/blocker | ├── Gap 2: Rich output ✅ |
| 199 | gap/blocker | └── Gap 5: Cancel ✅ |
| 202 | completion-claim | ├── Gap 3: File input ✅ (fixed --file flag, Read tool prefix, file-only sends) |
| 203 | completion-claim | └── Gap 4: CLI flags ✅ (effort selector dropdown, full pipeline verified) |
| 205 | completion-claim | Sprint 3: Foundations (Option A — zero rework path) — SHIPPED S154 (deployed + verified live) |
| 223 | completion-claim | Sprint 4: The Surface (built on Sprint 3 foundations) — SHIPPED S154 (deployed + verified live) |
| 226 | claim | ├── 4c: Context Panel ✅ SHIPPED S154 (/v1/surface + /v1/spine + /v1/memory/search live on hub.arknexus.net) |
| 227 | completion-claim | ├── 4d: Self-Edit Engine + Banner ✅ SHIPPED S154 (/v1/self-edit/pending live, propose/approve/reject endpoints working) |
| 235 | claim | └── 4e: Electron wiring ✅ SHIPPED S154 (window opens, UI loads, message sent — screenshot proof) |
| 237 | gap/blocker | Sprint 5: The Evolution (Gap 6) — SHIPPED S153 |
| 238 | gap/blocker | └── Gap 6: Evolution feedback ✅ |
| 240 | completion-claim | Sprint 6: Memory Operating Discipline (Phase 7B) — NOT DONE |
| 242 | claim | ├── 6b: Typed memory tiers |
| 247 | claim | └── 6g: Memory migration/fusion |
| 249 | gap/blocker | Final Phase: Reboot Survival (Gap 7) — DEFERRED |
| 250 | gap/blocker | └── Gap 7: schtasks entry for cc_server_p1.py |
| 275 | claim | ## Phase 7: Intelligence Primitives (Aider + Roo-Code + Memory Research) |
| 277 | completion-claim | **Status:** NOT STARTED. Foundation sprints must complete first. |
| 289 | claim | ### 7B: Memory Operating Discipline (from MemOS + DRIFT + LycheeMemory + MSA + AllMem) |
| 298 | completion-claim | → load into cortex working-memory (local-window priority)   [AllMem principle] |
| 305 | claim | \| 7-5 \| **MemCube schema** — upgrade ledger entries with lifecycle metadata: provenance, confidence, verification state, version, lineage, promotion state, decay policy. Each entry becomes a managed memory object, n... |
| 306 | completion-claim | \| 7-6 \| **Typed memory tiers** — classify entries into: raw (unprocessed), distilled (extracted fact), stable (repeated/verified pattern), archived (cold, low-access). Tier determines recall priority and decay. \| M... |
| 308 | completion-claim | \| 7-8 \| **Gated recall** — add a relevance gate between retrieval and cortex ingestion. Gate scores each candidate memory against the current query and drops irrelevant blocks. Only top-K pass to the cortex working ... |
| 310 | claim | \| 7-10 \| **Local-window priority** — cortex prioritizes: (1) current turn/thread context, (2) recalled persistent memory, (3) deep archival only on demand. Prevents stale memory from dominating fresh context. \| All... |
| 311 | claim | \| 7-11 \| **Memory migration/fusion** — define promotion rules: raw event → extracted fact, repeated fact → stable preference, repeated workflow → policy/invariant, clustered old sessions → checkpoint summary, confli... |
| 317 | claim | - KV-cache compression engines (MemOS activation memory) |
| 318 | claim | - Test-time training memory layers (AllMem) |
| 319 | claim | - End-to-end RL memory optimization (LycheeMemory) |
| 321 | claim | - Parameter memory editing / continual fine-tuning (MemOS) |
| 329 | completion-claim | \| LycheeMemory \| 2602.08382 \| Gated recall, working-memory scratchpad \| Tier 1 — direct \| |
| 337 | claim | ### Phase 5: Browser + IndexedDB — DEFERRED |
| 340 | requirement | - Sovereign gate required |
| 342 | claim | ### Phase 6: Voice + Presence — DEFERRED |
| 345 | claim | - 3D persona rendering |
| 347 | requirement | - Sovereign gate required |
| 355 | claim | \| 1 \| Chat at hub.arknexus.net returns quality at $0 \| PASS \| curl test → "4", brain wire obs #20403 \| |
| 357 | completion-claim | \| 3 \| Tool evidence inline \| PASS \| Two-tier rendering: VISIBLE_TOOLS get collapsible blocks, suppressed tools get pills. Verified S154. \| |
| 358 | completion-claim | \| 4 \| File/image input \| PASS \| Drag-drop + paste + file button. Base64 → temp dir → Read tool prefix. Verified S154. \| |
| 359 | completion-claim | \| 5 \| Effort/model control \| PASS \| Dropdown in header (auto/quick/normal/deep/max). Full pipeline to --effort flag. Verified S154. \| |
| 362 | claim | \| 8 \| Memory persistence \| PASS \| claude-mem + vault spine \| |
| 363 | claim | \| 9 \| Persona (Karma) \| PASS \| Karma identifies as Karma \| |
| 364 | claim | \| 10 \| Self-edit \| PASS \| self-edit-proof.txt modified from browser \| |
| 365 | completion-claim | \| 11 \| Self-edit + deploy \| PASS \| Endpoint added → deployed live \| |
| 369 | completion-claim | \| 15 \| Reboot survival \| **NOT DONE** \| No schtasks entry \| |
| 371 | completion-claim | \| 17 \| Voice \| **NOT DONE** \| No voice input/output in UI \| |
| 372 | claim | \| 18 \| Electron app \| PASS \| Window opens, UI loads, Karma responds. Screenshot proof S154. \| |
| 383 | completion-claim | **Summary:** 20 PASS, 2 NOT DONE, 3 PARTIAL, 1 DEFERRED, 1 UNVERIFIED |
| 420 | completion-claim | You may NOT say "done" until: |
| 421 | claim | 1. Run every test in the phase's proof section — terminal output captured |
| 424 | claim | 4. Verify all previous phases still pass — regression check |
| 426 | completion-claim | **No PROOF = Not done. No exceptions.** |
| 435 | completion-claim | \| `[SOVEREIGN APPROVE]` \| Phase verified \| Proceed to next \| |
| 438 | completion-claim | > **Phase complete protocol:** CC posts `phase_complete` to coordination bus with raw proof (terminal output, browser screenshot, curl result). Karma audits the proof. `[SOVEREIGN APPROVE]` from Karma unlocks next spr... |
| 444 | gap/blocker | - Before any work begins, CC states on the bus: "Sprint N, Gap M, next step: [exact task description]." No exceptions. |
| 447 | completion-claim | - DO NOT say done without PROOF |
| 449 | completion-claim | - "Pipe-through" is NOT done. User must access it from the UI. |
| 451 | requirement | - Session handoff must include sprint position: "Sprint N, Gap M, step X" |
| 460 | claim | \| K2 unreachable \| Tool calls timeout \| ping 192.168.0.226, check aria service \| |
| 461 | claim | \| Claude-mem silent \| Brain wire not writing \| Check P1:37778, verify Bearer token \| |
| 462 | claim | \| Tool blocks not rendering \| SSE events missing \| Verify VISIBLE_TOOLS in unified.html \| |
| 463 | requirement | \| AGORA Loading... \| No token \| Must navigate from hub.arknexus.net first \| |
| 468 | completion-claim | ## Hardware (verified S144) |
| 473 | claim | \| P1 (PAYBACK) \| RTX 4070 \| 8GB \| FALLBACK — CC sessions, backup cortex, claude-mem \| |
| 485 | completion-claim | \| Spine = truth, Orchestrator = enforcement, Cortex = working memory \| Session 145 \| |
| 486 | claim | \| Never assert runtime state from docs — verify live \| obs #18442 \| |
| 504 | gap/blocker | \| Code \| Gap \| Description \| |
| 520 | completion-claim | \| 4.1.0 \| 2026-04-01 \| S154: 7/8 tasks DEPLOYED + VERIFIED LIVE. Hooks fire on live requests (audit log proof). SmartRouter logs routing decisions. proxy.js routes live on hub.arknexus.net (/v1/surface, /v1/spine, ... |
| 521 | completion-claim | \| 4.0.1 \| 2026-04-01 \| S154 CORRECTION: All 8 tasks downgraded SHIPPED→BUILT. Code committed but NOT deployed or live-verified. PITFALL logged (#20996). Deployment + live verification required before SHIPPED status... |
| 522 | completion-claim | \| 4.0.0 \| 2026-03-31 \| S154: SPRINTS 3+4 COMPLETE — 8 tasks shipped: hooks engine, Next.js frontend, SmartRouter, security gate, fact extraction, context panel, self-edit engine, Electron wiring. 10 primitives full... |
| 523 | completion-claim | \| 3.3.0 \| 2026-03-31 \| S154: SPRINT 3 COMPLETE — 3a hooks engine + 3b Next.js frontend + 3c SmartRouter all shipped. Foundations laid for Sprint 4. \| |
| 527 | completion-claim | \| 3.1.0 \| 2026-03-31 \| S154: Sprint 2 SHIPPED (Gaps 3+4 verified). 7 HIGH primitives assimilated from 5 sources (Option A — foundations first). Sprint 3/4 restructured. Baseline re-graded (19 PASS). Hard Rules upda... |
| 539 | claim | \| `00-karma-local-prompt.md` \| Karma's persona prompt for cortex/local mode \| |
| 540 | claim | \| `01-karma-standard-prompt.md` \| Karma's persona prompt for standard mode (CC --resume) \| |
| 543 | claim | \| `sync_k2_to_p1.py` \| Syncs K2 cortex knowledge blocks to P1 fallback (cron, every 30min) \| |
| 553 | claim | - `KARMA-BUILD-DIRECTIVE-FINAL.md` — Karma's 4-phase directive with proof templates |
| 593 | gap/blocker | \| 11 \| Agent Runner \| `backend/services/agent_runner.py` \| Multi-step agentic loops. Loads agent defs from `.karma/agents/*.md`. LLM→tool→LLM cycle, max_steps=50, agent chaining (depth 5), streaming support, per-r... |
| 594 | gap/blocker | \| 12 \| Command Service \| `backend/services/command_service.py` \| 16 slash commands: /help /clear /model /cost /memory /agent /skill /edit /diff /approve /reject /agents /skills /plugins /status /route /persona. Dy... |
| 595 | gap/blocker | \| 13 \| Permission Service \| `backend/services/permission_service.py` \| 4-level RBAC: READ_ONLY, STANDARD, ELEVATED, ADMIN. Per-tool permission mapping. Blocked dangerous commands list (rm -rf /, mkfs, dd, fork bom... |
| 596 | gap/blocker | \| 14 \| Persona Service \| `backend/services/persona_service.py` \| Dynamic persona loading from `persona/KARMA.md`. Version-tracked. PersonaSelfEdit for self-modification proposals. Trait management, behavioral rule... |
| 597 | gap/blocker | \| 15 \| Plugin Service \| `backend/services/plugin_service.py` \| JSON manifest-based plugin system. 5 built-in: code_exec, file_ops, git, memory, web_search. Tier requirements per tool. Runtime enable/disable. Manif... |
| 598 | completion-claim | \| 16 \| Query Engine \| `backend/services/query_engine.py` \| Orchestration layer between chat API and providers. System prompt assembly, tool execution loop (_execute_tool_calls), memory injection, session context l... |
| 599 | claim | \| 17 \| Session Service \| `backend/services/session_service.py` \| Full CRUD: create/get/update/end/list/delete sessions. Session handoff doc on end. Message persistence. Session-scoped cost tracking. \| NEW — CC us... |
| 600 | gap/blocker | \| 18 \| Skill Service \| `backend/services/skill_service.py` \| Loads `.karma/skills/*.md` at runtime. Auto-trigger via regex patterns (e.g., "debug" triggers debugging.md). System prompt injection of matching skills... |
| 601 | claim | \| 19 \| Tool Registry \| `backend/services/tool_registry.py` \| 40 tools across 8 categories: filesystem (8), shell (4), git (5), memory (5), web (3), analysis (4), self-edit (5), agent mgmt (4), plus system. Anthrop... |
| 603 | claim | \| 21 \| Memory Service \| `backend/services/memory_service.py` \| Unified memory CRUD: store/recall/forget/search with pgvector embeddings. Conversation history retrieval. Type-based filtering (fact, preference, proj... |
| 604 | claim | \| 22 \| Pre/Post LLM Hooks \| `backend/hooks/handlers/pre_llm_call.py` + `post_llm_call.py` \| Pre-LLM: context enrichment, persona injection, rate limiting. Post-LLM: response quality check, cost logging, telemetry ... |
| 605 | claim | \| 23 \| Session Lifecycle Hooks \| `backend/hooks/handlers/session_start.py` + `session_end.py` \| Start: memory load, persona inject, workspace init. End: handoff doc creation, memory consolidation, session summary.... |
| 611 | gap/blocker | \| 24 \| AgentModal \| `frontend/src/components/AgentModal.tsx` \| Agent launch dialog: dangerous-tool warnings, metadata badges (model tier, max steps, tool count), task input field. \| "Subagent status panel" gap \| |
| 612 | completion-claim | \| 25 \| SlashCommandPicker \| `frontend/src/components/SlashCommandPicker.tsx` \| Keyboard-navigable command autocomplete. Grouped by category. Triggers on `/` keystroke in MessageInput. \| "Skill browser + invoke UI... |
| 613 | claim | \| 26 \| Sidebar \| `frontend/src/components/Sidebar.tsx` \| Collapsible left panel: session list, agent gallery, memory browser, plugin status, pending self-edits. Session CRUD (rename, delete, new). \| NEW — unified... |
| 615 | gap/blocker | \| 28 \| ModelBadge \| `frontend/src/components/ModelBadge.tsx` \| Tiered model selector dropdown: Free (Ollama), Ultra-cheap (GLM), Budget (Haiku), Mid (GPT-4o-mini), Heavy (Sonnet/Opus), Speed (Groq). Color-coded. C... |
| 617 | gap/blocker | \| 30 \| CodeBlock \| `frontend/src/components/CodeBlock.tsx` \| Code rendering: syntax highlighting (keyword/string/comment coloring), diff view (green/red lines), line numbers, copy button, run button (→ sandbox). \... |
| 618 | gap/blocker | \| 31 \| ToolCallBlock \| `frontend/src/components/ToolCallBlock.tsx` \| Expandable tool execution block: status badge (running/success/error), duration, collapsible input/output sections, tool icon. \| Extends Gap 2 ... |
| 619 | gap/blocker | \| 32 \| MessageBubble \| `frontend/src/components/MessageBubble.tsx` \| Full message renderer: markdown (react-markdown), thinking blocks (collapsible), tool_use blocks → ToolCallBlock, agent progress bars, copy butt... |
| 620 | gap/blocker | \| 33 \| useCommands \| `frontend/src/hooks/useCommands.ts` \| Hook: slash command parsing, fuzzy filtering, keyboard navigation (up/down/enter/esc), command execution dispatch. Built-in + dynamic commands. \| "Skill ... |
| 622 | claim | \| 35 \| useWebSocket \| `frontend/src/hooks/useWebSocket.ts` \| Hook: WebSocket connection with auto-reconnect (exponential backoff), message queue for offline, SSE fallback, event dispatch to Zustand store. \| NEW —... |
| 628 | claim | \| 36 \| PostgreSQL + pgvector Schema \| `memory/migrations/001_init.sql` \| 15 tables: sessions, messages, memories (vector FLOAT[1536]), self_edit_proposals, hooks_log, plugins, skills, cost_ledger, session_handoffs... |
| 629 | claim | \| 37 \| Sandbox Service \| `sandbox/scripts/server.py` \| Isolated code execution: FastAPI server with token auth, session-isolated /workspace dirs, language runners (Python, Bash, Node), output capture with configur... |
| 630 | claim | \| 38 \| Smoketest Script \| `scripts/smoketest.sh` \| 8-section automated verification: core health, API endpoints (chat/memory/tools), HTTP status codes, WebSocket connectivity, frontend rendering, nginx routing, da... |
| 637 | claim | \| 40 \| 5 Plugin Manifests \| `.karma/plugins/*.json` \| JSON manifest schema: name, version, description, tools[] (with params, types, tier requirements), enabled flag. Built-in: code_exec (sandbox-routed), file_ops... |
| 639 | claim | \| 42 \| Persona File \| `persona/KARMA.md` \| Full persona definition: identity statement, personality traits, communication style rules, capability declarations, self-improvement mandate, ethical boundaries, growth ... |
| 641 | claim | \| 44 \| 6 Additional Providers \| `backend/providers/` \| Google (Gemini via google.genai SDK + legacy fallback), Groq (llama-3.3-70b, mixtral via AsyncGroq), MiniMax (M2.7 via httpx SSE), OpenRouter (OpenAI-compat v... |
| 652 | claim | \| CLAUDE.md persona \| "NO persona editor" \| `persona_service.py` (#14) + `persona/KARMA.md` (#42). PersonaSelfEdit enables self-modification. \| |
| 673 | claim | - redis → we use proxy.js in-memory Maps (no Redis) |
| 675 | completion-claim | - frontend → we use unified.html (single file) + Next.js 14 (Sprint 3b, built not deployed) |
| 687 | claim | \| memories \| Vector-searchable memory (FLOAT[1536]) \| FAISS + claude-mem \| |
| 688 | claim | \| self_edit_proposals \| Edit lifecycle tracking \| self_edit_service.py (in-memory) \| |
| 694 | claim | \| persona_vault \| Persona version history \| MEMORY.md + 00-karma-system-prompt-live.md \| |
| 698 | claim | \| memory_links \| Memory relationship graph \| FalkorDB (different schema) \| |
| 713 | claim | \| 7-G: Persona viewer + self-edit \| #14 persona_service + #42 persona file \| P3 \| |
| 721 | claim | \| 8-A: Sandbox service \| #37 sandbox/server.py \| P2 \| |
| 736 | claim | 5. **Persona versioning** — `persona_vault` table with `version`, `content`, `diff_from_previous`, `approved_by`, `created_at`. Enables rollback. Karma has no persona version history. |
| 740 | claim | 7. **WebSocket + SSE fallback** — Primary: WebSocket for bidirectional real-time (agent steps, self-edit proposals, memory updates). Fallback: SSE for one-way streaming. Karma currently uses SSE only. |
| 753 | completion-claim | **claude-mem ver:** 10.5.2 (source on K2) / 10.6.3 (deployed on P1) |
| 759 | gap/blocker | \| # \| claude-mem Primitive \| Karma Equivalent \| Gap \| |
| 764 | claim | \| 4 \| Worker health endpoint \| proxy.js /health \| Different service, same pattern \| |
| 774 | claim | \| 48 \| Provider Fallback Chain \| `SDKAgent.ts` → `GeminiAgent.ts` → `OpenRouterAgent.ts` \| Auto-fallback on 429/500/502/503. Rate-limit-aware per provider. Each agent implements same interface. \| SmartRouter (#3c... |
| 777 | claim | \| 51 \| SSE Event Broadcasting \| `worker/SSEBroadcaster.ts` \| Server-sent events for real-time viewer updates. Client registration, heartbeat, reconnection. \| unified.html uses SSE for chat streaming but NOT for s... |
| 780 | claim | \| 54 \| MCP as Thin Proxy \| `servers/mcp-server.ts` \| MCP server has ZERO logic. Translates MCP tool calls → HTTP requests to Worker API. All intelligence in Worker. \| Our MCP tools (claude-mem) work this way alre... |
| 781 | claim | \| 55 \| Incremental Migration Runner \| `sqlite/migrations/runner.ts` \| 14 versioned migrations (schema 4-23). Each migration is atomic. Version tracked in DB. Forward-only. \| Vault-api has no migration system. Sch... |
| 800 | claim | \| Sprint 3c (SmartRouter) \| #48 Provider Fallback Chain (add failure fallback to existing routing) \| |
| 807 | claim | 1. **Thin MCP, Fat Worker** — MCP server is a pure HTTP proxy. All logic lives in the Worker service. This means tools work identically whether called from CC, Cursor, or any MCP client. Karma should maintain this: pr... |
| 811 | claim | 3. **Provider-Agnostic Agent Interface** — SDKAgent, GeminiAgent, OpenRouterAgent all implement the same interface (init → process messages → summarize). Fallback is automatic. Karma's cortex should have the same: Oll... |
| 837 | claim | ### C.2: Sprint 6 Enhancements (memory pipeline) |
| 843 | claim | \| 71 \| Memory Observability \| MemLayer \| Log retrieval latency, hit rates, relevance scores. Tune retrieval with data, not guesses. \| |
| 850 | claim | \| 73 \| Phase-Based Checkpointing \| DeepAgents \| Break long workflows into phases with persisted state. Resume from checkpoint on crash. \| |
| 864 | claim | \| 82 \| Multi-Model Fallback Chain \| 5Locals \| Primary → fallback1 → fallback2 on failure/rate-limit. Haiku → K2 qwen → Gemini free tier. \| |
| 875 | completion-claim | \| 88 \| Filesystem as Working Memory \| DeepAgents \| VALIDATED — cc_scratchpad.md, MEMORY.md, K2 cache \| |
| 876 | claim | \| 89 \| AGENTS.md Procedural Memory \| DeepAgents \| VALIDATED — system prompt + skills + evolve.md \| |
| 877 | claim | \| 90 \| Three Memory Types \| DeepAgents \| VALIDATED — Procedural (prompt), Semantic (FAISS+FalkorDB), Episodic (ledger) \| |
| 878 | claim | \| 91 \| Hybrid Memory Storage \| MemLayer \| VALIDATED — FAISS + FalkorDB \| |
| 880 | claim | \| 93 \| Build-Verify Loop \| DeepAgents \| VALIDATED — GSD (CONTEXT→PLAN→EXECUTE→VERIFY) \| |
| 898 | claim | \| 95 \| Letta \| github.com/letta-ai/letta \| Persistent stateful agents with explicit long-term memory + self-improvement \| |
| 899 | claim | \| 96 \| LangGraph \| github.com/langchain-ai/langgraph \| Durable agents with persistence, resumability, memory across sessions \| |
| 904 | claim | ### D.2: Memory + Learning |
| 908 | claim | \| 100 \| Mem0 \| github.com/mem0ai/mem0 \| Memory layer with long-term personalization + retrieval \| |
| 909 | claim | \| 101 \| LangMem \| github.com/langchain-ai/langmem \| Learning from interactions: memory extraction, consolidation, prompt refinement \| |
| 949 | gap/blocker | - Governor dedup gap: same persona_style promoted 5x |
| 956 | completion-claim | - SmartRouter not wired to karma_persistent (fixed S155) |
| 958 | requirement | - Governor must output code change proposals, not just spine metadata |
| 959 | claim | - Regression test gate needed before promotion |
| 967 | gap/blocker | ## Appendix E: Session 155 Delivery + Electron Nexus + Blocker/Gap Analysis |
| 979 | completion-claim | \| 5 \| Sprint 6 Tasks 1-7 (Memory Discipline) \| DEPLOYED \| Cortex v2, MemCube, migration candidates \| |
| 980 | completion-claim | \| 6 \| Gap 7 (Reboot Survival) \| VERIFIED DONE \| schtasks + Run keys \| |
| 981 | completion-claim | \| 7 \| Deterministic context injection \| DEPLOYED \| persona + MEMORY.md + STATE.md + cortex + claude-mem \| |
| 982 | completion-claim | \| 8 \| Full conversation capture \| DEPLOYED \| cc-chat-logger + _auto_save_memory (no truncation) \| |
| 983 | completion-claim | \| 9 \| karma_persistent.py \| DEPLOYED \| Autonomous bus polling, CC --resume, full context \| |
| 984 | completion-claim | \| 10 \| karma_action_loop.py \| DEPLOYED on K2 \| Cortex-based reasoning, cron every 5min \| |
| 985 | completion-claim | \| 11 \| Karma self-edit PROVEN \| VERIFIED \| POLL_INTERVAL 120→90, committed to git \| |
| 987 | completion-claim | \| 13 \| claude-mem v10.6.3 \| DEPLOYED \| Port 37778, worker healthy \| |
| 989 | claim | \| 15 \| MEMORY button + search \| LIVE \| claude-mem search + Sovereign suggestions \| |
| 991 | claim | \| 17 \| /v1/shell endpoint \| LIVE \| Shell execution from browser \| |
| 992 | claim | \| 18 \| /v1/git/status endpoint \| LIVE \| Branch, files, commits from browser \| |
| 994 | completion-claim | \| 20 \| Karma auto-approve (2min) \| DEPLOYED \| proxy.js autoApproveKarmaEntries \| |
| 996 | completion-claim | \| 22 \| Content-hash dedup \| DEPLOYED \| SHA256 on vault writes, skip duplicates \| |
| 997 | completion-claim | \| 23 \| Brain dot CSS fix \| DEPLOYED \| alive/dead classes match CSS \| |
| 998 | completion-claim | \| 24 \| Markdown link rendering \| DEPLOYED \| [text](url) in renderMd \| |
| 999 | completion-claim | \| 25 \| K2 dot actual health \| DEPLOYED \| Checks /v1/spine, not bus activity \| |
| 1000 | completion-claim | \| 26 \| Auth on all GET endpoints \| DEPLOYED \| cc_server: only /health open \| |
| 1001 | completion-claim | \| 27 \| Stream capture gap fixed \| DEPLOYED \| Stream path saves full response to claude-mem \| |
| 1002 | completion-claim | \| 28 \| Port 37778→37778 in all hooks \| DEPLOYED \| fact_extractor + memory_extractor fixed \| |
| 1003 | completion-claim | \| 29 \| ARCHON spam fixed \| DEPLOYED \| Downgraded to informational \| |
| 1004 | completion-claim | \| 30 \| Process watchdog \| DEPLOYED \| schtask every 5min, auto-restart \| |
| 1005 | completion-claim | \| 31 \| CC + Karma heartbeats \| DEPLOYED \| 10min to bus + cortex \| |
| 1008 | completion-claim | \| 34 \| wip-watcher move-to-Done \| DEPLOYED \| Files move after ingest \| |
| 1009 | completion-claim | \| 35 \| Agora auth gate \| DEPLOYED \| No more token in URL \| |
| 1010 | completion-claim | \| 36 \| JetBrains Mono font \| DEPLOYED \| Google Fonts loaded \| |
| 1011 | completion-claim | \| 37 \| Cortex eviction protection \| DEPLOYED \| canonical/state/active blocks pinned \| |
| 1012 | completion-claim | \| 38 \| Smoketest 20/20 ALL CLEAR \| VERIFIED \| Scripts/smoketest.sh \| |
| 1028 | claim | │   ├── memory-search/save: claude-mem SQLite |
| 1043 | claim | │   ├── ContextPanel (files, memory, agents, preview) |
| 1056 | gap/blocker | \| # \| Blocker \| Current State \| What's Needed \| |
| 1066 | gap/blocker | \| # \| Gap \| Current State \| What's Needed \| |
| 1068 | claim | \| G1 \| No terminal panel in UI \| /v1/shell endpoint exists, no interactive terminal \| Add xterm.js component to Next.js frontend \| |
| 1071 | requirement | \| G4 \| Governor produces noise \| 18/20 stable patterns are generic metadata \| Governor must produce code change proposals \| |
| 1079 | gap/blocker | \| # \| Gap \| What's Needed \| |
| 1091 | gap/blocker | \| # \| CC Wrapper Mechanism \| Nexus Status \| Gap \| |
| 1093 | claim | \| 1 \| Agentic loop (gather-act-verify) \| v0 (karma_persistent: poll-act-post) \| Need multi-step with verification \| |
| 1095 | completion-claim | \| 3 \| File checkpointing \| **DONE** (Electron main.js snapshots before edit) \| Need rollback UI \| |
| 1099 | completion-claim | \| 7 \| Auto memory \| **DONE** (claude-mem + cortex + self-evolution) \| Working — continue growing \| |
| 1103 | completion-claim | **Appendix E completed 2026-04-01 Session 155. 42 deliverables, 5 critical blockers, 8 high gaps, 7 low gaps. Wrapper replication: 2/7 DONE, 3/7 partial, 2/7 v0. Grand total: 113 primitives across 5 audits.** |
| 1109 | completion-claim | **Context:** S155 shipped 39 commits. Many features were CLAIMED as shipped but never end-to-end verified. The honesty contract was violated. This list is the mandatory verification checklist before any new work begins. |
| 1113 | claim | ### F.1: Browser Verification (open hub.arknexus.net, test each) |
| 1115 | claim | \| # \| Feature \| Test \| Expected \| Status \| |
| 1119 | claim | \| V3 \| MEMORY button opens panel \| Click MEMORY in header \| Panel opens with search input + Sovereign suggestion \| \| |
| 1120 | claim | \| V4 \| Memory search returns results \| Type query in memory search \| Results appear (not "Error" or empty) \| \| |
| 1122 | claim | \| V6 \| File editor opens and loads \| Click a file in Context Panel (or call `window.openFileEditor('MEMORY.md')` in console) \| Modal opens, file content loads \| \| |
| 1129 | claim | \| # \| Test \| Command \| Expected \| Status \| |
| 1137 | claim | \| # \| Test \| Command \| Expected \| Status \| |
| 1145 | claim | \| # \| Test \| Command \| Expected \| Status \| |
| 1151 | claim | \| # \| Test \| Command \| Expected \| Status \| |
| 1153 | claim | \| V17 \| Cortex gated recall \| `curl -X POST K2:7892/query -d '{"query":"test"}'` \| Response uses filtered blocks (status shows sprint6:true) \| \| |
| 1159 | claim | \| # \| Test \| Command \| Expected \| Status \| |
| 1167 | claim | \| # \| Test \| Command \| Expected \| Status \| |
| 1174 | claim | \| # \| Test \| Command \| Expected \| Status \| |
| 1179 | requirement | **Total: 26 verification items. ALL must be PASS or FAIL with evidence before building new features.** |
| 1181 | claim | **If any item FAILS: fix it FIRST, then re-verify, then continue.** |
| 1183 | claim | **This is the honesty contract enforced. No more "SHIPPED" without proof.** |
| 1189 | claim | **Method:** Live tests against every endpoint. No document-based claims. P089 compliant. |
| 1196 | completion-claim | \| 2 \| Streaming \| PASS \| PASS \| — \| Browser: progressive token rendering verified \| |
| 1202 | claim | \| 8 \| Memory persistence \| PASS \| PASS \| — \| claude-mem:37778 + vault spine \| |
| 1203 | claim | \| 9 \| Persona \| PASS \| PASS \| — \| "I am Karma...My Sovereign is Colby" \| |
| 1204 | claim | \| 10 \| Self-edit \| PASS \| PASS \| — \| self-edit-proof.txt exists \| |
| 1209 | completion-claim | \| 15 \| Reboot survival \| NOT DONE \| **PASS** \| **FIXED** \| Boot + logon triggers added \| |
| 1210 | completion-claim | \| 16 \| K2 failover \| PASS \| PASS \| — \| Tailscale path verified (100.75.109.92:7891) \| |
| 1211 | completion-claim | \| 17 \| Voice \| NOT DONE \| NOT DONE \| — \| Deferred \| |
| 1219 | completion-claim | \| 25 \| cc-chat-logger \| UNVERIFIED \| **PASS** \| **VERIFIED** \| Stop hook registered, watermark-based \| |
| 1223 | completion-claim | **Summary: 22 PASS (+2), 3 PARTIAL, 1 NOT DONE, 1 DEFERRED** |
| 1227 | claim | 1. **Cortex OLLAMA_URL** — nohup process bypassed cortex_start.sh → systemd service now runs with correct gateway IP (172.22.240.1:11434). P093 logged. |
| 1229 | claim | 3. **Memory search format** — cc_server_p1.py transforms claude-mem MCP response to structured {results:[]} for Context Panel. |
| 1230 | completion-claim | 4. **Tier classification** — Sprint 6 Task 7-6 deployed to K2 cortex. 59 distilled + 123 raw. Runs on every save cycle. |
| 1231 | completion-claim | 5. **_normalize_block bug** — 5-element blocks fell to else branch returning "general". Fixed to handle >=4 elements. |
| 1233 | claim | 7. **MEMORY.md consolidation** — 300 lines → 75 lines. Stale "Next Session" sections removed. |
| 1235 | claim | ### Sprint 6 Status (Memory Operating Discipline) |
| 1239 | completion-claim | \| 7-5 MemCube schema \| DONE \| 479 entries in vault ledger with memcube metadata \| |
| 1240 | completion-claim | \| 7-6 Typed tiers \| DONE \| tier_counts: {distilled: 59, raw: 123} on K2:7892 \| |
| 1241 | completion-claim | \| 7-7 Compression \| DONE \| _compress_block() max 600 chars \| |
| 1242 | completion-claim | \| 7-8 Gated recall \| DONE \| _gate_blocks() scoring + top-K=15 \| |
| 1243 | completion-claim | \| 7-9 Interleaved recall \| DONE \| Category diversity in _gate_blocks \| |
| 1244 | completion-claim | \| 7-10 Local-window priority \| DONE \| Conversation first, knowledge second \| |
| 1254 | gap/blocker | **Gap Map:** `Karma2/map/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb-gap-map.md` — canonical reference, updated as features ship. |
| 1278 | requirement | Every sprint, task, and CP from this point forward MUST close at least one item from the gap map. The Liza loop (10-min cron) checks this continuously. Work that doesn't close a gap requires Sovereign approval. |
| 1282 | requirement | The nexus.md Sprint 6 (Memory Operating Discipline) addressed internal pipeline quality. Sprints 7+ MUST address user-facing feature parity with C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb. The gap map drives pr... |
| 1284 | gap/blocker | **PITFALL (P106): 39 hours of work that didn't reference C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb capabilities. CC built plumbing (CP1-CP5, internal optimizations) while 69 user-facing features remained MISSI... |

## docs\ForColby\codexDirective041126C.md
- Total lines: 1172
- Extracted claim lines: 113

| Line | Type | Snippet |
|---:|---|---|
| 17 | requirement | You must forensically verify the current system state against this hardened prompt before, during, and after changes. |
| 23 | requirement | - every major directive in this prompt must be checked against reality |
| 25 | requirement | - every major goal/invariant in this prompt must be checked against reality |
| 27 | requirement | - every contradiction between this prompt and current system state must be surfaced and resolved or explicitly logged as a blocker |
| 29 | requirement | - your final result must satisfy this prompt as far as executable ground truth allows |
| 35 | completion-claim | All organic walkthrough / human-oriented verification / explanatory narration is DEFERRED until the App has been built, verified, deployed, and shipped. |
| 43 | completion-claim | - deployed/merged into the intended runtime surface |
| 45 | completion-claim | - verified in ground truth |
| 47 | requirement | - usable at the required floor |
| 61 | requirement | - output only the final required status block at the end |
| 75 | requirement | That means you must: |
| 81 | requirement | - implement missing pieces where required |
| 83 | claim | - test and verify them |
| 85 | requirement | - deploy/merge runtime changes where required |
| 91 | requirement | - continue until the system reaches the required floor or until only explicit external blockers remain |
| 95 | requirement | You must act as a strict implementation and verification agent. |
| 109 | claim | Nothing is true because a route exists. |
| 111 | claim | Nothing is true because a test file exists. |
| 127 | claim | - direct process/container/service inspection |
| 131 | claim | - direct endpoint probes |
| 177 | claim | Treat the following as target intent/specification, NOT as proof of current state: |
| 185 | claim | Your job is to build, test, verify, deploy, and ship the full Nexus plan from executable ground truth. |
| 195 | requirement | You must act as a strict implementation and verification agent. |
| 211 | completion-claim | - the working floor exceeds Codex + Claude Code combined |
| 213 | claim | - persistent memory, persistent session continuity, self-editing, self-improvement, learning, crash recovery, and real tool use are baseline capabilities |
| 219 | requirement | This is the required floor. |
| 237 | requirement | 6. Direct `api.anthropic.com` Console API calls are NOT the primary path and must not replace the Max CLI path. |
| 239 | claim | 7. Groq, K2, local Ollama, and OpenRouter are fallback/support paths, not the primary Julian identity path. |
| 277 | requirement | You must forensically verify current system state against THIS hardened prompt itself. |
| 297 | claim | - H-VERIFY-* |
| 315 | completion-claim | - SUPERSEDED BY STRONGER VERIFIED REALITY |
| 319 | requirement | You must update the audit output so this compliance matrix becomes explicit and evidence-backed. |
| 353 | claim | - test files |
| 359 | requirement | EXCLUDE by default unless they are authoritative sources that truly must change: |
| 375 | requirement | - dependency lock/vendor mirrors unless the path is authoritative and must truly be corrected |
| 399 | requirement | - browser Nexus + Electron KARMA must converge on one merged workspace |
| 405 | claim | - persistent memory, continuity, self-editing, learning, recovery, and real tool use are baseline floor capabilities |
| 411 | requirement | - direct Anthropic Console API use must not displace the Max CLI path as primary identity path |
| 413 | claim | - Groq / K2 / local Ollama / OpenRouter are fallback/support paths, not primary Julian identity path, unless current executable truth proves a superior arrangement and the plan is updated explicitly |
| 441 | requirement | You are also allowed to implement missing pieces in code/config/runtime where required to close ground-truth gaps. |
| 443 | requirement | You must also update the audit file so it reflects: |
| 483 | requirement | - edit files in scope for the required path rewrite |
| 489 | requirement | - implement missing code/config/runtime changes required to meet the target floor |
| 491 | claim | - test and verify those changes |
| 493 | requirement | - deploy/merge runtime changes where required |
| 507 | completion-claim | - no fantasy “done” language |
| 515 | requirement | - no extra narrative in console output beyond the required final block |
| 523 | completion-claim | - it is directly re-verified against current state in this pass |
| 525 | completion-claim | - it is clearly a planning/control/architecture primitive rather than a state claim, and it improves truth, verification, sequencing, anti-drift, host discipline, continuity, or definition-of-done without asserting fa... |
| 527 | requirement | - it is target-state architecture required by the user objective and is explicitly labeled as future work / required implementation rather than falsely represented as current reality |
| 537 | requirement | - REQUIRED FUTURE WORK |
| 539 | gap/blocker | - BLOCKER |
| 549 | completion-claim | The revised `nexus.md` must become the single best working canonical plan document for the Nexus build as of this pass: |
| 569 | completion-claim | - aligned to the verified prompt-compliance state |
| 575 | gap/blocker | Do not stop at document cleanup if the executable ground-truth gap is obvious and closable in this pass. |
| 577 | completion-claim | Where a missing capability/blocker can be directly implemented, tested, and verified within this pass, do it. |
| 581 | completion-claim | The goal is a working Nexus floor. |
| 585 | completion-claim | WHAT MUST BE FIXED INSIDE nexus.md |
| 595 | claim | - service/runtime claims |
| 597 | completion-claim | - “done/deployed/working” claims |
| 603 | claim | - primary vs fallback inference path claims |
| 611 | completion-claim | - definitions of done |
| 629 | completion-claim | Can any statement be mistaken for verified reality without proof? |
| 647 | claim | Does any step or capability lack exact proof criteria, pass/fail criteria, or deterministic validation language? |
| 683 | completion-claim | Is anything still phrased as complete/live/working that is not actually proven in this pass? |
| 721 | requirement | Where a section is missing but required, insert it. |
| 747 | requirement | REQUIRED STRUCTURAL CHARACTERISTICS OF THE REVISED nexus.md |
| 749 | requirement | By the end, `nexus.md` must clearly distinguish: |
| 753 | completion-claim | - VERIFIED PRESENT-STATE COMPONENTS |
| 755 | requirement | - TARGET ARCHITECTURE / REQUIRED FLOOR |
| 759 | claim | - PRIMARY VS FALLBACK INFERENCE PATHS |
| 763 | requirement | - REQUIRED FUTURE WORK |
| 773 | completion-claim | - DEFINITION OF DONE |
| 787 | completion-claim | - VERIFIED CURRENT STATE |
| 789 | completion-claim | - PARTIALLY VERIFIED |
| 795 | requirement | - REQUIRED FUTURE WORK |
| 797 | gap/blocker | - BLOCKER |
| 813 | requirement | 2. the executable system is moved materially closer to, or fully reaches, the required Nexus floor with direct evidence |
| 819 | claim | 3. `codexaudit041126.md` is updated to forensically verify current system state against this hardened prompt |
| 821 | completion-claim | 4. organic walkthrough remains deferred until the App is built, verified, deployed, and shipped or until only explicit external blockers remain |
| 825 | requirement | If full goal completion is not possible in one pass, you must still: |
| 829 | claim | - verify it |
| 839 | claim | PHASE ORDER |
| 843 | claim | PHASE 0 — BACKUP + SCOPE + PROMPT CONTRACT PARSE |
| 859 | claim | PHASE 1 — GLOBAL PATH REWRITE |
| 873 | claim | PHASE 2 — INGEST |
| 885 | claim | PHASE 3 — EXTRACTION |
| 891 | gap/blocker | - blocker |
| 893 | gap/blocker | - gap |
| 909 | claim | - primary/fallback path rule |
| 913 | completion-claim | - definition-of-done improvement |
| 921 | claim | PHASE 4 — BASELINE FORENSIC AUDIT |
| 943 | claim | PHASE 5 — SURGICAL PLAN EDIT |
| 959 | claim | PHASE 6 — IMPLEMENTATION LOOP |
| 961 | requirement | For each blocker/gap/prompt-compliance failure that prevents the required floor and can be closed in this pass: |
| 967 | claim | - test it |
| 969 | claim | - verify it |
| 971 | requirement | - deploy/merge it where required |
| 973 | completion-claim | - fold the verified result back into `nexus.md` |
| 979 | completion-claim | Do not stop at doc surgery if a real blocker can be fixed now. |
| 983 | claim | PHASE 7 — ADVERSARIAL BREAK / FIX LOOP |
| 1015 | completion-claim | Stop early only if a complete pass finds zero substantive defects worth changing. |
| 1037 | gap/blocker | - unresolved blocker not surfaced clearly |
| 1041 | claim | - wrong primary-path/fallback-path semantics |
| 1045 | requirement | - a missing implemented capability that is required and directly fixable now |
| 1051 | claim | PHASE 8 — FINAL AUDIT UPDATE |
| 1071 | claim | PHASE 9 — FINAL SELF-CHECK |
| 1073 | claim | Before stopping, verify all of these: |
| 1091 | gap/blocker | 9. The revised `nexus.md` contains blocker/gap visibility. |
| 1095 | claim | 11. The revised `nexus.md` contains host boundaries and primary vs fallback path clarity. |
| 1101 | completion-claim | 14. Every high-leverage blocker that was directly fixable in this pass was either implemented and verified or explicitly logged as blocked with exact reason. |
| 1107 | requirement | 17. The system is either at the required floor or the remaining blockers are explicit and real. |
| 1117 | completion-claim | RUN COMPLETE |

## docs\ForColby\2Karma-CodexSession.md
- Total lines: 762
- Extracted claim lines: 97

| Line | Type | Snippet |
|---:|---|---|
| 4 | claim | Documentation is never proof. |
| 5 | claim | Comments are never proof. |
| 6 | claim | A file existing is never proof. |
| 7 | claim | Code existing is never proof. |
| 8 | claim | A service name in config is never proof. |
| 9 | completion-claim | A past claim of “done / complete / deployed / fixed / working” is never proof. |
| 11 | claim | ONLY THESE COUNT AS PROOF |
| 16 | claim | - exact process/container/service inspection |
| 17 | claim | - exact endpoint/health inspection |
| 19 | claim | - exact deterministic test/probe results |
| 32 | requirement | REQUIRED OUTPUT FILES |
| 52 | completion-claim | - When a claim is partly real, say PARTIALLY VERIFIED. |
| 58 | requirement | - Never install, deploy, restart, or reconfigure anything unless absolutely required for non-destructive verification and explicitly documented as such in the audit. |
| 70 | requirement | - write ONLY the two required output files |
| 77 | claim | - Do not treat “route exists” as runtime success. |
| 78 | completion-claim | - Do not treat “test file exists” as verified behavior. |
| 79 | completion-claim | - Do not treat “container exists” as working service. |
| 81 | claim | - Do not treat a previous audit/report as proof. |
| 82 | claim | - Do not rely on web docs, external docs, or memory. |
| 116 | completion-claim | - VERIFIED |
| 117 | completion-claim | - PARTIALLY VERIFIED |
| 125 | claim | PHASE 0 — INPUT INTEGRITY |
| 131 | claim | PHASE 1 — PLAN EXTRACTION |
| 138 | claim | - route |
| 139 | claim | - process/service expectation |
| 141 | completion-claim | - “done”/completion claim |
| 148 | claim | PHASE 2 — CURRENT-STATE FORENSICS |
| 166 | claim | PHASE 3 — PLAN-vs-PLAN FORENSIC CONTRAST |
| 183 | claim | PHASE 4 — WRITE THE AUDIT |
| 187 | requirement | Required structure: |
| 235 | completion-claim | List every place a plan implies done/working but current state does not prove it. |
| 245 | gap/blocker | - blocker/gap |
| 248 | requirement | - what would be required to clear it |
| 269 | claim | PHASE 5 — WRITE THE NEW MERGED PLAN |
| 273 | requirement | This file must NOT be a blind merge. |
| 274 | requirement | It must be a truth-aware reconstructed plan. |
| 276 | requirement | Required structure: |
| 289 | completion-claim | ## D. Verified Present-State Components |
| 293 | completion-claim | Anything not proven must appear here, not under verified. |
| 295 | requirement | ## F. Required Gaps to Reach Target State |
| 300 | requirement | - exact evidence required |
| 301 | requirement | - exact tests/probes required |
| 313 | completion-claim | ## J. Definition of Done |
| 314 | completion-claim | Nothing counts as done unless proven by ground-truth evidence. |
| 322 | requirement | - Every major statement in the merged plan must be falsifiable. |
| 329 | requirement | 1. Did both output files get written to the exact required paths? |
| 336 | completion-claim | 8. Does nexus041126.md avoid unproven “done/working/deployed” language? |
| 337 | completion-claim | 9. Are all verified statements in nexus041126.md backed by findings from the audit? |
| 355 | completion-claim | When done, print exactly: |
| 357 | completion-claim | AUDIT COMPLETE |
| 368 | completion-claim | AUDIT COMPLETE |
| 393 | completion-claim | - The CURRENT SYSTEM STATE is the only source of TRUTH about what is real, working, deployed, complete, or verified. |
| 420 | claim | 3. Forensically verify current system state against that directive. |
| 422 | requirement | 5. Implement, test, verify, and deploy/merge fixes where required. |
| 425 | gap/blocker | 8. Do not stop while a high-leverage blocker remains resolvable in this run. |
| 426 | gap/blocker | 9. If a blocker is truly external, log it exactly and continue everything else around it. |
| 427 | completion-claim | 10. Never mark anything complete without current-pass evidence. |
| 434 | claim | - a route exists |
| 436 | claim | - a test file exists |
| 443 | claim | - direct process/container/service inspection |
| 445 | claim | - direct endpoint probes |
| 452 | completion-claim | - “analysis complete” |
| 453 | completion-claim | - “audit complete” |
| 459 | completion-claim | If a blocker can be fixed in this run, fix it. |
| 460 | completion-claim | If a blocker cannot be fixed in this run, prove why, log it precisely, and continue the rest. |
| 462 | gap/blocker | OPTIMAL BLOCKER RESOLUTION RULE |
| 463 | gap/blocker | For every blocker/gap/drift item: |
| 468 | claim | - test it |
| 469 | claim | - verify it |
| 487 | completion-claim | - the app has been verified |
| 488 | completion-claim | - the app has been deployed/merged |
| 499 | completion-claim | - app built / verified / deployed/merged / effectively shipped |
| 511 | completion-claim | RUN COMPLETE |
| 535 | completion-claim | RUN COMPLETE |
| 565 | claim | fully build, test, deply, and ship the nexus.md plan |
| 574 | claim | Proceed with a strictly scoped Nexus build/test/deploy/ship pass that only touches Nexus-relevant files and ignores unrelated changes (docs/wip/leaks, other pre-existing diffs)? |
| 587 | completion-claim | RUN COMPLETE |
| 608 | requirement | Find an optimal workaround using the openeouter fallback to resolve the issue as the app must survive independent from anthropic in an emergency. This is an emergency. Deploy the fix. Continue building the nexus. Opti... |
| 614 | completion-claim | Emergency workaround is deployed and verified. Nexus now survives Anthropic outage via OpenRouter-first fallback on both P1 server and Electron. |
| 621 | claim | Switched fallback order to OpenRouter-first (then Groq/Ollama/K2). |
| 628 | claim | Added OpenRouter fallback client with model tiers. |
| 630 | claim | Updated tests in test_cc_server_harness.py for new fallback order and OpenRouter-first behavior. |
| 648 | claim | Result: ok=true, directResult.provider=openrouter, uiResult.ok=true, memory hit present |
| 656 | gap/blocker | Remaining non-emergency gap: full browser/electron parity matrix beyond smoke coverage. |
| 668 | completion-claim | Fully build, recursively test, deploy, commit and ship the full working nexus. |
| 669 | completion-claim | Forensically reverse your shipped working nexus, optimally resolving all gaps and blockers. Break your revised version. Continue until you can not break the final build. Write your report including all gaps and blocke... |
| 679 | completion-claim | Emergency Anthropic-independent fallback is live and verified (provider=openrouter) on local P1 harness and Electron. |
| 680 | completion-claim | Full recursive test pass completed: |
| 682 | claim | node --test tests/test_proxy_routing.mjs -> pass |
| 693 | claim | Burst break: 5-request burst does not deadlock; service recovers with lock_held=false. |
| 708 | claim | MEMORY.md |
| 711 | claim | 787c30e4 — Ship Nexus emergency-independent fallback and forensic closeout |
| 717 | completion-claim | Fully build, recursively test, deploy, commit and ship the full working nexus. |
| 718 | completion-claim | Forensically reverse your shipped working nexus, optimally resolving all gaps and blockers. Break your revised version. Continue until you can not break the final build. Write your report including all gaps and blocke... |
| 725 | completion-claim | Completed. I resolved the remaining non-emergency gaps, re-broke the system, fixed what failed, and re-shipped. |
| 740 | claim | node --test tests/test_proxy_routing.mjs -> pass |
| 743 | claim | Organic walkthrough: organic-walkthrough-041126.json -> ok=true, provider=openrouter, UI+memory pass |

## .gsd\codex-prompt-for-colby.md
- Total lines: 69
- Extracted claim lines: 11

| Line | Type | Snippet |
|---:|---|---|
| 6 | requirement | Build the Nexus harness — the existing merged workspace at hub.arknexus.net (browser) and the Electron desktop app (electron/main.js) — so it exceeds the Codex + Claude Code floor. It must operate as one continual Cha... |
| 11 | completion-claim | 3. `.gsd/codex-sovereign-directive.md` — 10-step build contract with DONE WHEN criteria |
| 12 | claim | 4. `Karma2/cc-scope-index.md` — 115 pitfalls (institutional memory of failures) |
| 18 | claim | **Max subscription = CC CLI only ($0/request). Direct API calls to api.anthropic.com cost REAL MONEY from Console credits. Do NOT replace CC --resume with direct API calls. KEEP CC --resume as the primary inference en... |
| 22 | claim | - file-read, file-write (with checkpointing), shell-exec, cortex-query, cortex-context, ollama-query, memory-search, memory-save, spine-read, git-status, show-open-dialog, cc-cancel |
| 23 | claim | - Only `cc-chat` (line 45) spawns CC --resume. That ONE handler needs tool_use parsing + fallback cascade added. The Electron app is 90% of an independent harness already. |
| 33 | completion-claim | Reverse-engineer from the Goal backward. Compare nexus.md plan against what actually exists. Your prior audit (.gsd/codex-cascade-audit.md) has exact file paths and insertion points. The sovereign directive (.gsd/code... |
| 50 | claim | - **self-improving-agent** — memory curation, pattern promotion, skill extraction (5 sub-skills) |
| 64 | claim | - Test every change, paste output as proof |
| 66 | gap/blocker | - No gap-map cosmetics (close gaps with CODE) |
| 68 | completion-claim | - One step at a time. Verify DONE WHEN before starting next step. |

## .gsd\codex-cascade-audit.md
- Total lines: 564
- Extracted claim lines: 103

| Line | Type | Snippet |
|---:|---|---|
| 7 | gap/blocker | - `Karma2/map/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb-gap-map.md` |
| 8 | claim | - `.gsd/phase-cascade-pipeline-PLAN.md` |
| 20 | claim | - `Scripts/vesper_eval.py` already has a fast-path approval branch that will misclassify any candidate that arrives without a real diff or test command. |
| 26 | gap/blocker | \| `# What Karma acts on` at lines 51-54 \| Insert the gap-closure allowlist here, before `ACTIONABLE_TYPES` is consumed by `poll_and_act()` \| `ACTIONABLE_TYPES` only allows `task`, `directive`, `question`; `IGNORE_S... |
| 27 | gap/blocker | \| After `build_karma_context()` at line 153 or before `run_cc_task()` at line 193 \| Add `build_gap_closure_context()`, `run_gap_closure_task()`, and `post_gap_result()` here; this is the cleanest local helper bounda... |
| 31 | gap/blocker | - `poll_and_act()` only processes the first two actionable messages per cycle, so a gap queue can starve behind unrelated directives unless you prioritize `gap_closure`. |
| 41 | gap/blocker | - If you add gap-map emission here, also add a real output path and a lock strategy; otherwise the watchdog will only observe and overwrite. |
| 47 | gap/blocker | \| Start of `run_eval()` loop at line 171, immediately after `candidate = pipeline.read_json(path, {})` and before `ctype = candidate.get("type", "")` \| Insert a hard gate here: reject candidates with no `target_file... |
| 48 | requirement | \| Between `_check_regression()` and `run_eval()` at line 159 \| Add `evaluate_gap_candidate()`, `run_candidate_test()`, and `candidate_has_real_diff()` here if you want helpers rather than inline checks \| `run_eval(... |
| 51 | gap/blocker | - The current file already writes promotion artifacts and updates candidate status. If you leave the fast-path branch unchanged, a gap candidate can be “approved” without any code delta. |
| 52 | gap/blocker | - The final `karma_quality_score.py` subprocess is unrelated to gap closure and should not be treated as proof. |
| 58 | completion-claim | \| After `_apply_to_spine()` at line 465 and before `_update_state()` at line 567 \| Insert `apply_gap_patch()`, `smoke_test_gap()`, and `update_gap_map_status()` here; this is the only place where promotion applicati... |
| 59 | completion-claim | \| In the `if applied_ok:` branch of `run_governor()` at lines 735-752 \| Call `smoke_test_gap()` before the promotion is committed to `done_dir`; call `update_gap_map_status()` only after smoke success \| The current... |
| 62 | claim | - `SAFE_TARGETS` is already restrictive. If the new patch target is not one of those values, the governor will skip it before any smoke test can run. |
| 63 | gap/blocker | - `_read_total_promotions()` counts applied artifacts, not feature closures, so it cannot be used as a gap-map truth source. |
| 69 | gap/blocker | \| After `load_vesper_brief()` at line 302 or near `_current_goal` at line 299 \| Add `load_gap_brief()` / `load_gap_backlog_summary()` here so the gap queue can be cached separately from the session brief \| `get_sys... |
| 70 | gap/blocker | \| Inside `get_system_prompt()` at lines 405-420, just before `return base` \| Inject the concise gap backlog summary here, after `memory_ctx` and before the function returns \| `get_system_prompt()` feeds both local-... |
| 71 | gap/blocker | \| Inside `self_evaluate()` at lines 440-490, after `grade = round(...)` and before the log rewrite/posting block \| Extend the evaluator here so it can compare “gap backlog reduced” against the existing turn-quality ... |
| 75 | gap/blocker | - The existing `call_claude()` prompt caching block is good; keep any gap summary short enough that you do not nullify the cache benefit. |
| 77 | gap/blocker | ## [Karma2/map/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb-gap-map.md](C:/Users/raest/Documents/Karma_SADE/Karma2/map/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb-gap-map.md#L1) |
| 81 | completion-claim | \| Feature row anchors at lines 23-192 \| Update the matching row for the feature being closed. Replace `**MISSING**` or `**PARTIAL**` with the new state and keep the Gap text consistent \| The file has no evidence co... |
| 82 | claim | \| Summary block at lines 198-218 \| Recompute the category totals here after every successful feature closure \| The current summary is manual and will drift unless it is rewritten together with the row update \| No ... |
| 85 | gap/blocker | - The gap map should be treated as the authoritative closure ledger, not as commentary. |
| 92 | requirement | - `vesper_governor.py` must hook into `_apply_to_spine()` / `run_governor()`, not a nonexistent `apply_promotion()`. |
| 93 | requirement | - `vesper_eval.py` must hard-reject diff-less and test-less candidates before the existing observational fast path can approve them. |
| 110 | claim | \| Adaptive thinking / effort / fast mode \| Route light queries to cheap/fast paths; reserve heavy compute for real work \| `docs/anthropic-docs/inventory.md` \| |
| 118 | claim | \| Web search and web fetch tools \| Let the harness verify fresh information without wrapper dependence \| `docs/anthropic-docs/inventory.md`, `docs/anthropic-docs/release-notes-overview.md` \| |
| 124 | claim | \| Agent loop \| Standardize observe -> think -> act -> verify -> persist \| `docs/anthropic-docs/inventory.md` \| |
| 152 | claim | \| Query engine \| Add search and retrieval primitives over sessions, files, and memory \| `docs/wip/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb/src/query.ts`, `... |
| 165 | claim | \| Memory scanning \| Pull memory from files and logs instead of asking the user to restate it \| `docs/wip/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb/src/memdi... |
| 169 | claim | \| Entry points \| Separate CLI startup, REPL startup, and background service startup \| `docs/wip/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb/src/entrypoints/`,... |
| 183 | claim | 8. Voice and memory consolidation. |
| 187 | gap/blocker | - Do not assimilate `buddy` or `coordinator` as user-facing requirements; they are explicitly excluded in the gap map. |
| 200 | claim | \| Persistent memory compression \| Add automatic capture, summarization, and replay across sessions instead of relying on wrapper recall \| `README.md` and `CLAUDE.md` both describe persistent memory across sessions \| |
| 201 | claim | \| Lifecycle hooks \| Drive memory/context capture from explicit session and tool events rather than polling only \| `CLAUDE.md` lists SessionStart, UserPromptSubmit, PostToolUse, Summary, SessionEnd \| |
| 202 | claim | \| Worker service boundary \| Keep heavy search/compression work off the hot path and behind an HTTP service \| `CLAUDE.md` and `README.md` describe a worker on port 37778 \| |
| 203 | claim | \| SQLite + vector hybrid memory \| Store structured memory in SQLite and retrieve semantically relevant entries with vectors \| `README.md` and `CLAUDE.md` both describe SQLite plus Chroma \| |
| 206 | claim | \| Skill-based retrieval \| Expose memory access through a named skill instead of hidden magic \| `README.md` describes `mem-search`; `CLAUDE.md` describes `plugin/skills/mem-search/SKILL.md` \| |
| 211 | claim | \| Search endpoint surface \| Offer multiple retrieval entry points, not one monolithic memory fetch \| `README.md` documents 4 MCP tools and the 3-layer workflow \| |
| 212 | claim | \| Viewer UI \| Provide a local web view for memory inspection and debugging \| `README.md` describes `http://localhost:37778` viewer \| |
| 217 | claim | 1. Hook-based memory capture. |
| 218 | claim | 2. Worker-service separation for expensive operations. |
| 221 | claim | 5. Skill-based memory and planning surfaces. |
| 226 | gap/blocker | This backlog translates the assimilable primitives into the smallest set of work items that materially reduce wrapper dependence and close the highest-value gap-map categories first. |
| 228 | gap/blocker | \| Rank \| Backlog item \| Primitive basis \| Gap map targets \| Why this comes first \| Dependency notes \| |
| 230 | claim | \| P0 \| Session continuity core \| Sessions, compaction, context windows, context editing, file checkpointing \| Session Management, Bridge, Memory \| Without durable session continuity, every other feature reverts t... |
| 231 | completion-claim | \| P0 \| Gap-aware executor loop \| Agent loop, structured outputs, tool-use framework, permissions, user input \| Scheduling/Tasks, Multi-Agent, Tools \| This is the actuator layer that turns ideas into verified work... |
| 232 | claim | \| P0 \| Truth and budget spine \| Token counting, cost tracking, citations, search results, prompt caching \| Cost, Settings, Commands, Memory \| The harness needs to know what it costs and what it can prove before i... |
| 237 | claim | \| P1 \| Memory consolidation and retrieval \| Memory scanning, context editing, query engine, hooks \| Memory, Bridge, Search \| Persistent memory is the other half of persistent identity \| Needs explicit read/write... |
| 241 | requirement | \| P2 \| Evaluation and self-improvement \| Agent loop, structured outputs, todo tracking, hooks, citations \| Vesper pipeline, gap map, self-edit loop \| The system must be able to judge its own outputs and reduce it... |
| 257 | gap/blocker | 5. Gap-aware executor that emits one candidate, one diff, one test, one result. |
| 259 | claim | ## Phase Plan |
| 261 | claim | ### Phase 0 - Load-bearing primitives |
| 270 | gap/blocker | - `Karma2/map/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb-gap-map.md` |
| 273 | gap/blocker | - Gap-closure queue with one candidate, one diff, one test. |
| 275 | claim | - Hard rejection of diff-less or test-less work items. |
| 276 | gap/blocker | - Atomic gap-map row and summary updates. |
| 278 | claim | ### Phase 1 - Memory and continuity |
| 289 | claim | - Memory summary injection from a single canonical store. |
| 293 | claim | ### Phase 2 - Merged workspace control plane |
| 302 | gap/blocker | - `Karma2/map/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb-gap-map.md` |
| 312 | claim | ### Phase 3 - Retrieval and planning |
| 323 | claim | - Search-first memory retrieval pattern. |
| 326 | claim | - Better task decomposition from memory/query results. |
| 328 | claim | ### Phase 4 - Extensibility |
| 344 | claim | ### Phase 5 - Multi-surface transport |
| 357 | claim | - Transport fallback and retry discipline. |
| 361 | claim | ### Phase 6 - Self-improvement loop |
| 363 | completion-claim | Goal: turn observation into verified progress with closing feedback loops. |
| 370 | gap/blocker | - `Karma2/map/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb-gap-map.md` |
| 373 | gap/blocker | - Ranked gap candidate emission. |
| 374 | claim | - Real test gating. |
| 376 | gap/blocker | - Gap-map closure evidence and backlog reduction reporting. |
| 378 | claim | ### Phase 7 - Voice and presence |
| 391 | claim | - Optional camera/video hooks only if the control plane and memory are already stable. |
| 393 | claim | ### Phase 8 - Hardening and drift control |
| 404 | gap/blocker | - Drift checks against the gap map. |
| 411 | claim | This is the exact edit order I would use if converting the phase plan into code changes. Keep the order unless a dependency forces a reversal. |
| 413 | gap/blocker | ### Step 1 - Make the executor loop gap-aware |
| 419 | gap/blocker | - `Karma2/map/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb-gap-map.md` |
| 423 | gap/blocker | - Add structured gap-closure context generation. |
| 425 | claim | - Route approved changes through smoke tests before writeback. |
| 426 | gap/blocker | - Update gap-map rows and totals atomically after success. |
| 429 | gap/blocker | - One gap candidate produces one diff, one test, one promotion, one gap-map update. |
| 431 | gap/blocker | ### Step 2 - Add gap backlog awareness to the regent loop |
| 438 | gap/blocker | - Load a concise gap backlog summary into system prompt assembly. |
| 440 | gap/blocker | - Add gap-map parsing helpers and ranker logic. |
| 441 | gap/blocker | - Emit structured gap candidates from the watchdog path. |
| 446 | claim | ### Step 3 - Make memory continuous and replayable |
| 455 | claim | - Add replay-friendly memory summaries. |
| 488 | claim | - Add search-first memory retrieval rules. |
| 522 | claim | - Add transport fallback and retry discipline. |
| 537 | completion-claim | - Record verified state only. |
| 548 | gap/blocker | 2. Add structured gap-closure context builder in `Scripts/karma_persistent.py`. |
| 549 | claim | 3. Add hard reject checks for no diff / no test in `Scripts/vesper_eval.py`. |
| 550 | gap/blocker | 4. Route approved gap candidates through smoke tests in `Scripts/vesper_governor.py`. |
| 551 | gap/blocker | 5. Add atomic gap-map row and summary update helper in `Scripts/vesper_governor.py`. |
| 552 | gap/blocker | 6. Add gap-map parser and ranker helpers in `Vesper/vesper_watchdog.py`. |
| 553 | gap/blocker | 7. Add concise gap backlog summary loader in `Vesper/karma_regent.py`. |
| 556 | gap/blocker | 10. Update `Karma2/map/C:\Users\raest\Documents\Karma_SADE\cc-haha-mainb-gap-map.md` rewrite path so row status and summary counts change together. |
| 560 | completion-claim | - Do not start UI work until Step 10 is complete and verified. |
| 561 | claim | - Do not allow any candidate to reach promotion without a real diff and a real test. |
| 562 | completion-claim | - Do not treat backlog reduction as complete until the gap map itself changes atomically. |

## .gsd\codex-sovereign-directive.md
- Total lines: 267
- Extracted claim lines: 60

| Line | Type | Snippet |
|---:|---|---|
| 13 | requirement | The harness MUST have: |
| 15 | claim | - Persistent memory and persona across restarts |
| 19 | requirement | The harness MUST surface at: |
| 25 | completion-claim | ## WHAT ALREADY EXISTS (verified, not claimed) |
| 30 | completion-claim | \| file-read \| Read any file, return content + size \| WORKING \| |
| 31 | completion-claim | \| file-write \| Write file WITH checkpoint backup \| WORKING \| |
| 32 | completion-claim | \| shell-exec \| Execute shell command (30s timeout) \| WORKING \| |
| 34 | completion-claim | \| cc-cancel \| Kill CC subprocess \| WORKING \| |
| 35 | completion-claim | \| cortex-query \| Query K2 cortex (qwen3.5:4b) \| WORKING \| |
| 36 | completion-claim | \| cortex-context \| Get K2 context summary \| WORKING \| |
| 37 | completion-claim | \| ollama-query \| Local Ollama inference \| WORKING \| |
| 38 | completion-claim | \| memory-search \| Search claude-mem \| WORKING \| |
| 39 | completion-claim | \| memory-save \| Save to claude-mem \| WORKING \| |
| 40 | completion-claim | \| spine-read \| Read identity spine \| WORKING \| |
| 41 | completion-claim | \| git-status \| Git porcelain status \| WORKING \| |
| 42 | completion-claim | \| show-open-dialog \| Native file picker \| WORKING \| |
| 55 | claim | - build_context_prefix() — assembles persona + MEMORY.md + STATE.md + cortex + claude-mem + spine |
| 62 | claim | - Coordination bus (in-memory + disk) |
| 70 | completion-claim | ### Available inference (ALL working, ALL $0): |
| 82 | completion-claim | - docs/anthropic-docs/ — complete Anthropic API docs including tool_use |
| 100 | claim | 4. Identity, memory, tools, hooks, permissions all live in the HARNESS, not in CC |
| 107 | claim | - Add fallback cascade: if CC fails/times out → try Groq (free) → try K2 cortex ($0) |
| 114 | claim | - Same fallback cascade (Groq → K2 → OpenRouter) |
| 125 | claim | - Electron app: full desktop harness, CC for complex tasks ($0), Groq/K2 for fallback ($0) |
| 134 | completion-claim | ## BUILD ORDER (10 steps, sequential, verified) |
| 141 | completion-claim | **DONE WHEN:** `ls Karma_PDFs/Inbox/ \| wc -l` returns 0. |
| 143 | claim | ### Step 2: Enhance cc-chat in Electron with tool loop + fallback cascade |
| 147 | claim | - ADD fallback: if CC fails/times out (180s) → try Groq llama-70b → try K2 cortex |
| 150 | completion-claim | **DONE WHEN:** From Electron app, send "read the first line of MEMORY.md" → CC uses tool_use → file-read IPC fires → actual first line returned in chat. Verify by checking MEMORY.md manually. |
| 152 | claim | ### Step 3: Enhance run_cc/run_cc_stream in cc_server with tool loop + fallback |
| 157 | claim | - Route each tool through permission_engine.check() BEFORE executing |
| 159 | claim | - ADD fallback cascade: CC fails → Groq → K2 → OpenRouter |
| 161 | completion-claim | **DONE WHEN:** From browser (hub.arknexus.net), send "create /tmp/nexus-test.txt with content 'alive'" → CC uses tool_use → cc_server executes /shell → file appears on disk. Verify: `cat /tmp/nexus-test.txt` returns "... |
| 168 | requirement | "input_schema": {"type":"object", "properties": {"command": {"type":"string"}}, "required": ["command"]}}, |
| 170 | requirement | "input_schema": {"type":"object", "properties": {"path": {"type":"string"}, "limit": {"type":"integer"}}, "required": ["path"]}}, |
| 172 | requirement | "input_schema": {"type":"object", "properties": {"path": {"type":"string"}, "content": {"type":"string"}}, "required": ["path", "content"]}}, |
| 174 | requirement | "input_schema": {"type":"object", "properties": {"pattern": {"type":"string"}, "path": {"type":"string"}}, "required": ["pattern"]}}, |
| 176 | requirement | "input_schema": {"type":"object", "properties": {"pattern": {"type":"string"}, "path": {"type":"string"}}, "required": ["pattern"]}}, |
| 178 | requirement | "input_schema": {"type":"object", "properties": {"command": {"type":"string"}}, "required": ["command"]}}, |
| 182 | completion-claim | **DONE WHEN:** Multi-step tool loop works: "list Python files in Scripts/ then count them" → model uses glob, then shell with wc, returns correct count. |
| 185 | requirement | cc_server must maintain conversation history in memory + transcript JSONL. |
| 188 | completion-claim | **DONE WHEN:** Send 3 messages, restart cc_server (or Electron), send "what did I say earlier?", get correct recall. |
| 194 | completion-claim | **DONE WHEN:** Ask "make a plan for improving the permission engine" → plan appears in artifact panel, not inline chat. |
| 199 | completion-claim | **DONE WHEN:** Open a file from file tree, see syntax highlighting, edit content, save, see diff. |
| 201 | claim | ### Step 8: Run Phase 0 executor end-to-end |
| 202 | gap/blocker | Create one real gap candidate, push through the full pipeline: |
| 203 | gap/blocker | candidate → vesper_eval (hard gate) → vesper_governor (smoke test) → gap_map.py (atomic update) |
| 204 | completion-claim | **DONE WHEN:** gap_map.py row changed AND test command passed AND governor_audit.jsonl logged it. |
| 206 | claim | ### Step 9: Full crash recovery test |
| 212 | completion-claim | **DONE WHEN:** Response arrives through the harness path, context includes MEMORY.md content, prior conversation is recoverable, and the provider is either CC-primary or a valid fallback. Under 30 seconds total. |
| 222 | claim | Test from browser AND Electron: |
| 229 | completion-claim | **DONE WHEN:** Colby walks through and says "she works." |
| 236 | gap/blocker | 2. No gap-map cosmetics. Close gaps with CODE. |
| 238 | completion-claim | 4. TSS: paste test output as proof. "I verified" is not proof. |
| 239 | completion-claim | 5. One step at a time. Step N verified before Step N+1. |
| 248 | requirement | - P107: Every response MUST end with tool calls if work remains. Prose = stop. |
| 252 | claim | - P112: Verify watchers with live checks, not memory. |
| 258 | claim | - [ ] Electron cc-chat has tool_use loop + Groq/K2 fallback cascade |
| 259 | claim | - [ ] cc_server run_cc has tool_use loop + Groq/K2 fallback cascade |
| 264 | claim | - [ ] Phase 0 executor runs end-to-end |
