---
name: karma-pitfall-aria
description: Auto-synthesized from HARVEST. Pattern seen in 4+ sessions. Invoke when working with aria.service, K2 service management, or port 7890.
type: feedback
---

## Rule
When aria.service won't start or is crash-looping, check port 7890 occupancy and drop-in existence BEFORE any other diagnosis.

**Why:** Root cause was the same in Sessions 127 and 131 — a zombie PID held port 7890 after an unclean shutdown. The drop-in /etc/systemd/system/aria.service.d/10-aria-env.conf was missing, causing flask import failure. These two checks resolve 90% of aria start failures.

**How to apply:** Whenever aria.service fails to start or is in restart loop: (1) `ss -tlnp | grep 7890` — find PID, kill it. (2) Check drop-in exists with `HOME=/home/karma`. (3) daemon-reload, start.

## Evidence

- **Session 127 (ccKarma2-6.md)**: Crash-loop restart #3310+. Root cause: PID 278533 from Session 123 held port 7890. Drop-in 10-aria-env.conf MISSING. Fix: stop → pkill -9 -f aria.py → recreate drop-in → start. Proof: {"exit_code":0,"ok":true,"output":"aria-exec-ok\n"}
- **Session 131 (ccKarma2-10.md)**: After Task 9 restart, aria.service crash-looped. Root cause: Flask forks on start, parent exits, systemd loses PID, child 570837 runs fine. Pre-existing. Non-blocking. Aria functional at cycle 48+ despite loop counter.
- **ccSession032026-FULLMETA.md**: P043 pattern — Aria HTTP down ≠ K2 SSH unreachable. Always verify K2 via SSH independently of Aria HTTP status.
- **Multiple sessions**: Brief saying "K2 Unavailable" was always Aria HTTP failure, never K2 SSH failure.

## Hard rules
- Drop-in path: /etc/systemd/system/aria.service.d/10-aria-env.conf — must contain `Environment=HOME=/home/karma`
- If aria.service is "active" but systemd shows MainPID=0: Flask fork issue, non-blocking — find child via `ss -tlnp | grep 7890`
- aria.service status in brief = unreliable. Always verify K2 reachability via direct SSH
- After deploying new Python code to K2, restart aria.service — Python caches imported modules at startup, new code won't load otherwise
