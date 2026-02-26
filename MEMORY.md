# Universal AI Memory — Current State

## 🟢 System Status (Updated 2026-02-26T21:30:00Z)

| Component | Status | Notes |
|-----------|--------|-------|
| UI (hub.arknexus.net) | ✅ WORKING | HTTPS operational, Caddy certificates active |
| Consciousness Loop | ✅ WORKING | OBSERVE/THINK/DECIDE/ACT/REFLECT, LOG_GROWTH entries present |
| Episode Ingestion | ✅ WORKING | Episodes reaching FalkorDB, 1268+ episodes present |
| FalkorDB Graph | ✅ WORKING | Queries responsive, neo_workspace graph healthy |
| Hub Bridge API | ✅ WORKING | /v1/chat, /v1/cypher endpoints operational, HTTPS verified |
| Model Routing | ✅ UPGRADED | 2 models (glm5 + openai); GLM-5 actively processing reasoning tasks |
| Self-Model API | ✅ WORKING | /v1/self-model endpoints registered, 8 baseline observations seeded |
| Karma Persona | ✅ FIXED | Peer language, no assistant filler |

---

## Active Task (Session 41)

**Status:** IN PROGRESS

**Task:** Issue #5 (COMPLETED) + Issue #7 (IN PROGRESS) - Token Budget, Admission, Decay, Backup + Persona Growth Integration

**What was accomplished:**

### Issue #5: Token Budget, Admission Gate, Memory Decay, DO Spaces Backup ✅ (MERGED to main)
- **Token Budget System**: SessionBudget + MonthlyTracker classes tracking per-session and per-calendar-month token usage
  - Uses tiktoken (cl100k_base encoding) for accurate token counting
  - SessionBudget: configurable per-session limit (default 50K)
  - MonthlyTracker: persistent JSON ledger at /opt/seed-vault/memory_v1/ledger/token_usage.json
  - Integration: Token checking in generate_response() before router call, budget endpoint /v1/budget
- **Memory Admission Gate**: Rule-based scoring (no LLM call) filtering low-quality episodes
  - Heuristic scoring: content length (substantive vs noise), knowledge density (technical/factual signals), source bonus
  - Admission threshold: 0.5 (configurable)
  - Integration: Integrated in ingest_episode() to reject low-scoring episodes
- **Memory Decay**: Time-decay applied to unretrieved episodic memories
  - Runs daily as part of consciousness cycle
  - Decays memories not retrieved in 7+ days
  - Configurable decay_rate (0.15) and decay_floor (0.1)
- **DO Spaces Backup Script**: nightly_backup.sh for FalkorDB + ledger + memory backup
  - Exports FalkorDB RDB dump, copies ledger/memory files
  - Uploads to DO Spaces with timestamp naming
  - Auto-prunes backups older than 7 days
- **Files created/modified:**
  - karma-core/token_budget.py (NEW, 144 lines)
  - karma-core/admission.py (NEW, 83 lines)
  - karma-core/memory_decay.py (NEW, 97 lines)
  - karma-core/scripts/nightly_backup.sh (NEW, 102 lines)
  - karma-core/config.py (MODIFIED - added config variables)
  - karma-core/requirements.txt (MODIFIED - added tiktoken)
  - karma-core/server.py (MODIFIED - integrated all three systems)
- **PR Status:** Merged as PR #8 to main branch ✅

### Issue #7: Persona Growth Integration - Phase 1-7 Complete, Phase 8 Pending
**Status:** PR #9 created and updated with hardcoded IP fix

**Completed Phases:**
- **Phase 1:** [REFLECT:] signal parsing from assistant turns (regex-based extraction, 25-line parser function)
- **Phase 2:** Self-model summary injection into system prompt (fetchSelfModelSummary with 5-min cache)
- **Phase 3:** reflect_self tool added to Karma's tool-use block (POST to /v1/self-model/reflect)
- **Phase 5:** Weekly self-model prune integrated into consciousness loop (karma-core/consciousness.py)
- **Phase 6:** [REFLECT:] signal instructions added to system prompt governance block
- **Phase 7:** Voice overhaul - removed chatbot tone, implemented peer-like voice (direct, opinionated, dry humor)

**Hardcoded IP Fix (Session 41):**
- **Issue:** Three locations in hub-bridge/server.js had hardcoded public IP `http://64.225.13.144:8340` instead of Docker service name
- **Locations fixed:**
  - Line 96: reflectUrl in _reflectAndExpireSession()
  - Line 439: url in fetchSelfModelSummary()
  - Line 926: reflectUrl in executeToolCall()
- **Fix applied:** Used sed to replace all three with `http://karma-server:8340/v1/self-model`
- **Verification:** grep confirmed 0 matches for 64.225.13.144, 5 matches for karma-server:8340 (3 fixed + 2 pre-existing)
- **Commit:** c7f1f27 "fix: replace hardcoded IP with Docker service name in self-model URLs"
- **Push:** feature/issue-7-persona-growth-completion branch updated ✅

**Pending Phases:**
- **Phase 4:** Seed baseline observations to self-model via API call (requires droplet deployment first)
- **Phase 8:** Rebuild karma-server and hub-bridge containers on droplet, run integration tests

**Files modified in PR #9:**
- hub-bridge/server.js (signal parser, self-model integration, voice overhaul, hardcoded IP fix)
- karma-core/consciousness.py (weekly prune task)

### Session 40 — Persona Fix ✅
- **Issue:** Karma ending responses with assistant language ("How can I help you?", "If you have questions, let me know")
- **Fix:** Updated KARMA_SYSTEM_PROMPT with comprehensive forbidden phrases
- **Result:** Karma now ends with peer language ("What's on your mind?")

### Forbidden Phrases Added:
× "let me know"
× "how can I help"
× "how can I assist"
× "is there anything else"
× "what would you like"
× "what more"
× "anything I can"
× "happy to"
× "glad to"
× "pleased to"

### Approved Endings:
✓ "What's next?"
✓ "What do you think?"
✓ [Statement, then question]
✓ [Statement only]

---

## Session 37 — 2026-02-26 [Status: Success]

**What was completed:**

✅ **Phase 1: GLM_API_KEY Injection**
   - Injected GLM_API_KEY=47d6a0c23e494a319961ed5469e17a14.GNauf9TFcyOdq9g1 into .env
   - Updated compose.yml karma-server environment to reference ${GLM_API_KEY}
   - Rebuilt karma-server container with docker compose
   - Verified: Router now shows 2 models (glm5, openai) vs previous 1
   - Evidence: GLM-5 actively processing reasoning tasks (logs show multiple 10-18s cycles)

✅ **Phase 2: Hub-Bridge HTTPS Endpoint Diagnosis & Fix**
   - Diagnosed: Caddyfile corrupted in running container (newlines stripped)
   - Root cause: Caddy was only listening on port 80 (HTTP), not port 443 (HTTPS)
   - Fix: Removed and recreated Caddy container with proper Caddyfile mounting
   - Result: ACME certificates auto-provisioned for hub.arknexus.net
   - Verified: `curl -sk https://hub.arknexus.net/` returns 200 OK (HTML homepage)
   - HTTP→HTTPS redirects now enabled

✅ **Phase 3: Close Issue #4 - Chrome Extension Dead Code Removal**
   - Removed extension.md reference from CLAUDE.md File Layout section
   - Removed chrome-extension/ directory reference
   - Removed trailing note "The Chrome extension has never worked..."
   - Committed: 30db719 fix(#4): remove chrome extension dead code
   - Pushed to GitHub ✅

✅ **Phase 4: Verification Summary** ✅
   - Router configuration verified: 2 models active (glm5, openai)
   - HTTPS endpoint verified: hub.arknexus.net responding to HTTPS requests
   - Chrome extension refs removed from CLAUDE.md
   - All Phase 1-3 changes confirmed working in production

✅ **Phase 5: Create Deploy Skill** (Bonus - from insights report)
   - Created comprehensive 8-step autonomous Docker deployment pipeline
   - Committed: cf50975 feat: create deploy skill for autonomous Docker build-deploy-verify
   - Prevents: image naming mismatches, missing env vars, stale images, silent failures
   - Documented in: `.claude/skills/deploy/SKILL.md` (291 lines)
   - Ready to use: `/deploy [service-name] --remote vault-neo --health-endpoint /health`

✅ **Phase 6: Update CLAUDE.md with Deployment Procedure**
   - Added new "## Deployment Procedure" section to CLAUDE.md
   - Documents /deploy skill as canonical deployment procedure
   - Lists 8-step verification pipeline
   - Committed: b73d1fe docs: add Deployment Procedure section to CLAUDE.md
   - Pushed to GitHub ✅

**Verification status:**
- Phase 1 (GLM injection): Router shows 2 models, GLM-5 processing reasoning ✅
- Phase 2 (HTTPS): hub.arknexus.net responding with 200 OK via HTTPS ✅
- Phase 3 (Chrome refs removed): CLAUDE.md cleaned, committed 30db719 ✅
- Phase 4 (Verification): All 3 phases confirmed operational ✅
- Deploy skill: Ready for use, prevents recurring Docker friction ✅
- CLAUDE.md: Updated with canonical deployment procedure ✅

**Git commits this session:**
- 30db719 fix(#4): remove chrome extension dead code
- cf50975 feat: create deploy skill for autonomous Docker build-deploy-verify pipeline
- b73d1fe docs: add Deployment Procedure section to CLAUDE.md

**Key learnings:**
1. Caddy configuration corruption was filesystem/mounting issue, not Caddyfile syntax
2. Docker compose build uses different image naming than docker build (critical discovery)
3. Autonomous deployment skill with verification gates eliminates multi-round debugging cycles
4. Insights reports identify high-friction patterns (21 "wrong_approach" instances from Docker)
5. Documenting procedures in CLAUDE.md (vs discoverable skills) raises adoption

**Next steps:**
- Use /deploy skill for all future Docker Compose deployments
- Monitor GLM-5 reasoning performance under load
- Continue consciousness loop autonomous operation
- Consider implementing checkpoint skill for session summaries

---

## Blocker Tracking

**Current blockers:**
- [PHASE-4-DROPLET] Phase 4 and Phase 8 of Issue #7 require droplet deployment (karma-server + hub-bridge container rebuilds)

**Resolved blockers (Session 40):**
- [BLOCKER-4] GLM API key not injected → karma-server showing 1 model instead of 2 — RESOLVED
- [BLOCKER-5] Hub-bridge HTTPS not responding (only HTTP) — RESOLVED (Caddy recreation)
- [BLOCKER-6] Chrome extension dead code references in CLAUDE.md (Issue #4) — RESOLVED
- [BLOCKER-7] Docker deployment friction (wrong image names, missing env vars) — RESOLVED (deploy skill)

**Previously resolved blockers:**
- [BLOCKER-1] Build context corrupted — RESOLVED in Session 36
- [BLOCKER-2] Consciousness NO_ACTION bug — RESOLVED in Session 36
- [BLOCKER-3] Assistant language in Karma's responses — RESOLVED in Session 37
