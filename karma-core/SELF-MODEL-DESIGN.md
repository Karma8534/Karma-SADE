# Karma Self-Model — "Karma Builds Karma"

## What This Is

The self-model is how Karma develops a persona over time. It's a JSON file
(`Memory/13-self-model.json`) where Karma records observations about its own
behavior, which are then injected into the system prompt on session start.

This creates a feedback loop:
1. Karma has a session with Colby
2. At session end, Karma reflects: what went well, what went wrong, what to try differently
3. Reflections are written to `13-self-model.json`
4. Next session, the system prompt includes these self-observations
5. Karma adjusts behavior based on accumulated self-knowledge
6. Stale observations that aren't reinforced decay and are pruned (Decision #5)

## Architecture Constraints

- **Karma is the only origin of thought** — K2 never calls the reflection function
- **No autonomous LLM calls** — the LLM call happens during the session; `reflect_on_session()` just writes the result
- **Prompt-First** — self-model is loaded into the system prompt, same as user-facts
- **No new dependencies** — pure Python, reads/writes JSON, no vector DB or embeddings

## File Layout

```
Memory/
  13-self-model.json          ← Karma's self-observations (the self-model)
karma-core/
  self_reflection.py          ← Core logic: reflect_on_session(), get_self_model_summary()
  self_model_api.py           ← API endpoints: GET /v1/self-model, POST /v1/self-model/reflect
  SELF-MODEL-DESIGN.md        ← This file
```

## Schema: 13-self-model.json

Six categories, each with an array of timestamped observations:

| Category | What It Tracks |
|---|---|
| `communication_style` | How Karma communicates — verbosity, tone, structure |
| `knowledge_gaps` | Topics where Karma was wrong or uncertain |
| `strengths` | Things Karma consistently does well |
| `correction_history` | Times Colby corrected Karma (highest-weight signal) |
| `interaction_preferences` | What works/doesn't when talking to Colby |
| `growth_trajectory` | Session-over-session evolution |

Each observation entry:
```json
{
  "observation": "I tend to over-explain when Colby asks short questions",
  "confidence": 0.8,
  "created_at": "2026-02-26T19:00:00Z",
  "last_reinforced": "2026-02-26T19:00:00Z",
  "reinforcement_count": 1,
  "session_id": "session_38",
  "evidence": "Sessions 35-37: Colby said 'too long' twice"
}
```

## Decay & Pruning (Decision #5)

- Entries older than 30 days with `reinforcement_count < 2` are pruned
- Reinforcement resets the decay clock — if Karma re-observes the same pattern, it sticks
- Max 20 entries per category — if exceeded, lowest-confidence least-reinforced entries are dropped
- Simple word-overlap similarity check prevents duplicate observations (>60% overlap = reinforce)

## How to Use (During a Session)

### Karma calls reflect_on_session():
```python
from self_reflection import reflect_on_session

result = reflect_on_session(
    observations=[
        {
            "category": "communication_style",
            "observation": "I should be more concise when Colby asks yes/no questions",
            "confidence": 0.9,
            "evidence": "Colby interrupted twice this session"
        },
        {
            "category": "strengths",
            "observation": "My architecture analysis was accurate and useful",
            "confidence": 0.85,
        }
    ],
    session_id="session_38"
)
# result: {"ok": True, "written": 2, "pruned": 0, "session_id": "session_38"}
```

### Via API (hub-bridge tool-use):
```bash
curl -X POST http://localhost:8000/v1/self-model/reflect \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_38",
    "observations": [
      {"category": "correction_history", "observation": "I assumed Chrome Extension worked — it never did", "confidence": 1.0}
    ]
  }'
```

### System prompt injection (automatic on session start):
```python
from self_reflection import get_self_model_summary

# Returns formatted text block for system prompt
summary = get_self_model_summary(max_per_category=5)
# Inject into 00-karma-system-prompt-live.md generation
```

## Resurrection Path

When Karma restarts or a new session begins:
1. Server boots → loads 13-self-model.json
2. `get_self_model_summary()` generates text block
3. System prompt generator includes self-model alongside user-facts
4. Karma starts session knowing: who Colby is (05-user-facts.json) AND who Karma is (13-self-model.json)

## What This Does NOT Do

- Does not make autonomous LLM calls
- Does not replace or compete with the FalkorDB graph
- Does not introduce new services, databases, or dependencies
- Does not change the OBSERVE-only consciousness loop
- Does not let K2 modify the self-model — only Karma during sessions
