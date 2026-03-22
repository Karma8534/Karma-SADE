# STATE: Karma Peer — Decisions, Blockers, Progress

**Last updated:** 2026-03-22T08:40:00Z
**Session:** 121 COMPLETE (K-3 end-to-end verified, autonomous email pipeline live — check/status/personal in archon, Colby confirmed both emails received)
**Canonical source:** This file. Read at session start.

---

## Current Status (Verified 2026-03-10)

| Component | Status | Notes |
|-----------|--------|-------|
| **Consciousness Loop** | ✅ WORKING | 60s OBSERVE-only cycles. Zero LLM calls confirmed in source. RestartCount=0. |
| **Hub Bridge API** | ✅ WORKING | /v1/chat, /v1/ambient, /v1/context, /v1/cypher, /v1/ingest operational. |
| **Voice & Persona** | ✅ DEPLOYED | Peer-level voice via claude-haiku-4-5-20251001 (Session 76: haiku-20241022 was RETIRED, migrated). Both modes. |
| **FalkorDB Graph** | ✅ FULLY CAUGHT UP | 3877 nodes (3305 Episodic + 571 Entity + 1 Decision). batch_ingest cron every 6h. Last run: 305 eps/s, 0 errors. |
| **Ledger** | ✅ GROWING | 6,571 entries (verified 2026-03-16). Git commits + session-end hooks capturing actively. |
| **Work-Loss Prevention** | ✅ GATES LIVE | Pre-commit hook + session-end hook both active and verified. |
| **Ambient Tier 1 Hooks** | ✅ WORKING | Git + session-end captures verified in ledger. |
| **Ambient Tier 2 Endpoint** | ✅ DEPLOYED | /v1/context endpoint working. |
| **GSD File Structure** | ✅ ADOPTED | All .gsd/ files in place and being used. |
| **Chrome Extension** | ❌ SHELVED | Never worked reliably. Legacy data only. |
| **Conversation Capture** | ✅ WORKING | All 3049 hub/chat episodes ingested via --skip-dedup. |
| **batch_ingest Schedule** | ✅ CONFIGURED | Cron every 6h on vault-neo. --skip-dedup mode. |
| **karma-server image** | ✅ REBUILT | Session-66: graph_query handler + hooks.py whitelist fix. |
| **Primary Model (Decision #29)** | ✅ LIVE — Haiku 4.5 | claude-haiku-4-5-20251001 for both MODEL_DEFAULT + MODEL_DEEP. Session 76 emergency migration. |
| **Routing/Pricing (Decision #29)** | ✅ UPDATED | Haiku 4.5 pricing: $1.00/$5.00 per 1M. routing.js allow-list updated. |
| **GLM Rate Limiter** | ✅ KEPT (compat) | 40 RPM class kept in routing.js for compat; not invoked for claude- models. |
| **Config Validation Gate** | ✅ LIVE | MODEL_DEFAULT + MODEL_DEEP allow-lists. [CONFIG ERROR] + exit(1) on bad config. 27/27 tests. |
| **OpenAI API key** | ✅ SECURED | File-based read (mounted volume), not env var (docker inspect clean). |
| **PDF Watcher** | ✅ WORKING | Rate-limit backoff + jam notification + time-window scheduling. |
| **System Prompt Accuracy** | ✅ FIXED Session 85 | Tools contradiction removed (line 254). K2 ownership directive added. Tool list updated (shell_run, defer_intent, get_active_intents). "deep-mode only" confusion eliminated. 24,594 chars. |
| **Deep-Mode Tool Gate** | ⚠️ CLARIFIED | Session-85: deep_mode only switches Haiku↔Sonnet model. Tools available in ALL modes (line 1894: all routes through callLLMWithTools). "deep-mode only" labels removed from system prompt. |
| **v9 Phase 3 Persona Coaching** | ✅ DEPLOYED | Session-67: "How to Use Your Context Data" section in system prompt. KARMA_IDENTITY_PROMPT: 10,415 → 11,850 chars. docker restart only. |
| **FAISS Semantic Retrieval** | ✅ LIVE | fetchSemanticContext() in hub-bridge. karmaCtx + semanticCtx via Promise.all. 4073 entries indexed. Session-62. |
| **Correction Capture Protocol** | ✅ LIVE | Memory/corrections-log.md + CC Session End step 2. Session-62. |
| **FalkorDB lane backfill** | ✅ DONE | 3040 Episodic nodes with lane=NULL → lane="episodic". 0 remaining. Session-62. |
| **anr-vault-search** | ✅ FAISS | Custom search_service.py (NOT ChromaDB). FAISS + text-embedding-3-small. Auto-reindex on ledger change. |
| **MEMORY.md Spine Injection** | ✅ LIVE | `_memoryMdCache` (tail 2000 chars, 5min refresh) injected as "KARMA MEMORY SPINE (recent)" in buildSystemText(). Session-85: fixed from 800→2000. |
| **Universal Thumbs (turn_id)** | ✅ LIVE | All Karma messages show 👍/👎 via turn_id fallback. /v1/feedback accepts turn_id OR write_id. 11/11 tests. Session-72. |
| **Confidence Levels** | ✅ LIVE | [HIGH]/[MEDIUM]/[LOW] mandatory on technical claims. Anti-hallucination hard stop before [LOW] assertions. System prompt 12,524→14,601 chars. Session-72. |
| **Entity Relationships** | ✅ FIXED | MENTIONS co-occurrence replaces stale RELATES_TO (frozen at 2026-03-04). 11/11 tests. Session-72. |
| **Recurring Topics** | ✅ LIVE | Top-10 entities by episode count. _pattern_cache refreshed every 30min at startup. Session-64. |
| **Graphiti Watermark** | ✅ LIVE | batch_ingest watermark mode (Session 63). New episodes get entity extraction. :MENTIONS edges grow. |
| **batch_ingest cron** | ✅ --skip-dedup FIXED | Session-70: cron now uses --skip-dedup permanently. Graphiti mode silently fails at scale. |
| **GLM Tool-Calling** | ✅ LIVE | callGPTWithTools() now handles all non-Anthropic models (line 868 fix). Session-66. |
| **graph_query tool** | ✅ LIVE | Karma can run Cypher against FalkorDB neo_workspace in standard GLM mode. End-to-end verified. Session-66. |
| **get_vault_file tool** | ✅ LIVE | Karma can read canonical files by alias (MEMORY.md, system-prompt, etc.). Handled in hub-bridge. Session-66. |
| **hooks.py whitelist** | ✅ UPDATED | graph_query + get_vault_file added to ALLOWED_TOOLS. Session-66. |
| **TOOL_NAME_MAP** | ✅ FIXED | Pre-existing bug: was mapping read_file→file_read (wrong names). Now empty dict = identity passthrough. Session-66. |
| **K2_PASSWORD secret** | ✅ SECURED | Removed plaintext from docker-compose.karma.yml → ${K2_PASSWORD} env var. Value in hub.env. Session-66. |
| **Main branch protection** | ✅ ENABLED | allow_force_pushes=false, allow_deletions=false. Session-66. |
| **Deferred Intent Engine (Phase 4)** | ✅ LIVE | defer_intent tool, get_active_intents tool, /v1/feedback intent approval, active intent injection in buildSystemText |
| **MODEL_DEEP** | ✅ LIVE — sonnet-4-6 | Switched from haiku-4-5. ALLOWED_DEEP_MODELS updated. Monthly cap $60. Verified $0.0252/request. |
| **File Upload** | ✅ LIVE | Upload button working. Vision pipeline: JPG/PNG → base64 → Anthropic multimodal (deep mode). Verified with KarmaSession031026a.md. |
| **Thumbs ✓ saved confirmation** | ✅ LIVE | 👍 on write_id shows fade-out "✓ saved" in UI. Session 81. |
| **Aria Integration — Memory Writes** | ✅ LIVE | X-Aria-Delegated removed from aria_local_call. Service key auth only. Aria now writes observations. |
| **Aria Integration — vault-neo sync** | ✅ LIVE | After each aria_local_call, Aria observations POST to /v1/ambient → canonical ledger. Single spine preserved. |
| **Aria Integration — session_id** | ✅ LIVE | UUID per page load (window.karmaSessionId in unified.html). Passed with every aria_local_call. Coherent Aria thread. |
| **K2 Redundancy Cache** | ✅ LIVE | k2/sync-from-vault.sh pull/push/status. Cron: pull every 6h, push every 1h. Cache: /mnt/c/dev/Karma/k2/cache/. aria.service loads identity from cache at startup. Session 84c. |
| **CC Ascendant Watchdog** | ✅ LIVE | K2 systemd timer 60s. run #73 HEALTHY. Scripts/cc_ascendant_watchdog.py. Zero Anthropic tokens. Session 96. |
| **CC Identity Spine** | ✅ LIVE | cc_identity_spine.json on K2. identity.resume_block seeded. Governance tiers (candidate/stable) initialized. Session 96-97. |
| **CC Cohesion Resume Block** | ✅ LIVE | 6-sentence Ascendant assertion in spine. Surfaces in === CC ASCENDANT RESUME BLOCK === banner at every cold start via resurrect Step 1b. Session 97. |
| **Resurrect Step 1b** | ✅ UPDATED | Reads resume_block + stable_identity from K2 spine. Banner shown before brief. /anchor emergency-only. Session 96-97. |
| **CC Evolution Loop** | ✅ ACTIVE | Watchdog sender fixed (cc-watchdog). Phase 12 HEALTHY 0.60. Evolution log has 42 entries. Session 99. |
| **MANDATORY State-Write Protocol** | ✅ IN SYSTEM PROMPT | Section added to 00-karma-system-prompt-live.md: Karma MUST call aria_local_call after any DECISION/PROOF/PITFALL/DIRECTION/INSIGHT. Session 84b. |
| **shell_run tool** | ✅ LIVE | Karma can execute shell commands on K2 via aria /api/exec. Gated by X-Aria-Service-Key. hub-bridge v2.11.0. Session 84d. |
| **K2 /api/exec endpoint** | ✅ LIVE | Added to aria.py on K2. POST :7890/api/exec with command + service key. Returns stdout/stderr/exit_code. Session 84d. |
| **vault-neo → K2 SSH auth** | ✅ LIVE | vault-neo public key in K2 authorized_keys. Reverse tunnel works as karma@localhost:2223. Session 84d. |
| **K2 Structured Tools (k2_*)** | ✅ LIVE | 9 tools: k2_file_read, k2_file_write, k2_file_list, k2_file_search, k2_python_exec, k2_service_status, k2_service_restart, k2_scratchpad_read, k2_scratchpad_write. Hub-bridge routes k2_* → K2 /api/tools/execute. Session 86. |
| **K2 Tool Registry** | ✅ LIVE | k2_tools.py on K2 (9 tools, 23 TDD tests). aria.py endpoints: GET /api/tools/list, POST /api/tools/execute. Session 86. |
| **MAX_TOOL_ITERATIONS** | ✅ FIXED | Raised from 5→12 across Anthropic, OpenAI/ZAI, K2-Ollama providers. Session 86. |
| **Conversation Persistence** | ✅ LIVE | localStorage persistence: saveMessages/loadSavedMessages/clearConversation. New Chat button. Messages survive refresh. Session 87b. |
| **Context Fix (3 changes)** | ✅ DEPLOYED | KARMA_CTX_MAX_CHARS 3500, recent episodes 10, direction.md in buildSystemText. Session 86b. |
| **Coordination Bus v1** | ✅ LIVE | Endpoints + tool + context injection + UI panel + compose input + disk persistence (JSONL). Colby can see and send messages. Session 87b. |
| **K2 Working Memory Injection** | ✅ LIVE | fetchK2WorkingMemory() reads scratchpad.md + shadow.md via /api/exec. 4015 chars injected. 8th param to buildSystemText(). Session 85. |
| **K2 Memory Query (dynamic)** | ✅ FIXED | fetchK2MemoryGraph(userMessage) instead of hardcoded "Colby". 1200 chars, 3 hits. Session 85. |
| **K2 Ownership Directive** | ✅ IN SYSTEM PROMPT | K2 = Karma's resource (Chromium, Codex, KCC). Delegate heavy work to K2. Anthropic model = persona only. Session 85. |
| **Coordination Disk Persistence** | ✅ LIVE | /run/state/coordination.jsonl (bind-mounted). Messages survive rebuilds. loadCoordinationFromDisk() at startup. Session 87b. |
| **Context Tier Routing** | ✅ LIVE | 3-tier context routing: LIGHT (~11K), STANDARD (~20K), DEEP (~47K). Tier selection by message complexity. Session 99. |
| **Prompt Caching (Anthropic)** | ✅ LIVE | 3 cache breakpoints: session history, tool loop, tool definitions. 45-46% cache hit rate. Session 99. |
| **Karma Hard Rule (state claims)** | ✅ LIVE | Must cite K2 WORKING MEMORY before claiming infra state. Added to behavioral contract. Session 99. |
| **Ascendent Folder Protocol** | ✅ LIVE | for-karma/Ascendent/ — Inbox/ (drops), Read/ (processed), ForColby/ (CC→Colby). Session 99. |
| **Family Cohesion Layer** | ✅ LIVE | All 3 agents emit EVOLUTION_TAGS to bus: CC (SESSION CHECKPOINT), Karma (karma_bus_observer/10min), KCC (kcc_enhanced_watchdog/10 runs). Session 99. |
| **KCC Cognitive Bus Posts** | ✅ LIVE | kcc_enhanced_watchdog.py _emit_cognitive_posts(). INSIGHT every 10 runs, DECISION on alerts. TDD PASS. Session 99. |
| **CC Cognitive Checkpoint** | ✅ LIVE | cc_cognitive_write.ps1 writes cc_cognitive_checkpoint.json to K2 at session end. wrap-session mandatory. First run Session 99. |
| **Vesper (Regent)** | ✅ LIVE | karma_regent.py on K2. Sovereign greeting fast path (< 60 chars, no action verbs → [ONLINE] terse status, zero LLM). State injection ([VESPER STATE] block prepended to all LLM calls). VESPER_IDENTITY SOVEREIGN ARRIVAL rule. Hallucination closed. Session 103. |
| **Vesper UI (/regent)** | ✅ LIVE | Two-column: chat left (regent→colby), status right. isStatusMessage() filters from=colby — no double-display. Session 101-103. |
| **Vesper 6-Tier Inference Cascade** | ✅ REORDERED Session 107 | K2 → P1 → z.ai → Groq → OpenRouter → Claude. TDD: 3/3 green. Gate: timeout/None only (no KPI routing). regent_inference.py. |
| **Vesper Self-Improvement Pipeline** | ✅ ACTIVE | self_improving=True, spine v8, 2 stable patterns, total_promotions=4. All 5 convergence fixes deployed (vesper_patch_regent.py). Root blocker B1: ~50 new messages needed to fill tool_used=True window. |
| **Vesper KPI Cortex (Pre-Frontal)** | ✅ DEPLOYED | karma_regent.py: _current_goal/_kpi_window globals, load_current_goal(), get_kpi_trend(). state_block injects goal+kpi on every turn. Session 107. |
| **Vesper Adaptive Scan** | ✅ DEPLOYED | vesper_watchdog.py: backward scan collects 50 structured entries (vs stale 500-line window). Session 107. |
| **Vesper FalkorDB Write** | ✅ DEPLOYED | vesper_governor.py: pattern write via hub-bridge /v1/cypher on every promotion. safe_exec governance target + SAFE_EXEC_WHITELIST. Session 107. |
| **Regent Guardrails + Triage** | ✅ LIVE (pre-existing) | regent_guardrails.py (346 lines, checksum-gated begin_turn/finalize_turn), regent_triage.py (63 lines, classify()). docs/regent/ directory with identity_contract.json, session_state_schema.json. Begin_guarded_turn blocks on checksum drift. NOT built this session — was already on K2. |
| **Vesper Memory Quality (Gap 3)** | ✅ FIXED | Memory now stores Q&A interaction summaries (not raw log noise). get_memory_context() returns last 5 interactions. append_memory("interaction", ...) called at line 680. Session 104. |
| **vesper-watchdog.timer (Gap 4)** | ✅ LIVE | systemd timer: OnBootSec=2min, OnUnitActiveSec=10min. vesper-watchdog.service + .timer enabled on K2. Session 104. |
| **vesper_identity.md (Gap 6)** | ✅ CREATED | /mnt/c/dev/Karma/k2/cache/vesper_identity.md — sovereign voice anchor. Loaded at startup by _load_vesper_identity(). karma-regent restarted with new identity. Session 104. |
| **K2 MCP Server** | ✅ LIVE | Scripts/k2_mcp_server.py — 14 tools (file_read/write/list/search, python_exec, service_status/restart, scratchpad_read/write, bus_post, kiki_status/inject, ollama_chat, vesper_state). Registered in ~/.claude/mcp.json. Session 104. |
| **Operational Status Block** | ✅ IN SYSTEM PROMPT | "What Is Wired and Working RIGHT NOW" table + anti-pattern list in 00-karma-system-prompt-live.md. Fixes 2-year rediscovery cycle. Session 87b. |

---

## Active Blockers

1. ~~Coordination bus has no UI visibility~~ ✅ RESOLVED (Session 87b) — Panel + compose input deployed.
2. ~~Conversation thread UI clears on refresh~~ ✅ RESOLVED (Session 87b) — localStorage persistence deployed.
3. ~~**KIKI BRIDGE BROKEN**~~ ✅ RESOLVED (Session 90) — kiki_ filenames correct. Bridge reads real data.
4. ~~**P0: vault-neo cannot run tests**~~ ✅ RESOLVED (Session 92) — pytest installed, 27/27 pass. Artifact at docs/supervisor/artifacts/P0-vault-neo-pytest-evidence.txt. Commit 792ef95.
5. ~~**Kiki feedback loop missing**~~ ✅ RESOLVED (Session 93) — last_cycle_ts added to kiki state on every cycle. fetchK2WorkingMemory() path verified functional via Aria exec. Cycle count drift was cache lag (5min TTL), not a real gap.
6. ~~**Coordination bus REST API returns 404**~~ ✅ RESOLVED (Session 93) — /v1/coordination aliased to /v1/coordination/recent in hub-bridge. Returns 200.
7. ~~**Arbiter config path gap**~~ ✅ RESOLVED (Session 93) — Config/ dir created at /mnt/c/dev/Karma/k2/Config/, governance_boundary_v1.json + critical_paths.json copied from tmp/p0-proof/Config/. PolicyArbiter loads correctly.
8. ~~**4 pending bus messages from Karma**~~ ✅ BUS FIXED — watcher chaos cleared. Bus quiet, no auto-responders running.
9. ~~**CC cohesion test pending**~~ — resume_block confirmed working in Session 97+.
10. **B1: Evolution log sparsity** — 22/89,758 structured entries. Resolves with ~50 new Regent messages. Time-based, no code change needed. ETA 1-3 days.
11. **B2: Synthetic stable patterns** — both stable patterns are Codex e2e artifacts (type=pipeline_e2e_validation). Cosmetic issue; real patterns will emerge as B1 resolves.
12. ~~**P0N-A URGENT**~~ ✅ LIVE (Session 111) — hub.arknexus.net/cc working, CC Ascendant responds with identity + state.
13. **P3-D** — ✅ LIVE as of session 109. Hooks deployed + committed. No longer a blocker.
14. **K2 aria.service inactive** — prevents cognitive snapshots. Needs `systemctl --user start aria` on K2 WSL.

## Next Session Starts Here
1. `/resurrect`
2. Fix `/v1/ambient` route in hub-bridge server.js (PITFALL #9641 — hooks silently failing)
3. OR continue PHASE KNOWLEDGE: next K-* task per Karma2/PLAN.md
**Blocker if any:** None critical. Ambient fix is a hub-bridge deploy (use /deploy skill).

---

## Key Decisions (Locked)

### Decision #1: Droplet Primacy (2026-02-23, LOCKED)
Droplet (vault-neo) is Karma's permanent home. K2 is a worker that syncs back. All state on droplet.

### Decision #2: Dual-Model Routing (2026-02-27, LOCKED)
GLM-4.7-Flash (primary, ~80%) + gpt-4o-mini fallback (~20%). Verified MODEL_DEEP=gpt-4o-mini on 2026-03-04.

### Decision #3: Consciousness Loop OBSERVE-Only (2026-02-28, LOCKED)
K2 consciousness loop does NOT autonomously call LLM. OBSERVE → rule-based DECIDE → LOG only.

### Decision #4: GSD Workflow Adoption (2026-03-03, LOCKED)
GSD file structure adopted: PROJECT.md, REQUIREMENTS.md, STATE.md, ROADMAP.md, phase-CONTEXT/PLAN/SUMMARY per major feature.

### Decision #5: Honesty Contract (2026-03-03, RENEWED)
Brutal honesty always. Evidence before assertions. Never claim done without proof.

### Decision #6: Chrome Extension Shelved (2026-03-03, LOCKED)
Chrome extension never worked reliably. Removed from all documentation.

### Decision #7: PowerShell for Git Ops (2026-03-03, LOCKED)
Git Bash has persistent index.lock issue on Windows. All git operations via PowerShell.

### Decision #8: --skip-dedup is Standard batch_ingest Mode (2026-03-03, LOCKED)
Graphiti dedup queries time out at scale (85% error rate). Direct Cypher write via --skip-dedup: 899 eps/s, 0 errors. Cron uses --skip-dedup by default.

### Decision #9: OpenAI API Key File-Based (2026-03-03, LOCKED)
API key read from mounted volume file, not injected as env var. docker inspect stays clean.

### Decision #10: KARMA_IDENTITY_PROMPT file-loaded at startup (2026-03-04, LOCKED)
Hub-bridge reads Memory/00-karma-system-prompt-live.md via KARMA_SYSTEM_PROMPT_PATH env var at startup.
Injected as identityBlock at top of buildSystemText(). File is volume-mounted read-only.
Future persona changes require only: git pull on vault-neo + docker restart anr-hub-bridge. No rebuild.

### Decision #11: anr-vault-search is FAISS (confirmed 2026-03-04)
anr-vault-search container runs custom search_service.py — FAISS + OpenAI text-embedding-3-small.
NOT ChromaDB. Endpoint: POST localhost:8081/v1/search. All ChromaDB references removed from all docs.

### Decision #12: Semantic context injected in parallel (2026-03-04, LOCKED)
karmaCtx (FalkorDB recency) + semanticCtx (FAISS top-5) fetched via Promise.all before every /v1/chat.
4s timeout on FAISS call — graceful null if service unavailable. No serial dependency.

### Decision #13: callGPTWithTools routes ALL non-Anthropic models (2026-03-05, LOCKED)
Line 868 in server.js changed from `return callLLM()` → `return callGPTWithTools()`. GLM-4.7-Flash
natively supports function calling via Z.ai OpenAI-compatible API. No provider switch needed.

### Decision #14: TOOL_NAME_MAP is identity passthrough (2026-03-05, LOCKED)
Pre-existing bug found: TOOL_NAME_MAP had file_read/file_write/file_edit/shell_exec (wrong names —
karma-server uses read_file/write_file/edit_file/bash). Fixed to empty dict `{}` which falls through to
`|| toolName` in the mapping code. Empty dict = correct. Any non-empty mapping = likely wrong.

### Decision #15: get_vault_file handled in hub-bridge, not karma-server (2026-03-05, LOCKED)
Hub-bridge has /karma/ volume mount access (read-only). karma-server ALLOWED_PATHS doesn't cover /karma/ paths.
graph_query stays proxied to karma-server (needs FalkorDB access). Architecture split by access path.

### Decision #16: Tool-calling gated to deep-mode only (2026-03-05, LOCKED)
Standard GLM requests (deep_mode=false) route to callLLM() — no tools. Deep requests (x-karma-deep: true header) route to callLLMWithTools(). Security fix deployed in Session 67 (commit 41b2c06). Prevents unauthorized tool access in standard chat mode.

### Decision #17: v9 Phase 4 — Karma write agency via thumbs up/down gate (2026-03-05, APPROVED)
Design validated with user. Three-in-one mechanism: (1) thumbs up/down gates Karma's memory writes; (2) accumulates DPO preference pairs; (3) 👎 + text feeds corrections pipeline.
API: POST /v1/feedback {turn_id, rating: +1/-1, note?: string}. turn_id already in every /v1/chat response.
New tools: write_memory(content), annotate_entity(name, note), flag_pattern(description).
Safe target: PATCH /v1/vault-file/MEMORY.md (append-only). Web UI thumbs up/down already present. NOT YET IMPLEMENTED — design only.

---

## Session History

### Session 57 Accomplishments
- FalkorDB unfrozen (Blocker #1)
- hub/chat entries now reach FalkorDB (Blocker #2)
- Cron configured every 6h (Blocker #3)
- GSD docs updated

### Session 58 Accomplishments
- OpenAI API key secured (file-based, not env var)
- karma-server restart loop fixed (gpt-5-mini → gpt-4o-mini)
- GLM rate-limit handling redesigned (throttle, never paid fallback)
- karma-server image rebuilt with all fixes
- K2 sync worker deprecated
- 10 stale remote branches deleted
- compose credentials externalized

### Session 59 Accomplishments
- --skip-dedup added to batch_ingest (899 eps/s, 0 errors)
- FalkorDB datetime() fix (ISO strings only, no datetime() function)
- OPENAI_API_KEY env propagation fixed (os.environ.setdefault())
- Full backfill complete: 3049 episodes ingested (was 1749)
- karma-server image rebuilt with all fixes
- Cron updated to --skip-dedup

---

## Known Limitations
- ~~Conversation persistence~~ ✅ RESOLVED Session 87b — localStorage persistence deployed.
- **Chrome extension:** Shelved permanently
- **K2 not online:** Consciousness loop runs on droplet only
- **No fine-tuning yet:** Need 20+ DPO preference pairs (accumulation in progress)
- **Ambient Tier 3:** Screen capture daemon not built
- **Entity graph growth lag:** Graphiti runs every 6h via cron. New episodes take up to 6h before entity nodes appear in FalkorDB.
- **Per-episode Graphiti failures:** Watermark advances past failed episodes — silently lost at high error rates. Acceptable at low error rates.
- **graph_query 100-row cap:** query_relevant_relationships() returns max 100 rows. Dense graphs may miss edges. Acceptable for now.
- **get_vault_file 20KB cap:** Large files truncated at 20,000 chars. Acceptable for current vault files.
- **hooks.py legacy aliases:** file_read, shell_exec still in ALLOWED_TOOLS but unused (pre-existing, harmless).

---

### Session 67 Accomplishments (2026-03-05)
- Security fix: deep-mode tool gate — standard GLM no longer gets tool execution (commit 41b2c06)
- v9 Phase 3 persona coaching deployed: "How to Use Your Context Data" section in system prompt (commit f90cea7)
  - Fixed stale tool list (read_file/write_file → graph_query/get_vault_file)
  - Entity Relationships behavioral coaching: weave connections unprompted
  - Recurring Topics behavioral coaching: calibrate depth to top topics
  - Deep mode proactivity: call graph_query before answering strategic questions
- karma-server LLM analysis: router.py confirmed dead code (karma-terminal stale since 2026-02-27)
- v9 Phase 4 design approved: Karma write agency via thumbs up/down gate (obs #4032)
- karma-verify smoke test false alarm documented (obs #4035) — checks "reply" but hub returns "assistant_text"

## Next Session Agenda (Session 68)

1. **Acceptance test for v9 Phase 3**: Ask Karma about a Recurring Topic — verify she references relationship data unprompted. This validates persona coaching actually changed behavior.
2. **v9 Phase 4 kickoff**: Brainstorming skill → design doc → implementation plan for write_memory tool + POST /v1/feedback endpoint.
3. **Fix karma-verify skill**: Update smoke test to check "assistant_text" instead of "reply".

---

### Session 60 Accomplishments
- drift-fix Phase complete: pricing, routing, MODEL_DEEP defaults, ANALYSIS_MODEL all corrected
- Stage 3 build_hub.sh: safeguarded build script, app/ guard verified
- Phase F GLM Rate Limiter: GlmRateLimiter class, 25/25 tests GREEN, wired into server.js
- F4 deployed + V1-V5 all verified in production: 429 on burst, deep unaffected, ingest normal, $0 delta
- Two injection attempts caught + flagged (security posture verified)

---

### Session 61 Accomplishments
- Phase G Config Validation Gate: MODEL_DEFAULT allow-list + [CONFIG ERROR] structured log + process.exit(1)
- 27/27 tests GREEN (up from 25/25); two commits RED→GREEN per TDD discipline
- Production verified: docker exit_code=1 on bad MODEL_DEFAULT confirmed
- hub.env inline allowed-value comments added on vault-neo

---

### Session 64 Accomplishments (2026-03-05)
- Entity Relationships: query_relevant_relationships() — bulk RELATES_TO edge query using r.fact
- Recurring Topics: _pattern_cache + _refresh_pattern_cache() — top-10 by episode count, 30min refresh
- Both wired into build_karma_context() + startup loop; 9 new tests, 27/28 suite (1 pre-existing)
- Deployed + verified: 20 edges for Karma query; Karma:357, User:315, Colby:138 in recurring topics
- v9 direction set: persona iteration first (cheap + highest leverage)
- Corrected: Session 63 Graphiti watermark WAS deployed (cc-session-brief only showed top-5 commits)

### Session 63 Accomplishments (2026-03-04)
- Graphiti watermark deployed to vault-neo: entity extraction enabled for new episodes
- batch_ingest.py: watermark logic + Graphiti as default + 200 episode cap
- Cron: --skip-dedup removed, WATERMARK_PATH=/ledger/.batch_watermark set
- corrections-log.md updated

### Session 62 Accomplishments (v8 — 2026-03-04)

**v8 Phase 1: Fix self-knowledge**
- Audited live system prompt — confirmed it was describing Open WebUI/Ollama from Feb 2026, not actual hub-bridge system
- Rewrote Memory/00-karma-system-prompt-live.md: accurate arch, Brave Search, FAISS, 5 data model corrections
- Discovered: hub-bridge was NOT loading the system prompt file — buildSystemText() was fully hardcoded
- Wired KARMA_IDENTITY_PROMPT via fs.readFileSync at startup, injected as identityBlock in buildSystemText()
- Future system prompt updates: git pull + docker restart only (no rebuild needed)
- 4/4 acceptance tests pass: tools list, .verdict.txt location, batch_ingest direction, GLM-4.7-Flash identity

**v8 Phase 3: Correction capture**
- Memory/corrections-log.md created with format template + 6 backlog corrections (all INCORPORATED)
- CLAUDE.md Session End Protocol step 2 added: scan session for Karma errors → corrections-log.md

**v8 Phase 2: Semantic retrieval**
- Discovered: anr-vault-search is NOT ChromaDB — it is custom search_service.py using FAISS + OpenAI text-embedding-3-small
- 4073 entries indexed, auto-reindex on ledger FileSystemWatcher + every 5min periodic
- Added fetchSemanticContext() to hub-bridge (4s timeout, POST localhost:8081/v1/search, top-5)
- karmaCtx + semanticCtx now fetched in parallel via Promise.all before each /v1/chat response
- Tasks 2.2 (new indexer) and 2.4 (cron sync) NOT NEEDED — service already handles these
- All architecture.md, system prompt, MEMORY.md references corrected from ChromaDB → FAISS

**v8 Phase 4: v7 cleanup**
- MONTHLY_USD_CAP=35.00 — already in hub.env (no change needed)
- x-karma-deep capability gate — already in server.js (no change needed)
- lane=NULL backfill: 3040 Episodic nodes set to lane="episodic" via Cypher. 0 remaining.

### Session 66 Accomplishments (2026-03-05)

**Promise Loop Fix — Phases 1 & 2:**
- RC1 fix: Line 413 (buildSystemText) false tool declaration corrected — accurate tool list with deep-mode gate
- RC2 fix: Line 868 `callLLMWithTools()` — changed `callLLM()` → `callGPTWithTools()` for all non-Anthropic models
- RC3 fix: System prompt context size corrected "~1800 chars" → "~12,000 chars (KARMA_CTX_MAX_CHARS)"
- RC4 fix: GLM_RPM_LIMIT raised from 20 → 40 in hub.env; honest 429 behavior documented in system prompt
- graph_query + get_vault_file added to TOOL_DEFINITIONS + TOOL_NAME_MAP + executeToolCall() in server.js
- graph_query handler added to karma-core/server.py execute_tool_action()
- graph_query + get_vault_file added to hooks.py ALLOWED_TOOLS whitelist (pre-existing pitfall: whitelist gates ALL tools)
- TOOL_NAME_MAP pre-existing bug fixed: file_read/file_write/file_edit/shell_exec → empty dict (identity passthrough)
- K2_PASSWORD moved from plaintext in docker-compose.karma.yml → ${K2_PASSWORD} env var + hub.env on vault-neo
- End-to-end verified: hub-bridge logs show callGPTWithTools → finish_reason=tool_calls → execute → finish_reason=stop
- 25 stale remote branches deleted; main branch protection enabled (no force push, no deletion)
- PR #14 squash-merged to main (squash commit: 357bcb9)

### Decision #10: KARMA_IDENTITY_PROMPT file-loaded at startup (2026-03-04, LOCKED)
Hub-bridge reads Memory/00-karma-system-prompt-live.md via KARMA_SYSTEM_PROMPT_PATH env var at startup.
Injected as identityBlock at top of buildSystemText(). File is volume-mounted read-only.
Future persona changes require only: git pull on vault-neo + docker restart anr-hub-bridge. No rebuild.

### Decision #11: anr-vault-search is FAISS (confirmed 2026-03-04)
anr-vault-search container runs custom search_service.py — FAISS + OpenAI text-embedding-3-small.
NOT ChromaDB. Endpoint: POST localhost:8081/v1/search. All ChromaDB references removed from all docs.

### Decision #12: Semantic context injected in parallel (2026-03-04, LOCKED)
karmaCtx (FalkorDB recency) + semanticCtx (FAISS top-5) fetched via Promise.all before every /v1/chat.
4s timeout on FAISS call — graceful null if service unavailable. No serial dependency.

---

**Last updated:** 2026-03-10T22:30:00Z (Session 75 — Model switch to Haiku 3.5 + lib/*.js into git)
**Owner:** Claude Code (writes on Colby approval)
**Canonical location:** C:\Users\raest\Documents\Karma_SADE\.gsd\STATE.md

### Session 68 Accomplishments (2026-03-05)

**v9 Phase 4 — Karma Write Agency: ALL 10 TASKS COMPLETE**

- Task 1: `hub-bridge/lib/feedback.js` — processFeedback + prunePendingWrites, 7 tests green (commit a17ce54)
- Task 2: `write_memory` tool in server.js — pending_writes Map + tool def + writeId threading through callLLMWithTools→callGPTWithTools (commits 57ce894, 268bd08)
- Task 3: `POST /v1/feedback` endpoint — auth + processFeedback + MEMORY.md fs.appendFileSync + DPO vault write (commits fe8a3b8, 722c05a, b002b5b)
- Task 4: `karma-core/hooks.py` — `"write_memory"` added to ALLOWED_TOOLS (commit 362de7e)
- Task 5: karma-server deployed — hooks.py synced to build context, image rebuilt, container healthy (RestartCount=0)
- Task 6: hub-bridge deployed — server.js + lib/feedback.js synced, `lib/` created in parent build context, image rebuilt
- Task 7: `unified.html` — write_id threading + thumbs-down textarea + quality fixes (no 400s, fresh token, double-submit guard) (commits 0618fbb, 314d301)
- Task 8: system prompt — write_memory coaching paragraph in "How to Use Your Context Data" (commit 6f078e7); prompt: 11850→12366 chars
- Task 9: hub-bridge redeployed with all UI changes; RestartCount=0; prompt length confirmed 12366
- Task 10: End-to-end acceptance test PASSED — all 5 tests green:
  1. Standard mode: no write_id ✅
  2. Deep mode: write_id returned ✅
  3. 👍 → `{wrote:true}` + MEMORY.md [KARMA-WRITE] line ✅
  4. 👎 → `{wrote:false}` + MEMORY.md unchanged ✅
  5. DPO pair in ledger: `type:"log", tags:["dpo-pair"]`, ledger 4118→4119 ✅

**DPO bug fixes (2 iterations):**
- Fix 1 (69f061b): bare object → `buildVaultRecord()` (vault requires type/confidence/verification/content as object)
- Fix 2 (cf63957): `type:"dpo-pair"` → `type:"log"` (vault only allows ["fact","preference","project","artifact","log","contact"]); added status check

### Decision #19: write_memory gate uses in-process pending_writes Map (2026-03-05, LOCKED)
Approach A selected: `pending_writes` is a module-level Map in server.js. Key = `req_write_id` (generated pre-LLM). No vault round-trip for pending state. Entries removed on /v1/feedback approval/rejection or on TTL expiry (prunePendingWrites). No Redis or external state needed. Simpler, faster, sufficient for single-process hub-bridge.

### Decision #20: DPO vault records use type:"log" with tags:["dpo-pair"] (2026-03-05, LOCKED)
Vault-api schema only allows types: ["fact","preference","project","artifact","log","contact"]. "dpo-pair" is not a valid type. Correct pattern: `type:"log"`, `tags:["dpo-pair"]`. buildVaultRecord() required — bare objects fail schema validation (missing type/confidence/verification/content-as-object). Always check response status after vaultPost() — fire-and-forget swallows 422 errors silently.

### Decision #21: hub-bridge lib/ files belong in build context parent, not app/ (2026-03-05, LOCKED)
Build context is `/opt/seed-vault/memory_v1/hub_bridge/` (the parent). Dockerfile COPY commands are relative to this parent. `COPY lib/ ./lib/` requires `lib/feedback.js` at `/opt/seed-vault/memory_v1/hub_bridge/lib/` — NOT under `app/`. Must `mkdir -p` this directory first, then `cp`. Easy to get wrong because server.js lives under `app/`.

**Last updated:** 2026-03-09T23:00:00Z (Session 70 — system prompt trim + cron fix + FalkorDB catchup)

### Session 70 Accomplishments (2026-03-09)
- System prompt trimmed: 16,519 → 11,674 chars (-29%) — reduces per-request input from 67K → 57K chars, fixes recurring 429s
- "Resurrection spine" language banned in system prompt — old design doc artifact, not live behavior
- Context lag explained: "0-6h FalkorDB lag is normal and expected"
- **CRON BUG FIXED**: vault-neo crontab was using Graphiti mode (no --skip-dedup). Graphiti silently fails at scale: watermark advances, 0 FalkorDB nodes created, no error in logs. Fixed: `--skip-dedup` added permanently to cron.
- Manual FalkorDB catchup: reset watermark to 4100, ran --skip-dedup: 118 entries, 0 errors, 879 eps/s. March 5+9 entries now in FalkorDB.
- **Thumbs up/down UI feature**: brainstorming started (not complete) — DRL article connection noted, session ended before code exploration.

### Next Session Agenda (Session 71)
1. **Thumbs up/down UI feature**: Resume brainstorming — explore hub-bridge/app/server.js for existing /v1/feedback + unified.html for current UI state. Then writing-plans → implement.

**Last updated:** 2026-03-05T21:30:00Z (Session 68 — v9 Phase 4 complete)

### Decision #22: MENTIONS co-occurrence replaces stale RELATES_TO (2026-03-10, LOCKED)
RELATES_TO edges (1,423) are permanently frozen at 2026-03-04 — all from Chrome extension + Graphiti dedup era.
--skip-dedup mode (active since Session 59) never creates RELATES_TO; only creates MENTIONS.
query_relevant_relationships() now uses Episodic→Entity MENTIONS co-occurrence cross-join, cocount >= 2.
Live data: Karma/Colby=123, Karma/User=100, User/Universal AI Memory=44. 11/11 TDD tests GREEN.

### Decision #23: Confidence level tags mandatory in system prompt (2026-03-10, LOCKED)
[HIGH]/[MEDIUM]/[LOW] tags on all technical claims. [HIGH] = verified in current context this session.
[MEDIUM] = reasonable inference from pattern/adjacent evidence. [LOW] = unverified.
Placement: on specific claims only, not every sentence. Reserve [HIGH] strictly — value comes from rarity.

### Decision #24: Anti-hallucination hard stop before [LOW] claims (2026-03-10, LOCKED)
Before asserting unverified API behavior, function signatures, or endpoint paths: Karma must STOP and write:
"[LOW] I haven't verified this. Should I fetch_url or graph_query to confirm first?"
Do not proceed with the unverified claim. Propose verification instead.
In standard mode: "[LOW] This isn't in my current context — you'd need to check docs or run a query via CC."

### Decision #25: Context7 rejected — DIY get_library_docs with URL map (2026-03-10, LOCKED)
Context7 free tier (1,000 calls/month) covers estimated usage (60-750/month) but adds external dependency.
Decision: build get_library_docs(library) as hub-bridge deep-mode tool using hardcoded URL map + existing fetch_url logic.
Target libraries: redis-py, falkordb, falkordb-py, fastapi. ~30min implementation. No external account required.
Status: DECIDED, not yet implemented (v10 priority #5).

### Decision #26: Universal thumbs via turn_id (2026-03-10, LOCKED)
Every Karma response now carries 👍/👎 UI regardless of write_memory presence.
/v1/feedback accepts turn_id as alternative to write_id. write_id takes priority when both present.
General quality signal + DPO pair accumulation even in standard mode.
Thumbs-down + note feeds correction pipeline. Backward compatible — existing write_memory gate unchanged.

### Session 72 Accomplishments (2026-03-10)

**v10 Priority #1: Universal Thumbs via turn_id — COMPLETE**
- hub-bridge/lib/feedback.js: processFeedback() extended with turn_id 5th param; stored in dpo_pair
- hub-bridge/app/server.js: /v1/feedback validation updated — turn_id OR write_id required; turn_id passed through
- hub-bridge/app/public/unified.html: gate changed from writeId-only to (writeId || turnId); buildFeedbackPayload sends write_id first, falls back to turn_id; all 3 signal paths send correct payload
- 4 new TDD tests (11/11 GREEN); deployed + smoke test verified {wrote:false} on turn_id-only POST
- PITFALL: All changed hub-bridge files (server.js, lib/feedback.js, app/public/unified.html) must be synced to build context — not just server.js. Session-72 caught: unified.html + feedback.js were not synced on prior deploy.

**v10 Blocker #2: Entity Relationships data quality — COMPLETE**
- ROOT CAUSE: query_relevant_relationships() queried RELATES_TO — 1,423 edges frozen at 2026-03-04 (Chrome ext era). --skip-dedup mode never creates RELATES_TO; Graphiti dedup (disabled Session 59) was sole creator.
- FIX: MENTIONS co-occurrence query — Episodic→Entity cross-join, cocount >= 2, ORDER BY cocount DESC LIMIT 20
- Relationship label format: "co-occurs in N episodes" (human-readable, not raw edge fact)
- LIVE data confirmed: Karma/Colby=123, Karma/User=100, User/Universal AI Memory=44
- TDD: 2 new tests (test_query_relevant_relationships_uses_mentions_not_relates_to, test_query_relevant_relationships_formats_cooccurrence_label); 11/11 GREEN
- Deployed: git pull → cp server.py to build context → --no-cache rebuild → docker compose up -d → RestartCount=0

**v10 Priority #3+#4: Confidence Levels + Anti-Hallucination Gate — COMPLETE**
- Added "Confidence Levels — Mandatory for Technical Claims" section to Memory/00-karma-system-prompt-live.md
- [HIGH]/[MEDIUM]/[LOW] tag definitions + placement rule + calibration rules
- Anti-hallucination gate: hard stop + propose verification before proceeding with [LOW] claims
- KARMA_IDENTITY_PROMPT: 12,524 → 14,601 chars
- Deployed via docker restart anr-hub-bridge (no rebuild needed); acceptance tests: [LOW] on unverified redis-py signature; [HIGH] on known system facts — both passed
- Covers v10 priority #3 (confidence levels) AND #4 (anti-hallucination pre-check) in single section

**v10 Context Blindness Fix (Session 72 Root Bug)**
- ROOT CAUSE: buildSystemText() had no path for MEMORY.md injection — Karma never saw MEMORY.md content
- FIX: _memoryMdCache module-level cache (tail 3000 chars), loaded at startup + refreshed every 5min
- Injected as "--- KARMA MEMORY SPINE (recent) ---" section in buildSystemText()
- hub-bridge now auto-injects last 3000 chars of MEMORY.md into every /v1/chat request
- 6/6 TDD tests (test_system_text.js) GREEN; deployed + verified Karma can see v10 plan details

### Decision #28: claude-3-5-haiku-20241022 as primary model (2026-03-10, SUPERSEDED by #29)
Previously set as primary in Session 75. Model was already RETIRED as of 2026-02-19 — this was an error.

### Decision #29: claude-haiku-4-5-20251001 as primary model (2026-03-10, LOCKED)
haiku-20241022 RETIRED 2026-02-19 — was producing `Error: internal_error` in Karma UI.
Official Anthropic replacement: claude-haiku-4-5-20251001 (Active, retirement not before Oct 2026).
MODEL_DEFAULT=claude-haiku-4-5-20251001, MODEL_DEEP=claude-haiku-4-5-20251001. Pricing: $1.00/$5.00 per 1M.
routing.js ALLOWED_DEFAULT_MODELS + ALLOWED_DEEP_MODELS updated. hub.env on vault-neo updated. Container rebuilt --no-cache.
Verified: `model: claude-haiku-4-5-20251001, debug_provider: anthropic` in live API response.

### Decision #30: Cognitive Architecture Layer is the next major milestone (2026-03-10, LOCKED)
Colby identified that Karma's original purpose was cognitive architecture — never built. 75+ sessions of plumbing without the core layer. Three missing components:
- **Self-Model Kernel**: A dynamic, per-request phase where Karma maintains an explicit model of herself (capabilities, current state, recent patterns) — NOT the static system prompt.
- **Metacognitive Trace**: Real-time capture of Karma's reasoning about her own reasoning — WHY she said what she said, what alternatives she considered, confidence trajectory. The consciousness loop was supposed to be this. It stalled at OBSERVE-only.
- **Deferred Intent Engine**: A mechanism to carry forward behavioral intentions across turns and sessions. "When X comes up, also do Y." "Next session: remember to mention Z." Not approval-gating (that's write_memory) — intent scheduling.
These three together form the Cognitive Architecture Layer — what makes Karma cognizant rather than merely contextually rich. This is Milestone 8.

### Session 74 Accomplishments (2026-03-10) — v11 Karma Full Read Access
- get_vault_file extended: repo/<path> + vault/<path> prefixes + traversal protection (path.resolve + startsWith)
- /opt/seed-vault:/karma/vault:ro volume mount added to compose.hub.yml
- get_local_file(path) tool: hub-bridge calls PowerShell HTTP server on Payback (Tailscale 100.124.194.102:7771)
- karma-file-server.ps1: PowerShell HttpListener, bearer token auth, 40KB cap, traversal protection
- KarmaFileServer Windows Task Scheduler task registered (always-on, AtBoot+AtLogon)
- System prompt updated: repo/<path> + vault/<path> + get_local_file concrete examples (16,511 chars)
- 7/7 end-to-end tests passed; all 8 plan tasks complete

### Session 75 Accomplishments (2026-03-10) — Model Switch to Haiku 3.5
- Diagnosed: DPO pairs ARE working (log evidence); prior "0 pairs" was outdated
- MODEL_DEFAULT + MODEL_DEEP switched from GLM/gpt-4o-mini → claude-3-5-haiku-20241022
- routing.js: updated ALLOWED_DEFAULT_MODELS + ALLOWED_DEEP_MODELS + default constants (Decision #28)
- hub.env on vault-neo: MODEL_DEFAULT + MODEL_DEEP updated; PRICE_CLAUDE updated to Haiku rates
- lib/*.js (feedback.js, routing.js, pricing.js, library_docs.js) committed to git — were missing from repo
- Container rebuilt --no-cache and deployed; RestartCount=0; env verified inside container
- Acknowledged root failure: backend-only verification declared as "green" without UX testing

### Session 84 Accomplishments (2026-03-11)
- MANDATORY K2 state-write protocol added to system prompt: Karma must call aria_local_call after DECISION/PROOF/PITFALL/DIRECTION/INSIGHT (Session 84b)
- K2 redundancy cache built: sync-from-vault.sh pull/push/status, 6h pull cron, 1h push cron, aria.service starts with identity cached (Session 84c)
- /health endpoint added to aria.py on K2 — returns vault_reachable, cache_age_hours, last_sync (Session 84c)
- vault-neo public key added to K2 authorized_keys; reverse tunnel verified: karma@localhost:2223 → K2:22 (Session 84d)
- shell_run tool added to hub-bridge TOOL_DEFINITIONS + handler: calls K2:7890/api/exec (Session 84d)
- /api/exec endpoint added to aria.py: subprocess.run gated by X-Aria-Service-Key, 30s timeout (Session 84d)
- hub-bridge v2.11.0 deployed, RestartCount=0 (Session 84d)
- Decision #34: shell_run routes through aria /api/exec, not direct SSH (locked Session 84d)

### Session 85 (2026-03-12) — Emergency Fix: Karma Broken Memory + System Prompt
- EMERGENCY: Karma forgot most of week, couldn't use tools (fetch_url), contradictory system prompt
- ROOT CAUSES (5): tools contradiction line 254, MEMORY_MD_TAIL slashed to 800, K2 query hardcoded "Colby", scratchpad/shadow not wired, accumulated drift
- System prompt: removed tools contradiction, added K2 ownership directive, updated tool list, eliminated "deep-mode only" confusion
- server.js: MEMORY_MD_TAIL_CHARS 800→2000, fetchK2MemoryGraph("Colby")→fetchK2MemoryGraph(userMessage)
- NEW: fetchK2WorkingMemory() — reads scratchpad.md + shadow.md via /api/exec, injected as 8th param to buildSystemText
- BUGFIX: /api/exec returns {ok:true} not {success:true} — fetchK2WorkingMemory initially checked wrong field
- VERIFIED: K2 working memory 4015 chars loaded, K2 memory graph 1200 chars/3 hits, fetch_url working, shell_run working
- Decision #35: K2 is Karma's resource — delegate heavy work (browse/code/compute) to K2, Anthropic model = persona only
- Claude-mem observations: #5325 (root causes), #5326 (plan), #5337 (bugfix), #5338 (verification)

## Next Session Starts Here

1. **Fix Karma regression** — She's still giving status dumps instead of acting from the operational table. The prompt update wasn't enough. Investigate: is the updated system prompt actually loaded? Check docker logs for prompt length.
2. **Karma↔CC behavioral test** — Have Karma POST to CC via coordination_post. CC reads and responds. First real exchange without Colby relaying.
3. **If JSON truncation recurs** — Increase HUB_MAX_OUTPUT_TOKENS_DEFAULT from 3000 to 4096 in hub.env.

**Blocker:** Karma regression — if she can't act from the operational table, the coordination loop won't work because she'll keep re-deriving instead of using coordination_post.

### Decision #31: "Aria" unified into Karma — one peer, two compute paths (2026-03-11, LOCKED)
"Aria" was a working name for K2's local Karma instance built in isolation. Confirmed by Colby: no separate entity. One peer (Karma), two compute paths: cloud (vault-neo + Anthropic API) and local (K2 + qwen3-coder:30b). One memory spine. All code built for "Aria" on K2 is Karma's local half. aria_local_call = Karma calling herself on local hardware.

### Decision #32: MODEL_DEEP = claude-sonnet-4-6 (2026-03-11, LOCKED)
MODEL_DEFAULT stays claude-haiku-4-5-20251001 (cheap, fast, standard queries).
MODEL_DEEP changed to claude-sonnet-4-6 (stronger reasoning, peer-quality conversation, better tool-calling).
hub.env updated on vault-neo. routing.js allow-list must be verified to include claude-sonnet-4-6.

### Decision #33: Subscription cleanup — target $30-35/mo (2026-03-11, LOCKED)
Cut (auto-top-up disabled): GLM/z.ai, MiniMax, Perplexity API, Groq, Twilio, Postmark.
Keep: DigitalOcean ($24), Anthropic API (~$5-15), OpenAI API (<$1 embeddings), Brave Search, Cloudflare, Porkbun.
Evaluate: OpenRouter (unified model API, could replace direct Anthropic+OpenAI), Google Workspace (user doesn't use it — Cloudflare email routing is free alternative).

### Session 81 Accomplishments (2026-03-11)
- Context amnesia root cause diagnosed from KarmaSession031026a.md: MAX_SESSION_TURNS=8 (deployed Session 80)
- File upload fix deployed and verified: KarmaSession031026a.md successfully uploaded and analyzed by Karma
- vault-neo → K2 Tailscale confirmed: Ollama at :11434, Aria/Karma-local service at :7890 both operational
- qwen3-coder:30b confirmed MoE architecture: ~3.3B active per token, ~0.26s warm latency
- ARCHITECTURAL CLARITY: "Aria" = Karma's local compute half. Not a separate entity.
- MODEL_DEEP switched to claude-sonnet-4-6 in hub.env
- Subscription cleanup plan established — 6 services cut, target $30-35/mo
- PITFALL: `cp -r source/ dest/` does not overwrite existing files — always explicit file copy for individual files

### Session 81 Complete Accomplishments (2026-03-11)
- Context amnesia root cause diagnosed: MAX_SESSION_TURNS=8 (Session 80 deploy)
- File upload button fixed and verified: cp -r pitfall documented
- vault-neo → K2 Tailscale confirmed: Ollama :11434, Aria :7890 both operational
- qwen3-coder:30b: confirmed MoE ~3.3B active/token, ~0.26s warm latency
- ARCH CLARITY: "Aria" = Karma's local compute half (not separate entity)
- MODEL_DEEP=claude-sonnet-4-6 deployed + verified ($0.0252/req, cites episode IDs)
- routing.js ALLOWED_DEEP_MODELS updated to include claude-sonnet-4-6
- Monthly cap raised to $60 in hub.env; compose up -d to apply
- Subscription cleanup: 6 services cut (GLM, MiniMax, Perplexity API, Groq, Twilio, Postmark)
- Thumbs ✓ saved UI confirmation deployed
- Codex Aria API inventory complete: 80 endpoints, memory subsystems, auth paths documented
- X-Aria-Delegated header removed from aria_local_call — Aria now writes observations
- Aria → vault-neo sync: observations POST to /v1/ambient after each chat call
- session_id threading wired: UUID per page load → coherent Aria conversation thread
- Decisions #29-#33 locked and promoted to 02-stable-decisions.md

## Next Session Starts Here

### 🔴 PRIORITY #1: Conversation Thread Persistence (EMERGENCY)
Karma lost an entire conversation mid-session (2026-03-12 ~12:03 PM) after an `internal_error` killed one API call. Browser JS conversation array was wiped. Karma introduced herself fresh — zero recall of the thread about PDF processing, directory questions, etc.

**Root cause:** No server-side conversation storage. Thread lives only in `unified.html` JS array.
**Evidence:** Vault ledger has ALL turns (`[hub,chat,default]` entries with user_message + assistant_text) but no mechanism to reload them into a conversation.
**Impact:** Everything else is useless if Karma forgets mid-conversation. Colby's words: "Session continuity is supposed to be constant!?!"

**Fix needed:**
1. Server-side conversation storage keyed by session_id (already exists — `window.karmaSessionId` UUID per page load)
2. On error/reconnect, client requests conversation history from server
3. Server returns stored turns, client rebuilds conversation array
4. K2 MCP Phase 3 is **PAUSED** until this is fixed.

### Other items (PAUSED pending conversation persistence fix)
- K2 MCP Phase 3: dynamic tool discovery at hub-bridge startup
- Prompt caching (Anthropic ephemeral cache_control)
- Colby has a PDF to share — waiting after doc updates

**Active models:** MODEL_DEFAULT=claude-haiku-4-5-20251001, MODEL_DEEP=claude-sonnet-4-6 (both LIVE)
**hub-bridge:** v2.11.0, RestartCount=0, 2026-03-12
**K2 tools:** 9 k2_* structured tools LIVE via /api/tools/execute
