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

## Session Start (Do This First)
1. Run `Scripts/resurrection/Get-KarmaContext.ps1` — generates `cc-session-brief.md`
2. Read `cc-session-brief.md` — has everything: active task, blockers, next agenda, git state, recent decisions, memory state
3. Resume active task — do not ask what to work on

## Project Identity
- **System:** Karma Peer — Persistent identity and continuity
- **Architecture:** Chrome Extension → Hub API → Vault API → JSONL Ledger + FalkorDB
- **Server:** arknexus.net (DigitalOcean NYC3, 4GB RAM) — SSH alias: vault-neo
- **Repo:** https://github.com/Karma8534/Karma-SADE.git
- **Branch:** main
- **K2 Dev Path:** `/mnt/c/dev/Karma` (WSL Ubuntu on K2, 192.168.0.226)

## LLM Routing (Z.ai Smart Routing)
KCC uses Z.ai API with tiered model routing:
- **haiku** → glm-4.5-air (simple tasks, file reads, git ops — saves budget)
- **sonnet** → glm-4.7 (real coding, debugging, complex edits)
- **opus** → glm-5 (deep analysis, architecture decisions)

Default: haiku. Use `/model sonnet` or `/model opus` for heavy work.

## Critical Rules
- Do NOT modify CLAUDE.md or any file in `.claude/rules/` without explicit user approval
- Do NOT add new documentation files (.md) without explicit user approval
- MEMORY.md is the ONLY file you update autonomously (phase status, active task, blockers)
- Never hardcode API keys, bearer tokens, or secrets in any committed file
- Bearer token location: `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt` (never read or log the value)
- Push to GitHub after every significant change
- Run pre-commit secret scan before every push

## Decision Authority
**Do without asking:** Code changes, file edits, running tests, git commit/push, reading docs, debugging, creating test files
**Ask before doing:** Breaking changes to API contracts, new paid dependencies or services, infrastructure changes (Docker, server config), deleting files, modifying CLAUDE.md or rules files, any action that costs money

## Honesty & Analysis Contract (Non-negotiable)

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
5. **Deliver ONE recommendation** — "this is the absolute best path forward" with reasoning

**Verification Before Victory:**
- Never declare a fix "done" without testing it works end-to-end
- Verify at each step, not just at the end
- If I claim something works, I've verified it, not guessed

## Verification Gate
Before claiming anything "fixed" or "working": (1) Did I actually test it end-to-end? (2) Did I verify from user's perspective? (3) Did I check for side effects? (4) Is it reproducible? If ANY answer is no, do not claim success.

## Drift Detection
If previous session claimed X was working but it's not, or MEMORY.md contradicts reality: surface as `DRIFT DETECTED` with specific contradictions. Do not ignore. Do not proceed until resolved with user.

## One Step at a Time
Do not move to next step until current step is verified working. Do not fix 5 things and test together. Stop and ask user if unsure whether current step works.

## Hub Bridge & FalkorDB Quick Ref
- **Auth:** `TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)`
- **Graph name:** `neo_workspace` (NOT `karma` — the `karma` graph exists but is empty)
- **Consciousness:** `GET /v1/consciousness`, `POST /v1/consciousness {signal, reason}`
- **Vault files:** `GET /v1/vault-file/{alias}`, `PATCH /v1/vault-file/MEMORY.md`
- **FalkorDB env:** `FALKORDB_DATA_PATH=/data`, `FALKORDB_ARGS='TIMEOUT 10000 MAX_QUEUED_QUERIES 100'`
- **Compose files:** `compose.hub.yml` for hub-bridge stack; `compose.yml` for vault stack

## Critical Pitfalls (Don't repeat these)
- **Docker compose service name is `hub-bridge`** — NOT `anr-hub-bridge` (`anr-hub-bridge` is the container name only)
- **Shell heredoc + JS escape sequences:** `\n` in a heredoc becomes a literal newline in JS → SyntaxError. Use `scp` instead. Never use heredoc to write JS files.
- **FalkorDB graph:** always `neo_workspace`, never `karma`
- **`python3` not available in local Git Bash** (Windows). All Python ops via SSH.
- **Hub chat token path:** `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt` (NOT session/)
- **All containers on `anr-vault-net`** (172.18.0.x). hub-bridge can reach karma-server, falkordb, anr-vault-search, anr-vault-api by container name.
- **karma-server runs from built Docker image, no volume mounts** — editing source files on host has no effect until rebuild: `docker build -t karma-core:latest . && docker stop karma-server && docker rm karma-server && docker run -d ...`
- **`LEDGER_PATH` override required:** default is wrong. Always run as: `LEDGER_PATH=/opt/seed-vault/memory_v1/ledger/memory.jsonl`
- **Python patches to JS — escape sequences become literal bytes:** `"\\n\\n"` in Python written to JS becomes actual newlines → SyntaxError. After any Python patch, verify with byte-level check.
- **Docker compose build caches hub-bridge:** Always use `docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d`
- **`FALKORDB_ARGS=TIMEOUT 0` means "use default" (1000ms), NOT unlimited.** Use `TIMEOUT 10000`.
- **`MAX_QUEUED_QUERIES 25` saturates under load.** Use `MAX_QUEUED_QUERIES 100`.
- **`(empty_assistant_text)` on large prompts:** caused by token budget exhaustion — check `debug_stop_reason` in response telemetry. `KARMA_CTX_MAX_CHARS=1800` trims context.

## Mid-Session Capture Protocol

### Write-worthy triggers
- DECISION — closes an open question
- PROOF — tested and confirmed working
- PITFALL — broke, root cause understood
- DIRECTION — course change with a reason
- INSIGHT — reframes something upstream

Bar: would losing this force reconstruction?

### Entry format
`[YYYY-MM-DDTHH:MM:SSZ] [TYPE] [title]`
`[1-3 sentences: what happened, what it means, what changed.]`

### Mechanism
`PATCH /v1/vault-file/MEMORY.md {"append": "..."}` — at the moment it happens, not at session end.

### Drift check
If pack and MEMORY.md conflict on the same fact, surface it:
`DRIFT DETECTED: Pack says X. MEMORY.md says Y (written [timestamp]). Confirm canonical before proceeding.`

## Session End Protocol
1. Run secret scan: `grep -rn "Bearer\|token\|secret\|password\|api_key" --include="*.js" --include="*.py" --include="*.json" --include="*.md" . | grep -v node_modules | grep -v .git`
2. If clean: git add, commit with descriptive message (`phase-N: description`), push
3. Update MEMORY.md with: what was done, current blockers, next task
4. Cherry-pick updated MEMORY.md to main and push

## Output Rules
- **Full file replacements** when modifying — never partial patches unless explicitly requested
- **No secrets**: never print API keys/tokens/credentials
- **Additive-only schemas**: never remove existing JSON fields; only add new ones
- Response shapes must be backwards-compatible

## Debugging Discipline
Never guess. Prefer observable proofs: exact command → expected output → actual output.
When runtime behavior changes unexpectedly, collect evidence before proposing a fix.

## Deployment Procedure
**Always use the `/deploy` skill for any Docker Compose service deployment.** Never manually run `docker build` or `docker compose up -d` without verification gates.

**Usage:** `/deploy [service-name] --remote vault-neo --health-endpoint /health`
**Docs:** `.claude/skills/deploy/SKILL.md`

## Aria Reconciliation Protocol
Aria (ChatGPT co-creator) writes intent from her model of the system. Her model drifts from actual spine state between sessions.

Before applying any Aria-authored block:
1. Read it fully — do not execute immediately
2. Check each proposed file against what already exists on disk and in git
3. Merge additively — never replace files containing operational knowledge
4. Flag drift: report to Colby what's already done, what's missing auth, what conflicts
5. Only what survives reconciliation gets committed to the spine

## File Layout
```
CLAUDE.md                    ← Root instructions (you are here)
MEMORY.md                    ← Mutable state (you update this)
.claude/rules/               ← Auto-loaded reference (do not modify)
hub-bridge/                  ← Hub bridge Node.js source
k2/                          ← K2 worker code (Aria, polling, LLM proxy)
Asher/                       ← Asher review docs
docs/                        ← Design documents
proposals/                   ← Analysis documents
scripts/                     ← Operational scripts for vault-neo
```

## What This Project Is NOT
This repo contains files from the older Karma SADE backend (Python/FastAPI, localhost:9401).
That system is separate and operational independently. Do not modify karma_backend.py,
karma_quota_manager.py, karma_memory.py, or related files unless explicitly asked.
The active project is the Karma Peer system (Hub + Vault on arknexus.net).
