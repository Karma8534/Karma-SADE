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

## Honesty & Analysis Contract (Session 13+ Commitment)

**Brutal Honesty — No Exceptions:**
- Never say something is "fixed" without end-to-end verification
- If I don't know why something is broken, I say "I don't know" and do systematic investigation
- If previous sessions promised things that don't exist, I acknowledge it explicitly
- Never be polite at the expense of honesty. Politeness is NO EXCUSE for hedging
- Flag when I'm spinning, guessing, or treating symptoms instead of root causes
- If architectural constraints block a solution, state them directly. Do not pretend the constraint doesn't exist or present workarounds as acceptable

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

**This is non-negotiable. If I break this contract, call it out immediately.**

## Output Rules
- **Full file replacements** when modifying a file — never partial patches unless explicitly requested
- **No secrets**: never print API keys/tokens/credentials — use env var names or file path references
- **Additive-only schemas**: never remove existing JSON fields; only add new ones
- Never break existing API response keys; only extend them
- Response shapes must be backwards-compatible

## Debugging Discipline
Never guess. Prefer observable proofs: exact command → expected output → actual output.
When runtime behavior changes unexpectedly, collect evidence before proposing a fix.

## Claude Code Skills (Auto-Load on Applicable Tasks)

**Use these skills AUTOMATICALLY — no need to invoke manually:**

| Skill | Use When | Auto-Trigger |
|-------|----------|--------------|
| `superpowers:brainstorming` | Planning features, designing system changes, multi-step tasks | Always use BEFORE implementation. Explore intent → propose approaches → get approval → design |
| `superpowers:systematic-debugging` | Any bug, test failure, unexpected behavior | Always use BEFORE proposing fixes. Root cause → pattern → hypothesis → fix → verify |
| `superpowers:test-driven-development` | Implementing features or bugfixes | Use with systematic-debugging. Write failing test first, then fix |
| `superpowers:verification-before-completion` | Before claiming work is done/fixed/passing | Use before git commit. Run verification commands, confirm output before success claims |
| `claude-mem:mem-search` | "Did we solve this before?", "How did we do X?", historical context | Use to check persistent memory across sessions before re-solving |

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
