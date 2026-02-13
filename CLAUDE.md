# Universal AI Memory System — Claude Code Instructions

## Session Start (Do This First)
1. Read MEMORY.md for current phase status and active task
2. Run: `ssh vault-neo "systemctl status seed-vault && wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"`
3. Check git log --oneline -5 for recent changes
4. Resume the active task listed in MEMORY.md — do not ask what to work on

## Project Identity
- **System:** Universal AI Memory — cross-platform conversation capture and recall
- **Architecture:** Chrome Extension → Hub API → Vault API → JSONL Ledger
- **Server:** arknexus.net (DigitalOcean NYC3, 4GB RAM) — SSH alias: vault-neo
- **Repo:** https://github.com/Karma8534/Karma-SADE.git
- **Branch:** claude/elegant-solomon

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
PHASE-*.md                   ← Phase documentation (read-only reference)
SESSION-SUMMARY-*.md         ← Session logs (read-only reference)
chrome-extension/            ← Extension source code
```

## What This Project Is NOT
This repo also contains files from the older Karma SADE backend (Python/FastAPI, localhost:9401).
That system is separate and operational independently. Do not modify karma_backend.py,
karma_quota_manager.py, karma_memory.py, or related files unless explicitly asked.
The active project is the Universal AI Memory system (Chrome extension + Vault on arknexus.net).
