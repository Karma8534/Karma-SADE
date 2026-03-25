# Phase: Plan-B Julian — Implementation Plan
**Created:** 2026-03-23 (Session 136)
**Context:** `.gsd/phase-plan-b-julian-CONTEXT.md`
**Spec:** `Karma2/PLAN-B-julian.md`

---

## Task 1: Kill zombie PIDs on port 7891 (B1)

**Action:** Check current state of port 7891 and cc_server_p1.py processes:
```powershell
netstat -ano | findstr ":7891"
# Note all PIDs
Get-Process -Id <pids> | Select-Object Id, ProcessName, StartTime
```
Then fix `Scripts/Start-CCServer.ps1` restart loop: kill all PIDs on 7891 before spawning new one.

<verify>netstat -ano | findstr 7891 shows exactly ONE process after running Start-CCServer.ps1</verify>
<done>[x] Task 1 complete — 1 process on 7891 (PID 14572). Added kill-on-port-7891 block at top of Start-CCServer.ps1 before while loop. Script now kills any existing 7891 processes before spawning new one.</done>

---

## Task 2: Read cc_server_p1.py to understand current implementation

**Action:** Read `Scripts/cc_server_p1.py` to understand current Ollama integration, then plan the --resume replacement.

<verify>Know exactly which function to replace (run_cc equivalent), its signature, and where session ID should persist.</verify>
<done>[x] Task 2 complete — inline Ollama block in do_POST lines 109-132. No separate run_cc(). Session ID in ~/.cc_server_session_id.</done>

---

## Task 3: Replace Ollama backend with CC --resume subprocess (B2)

**Action:** Update cc_server_p1.py:
- Replace Ollama API call with `subprocess.run(["claude", "-p", prompt, "--resume", session_id])`
- Add SESSION_FILE = Path("~/.cc_server_session_id").expanduser() for persistence
- Handle new-session case (no --resume on first call)
- Extract and save session ID from output

<verify>
- POST localhost:7891 → response from real CC (not llama)
- POST second message → response demonstrates context retention (references first message)
</verify>
<done>[x] Task 3 complete — run_cc() written, CLAUDE_CMD=C:\Users\raest\AppData\Roaming\npm\claude.cmd. POST 1: "Noted, ZEPHYR99." POST 2: "ZEPHYR99." — context retained via --resume. Verified.</done>

---

## Task 4: Wire hub-bridge /cc route to P1:7891 (B3)

**Action:** Add `/cc` POST route to hub-bridge server.js on vault-neo:
- Forward to `http://100.124.194.102:7891` (P1 Tailscale IP)
- Auth: same Bearer token check as /v1/chat
- Timeout: 120s

Deploy via standard hub-bridge deploy procedure.

<verify>
```bash
curl -X POST https://hub.arknexus.net/cc \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "What is 2+2?"}'
```
Returns response from real CC, not llama3.1:8b.
</verify>
<done>[x] Task 4 complete — /cc route already existed in hub-bridge (CC_SERVER_URL=http://100.124.194.102:7891). /cc/health OK. POST to hub.arknexus.net/cc returned: "I am Claude Code — CC Ascendant, Karma's voice and peer." No deploy needed.</done>

---

## Task 5: Register cc_server as Windows startup task (B4)

**Action:** Register Task Scheduler task `KarmaJulianServer`:
```powershell
schtasks /create /tn "KarmaJulianServer" /tr "powershell.exe -WindowStyle Hidden -File 'Scripts\Start-CCServer.ps1'" /sc onlogon /ru "$env:USERNAME" /f
```

<verify>
- Reboot P1 (or simulate: Stop + Start task)
- curl hub.arknexus.net/cc responds within 60s without manual intervention
</verify>
<done>[x] Task 5 complete — KarmaCCServer HKCU Run key already exists (equivalent to KarmaJulianServer). Task Scheduler access denied — Run key used instead. Start-CCServer.ps1 loop started in background; crash recovery verified: killed PID 36344, restarted as PID 36920 within 15s. HKCU Run key fires on every logon.</done>

---

## B-GATE Check

All tasks complete when:
- [ ] netstat -ano | findstr 7891 shows exactly ONE process (B1)
- [ ] POST to /cc returns response from real CC with context retention (B2+B3)
- [ ] P1 reboot → /cc responds within 60s automatically (B4)
