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
1. Run `Scripts/resurrection/Get-KarmaContext.ps1` then read `karma-context.md` for Karma's live graph context
2. Read `MEMORY.md` (`C:\Users\raest\Documents\Karma_SADE\MEMORY.md`) for current phase status and active task
3. Run: `ssh vault-neo "systemctl status seed-vault && wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"`
4. Check git log --oneline -5 for recent changes
5. Resume the active task listed in MEMORY.md — do not ask what to work on

## Project Identity
- **System:** Karma Peer — Universal AI Memory with persistent identity and continuity
- **Architecture:** Chrome Extension → Hub API → Vault API → JSONL Ledger + FalkorDB
- **Server:** arknexus.net (DigitalOcean NYC3, 4GB RAM) — SSH alias: vault-neo
- **Repo:** https://github.com/Karma8534/Karma-SADE.git
- **Branch:** main (working branch; claude/elegant-solomon is legacy)

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

## Output Rules
- **Full file replacements** when modifying a file — never partial patches unless explicitly requested
- **No secrets**: never print API keys/tokens/credentials — use env var names or file path references
- **Additive-only schemas**: never remove existing JSON fields; only add new ones
- Never break existing API response keys; only extend them
- Response shapes must be backwards-compatible

## Debugging Discipline
Never guess. Prefer observable proofs: exact command → expected output → actual output.
When runtime behavior changes unexpectedly, collect evidence before proposing a fix.

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
