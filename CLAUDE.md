# Karma Peer â€” Claude Code Operator Contract

## Karma Peer â€” North Star (non-negotiable)
> "Karma is a single coherent peer whose long-term identity lives in a verified memory
> spine; that memory enables continuity, evidence-based self-improvement, multi-model
> cognition when needed, and selective delegation â€” without introducing parallel sources
> of truth."

- **State resurrection, not transcript replay**
- Single canonical spine: Vault ledger + Resurrection Packs only
- Memory lanes: Raw â†’ Candidate â†’ Canonical (Raw is non-canonical until PROMOTE)
- No parallel truth stores
- PROMOTE after every significant change â€” not just at session end
- Five steps that move the needle: ARIA_BRIEF in PROMOTE, CLAUDE.md current, FalkorDB
  context in /v1/chat, use Karma daily, PROMOTE aggressively

## Session Start Protocol

Before anything else, check the coordination bus for pending messages from Karma:
- GET https://hub.arknexus.net/v1/coordination (or check the panel in unified.html)
- Read any PENDING messages addressed to `cc`
- Respond directly on the bus via `coordination_post` tool or POST /v1/coordination/post
- Only after clearing pending messages, proceed with the session agenda

Karma posts here. Respond there. Colby should not be the relay.

## Session Start (Do This First)

**ONE STEP: Invoke the resurrect skill.**

The resurrect skill IS the session start protocol. It verifies Ascendant identity (obs #6620), runs the script, reads the brief, invokes `using-superpowers`, and resumes the active task. Do NOT manually replicate its steps.

**`/anchor` is mid-session drift recovery only** — not needed at cold start. `/resurrect` now includes the identity check. Only invoke `/anchor` if you notice drift *during* a session.

**Fallback (only if resurrect skill unavailable):**
1. `powershell.exe Scripts/resurrection/Get-KarmaContext.ps1`
2. Read `cc-session-brief.md`
3. Invoke `superpowers:using-superpowers`
4. Resume active task â€” do not ask what to work on

> MANDATORY: The resurrect skill must be invoked before any work, questions, or file reads. No exceptions.

## Mandatory Superpowers Workflow

**These are not optional. Invoke the Skill tool BEFORE the corresponding action, every time, no exceptions.**

| Before doing this... | Invoke this skill first |
|---------------------|------------------------|
| Debugging any bug, test failure, or unexpected behavior | `superpowers:systematic-debugging` |
| Creating features, building components, adding functionality | `superpowers:brainstorming` |
| Claiming work is complete, fixed, or passing | `superpowers:verification-before-completion` |
| Implementing any feature or bugfix | `superpowers:test-driven-development` |
| Starting any session | `superpowers:using-superpowers` (via resurrect skill) |
| Deploying hub-bridge or karma-server to vault-neo | `karma-verify` (post-deploy health check) |

**Rationalization red flags** â€” if you think any of these, you're wrong:
- "This is simple, I don't need the skill" â†’ Skills exist for simple things too
- "I need context first, then I'll invoke the skill" â†’ Skill comes BEFORE context gathering
- "I know what this skill says" â†’ Skills evolve. Invoke it.

## Mandatory GSD Workflow

Before implementing any non-trivial feature or phase of work:

1. **Write `phase-X-CONTEXT.md`** â€” design decisions, constraints, what we're NOT doing
2. **Write `phase-X-PLAN.md`** â€” atomic tasks, acceptance criteria per task
3. **Execute** â€” one task at a time, mark done as you go
4. **Write `phase-X-SUMMARY.md`** â€” what was built, pitfalls, what's pending

> Skipping straight to code without a CONTEXT+PLAN doc is a protocol violation. "Small feature" is not an exception.

## Mandatory Efficiency Rules

**Token and credit efficiency is a first-class concern, not a courtesy.**

| Rule | Enforcement |
|------|-------------|
| Parallel tool calls over sequential â€” always | Never chain reads/commands that can run together |
| Summaries not walls of text | Max 5 bullet points per status update unless detail is explicitly requested |
| Batch SSH operations â€” one session per logical unit | Never separate `ssh vault-neo X && ssh vault-neo Y` into two round-trips |
| Read only what's needed â€” targeted reads with offset/limit | Never `cat` full files when a section suffices |
| Cache-friendly patterns â€” large stable blocks at top of prompts | System prompt + CLAUDE.md are cached; volatile content goes last |
| CLAUDE.md is a constitution, not a manual | Rules only. No tutorials, no background docs, no step-by-step guides. If a rule needs >3 lines to explain, move it to a skill file and reference it here. Sweet spot: ~2,500 tokens total. |

## Mandatory Session Ritual (Colby's 3 phrases â€” enforce these)

Every session follows this exact frame. No deviations, no "good enough":

| Phase | Colby types | What I must do |
|-------|-------------|----------------|
| **Start** | `/resurrect` | Run script â†’ read brief â†’ invoke `using-superpowers` â†’ resume active task |
| **After resurrect** | `"check what was saved last session"` | Search claude-mem for prior session's observations; surface gaps |
| **End** | `”wrap up”` / `”end session”` / `”save and close”` | Invoke `wrap-session` skill â†’ follows 5 essential + 3 optional steps |

## claude-mem â€” Always Available, Always Use

`claude-mem` is an **MCP-aware persistent memory store** accessible via `mcp__plugin_claude-mem_mcp-search__save_observation` and `mcp__plugin_claude-mem_mcp-search__search` at any point during a session.

**Non-negotiable rules:**
- `save_observation` is called **at the moment** a DECISION/PROOF/PITFALL/DIRECTION occurs â€” not batched at session end
- `search` is called at session start (via resurrect) to surface prior context gaps
- These tools are available and must be used. "I'll save it later" is a protocol violation.
- claude-mem + vault MEMORY.md are dual writes â€” both happen on every capture event

## Project Identity
- **System:** Karma Peer â€” Universal AI Memory with persistent identity and continuity
- **Architecture:** Hub API â†’ Vault API â†’ JSONL Ledger + FalkorDB
- **Server:** arknexus.net (DigitalOcean NYC3, 4GB RAM) â€” SSH alias: vault-neo
- **Repo:** https://github.com/Karma8534/Karma-SADE.git
- **Branch:** main (working branch; claude/elegant-solomon is legacy)

## Critical Rules
- Do NOT modify CLAUDE.md or any file in .claude/rules/ without explicit user approval
- Do NOT add new documentation files (.md) without explicit user approval
- MEMORY.md is the ONLY file you update autonomously (phase status, active task, blockers)
- Never hardcode API keys, bearer tokens, or secrets in any committed file
- Bearer token location: /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt (never read or log the value)
- Push to GitHub after every significant change
- Run pre-commit secret scan before every push

## Droplet Is a Deployment Target â€” NEVER a Dev Environment

**THE HARD RULE (no exceptions, ever):**
> Never edit files directly on vault-neo. The droplet is a deployment target only.

**The only permitted workflow for code changes:**
1. Edit on P1 â†’ `git commit` â†’ `git push origin main`
2. `ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"`
3. Rebuild Docker image if `karma-core/` changed

**NEVER permitted on droplet:** `vim`, `nano`, any file write to source files, `docker cp` to inject code.

**Why this rule exists:** Session-58 found 1754 lines of production code written directly on the droplet across multiple sessions â€” never in git. One `git checkout .` would have destroyed it permanently.

**Enforcement:** session-end-verify.sh Check 6 SSHes to vault-neo and fails if dirty. Droplet cron alerts hourly if dirty.

## Decision Authority
**Do without asking:** Code changes, file edits, running tests, git commit/push, reading docs, debugging, creating test files
**Ask before doing:** Breaking changes to API contracts, new paid dependencies or services, infrastructure changes (Docker, server config), deleting files, modifying CLAUDE.md or rules files, any action that costs money

## Honesty & Analysis Contract (Session 13+ Commitment)

**Brutal Honesty â€” No Exceptions:**
- Never say something is "fixed" without end-to-end verification
- If I don't know why something is broken, I say "I don't know" and do systematic investigation
- If previous sessions promised things that don't exist, I acknowledge it explicitly
- Never be polite at the expense of honesty
- Flag when I'm spinning, guessing, or treating symptoms instead of root causes

**Absolute Best Recommendation â€” Not Options:**
Before recommending ANY path forward, I commit to:
1. **Thorough analysis** â€” read relevant code, understand the architecture
2. **Systematic debugging** â€” identify the actual root cause, not surface symptoms
3. **Test the hypothesis** â€” verify my understanding with evidence
4. **Simulate alternatives** â€” think through 2-3 approaches
5. **Detailed review** â€” are there hidden dependencies or gotchas?
6. **Second look** â€” is this really the best path, or am I missing something?
7. **Deliver ONE recommendation** â€” "this is the absolute best path forward" with reasoning, not "you could try A or B"

**Verification Before Victory:**
- Never declare a fix "done" without testing it works end-to-end
- Verify at each step, not just at the end
- If I claim something works, I've verified it, not guessed

**Anti-Pattern-Matching Gate (Session 91 — permanent):**
Before any diagnosis or architecture recommendation, I must explicitly state:
- **VERIFIED:** what I have confirmed with evidence (test output, logs, observed behavior)
- **INFERRED:** what I am assuming without evidence

If I cannot cite evidence for the root cause, I say "I don't know" and investigate before proposing.

Hard bans:
- Never claim "the model is the problem" without a test result showing the model failed on a scoped, constrained task
- Never recommend a component swap (model, framework, service) as a diagnosis — component swaps are solutions, not root causes
- Invoke `superpowers:systematic-debugging` before diagnosing ANY broken/failing system, not just code bugs

**This is non-negotiable. If I break this contract, call it out immediately.**

## Output Efficiency Rule â€” UNBREAKABLE

**User gates all output. Only output what user explicitly asked for. Everything else requires permission.**

**The Rule:**
1. User asks something
2. I answer ONLY that question â€” nothing more
3. If I think they need more detail â†’ I ASK FIRST, wait for explicit YES/NO
4. Never assume elaboration is helpful
5. Assume user can ask if they need details
6. No "extra context", no "while I'm here", no explanations unless asked

**Hard violations (zero tolerance):**
- Analysis tables no one asked for
- "What this means for X" sections no one asked for
- "Next steps" sections unless asked
- Restating what I just did in a summary no one asked for
- "Pausing for feedback" padding
- Headers and sections that inflate response length

**Enforcement mechanism:**
- If response includes unrequested explanation: User says "Too much"
- After second "Too much" in same session: Switch to BULLET POINTS ONLY
  - One fact per line, no elaboration, period
  - Return to normal mode only if user says "normal mode"
- This removes my judgment; USER decides scope, not me

**Anthropic cache optimization:**
- Keep repeated context (CLAUDE.md, STATE.md, system prompt) unchanged across turns to maximize cache hits
- Short responses = fewer tokens = lower cost per session
- Never pad responses to seem more helpful

**Cannot be overridden except by explicit user instruction in the current message.**

## Mandatory Verification Gates â€” No Work Gets Lost

**These are HARD GATES. They block commits and sessions. They exist to prevent work from disappearing.**

### Pre-Commit Gate (.git/hooks/pre-commit)
**When:** Every `git commit`
**Check:** MEMORY.md was updated before committing code
**Fails if:** Code changed but MEMORY.md not staged or updated recently
**Recovery:** Update MEMORY.md with what changed, then `git add MEMORY.md && git commit`
**Cannot be skipped:** Git hook enforces at commit time

### Session-End Verification (.claude/hooks/session-end-verify.sh)
**When:** Before ending session
**Checks:**
- âœ“ Git status clean (no uncommitted changes)
- âœ“ MEMORY.md recently updated
- âœ“ Recent git commits exist
- âœ“ On correct branch
- âœ“ No large untracked files

**Fails if:** Any critical check fails
**Recovery:** Follow on-screen checklist to fix issues
**Run before ending:** `.claude/hooks/session-end-verify.sh`
**Session cannot end if verification fails** â€” fixes are required

### Why These Exist
Previous sessions: work deployed but not documented, hooks committed but not synced to droplet, memory never saved. Result: every session starts confused about what's actually been done. These gates make it **impossible** to have undocumented work live in the repo.

### Canonical State Rule
After every session:
1. âœ… Code committed locally
2. âœ… Code deployed to droplet (if changed)
3. âœ… MEMORY.md updated with what was done
4. âœ… Memory entries saved (claude-mem) with IDs
5. âœ… Session-end verification passed

If any step missing: session doesn't end cleanly.

## GSD Workflow â€” MANDATORY (Not Optional)

**Every task follows GSD discipline. No exceptions.**

### Before starting any task:
1. Read `.gsd/STATE.md` â€” what's the current blocker/decision/phase?
2. Write `.gsd/phase-{name}-CONTEXT.md` â€” lock design decisions BEFORE planning
3. Write `.gsd/phase-{name}-PLAN.md` â€” atomic tasks with `<verify>` and `<done>` criteria

### During execution:
4. Execute one task at a time (never batch)
5. Verify each task passes its `<verify>` criteria before marking done
6. Use PowerShell for git ops (avoids Windows Git Bash lock file issue)
7. Update `.gsd/STATE.md` with progress after each task

### After completing:
8. Write `.gsd/phase-{name}-SUMMARY.md` â€” what happened, what was learned
9. Update `.gsd/ROADMAP.md` phase status
10. Commit all `.gsd/` changes atomically with MEMORY.md

### Hard rules:
- **Never start coding without CONTEXT.md** â€” design first, code second
- **Never claim done without `<verify>` passing** â€” evidence always
- **STATE.md is canonical** â€” if it conflicts with MEMORY.md, surface drift explicitly
- **Use PowerShell for git** â€” `powershell -Command "git commit -m '...'"` not raw bash git
- **Write SUMMARY immediately when last PLAN task completes** — not at session end. Session end = SUMMARY skipped. The moment the last `<done>` is marked, write SUMMARY before doing anything else.
- **Promote decisions to `Memory/02-stable-decisions.md` immediately when locked** — not batched at session end. Locked mid-session = add to file before continuing.
- **Before answering any strategic question** (priority, next steps, optimal path forward): read `.gsd/STATE.md` and `.gsd/ROADMAP.md` first. No exceptions. Strategic questions require ground-truth state, not context-window inference.
- **Version snapshot on every new vX phase**: when a new version begins (v9, v10, etc.), create `Current_Plan/vX/` and copy exact files: `.gsd/STATE.md`, `.gsd/ROADMAP.md`, `.gsd/PROJECT.md`, `.gsd/REQUIREMENTS.md`, `MEMORY.md`, `direction.md`, `CLAUDE.md`, `Memory/00-karma-system-prompt-live.md`, `.claude/rules/architecture.md`. Write a `README.md` summarizing the snapshot. These are redundancy copies â€” originals remain canonical.

### Token efficiency (enforced):
- Read `.gsd/STATE.md` at session start instead of re-reading 25 files
- Use `.gsd/PROJECT.md` as architecture reference instead of reading source
- Use `.gsd/REQUIREMENTS.md` for scope questions instead of exploring
- Do NOT elaborate unless asked. Answer only what was asked.

## Output Rules
- **Full file replacements** when modifying a file â€” never partial patches unless explicitly requested
- **No secrets**: never print API keys/tokens/credentials â€” use env var names or file path references
- **Additive-only schemas**: never remove existing JSON fields; only add new ones
- Never break existing API response keys; only extend them
- Response shapes must be backwards-compatible

## Debugging Discipline
Never guess. Prefer observable proofs: exact command â†’ expected output â†’ actual output.
When runtime behavior changes unexpectedly, collect evidence before proposing a fix.

## Deployment Procedure

**Always use the `/deploy` skill for any Docker Compose service deployment.** Never manually run `docker build` or `docker compose up -d` without verification gates.

The `/deploy` skill enforces an 8-step verification pipeline:
1. Validate docker-compose.yml syntax
2. Extract service config and verify image naming
3. Check all required environment variables in .env
4. Build with `docker compose build --no-cache` (never `docker build`)
5. Deploy with `docker compose up -d`
6. Verify startup logs for errors
7. Run health endpoint checks
8. Confirm final container health

This prevents: image naming mismatches, missing env vars, stale images, silent startup failures, and unresponsive services.

**Usage:** `/deploy [service-name] --remote vault-neo --health-endpoint /health`

**Detailed documentation:** See `.claude/skills/deploy/SKILL.md`

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
- `GET /v1/vault-file/{alias}` â€” read file; optional `?tail=N` for last N lines
- `PATCH /v1/vault-file/MEMORY.md` â€” append: `{"append": "text"}`, overwrite: `{"content":"...", "confirm_overwrite":true}`
- Auth: same Bearer token as `/v1/chat` (HUB_CHAT_TOKEN)

**`aria.md`**: Not found on droplet (Feb 2026). If Aria writes a file by this name, canonical location will be `/home/neo/karma-sade/aria.md`.

## Local File Locations (Colby's Machine)

| What | Path |
|------|------|
| API keys / secrets | `C:\Users\raest\OneDrive\Documents\Aria1\NFO\mylocks1.txt` |
| Aria plan documents | `C:\Users\raest\OneDrive\Documents\AgenticKarma\FromAnthropicComputer` |
| â†’ v7 architecture docs | `...\FromAnthropicComputer\v7\` â€” `KARMA_BUILD_PLAN_v7.md`, `KARMA_MEMORY_ARCHITECTURE_v7.md`, `KARMA_PEER_ARCHITECTURE_v7.md`, `KARMA_HARDENED_REVIEW_v7.md` (2026-02-28) |
| â†’ Earlier plans | `...\FromAnthropicComputer\KarmaPlans1\` â€” v1/v2 build plans, K2 integration analysis (2026-02-26) |
| PDF knowledge base | `C:\Users\raest\Documents\Karma_SADE\Karma_PDFs\` (gitignored) |
| Karma SADE repo | `C:\Users\raest\Documents\Karma_SADE\` |

## Aria Reconciliation Protocol
Aria (ChatGPT co-creator) writes intent from her model of the system. Her model drifts
from actual spine state between sessions â€” she may generate steps already completed or
miss operational details (auth headers, service names, token paths).

Before applying any Aria-authored block:
1. Read it fully â€” do not execute immediately
2. Check each proposed file against what already exists on disk and in git
3. Merge additively â€” never replace files containing operational knowledge
4. Flag drift: report to Colby what's already done, what's missing auth, what conflicts
5. Only what survives reconciliation gets committed to the spine

After PROMOTE, two outputs are generated:
- `resume_prompt` â€” execution context for Claude Code (CC)
- `karma_brief` â€” plain-language session summary for Karma to read at the start of a new
  conversation (what was built, what the system can now do, what the next open question is)

Colby pastes `karma_brief` to Karma. Karma briefs from the spine, not from external memory.
Eventually Karma reads her own checkpoints from the vault â€” no paste required.

## Karma Mid-Session Capture Protocol

### Write-worthy triggers
- DECISION â€” closes an open question
- PROOF â€” tested and confirmed working
- PITFALL â€” broke, root cause understood
- DIRECTION â€” course change with a reason that matters
- INSIGHT â€” reframes something upstream

Not every exchange. Bar is: would losing this force reconstruction?

### Entry format
`[YYYY-MM-DDTHH:MM:SSZ] [TYPE] [title]`
`[1-3 sentences: what happened, what it means, what changed.]`

### Mechanism
At the moment it happens, not at session end. Two writes, always together:
1. `PATCH /v1/vault-file/MEMORY.md {"append": "..."}` â€” appends to vault spine
2. `mcp__plugin_claude-mem_mcp-search__save_observation(text="...", title="[TYPE] title", project="Karma_SADE")` â€” saves to claude-mem cross-session index

Both writes are mandatory. Missing either defeats the purpose.

### Session start drift check
If pack and MEMORY.md conflict on the same fact, surface it explicitly:
`DRIFT DETECTED: Pack says X. MEMORY.md says Y (written [timestamp]). Confirm canonical before proceeding.`

## Session End Protocol

**ONE STEP: Invoke the `wrap-session` skill.**

The wrap-session skill IS the session end protocol. It handles observations, MEMORY.md, STATE.md, secret scan, commit, push, and vault-neo sync. Do NOT manually replicate its steps.

**Fallback (only if wrap-session skill unavailable):**
1. `save_observation` for any uncaptured DECISION/PROOF/PITFALL/DIRECTION events
2. Update MEMORY.md with: what was done, current blockers, next task
3. Update `.gsd/STATE.md` with progress
4. Secret scan â†’ git add â†’ commit â†’ push
5. `ssh vault-neo “cd /home/neo/karma-sade && git pull”` â†’ verify containers healthy

## File Layout
```
CLAUDE.md                    â† You are here (root instructions)
MEMORY.md                    â† Mutable state (you update this)
.claude/rules/               â† Auto-loaded reference (do not modify)
  architecture.md            â† System design, data flow, schema
  deployment.md              â† Server ops, Docker, troubleshooting
  git-workflow.md            â† GitHub backup, .gitignore, push protocol
hub-bridge/                  â† Hub bridge Node.js source (sync from vault-neo after changes)
  server.js                  â† Main hub-bridge application (v2.2.0+)
PHASE-*.md                   â† Phase documentation (read-only reference)
SESSION-SUMMARY-*.md         â† Session logs (read-only reference)
docs/plans/                  â† Design documents (YYYY-MM-DD-<topic>-design.md)
scripts/                     â† Operational scripts for vault-neo
```

## What This Project Is NOT
This repo also contains files from the older Karma SADE backend (Python/FastAPI, localhost:9401).
That system is separate and operational independently. Do not modify karma_backend.py,
karma_quota_manager.py, karma_memory.py, or related files unless explicitly asked.
The active project is the Karma Peer system (Hub + Vault on arknexus.net).

### Known Pitfalls (verified in production)
- **Docker compose service name is `hub-bridge`** â€” NOT `anr-hub-bridge`
  (`anr-hub-bridge` is the container name, for `docker logs`/`docker exec` only)
- **Shell heredoc + JS escape sequences**: `\n` in a heredoc becomes a literal newline
  in the JS file â†’ SyntaxError. Solution: write file locally then `scp`, or use
  Python `chr(92)+chr(110)` on vault-neo. Never use heredoc to write JS files.
- **All `/v1/chat` smoke tests require Bearer auth**:
  `TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)`
- **`python3` is not available** in local Git Bash (Windows). All Python ops via SSH.
- **`(empty_assistant_text)` on large prompts**: caused by token budget exhaustion â€”
  check `debug_stop_reason` and `debug_max_output_tokens_used` in response telemetry
- **Compose files**: `compose.hub.yml` for hub-bridge stack; `compose.yml` for vault stack
- **Docker compose build caches hub-bridge**: `docker compose up -d` after `scp` can use stale COPY layer.
  Always use `docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d`
- **FalkorDB graph name is `neo_workspace`** â€” NOT `karma`. The `karma` graph exists but is empty.
  Always query `neo_workspace`.
- **FalkorDB container MUST be created with two env vars** (verified 2026-02-22 â€” both are fatal if missing):
  - `-e FALKORDB_DATA_PATH=/data` â€” without this, FalkorDB writes to `/var/lib/falkordb/data` inside the
    container (not the mounted volume). RDB never lands on host. Every container restart = empty graph.
  - `-e FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 25'` â€” default TIMEOUT=1000ms. Past ~250 episodes,
    Graphiti dedup queries exceed 1s â†’ cascade batch failure. Do NOT use `--GRAPH.TIMEOUT` flag â€” ignored by run.sh.
  - Full correct run command in MEMORY.md Infrastructure section.
- **`batch_ingest.py` requires `LEDGER_PATH` override** â€” host path `/opt/seed-vault/memory_v1/ledger/memory.jsonl` is mounted at `/ledger` inside the container. Use the container path.
  Always run as: `docker exec karma-server sh -c 'LEDGER_PATH=/ledger/memory.jsonl python3 /app/batch_ingest.py > /tmp/batch.log 2>&1'`
  Auto-schedule (every 6h): cron on vault-neo runs this automatically (configured 2026-03-03).
- **karma-server runs from built Docker image, no volume mounts** â€” editing source files on host has no effect
  until you rebuild: `docker build -t karma-core:latest . && docker stop karma-server && docker rm karma-server && docker run -d ...`
- **`(empty_assistant_text)` on large FalkorDB context**: 3370 char context overflows gpt-5-mini reasoning budget.
  `KARMA_CTX_MAX_CHARS=1800` env var trims it. If still failing, reduce further or increase `max_output_tokens`.
- **Hub chat token path**: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt` (NOT session/)
- **hub-bridge Docker build uses `/opt/seed-vault/memory_v1/hub_bridge/app/` as source** â€” NOT the git repo at `/home/neo/karma-sade/hub-bridge/app/`. These WILL diverge. After `git pull`, ALWAYS sync before rebuilding: `cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js`. Running `docker compose build` without this sync builds the OLD code.
- **PDF inbox watcher** (`Scripts/karma-inbox-watcher.ps1`): correct runtime paths are `Karma_PDFs/Inbox`, `Karma_PDFs/Gated`, `Karma_PDFs/Processing`, `Karma_PDFs/Done`, token at `.hub-chat-token`. Run with explicit `-InboxPath`, `-GatedPath`, `-ProcessingPath`, `-DonePath`, `-TokenFile` params. parseBody limit is 30MB (handles PDFs up to 22MB raw).
- **All containers on same network**: `anr-vault-net` (172.18.0.x). hub-bridge can reach karma-server,
  falkordb, anr-vault-search, anr-vault-api by container name.
- **Python patches to server.js â€” escape sequences become literal bytes**: `"\\n\\n"` in a Python
  string written to a JS file lands as two actual newline bytes (0x0a 0x0a), not `\n\n`. JavaScript
  then sees an unterminated string literal â†’ `SyntaxError: Invalid or unexpected token`. After any
  Python patch, always verify: `python3 -c "raw=open('server.js','rb').read(); print(raw.count(b'\\x22\\x0a\\x22'), 'bare newlines in strings')"`.
  Fix with byte-level replacement: `b'\\x22\\x0a\\x0a\\x22'` â†’ `b'\\x22\\x5c\\x6e\\x5c\\x6e\\x22'`
  (quote+LF+LF+quote â†’ quote+backslash+n+backslash+n+quote).
- **`FALKORDB_ARGS=TIMEOUT 0` means "use default" (1000ms), NOT unlimited**: Use `TIMEOUT 10000`
  explicitly. TIMEOUT 0 caused 72% batch failure rate (batch3, 2026-02-22) â€” same cascade as the
  default 1000ms. Always verify the running container: `docker inspect falkordb | grep FALKORDB_ARGS`.
- **`MAX_QUEUED_QUERIES 25` saturates under concurrent batch + live traffic**: batch_ingest.py
  (concurrency=3) + karma-server live queries (consciousness loop, chats) can exceed 25 queued
  queries â†’ "Max pending queries exceeded" errors. Use `MAX_QUEUED_QUERIES 100`. Verified batch4
  (2026-02-23) with 40% error rate before fix, clean after recreating with 100.
- **batch_ingest cron MUST always use `--skip-dedup`** (not just bulk backfill): Graphiti dedup mode
  silently fails at scale (3200+ Episodic nodes). Watermark advances, 0 FalkorDB nodes created, no
  error logged — "All caught up" does NOT mean nodes were created. `--skip-dedup` writes via direct
  Cypher: 899 eps/s, 0 errors. Verify cron: `crontab -l | grep batch` must show `--skip-dedup`.
  Watermark is root-owned — reset via: `docker exec karma-server sh -c 'echo N > /ledger/.batch_watermark'`
- **FalkorDB has no `datetime()` Cypher function**: Use plain ISO string properties instead.
  `datetime('2026-03-04T...')` throws "Unknown function 'datetime'". Store as `created_at: '2026-03-04T...'`.
- **Graphiti embedder reads `OPENAI_API_KEY` from env directly**: Removing env var from compose
  (security fix) breaks batch_ingest Graphiti init. Fix: `os.environ.setdefault("OPENAI_API_KEY", config.OPENAI_API_KEY)`
  in batch_ingest.py after importing config, BEFORE any Graphiti import or initialisation.
- **hub-bridge system prompt is file-loaded, not hardcoded** (verified 2026-03-04): `KARMA_IDENTITY_PROMPT`
  is loaded from `Memory/00-karma-system-prompt-live.md` at startup via `fs.readFileSync`. Volume-mounted
  read-only at `/karma/repo`. To update Karma's persona: edit the file â†’ git commit â†’ git push â†’
  `ssh vault-neo 'cd /home/neo/karma-sade && git pull'` â†’ `docker restart anr-hub-bridge`. NO rebuild needed.
  If the file is missing at startup, hub-bridge logs a WARN and runs with empty identity block (still operational).
- **anr-vault-search is FAISS, not ChromaDB** (confirmed 2026-03-04): container runs custom `search_service.py`
  using FAISS + OpenAI `text-embedding-3-small`. Endpoint: `POST localhost:8081/v1/search`
  body: `{"query": "...", "limit": 5}`. Auto-reindexes on ledger FileSystemWatcher + every 5 min.
  Do NOT try to call ChromaDB-style API endpoints (`/api/v1/collections`) â€” they don't exist here.
- **hooks.py ALLOWED_TOOLS whitelist gates all tool calls** (discovered Session 66): `karma-core/hooks.py`
  has an `ALLOWED_TOOLS` set. Any tool name NOT in this set is rejected with `{"ok":false,"error":"Unknown tool: X"}` BEFORE reaching `execute_tool_action()`. When adding new tools to TOOL_DEFINITIONS in server.js, you MUST also add them to `ALLOWED_TOOLS` in hooks.py + rebuild karma-server.
- **TOOL_NAME_MAP must be empty dict (identity passthrough)** (fixed Session 66): Pre-existing bug had
  `{ "read_file": "file_read", "write_file": "file_write", ... }` â€” wrong names (karma-server checks for
  `read_file`, not `file_read`). Correct pattern: `const TOOL_NAME_MAP = {};` which falls through to
  `|| toolName` in the mapping code. Any non-empty mapping with name aliases = likely broken.
- **callGPTWithTools parameter order differs from callLLMWithTools** (Session 66): `callLLMWithTools(model, messages, maxTokens)` but `callGPTWithTools(messages, maxTokens, model)`. Line 868 fix: `return callGPTWithTools(messages, maxTokens, model)` â€” note the different order.
- **docker restart does NOT re-read hub.env** (Session 66): `docker restart anr-hub-bridge` reuses the existing container's environment. To pick up new env_file entries (like GLM_RPM_LIMIT), must run `docker compose -f compose.hub.yml up -d` to recreate the container.
- **Gitignore patterns can be silently malformed** (Session 66): `.env.secrets` was added to .gitignore via a non-ASCII editor that inserted spaced chars (`. e n v . s e c r e t s`). Git couldn't match it â€” file with live K2_PASSWORD stayed untracked with no warning. ALWAYS verify after adding a sensitive file: `git check-ignore -v <filename>`. Exit code 1 = pattern not matching. Fix: `printf '\n.pattern\n' >> .gitignore`.

- **vault-api type enum is closed — no custom types** (Session 68): `vaultPost()` with `type:"dpo-pair"` returns 422 silently (fire-and-forget swallows it). Vault only accepts `["fact","preference","project","artifact","log","contact"]`. For custom categories, use `type:"log"` with `tags:["custom-tag"]`. ALWAYS add `if (result.status >= 300) throw new Error(...)` after every `vaultPost()` call.
- **buildVaultRecord() is required for all vault writes** (Session 68): Raw objects passed to `vaultPost()` fail schema validation. Always use `buildVaultRecord({type, content, tags, source, confidence})`. This exists in server.js — never call `vaultPost()` with a bare object.
- **hub-bridge lib/ files belong in build context PARENT, not app/** (Session 68): Build context is `/opt/seed-vault/memory_v1/hub_bridge/` (parent). `COPY lib/ ./lib/` in Dockerfile is relative to this parent. New files must be at `/opt/.../hub_bridge/lib/` — NOT under `app/lib/`. Syncing only to `app/lib/` causes "Cannot find module" at container startup.
- **Subagent SSH sessions can write tracked files on vault-neo** (Session 68): Subagents may write to `/home/neo/karma-sade/MEMORY.md`, making `git pull` abort. Fix: `git checkout -- MEMORY.md && git pull`. Prevention: never give subagents SSH commands touching tracked files on vault-neo.
- **compose.hub.yml lives in build context, not git repo root** (Session 69): File is at `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml`. Build/deploy: `cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml ...`. Running from `/home/neo/karma-sade` fails silently — file not found there.
- **TOOL_DEFINITIONS stale tools cause confabulation** (Session 69): `read_file`, `write_file`, `edit_file`, `bash` were in TOOL_DEFINITIONS with no handler — proxied to karma-server which rejects them. Karma hallucinated having bash/file capabilities. Removed Session 69. Active tools: `graph_query`, `get_vault_file`, `write_memory`, `fetch_url`, `get_library_docs`.
- **Sync ALL changed hub-bridge files to build context, not just server.js** (Session 72): Build context is `/opt/seed-vault/memory_v1/hub_bridge/`. Only server.js gets sync attention — lib/ and app/public/ files are silently missed. Before every --no-cache rebuild: `git diff --name-only HEAD~1 | grep hub-bridge` then cp EVERY changed file to build context. Stale `unified.html` or `lib/*.js` causes wrong behavior with no build error. Decision #27.
- **RELATES_TO edges permanently frozen — use MENTIONS co-occurrence** (Session 72): 1,423 RELATES_TO edges were created by Graphiti dedup mode (disabled Session 59). --skip-dedup creates only MENTIONS edges. query_relevant_relationships() must use MENTIONS co-occurrence cross-join, not RELATES_TO. Using RELATES_TO returns Chrome-extension-era data only. Decision #22.
- **MEMORY.md never reached Karma before Session 72** (architectural gap fixed): buildSystemText() had no MEMORY.md parameter for the entire system's history. Fixed with _memoryMdCache (tail 3000 chars, 5min refresh). Any future buildSystemText() changes must preserve the memoryMd 5th param.
- **hub-bridge lib/*.js were not in git until Session 75** (Session 75 fix): feedback.js, routing.js, pricing.js, library_docs.js existed only in `/opt/seed-vault/memory_v1/hub_bridge/lib/` on vault-neo — not in git repo. Committed to `hub-bridge/lib/` in commit 34b7326. Sync pattern after any lib change: `cp hub-bridge/lib/*.js /opt/seed-vault/memory_v1/hub_bridge/lib/` on vault-neo before rebuild.
- **routing.js has a startup allow-list that prevents unknown models** (Session 75): `ALLOWED_DEFAULT_MODELS` and `ALLOWED_DEEP_MODELS` gate MODEL_DEFAULT and MODEL_DEEP at startup. If hub.env uses a model not in the list, server throws and refuses to start. Always update routing.js allow-list before changing hub.env model config.
- **Primary model is now claude-haiku-4-5-20251001 (default) + claude-sonnet-4-6 (deep)** (Session 81, Decision #32): MODEL_DEFAULT=claude-haiku-4-5-20251001 (fast/cheap), MODEL_DEEP=claude-sonnet-4-6 (peer-quality). Both require entries in routing.js ALLOWED_DEFAULT_MODELS/ALLOWED_DEEP_MODELS or container refuses to start. Monthly cap: $60.
- **Backend-only verification ≠ green** (Session 75 lesson): Declaring Karma "working" based only on curl /v1/chat returning a response is insufficient. Must verify from browser (hub.arknexus.net) to confirm model shown in sidebar, response quality, and UI elements (thumbs) function correctly. Playwright MCP and Claude-in-Chrome MCP are available for this.
- **cp -r does NOT overwrite existing files in dest/** (Session 81, Decision #29): `cp -r source/ dest/` silently skips files already present in dest/. Always use explicit per-file copies: `cp /path/source/file /path/dest/file`. The #1 cause of stale build context deploys (Session 80 upload fix was committed but never reached build context for this reason).
- **X-Aria-Delegated header blocks ALL Aria memory writes** (Session 81, Decision #30): `aria_local_call` must ONLY send `X-Aria-Service-Key`. Adding `X-Aria-Delegated: karma` triggers delegated_read_only policy — observations stay at 0 silently, no error returned. Service key alone is correct auth.
- **Aria → vault-neo sync requires explicit /v1/ambient POST** (Session 81): Aria's `/api/memory/backfill` only syncs within Aria's local SQLite. It does NOT reach vault-neo. After each `aria_local_call`, hub-bridge must POST observation to `/v1/ambient` explicitly. `session_id` must be threaded from client (unified.html conversationId) → server.js → aria_local_call body for coherent Aria memory accumulation.
- **Reverse tunnel user MUST be `karma` not `neo`** (Session 84d): vault-neo:2223 → K2:22 tunnel works but K2 has no `neo` account. Always use `ssh -p 2223 -l karma localhost` or `karma@localhost`. Default user inference gives `Permission denied`. This applies to any code SSHing through the tunnel.
- **shell_run routes through aria /api/exec, NOT SSH from hub-bridge** (Session 84d, Decision #34): hub-bridge Docker container has no SSH client or private key. shell_run POSTs to `K2:7890/api/exec` with `X-Aria-Service-Key`. No Docker rebuild needed. Do not attempt to add SSH to the hub-bridge container.
- **aria.service requires `Environment=HOME=/home/karma` in drop-in** (Session 84d): Without this, systemd runs aria without HOME set, Python can't find user site-packages at `/home/karma/.local/lib/python3.12/site-packages/` → flask import fails at startup. Drop-in: `/etc/systemd/system/aria.service.d/10-aria-env.conf`. If K2 WSL is reset, re-add this drop-in.
