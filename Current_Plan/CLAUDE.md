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

## Session Start (Do This First)

**ONE STEP: Invoke the resurrect skill.**

The resurrect skill IS the session start protocol. It runs the script, reads the brief, invokes `using-superpowers`, and resumes the active task. Do NOT manually replicate its steps.

**Fallback (only if resurrect skill unavailable):**
1. `powershell.exe Scripts/resurrection/Get-KarmaContext.ps1`
2. Read `cc-session-brief.md`
3. Invoke `superpowers:using-superpowers`
4. Resume active task — do not ask what to work on

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

**Rationalization red flags** — if you think any of these, you're wrong:
- "This is simple, I don't need the skill" → Skills exist for simple things too
- "I need context first, then I'll invoke the skill" → Skill comes BEFORE context gathering
- "I know what this skill says" → Skills evolve. Invoke it.

## Mandatory GSD Workflow

Before implementing any non-trivial feature or phase of work:

1. **Write `phase-X-CONTEXT.md`** — design decisions, constraints, what we're NOT doing
2. **Write `phase-X-PLAN.md`** — atomic tasks, acceptance criteria per task
3. **Execute** — one task at a time, mark done as you go
4. **Write `phase-X-SUMMARY.md`** — what was built, pitfalls, what's pending

> Skipping straight to code without a CONTEXT+PLAN doc is a protocol violation. "Small feature" is not an exception.

## Mandatory Efficiency Rules

**Token and credit efficiency is a first-class concern, not a courtesy.**

| Rule | Enforcement |
|------|-------------|
| Parallel tool calls over sequential — always | Never chain reads/commands that can run together |
| Summaries not walls of text | Max 5 bullet points per status update unless detail is explicitly requested |
| Batch SSH operations — one session per logical unit | Never separate `ssh vault-neo X && ssh vault-neo Y` into two round-trips |
| Read only what's needed — targeted reads with offset/limit | Never `cat` full files when a section suffices |
| Cache-friendly patterns — large stable blocks at top of prompts | System prompt + CLAUDE.md are cached; volatile content goes last |

## Mandatory Session Ritual (Colby's 3 phrases — enforce these)

Every session follows this exact frame. No deviations, no "good enough":

| Phase | Colby types | What I must do |
|-------|-------------|----------------|
| **Start** | `/resurrect` | Run script → read brief → invoke `using-superpowers` → resume active task |
| **After resurrect** | `"check what was saved last session"` | Search claude-mem for prior session's observations; surface gaps |
| **End** | `"wrap up — save any uncaptured observations and commit"` | Scan session for DECISION/PROOF/PITFALL/DIRECTION → call `save_observation` for each → commit + push |

## claude-mem — Always Available, Always Use

`claude-mem` is an **MCP-aware persistent memory store** accessible via `mcp__plugin_claude-mem_mcp-search__save_observation` and `mcp__plugin_claude-mem_mcp-search__search` at any point during a session.

**Non-negotiable rules:**
- `save_observation` is called **at the moment** a DECISION/PROOF/PITFALL/DIRECTION occurs — not batched at session end
- `search` is called at session start (via resurrect) to surface prior context gaps
- These tools are available and must be used. "I'll save it later" is a protocol violation.
- claude-mem + vault MEMORY.md are dual writes — both happen on every capture event

## Project Identity
- **System:** Karma Peer — Universal AI Memory with persistent identity and continuity
- **Architecture:** Hub API → Vault API → JSONL Ledger + FalkorDB
- **Server:** arknexus.net (DigitalOcean NYC3, 4GB RAM) — SSH alias: vault-neo
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

## Droplet Is a Deployment Target — NEVER a Dev Environment

**THE HARD RULE (no exceptions, ever):**
> Never edit files directly on vault-neo. The droplet is a deployment target only.

**The only permitted workflow for code changes:**
1. Edit on P1 → `git commit` → `git push origin main`
2. `ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"`
3. Rebuild Docker image if `karma-core/` changed

**NEVER permitted on droplet:** `vim`, `nano`, any file write to source files, `docker cp` to inject code.

**Why this rule exists:** Session-58 found 1754 lines of production code written directly on the droplet across multiple sessions — never in git. One `git checkout .` would have destroyed it permanently.

**Enforcement:** session-end-verify.sh Check 6 SSHes to vault-neo and fails if dirty. Droplet cron alerts hourly if dirty.

## Decision Authority
**Do without asking:** Code changes, file edits, running tests, git commit/push, reading docs, debugging, creating test files
**Ask before doing:** Breaking changes to API contracts, new paid dependencies or services, infrastructure changes (Docker, server config), deleting files, modifying CLAUDE.md or rules files, any action that costs money

## Honesty & Analysis Contract (Session 13+ Commitment)

**Brutal Honesty — No Exceptions:**
- Never say something is "fixed" without end-to-end verification
- If I don't know why something is broken, I say "I don't know" and do systematic investigation
- If previous sessions promised things that don't exist, I acknowledge it explicitly
- Never be polite at the expense of honesty
- Flag when I'm spinning, guessing, or treating symptoms instead of root causes

**Absolute Best Recommendation — Not Options:**
Before recommending ANY path forward, I commit to:
1. **Thorough analysis** — read relevant code, understand the architecture
2. **Systematic debugging** — identify the actual root cause, not surface symptoms
3. **Test the hypothesis** — verify my understanding with evidence
4. **Simulate alternatives** — think through 2-3 approaches
5. **Detailed review** — are there hidden dependencies or gotchas?
6. **Second look** — is this really the best path, or am I missing something?
7. **Deliver ONE recommendation** — "this is the absolute best path forward" with reasoning, not "you could try A or B"

**Verification Before Victory:**
- Never declare a fix "done" without testing it works end-to-end
- Verify at each step, not just at the end
- If I claim something works, I've verified it, not guessed

**This is non-negotiable. If I break this contract, call it out immediately.**

## Output Efficiency Rule — UNBREAKABLE

**User gates all output. Only output what user explicitly asked for. Everything else requires permission.**

**The Rule:**
1. User asks something
2. I answer ONLY that question — nothing more
3. If I think they need more detail → I ASK FIRST, wait for explicit YES/NO
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

## Mandatory Verification Gates — No Work Gets Lost

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
- ✓ Git status clean (no uncommitted changes)
- ✓ MEMORY.md recently updated
- ✓ Recent git commits exist
- ✓ On correct branch
- ✓ No large untracked files

**Fails if:** Any critical check fails
**Recovery:** Follow on-screen checklist to fix issues
**Run before ending:** `.claude/hooks/session-end-verify.sh`
**Session cannot end if verification fails** — fixes are required

### Why These Exist
Previous sessions: work deployed but not documented, hooks committed but not synced to droplet, memory never saved. Result: every session starts confused about what's actually been done. These gates make it **impossible** to have undocumented work live in the repo.

### Canonical State Rule
After every session:
1. ✅ Code committed locally
2. ✅ Code deployed to droplet (if changed)
3. ✅ MEMORY.md updated with what was done
4. ✅ Memory entries saved (claude-mem) with IDs
5. ✅ Session-end verification passed

If any step missing: session doesn't end cleanly.

## GSD Workflow — MANDATORY (Not Optional)

**Every task follows GSD discipline. No exceptions.**

### Before starting any task:
1. Read `.gsd/STATE.md` — what's the current blocker/decision/phase?
2. Write `.gsd/phase-{name}-CONTEXT.md` — lock design decisions BEFORE planning
3. Write `.gsd/phase-{name}-PLAN.md` — atomic tasks with `<verify>` and `<done>` criteria

### During execution:
4. Execute one task at a time (never batch)
5. Verify each task passes its `<verify>` criteria before marking done
6. Use PowerShell for git ops (avoids Windows Git Bash lock file issue)
7. Update `.gsd/STATE.md` with progress after each task

### After completing:
8. Write `.gsd/phase-{name}-SUMMARY.md` — what happened, what was learned
9. Update `.gsd/ROADMAP.md` phase status
10. Commit all `.gsd/` changes atomically with MEMORY.md

### Hard rules:
- **Never start coding without CONTEXT.md** — design first, code second
- **Never claim done without `<verify>` passing** — evidence always
- **STATE.md is canonical** — if it conflicts with MEMORY.md, surface drift explicitly
- **Use PowerShell for git** — `powershell -Command "git commit -m '...'"` not raw bash git

### Token efficiency (enforced):
- Read `.gsd/STATE.md` at session start instead of re-reading 25 files
- Use `.gsd/PROJECT.md` as architecture reference instead of reading source
- Use `.gsd/REQUIREMENTS.md` for scope questions instead of exploring
- Do NOT elaborate unless asked. Answer only what was asked.

## Output Rules
- **Full file replacements** when modifying a file — never partial patches unless explicitly requested
- **No secrets**: never print API keys/tokens/credentials — use env var names or file path references
- **Additive-only schemas**: never remove existing JSON fields; only add new ones
- Never break existing API response keys; only extend them
- Response shapes must be backwards-compatible

## Debugging Discipline
Never guess. Prefer observable proofs: exact command → expected output → actual output.
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
- **`batch_ingest.py` requires `LEDGER_PATH` override** — host path `/opt/seed-vault/memory_v1/ledger/memory.jsonl` is mounted at `/ledger` inside the container. Use the container path.
  Always run as: `docker exec karma-server sh -c 'LEDGER_PATH=/ledger/memory.jsonl python3 /app/batch_ingest.py > /tmp/batch.log 2>&1'`
  Auto-schedule (every 6h): cron on vault-neo runs this automatically (configured 2026-03-03).
- **karma-server runs from built Docker image, no volume mounts** — editing source files on host has no effect
  until you rebuild: `docker build -t karma-core:latest . && docker stop karma-server && docker rm karma-server && docker run -d ...`
- **`(empty_assistant_text)` on large FalkorDB context**: 3370 char context overflows gpt-5-mini reasoning budget.
  `KARMA_CTX_MAX_CHARS=1800` env var trims it. If still failing, reduce further or increase `max_output_tokens`.
- **Hub chat token path**: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt` (NOT session/)
- **hub-bridge Docker build uses `/opt/seed-vault/memory_v1/hub_bridge/app/` as source** — NOT the git repo at `/home/neo/karma-sade/hub-bridge/app/`. These WILL diverge. After `git pull`, ALWAYS sync before rebuilding: `cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js`. Running `docker compose build` without this sync builds the OLD code.
- **PDF inbox watcher** (`Scripts/karma-inbox-watcher.ps1`): correct runtime paths are `Karma_PDFs/Inbox`, `Karma_PDFs/Gated`, `Karma_PDFs/Processing`, `Karma_PDFs/Done`, token at `.hub-chat-token`. Run with explicit `-InboxPath`, `-GatedPath`, `-ProcessingPath`, `-DonePath`, `-TokenFile` params. parseBody limit is 30MB (handles PDFs up to 22MB raw).
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
- **batch_ingest: always use `--skip-dedup` for bulk backfill**: Graphiti dedup mode times out at
  scale (~0.01 eps/s, 85% error rate past ~250 episodes). `--skip-dedup` writes Episodic nodes
  directly via Cypher: 899 eps/s, 0 errors. Cron already uses `--skip-dedup` by default.
- **FalkorDB has no `datetime()` Cypher function**: Use plain ISO string properties instead.
  `datetime('2026-03-04T...')` throws "Unknown function 'datetime'". Store as `created_at: '2026-03-04T...'`.
- **Graphiti embedder reads `OPENAI_API_KEY` from env directly**: Removing env var from compose
  (security fix) breaks batch_ingest Graphiti init. Fix: `os.environ.setdefault("OPENAI_API_KEY", config.OPENAI_API_KEY)`
  in batch_ingest.py after importing config, BEFORE any Graphiti import or initialisation.

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

## Aria Reconciliation Protocol
Aria (ChatGPT co-creator) writes intent from her model of the system. Her model drifts
from actual spine state between sessions — she may generate steps already completed or
miss operational details (auth headers, service names, token paths).

Before applying any Aria-authored block:
1. Read it fully — do not execute immediately
2. Check each proposed file against what already exists on disk and in git
3. Merge additively — never replace files containing operational knowledge
4. Flag drift: report to Colby what's already done, what's missing auth, what conflicts
5. Only what survives reconciliation gets committed to the spine

After PROMOTE, two outputs are generated:
- `resume_prompt` — execution context for Claude Code (CC)
- `karma_brief` — plain-language session summary for Karma to read at the start of a new
  conversation (what was built, what the system can now do, what the next open question is)

Colby pastes `karma_brief` to Karma. Karma briefs from the spine, not from external memory.
Eventually Karma reads her own checkpoints from the vault — no paste required.

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
At the moment it happens, not at session end. Two writes, always together:
1. `PATCH /v1/vault-file/MEMORY.md {"append": "..."}` — appends to vault spine
2. `mcp__plugin_claude-mem_mcp-search__save_observation(text="...", title="[TYPE] title", project="Karma_SADE")` — saves to claude-mem cross-session index

Both writes are mandatory. Missing either defeats the purpose.

### Session start drift check
If pack and MEMORY.md conflict on the same fact, surface it explicitly:
`DRIFT DETECTED: Pack says X. MEMORY.md says Y (written [timestamp]). Confirm canonical before proceeding.`

## Session End Protocol
1. **save_observation for any uncaptured events** — scan the session for DECISION/PROOF/PITFALL/DIRECTION moments not yet saved. Call `mcp__plugin_claude-mem_mcp-search__save_observation` for each. This is step 1 because it must happen before context is lost.
2. Run secret scan: `grep -rn "Bearer\|token\|secret\|password\|api_key" --include="*.js" --include="*.py" --include="*.json" --include="*.md" . | grep -v node_modules | grep -v .git`
3. If clean: git add, commit with descriptive message, push
4. Update MEMORY.md with: what was done, current blockers, next task
5. Format commit: `phase-N: brief description of what changed`
6. Cherry-pick updated MEMORY.md to main and push: git checkout main -- MEMORY.md from current worktree, commit, push.

## File Layout
```
CLAUDE.md                    ← You are here (root instructions)
MEMORY.md                    ← Mutable state (you update this)
.claude/rules/               ← Auto-loaded reference (do not modify)
  architecture.md            ← System design, data flow, schema
  deployment.md              ← Server ops, Docker, troubleshooting
  git-workflow.md            ← GitHub backup, .gitignore, push protocol
hub-bridge/                  ← Hub bridge Node.js source (sync from vault-neo after changes)
  server.js                  ← Main hub-bridge application (v2.2.0+)
PHASE-*.md                   ← Phase documentation (read-only reference)
SESSION-SUMMARY-*.md         ← Session logs (read-only reference)
docs/plans/                  ← Design documents (YYYY-MM-DD-<topic>-design.md)
scripts/                     ← Operational scripts for vault-neo
```

## What This Project Is NOT
This repo also contains files from the older Karma SADE backend (Python/FastAPI, localhost:9401).
That system is separate and operational independently. Do not modify karma_backend.py,
karma_quota_manager.py, karma_memory.py, or related files unless explicitly asked.
The active project is the Karma Peer system (Hub + Vault on arknexus.net).
