# Karma SADE — Session Handoff

**Date**: 2026-02-12
**Session**: Warp (Oz) — crash recovery + resilience implementation
**GitHub**: https://github.com/Karma8534/Karma-SADE (private)

---

## System Architecture

```
PAYBACK (Windows 11, Intel Core Ultra 9, 63GB RAM, RTX 4070 8GB)
├── Open WebUI ─── C:\openwebui\venv\Scripts\open-webui.exe serve
│   ├── Port 8080
│   ├── DB: C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db
│   ├── Model: karma-sade-architect (base_model_id: gpt-4o)
│   └── Connections (in config table):
│       ├── Groq: gsk_... → https://api.groq.com/openai/v1
│       └── OpenAI: sk-svcacct-... → https://api.openai.com/v1
│
├── Cockpit ─── C:\Users\raest\Documents\Karma_SADE\Scripts\karma_cockpit_service.py
│   ├── Port 9400, v2.0.0 (2,313 lines, 90,480 bytes)
│   ├── 34 routes / 28 tool functions
│   ├── Playwright headful browser, profile at ~/karma/browser-profile
│   ├── API token at ~/karma/cockpit-token.txt
│   └── Gemini CLI: v0.28.2, GEMINI_API_KEY in user env
│
├── Ollama ─── 6 models
│   ├── llama3-groq-tool-use:8b, llama3.1:8b, gemma3:4b
│   ├── qwen2.5-coder:3b (memory extraction), deepseek-coder:6.7b
│   └── nomic-embed-text (embeddings)
│
├── Memory Sync ─── KarmaSADE-MemorySync scheduled task (every 30 min)
│   ├── Step 1: karma_chat_extractor.py (extract from chats via qwen2.5-coder:3b)
│   ├── Step 2: generate_karma_prompt.py (rebuild system prompt → DB)
│   ├── Step 3: karma_vault_sync.py (bidirectional API sync with Vault)
│   └── Step 4: git_sync.py (commit + push to GitHub)
│
├── Vault (remote) ─── vault-neo / 64.225.13.144 (DigitalOcean NYC3)
│   ├── 4 Docker containers: vault API, hub-bridge, db, nginx
│   ├── Git clone at ~/karma-sade/ (pulls from GitHub via cron */30)
│   ├── Deploy key: ~/.ssh/karma_deploy_key (read-only)
│   └── Pull script: ~/karma-sade-pull.sh
│
├── Monitoring ─── KarmaSADE-Sentinel scheduled task (every 15 min)
│   └── C:\Users\raest\Documents\Karma_SADE\Scripts\sentinel.ps1 (v1.1.0; includes Cockpit HTTP health)
│
├── Watchdog ─── KarmaSADE-Watchdog scheduled task (every 5 min)
│   └── C:\Users\raest\Documents\Karma_SADE\Scripts\karma_watchdog.ps1
│
├── DB Backup ─── KarmaSADE-BackupDB scheduled task (daily 3:00 AM)
│   └── C:\Users\raest\Documents\Karma_SADE\Scripts\karma_backup_webui.ps1
│
├── Secrets (DPAPI) ─── local encrypted store
│   ├── Tool: C:\Users\raest\Documents\Karma_SADE\Scripts\karma_secrets.ps1
│   └── Store: %USERPROFILE%\karma\secrets.json (gitignored)
│
└── Startup (Windows login)
    └── karma_startup.vbs → karma_startup.ps1 (ordered orchestrator; health-gated)
        Path: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\karma_startup.vbs
```

---

## What Was Done This Session (2026-02-12)

### 1. Crash Recovery
- Open WebUI was down (runs from venv, NOT Docker)
- Restarted Open WebUI, cockpit, memory sync
- Unstuck KarmaSADE-MemorySync scheduled task

### 2. Fixed Karma 404 "Model Not Found"
- Root cause: config table in webui.db had empty OpenAI key slot
- Fixed: wrote both API keys + base URLs to config.openai in DB
- Fixed: aligned meta.base_model_id and meta.params.model from stale llama3.1:8b → gpt-4o
- Verified both Groq and OpenAI keys work end-to-end

### 3. Version String
- Updated cockpit /health from 1.0.0 → 2.0.0

### 4. GitHub Repo (Resilience Gap #1)
- Installed gh CLI, authenticated as Karma8534
- Created private repo: Karma8534/Karma-SADE
- .gitignore: excludes __pycache__, Logs/, screenshots, _test_* scripts
- Initial commit: 94 files, 11,531 lines

### 5. GitHub ↔ Vault Integration
- Created git_sync.py (step 4 of memory pipeline)
- Generated ED25519 deploy key on vault-neo
- Added as read-only deploy key to GitHub repo
- Cloned repo on droplet, cron pulls every 30 min
- Deprecated sync_docs_to_droplet.py (SCP replaced by git)
- End-to-end tested: local → GitHub → droplet ✓

### 6. Resilience Gaps #2–#5 Implemented (code)
- Added: startup orchestrator: `Scripts/karma_startup.ps1` + `Scripts/karma_startup.vbs`
- Added: watchdog auto-restart: `Scripts/karma_watchdog.ps1`
- Added: Open WebUI DB backups: `Scripts/karma_backup_webui.ps1`
- Added: DPAPI secrets manager: `Scripts/karma_secrets.ps1`
- Added: deployment helper (WhatIf-capable): `Scripts/deploy_resilience.ps1`
- Updated: `Scripts/sentinel.ps1` → v1.1.0 (adds Cockpit HTTP health; overall status driven by HTTP + disk)
- Updated: `.gitignore` to ignore `secrets.json` and `.vault_token`

### 7. Cockpit Token + Test Harness Fixes
- Cockpit requires `Authorization: Bearer <token>` for all routes except `/health`.
- Updated helper/test scripts to automatically read the token from: `~\karma\cockpit-token.txt`
  - `Scripts/exec_js.py`, `Scripts/send_msg.py`, `Scripts/send_msg_debug.py`
  - `Scripts/test_cockpit.py`, `Scripts/test_cockpit_agentic.py`
  - `_test_*` scripts
- Tests:
  - `test_cockpit.py`: 60/60 passing
  - `test_cockpit_agentic.py`: passes with skips when Open WebUI tool-call UI/side-effects are not reliably detectable

### 8. Resilience Deployed on PAYBACK (system changes)
Startup folder
- Removed old launchers:
  - `start_openwebui.vbs`
  - `start_cockpit.vbs`
- Installed unified launcher:
  - `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\karma_startup.vbs`

Scheduled tasks
- `KarmaSADE-Watchdog` (every 5 min)
  - Note: Creating it with "highest privileges" failed (Access denied), so it was created without `/rl highest`.
- `KarmaSADE-BackupDB` (daily 03:00)
- Backup ran once successfully; logs at: `C:\Users\raest\Documents\Karma_SADE\Logs\karma-backup.log`
  - Note: `sqlite3` CLI not found in PATH, so backup fell back to file copy (still usable, but less ideal during concurrent writes).
- Watchdog ran once; logs at: `C:\Users\raest\Documents\Karma_SADE\Logs\karma-watchdog.log`

Sentinel scheduled task fix
- `KarmaSADE-Sentinel` was failing when run under Windows PowerShell (`powershell.exe`).
- Updated task to run under PowerShell 7 (`pwsh.exe`) and verified it now exits 0 and logs Cockpit status to `sentinel-runtime.log`.

---

## Resilience Plan Status

1. Git version control — DONE (GitHub repo + auto-push every 30 min)
2. Startup ordering — DONE (karma_startup.vbs → karma_startup.ps1 orchestrator)
3. Auto-restart on failure — DONE (KarmaSADE-Watchdog scheduled task)
4. API keys encrypted-at-rest option — DONE (karma_secrets.ps1 DPAPI store; startup scripts no longer need plaintext keys)
5. webui.db backup — DONE (KarmaSADE-BackupDB scheduled task)

---

## Key File Locations

- `Scripts/karma_cockpit_service.py` — Cockpit service v2.0.0
- `Scripts/karma_memory_sync.py` — 4-step sync orchestrator
- `Scripts/git_sync.py` — Step 4: git commit + push
- `Scripts/karma_vault_sync.py` — Bidirectional Vault API sync
- `Scripts/generate_karma_prompt.py` — Builds system prompt from facts
- `Scripts/karma_chat_extractor.py` — Extracts facts from chats
- `Memory/05-user-facts.json` — Source of truth for all facts
- `Memory/00-karma-system-prompt-live.md` — Current generated system prompt

Startup folder: `C:\Users\raest\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\`
- Installed launcher: `karma_startup.vbs`

Scheduled tasks:
- Watchdog: `KarmaSADE-Watchdog` (every 5 min)
- Backup: `KarmaSADE-BackupDB` (daily 03:00)
- Sentinel: `KarmaSADE-Sentinel` (every 15 min; runs `pwsh.exe`)

Logs:
- Watchdog log: `C:\Users\raest\Documents\Karma_SADE\Logs\karma-watchdog.log`
- Backup log: `C:\Users\raest\Documents\Karma_SADE\Logs\karma-backup.log`
- Sentinel log: `C:\Users\raest\Documents\Karma_SADE\Logs\sentinel-runtime.log`

Open WebUI DB: `C:\openwebui\venv\Lib\site-packages\open_webui\data\webui.db`

---

## How to Start a New Session

Paste this into the new conversation:

> Read the session handoff at `C:\Users\raest\Documents\Karma_SADE\Memory\08-session-handoff.md`.
> This is the Karma SADE system — memory-first, vault-centric, multi-agent AI.
> GitHub: https://github.com/Karma8534/Karma-SADE (private, user Karma8534).
> Verify all services are healthy before proceeding.

### Health Check Commands
```
curl http://127.0.0.1:8080          # Open WebUI (expect 200)
curl http://127.0.0.1:9400/health   # Cockpit (expect karma_ready: true, version: 2.0.0)
ollama list                          # 6 models
ssh vault-neo "git -C ~/karma-sade log --oneline -1"  # Latest commit on droplet
```

---

## User Profile

- **Name**: Neo
- **Skill level**: Self-described novice with computers
- **Preferences**: Step-by-step, one action at a time, deep-dive with rationale but concise
- **Safety**: No destructive changes without explicit approval
- **Favorite color**: Purple
- **Machine**: PAYBACK
