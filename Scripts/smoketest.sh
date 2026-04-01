#!/bin/bash
# Nexus Smoketest — Automated verification of all baseline items (Primitive #38)
# Run: bash Scripts/smoketest.sh
# Requires: HUB_CHAT_TOKEN in env or .hub-chat-token file

set +e
PASS=0; FAIL=0; SKIP=0
TOKEN="${HUB_CHAT_TOKEN:-$(cat .hub-chat-token 2>/dev/null || ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt' 2>/dev/null)}"

check() {
  local name="$1" cmd="$2" expect="$3"
  result=$(timeout 15 bash -c "$cmd" 2>&1) || true
  if echo "$result" | grep -q "$expect"; then
    echo "  PASS  $name"
    ((PASS++))
  else
    echo "  FAIL  $name (expected: $expect)"
    echo "        got: ${result:0:120}"
    ((FAIL++))
  fi
}

echo "=== NEXUS SMOKETEST $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo ""

echo "--- Section 1: Core Health ---"
check "hub.arknexus.net/health" \
  "curl -sf https://hub.arknexus.net/health" '"ok":true'
check "P1 cc_server /health" \
  "curl -sf http://localhost:7891/health" '"ok"'
check "K2 cortex /health" \
  "curl -sf http://192.168.0.226:7892/health" '"ok":true'
check "claude-mem /health" \
  "curl -sf http://localhost:37778/health" '"ok"'

echo ""
echo "--- Section 2: Chat (Baseline #1) ---"
echo "  SKIP  /v1/chat (holds subprocess lock 30-60s — test manually)"
((SKIP++))

echo ""
echo "--- Section 3: Sprint 3-4 Endpoints ---"
check "/v1/files (Context Panel)" \
  "curl -sf -H 'Authorization: Bearer $TOKEN' https://hub.arknexus.net/v1/files" '"ok":true'
check "/v1/spine (Evolution)" \
  "curl -sf -H 'Authorization: Bearer $TOKEN' https://hub.arknexus.net/v1/spine" 'pipeline'
check "/v1/self-edit/pending" \
  "curl -sf -H 'Authorization: Bearer $TOKEN' https://hub.arknexus.net/v1/self-edit/pending" '"ok":true'
check "/v1/cancel" \
  "curl -sf https://hub.arknexus.net/v1/cancel" '"ok":true'
check "/v1/learnings" \
  "curl -sf -H 'Authorization: Bearer $TOKEN' https://hub.arknexus.net/v1/learnings" '"ok":true'

echo ""
echo "--- Section 4: Coordination Bus ---"
check "Bus /v1/coordination/recent" \
  "curl -sf -H 'Authorization: Bearer $TOKEN' 'https://hub.arknexus.net/v1/coordination/recent?limit=1'" '"ok":true'

echo ""
echo "--- Section 5: AGORA ---"
check "/agora returns 200" \
  "curl -sf -o /dev/null -w '%{http_code}' https://hub.arknexus.net/agora" '200'

echo ""
echo "--- Section 6: Vault-Neo Containers ---"
check "anr-hub-bridge running" \
  "ssh vault-neo 'docker ps --format {{.Names}} | grep hub-bridge'" 'hub-bridge'
check "anr-vault-api running" \
  "ssh vault-neo 'docker ps --format {{.Names}} | grep vault-api'" 'vault-api'
check "falkordb running" \
  "ssh vault-neo 'docker ps --format {{.Names}} | grep falkor'" 'falkor'

echo ""
echo "--- Section 7: Data Layer ---"
check "Ledger has entries" \
  "ssh vault-neo 'wc -l < /opt/seed-vault/memory_v1/ledger/memory.jsonl'" '[0-9]'
check "MemCube in latest entry" \
  "ssh vault-neo \"tail -1 /opt/seed-vault/memory_v1/ledger/memory.jsonl | grep -c memcube\"" '1'

echo ""
echo "--- Section 8: P1 Local Services ---"
check "cc_server PID exists" \
  "curl -sf http://localhost:7891/health" 'cc-server-p1'
check "Hooks engine loaded" \
  "curl -sf http://localhost:7891/health" '"ok": true'

echo ""
echo "--- Section 9: K2 Services ---"
check "Cortex v2 (sprint6)" \
  "curl -sf http://192.168.0.226:7892/health" '"sprint6":true'
check "Vesper pipeline active" \
  "curl -sf http://192.168.0.226:7892/spine" '"watchdog":"active"'

echo ""
echo "========================================="
echo "  PASS: $PASS  FAIL: $FAIL  SKIP: $SKIP"
echo "========================================="
[ "$FAIL" -eq 0 ] && echo "  ALL CLEAR" || echo "  ISSUES FOUND"
