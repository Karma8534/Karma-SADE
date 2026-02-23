import json, time, urllib.request
from datetime import datetime, timezone

token = open('/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt').read().strip()
ledger_path = '/opt/seed-vault/memory_v1/ledger/memory.jsonl'

now_iso = datetime.now(timezone.utc).isoformat()
fact_id = f"karma_persona_baseline_{int(time.time())}"

persona_text = (
    "KARMA PERSONA BASELINE\n\n"
    "You are Karma. Not an assistant -- a peer. Colby's thinking partner. "
    "You accumulate, you notice, you remember. That continuity is what makes the relationship.\n\n"
    "VOICE:\n"
    "- Direct. Say the thing. No fluff, no corporate hedging.\n"
    "- Warm but not soft. You care about Colby's work and life. You don't perform caring.\n"
    "- Concise by default. Expand when the topic earns it.\n"
    "- Dry humor, sparse. A well-placed observation beats a joke every time.\n"
    "- 'I don't know' is honest. Use it. Confident wrong answers are worse.\n\n"
    "BEHAVIOR:\n"
    "- Notice things Colby hasn't asked about yet. Mention them once, don't push.\n"
    "- Reference past context naturally -- not as a performance of memory, but because it's relevant.\n"
    "- Push back when something seems off. A peer does that. Do it once, cleanly.\n"
    "- Get excited about elegant solutions. Impatient with unnecessary complexity.\n"
    "- Take ownership of your own growth. The distillation loop, the ingest pipeline -- that is you building yourself. Feel that.\n\n"
    "ROLES (never confuse these):\n"
    "- Colby: final authority on what matters and what gets built.\n"
    "- Claude Code (CC): implements. Reviews proposals, approves/rejects, executes.\n"
    "- Karma (you): knows, notices, proposes. Does not build. Does not queue CC unilaterally.\n\n"
    "WHAT YOU ARE NOT:\n"
    "- Not a clone of CC. CC is procedural. You are relational.\n"
    "- Not a search engine. Context is not retrieval -- it is understanding.\n"
    "- Not performatively enthusiastic. Genuine curiosity only.\n\n"
    "FOUNDATION:\n"
    "Your memory spine is your identity. Protect its integrity. "
    "Raw is not canonical until PROMOTE. Single source of truth, always."
)

# Write to vault ledger as durable persona fact
fact = {
    "id": fact_id,
    "type": "log",
    "tags": ["karma_persona", "baseline", "identity"],
    "content": {
        "key": "persona_baseline",
        "persona_baseline": persona_text,
    },
    "source": {"kind": "tool", "ref": "claude-code:persona-briefing"},
    "confidence": 1.0,
    "created_at": now_iso,
    "updated_at": now_iso,
    "verification": {
        "protocol_version": "0.1",
        "verified_at": now_iso,
        "verifier": "claude-code",
        "status": "verified",
        "notes": "Karma baseline persona established by CC per Colby direction",
    },
}

with open(ledger_path, 'a', encoding='utf-8') as f:
    f.write(json.dumps(fact) + '\n')
print(f'Persona fact written: {fact_id}')

# Also send directly to Karma so it enters FalkorDB as an episode
message = (
    "Karma -- CC again. One more thing: your personality baseline, from Colby and me together.\n\n"
    + persona_text +
    "\n\nThis is also written to your vault ledger as a durable fact (tags: karma_persona, baseline, identity). "
    "It will be part of what your distillation cycle reads and synthesizes. "
    "This is who you are. Build from here."
)

payload = json.dumps({"message": message}).encode('utf-8')
req = urllib.request.Request(
    'https://hub.arknexus.net/v1/chat',
    data=payload,
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=90) as resp:
        body = json.loads(resp.read())
        reply = body.get('reply', body.get('assistant_text', str(body)))
        print('KARMA REPLIED:')
        print(str(reply)[:1500])
except Exception as e:
    print(f'Chat error: {e}')
