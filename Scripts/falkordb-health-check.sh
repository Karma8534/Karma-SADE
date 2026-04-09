#!/bin/bash
# FalkorDB health check — posts bus alert if container is not running
# Installed on vault-neo at /opt/seed-vault/scripts/falkordb-health-check.sh
# Cron: */5 * * * * /opt/seed-vault/scripts/falkordb-health-check.sh >> /var/log/falkordb-health.log 2>&1
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
