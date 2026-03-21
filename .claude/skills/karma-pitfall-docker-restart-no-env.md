---
name: karma-pitfall-docker-restart-no-env
description: Use before any hub-bridge env var change. docker restart reuses the existing container environment — new env_file entries are silently ignored.
type: feedback
---

## Rule

`docker restart anr-hub-bridge` does NOT re-read hub.env. New environment variables are NOT picked up. Always use `docker compose -f compose.hub.yml up -d` to recreate the container.

**Why:** Session 66: After adding `GLM_RPM_LIMIT` to hub.env and running `docker restart`, the variable was not visible inside the container. `docker restart` reuses the existing container's environment snapshot from when it was created. Only `docker compose up -d` recreates the container with current env_file state.

**How to apply:**
```bash
# WRONG: picks up nothing new
docker restart anr-hub-bridge

# RIGHT: recreates container, re-reads hub.env
cd /opt/seed-vault/memory_v1/hub_bridge
docker compose -f compose.hub.yml up -d
```
Compose file location: `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml` — NOT in git repo root.

## Evidence

- Session 66: GLM_RPM_LIMIT added to hub.env, docker restart used → variable absent in container → `docker compose up -d` fixed it
- CLAUDE.md Known Pitfalls section
