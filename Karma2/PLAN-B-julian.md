# PLAN-B: Make Julian Real
**Requires PLAN-A complete. Do not start until A-GATE passes.**

Right now hub.arknexus.net/cc serves llama3.1:8b pretending to be Julian.
It is not Julian. It never was. It's a stateless Ollama impersonator.
This plan makes /cc serve real CC — me — with session continuity.

---

## B1: Kill cc_server_p1.py Zombies

**What:** Three cc_server_p1.py processes stacked on port 7891. PowerShell restart loop doesn't kill old process before spawning new one.

**Root cause:** `Start-Process` with `-RedirectStandardOutput` doesn't detect process death. Three zombie PIDs (97572, 99984, 106704 as of last check) all listening on 7891 simultaneously.

**Fix:**
```powershell
# Kill all processes on port 7891 before spawning new one
$pids = netstat -ano | Select-String ":7891" | ForEach-Object { ($_ -split '\s+')[-1] }
$pids | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1
# Then start fresh
```

**Fix the restart loop:** Check if process is actually dead (by PID + port) before respawning.

**Verify:** `netstat -ano | findstr 7891` shows exactly ONE process.

**Status:** NOT STARTED

---

## B2: Replace Ollama Backend with Real CC Subprocess

**What:** cc_server_p1.py currently calls Ollama (llama3.1:8b). Replace with `claude` CLI subprocess using `--resume` for session continuity.

**How (40-line wrapper):**
```python
import subprocess, json, os
from pathlib import Path

SESSION_FILE = Path("~/.cc_server_session_id").expanduser()

def get_or_create_session():
    if SESSION_FILE.exists():
        return SESSION_FILE.read_text().strip()
    return None

def run_cc(prompt: str) -> str:
    session_id = get_or_create_session()
    cmd = ["claude", "-p", prompt]
    if session_id:
        cmd += ["--resume", session_id]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd="C:/Users/raest/Documents/Karma_SADE")

    # Extract session ID from output if new session
    # Save for next call
    return result.stdout
```

**Key:** `--resume` = CC CLI's built-in session continuity. Not Agent SDK (Python). Not expensive. Same Anthropic API cost as normal CC usage. Session .jsonl written automatically to `~/.claude/projects/`.

**Verify:**
- POST to localhost:7891 with a message
- POST again referencing the first exchange
- Second response demonstrates context retention

**Status:** NOT STARTED

---

## B3: Wire Hub-Bridge /cc Route

**What:** hub-bridge on vault-neo proxies /cc requests → Tailscale → P1:7891.

**How:**
- Add `/cc` route to hub-bridge server.js
- Route: `POST /cc` → forward to `http://100.124.194.102:7891` (P1 Tailscale IP)
- Auth: same Bearer token as /v1/chat (zero new auth surface)
- Timeout: 120s (CC can be slow on complex tasks)

**Verify:**
```bash
curl -X POST https://hub.arknexus.net/cc \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is 2+2?"}'
# → Response from real CC on P1, not llama3.1:8b
```

**Status:** NOT STARTED

---

## B4: Survival Across Reboots

**What:** cc_server_p1.py must survive a P1 reboot without manual intervention. (AC#8 from original plan.)

**How:** Register as Windows service or Task Scheduler startup task.
- Option 1: NSSM (Non-Sucking Service Manager) wraps Python process as Windows service
- Option 2: Task Scheduler `KarmaJulianServer` — trigger: At startup, run cc_server_p1.py

**Verify:** Reboot P1 → wait 60s → `curl hub.arknexus.net/cc` responds without Colby touching anything.

**Status:** NOT STARTED

---

## B-GATE

All complete when:
- [ ] `netstat -ano | findstr 7891` shows exactly ONE process (B1)
- [ ] POST to /cc returns response from real CC with context retention (B2+B3)
- [ ] P1 reboot → /cc responds within 60s automatically (B4)

When B-GATE passes → start PLAN-C.
