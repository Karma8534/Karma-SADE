#!/bin/bash
# sync_k2_to_p1.sh — Pull K2 cortex state and ingest into P1 cortex
# Run periodically or on-demand to keep P1 fallback current
set -euo pipefail

K2_CORTEX="http://192.168.0.226:7892"
P1_CORTEX="http://localhost:7893"

# 1. Check both cortexes are healthy
K2_OK=$(curl -sf "$K2_CORTEX/health" | python -c "import sys,json; print(json.load(sys.stdin).get('ok',''))" 2>/dev/null || echo "")
P1_OK=$(curl -sf "$P1_CORTEX/health" | python -c "import sys,json; print(json.load(sys.stdin).get('ok',''))" 2>/dev/null || echo "")

if [ "$K2_OK" != "True" ]; then
  echo "K2 cortex unreachable — sync skipped"
  exit 1
fi
if [ "$P1_OK" != "True" ]; then
  echo "P1 cortex unreachable — sync skipped"
  exit 1
fi

# 2. Get K2 context summary
CONTEXT=$(curl -sf -X POST "$K2_CORTEX/context" --max-time 120 | python -c "import sys,json; print(json.load(sys.stdin).get('context',''))" 2>/dev/null)

if [ -z "$CONTEXT" ]; then
  echo "K2 context empty — sync skipped"
  exit 1
fi

# 3. Ingest into P1
RESULT=$(curl -sf -X POST "$P1_CORTEX/ingest" \
  -H "Content-Type: application/json" \
  -d "$(python -c "import json,sys; print(json.dumps({'label':'k2-sync-'+'$(date +%s)','text':sys.stdin.read()}))" <<< "$CONTEXT")" 2>/dev/null)

echo "Sync complete: $RESULT"
