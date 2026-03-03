#!/usr/bin/env bash
# Step 4.7: Reflection Directives (P15)
# Weekly cron: the ONLY periodic LLM call (~$0.02/week via gpt-4o-mini).
# Cron: 0 6 * * 1 (every Monday at 6am UTC)
set -euo pipefail
MEMORY_DB="${MEMORY_DB_PATH:-/opt/seed-vault/memory_v1/memory.db}"
KARMA_URL="http://localhost:8340"
LOG_FILE="/opt/seed-vault/memory_v1/ledger/reflection_directives.jsonl"

UNREFLECTED=$(sqlite3 "$MEMORY_DB" "SELECT COUNT(*) FROM observations WHERE reflected=0" 2>/dev/null || echo "0")
if [ "$UNREFLECTED" -lt 5 ]; then
    echo "[REFLECT] Only $UNREFLECTED unreflected observations — skipping"
    exit 0
fi
echo "[REFLECT] Processing $UNREFLECTED unreflected observations..."

OBS_TEXT=$(sqlite3 -separator '|' "$MEMORY_DB" "SELECT event_type, description, outcome FROM observations WHERE reflected=0 ORDER BY observed_at DESC LIMIT 100" 2>/dev/null)
if [ -z "$OBS_TEXT" ]; then
    echo "[REFLECT] No observations extracted"
    exit 0
fi

RESPONSE=$(curl -sf "$KARMA_URL/ask?q=$(python3 -c "
import urllib.parse
prompt = 'Analyze these system observations and generate 3-5 reflection directives as JSON. Output ONLY JSON: {\"directives\": [{\"text\": \"...\", \"category\": \"...\"}]}. Categories: learning, risk, preference, technical, decision. Observations: $OBS_TEXT'
print(urllib.parse.quote(prompt[:2000]))
")" 2>/dev/null)

if [ -z "$RESPONSE" ]; then
    echo "[REFLECT] LLM call failed"
    exit 1
fi

echo "$RESPONSE" | python3 -c "
import sys, json, time
try:
    data = json.load(sys.stdin)
    answer = data.get('answer', '')
    start = answer.find('{')
    end = answer.rfind('}') + 1
    if start >= 0 and end > start:
        parsed = json.loads(answer[start:end])
        directives = parsed.get('directives', [])
    else:
        directives = []
    if not directives:
        print('[REFLECT] No directives extracted')
        sys.exit(0)
    log_entry = {'timestamp': time.time(), 'iso': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'directives': directives, 'observations_processed': $UNREFLECTED, 'model': data.get('model', 'unknown')}
    with open('$LOG_FILE', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    for d in directives:
        print(f\"  [{d.get('category','?')}] {d.get('text','')}\")
    print(f'[REFLECT] {len(directives)} directives generated')
except Exception as e:
    print(f'[REFLECT] Parse error: {e}')
    sys.exit(1)
"

sqlite3 "$MEMORY_DB" "UPDATE observations SET reflected=1 WHERE reflected=0" 2>/dev/null
echo "[REFLECT] Observations marked as reflected"

python3 -c "
import json, urllib.request
log_path = '$LOG_FILE'
karma_url = '$KARMA_URL'
with open(log_path) as f:
    lines = [l.strip() for l in f if l.strip()]
if not lines:
    exit(0)
last = json.loads(lines[-1])
for d in last.get('directives', []):
    payload = json.dumps({'content': f\"[DIRECTIVE] {d['text']}\", 'category': d.get('category', 'learning'), 'source': 'weekly_reflection', 'confidence': 0.8, 'pinned': True}).encode()
    req = urllib.request.Request(f'{karma_url}/v1/admit', data=payload, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())
        print(f\"  Admitted: {d['text'][:60]}... -> {result.get('action','?')}\")
    except Exception as e:
        print(f\"  Failed: {e}\")
" 2>/dev/null

echo "[REFLECT] Weekly reflection complete."
