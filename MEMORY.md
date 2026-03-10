## Phase 4 Task 9 — Deferred Intent Engine deployed to vault-neo (2026-03-10)

**Status:** ✅ LIVE — Full acceptance test passed. hub-bridge v2.11.0.

### Deployment result
- `deferred_intent.js` + `server.js` synced to build context, `--no-cache` rebuild succeeded
- Startup: `[INTENT] Loaded 0 active intents from ledger` (correct — fresh deploy)
- Acceptance test 1 (propose): `intent_id: int_1773184629042_2hjg5g`, `ok: true`
- Acceptance test 2 (approve): `{"ok":true,"signal":"up","intent_id":"...","approved":true}`
- Acceptance test 3 (trigger): redis-py question surfaced intent; Karma showed verification behavior with [LOW] confidence signal
- STATE.md updated: Deferred Intent Engine row added

---

## Phase 4 Task 5 — defer_intent tool added (2026-03-10)

**Status:** ✅ COMPLETE — `defer_intent` tool added to TOOL_DEFINITIONS and executeToolCall handler in hub-bridge/app/server.js. Syntax clean (node --check). Pending commit.

- TOOL_DEFINITIONS entry added after get_library_docs
- Handler added before write_memory in executeToolCall — validates fields, creates int_ prefixed ID, stores in pending_intents Map
- Approval gated via /v1/feedback with intent_id (same pattern as write_memory/write_id)

---

## Session 77 — Cognitive Architecture Layer design (2026-03-10)

**Status:** ✅ DESIGN COMPLETE — `docs/plans/2026-03-10-cognitive-architecture-design.md` committed

### What was designed
Three-component Cognitive Architecture Layer (Milestone 8, Decision #30):
- **Self-Model Kernel**: `buildSelfModelSnapshot()` in hub-bridge, injected in `buildSystemText()`. Pure observational data: tools available, claim calibration, RPM state, unapproved writes, active/pending intents, detected patterns. Coaching in system prompt (threshold rules). `get_self_model()` deep-mode tool for live verification.
- **Metacognitive Trace**: `capture_trace()` outbound tool, async write to consciousness.jsonl, observability logging. Trace schema: turn_id, topic, confidence_used, alternatives_considered (0-5 cap), tool_called, tool_changed_answer, pre/post tool confidence, write_memory_proposed. Phase 2b: consciousness loop rule-based pattern detection (confidence drift, tool effectiveness, memory cluster).
- **Deferred Intent Engine**: `defer_intent()` + `get_active_intents()` tools. Storage: vault ledger type:"log" tags:["deferred-intent"]. Fire modes: once, once_per_conversation, recurring. Karma-created: approval gate (same as write_memory). Colby-created: direct. Tag-based trigger matching in karmaCtx. Phase 2b: trace-to-intent loop (consciousness-proposed intents).

### Implementation order (Approach B: Kernel-first)
Phase 1 → Phase 2 → Phase 2b → Phase 3 → Phase 4 → Future (trace-to-intent)

### Session-end protocol addition needed
CLAUDE.md: add "review pending intent proposals" alongside "review pending writes" in checklist.

### Next step
Invoke `superpowers:writing-plans` to create implementation plan for Phase 1.

---

## Session 76 — Emergency: migrate to claude-haiku-4-5-20251001 (2026-03-10)

**Status:** ✅ COMPLETE

### What changed
- `claude-3-5-haiku-20241022` was RETIRED 2026-02-19 — was causing `Error: internal_error` in Karma UI
- `routing.js`: `ALLOWED_DEFAULT_MODELS` + `ALLOWED_DEEP_MODELS` updated; defaults → `claude-haiku-4-5-20251001` (Decision #29)
- `hub.env` on vault-neo: MODEL_DEFAULT + MODEL_DEEP → `claude-haiku-4-5-20251001`, pricing $1.00/$5.00
- Container rebuilt `--no-cache`, deployed. Verified: `model: claude-haiku-4-5-20251001, debug_provider: anthropic`
- **Revelation (Decision #30)**: Karma was always supposed to have a Cognitive Architecture Layer — never built. Self-Model Kernel + Metacognitive Trace + Deferred Intent Engine. Documented in STATE.md + ROADMAP.md Milestone 8. This is the next major milestone.

### System state
- Hub Bridge: ✅ claude-haiku-4-5-20251001 live, RestartCount=0
- All other containers: ✅ unchanged

---

## Session 75 — Switch Karma primary model to Claude Haiku 3.5 (2026-03-10)

**Status:** ✅ COMPLETE — Haiku 3.5 live, container healthy

### What changed
- `MODEL_DEFAULT` + `MODEL_DEEP`: `glm-4.7-flash`/`gpt-4o-mini` → `claude-3-5-haiku-20241022` (both)
- `hub-bridge/lib/routing.js`: updated `ALLOWED_DEFAULT_MODELS`, `ALLOWED_DEEP_MODELS`, default constants (Decision #28)
- `hub.env` on vault-neo: MODEL_DEFAULT + MODEL_DEEP updated; `PRICE_CLAUDE_INPUT_PER_1M=0.80`, `OUTPUT=4.00`
- `hub-bridge/lib/*.js` (all 4 files) committed to git — were missing from repo, only in build context
- Container rebuilt `--no-cache` and deployed; `RestartCount=0`; verified via `docker exec env | grep MODEL`

### DPO diagnosis (resolved)
- DPO pairs ARE being written — logs confirmed: `[FEEDBACK] DPO pair stored: signal=up`
- Previous "0 pairs" claim was outdated/unverified. Feedback pipeline is functional.

### Verified system state (2026-03-10)

| Component | Status |
|-----------|--------|
| Hub Bridge | ✅ Running — claude-3-5-haiku-20241022 for both standard + deep mode |
| DPO feedback | ✅ Working — pairs confirmed in logs |
| lib/*.js in git | ✅ Fixed — all 4 files committed (34b7326) |
| v11 read access | ✅ Live from Session 74 |
| FalkorDB | ✅ 3877+ nodes, cron every 6h |

### Next session
1. Chat with Karma at hub.arknexus.net — confirm sidebar shows claude-3-5-haiku-20241022
2. Click 👍 on a response — confirm DPO pair in ledger (search tags:["dpo-pair"])
3. Before any hub-bridge rebuild: sync `hub-bridge/lib/*.js` to `/opt/seed-vault/memory_v1/hub_bridge/lib/`

## Session 74 — v11 Karma Full Read Access COMPLETE (2026-03-10)

**Status:** ✅ ALL 8 TASKS DONE — 7/7 end-to-end tests passed

### What was built
- `get_vault_file` extended: `repo/<path>` (→/karma/repo) + `vault/<path>` (→/karma/vault) prefixes, traversal protection, backward compat with 9 existing aliases
- `/opt/seed-vault:/karma/vault:ro` volume mount added to compose.hub.yml
- `get_local_file(path)` tool added: hub-bridge calls Payback file server via Tailscale 100.124.194.102:7771
- `Scripts/karma-file-server.ps1`: PowerShell HTTP server on port 7771, bearer token auth, 40KB cap, traversal protection
- `Scripts/generate-file-token.ps1`: one-time token generator
- `KarmaFileServer` Windows Task Scheduler task: always-on, StopIfGoingOnBatteries=false, 9999 restart attempts
- URL ACL registered: `http://+:7771/`
- System prompt updated: complete tool docs for all three access patterns

### Commits (in order)
- `245b3e5` — compose vault mount
- `d28684b` — get_vault_file extension
- `a9eae3c` — import style fixes
- `7bb0e9b` — file server scripts
- `1656d86` — task registration scripts
- `5ec17a3` — get_local_file tool
- `40316e5` — system prompt unblock
- `88a6eba` — system prompt complete

### Key pitfalls discovered
1. System prompt blocking instruction silently defeats new tools — positive action must be PRIMARY, not an exception clause
2. `nodePath.default.resolve` is ESM fragile — both fs and path were already top-level imports
3. `docker compose up -d` required (not restart) to pick up new hub.env vars and volume mounts

### claude-mem observations saved: #4648, #4649, #4650, #4651

## Session 73 — v11 Task 6: system prompt tool docs completed (2026-03-10)

**What changed:** Memory/00-karma-system-prompt-live.md — complete tool documentation for v11 access patterns
- get_vault_file: added repo/<path> and vault/<path> prefix documentation + path traversal blocked note + cc-brief alias
- get_local_file: added concrete path examples + promoted out of trailing exception clause
- Deep mode tool list (line 26): added get_local_file to the tool list (was missing)
- Blocking instruction rewritten: "use get_local_file" is now the primary instruction for Karma_SADE reads; "I can't do that" only for shell/browser/arbitrary paths
- No code changes, no rebuild needed — docker restart anr-hub-bridge sufficient

## Session 73 — v11 Task 5: get_local_file tool added (2026-03-10)

**What changed:** hub-bridge/app/server.js — added `get_local_file` tool
- New env vars: `LOCAL_FILE_SERVER_URL`, `LOCAL_FILE_TOKEN` read at startup
- New TOOL_DEFINITION for `get_local_file` (after get_vault_file in array)
- New handler in executeToolCall: calls Payback file server at LOCAL_FILE_SERVER_URL via Bearer auth
- Handler guards: empty path, missing config, HTTP errors, fetch errors, 10s timeout
- buildSystemText tool list updated to include get_local_file(path)
- Active tools comment updated (line ~796)
- File server URL: http://100.124.194.102:7771 (Tailscale IP for Payback)
- hub.env on vault-neo: LOCAL_FILE_SERVER_URL + LOCAL_FILE_TOKEN appended

## Session 73 — Code quality fix: get_vault_file handler (2026-03-10)

**What changed:** hub-bridge/app/server.js — get_vault_file import cleanup
- Removed redundant `await import("fs")` and `await import("path")` (both top-level at lines 2-3)
- Replaced `nodePath.default.resolve()` with top-level `path.resolve()`
- Replaced `readFileSync()` with `fs.readFileSync()` using top-level import
- Added empty alias guard: `if (!alias) return { error: "missing_alias", ... }`
- Added comment above traversal check re: normalize behavior of resolve()

## Session 73 (2026-03-10) — v11 Task 1: vault volume mount

**Active task:** v11 Full Read Access — Task 1 COMPLETE
- Added `/opt/seed-vault:/karma/vault:ro` volume mount to `hub-bridge/compose.hub.yml`
- Positioned between `/karma/repo:ro` and `/karma/ledger:rw` as required
- Committed to main, syncing to vault-neo build context

## Session 71 continued (2026-03-10) — v10 snapshot created

**v10 snapshot (COMPLETE + cross-validated):** Created `Current_Plan/v10/` with 10 files. Cross-validated against Karma's own PDF analysis — added 6 missed primitives: Path-Based Rules, Multi-Agent Brainstorm, Hooks>LLMs for deterministic tasks (CCintoanOS); Plans as Files, YOLO Mode security honesty, MCP CLI-progressive (PiMonoCoder). direction.md now has 16 total primitives. v10 priority order: universal thumbs → Entity Relationships fix → confidence levels + anti-hallucination → Context7 MCP → hooks>LLMs for correction capture.

## Session 71 (2026-03-10) — Universal thumbs + Recurring Topics coaching fix

**Thumbs (COMPLETE):** Extended `/v1/feedback` + `processFeedback()` + `unified.html` to show thumbs on ALL Karma messages via `turn_id` fallback. 11/11 tests pass. Deployed.

**Deep mode toggle (COMPLETE):** Added DEEP button to unified.html input bar — toggles purple when active, sends `x-karma-deep: true` header. Static file, no rebuild needed.

**Persona coaching (COMPLETE):**
- Diagnosed: Recurring Topics coaching was abstract ("invisibly raise your floor") — no trigger, no behavior
- Fixed: Rewrote `Memory/00-karma-system-prompt-live.md` Recurring Topics section with concrete trigger→action pattern (matches Recently Learned style)
- Verified: behavior change confirmed — Karma now acknowledges recurring topics explicitly
- Entity Relationships: data is stale (all Chrome extension edges) — separate investigation needed

## Session 70 (2026-03-09) — FalkorDB catchup + cron fix + resurrection spine ban

**Active task:** COMPLETE
1. Root cause: cron was using Graphiti mode (no --skip-dedup) → silently failing at scale → 0 new nodes for March 5-9 entries despite watermark advancing
2. Fix: added --skip-dedup to vault-neo crontab; reset watermark to 4100; manual run: 118 entries, 0 errors, 879 eps/s
3. Verified: 76 March-5 nodes + March-9 nodes now in FalkorDB
4. System prompt: added explicit "resurrection spine" ban + context lag explanation (0-6h lag is normal)
5. **PITFALL**: Graphiti mode silently fails for incremental ingest at scale. --skip-dedup MUST be in cron.

## Session 70 (2026-03-05) — System prompt trim to fix 429 rate limits

**Active task:** COMPLETE
1. System prompt trimmed: 16,519 → 11,674 chars (−29%) — reduces TPM per request, fixes recurring 429s
2. Removed: API Surface table, 3 low-value corrections (#1 verdict.txt, #2 batch_ingest direction, #5 consciousness loop), infrastructure container list, machine specs, verbose coaching
3. Preserved exactly: session continuity mechanism, Recently Learned priority rules, tool routing, all critical corrections, ASSIMILATE/DEFER/DISCARD, Behavioral Contract

## Session 69 post-wrap #3 (2026-03-05) — primitives context priority + FalkorDB schema

**Active task:** COMPLETE
1. "Recently Learned" priority rule: read block FIRST, never skip to "run this query yourself"
2. Correction #8: FalkorDB Episodic real fields — e.source/e.title/e.timestamp do NOT exist

## Session 69 post-wrap #2 (2026-03-05) — SIGNAL_REGEX + primitives coaching

**Active task:** COMPLETE
1. SIGNAL_REGEX: `/^\[...\]$/m` → `/\[...\]/` — multi-line synthesis no longer silently dropped. 44 canonical primitives confirmed in FalkorDB.
2. System prompt: duplicate `---` removed, "How You Improve Over Time" rewritten (identity.json analogy gone), primitives coaching added ("Recently Learned" = primitive list)
3. Corrections log: 4 new entries appended

## Session 69 post-wrap (2026-03-05) — Karma Self-Model Corrections

**Active task:** COMPLETE — no blockers
**What changed:** 3 additional system prompt corrections based on live Karma analysis:
1. fetch_url capability: "cannot browse URLs" bullet corrected — she can in deep mode w/ user-provided URLs
2. K2 deprecated: explicit correction added — K2 is not running, not a sync worker
3. Session continuity: added "How Session Continuity Actually Works" — no identity.json/invariants.json loading, actual mechanism is system prompt + FalkorDB karmaCtx injection per request
4. Corrections 6 & 7 added to Data Model Corrections section
**Deploy:** git pull + docker restart anr-hub-bridge (no rebuild needed)

---

## Session 67 (2026-03-05) — Security Fix: Deep-Mode Tool Gate

**Status:** ✅ COMPLETE (2 deployments: security fix + persona coaching)

### What Changed
1. **Security fix** (commit 41b2c06): server.js line 1271 — gate tool-calling to deep-mode only
   - `deep_mode ? callLLMWithTools() : callLLM()` — standard GLM requests no longer get tools
2. **v9 Phase 3 persona coaching** (commit f90cea7): Memory/00-karma-system-prompt-live.md
   - Fixed stale tool list: read_file/write_file → graph_query/get_vault_file
   - New section "## How to Use Your Context Data": Entity Relationships, Recurring Topics, deep-mode graph_query rules
   - KARMA_IDENTITY_PROMPT: 10415 → 11850 chars

### Session 67 Extended — v9 Phase 4 Design Finalized

**v9 Phase 4: Karma Write Agency** (design complete, not yet implemented)
- Karma gets write tools: `write_memory(content)`, `annotate_entity(name, note)`, `flag_pattern(description)`
- Write gate: thumbs up/down in web UI gates whether Karma's proposed memory note actually lands
- Optional text box: 👍 + text → write user's phrasing instead of Karma's; 👎 + text → corrections-log.md
- Three-in-one: write gate + DPO preference pairs + corrections pipeline
- API: `POST /v1/feedback {turn_id, rating: +1/-1, note?: string}` — turn_id already in every /v1/chat response
- Web UI: thumbs up/down already present at hub.arknexus.net, text box already opens on click
- Safe target: PATCH /v1/vault-file/MEMORY.md (append-only, auditable)
- obs #4032 saved

**Also confirmed during Session 67 analysis:**
- karma-server router.py is dead code (karma-terminal stale since 2026-02-27; spend = $0.12/month)
- Groq swap: not worth it — router is unused, Graphiti uses OpenAI directly (cannot swap without rewrite)
- ANALYSIS_MODEL config bug (defaults to glm-4.7-flash but OpenAI provider at api.openai.com): non-impactful

### Session 68 — v9 Phase 4 Design + Acceptance Test + karma-verify Fix

**Acceptance test (v9 Phase 3):** PASSED — Karma referenced entity relationship data unprompted when asked about Claude Code usage. Said "That's what I see in my graph" — explicit graph attribution. Persona coaching confirmed working.

**karma-verify fix:** SKILL.md updated — smoke test now checks `assistant_text` instead of `reply` (was false FAILED on healthy service).

**v9 Phase 4 design (Session 68 brainstorm):**
- Scope reduced: `write_memory` only (annotate_entity/flag_pattern deferred)
- Gate: in-process `pending_writes` Map (Approach A — no vault round-trip)
- Optional note: inline textarea after 👎 click in unified.html (~15 lines)
- DPO storage: ledger via /v1/ambient with `dpo-pair` tag
- Design doc: `docs/plans/2026-03-05-v9-phase4-write-memory-design.md`
- Files to change: server.js (pending_writes Map + write_memory tool + /v1/feedback endpoint), unified.html (textarea), hooks.py (ALLOWED_TOOLS), 00-karma-system-prompt-live.md (coaching paragraph)

### Session 68 Implementation Progress

**v9 Phase 4 implementation — Tasks 1-3 complete (server.js):**
- Task 1: `hub-bridge/lib/feedback.js` — prunePendingWrites + processFeedback, 7 tests green (commit a17ce54)
- Task 2: `write_memory` tool — pending_writes Map + tool def + writeId threading (commits 57ce894, 268bd08)
- Task 3: `POST /v1/feedback` endpoint — auth + processFeedback + MEMORY.md fs.appendFileSync + DPO ledger (commits fe8a3b8, 722c05a, fix)
- **Active task:** Task 4 — update karma-core/hooks.py ALLOWED_TOOLS ✅ DONE (commit pending)
- Task 4: Added `"write_memory"` to ALLOWED_TOOLS in karma-core/hooks.py

### Session 68 Continued — Tasks 5-7 Complete

**Task 5:** ✅ 00-karma-system-prompt-live.md updated — write_memory coaching paragraph added. Deployed: git push → vault-neo git pull → docker restart anr-hub-bridge → karma-server rebuilt.

**Task 6:** ✅ (see prior session notes)

**Acceptance test hotfix:** DPO vault record used bare object — failed vault schema (missing type/confidence/verification, content must be object). Fixed: switched to `buildVaultRecord()` in /v1/feedback endpoint. Redeploy required.

**Task 7:** ✅ unified.html updated — write_id in feedback POSTs + inline textarea after 👎
- `handleMessage` now reads `data.write_id` (from server response field `write_id: proposed_write_id`)
- `addMessage(role, content, writeId)` — stores `writeId` in `wrap.dataset.writeId`
- `sendFeedback(writeId, signal, btnEl, msgWrap)` — 👍 POSTs `{write_id, signal}` immediately; 👎 injects `.feedback-note` div with textarea + submit button
- Submit POSTs `{write_id, signal: "down", note?: ...}` then collapses the div
- Feedback-note div ID: `fn-{writeId}` (or `fn-unknown` if write_id is null)
- CSS added: `.feedback-note`, `.feedback-note textarea`, `.feedback-note button`

### Task 7 Quality Fixes Applied (code review pass)
Three bugs fixed in unified.html (feedback buttons, stale token, double-submit guard):
1. Feedback buttons only rendered when `writeId` is truthy — no more 400s in standard mode
2. Submit onclick calls `getToken()` fresh — not captured in outer closure
3. `this.disabled = true` at start of Submit onclick — double-submit guard

### Session 68 Final — v9 Phase 4 ALL TASKS COMPLETE

**Task 8:** ✅ system prompt coaching — write_memory paragraph added to `## How to Use Your Context Data` (commit 6f078e7). KARMA_IDENTITY_PROMPT: 11850 → 12366 chars.

**Task 9:** ✅ hub-bridge redeployed with all v9 Phase 4 changes (server.js + lib/feedback.js + unified.html). Key pitfall: `lib/feedback.js` must be synced to `/opt/seed-vault/memory_v1/hub_bridge/lib/` (parent build context), not `/app/lib/`.

**Task 10:** ✅ End-to-end acceptance test PASSED (all 5 tests green):
1. Standard mode: no write_id returned ✅
2. Deep mode: write_id returned (e.g., wr_1772744647526_0azpyz) ✅
3. Thumbs-up: `{ok:true, wrote:true}` → MEMORY.md contains `[KARMA-WRITE]` line ✅
4. Thumbs-down: `{ok:true, wrote:false}` → MEMORY.md unchanged ✅
5. DPO pairs in ledger: `type:"log", tags:["dpo-pair"]` (ledger 4118→4119) ✅

**DPO bug fixes (2 iterations):**
- Fix 1 (69f061b): bare object → `buildVaultRecord()` — vault schema requires type/confidence/verification/content as object
- Fix 2 (cf63957): `type:"dpo-pair"` → `type:"log"` — vault only accepts ["fact","preference","project","artifact","log","contact"]. Added status check (`dpResult.status >= 300 → throw`).

**v9 Phase 4 complete.** All commits on main.

### Session 69 — fetch_url Tool + Stale Tool Cleanup

**v9 Phase 5:** ✅ MENTIONS edges verified — 2,363 in neo_workspace (healthy/growing)

**fetch_url tool (v9 Phase 5b):** ✅ LIVE — hub-bridge v2.11.0
- Handles `fetch_url(url)` in executeToolCall before proxy fallthrough (same as get_vault_file)
- Strips HTML (script/style/tags), collapses whitespace, 8KB cap, 10s timeout
- Returns `{ok, url, content, chars}` or `{error, message, url}`
- Only for URLs explicitly provided by user — coaching added to system prompt

**Stale tool cleanup:** ✅ Removed `read_file`, `write_file`, `edit_file`, `bash` from TOOL_DEFINITIONS — these had no handler, proxied to karma-server (rejected), caused Karma to claim bash capabilities she didn't have.

**Active tools (deep mode):** `graph_query`, `get_vault_file`, `write_memory`, `fetch_url`

**karma-hub-deploy skill:** ✅ Fixed — compose.hub.yml path corrected to `/opt/seed-vault/memory_v1/hub_bridge/`

**Next session:** Run Phase 3 acceptance test (still PENDING from Session 67) — ask Karma about a Recurring Topic in deep mode, verify relationship data referenced unprompted. DPO accumulation: 3/20 (time-gated).

---

## Session 73 Start

**State:** v10 COMPLETE. No active task. No blockers.

**FalkorDB (verified 2026-03-10):** 3305 Episodic + 571 Entity + 1 Decision = 3877 nodes. Batch cron healthy (305 eps/s, 0 errors). MENTIONS co-occurrence live.

**DPO accumulation:** Mechanism live (Session 68). ~0/20 pairs. Grows with regular deep-mode Karma usage.

# currentDate
Today's date is 2026-03-10.

---

## Session 66 (2026-03-05) — Session Wrap-Up (Final)

**Status:** ✅ COMPLETE (10-step protocol done)

### What Changed
- STATE.md: Session 66 accomplishments, 3 new decisions (#13-#15), GLM Tool-Calling/graph_query/get_vault_file component rows, GLM_RPM_LIMIT corrected to 40
- ROADMAP.md: v9 Phase 2 (Promise Loop Fix) marked DONE, persona coaching Phase 3, quality gaps updated
- CLAUDE.md: 4 new pitfalls (hooks.py whitelist, TOOL_NAME_MAP identity passthrough, callGPTWithTools param order, docker restart vs compose up)
- architecture.md: tool-calling section added to Hub API description
- direction.md: status updated to Session 66, GLM_RPM_LIMIT updated to 40
- Memory/problems-log.md: CREATED — 4 problems from Session 66 documented with root causes
- Memory/11-session-summary-latest.md: OVERWRITTEN with Session 66 summary
- Memory/08-session-handoff.md: OVERWRITTEN with current system state + Session 67 next steps
- Memory/02-stable-decisions.md: Decisions #13-#18 appended
- Memory/04-session-learnings.md: Session 66 patterns appended
- Memory/corrections-log.md: 3 new corrections (context size, karmaCtx fetch, RPM limit)
- .gitignore: Fixed malformed .env.secrets pattern (had spaces between chars); added clean pattern
- vault MEMORY.md: "Next Session Starts Here (Session 67)" section appended via hub API

### Addendum Changes (same session)
- CLAUDE.md: +1 pitfall (gitignore malformed patterns), +1 superpowers row (karma-verify for post-deploy), Known Pitfalls moved to END of file (cache optimization)
- Memory/03-sentinel-and-health.md: fully rewritten to Docker-based monitoring (was stale Ollama/OpenWebUI)
- Memory/12-resource-inventory.json: models/containers/hub_bridge updated; Z.ai added as subscription
- Current_Plan/v9/: synced 7 canonical files

### Next Task (Session 67)
v9 Phase 3 — Persona coaching: edit Memory/00-karma-system-prompt-live.md to add behavioral guidance for Entity Relationships + Recurring Topics. Deploy: git push → vault-neo git pull → docker restart anr-hub-bridge.
- vault MEMORY.md (on droplet): Session 66 summary appended via hub API

### Why
Session 66 implemented promise loop fix + GLM tool-calling. Docs needed to reflect verified system state.

### Blockers / Next Steps
- [ ] Git pull on vault-neo to deploy doc changes
- [ ] Re-run Get-KarmaContext.ps1 to regenerate cc-session-brief.md with current vault state
- [ ] Session 67: persona coaching (teach Karma WHAT TO DO with Entity Relationships + Recurring Topics data)

---

## Session 66 (2026-03-05) — Open-Source Release Prep

**Status:** ✅ COMPLETE (done earlier in session)

### What Changed
- Repository visibility changed from PRIVATE to PUBLIC on GitHub
- README.md fully rewritten — reframed from personal desktop tool to open-source memory backbone for AI agents
- Old README preserved as README.old.md
- MIT LICENSE file added
- karma-core/.env.example created (safe config template, no secrets)
- Applying for Anthropic Claude for Open Source Program (Track 2: Ecosystem Impact)

### Why
- Claude for Open Source Program requires public repo + ecosystem impact narrative
- Old README contained personal Windows paths, desktop shortcuts, and personal framing — would fail reviewer inspection
- LICENSE required for credible open-source project

### Blockers / Next Steps
- [ ] Submit application at claude.com/contact-sales/claude-for-oss
- [ ] Polish repo structure if reviewer feedback requires it

# Universal AI Memory — Current State

## Session 65 (2026-03-05) — CLAUDE.md Rules + v9 Plan Snapshot + Fix Karma Promise Loop (Phase 1)

**Status:** ✅ IN PROGRESS — Phase 1 deployed; Phase 2 pending

### What Was Done
- Added strategic-question pre-read rule to CLAUDE.md GSD hard rules
- Added version snapshot rule to CLAUDE.md GSD hard rules
- Created `Current_Plan/v9/` snapshot (10 files)
- Ingested CreatorInfo.pdf ("The File That Made the Creator of Claude Code Go Viral" — Cherny CLAUDE.md workflow). 2/3 chunks ASSIMILATE, lane=canonical in FalkorDB.
- Integrated PDF insights into 5 docs: direction.md (external validation table), ROADMAP.md (Known Quality Gap: corrections trigger), 00-karma-system-prompt-live.md (How You Improve section), CLAUDE.md (constitution principle), REQUIREMENTS.md (systematic mistake-capture requirement)
- Re-copied all updated files to Current_Plan/v9/
- Key insight: Cherny independently validates Karma's two-tier architecture (identity.json=global, direction.md=project). Gap documented: corrections capture is session-based, not event-driven.
- **Phase 1 — Karma promise loop fix (deploy: branch fix/karma-tool-calling)**:
  - Root causes confirmed: RC1 (false tool declarations in server.js line 413), RC2 (line 868 gates tool-calling to Anthropic-only), RC3 (system prompt said 1800 chars context, actually 12,000), RC4 (GLM_RPM_LIMIT self-imposed, was 20)
  - KARMA_CTX_MAX_CHARS=12000 already in hub.env (was already fixed, plan said raise from 1200)
  - Fixed `Memory/00-karma-system-prompt-live.md`: corrected context size (1800→12,000), added tool-mode gate (standard GLM = no tools), added rate-limit honesty, removed misleading /v1/cypher "can call yourself" language
  - Added GLM_RPM_LIMIT=40 to `/opt/seed-vault/memory_v1/hub_bridge/config/hub.env`
  - Phase 2 changes (in branch, pre-deploy): server.js line 868 → callGPTWithTools (GLM now gets real tool-calling); line 413 fixed (honest tool text, no false declarations); TOOL_DEFINITIONS + graph_query + get_vault_file; TOOL_NAME_MAP simplified (identity passthrough); get_vault_file handled directly in executeToolCall via VAULT_FILE_ALIASES; karma-core/server.py: graph_query added to TOOL_DEFINITIONS + execute_tool_action handler (Cypher via get_falkor())
  - karma-core/hooks.py: graph_query + get_vault_file added to ALLOWED_TOOLS whitelist (hook was gatekeeping and rejecting new tool names — pre-existing oversight)
  - Security: docker-compose.karma.yml K2_PASSWORD moved from plaintext to ${K2_PASSWORD}; value in hub.env on vault-neo

---

## Session 64 (2026-03-04) — Entity Relationship Context (Gap 1)

**Status:** ✅ COMPLETE — Entity Relationship Context deployed and verified in production

### What Was Built
- `_pattern_cache` + `_refresh_pattern_cache()` — top-10 entities by episode count, 30min refresh
- `query_relevant_relationships()` — bulk RELATES_TO edge query using r.fact (not type(rel))
- Both wired into `build_karma_context()` + startup refresh loop
- 9 new tests, 27/28 total (1 pre-existing FalkorDB ConnectionError unrelated)
- Deployed to vault-neo. Verified: Entity Relationships (20 edges for "Karma") + Recurring Topics (Karma:357, User:315, Colby:138...) both in /raw-context response.
- Approach C: per-message edge query + 30min cached pattern query
- hub-bridge: zero changes
- One file: `karma-core/server.py`
- CRITICAL: query_entity_relationships() at line 510 exists but wrong (type(rel) not r.fact)
- New function: query_relevant_relationships(list[str]) added after line 527

### Session 64 Also
5 skills created: karma-server-deploy, karma-hub-deploy, karma-verify,
watermark-incremental-processing, falkordb-cypher → ~/.claude/skills/

### Session 63 — COMPLETE
Graphiti watermark deployed. karma-server now runs Graphiti entity extraction on new episodes.
Watermark at line 4075 in `/opt/seed-vault/memory_v1/ledger/.batch_watermark`.
- batch_ingest.py: watermark logic + Graphiti as default + 200 episode cap
- Cron: drop --skip-dedup
- Deployment requires karma-server rebuild + watermark init

### Key Discovery
Entity graph NOT growing since Session 59. --skip-dedup bypasses Graphiti entirely.
571 Entity nodes are legacy (pre-Session-59). All 3049 Episodic nodes have zero cross-session entity extraction.
Karma can recall (FAISS) but cannot reason across sessions (no Entity/relationship graph growth).

---

## Session 62 (2026-03-04) — v8 ALL PHASES COMPLETE

**Status:** ✅ COMPLETE

### Verified System State (2026-03-04)

| Component | Status |
|-----------|--------|
| Hub Bridge API | ✅ /v1/chat, /v1/ambient, /v1/context, /v1/cypher, /v1/ingest operational |
| System Prompt | ✅ ACCURATE — Memory/00-karma-system-prompt-live.md wired via KARMA_IDENTITY_PROMPT. 4/4 acceptance tests. |
| FAISS Semantic Retrieval | ✅ LIVE — fetchSemanticContext() in hub-bridge. 4073 entries. Parallel with FalkorDB context. |
| Correction Capture | ✅ LIVE — corrections-log.md + CC Session End step 2 |
| FalkorDB Graph | ✅ 3049 Episodic + 571 Entity + 1 Decision = 3621 nodes. lane=NULL backfill done (3040 nodes fixed). |
| Consciousness Loop | ✅ OBSERVE-only, 60s cycles, RestartCount: 0 |
| batch_ingest | ✅ Watermark-based Graphiti mode. Entity extraction live for new episodes. Cron: WATERMARK_PATH set, --skip-dedup removed. |
| GLM Rate Limiter | ✅ 20 RPM global. 429 on chat, waitForSlot on ingest. |
| Config Validation Gate | ✅ MODEL_DEFAULT + MODEL_DEEP allow-lists. Exit(1) on bad config. |
| PDF Watcher | ✅ Rate-limit backoff + jam notification + time-window |
| Chrome Extension | ❌ SHELVED permanently |

### v8 Key Pitfalls (new this session)
- **hub-bridge was NOT loading system prompt from file** — buildSystemText() was fully hardcoded. File existed as vault-file alias only. Fix: KARMA_IDENTITY_PROMPT loaded via fs.readFileSync at startup.
- **anr-vault-search is FAISS not ChromaDB** — all architecture docs had wrong service type. POST :8081/v1/search, not ChromaDB API. Auto-reindexes on ledger change + every 5min.
- **KARMA_IDENTITY_PROMPT path**: env var `KARMA_SYSTEM_PROMPT_PATH` defaults to `/karma/repo/Memory/00-karma-system-prompt-live.md`. File is volume-mounted read-only. Future persona changes: git pull + docker restart (no rebuild).

### v8 COMPLETE — All Phases Done (2026-03-04)

| Phase | Goal | Status |
|-------|------|--------|
| Phase 1: Fix self-knowledge | System prompt describes actual hub-bridge system | ✅ COMPLETE |
| Phase 3: Correction capture | corrections-log.md + CC session-end protocol | ✅ COMPLETE |
| Phase 2: Semantic retrieval | FAISS fetchSemanticContext() wired into hub-bridge | ✅ COMPLETE |
| Phase 4: v7 cleanup | Budget guard verified, capability gate verified, 3040 lane=NULL fixed | ✅ COMPLETE |

### Phase 4 details (2026-03-04)
- MONTHLY_USD_CAP=35.00 already in hub.env — no change needed
- x-karma-deep capability gate already in server.js — no change needed
- lane=NULL backfill: SET lane="episodic" on 3040 Episodic nodes in neo_workspace — 0 remaining

### Phase 2 details (2026-03-04)
- anr-vault-search: FAISS service (not ChromaDB), 4073 entries indexed, auto-reindex on ledger change + every 5min
- Added fetchSemanticContext() to hub-bridge — queries anr-vault-search:8081/v1/search, top-5 results
- karmaCtx + semanticCtx fetched in parallel (Promise.all), both injected into buildSystemText

### Phase 1 details (2026-03-04)
- Audited live system prompt — was Open WebUI/Ollama persona from Feb 2026
- Rewrote: accurate hub-bridge arch, Brave Search, FAISS semantic memory, 5 data model corrections
- Wired KARMA_IDENTITY_PROMPT into hub-bridge buildSystemText() (was NOT being loaded before)
- Brave Search: BSA key configured, debug_search:hit confirmed working
- 4/4 acceptance tests pass

## Karma Architecture — Locked Principles (2026-03-03)

**Optimization law:** Assimilate primitives. Reject systems. Integrate only what doesn't add dependency gravity or parallel truth. Complexity is failure.

**True architecture:**
- Single coherent peer. Droplet-primary (vault-neo = source of truth)
- Chat surface: Hub Bridge. Identity: Vault ledger. Continuity: Resurrection Packs
- K2 = continuity substrate only (preserve, observe, sync). NEVER calls LLM autonomously
- Karma is the ONLY origin of thought. No exceptions.

**PDF primitives extraction filter:** (1) fits single-consciousness, (2) no dependency gravity, (3) no parallel truth, (4) implementable in existing vault-neo + Hub Bridge + FalkorDB stack

## Aria Plan Documents — Path (2026-03-04)

**Location:** `C:\Users\raest\OneDrive\Documents\AgenticKarma\FromAnthropicComputer`

**Contents:**
- `v7/` — Aria's v7 architecture docs (2026-02-28): `KARMA_BUILD_PLAN_v7.md`, `KARMA_MEMORY_ARCHITECTURE_v7.md`, `KARMA_PEER_ARCHITECTURE_v7.md`, `KARMA_HARDENED_REVIEW_v7.md`, `KARMA_VERIFICATION_CHAT_TEST.md` (2026-03-03)
- `KarmaPlans1/` — Earlier plans (2026-02-26): `KARMA_BUILD_PLAN.md`, `KARMA_PEER_ARCHITECTURE.md`, `KARMA_MEMORY_ARCHITECTURE.md`, `K2_INTEGRATION_ANALYSIS.md`
- `AsherMemRev.md`, `MemoryApproach.PDF` — Aria memory review docs
- Reconciliation rule (CLAUDE.md): read fully before applying, check against disk/git, merge additively, flag drift

---

## Session 60 (2026-03-04) — drift-fix Phase: Architecture Realignment IN PROGRESS

**Status:** ✅ drift-fix COMPLETE. ✅ Phase F (GLM rate limiter) COMPLETE — all V1-V5 verified.

### Phase F — GLM Rate Limiter (COMPLETE 2026-03-04)
- Design locked: 20 RPM global, no paid failover, /v1/chat=429, /v1/ingest=waitForSlot(60s)
- Stage 3 (build_hub.sh): ✅ written + verified (app/ guard blocks, root succeeds)
- Docs: docs/plans/2026-03-04-glm-ratelimit-design.md + CONTEXT.md §6 + PLAN.md Phase F
- F1 RED: 7/7 tests confirmed failing ✅ | F2 GREEN: GlmRateLimiter implemented, 25/25 pass ✅
- F3 GREEN: Wired into server.js (/v1/chat=429, /v1/ingest=waitForSlot, brief=graceful skip) ✅
- F4 VERIFIED: V1 ✅ 429 on burst | V2 ✅ deep mode unaffected | V3 ✅ ingest normal | V4 ✅ $0 delta | V5 ✅ INIT log
- Two injection attempts caught + flagged this session (KCC directive + "Full Resolution Execution Prompt")

### Phase G — Config Validation Gate (Session 61, active)
- Net-new: MODEL_DEFAULT allow-list validation (MODEL_DEEP check already existed)
- G1 RED: G-a failing (MODEL_DEFAULT check missing), G-b already passes ✅
- G2 GREEN: ALLOWED_DEFAULT_MODELS added, validateModelEnv extended, try/catch startup wrapper — 27/27 ✅
- G3 VERIFIED: [CONFIG ERROR] fires on bad MODEL_DEFAULT + docker exit_code=1 confirmed ✅
- claude-mem #3497 saved
- session-end-verify.sh: Check 5 now respects .gitignore (git check-ignore filter); Check 7 uses tail -n +2 (Windows pwd mismatch fix) → 7/7 PASS

### Completed This Session
- STATE.md + direction.md updated (both stale — S57 and Feb 23 respectively)
- Blockers #4 + #5 verified resolved (RestartCount=0, MODEL_DEEP=gpt-4o-mini)
- Audit revealed deeper drift vs Decision #2: spend tracking wrong, tool-use hardcoded to OpenAI
- GSD: phase-drift-fix CONTEXT.md + PLAN.md + SUMMARY.md written
- Phase A preflight: GLM tool-capability PROVEN SUPPORTED (Z.ai probe)
- Phase B RED: 22 tests written, all failing
- Phase C GREEN: lib/pricing.js + lib/routing.js implemented; server.js + config.py + Dockerfile updated
- Phase D VERIFIED: D1-D6 all PASS (GLM=$0, deep=gpt-4o-mini, startup validation, spend frozen)
- PITFALL: Dockerfile build context must be hub-bridge root, not app/ (lib/ was unreachable)

## Session 59 (2026-03-04) — batch_ingest Hotfixes + Full Backfill Complete

**Status:** ✅ COMPLETE

### Verified System State (2026-03-04)

| Component | Status | Evidence |
|-----------|--------|----------|
| Hub Bridge API | ✅ WORKING | /v1/chat, /v1/ambient, /v1/context, /v1/cypher, /v1/ingest |
| Consciousness Loop | ✅ WORKING | 60s OBSERVE-only, RestartCount: 0 |
| FalkorDB Graph | ✅ FULLY CAUGHT UP | 3049 Episodic + 571 Entity + 1 Decision = 3621 nodes |
| batch_ingest | ✅ FIXED + FAST | --skip-dedup: 899 eps/s, 0 errors; cron updated |
| karma-server image | ✅ REBUILT | All fixes baked in |
| PDF Watcher | ✅ REDESIGNED | Rate-limit backoff + jam notification + time-window |
| Conversation Capture | ✅ COMPLETE | 3049 episodes ingested (was 1749) |

### Session 59 Fixes
1. **batch_ingest OPENAI_API_KEY** — `os.environ.setdefault()` after config import; Graphiti embedder needs env var, not just config.py
2. **batch_ingest --skip-dedup** — direct FalkorDB Cypher write bypasses Graphiti dedup queries; 899 eps/s vs 0.01 eps/s
3. **FalkorDB datetime() incompatibility** — FalkorDB has no `datetime()` function; timestamps stored as strings
4. **Cron updated** — now uses `--skip-dedup` by default
5. **Image rebuilt** — all three fixes baked in; cron-safe

### Pitfalls Discovered (add to CLAUDE.md)
- **Graphiti embedder reads `OPENAI_API_KEY` env var directly** — removing from compose env requires `os.environ.setdefault()` in any script that initialises Graphiti before the env var is set
- **FalkorDB has no `datetime()` Cypher function** — store timestamps as ISO strings; `datetime('...')` throws "Unknown function"
- **Graphiti dedup queries time out at scale** — `--skip-dedup` (direct Cypher write) is the correct mode for bulk backfill; Graphiti mode only for small targeted runs

---

## Session 58 (2026-03-03) — All Blockers Resolved

**Status:** ✅ COMPLETE

### Accomplishments
- ✅ Three-way repo divergence resolved — GitHub/P1/droplet all at commit 63df177, then 833c06a
- ✅ 1754 lines of production karma-core rescued from droplet (hooks.py, memory_tools.py, router.py, session_briefing.py, compaction.py, consciousness.py, identity.json)
- ✅ Drift prevention deployed: CLAUDE.md hard rule (droplet = deploy target only) + session-end Check 6 (SSH dirty check) + hourly cron on vault-neo
- ✅ PDF pipeline restored: parseBody 30MB, hub-bridge rebuilt, watcher running against Karma_PDFs/
- ✅ CRITICAL PITFALL documented: hub-bridge build context ≠ git repo (must cp server.js before rebuild)

### What triggered reconciliation
- Droplet used as dev environment across multiple sessions — karma-core files never committed
- P1 feature branch 20+ commits ahead of GitHub main
- Root cause fixed permanently via CLAUDE.md rule + session-end hook

## Session 57 (2026-03-03) — Current State

**Status:** 🟡 BLOCKERS CLEARING — FalkorDB unfrozen, hub/chat ingestion now running

### Verified System State (2026-03-03)

| Component | Status | Evidence |
|-----------|--------|----------|
| Hub Bridge API | ✅ WORKING | /v1/chat, /v1/ambient, /v1/context, /v1/cypher operational |
| Consciousness Loop | ✅ WORKING | 60s OBSERVE-only cycles confirmed, zero LLM calls |
| Ledger | ✅ GROWING | ~4000 entries, git commits + session-end hooks capturing |
| FalkorDB Graph | ✅ GROWING | 1642+ nodes — batch_ingest running, cron every 6h |
| Conversation Capture | ✅ FIXED | hub/chat entries now ingested via extended batch_ingest |
| Chrome Extension | ❌ SHELVED | Never worked reliably. Legacy data only. |
| batch_ingest | ✅ RUNNING | Cron every 6h + extended to process hub/chat entries |
| Ambient Tier 1 | ✅ WORKING | Git + session-end hooks → /v1/ambient → ledger confirmed |
| Karma Terminal | ⚠️ STALE | Last capture 2026-02-27 |
| GSD Workflow | ✅ ADOPTED | .gsd/ structure in place |

### Active Blockers (Priority Order)

**#1 ✅ RESOLVED: FalkorDB unfrozen (2026-03-03)**
- batch_ingest ran: 1570 → 1642 nodes
- LEDGER_PATH corrected: `/ledger/memory.jsonl` (container mount)
- Cron installed: `0 */6 * * *` on vault-neo

**#2 ✅ RESOLVED: hub/chat entries now reach FalkorDB (2026-03-03)**
- Root cause: batch_ingest only checked `assistant_message`; hub/chat uses `assistant_text`
- Fix: extended batch_ingest.py — detects hub/chat by tags, reads `assistant_text` fallback
- 1538 Colby<->Karma conversations now being ingested (running now)
- Option 2 (ASSIMILATE signals) earmarked for future quality/curation layer

**#3 ✅ RESOLVED: Auto-schedule configured (2026-03-03, verified session-58)**
- Cron every 6h on vault-neo — `0 */6 * * *` with pgrep guard (was claimed done session-57 but was actually missing; added session-58)

**#4 ✅ RESOLVED: karma-server image rebuilt (2026-03-03)**
- Synced batch_ingest.py + config.py from git repo to /opt/seed-vault/memory_v1/karma-core/
- Rebuilt compose-karma-server:latest via docker compose build --no-cache
- Restarted: RestartCount=0, clean startup, consciousness loop active

**#5 ✅ RESOLVED: MODEL_DEEP corrected (2026-03-03)**
- Was `gpt-5-mini` (non-existent model) — every deep-analysis call was failing silently
- Fixed to `gpt-4o-mini` in `/opt/seed-vault/memory_v1/hub_bridge/config/hub.env`; hub-bridge restarted and verified

**#10 ✅ RESOLVED: Karma chat internal_error on GLM 429 (2026-03-03)**
- Root cause: PDF watcher hammered Z.ai with no delay → rate limit exhausted → /v1/chat 429 → internal_error
- Wrong fix: added gpt-4o-mini fallback (violates Decision #7 — GLM always, other only emergency). REVERTED.
- Correct fix: watcher now sleeps `$IngestDelaySec` (default 8s) between each file during startup batch
- hub-bridge fallback reverted + rebuilt; watcher throttle committed

**#7 ✅ RESOLVED: OPENAI_API_KEY no longer exposed in docker inspect (2026-03-03)**
- Root cause: key was injected as env var via compose.yml → visible in `docker inspect karma-server`
- Fix: config.py reads from mounted file `/opt/seed-vault/memory_v1/session/openai.api_key.txt`; removed env var from compose.yml karma-server section
- Rebuilt karma-core:latest image, restarted; verified PASS: OPENAI_API_KEY not in env

**#8 ✅ RESOLVED: karma-server restart loop (2026-03-03)**
- Root cause: MODEL_DEEP=gpt-5-mini caused exceptions → container crashed → Docker restarted → cycle: 1 always
- Fix: already resolved by #2 + #3. RestartCount: 0 confirmed post-rebuild.

**#9 ✅ RESOLVED: misc cleanup (2026-03-03)**
- compose.karma-server.yml: K2_PASSWORD/POSTGRES_PASSWORD replaced with env var references
- karma-k2-sync: DEPRECATED header added to all 4 copies (Karma_PDFs/ + k2-worker/)
- 10 stale claude/ remote branches deleted from GitHub

**#6 ✅ RESOLVED: PDF ingestion pipeline restored (2026-03-03)**
- Caller: `Scripts/karma-inbox-watcher.ps1` — watches Inbox/ and Gated/, sends base64 to /v1/ingest
- Root cause: large PDFs (15MB raw = ~20MB base64) hit parseBody 20MB cap → req.destroy()
- Fix: parseBody limit raised to 30MB — deployed + hub-bridge image rebuilt
- Watcher running, processing ~80 PDF backlog, Done/ growing (108 → 112+), 0 new errors
- Token: `C:\Users\raest\Documents\Karma_SADE\.hub-chat-token`; paths: Karma_PDFs/{Inbox,Gated,Processing,Done}

### Session 57 Accomplishments
- ✅ Consciousness loop OBSERVE-only contract confirmed (CYCLE_REFLECTION = log type, not mode)
- ✅ Chrome extension shelved — all docs updated
- ✅ FalkorDB unfrozen — batch_ingest ran, cron claimed configured (NOT VERIFIED — found missing in session-58, now fixed)
- ✅ LEDGER_PATH bug fixed in all docs (was wrong host path, correct = /ledger/memory.jsonl)
- ✅ hub/chat → FalkorDB gap closed — extended batch_ingest with hub-chat support
- ✅ 1538 Colby<->Karma conversations now ingesting into graph
- ✅ Superpowers enforcement: CLAUDE.md mandatory workflow table added, save_observation added to capture protocol, resurrect skill updated to invoke using-superpowers
- ✅ 4 structural gaps closed: Session Start → resurrect skill only (Gap 1), GSD enforcement rule (Gap 2), token efficiency table (Gap 3), save_observation as Session End step 1 (Gap 4)
- ✅ Session ritual table + claude-mem always-available section added to CLAUDE.md (dual-write rule, at-the-moment rule)

---

## Infrastructure
- P1 + K2: i9-185H, 64GB RAM, RTX 4070 8GB
- Tailscale: P1=100.124.194.102, K2=100.75.109.92, droplet=100.92.67.70
- SSH alias: vault-neo
- API keys: C:\Users\raest\OneDrive\Documents\Aria1\NFO\mylocks1.txt
- Git ops: Use PowerShell (Git Bash has persistent index.lock issue on Windows)
- FalkorDB graph name: `neo_workspace` (NOT `karma`)
- Hub token path: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt`

## Known Pitfalls (active)
- **hub-bridge Dockerfile build context = hub-bridge root (not app/)**: compose.hub.yml uses `context: .` + `dockerfile: app/Dockerfile`. Dockerfile COPYs `app/server.js` + `lib/`. server.js imports `./lib/pricing.js` (from /app). Tests import `../lib/pricing.js` (from hub-bridge/tests/).
- **KARMA_IDENTITY_PROMPT**: hub-bridge reads system prompt from file at startup via `KARMA_SYSTEM_PROMPT_PATH`. File = `/karma/repo/Memory/00-karma-system-prompt-live.md` (volume-mounted). If file missing, WARN logged, identity block empty (hub still runs). Update cycle: git pull + docker restart only.
- **anr-vault-search is FAISS not ChromaDB**: endpoint POST :8081/v1/search, body `{query, limit}`. Auto-reindex on ledger FileSystemWatcher + every 5min. Not a ChromaDB API.
- `python3` not available in Git Bash — use SSH for Python ops
- Docker compose service: `hub-bridge` (container name: `anr-hub-bridge`)
- batch_ingest requires `LEDGER_PATH` override (see CLAUDE.md)
- karma-server built from Docker image — source file edits require rebuild
- FalkorDB requires both env vars: `FALKORDB_DATA_PATH=/data` and `FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 100'`
- **hub-bridge build context ≠ git repo**: build uses `/opt/seed-vault/memory_v1/hub_bridge/app/`, NOT `/home/neo/karma-sade/hub-bridge/app/`. After any git pull, sync first: `cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js`

# currentDate
Today's date is 2026-03-10.

## Session 62 Task 2 — Graphiti Watermark Wired into run() (2026-03-04T22:23:29Z)

**Status:** COMPLETE

- Wired  /  /  into  for Graphiti mode.
-  path is unchanged (count-based dedup, bulk backfill).
- Graphiti mode now uses watermark-based episode selection: reads from last watermark, caps at  (default 200), writes watermark after wave loop.
- Added  CLI argument to .
- Added  env var read (default ).
- All 7 watermark tests pass. Dry-run validation passes. Syntax OK.

## Session 68 (2026-03-05) — v9 Phase 4 Tasks 1+2
Task 1 complete: hub-bridge/lib/feedback.js (processFeedback + prunePendingWrites, pure functions, no I/O) + hub-bridge/tests/test_feedback.js (7 tests, all green).
Task 2 complete: server.js -- pending_writes Map, write_memory tool def, executeToolCall write_memory case, writeId threaded through callLLMWithTools+callGPTWithTools, req_write_id per-request, proposed_write_id in 200+207 responses.

Task 3 complete: bare newline fix in appendFileSync (CRLF ->
 escape) + emoji log messages (thumbs up/down) in feedback endpoint. Syntax verified clean.

Task 8 complete: write_memory coaching paragraph appended to "## How to Use Your Context Data" section in Memory/00-karma-system-prompt-live.md. Paragraph instructs Karma to call write_memory(content) in deep-mode when she learns something worth persisting (preferences, corrections, new facts not in MEMORY.md yet), notes approval gate, and sets a "don't call every turn" bar.


## Session 68+ Fix: Remove Stale Tool Definitions

- Removed 4 stale tool objects from TOOL_DEFINITIONS in hub-bridge/app/server.js: read_file, write_file, edit_file, bash
- These had no handler and caused Karma to confabulate capabilities
- TOOL_DEFINITIONS now contains only 3 active tools: graph_query, get_vault_file, write_memory
- Updated stale comment from "4 tools only" to reflect current 3-tool reality

## Session 70 Wrap-up (2026-03-09)

Completed: batch_ingest --skip-dedup PITFALL added to CLAUDE.md + architecture.md. STATE.md, problems-log.md, session-handoff (Session 71), session-summary updated. cc-session-brief.md regenerated. Secret scan clean.

Next: Session 71 — thumbs up/down general feedback UI for Karma chat.
n## Session 72 (2026-03-10) — Watcher Fix + v10 Startn### karma-inbox-watcher persistent startup fixn- Fix: added Step 4 to karma_startup.ps1 — watcher now launches via existing logon orchestratorn- Watcher runs at every logon; running now (PID 235260)

### Session 72 fix: MEMORY.md spine injection (2026-03-10)
- BUG: MEMORY.md never appeared in Karma's standard context -- she was blind to her own memory spine
- ROOT CAUSE: buildSystemText had no memoryMd param; MEMORY.md only accessible via get_vault_file in deep mode
- FIX: _memoryMdCache (tail 3000 chars), loadMemoryMd() on startup + 5min refresh, injected as KARMA MEMORY SPINE section
- PROOF: 17/17 tests GREEN (11 feedback + 6 system_text); deployed to vault-neo
- STATUS: Karma now has v10 context on every request without needing deep mode
\

### Session 72: Entity Relationships data quality fix (2026-03-10)
- BUG: query_relevant_relationships() used RELATES_TO â€” 1,423 edges permanently frozen at 2026-03-04 (Chrome ext era)
- ROOT CAUSE: --skip-dedup mode never creates RELATES_TO edges; Graphiti dedup (disabled Session 59) was the only creator
- FIX: MENTIONS co-occurrence query â€” Episodic->Entity cross-join, cocount >= 2, ORDER BY cocount DESC LIMIT 20
- LIVE: Karma/Colby=123, Karma/User=100, User/Universal AI Memory=44 â€” current, growing data
- PROOF: 11/11 tests GREEN (2 new TDD); RestartCount=0; live query confirmed in deployed container
- STATUS: v10 blocker #2 COMPLETE

### Session 72: Confidence levels + anti-hallucination gate (2026-03-10)
- FEATURE: [HIGH]/[MEDIUM]/[LOW] tags mandatory on technical claims in system prompt
- FEATURE: Anti-hallucination hard stop â€” before asserting unverified API/function behavior, Karma must stop and offer to verify first
- Covers v10 priority #3 (confidence levels) AND #4 (anti-hallucination pre-check) in one section
- PROOF: [LOW] on unverified redis-py signature + verification suggestion; [HIGH] on known system facts
- KARMA_IDENTITY_PROMPT: 12524 â†’ 14601 chars; docker restart only (no rebuild needed)
- STATUS: v10 priorities #3 + #4 COMPLETE

### Session 72: get_library_docs tool (v10 priority #5) (2026-03-10)
- FEATURE: get_library_docs(library) deep-mode tool — URL map lookup + fetch_url reuse pattern
- Libraries: redis-py, falkordb, falkordb-py, fastapi (covers Karma's actual [LOW] claim libraries)
- DECISION: Context7 rejected (external dependency not needed); DIY with existing fetch_url logic
- Files: hub-bridge/lib/library_docs.js (new), hub-bridge/app/server.js (import + TOOL_DEFINITIONS + handler)
- TDD: 7/7 tests GREEN (test_library_docs.js); 24/24 full suite GREEN
- STATUS: v10 priority #5 COMPLETE

### Session 72: System prompt updated for get_library_docs (2026-03-10)
- Added get_library_docs to tool list (line 26), CANNOT Do exception, deep-mode coaching, anti-hallucination gate
- Karma now knows when/how to call get_library_docs before [LOW] library API claims

### Session 72: Wrap-up documentation (2026-03-10)
- Updated direction.md: v10 COMPLETE (was v9 IN PROGRESS)
- Updated Memory/08-session-handoff.md: Session 72 system state + new pitfalls
- Updated Memory/11-session-summary-latest.md: full Session 72 summary
- Updated Memory/02-stable-decisions.md: Decisions #22–#27 promoted
- Updated Memory/04-session-learnings.md: 5 patterns captured
- Updated Memory/corrections-log.md: 2 corrections documented
- Updated Memory/problems-log.md: 3 problems logged
- Updated .claude/rules/architecture.md: v10 features documented
- Updated CLAUDE.md: 4 new pitfall entries
- Regenerated cc-session-brief.md: current as of Session 72
- STATUS: All documentation synchronized. v10 complete. No blockers.

## Session 73 — Watcher Fix (2026-03-10)

**PITFALL/FIX: KarmaInboxWatcher was dying silently**
- Root cause: `StopIfGoingOnBatteries=true` — Task Scheduler killed it when machine went on battery
- Secondary: wrong paths (OneDrive default vs Karma_PDFs/), restarts exhausted after 3 attempts
- Fix: admin script rewrote task — battery flags false, 9999 restarts/2min, AtLogon+AtStartup triggers, correct Karma_PDFs/ paths
- Emergency restart: `Scripts/start-watcher-now.ps1` (no admin)
- Permanent fix script: `Scripts/fix-watcher-task-ADMIN.ps1` (requires admin, already applied)
- PROOF: Done=206 (+2 during fix), Inbox=3 (was 10), queue moving post-fix

## Phase 4 Task 1 — Deferred Intent Engine (2026-03-10)

**Created: hub-bridge/lib/deferred_intent.js**
- Pure logic module, no I/O, no external dependencies
- Exports: `generateIntentId()`, `triggerMatches()`, `buildActiveIntentsText()`, `getSurfaceIntents()`
- Syntax verified: `node --check` passed
- STATUS: Task 1 complete. Next: tests + integration into server.js context assembly.

## Session 78 Final (2026-03-10) — All tasks complete, code review applied

All 9 implementation tasks complete. Post-review commit 7a96fda pushed and redeployed.

6 code review fixes:
1. DPO guard: if (write_id || turn_id) — intent-only feedback no longer pollutes DPO dataset
2. Cache eviction: _activeIntentsMap.clear() before repopulate — completed intents evicted
3. triggerMatches null guard: (userMessage || "").toLowerCase()
4. generateIntentId: imported from module, inline duplicate removed
5. once fire_mode: added to _firedThisSession (was only once_per_conversation)
6. Removed misleading _activeIntentsCacheTs on approval

Final state: v2.11.0 live, RestartCount=0, loads active intents from ledger at startup.
Next: Phase 1 Self-Model Kernel — buildSelfModelSnapshot(), Haiku 4.5 RPM tracking, injection.
