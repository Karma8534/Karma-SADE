---
name: karma-pitfall-cp-no-overwrite
description: Use before any hub-bridge or karma-server deployment. cp -r silently skips existing files in dest/ — causes stale build context deploys.
type: feedback
---

## Rule

Never use `cp -r source/ dest/` to sync hub-bridge or karma-server files to build context. Always use explicit per-file copies.

**Why:** Session 81 (Decision #29): `cp -r` silently skips files already present in dest/. A fix to `unified.html` (upload fix committed to git) was never applied to the build context — the old broken file stayed. `docker compose build --no-cache` built the stale code with no error. Deployed broken behavior. The fix was sitting in git for an entire session before the cause was found.

**How to apply:**
```bash
# WRONG: cp -r /home/neo/karma-sade/hub-bridge/app/ /opt/seed-vault/memory_v1/hub_bridge/app/
# RIGHT: explicit per-file copies
cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js
cp /home/neo/karma-sade/hub-bridge/lib/feedback.js /opt/seed-vault/memory_v1/hub_bridge/lib/feedback.js
```
Before every `--no-cache` rebuild: `git diff --name-only HEAD~1 | grep hub-bridge` then cp EVERY changed file explicitly.

## Evidence

- Session 81: upload fix deployed but build context had stale `unified.html` — diagnosed after full session of confusion
- Decision #29 in architecture.md
