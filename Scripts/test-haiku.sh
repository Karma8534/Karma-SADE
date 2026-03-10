#!/bin/bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
RESP=$(curl -s https://hub.arknexus.net/v1/chat \
  -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"one word reply only: haiku_test"}')
echo "$RESP" | python3 -c "import sys,json; d=json.load(sys.stdin); print('model:', d.get('model','?')); print('response:', d.get('assistant_text','?')[:120])"
