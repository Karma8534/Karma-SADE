#!/usr/bin/env bash
# Step 4.5: Script Distillation (P13)
# Distilled operations — reliable tool-call sequences saved as shell scripts.
# Zero ongoing LLM cost for repeated operations.
#
# Usage: distilled_ops.sh <operation> [args...]
set -euo pipefail
KARMA_URL="http://localhost:8340"
HUB_URL="http://localhost:18090"
TOKEN="${HUB_BRIDGE_TOKEN:-cb5617b2ce67470d389dcff1e1fe417aa2626ae699c7d5f831b133cb1f4d450e}"
_curl_get() { curl -sf -H "Authorization: Bearer $TOKEN" "$1" 2>/dev/null; }
_curl_post() { curl -sf -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "${2:-{}}" "$1" 2>/dev/null; }
case "${1:-help}" in
  health)
    echo "=== Karma Server ==="
    _curl_get "$KARMA_URL/health" | python3 -m json.tool 2>/dev/null || echo "UNREACHABLE"
    echo ""
    echo "=== Containers ==="
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "docker not accessible"
    echo ""
    echo "=== Memory ==="
    free -m | head -2
    echo ""
    echo "=== Disk ==="
    df -h /opt/seed-vault | tail -1
    ;;
  graph-stats)
    _curl_get "$KARMA_URL/health" | python3 -c "
import sys, json
d = json.load(sys.stdin)
g = d.get('graph', {})
print(f\"Entities: {g.get('entities','?')}  Episodes: {g.get('episodes','?')}  Relationships: {g.get('relationships','?')}\")
s = d.get('sqlite', {})
print(f\"Mem cells: {s.get('mem_cells','?')}  Observations: {s.get('observations_total','?')} ({s.get('observations_unreflected','?')} unreflected)\")
"
    ;;
  candidates)
    _curl_get "$KARMA_URL/candidates/list" | python3 -c "
import sys, json
d = json.load(sys.stdin)
cs = d.get('candidates', [])
if not cs:
    print('No pending candidates.')
else:
    for c in cs:
        flag = ' [CONFLICT]' if c.get('lane') == 'conflict' else ''
        print(f\"  {c['uuid'][:12]}  conf={c.get('confidence',0):.2f}  {c.get('name','?')}{flag}\")
    print(f\"Total: {len(cs)} pending\")
"
    ;;
  promote)
    shift
    if [ $# -eq 0 ]; then
      echo "Usage: distilled_ops.sh promote <uuid1> [uuid2] ..."
      exit 1
    fi
    UUIDS=$(printf '"%%s",' "$@" | sed 's/,$//')
    _curl_post "$KARMA_URL/promote-candidates" "{\"approved_uuids\": [$UUIDS], \"authorized_by\": \"Colby\"}" | python3 -m json.tool
    ;;
  budget)
    _curl_get "$KARMA_URL/v1/budget" | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f\"Today:  \${d.get('today_usd',0):.4f}\")
print(f\"Month:  \${d.get('month_usd',0):.4f}\")
print(f\"Cap:    \${d.get('daily_cap_usd',0):.2f}/day, \${d.get('monthly_cap_usd',0):.2f}/month\")
"
    ;;
  staleness)
    _curl_post "$KARMA_URL/v1/staleness/scan" | python3 -m json.tool
    ;;
  backup-now)
    echo "Running backup..."
    /opt/seed-vault/scripts/backup.sh 2>&1
    echo "Done."
    ;;
  logs)
    docker logs karma-server --tail="${2:-50}" 2>&1
    ;;
  *)
    echo "Distilled Operations — Zero-LLM common tasks"
    echo ""
    echo "Usage: distilled_ops.sh <operation>"
    echo ""
    echo "  health       Full system health check"
    echo "  graph-stats  Knowledge graph counts"
    echo "  candidates   List pending candidates for review"
    echo "  promote      Promote candidates (pass UUIDs)"
    echo "  budget       Current budget report"
    echo "  staleness    Run staleness scan"
    echo "  backup-now   Trigger immediate backup"
    echo "  logs [N]     Tail karma-server logs (default 50)"
    ;;
esac
