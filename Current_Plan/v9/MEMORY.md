# Universal AI Memory — Current State

## Session 65 (2026-03-05) — CLAUDE.md Rules + v9 Plan Snapshot

**Status:** ✅ IN PROGRESS

### What Was Done
- Added strategic-question pre-read rule to CLAUDE.md GSD hard rules
- Added version snapshot rule to CLAUDE.md GSD hard rules
- Created `Current_Plan/v9/` snapshot (10 files)
- Ingested CreatorInfo.pdf ("The File That Made the Creator of Claude Code Go Viral" — Cherny CLAUDE.md workflow). 2/3 chunks ASSIMILATE, lane=canonical in FalkorDB.
- Integrated PDF insights into 5 docs: direction.md (external validation table), ROADMAP.md (Known Quality Gap: corrections trigger), 00-karma-system-prompt-live.md (How You Improve section), CLAUDE.md (constitution principle), REQUIREMENTS.md (systematic mistake-capture requirement)
- Re-copied all updated files to Current_Plan/v9/
- Key insight: Cherny independently validates Karma's two-tier architecture (identity.json=global, direction.md=project). Gap documented: corrections capture is session-based, not event-driven.

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
Today's date is 2026-03-05.

## Session 62 Task 2 — Graphiti Watermark Wired into run() (2026-03-04T22:23:29Z)

**Status:** COMPLETE

- Wired  /  /  into  for Graphiti mode.
-  path is unchanged (count-based dedup, bulk backfill).
- Graphiti mode now uses watermark-based episode selection: reads from last watermark, caps at  (default 200), writes watermark after wave loop.
- Added  CLI argument to .
- Added  env var read (default ).
- All 7 watermark tests pass. Dry-run validation passes. Syntax OK.
