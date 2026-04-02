---
name: karma-verify
description: Use after any deployment to vault-neo (karma-server or hub-bridge) to confirm the service started correctly before declaring the deployment complete.
---

# karma-verify

## Overview

Verify a deployment succeeded before closing the session. RestartCount=0 is the minimum bar. Logs and /health confirm the service is actually functional.

## karma-server Verification

```bash
# 1. RestartCount must be 0
ssh vault-neo "docker inspect karma-server --format '{{.RestartCount}}'"
# Expected: 0

# 2. Startup banner in logs
ssh vault-neo "docker logs karma-server --tail=25 2>&1 | grep -E 'KARMA CHAT SERVER|ACTIVE|FAILED|ERROR|Pattern cache'"
# Expected: "KARMA CHAT SERVER — Online" + services listed as ACTIVE

# 3. Health endpoint
ssh vault-neo "curl -s localhost:8340/health | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d[\"ok\"], d[\"graph_stats\"])'"
# Expected: True {entities: N, episodes: N}

# 4. /raw-context smoke test
ssh vault-neo "curl -s 'localhost:8340/raw-context?q=Karma' | python3 -c 'import sys,json; r=json.load(sys.stdin); print(r[\"ok\"])'"
# Expected: True
```

## hub-bridge Verification

```bash
# 1. RestartCount must be 0
ssh vault-neo "docker inspect anr-hub-bridge --format '{{.RestartCount}}'"
# Expected: 0

# 2. Startup logs
ssh vault-neo "docker logs anr-hub-bridge --tail=20 2>&1 | grep -E 'listening|ERROR|identity|WARN'"
# Expected: listening on port + identity block loaded

# 3. /v1/chat smoke test (requires token)
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "ping"}' | python3 -c 'import sys,json; r=json.load(sys.stdin); print("ok" if r.get("assistant_text") else "FAILED")'
```

## Failure Responses

| Symptom | Action |
|---------|--------|
| RestartCount > 0 | Check logs: `docker logs <name> --tail=50 2>&1 \| grep -i error` |
| SyntaxError in logs | Python syntax error — fix and redeploy |
| Health returns 500 | FalkorDB connection issue — check `docker ps` for falkordb container |
| /v1/chat returns 401 | Token path wrong — verify `/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt` |
| RestartCount climbing | Container is crash-looping — do NOT leave it running, fix immediately |
