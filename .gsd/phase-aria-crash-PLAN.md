# Phase: aria-crash — aria.service Crash Loop Diagnosis + Fix
Generated: 2026-03-22 (Session 125 wrap)

## Task 1 — Read crash traceback from K2 systemd journal
```
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes localhost 'journalctl --user -xe -u aria.service -n 100 --no-pager'"
```
<verify>Python traceback visible in output, showing exact file + line where startup fails</verify>
<done>false</done>

## Task 2 — Check port 7890 for zombie holder
```
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes localhost 'ss -tlnp | grep 7890 || echo port-free'"
```
<verify>Either "port-free" or PID shown. If PID held: identify process, kill if it's a zombie</verify>
<done>false</done>

## Task 3 — Verify systemd drop-in still present
```
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes localhost 'cat /etc/systemd/system/aria.service.d/10-aria-env.conf 2>/dev/null || echo MISSING'"
```
<verify>`Environment=HOME=/home/karma` present. If MISSING: recreate drop-in + daemon-reload</verify>
<done>false</done>

## Task 4 — Fix root cause identified in Task 1
Apply targeted fix for whatever the traceback shows. Common cases:
- Zombie on port: `kill -9 PID; systemctl --user restart aria.service`
- Drop-in missing: recreate + `systemctl --user daemon-reload`
- Import error: check pip install / missing package
- Syntax error in aria code: patch the specific file
<verify>aria.service shows `Active: active (running)` with no FAILED in status</verify>
<done>false</done>

## Task 5 — Verify aria endpoint responds
```
ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes localhost 'curl -s http://localhost:7890/health'"
```
<verify>HTTP 200 response from aria /health endpoint</verify>
<done>false</done>

## Task 6 — Verify shell_run tool works end-to-end
Send a test message to Karma with `x-karma-deep: true` that exercises shell_run. Or test via bus:
```
ssh vault-neo "python3 -c \"import json,urllib.request; token=open('/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt').read().strip(); payload=json.dumps({'command':'echo aria-test-ok'}).encode(); req=urllib.request.Request('https://hub.arknexus.net/v1/shell-run',data=payload,headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'},method='POST'); r=urllib.request.urlopen(req,timeout=15); print(r.read())\""
```
<verify>Response contains "aria-test-ok" in stdout field</verify>
<done>false</done>

## Task 7 — Update STATE.md: K-3 blocker resolved
Mark aria.service FIXED, update K-3 from WARNING to VERIFIED-PARTIAL (ambient obs still needed).
<verify>STATE.md updated, committed</verify>
<done>false</done>

## Notes
- All K2 SSH uses `ssh vault-neo "ssh -p 2223 -l karma ..."` pattern (NOT `neo@`)
- Heredoc pattern for Python on K2: `cat << 'PYEOF' | ssh ... python3` then PYEOF
- Do NOT start fixing until Task 1 gives the traceback (no blind guessing)
- Loop circuit breaker: if 3 fix attempts fail → STOP, post to bus, await Sovereign
