---
name: karma-pitfall-hub-bridge-build-context
description: Use before any hub-bridge deployment. Build source is /opt/seed-vault/.../hub_bridge/ NOT the git repo. These diverge silently — git pull on vault-neo does not update the build context.
type: feedback
---

## Rule

hub-bridge Docker builds from `/opt/seed-vault/memory_v1/hub_bridge/` as build context — NOT from the git repo at `/home/neo/karma-sade/hub-bridge/`. After every `git pull` on vault-neo, you MUST manually sync changed files before rebuilding.

**Why:** Multiple sessions lost to this: `git pull` succeeds, `--no-cache` rebuild succeeds, container starts — but running OLD code because the sync step was skipped. No error at any step. The build context is the only thing that matters for what gets compiled into the image.

**How to apply:**
```bash
# After git pull on vault-neo, before rebuild:
cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js

# For lib/ files (check git diff first):
git diff --name-only HEAD~1 | grep hub-bridge | while read f; do
    cp /home/neo/karma-sade/$f /opt/seed-vault/memory_v1/hub_bridge/${f#hub-bridge/}
done

# lib/*.js location in git: hub-bridge/lib/*.js
# lib/*.js location in build context: /opt/seed-vault/memory_v1/hub_bridge/lib/*.js
# compose.hub.yml is IN the build context dir, not the git repo

# Rebuild command (from build context dir):
cd /opt/seed-vault/memory_v1/hub_bridge
docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d
```

## Evidence

- Sessions 67-81: Multiple deploys with stale code — traced to missing sync step
- Session 75: lib/*.js files not in git until then (existed only in build context)
- Decision #27, #29 in architecture.md
