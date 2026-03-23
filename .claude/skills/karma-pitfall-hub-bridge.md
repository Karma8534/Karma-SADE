---
name: karma-pitfall-hub-bridge
description: Auto-synthesized from HARVEST. Pattern seen in 5+ sessions. Invoke when working with hub-bridge server.js, ambient capture, or deployment.
type: feedback
---

## Rule
Before assuming any hub-bridge endpoint works, grep server.js for occurrences. Endpoints referenced in CLAUDE.md or hook scripts may not exist in the actual running code.

**Why:** /v1/ambient was missing for an unknown duration. All git post-commit and session-end hook captures silently 404'd. "not_found" response from hub-bridge is not a 404 HTTP status — it's a JSON body, easy to miss in logs.

**How to apply:** After any hub-bridge deploy: smoke-test every capture path explicitly. After adding a new endpoint: verify with curl from vault-neo before declaring complete.

## Evidence

- **Session 117 (ccKarma2-1.md)**: /v1/ambient = 0 occurrences in server.js. Discovered when debugging why captures weren't landing. Duration of silent failure: unknown.
- **Session 118 (ccKarma2-2.md)**: /v1/ambient added at line 3403. Proof: {"ok":true,"id":"mem_VkD-qKcKpwei25X0"}. Hooks now capture to vault.
- **ccSession032026-FULLMETA.md**: hub-bridge Docker build uses /opt/seed-vault/.../hub_bridge/app/server.js as build source — NOT git repo. Always cp after git pull before --no-cache rebuild.
- **Multiple sessions**: cp -r does NOT overwrite existing files in dest/. Always use explicit per-file copies when syncing to build context.

## Hard rules
- Smoke test: `curl -X POST https://hub.arknexus.net/v1/ambient -H "Authorization: Bearer $CAPTURE_TOKEN" -H "Content-Type: application/json" -d '{"source":"test","content":"test"}'` — must return `{"ok":true}`
- hub-bridge build context: /opt/seed-vault/memory_v1/hub_bridge/app/server.js (NOT git repo at /home/neo/karma-sade/)
- Always grep server.js before claiming an endpoint exists: `grep -c "ambient" hub-bridge/app/server.js`
- Deploy order: git commit → push → pull vault-neo → cp to build context → --no-cache rebuild → verify
