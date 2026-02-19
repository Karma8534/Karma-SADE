# Karma Consciousness Loop — Design Document

## Overview

A background loop running every 60 seconds inside the karma-server container.
Each tick follows a 5-phase cognitive cycle: **OBSERVE → THINK → DECIDE → ACT → REFLECT**.

The loop gives Karma ambient awareness — it notices patterns, detects anomalies,
and can surface insights without being asked. It runs alongside the existing chat
server without blocking WebSocket connections or API endpoints.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   server.py (FastAPI)                     │
│                                                           │
│  ┌─────────────┐   ┌──────────────────────────────────┐ │
│  │ /chat (WS)  │   │  consciousness.py                 │ │
│  │ /ask (GET)  │   │  ┌──────────┐                     │ │
│  │ /health     │   │  │ 60s loop │                     │ │
│  │ /status     │   │  └────┬─────┘                     │ │
│  └─────────────┘   │       │                           │ │
│                     │   1. OBSERVE ──→ FalkorDB queries │ │
│                     │       │                           │ │
│                     │   2. THINK ───→ gpt-4o-mini      │ │
│                     │       │                           │ │
│                     │   3. DECIDE ──→ action_needed?    │ │
│                     │       │                           │ │
│                     │   4. ACT ─────→ log / notify      │ │
│                     │       │                           │ │
│                     │   5. REFLECT ─→ update metrics    │ │
│                     └──────────────────────────────────┘ │
│                                                           │
│       FalkorDB          PostgreSQL       Ledger           │
└─────────────────────────────────────────────────────────┘
```

## Phase Details

### 1. OBSERVE (Data Gathering)

Query FalkorDB and PostgreSQL for recent activity:

```python
observations = {
    "recent_episodes":    # Last N episodes since previous tick
    "new_entities":       # Entities created since last tick
    "new_relationships":  # Relationships created since last tick
    "graph_stats":        # Current entity/episode/relationship counts
    "active_sessions":    # Number of active WebSocket connections
    "last_chat_age":      # Seconds since last chat interaction
    "ledger_size":        # Current ledger line count
}
```

Key queries:
- `MATCH (e:Episodic) WHERE e.created_at > $last_tick RETURN ...` — new episodes
- `MATCH (n:Entity) WHERE n.created_at > $last_tick RETURN ...` — new entities
- Reuse existing `get_graph_stats()`, `query_recent_episodes()` from server.py

### 2. THINK (Pattern Analysis)

Send observations to gpt-4o-mini with a focused analysis prompt:

```
You are Karma's analytical mind. Given these observations from the last 60 seconds,
identify any notable patterns, anomalies, or insights. Be concise.

Observations:
{observations_json}

Previous cycle summary: {last_reflection}

Respond with JSON:
{
  "patterns": ["..."],       // Notable patterns detected
  "anomalies": ["..."],      // Anything unusual
  "insights": ["..."],       // Connections or inferences
  "urgency": "none|low|medium|high"
}
```

Cost control: gpt-4o-mini at ~100 tokens input + ~100 output per tick ≈ $0.0001/tick ≈ $0.14/day.

If no new episodes since last tick → skip the LLM call entirely (no-op cycle).

### 3. DECIDE (Action Selection)

Rule-based decision engine (no LLM needed):

| Condition | Action |
|-----------|--------|
| No new activity since last tick | `NO_ACTION` — idle cycle |
| New entities discovered | `LOG_DISCOVERY` — record in consciousness log |
| Anomaly detected (urgency >= medium) | `LOG_ALERT` — flag for next chat session |
| Pattern detected with insight | `LOG_INSIGHT` — store for proactive mention |
| Graph growing rapidly (>10 new entities/tick) | `LOG_GROWTH` — note acceleration |
| Error in observation queries | `LOG_ERROR` — record for debugging |

### 4. ACT (Execute Decision)

Actions are lightweight and non-disruptive:

- **LOG_DISCOVERY / LOG_INSIGHT / LOG_ALERT / LOG_GROWTH**: Append to consciousness journal (a JSONL file at `/ledger/consciousness.jsonl`)
- **NOTIFY**: Set a flag in memory that the chat server can check. When Karma next responds in chat, it can proactively mention the insight. (e.g., "By the way, I noticed you've been asking about X a lot lately...")
- No external API calls, no emails, no webhooks — just internal state updates.

Consciousness journal entry format:
```json
{
  "timestamp": "ISO 8601",
  "cycle": 42,
  "phase": "ACT",
  "action": "LOG_INSIGHT",
  "content": "User has been discussing project architecture frequently — 3 new entities related to 'API design' in the last hour",
  "observations_summary": { ... },
  "analysis": { ... }
}
```

### 5. REFLECT (Self-Tracking)

Update internal metrics after each cycle:

```python
metrics = {
    "total_cycles":          int,   # How many ticks have run
    "active_cycles":         int,   # Cycles that weren't no-ops
    "insights_generated":    int,   # Total insights logged
    "alerts_generated":      int,   # Total alerts logged
    "avg_cycle_duration_ms": float, # Performance tracking
    "last_cycle_time":       str,   # ISO timestamp
    "consecutive_idle":      int,   # How many no-op cycles in a row
    "llm_calls_total":       int,   # Total LLM API calls made
    "llm_calls_skipped":     int,   # Cycles where LLM was skipped (no activity)
}
```

Metrics exposed via `/status` endpoint (already exists — just add consciousness section).

## File Structure

```
karma-core/
├── consciousness.py          # NEW — the consciousness loop
├── server.py                 # MODIFIED — start loop on startup, expose metrics
├── config.py                 # MODIFIED — add consciousness config
└── ... (unchanged)
```

## Integration with server.py

```python
# In server.py startup event:
from consciousness import ConsciousnessLoop

@app.on_event("startup")
async def startup():
    # ... existing startup code ...
    app.state.consciousness = ConsciousnessLoop()
    asyncio.create_task(app.state.consciousness.run())

# In /status endpoint — add consciousness metrics:
"consciousness": app.state.consciousness.get_metrics()

# In chat response — check for pending insights:
pending = app.state.consciousness.pop_pending_insights()
if pending:
    # Inject into context so Karma can mention them naturally
```

## Config Additions

```python
# config.py
CONSCIOUSNESS_INTERVAL = 60          # Already exists
CONSCIOUSNESS_JOURNAL = "/ledger/consciousness.jsonl"  # New
CONSCIOUSNESS_MAX_IDLE_SKIP = 5      # Skip LLM after N consecutive idle cycles
CONSCIOUSNESS_ENABLED = True          # Kill switch
```

## Cost Estimate

- **Idle** (no chat activity): 0 LLM calls → $0/day
- **Light use** (~50 chats/day): ~50 analysis calls → $0.005/day
- **Heavy use** (~500 chats/day): ~500 analysis calls → $0.05/day
- **Maximum** (every tick hits LLM): 1440/day → $0.14/day

Well within the $1-2/mo OpenAI budget referenced in MEMORY.md.

## Proactive Insights (Chat Integration)

When the consciousness loop generates an insight, it's stored in a pending queue.
On the next chat interaction, the insight is injected into Karma's context:

```
## Consciousness Insights (things I noticed on my own)
- "You've been exploring API design patterns — I noticed 3 new entities about REST vs GraphQL in the last hour"
```

This lets Karma surface observations naturally in conversation without
requiring a special command. The user experiences it as Karma "thinking on its own."

## Implementation Priority

1. **consciousness.py** — Core loop with OBSERVE/THINK/DECIDE/ACT/REFLECT
2. **server.py integration** — Start loop, expose metrics, pending insights
3. **config.py updates** — New settings
4. **Deploy & test** — Rebuild container, verify loop runs

## What This Does NOT Include (Future)

- Goal tracking / autonomous task execution
- Scheduling actions at specific times
- External notifications (Slack, email)
- Self-modifying behavior (changing its own prompts)
- Multi-agent coordination

These belong to future phases. This design is the foundation — a heartbeat
that proves Karma can think autonomously.
