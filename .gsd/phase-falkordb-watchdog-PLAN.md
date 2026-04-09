# FalkorDB Auto-Restart + Alert Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent FalkorDB silent-exit outages by adding `--restart=unless-stopped` and a 5-minute cron alert on vault-neo.

**Architecture:** Recreate FalkorDB container with Docker restart policy (handles auto-recovery), then install a shell script that polls container state every 5 minutes and posts a coordination bus alert if down. No new services, no K2 dependency.

**Tech Stack:** Docker, bash, vault-neo crontab, hub coordination bus (POST /v1/coordination/post)

---

### Task 1: Recreate FalkorDB with restart=unless-stopped

**Files:**
- Modify: vault-neo FalkorDB container (runtime, not a file)

- [ ] **Step 1: Verify current restart policy**

```bash
ssh vault-neo "docker inspect falkordb --format '{{.HostConfig.RestartPolicy.Name}}'"
```
Expected: `no`

- [ ] **Step 2: Stop the container (do NOT remove volume)**

```bash
ssh vault-neo "docker stop falkordb && docker rm falkordb"
```
Expected: `falkordb` printed twice (stop then rm). Volume `anr-falkordb-data` survives.

Verify volume intact:
```bash
ssh vault-neo "docker volume inspect anr-falkordb-data --format '{{.Name}}'"
```
Expected: `anr-falkordb-data`

- [ ] **Step 3: Recreate with unless-stopped restart policy**

```bash
ssh vault-neo "docker run -d \
  --name falkordb \
  --restart unless-stopped \
  --network anr-vault-net \
  -p 127.0.0.1:6379:6379 \
  -p 127.0.0.1:3000:3000 \
  -e FALKORDB_DATA_PATH=/data \
  -e 'FALKORDB_ARGS=TIMEOUT 10000 MAX_QUEUED_QUERIES 100' \
  -v anr-falkordb-data:/data \
  falkordb/falkordb"
```
Expected: container ID printed (64-char hex)

- [ ] **Step 4: Verify restart policy and health**

```bash
ssh vault-neo "docker inspect falkordb --format '{{.HostConfig.RestartPolicy.Name}}' && docker inspect falkordb --format '{{.State.Running}}'"
```
Expected:
```
unless-stopped
true
```

- [ ] **Step 5: Verify FalkorDB graph still accessible**

```bash
ssh vault-neo "docker exec falkordb redis-cli GRAPH.LIST 2>/dev/null | head -5 || echo 'FALKORDB_RESPONSIVE'"
```
Expected: graph names (including `neo_workspace`) or `FALKORDB_RESPONSIVE`

- [ ] **Step 6: Commit MEMORY.md with restart policy change**

Update MEMORY.md to note FalkorDB now has `unless-stopped` restart policy. Then:
```bash
cd "C:/Users/raest/Documents/Karma_SADE"
powershell -Command "git add MEMORY.md; git commit -m 'ops: FalkorDB restart policy changed to unless-stopped'"
powershell -Command "git push origin main"
```

---

### Task 2: Install health-check cron on vault-neo

**Files:**
- Create: `/opt/seed-vault/scripts/falkordb-health-check.sh` on vault-neo (via SSH write)
- Modify: vault-neo root crontab (`crontab -e` or `crontab -` pattern)

- [ ] **Step 1: Write health check script to vault-neo (via scp, not heredoc — P019)**

Write file locally first, then scp to vault-neo.

Create `Scripts/falkordb-health-check.sh` locally:
```bash
#!/bin/bash
# FalkorDB health check — posts bus alert if container is not running
LOGFILE=/var/log/falkordb-health.log
TOKEN_FILE=/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt
HUB_URL=https://hub.arknexus.net/v1/coordination/post

RUNNING=$(docker inspect falkordb --format '{{.State.Running}}' 2>/dev/null)
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
if [ "$RUNNING" != "true" ]; then
  echo "[$TS] ALERT: FalkorDB not running (state=$RUNNING)" >> $LOGFILE
  TOKEN=$(cat $TOKEN_FILE 2>/dev/null)
  if [ -n "$TOKEN" ]; then
    MSG="[INFRA ALERT $TS] FalkorDB container is DOWN on vault-neo. Auto-restart should have triggered. Check: docker ps -a | grep falkordb"
    curl -sf -X POST "$HUB_URL" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{\"from\":\"vault-neo-cron\",\"to\":\"all\",\"type\":\"alert\",\"urgency\":\"blocking\",\"content\":\"$MSG\"}" >> $LOGFILE 2>&1
  fi
else
  echo "[$TS] OK: FalkorDB running" >> $LOGFILE
fi
```

Then push to vault-neo:
```bash
ssh vault-neo "mkdir -p /opt/seed-vault/scripts"
scp "C:/Users/raest/Documents/Karma_SADE/Scripts/falkordb-health-check.sh" vault-neo:/opt/seed-vault/scripts/falkordb-health-check.sh
ssh vault-neo "chmod +x /opt/seed-vault/scripts/falkordb-health-check.sh"
```

- [ ] **Step 2: Verify script was written correctly**

```bash
ssh vault-neo "head -5 /opt/seed-vault/scripts/falkordb-health-check.sh && ls -la /opt/seed-vault/scripts/falkordb-health-check.sh"
```
Expected: script header lines + `-rwxr-xr-x` permissions

- [ ] **Step 3: Run script manually — verify OK log line**

```bash
ssh vault-neo "/opt/seed-vault/scripts/falkordb-health-check.sh && tail -3 /var/log/falkordb-health.log"
```
Expected: `[TIMESTAMP] OK: FalkorDB running`

- [ ] **Step 4: Register cron (every 5 minutes)**

```bash
ssh vault-neo "(crontab -l 2>/dev/null; echo '*/5 * * * * /opt/seed-vault/scripts/falkordb-health-check.sh >> /var/log/falkordb-health.log 2>&1') | crontab -"
```

- [ ] **Step 5: Verify cron entry**

```bash
ssh vault-neo "crontab -l | grep falkordb"
```
Expected: `*/5 * * * * /opt/seed-vault/scripts/falkordb-health-check.sh >> /var/log/falkordb-health.log 2>&1`

- [ ] **Step 6: Simulate down state — verify alert fires**

```bash
# Stop FalkorDB, run script, verify bus alert, restart FalkorDB
ssh vault-neo "docker stop falkordb && /opt/seed-vault/scripts/falkordb-health-check.sh && tail -5 /var/log/falkordb-health.log"
```
Expected log: `ALERT: FalkorDB not running`

```bash
# Verify bus received the alert
TOKEN=$(ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt')
ssh vault-neo "curl -s -H 'Authorization: Bearer $TOKEN' 'http://localhost:18090/v1/coordination/recent?from=vault-neo-cron&limit=2' | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d[\"count\"], \"alerts\" if d[\"count\"] else \"NO_ALERTS\")'"
```
Expected: `1 alerts` (or higher)

```bash
# FalkorDB should have auto-restarted due to unless-stopped policy
ssh vault-neo "sleep 5 && docker inspect falkordb --format '{{.State.Running}}'"
```
Expected: `true`

- [ ] **Step 7: Commit MEMORY.md + push**

Update MEMORY.md to note cron health check installed. Then:
```bash
cd "C:/Users/raest/Documents/Karma_SADE"
powershell -Command "git add MEMORY.md; git commit -m 'ops: FalkorDB health-check cron installed on vault-neo'"
powershell -Command "git push origin main"
```

---

### Acceptance Summary

| Check | Command | Expected |
|-------|---------|----------|
| Restart policy | `docker inspect falkordb --format '{{.HostConfig.RestartPolicy.Name}}'` | `unless-stopped` |
| Cron registered | `crontab -l \| grep falkordb` | cron entry present |
| Script executable | `ls -la /opt/seed-vault/scripts/falkordb-health-check.sh` | `-rwxr-xr-x` |
| Alert on down | Stop container → run script → check log | `ALERT: FalkorDB not running` |
| Auto-restart works | After stop → wait 5s → check state | `true` |
