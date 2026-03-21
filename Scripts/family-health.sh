#!/bin/bash
# family-health.sh — Unified Karma family health check
# Run on vault-neo: bash Scripts/family-health.sh
# Checks 7 components → HEALTHY / DEGRADED / DOWN

set -uo pipefail

PASS=0
WARN=0
FAIL=0

check() {
    local name="$1"
    local status="$2"
    local detail="$3"
    printf "  %-32s %s\n" "$name" "$status"
    [ -n "$detail" ] && printf "    %s\n" "$detail"
}

echo "=== KARMA FAMILY HEALTH $(date -u '+%Y-%m-%dT%H:%M:%SZ') ==="
echo ""

# --- VAULT-NEO CONTAINERS ---
echo "[VAULT-NEO CONTAINERS]"

for container in anr-hub-bridge karma-server falkordb anr-vault-api; do
    info=$(docker inspect "$container" 2>/dev/null) || { check "$container" "DOWN" "container not found"; ((FAIL++)); continue; }
    running=$(echo "$info" | python3 -c "import sys,json; d=json.load(sys.stdin)[0]; print(d['State']['Running'])")
    restarts=$(echo "$info" | python3 -c "import sys,json; d=json.load(sys.stdin)[0]; print(d['RestartCount'])")
    if [ "$running" = "True" ] && [ "$restarts" -eq 0 ]; then
        check "$container" "HEALTHY" ""
        ((PASS++))
    elif [ "$running" = "True" ] && [ "$restarts" -gt 0 ]; then
        check "$container" "DEGRADED" "RestartCount=$restarts"
        ((WARN++))
    else
        status=$(echo "$info" | python3 -c "import sys,json; d=json.load(sys.stdin)[0]; print(d['State']['Status'])")
        check "$container" "DOWN" "Status=$status RestartCount=$restarts"
        ((FAIL++))
    fi
done

# --- HUB-BRIDGE API ---
echo ""
echo "[HUB-BRIDGE API]"

TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt 2>/dev/null || echo "")
if [ -z "$TOKEN" ]; then
    check "hub-bridge /health" "DOWN" "token not found"
    ((FAIL++))
else
    http_code=$(curl -s -o /dev/null -w "%{http_code}" -m 5 -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/health 2>/dev/null || echo "000")
    if [ "$http_code" = "200" ]; then
        check "hub-bridge /health" "HEALTHY" "HTTP 200"
        ((PASS++))
    else
        check "hub-bridge /health" "DEGRADED" "HTTP $http_code"
        ((WARN++))
    fi

    bus_code=$(curl -s -o /dev/null -w "%{http_code}" -m 5 -H "Authorization: Bearer $TOKEN" "https://hub.arknexus.net/v1/coordination/recent?limit=1" 2>/dev/null || echo "000")
    if [ "$bus_code" = "200" ]; then
        check "coordination-bus" "HEALTHY" "HTTP 200"
        ((PASS++))
    else
        check "coordination-bus" "DEGRADED" "HTTP $bus_code"
        ((WARN++))
    fi
fi

# --- K2 SERVICES ---
echo ""
echo "[K2 SERVICES]"

k2_result=$(ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes localhost \
    "systemctl is-active karma-regent aria 2>/dev/null; echo '---'; cat /mnt/c/dev/Karma/k2/cache/regent_control/vesper_pipeline_status.json 2>/dev/null | python3 -c \"import sys,json; d=json.load(sys.stdin); print('pipeline selfimproving=' + str(d.get('self_improving','?')))\" 2>/dev/null || echo 'pipeline read failed'" \
    2>/dev/null || echo "SSH_FAIL")

if [ "$k2_result" = "SSH_FAIL" ]; then
    check "K2 SSH" "DOWN" "cannot reach K2 via tunnel (vault-neo:2223)"
    check "karma-regent.service" "UNKNOWN" ""
    check "aria.service" "UNKNOWN" ""
    check "vesper-pipeline" "UNKNOWN" ""
    ((FAIL++))
else
    regent_active=$(echo "$k2_result" | sed -n '1p')
    aria_active=$(echo "$k2_result" | sed -n '2p')
    pipeline_line=$(echo "$k2_result" | grep 'pipeline selfimproving' || echo "pipeline selfimproving=?")

    [ "$regent_active" = "active" ] && { check "karma-regent.service" "HEALTHY" "active"; ((PASS++)); } || { check "karma-regent.service" "DOWN" "status=$regent_active"; ((FAIL++)); }
    [ "$aria_active" = "active" ] && { check "aria.service" "HEALTHY" "active"; ((PASS++)); } || { check "aria.service" "DEGRADED" "status=$aria_active"; ((WARN++)); }

    if echo "$pipeline_line" | grep -q "True"; then
        check "vesper-pipeline" "HEALTHY" "$pipeline_line"
        ((PASS++))
    else
        check "vesper-pipeline" "DEGRADED" "$pipeline_line"
        ((WARN++))
    fi
fi

# --- SUMMARY ---
echo ""
echo "=== SUMMARY ==="
TOTAL=$((PASS + WARN + FAIL))
echo "  HEALTHY:  $PASS / $TOTAL"
echo "  DEGRADED: $WARN / $TOTAL"
echo "  DOWN:     $FAIL / $TOTAL"
echo ""
if [ "$FAIL" -gt 0 ]; then
    echo "STATUS: DEGRADED (failures present)"
    exit 2
elif [ "$WARN" -gt 0 ]; then
    echo "STATUS: DEGRADED (warnings present)"
    exit 1
else
    echo "STATUS: HEALTHY"
    exit 0
fi
