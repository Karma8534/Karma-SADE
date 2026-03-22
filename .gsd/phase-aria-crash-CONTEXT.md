# Phase: aria-crash — aria.service Crash Loop Diagnosis
Generated: 2026-03-22 (Session 125 wrap)

## What We're Doing
Diagnosing and fixing the aria.service crash loop on K2. The service is in restart loop #2015+, exiting with code=1/FAILURE every ~15s. This was "fixed" in Session 123 (zombie PID killed) but re-entered crash loop.

## Why It Matters
aria.service is the entire K-3 ambient pipeline:
- ambient_observer.py — watchdog feed, regent evolution
- shell_run tool — Karma's local compute access
- /api/exec endpoint — K2 command execution
- vesper pipeline stages — watchdog/eval/governor all depend on aria being alive

Until fixed: K-3 = DEAD, Kiki's ambient observation loop offline, governor can't write to FalkorDB.

## What We Know
- Session 123: zombie `python3 -m aria` process held port 7890 → killed → service restarted OK
- Current state: restart #2015+ (as of Session 125 audit ~2026-03-22 14:00 UTC)
- Exit code: 1/FAILURE — this is a startup crash (not a runtime crash)
- Systemd drop-in `/etc/systemd/system/aria.service.d/10-aria-env.conf` adds `Environment=HOME=/home/karma` — required for flask import
- Port: 7890 (aria /api/exec endpoint)

## What We Don't Know
- The Python traceback — never read `journalctl --user -xe -u aria.service` this session
- Whether port 7890 is held again by another process
- Whether the drop-in still exists after any WSL reset
- Whether a dependency (flask, etc.) was broken by a pip update

## Constraints
- K2 SSH: `ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes localhost 'CMD'"`
- Heredoc pattern for multi-line: use `cat << 'PYEOF' | python3` on K2 side
- Do NOT edit K2 files directly from vault-neo without verification
- Do NOT restart aria.service blind — read traceback first

## What We're NOT Doing
- Not rebuilding/reinstalling aria from scratch without understanding root cause
- Not patching K2 Python files until traceback confirms location of failure
- Not marking K-3 DONE until ambient observer completes a full watchdog cycle

## Acceptance Criteria
- aria.service shows `Active: active (running)` with restart_counter stable
- `curl localhost:7890/health` from K2 returns 200
- /api/exec processes a test command successfully
- Watchdog completes one cycle with structured entries captured
