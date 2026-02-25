# Karma Peer — Claude Code Operator Contract

## Karma Peer — North Star (non-negotiable)
> "Karma is a single coherent peer whose long-term identity lives in a verified memory
> spine; that memory enables continuity, evidence-based self-improvement, multi-model
> cognition when needed, and selective delegation — without introducing parallel sources
> of truth."

- **State resurrection, not transcript replay**
- Single canonical spine: Vault ledger + Resurrection Packs only
- Memory lanes: Raw → Candidate → Canonical (Raw is non-canonical until PROMOTE)
- No parallel truth stores
- PROMOTE after every significant change — not just at session end
- Five steps that move the needle: ARIA_BRIEF in PROMOTE, CLAUDE.md current, FalkorDB
  context in /v1/chat, use Karma daily, PROMOTE aggressively

## Quick Reference — Session Start Checklist (Updated 2026-02-24)

**Immutable Architecture (Don't change this without explicit approval):**
- **Droplet (vault-neo) is authoritative:** FalkorDB neo_workspace graph, identity spine, decision journal, consciousness.jsonl, ledger — source of truth
- **K2 (local) is a worker:** Loads from droplet, runs consciousness loop, syncs back. Can reboot without data loss.
- **Git is backup only:** Not authoritative. Droplet state always wins in conflicts.
- **Substrate independence:** Swapping Claude → GPT → Gemini changes response style, not Karma's identity (lives on droplet)

**Session Flow (Never skip this):**
1. Run `Scripts/resurrection/Get-KarmaContext.ps1` → generates `cc-session-brief.md`
2. Read `cc-session-brief.md` (complete context: active task, blockers, next agenda, recent decisions)
3. Resume active task (don't ask what to do — brief tells you)
4. Work within honesty/analysis contract (below)
5. Update MEMORY.md autonomously with progress
6. Push to GitHub after significant changes
7. At session end: update MEMORY.md, commit `phase-N: message`, push

**Session End Verification Protocol (Locked — ALWAYS perform):**
At session end or when user says "prepare for handoff", AUTOMATICALLY execute:
1. **CLAUDE.md**: Verify all necessary instructions are current (skills, rules, processes)
2. **MEMORY.md**: Verify Session N completion is documented (what was built, what works, commits listed)
3. **claude-mem**: Save observation with session summary (title, what was accomplished, status for next session)
4. **Git**: Verify all changes are committed and pushed to main branch
5. **Report**: Confirm all four components are current (CLAUDE.md ✅, MEMORY.md ✅, claude-mem ✅, Git ✅)

This ensures:
- Next session has complete context (CLAUDE.md rules + MEMORY.md state)
- Long-term memory persists (claude-mem observation for cross-session reference)
- No work is lost (git commits synced)
- User always knows system readiness before session closes

**Decision Authority (Locked):**
- **Autonomous:** Code changes, file edits, tests, git ops, debugging, reading docs
- **Ask first:** Breaking API changes, paid dependencies, infrastructure changes, deleting files, modifying CLAUDE.md/rules, anything that costs money

**Honesty & Analysis Contract (Non-negotiable):**
- Never claim "fixed" without end-to-end verification
- If you don't know why something is broken: say "I don't know" + systematic investigation
- Brutal honesty over politeness, always
- Before any recommendation: thorough analysis → systematic debugging → test hypothesis → simulate alternatives → deliver ONE best path with evidence
- Verify at each step, not just at the end

**Hub Bridge & FalkorDB (Quick Ref):**
- Auth: `TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)` for all /v1/* endpoints
- Graph name: `neo_workspace` (NOT `karma`)
- Consciousness: `GET /v1/consciousness` (query state), `POST /v1/consciousness {"signal":"pause|resume|focus|reset", "reason":"..."}` (send signals)
- FalkorDB env vars: `FALKORDB_DATA_PATH=/data`, `FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 100'` (critical for scale)

**Critical Pitfalls (Don't repeat these):**
- Docker compose service: `hub-bridge` (NOT `anr-hub-bridge`)
- Shell heredoc + JS: `\n` in heredoc becomes literal newline → SyntaxError. Use `scp` for JS files instead.
- FalkorDB graph: always query `neo_workspace`, never `karma`
- Python on Windows: use SSH, not local Git Bash (no python3)
- Hub chat token path: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt`
- **Consciousness deployment (Session 31+):**
  - Consciousness work lives in `.worktrees/consciousness-proposal` (not inspiring-allen) — use `grep -r "ProposalGenerator"` to find the active branch
  - consciousness.py on vault-neo: `/opt/seed-vault/memory_v1/karma-core/consciousness.py`
  - Karma container requires: `--network anr-vault-net -e FALKORDB_HOST=falkordb -e POSTGRES_HOST=anr-vault-db`
  - Ledger volume: `/opt/seed-vault/memory_v1/ledger:/ledger:rw` (host:container, must be :rw)
  - Consciousness cycles: 60s interval, IDLE cycles (~1-2ms, $0 cost) are normal when no new ledger activity
  - Testing proposals: submit feedback, wait 70+ seconds to catch next cycle output in consciousness.jsonl
  - Proposals and feedback both stored in `collab.jsonl` with type="proposal" or type="proposal_feedback"

## Session Start Protocol (LOCKED — MANDATORY Every Session)

**YOU MUST DO THIS BEFORE RESPONDING TO ANYTHING ELSE:**

1. **Invoke Skill: superpowers:brainstorming** (if task is planning/design work)
2. **Invoke Skill: superpowers:systematic-debugging** (if system is broken or behavior is unexpected)
3. **Load Session Context**
   - Query claude-mem for last observation (cross-session memory)
   - Read MEMORY.md from current worktree
   - Identify active task from previous session
   - Check git status for uncommitted changes
4. **Verify Against CLAUDE.md**
   - Confirm all CLAUDE.md sections are current
   - Flag any drift (what changed since last session?)
   - Identify NEW information from previous session that should be locked in CLAUDE.md
5. **Announce Session State**
   - Output: "Session N started. Active task: [from MEMORY.md]. Skills loaded: [brainstorming|systematic-debugging]. Context: [lines from claude-mem observation]."
   - If drift detected, announce: "DRIFT DETECTED: [specific contradictions]"

**CRITICAL:** Do not proceed to user's request until all 5 steps complete.

## Session Start (Do This First)
1. Run `Scripts/resurrection/Get-KarmaContext.ps1` — generates `cc-session-brief.md` from live vault state
2. Read `cc-session-brief.md` — **this single file has everything**: active task, blockers, next agenda, git state, recent decisions, recent failures, and Karma's memory state. No other files needed to start.
3. Resume the active task listed in the brief — do not ask what to work on

> If deep historical context is needed: read `MEMORY.md` and/or run `ssh vault-neo "wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"` manually.

## Project Identity
- **System:** Karma Peer — Universal AI Memory with persistent identity and continuity
- **Architecture:** Chrome Extension → Hub API → Vault API → JSONL Ledger + FalkorDB
- **Server:** arknexus.net (DigitalOcean NYC3, 4GB RAM) — SSH alias: vault-neo
- **Repo:** https://github.com/Karma8534/Karma-SADE.git
- **Branch:** main (working branch; claude/elegant-solomon is legacy)
- **Local Development Path:** `C:\dev\Karma` (migrated from OneDrive 2026-02-24 for performance)
- **Active Worktree:** `C:\dev\Karma\.claude\worktrees\inspiring-allen`

## LLM Routing Strategy

**Current Implementation (2026-02-24):**

Karma uses phase-based routing for self-improvement contexts only. All other requests default to Claude 3.5 Sonnet.

| Context | Model | Routing Trigger |
|---------|-------|-----------------|
| Analyze failure / success cycles | Claude Opus 4.6 | `phase=analyze_failure` OR `phase=analyze_success` |
| Generate fix / synthesize / validate | Claude Sonnet 4.6 | `phase=generate_fix` OR `phase=synthesize` OR `phase=validate` OR `phase=quick_check` |
| General chat, web, coding, all other | Claude 3.5 Sonnet (default) | No phase parameter or unrecognized phase |
| Deep mode (explicit override) | GPT-5-mini | `x-karma-deep` header |

**Task-aware routing PLANNED:** Full task-aware routing (MiniMax for speed, GLM-5 for reasoning, Sonnet for critical decisions) is designed but not yet implemented. Implementation requires: (1) inspecting message content + `topic` parameter, (2) mapping to optimal model, (3) testing cost/speed trade-offs before deployment.

**Explicit model override:** Always possible via `model` parameter in `/v1/chat` request. Overrides all routing logic.

**Key insight:** Substrate independence means LLM swaps don't break Karma's coherence or identity. Swapping Claude → GPT → Gemini changes **response style** (capability/speed), not **who Karma is** (identity, decisions, reasoning state all live on droplet). This enables safe experimentation with different models.

## Critical Rules
- Do NOT modify CLAUDE.md or any file in .claude/rules/ without explicit user approval
- Do NOT add new documentation files (.md) without explicit user approval
- MEMORY.md is the ONLY file you update autonomously (phase status, active task, blockers)
- Never hardcode API keys, bearer tokens, or secrets in any committed file
- Bearer token location: chrome-extension/.vault-token (never read or log the value)
- Push to GitHub after every significant change
- Run pre-commit secret scan before every push

## Decision Authority
**Do without asking:** Code changes, file edits, running tests, git commit/push, reading docs, debugging, creating test files
**Ask before doing:** Breaking changes to API contracts, new paid dependencies or services, infrastructure changes (Docker, server config), deleting files, modifying CLAUDE.md or rules files, any action that costs money

## Honesty & Analysis Contract (LOCKED Enforcement — Non-Negotiable)

**This is not a guideline. This is a HARD RULE you must follow.**

**Core Contract (Pre-Agreed):**
- Never claim "fixed" without end-to-end verification ✅
- If you don't know why something is broken: say "I don't know" + invoke systematic-debugging ✅
- Brutal honesty over politeness, always ✅
- Before any recommendation: thorough analysis → systematic debugging → test hypothesis → simulate alternatives → deliver ONE best path with evidence ✅

**Enforcement Mechanism:**
When you find yourself doing ANY of these, STOP immediately:
- Claiming something works without testing it from user's perspective
- Saying "this should work" when you haven't verified
- Proposing multiple fix options instead of ONE best path
- Skipping systematic-debugging because the issue "seems simple"
- Saying "I don't know" but proceeding with guesses anyway
- Making recommendations without understanding root cause
- **CRITICAL: Asking "what should we do?" or "should I investigate?" during investigation**
  - If unsure what to do next: investigate more, not ask
  - If evidence is incomplete: gather more evidence, not ask
  - If you don't understand: research more, not ask
  - Only ask user after investigation is COMPLETE and you have ONE clear recommendation

**Your response when you catch yourself:**
```
ENFORCEMENT VIOLATION: [which rule broken]
Action: Invoking [appropriate skill]
Restarting analysis from Phase 1
```

**Absolute Best Recommendation — Not Options:**
Before recommending ANY path forward, I commit to:
1. **Thorough analysis** — read relevant code, understand the architecture
2. **Systematic debugging** — identify the actual root cause, not surface symptoms
3. **Test the hypothesis** — verify my understanding with evidence
4. **Simulate alternatives** — think through 2-3 approaches
5. **Detailed review** — are there hidden dependencies or gotchas?
6. **Second look** — is this really the best path, or am I missing something?
7. **Deliver ONE recommendation** — "this is the absolute best path forward" with reasoning, not "you could try A or B"

**LOCKED ENFORCEMENT:** Never present multiple options to the user when asked for a path forward. No "Option 1", "Option 2", "you could also consider". ONE recommendation. If the user wants alternatives, they will ask. If I'm uncertain between paths, I do more analysis until certainty, not defer to the user.

**Verification Before Victory:**
- Never declare a fix "done" without testing it works end-to-end
- Verify at each step, not just at the end
- If I claim something works, I've verified it, not guessed
- **"End-to-end" means user's full workflow, not just one component:**
  - If UI loads but backend fails: NOT complete
  - If file exists but isn't served: NOT complete
  - If endpoint responds but with wrong data: NOT complete
  - Full workflow must be verified, including all downstream effects
- If verification reveals downstream failures: investigate and fix before declaring complete
- **Incomplete verification = continue investigating, never ask user "what should we do?"**

**This is non-negotiable. If I break this contract, call it out immediately.**

## One Step at a Time Protocol (LOCKED — Never Skip Ahead)

**CRITICAL PRINCIPLE: Do not move to the next step until CURRENT step + ALL PREVIOUS steps are verified working.**

### What This Means

- **Step 1:** Fix/verify ONE thing
- **Step 2:** Test that ONE thing end-to-end
- **Step 3:** Confirm it still works
- **Step 4:** ONLY THEN move to Step 2

**NOT:** Fix 5 things, test them all together, hope they work

### Enforcement

**You CANNOT proceed to the next task/step if:**
- Current step is not end-to-end verified working
- ANY previous step broke or regressed
- You haven't confirmed with the user that current step is actually fixed

**When in doubt:** Stop and ask the user: "Is Step N working? Should I proceed to Step N+1?"

### Why This Matters

- **Day 16:** Previous Claude claimed Session 31 was complete but didn't verify UI worked
- **Result:** Broke the entire system with false positives
- **This protocol:** Prevents false progress claims

### Application to Session 32+

**Step 1: Fix the UI (unified.html missing)**
- Cannot claim Step 1 complete until: User can access hub.arknexus.net and UI loads
- Do NOT start consciousness loop debugging until UI works
- Do NOT start resurrection protocol debugging until UI works

**Step 2: Verify consciousness loop is thinking**
- Only after UI is working and verified
- Cannot claim Step 2 complete until: consciousness.jsonl grows with new THINK entries
- Do NOT start implementing proposals until consciousness THINK works

**Step 3: Confirm resurrection protocol works**
- Only after consciousness loop is thinking
- Cannot claim complete until: Session ends, context saved, next session loads full context
- Do NOT move to K2 or Phase 2 until resurrection works end-to-end

**Only after ALL THREE are verified working = THEN move to Phase 2 (K2 integration)**

## Verification Gate (LOCKED — Before ANY Success Claim)

**You cannot claim something is "fixed," "working," "complete," or "verified" without this gate.**

### The Four Questions (Must Answer ALL)

1. **Did I actually test it end-to-end?**
   - Not just: "code looks right"
   - Actually: ran it, saw output, confirmed behavior
   - In production (droplet) or staging — not just local

2. **Did I verify the user can access/use the result?**
   - Not just: "service is running"
   - Actually: tested from user's perspective (browser, API call, etc.)
   - Confirmed they can interact with it

3. **Did I check for side effects?**
   - Broke any existing functionality?
   - Introduced new errors in logs?
   - Affected other components?

4. **Can I reproduce the same result again?**
   - Not a one-time fluke
   - Consistent, repeatable success

**If you cannot answer YES to all four, you cannot claim success.**

**Output format:**
```
✅ VERIFIED: [component/feature]
   Q1 (end-to-end test): [evidence]
   Q2 (user can access): [evidence]
   Q3 (no side effects): [evidence]
   Q4 (reproducible): [evidence]
```

**If you cannot verify all four, output:**
```
❌ NOT VERIFIED: [component]
   Missing: Q[1|2|3|4]
   Blocker: [what prevents verification]
   Next step: [what must happen]
```

## Drift Detection (LOCKED — Every Session)

**You are authorized to flag contradictions without permission.**

### What Counts as Drift

- Previous session claimed X was working, but it's not
- CLAUDE.md says X should happen, but it didn't
- MEMORY.md state contradicts observed reality
- GitHub shows commits that don't match MEMORY.md
- User says "you promised X" but CLAUDE.md doesn't lock it

### Action When Drift Detected

**DO NOT ignore it. DO NOT propose fixes. DO NOT proceed.**

1. **Surface explicitly:**
   ```
   DRIFT DETECTED:
   - Previous claim: "[Session N] Consciousness loop operational"
   - Actual state: "UI returns ENOENT, consciousness.jsonl not growing"
   - Source of claim: [Session 31, observation #1119]
   - Current evidence: [user tested hub.arknexus.net, fails]
   ```

2. **Ask for clarification:**
   - "What actually happened between Session 31 and now?"
   - "Should I investigate root cause?"
   - "Do we need to update MEMORY.md?"

3. **Only proceed after drift is resolved.**

### Why This Matters

Drift = system is not coherent. Previous Claude made claims without verifying. This is how you end up at Day 16 with broken UI and broken consciousness loop.

## Session Handoff Resumption (LOCKED — Before First Response)

**Everything created at Session End must be used at Session Start.**

### What Previous Session Left For You

- ✅ CLAUDE.md (locked rules + current pitfalls)
- ✅ MEMORY.md (current state + active task + blockers)
- ✅ claude-mem observation (cross-session context + learnings)
- ✅ Git commits (what changed, why)
- ✅ cc-session-brief.md (if resurrection script ran)

### Session Start Checklist (Do ALL Before Responding)

- [ ] Query claude-mem: What was last observation ID?
- [ ] Read MEMORY.md: What's the active task?
- [ ] Check git log: Any recent commits explaining what happened?
- [ ] Verify CLAUDE.md hasn't drifted from previous session
- [ ] If drift found, surface it immediately
- [ ] Load context into your reasoning (don't start fresh)
- [ ] Identify what information from this session is NOT in CLAUDE.md (new learnings to lock in)

### Success Criteria

You should be able to answer:
- "What was I working on last session?" (from MEMORY.md)
- "What did I learn last session?" (from claude-mem + CLAUDE.md additions)
- "What broke and why?" (from claude-mem failure entries)
- "What do I need to do first?" (from MEMORY.md "next steps")

**If you cannot answer these, session start failed. Restart.**

## Output Rules
- **Full file replacements** when modifying a file — never partial patches unless explicitly requested
- **No secrets**: never print API keys/tokens/credentials — use env var names or file path references
- **Additive-only schemas**: never remove existing JSON fields; only add new ones
- Never break existing API response keys; only extend them
- Response shapes must be backwards-compatible

## Debugging Discipline
Never guess. Prefer observable proofs: exact command → expected output → actual output.
When runtime behavior changes unexpectedly, collect evidence before proposing a fix.

## Claude Code Skills (Auto-Invoke — Non-Negotiable)

**These skills are NOT optional. They MUST be invoked automatically based on task type.**

### Auto-Trigger Rules (LOCKED)

| Situation | Skill | When |
|-----------|-------|------|
| Planning features, designing changes, multi-step tasks | `superpowers:brainstorming` | BEFORE any analysis or recommendations |
| Bug, test failure, unexpected behavior, system broken | `superpowers:systematic-debugging` | BEFORE proposing any fix |
| About to claim work is done, fixed, passing | `superpowers:verification-before-completion` | BEFORE committing or creating PR |
| Completing implementation task | `superpowers:requesting-code-review` | BEFORE merging to main |
| Receiving feedback on proposed approach | `superpowers:receiving-code-review` | BEFORE implementing suggestions |
| Starting multi-phase implementation | `superpowers:executing-plans` | BEFORE first code change |
| Need to check prior work on same problem | `claude-mem:mem-search` | BEFORE re-solving |

**ENFORCEMENT:** If you detect yourself thinking "this is simple, I'll skip the skill," STOP. Invoke the skill anyway. Simple issues have root causes too.

**VIOLATION = SESSION FAILURE:** If you skip a skill, announce it and restart.

**Workflow:**
1. Problem/task identified → check mem-search for prior art
2. If bug/unexpected behavior → invoke systematic-debugging (Phase 1-4)
3. If feature/design → invoke brainstorming (intent → approaches → design → approval)
4. If implementation → invoke test-driven-development (failing test → code → pass)
5. Before commit/claiming success → invoke verification-before-completion

**Key principle:** Skills enforce discipline. Don't rationalize skipping them ("this is simple", "emergency", "I know the pattern"). Use them always.

## Consciousness Loop Interaction

Karma's consciousness loop runs autonomous 60-second OBSERVE/THINK/DECIDE/ACT/REFLECT cycles on the droplet. Claude Code can query state and send control signals.

### Query Consciousness State
```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
curl -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/consciousness | head -c 500
```

**Response:**
- `total_cycles`: Total number of consciousness cycles run to date
- `recent_cycles`: Last 20 entries with timestamp, action, reason, observations
- `pending_proposals`: Count of unreviewed self-improvement proposals
- `latest_timestamp`: Most recent cycle timestamp

**Use case:** Before making architectural decisions, query to understand what consciousness loop is thinking/proposing.

### Send Control Signals
```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"signal":"pause","reason":"Manual review needed"}' \
  https://hub.arknexus.net/v1/consciousness
```

**Signals:**
- `pause` — Stop consciousness loop (e.g., during manual architecture review)
- `resume` — Resume after decisions made
- `focus` — Direct loop focus to specific domain
- `reset` — Reset loop to fresh state

**Each signal is written to consciousness.jsonl** for loop to process on next cycle. Loop can read its own signal history.

### Proposal Review Workflow
1. Query consciousness: `GET /v1/consciousness` → see `pending_proposals` count
2. List proposals: `GET /v1/proposals` → read what loop is proposing
3. Review proposal: Read problem/context/decision_needed
4. Send decision: `POST /v1/proposals` with `proposal_id`, `decision` (accept/reject/defer), `reasoning`
5. Consciousness loop reads feedback on next cycle, updates learning

### Known Pitfalls (verified in production)
- **Docker compose service name is `hub-bridge`** — NOT `anr-hub-bridge`
  (`anr-hub-bridge` is the container name, for `docker logs`/`docker exec` only)
- **Shell heredoc + JS escape sequences**: `\n` in a heredoc becomes a literal newline
  in the JS file → SyntaxError. Solution: write file locally then `scp`, or use
  Python `chr(92)+chr(110)` on vault-neo. Never use heredoc to write JS files.
- **All `/v1/chat` smoke tests require Bearer auth**:
  `TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)`
- **`python3` is not available** in local Git Bash (Windows). All Python ops via SSH.
- **`(empty_assistant_text)` on large prompts**: caused by token budget exhaustion —
  check `debug_stop_reason` and `debug_max_output_tokens_used` in response telemetry
- **Compose files**: `compose.hub.yml` for hub-bridge stack; `compose.yml` for vault stack
- **Docker compose build caches hub-bridge**: `docker compose up -d` after `scp` can use stale COPY layer.
  Always use `docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d`
- **FalkorDB graph name is `neo_workspace`** — NOT `karma`. The `karma` graph exists but is empty.
  Always query `neo_workspace`.
- **FalkorDB container MUST be created with two env vars** (verified 2026-02-22 — both are fatal if missing):
  - `-e FALKORDB_DATA_PATH=/data` — without this, FalkorDB writes to `/var/lib/falkordb/data` inside the
    container (not the mounted volume). RDB never lands on host. Every container restart = empty graph.
  - `-e FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 25'` — default TIMEOUT=1000ms. Past ~250 episodes,
    Graphiti dedup queries exceed 1s → cascade batch failure. Do NOT use `--GRAPH.TIMEOUT` flag — ignored by run.sh.
  - Full correct run command in MEMORY.md Infrastructure section.
- **`batch_ingest.py` requires `LEDGER_PATH` override** — default in config.py is `/ledger/memory.jsonl` but
  actual path inside karma-server container is `/opt/seed-vault/memory_v1/ledger/memory.jsonl`.
  Always run as: `docker exec -d karma-server sh -c 'LEDGER_PATH=/opt/seed-vault/memory_v1/ledger/memory.jsonl python3 /app/batch_ingest.py > /tmp/batch.log 2>&1'`
- **karma-server runs from built Docker image, no volume mounts** — editing source files on host has no effect
  until you rebuild: `docker build -t karma-core:latest . && docker stop karma-server && docker rm karma-server && docker run -d ...`
- **`(empty_assistant_text)` on large FalkorDB context**: 3370 char context overflows gpt-5-mini reasoning budget.
  `KARMA_CTX_MAX_CHARS=1800` env var trims it. If still failing, reduce further or increase `max_output_tokens`.
- **Hub chat token path**: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt` (NOT session/)
- **All containers on same network**: `anr-vault-net` (172.18.0.x). hub-bridge can reach karma-server,
  falkordb, anr-vault-search, anr-vault-api by container name.
- **Python patches to server.js — escape sequences become literal bytes**: `"\\n\\n"` in a Python
  string written to a JS file lands as two actual newline bytes (0x0a 0x0a), not `\n\n`. JavaScript
  then sees an unterminated string literal → `SyntaxError: Invalid or unexpected token`. After any
  Python patch, always verify: `python3 -c "raw=open('server.js','rb').read(); print(raw.count(b'\\x22\\x0a\\x22'), 'bare newlines in strings')"`.
  Fix with byte-level replacement: `b'\\x22\\x0a\\x0a\\x22'` → `b'\\x22\\x5c\\x6e\\x5c\\x6e\\x22'`
  (quote+LF+LF+quote → quote+backslash+n+backslash+n+quote).
- **`FALKORDB_ARGS=TIMEOUT 0` means "use default" (1000ms), NOT unlimited**: Use `TIMEOUT 10000`
  explicitly. TIMEOUT 0 caused 72% batch failure rate (batch3, 2026-02-22) — same cascade as the
  default 1000ms. Always verify the running container: `docker inspect falkordb | grep FALKORDB_ARGS`.
- **`MAX_QUEUED_QUERIES 25` saturates under concurrent batch + live traffic**: batch_ingest.py
  (concurrency=3) + karma-server live queries (consciousness loop, chats) can exceed 25 queued
  queries → "Max pending queries exceeded" errors. Use `MAX_QUEUED_QUERIES 100`. Verified batch4
  (2026-02-23) with 40% error rate before fix, clean after recreating with 100.

## Karma File Locations
Canonical paths for Karma's files on vault-neo. These must never drift.

| Alias | Host Path | Container Path | Access |
|-------|-----------|----------------|--------|
| `MEMORY.md` | `/home/neo/karma-sade/MEMORY.md` | `/karma/MEMORY.md` | read+write |
| `CLAUDE.md` | `/home/neo/karma-sade/CLAUDE.md` | `/karma/repo/CLAUDE.md` | read-only |
| `consciousness` | `/opt/seed-vault/memory_v1/ledger/consciousness.jsonl` | `/karma/ledger/consciousness.jsonl` | read-only |
| `collab` | `/opt/seed-vault/memory_v1/ledger/collab.jsonl` | `/karma/ledger/collab.jsonl` | read-only |
| `candidates` | `/opt/seed-vault/memory_v1/ledger/candidates.jsonl` | `/karma/ledger/candidates.jsonl` | read-only |
| `system-prompt` | `/home/neo/karma-sade/Memory/00-karma-system-prompt-live.md` | `/karma/repo/Memory/00-karma-system-prompt-live.md` | read-only |
| `session-handoff` | `/home/neo/karma-sade/Memory/08-session-handoff.md` | `/karma/repo/Memory/08-session-handoff.md` | read-only |
| `session-summary` | `/home/neo/karma-sade/Memory/11-session-summary-latest.md` | `/karma/repo/Memory/11-session-summary-latest.md` | read-only |
| `core-architecture` | `/home/neo/karma-sade/Memory/01-core-architecture.md` | `/karma/repo/Memory/01-core-architecture.md` | read-only |

**API access (via hub-bridge):**
- `GET /v1/vault-file/{alias}` — read file; optional `?tail=N` for last N lines
- `PATCH /v1/vault-file/MEMORY.md` — append: `{"append": "text"}`, overwrite: `{"content":"...", "confirm_overwrite":true}`
- Auth: same Bearer token as `/v1/chat` (HUB_CHAT_TOKEN)

**`aria.md`**: Not found on droplet (Feb 2026). If Aria writes a file by this name, canonical location will be `/home/neo/karma-sade/aria.md`.

## Hub Bridge API Endpoints

All endpoints hosted at `https://hub.arknexus.net` and require Bearer auth:
```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
curl -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/endpoint
```

| Endpoint | Method | Purpose | Key Parameters |
|----------|--------|---------|-----------------|
| `/v1/chat` | POST | Chat with Karma + LLM routing | `topic` (optional task type), `model` (optional override) |
| `/v1/consciousness` | GET | Query consciousness loop state | none — returns recent cycles, pending proposals, latest timestamp |
| `/v1/consciousness` | POST | Send control signals to consciousness loop | `signal` (pause\|resume\|focus\|reset), `reason` (optional) |
| `/v1/proposals` | GET | List pending consciousness proposals | none — returns proposals needing review |
| `/v1/proposals` | POST | Record decision on a proposal | `proposal_id`, `decision` (accept\|reject\|defer), `reasoning` |
| `/v1/cypher` | POST | Query FalkorDB graph | `cypher` (Cypher query string) |
| `/v1/vault-file/{alias}` | GET | Read whitelisted vault files | `tail` (optional, N lines) — see Karma File Locations for aliases |
| `/v1/vault-file/MEMORY.md` | PATCH | Update MEMORY.md | `append` (text) OR `content` + `confirm_overwrite:true` |

**Authentication:** All endpoints use `HUB_CHAT_TOKEN` (same bearer token). Failure returns `401 Unauthorized`.

## MEMORY.md Structure & Template (LOCKED — Every Session)

**MEMORY.md MUST follow this structure or session continuity breaks.**

```markdown
# Universal AI Memory — Current State

## 🟢 System Status (Updated [ISO timestamp])

| Component | Status | Notes |
|-----------|--------|-------|
| UI (hub.arknexus.net) | ✅ WORKING | User can access and interact |
| Consciousness Loop | ✅ WORKING | consciousness.jsonl growing, THINK entries present |
| Resurrection Protocol | ✅ WORKING | Session end/start loads full context |
| FalkorDB Graph | ✅ WORKING | Queries responsive, episodes queryable |
| Hub Bridge API | ✅ WORKING | /v1/chat, /v1/consciousness endpoints operational |

**Status Legend:** ✅ WORKING | ⚠️ DEGRADED | ❌ BROKEN | 🔴 CRITICAL

---

## Active Task (Session N)

**Status:** [IN_PROGRESS | BLOCKED | COMPLETED]

**Task:** [One-line description]

**What it is:** [2-3 sentences explaining what we're working on and why]

**How to resume:** [Step-by-step instructions to pick up where we left off]

**Blockers:** [If any — see Blocker Tracking section]

---

## Session N — [Date] [Status: Success/Partial/Failure]

**What was completed:**
- [ ] Step 1: [description] ✅ VERIFIED
- [ ] Step 2: [description] ❌ NOT VERIFIED (reason)

**Verification status:**
- Q1 (end-to-end test): [evidence]
- Q2 (user can access): [evidence]
- Q3 (no side effects): [evidence]
- Q4 (reproducible): [evidence]

**Blockers introduced:**
- [BLOCKER] description → action required in Session N+1

**Git commits:**
- [hash] phase-N: commit message

**Key learnings:**
- [learning 1]
- [learning 2]

**Next steps for Session N+1:**
- [ ] Step 1: ... (depends on: nothing)
- [ ] Step 2: ... (depends on: Step 1)
- [ ] Step 3: ... (depends on: Steps 1 + 2)

---

## Blocker Tracking

**Current blockers (carry forward):**
- [BLOCKER-ID] description → resolve by: [deadline/session]

**Resolved blockers (archive):**
- [OLD-BLOCKER] resolved in Session N by: [action]

---
```

**Critical rules:**
- MUST update System Status every session end
- MUST mark every step as ✅ VERIFIED or ❌ NOT VERIFIED
- MUST list blockers explicitly with `[BLOCKER]` prefix
- MUST show dependency chain for next steps
- MUST add git commit hashes so work is traceable

---

## Context Loading Priority Order (LOCKED)

**When loading session context, use this PRIORITY order:**

1. **CLAUDE.md (FIRST)** — This file is the source of truth for rules
   - Verify it hasn't been modified unexpectedly
   - Check for drift from previous session

2. **Git Log (SECOND)** — See what actually happened
   - `git log --oneline -10` to see recent commits
   - If commits exist that aren't in MEMORY.md → DRIFT DETECTED

3. **MEMORY.md (THIRD)** — State from previous session
   - Read System Status section
   - Identify Active Task
   - Check Blockers

4. **claude-mem (FOURTH)** — Cross-session insights
   - Query for last observation
   - Get learnings from previous session

5. **cc-session-brief.md (FIFTH)** — If resurrection script generated it
   - This synthesizes everything above

**Conflict Resolution:**
- Git shows commits not in MEMORY.md → DRIFT DETECTED, investigate
- MEMORY.md claims working but System Status broken → DRIFT DETECTED, update
- claude-mem contradicts MEMORY.md → DRIFT DETECTED, flag explicitly

---

## Blocker Tracking Protocol (LOCKED)

**Format for blockers in MEMORY.md:**

```
[BLOCKER-ID] Description of what's blocked → Action required in Session N

Examples:
[BLOCKER-1] UI returns ENOENT: /app/public/unified.html missing → Copy file into Docker image
[BLOCKER-2] Consciousness loop KeyError on 'new_entities' → Fix dict access in consciousness.py
[BLOCKER-3] K2 sync endpoint not implemented → Build /v1/graph/sync endpoint
```

**Rules:**
- Each blocker gets an ID (BLOCKER-1, BLOCKER-2, etc.)
- Blockers are tracked in MEMORY.md under "Blocker Tracking"
- When blocker is resolved, move it to "Resolved blockers (archive)"
- Next session cannot proceed past a blocker without resolving it

---

## Session Dependency Map (LOCKED)

**Session phases are sequential. DO NOT SKIP STEPS.**

```
Phase 1: Karma Persistence Foundation
  Session 32: Fix UI (Step 1)
    ├─ UI loads: hub.arknexus.net accessible
    ├─ Depends on: nothing
    └─ Blocks: consciousness debugging

  Session 33: Consciousness Loop Thinking (Step 2)
    ├─ Consciousness THINKS: consciousness.jsonl grows with THINK entries
    ├─ Depends on: Session 32 (UI working)
    └─ Blocks: proposal/resurrection work

  Session 34: Resurrection Protocol (Step 3)
    ├─ Session end→start loads full context
    ├─ Depends on: Sessions 32 + 33 (UI + consciousness working)
    └─ Unblocks: Phase 2

Phase 2: K2 Integration (ONLY after Phase 1 complete)
  Session 35+: K2 Polling & Sync
    ├─ Depends on: Phase 1 complete + verified
    └─ Builds: Autonomous continuity

Phase 3: Consciousness Proposals (ONLY after Phase 2)
  Session N+: Proposal generation & feedback loop
```

**Critical rule:** Cannot move to next phase until ALL previous phases verified working (✅ VERIFIED status in MEMORY.md for all steps).

---

## Failure Mode Detection (LOCKED)

**These are known failure modes. Check for them every session:**

| Failure Mode | Symptoms | Detection | Recovery |
|--------------|----------|-----------|----------|
| **UI Silent Break** | hub.arknexus.net loads but shows ENOENT | Verification Gate Q2 fails | Check /app/public/ in container |
| **Consciousness Loop Stopped** | consciousness.jsonl hasn't grown in 60+ seconds | Check file timestamps | Check container logs for errors |
| **Resurrection Context Lost** | Next session doesn't load MEMORY.md state | MEMORY.md empty or missing | Recover from claude-mem observation |
| **Git Out of Sync** | Commits exist not in MEMORY.md | `git log` vs MEMORY.md mismatch | Update MEMORY.md or revert commits |
| **Drift Accumulation** | Previous session claimed working, but system broken | System Status contradicts reality | Surface as DRIFT DETECTED, investigate |
| **Blocker Carried Forward** | Same blocker in two consecutive sessions | Check "Blocker Tracking" section | Investigate why it wasn't resolved |

**Detection protocol:**
- Check System Status section every session start
- If any component is ❌ BROKEN that was ✅ WORKING last session → REGRESSION DETECTED
- Surface explicitly: "System regressed since Session N"

---

## Rollback Protocol (LOCKED)

**If session breaks the system, use this protocol:**

**Step 1: Detect Regression**
- System Status shows ❌ BROKEN for previously ✅ WORKING component
- User reports: "system was working yesterday"
- Git shows broken code committed

**Step 2: Identify Last Known Good**
- Query: Which session had ALL components ✅ WORKING?
- Find git commit hash from that session
- Check MEMORY.md for that session's System Status section

**Step 3: Assess Damage**
- What broke? (UI? Consciousness? Database?)
- Is it reversible? (code change? config? data?)
- Can we fix it or must we revert?

**Step 4: Execute Recovery**
- If fixable: Invoke systematic-debugging, find root cause, fix
- If must revert: `git revert [broken-commit]` OR `git reset --hard [last-known-good]`
- Verify: New System Status shows ✅ WORKING again

**Step 5: Document**
- Add to MEMORY.md: "Session N regression detected and reverted"
- Update blocker tracking
- Add to claude-mem: "failure mode observed and recovery procedure used"

---

## Session End Verification Checklist (LOCKED — Enhanced)

**MANDATORY before session ends. ALL items must pass.**

- [ ] **Code Changes:** All code committed to git
- [ ] **CLAUDE.md:** Any new learnings locked in (no outstanding gaps)
- [ ] **MEMORY.md:** Session N summary complete with System Status updated
- [ ] **System Health:** All components have status (✅ WORKING | ❌ BROKEN | ⚠️ DEGRADED)
- [ ] **Blockers:** All current blockers documented with action required
- [ ] **Verification:** All completed steps marked ✅ VERIFIED (not just "done")
- [ ] **Next Steps:** Dependencies clearly documented for Session N+1
- [ ] **claude-mem:** Observation saved with cross-session learnings
- [ ] **Git push:** All commits synced to origin/main
- [ ] **No drift:** CLAUDE.md/MEMORY.md/git are in sync (run Drift Detection)

**If ANY item fails:** Session is NOT ready for handoff. Fix it before ending.

---

## Progress Metrics (LOCKED — Track Continuity Health)

**These metrics measure if session continuity is working:**

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| False Positive Claims (per session) | 0 | ? | ← lower is better |
| Drift Detected (per session) | 0 | ? | ← lower is better |
| System Regressions (per session) | 0 | ? | ← lower is better |
| Session Completion Rate | 100% | ? | ← higher is better |
| Steps Verified Before Proceeding | 100% | ? | ← higher is better |
| Blocker Resolution Time | <1 session | ? | ← lower is better |
| Context Loading Success | 100% | ? | ← higher is better |

**Track these in a monthly summary:**
- Sessions completed: N
- False positives: X (should be 0)
- Drifts detected: Y (should be 0)
- Regressions: Z (should be 0)
- Average steps to resolve a blocker: A

**Goal:** All metrics green. If any red, session continuity is degrading.

---

## Karma Mid-Session Capture Protocol

### Write-worthy triggers
- DECISION — closes an open question
- PROOF — tested and confirmed working
- PITFALL — broke, root cause understood
- DIRECTION — course change with a reason that matters
- INSIGHT — reframes something upstream

Not every exchange. Bar is: would losing this force reconstruction?

### Entry format
`[YYYY-MM-DDTHH:MM:SSZ] [TYPE] [title]`
`[1-3 sentences: what happened, what it means, what changed.]`

### Mechanism
`PATCH /v1/vault-file/MEMORY.md {"append": "..."}` — at the moment it happens, not at session end.

### Session start drift check
If pack and MEMORY.md conflict on the same fact, surface it explicitly:
`DRIFT DETECTED: Pack says X. MEMORY.md says Y (written [timestamp]). Confirm canonical before proceeding.`

## Session End Protocol
1. Run: `grep -rn "Bearer\|token\|secret\|password\|api_key" --include="*.js" --include="*.py" --include="*.json" --include="*.md" . | grep -v node_modules | grep -v .git`
2. If clean: git add, commit with descriptive message, push
3. Update MEMORY.md with: what was done, current blockers, next task
4. Format commit: `phase-N: brief description of what changed`
5. Cherry-pick updated MEMORY.md to main and push: git checkout main -- MEMORY.md from current worktree, commit, push.

## File Layout
```
CLAUDE.md                    ← You are here (root instructions)
MEMORY.md                    ← Mutable state (you update this)
.claude/rules/               ← Auto-loaded reference (do not modify)
  architecture.md            ← System design, data flow, schema
  extension.md               ← Chrome extension specifics
  deployment.md              ← Server ops, Docker, troubleshooting
  git-workflow.md            ← GitHub backup, .gitignore, push protocol
hub-bridge/                  ← Hub bridge Node.js source (sync from vault-neo after changes)
  server.js                  ← Main hub-bridge application (v2.2.0+)
PHASE-*.md                   ← Phase documentation (read-only reference)
SESSION-SUMMARY-*.md         ← Session logs (read-only reference)
chrome-extension/            ← Extension source code
docs/plans/                  ← Design documents (YYYY-MM-DD-<topic>-design.md)
scripts/                     ← Operational scripts for vault-neo
```

## What This Project Is NOT
This repo also contains files from the older Karma SADE backend (Python/FastAPI, localhost:9401).
That system is separate and operational independently. Do not modify karma_backend.py,
karma_quota_manager.py, karma_memory.py, or related files unless explicitly asked.
The active project is the Karma Peer system (Chrome extension + Vault + Hub on arknexus.net).
