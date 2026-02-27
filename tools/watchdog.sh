#!/bin/bash
# Step 4.9: Watchdog / Self-Repair
# Monitors FalkorDB memory, stuck observer, container health.
# Run via cron every 5 minutes: */5 * * * * /opt/seed-vault/memory_v1/tools/watchdog.sh >> /opt/seed-vault/memory_v1/ledger/watchdog.log 2>&1

VAULT_DIR="/opt/seed-vault/memory_v1"
LOG_PREFIX="[WATCHDOG $(date -u +%Y-%m-%dT%H:%M:%SZ)]"
FALKORDB_MEM_LIMIT_MB=1500
OBSERVER_STALE_SECONDS=300

# 1. Check FalkorDB memory usage
FALKOR_CONTAINER=$(docker ps -q --filter name=falkordb 2>/dev/null)
if [ -n "$FALKOR_CONTAINER" ]; then
    MEM_USAGE=$(docker stats --no-stream --format "{{.MemUsage}}" "$FALKOR_CONTAINER" 2>/dev/null | awk -F'/' '{print $1}' | tr -d ' ')
    MEM_MB=$(echo "$MEM_USAGE" | awk '{
        if (index($0, "GiB") > 0) { gsub(/GiB/, ""); printf "%.0f", $0 * 1024; }
        else if (index($0, "MiB") > 0) { gsub(/MiB/, ""); printf "%.0f", $0; }
        else { print 0; }
    }')
    
    if [ "$MEM_MB" -gt "$FALKORDB_MEM_LIMIT_MB" ] 2>/dev/null; then
        echo "$LOG_PREFIX ALERT: FalkorDB using ${MEM_MB}MB (limit: ${FALKORDB_MEM_LIMIT_MB}MB). Restarting."
        docker restart "$FALKOR_CONTAINER" 2>/dev/null
        sleep 10
        echo "$LOG_PREFIX FalkorDB restarted."
    fi
else
    echo "$LOG_PREFIX WARNING: FalkorDB container not found."
fi

# 2. Check observer / consciousness loop (last observation timestamp)
if [ -f "$VAULT_DIR/memory.db" ]; then
    LAST_OBS=$(sqlite3 "$VAULT_DIR/memory.db" "SELECT MAX(observed_at) FROM observations" 2>/dev/null)
    NOW=$(date +%s)
    if [ -n "$LAST_OBS" ]; then
        LAST_OBS_INT=${LAST_OBS%.*}
        AGE=$((NOW - LAST_OBS_INT))
        if [ "$AGE" -gt "$OBSERVER_STALE_SECONDS" ] 2>/dev/null; then
            echo "$LOG_PREFIX WARNING: Observer stale — last observation ${AGE}s ago (limit: ${OBSERVER_STALE_SECONDS}s)."
            KARMA_CONTAINER=$(docker ps -q --filter name=karma-server 2>/dev/null)
            if [ -n "$KARMA_CONTAINER" ]; then
                echo "$LOG_PREFIX Restarting karma-server to recover observer."
                docker restart "$KARMA_CONTAINER" 2>/dev/null
                sleep 15
                echo "$LOG_PREFIX karma-server restarted."
            fi
        fi
    fi
fi

# 3. Check container health
for CONTAINER in karma-server anr-hub-bridge anr-vault-api anr-vault-db falkordb; do
    STATUS=$(docker inspect --format='{{.State.Status}}' "$CONTAINER" 2>/dev/null)
    if [ "$STATUS" != "running" ]; then
        echo "$LOG_PREFIX ALERT: $CONTAINER is $STATUS. Attempting restart."
        docker start "$CONTAINER" 2>/dev/null
        sleep 5
    fi
done

# 4. Disk usage check (warn at 80%)
DISK_PCT=$(df /opt/seed-vault | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$DISK_PCT" -gt 80 ] 2>/dev/null; then
    echo "$LOG_PREFIX WARNING: Disk usage at ${DISK_PCT}%."
fi
