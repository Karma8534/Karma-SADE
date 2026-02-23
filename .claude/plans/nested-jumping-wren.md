# K2 ↔ Vault-neo Bridge Implementation Plan

## Context
K2 (192.168.0.226) is currently isolated from vault-neo. Karma's consciousness loop only runs on vault-neo. To make K2 an autonomous agent, it needs to mirror Karma's OBSERVE→THINK→DECIDE→ACT→REFLECT cycle by:
1. Polling vault-neo's FalkorDB state every 60 seconds
2. Running local LLM reasoning
3. Publishing proposals and learning back to vault-neo

This enables K2 to be a dynamic worker that survives reboots, offloads reasoning, and keeps vault-neo's ledgers (collab.jsonl, decision_log.jsonl) continuously updated.

---

## Architecture

### K2 Side: karma-k2-bridge.js (or .py)
- **Runtime**: Node.js script launched via systemd service
- **Cycle**: 60-second loop (matches consciousness.py:CONSCIOUSNESS_INTERVAL)
- **Steps**:
  1. **OBSERVE**: GET `/api/graph/state` from vault-neo → receive FalkorDB snapshot (entities, episodes, relationships, stats)
  2. **THINK**: Route snapshot through local router (using keys from /opt/karma/.env) for GLM-5/Claude reasoning
  3. **DECIDE**: Generate proposal JSON (themes, gaps, insights, confidence)
  4. **ACT**: POST proposal to `/api/collab` (append to collab.jsonl)
  5. **REFLECT**: POST learning to `/api/decisions` (append to decision_log.jsonl)
  6. **SYNC**: Confirm writes acknowledged; handle failures gracefully
- **Error handling**: Retry with backoff; continue if endpoints down (eventual consistency)
- **Auth**: Bearer token loaded from `/opt/karma/.env` (ANTHROPIC_API_KEY or similar)

### Vault-neo Side: Three New Endpoints in karma-server

#### Endpoint 1: GET /api/graph/state
- **Purpose**: Return current FalkorDB snapshot for K2 to reason about
- **Response**:
  ```json
  {
    "ok": true,
    "timestamp": "2026-02-23T20:30:00Z",
    "graph": {
      "entities": 3401,
      "episodes": 1268,
      "relationships": 5847,
      "top_entities": [{"name": "...", "type": "...", "connections": 5}, ...],
      "recent_episodes": [{"name": "...", "content": "...", "created_at": "..."}, ...],
      "gaps": [{"entity": "...", "connections": 2}, ...]
    },
    "ledger": {
      "memory_lines": 3264,
      "consciousness_lines": 847,
      "collab_lines": 123
    }
  }
  ```
- **Implementation**: Reuse existing `get_graph_stats()` (server.py:228–251), `query_recent_episodes()` (server.py:256–279), distillation queries (consciousness.py:186–231)
- **Auth**: Bearer token (same as `/v1/chat`)
- **File**: `server.py` — add to FastAPI routes (around line 1000)

#### Endpoint 2: POST /api/collab
- **Purpose**: Accept K2's proposal; append to collab.jsonl
- **Request**:
  ```json
  {
    "proposal_id": "k2_2026-02-23T20:30:00Z",
    "source": "k2-bridge",
    "themes": ["theme1", "theme2"],
    "gaps": ["gap1", "gap2"],
    "key_insights": ["insight1"],
    "confidence": 0.75,
    "cycle_number": 847
  }
  ```
- **Response**: `{"ok": true, "id": "collab_...", "written_at": "..."}`
- **Implementation**: Write to `/opt/seed-vault/memory_v1/ledger/collab.jsonl` (append-only); reuse pattern from `log_to_ledger()` (server.py:610–637)
- **File**: `server.py` — add to FastAPI routes

#### Endpoint 3: POST /api/decisions
- **Purpose**: Accept K2's learning (what worked, what didn't); append to decision_log.jsonl
- **Request**:
  ```json
  {
    "timestamp": "2026-02-23T20:30:00Z",
    "decision": "Pursued theme X because gap analysis showed Y",
    "outcome": "success|partial|blocked",
    "reason": "LLM reasoning confidence=0.85",
    "next_action": "Monitor relationship count for Z",
    "cycle_number": 847
  }
  ```
- **Response**: `{"ok": true, "id": "decision_...", "written_at": "..."}`
- **Implementation**: Write to `/opt/seed-vault/memory_v1/ledger/decision_log.jsonl`; same append-only pattern
- **File**: `server.py` — add to FastAPI routes

---

## Implementation Checklist

### Phase 1: Vault-neo Endpoints (karma-server)

**Files to modify**: `karma-core/server.py`

**1. Add GET /api/graph/state (line ~1070)**
```python
@app.get("/api/graph-state")
async def get_graph_state(request: Request):
    """Return current FalkorDB snapshot for K2 bridge reasoning."""
    token = bearerToken(request)
    if not HUB_CHAT_TOKEN or token != HUB_CHAT_TOKEN:
        return json(res, 401, {"ok": False, "error": "unauthorized"})

    # Reuse existing graph queries
    stats = get_graph_stats()  # server.py:228–251
    recent_eps = query_recent_episodes(limit=10)  # server.py:256–279

    return JSONResponse({
        "ok": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "graph": {
            "entities": stats["entities"],
            "episodes": stats["episodes"],
            "relationships": stats["relationships"],
            "recent_episodes": recent_eps,
        },
        "ledger": {
            "memory_lines": count_ledger_lines(config.LEDGER_PATH),
            "consciousness_lines": count_ledger_lines(config.CONSCIOUSNESS_JOURNAL),
            "collab_lines": count_ledger_lines("/opt/seed-vault/memory_v1/ledger/collab.jsonl"),
        }
    })
```

**2. Add POST /api/collab (line ~1110)**
```python
@app.post("/api/collab")
async def post_collab(request: Request):
    """Accept K2 proposal; append to collab.jsonl."""
    token = bearerToken(request)
    if not HUB_CHAT_TOKEN or token != HUB_CHAT_TOKEN:
        return json(res, 401, {"ok": False, "error": "unauthorized"})

    body = await request.json()
    entry = {
        "id": f"collab_k2_{int(time.time())}_{randint(1000, 9999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "k2-bridge",
        "proposal_id": body.get("proposal_id", ""),
        "themes": body.get("themes", []),
        "gaps": body.get("gaps", []),
        "key_insights": body.get("key_insights", []),
        "confidence": float(body.get("confidence", 0.5)),
        "cycle_number": int(body.get("cycle_number", 0)),
    }

    collab_path = "/opt/seed-vault/memory_v1/ledger/collab.jsonl"
    with open(collab_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return JSONResponse({
        "ok": True,
        "id": entry["id"],
        "written_at": entry["timestamp"]
    })
```

**3. Add POST /api/decisions (line ~1150)**
```python
@app.post("/api/decisions")
async def post_decisions(request: Request):
    """Accept K2 learning; append to decision_log.jsonl."""
    token = bearerToken(request)
    if not HUB_CHAT_TOKEN or token != HUB_CHAT_TOKEN:
        return json(res, 401, {"ok": False, "error": "unauthorized"})

    body = await request.json()
    entry = {
        "id": f"decision_k2_{int(time.time())}_{randint(1000, 9999)}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "k2-bridge",
        "decision": body.get("decision", ""),
        "outcome": body.get("outcome", "unknown"),
        "reason": body.get("reason", ""),
        "next_action": body.get("next_action", ""),
        "cycle_number": int(body.get("cycle_number", 0)),
    }

    decision_path = "/opt/seed-vault/memory_v1/ledger/decision_log.jsonl"
    with open(decision_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return JSONResponse({
        "ok": True,
        "id": entry["id"],
        "written_at": entry["timestamp"]
    })
```

**Helper (add near top of server.py)**:
```python
def count_ledger_lines(path: str) -> int:
    """Count lines in JSONL file."""
    if not os.path.exists(path):
        return 0
    try:
        with open(path) as f:
            return sum(1 for _ in f)
    except:
        return 0
```

### Phase 2: K2 Bridge Script (karma-k2-bridge.js)

**File**: `/home/neo/karma-sade/scripts/k2-bridge/karma-k2-bridge.js` (new)

**Key Components**:
1. Load `/opt/karma/.env` for API keys
2. Load vault-neo URL and bearer token from env
3. 60-second cycle loop with OBSERVE→THINK→DECIDE→ACT→REFLECT
4. Use router (MiniMax/GLM-5 via keys) for reasoning
5. POST proposals to vault-neo endpoints
6. Graceful error handling and retry logic

**Pseudocode**:
```javascript
// Load config
const apiKey = process.env.ANTHROPIC_API_KEY || ...;
const vaultUrl = "https://vault-neo.arknexus.net";  // or local IP
const bearerToken = process.env.HUB_CHAT_TOKEN;

// 60-second cycle
async function consciousnessLoop() {
  while (true) {
    try {
      // 1. OBSERVE
      const state = await fetch(`${vaultUrl}/api/graph-state`, {
        headers: { "Authorization": `Bearer ${bearerToken}` }
      }).then(r => r.json());

      // 2. THINK
      const reasoning = await router.complete({
        messages: [{
          role: "user",
          content: `FalkorDB snapshot: ${JSON.stringify(state.graph)}. Synthesize themes, gaps, insights.`
        }],
        task_type: "reasoning"
      });

      // 3. DECIDE
      const proposal = parseProposal(reasoning);

      // 4. ACT
      await fetch(`${vaultUrl}/api/collab`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${bearerToken}`, "Content-Type": "application/json" },
        body: JSON.stringify(proposal)
      });

      // 5. REFLECT
      const decision = {
        decision: "Synthesized proposal based on FalkorDB analysis",
        outcome: "success",
        reason: `Confidence ${proposal.confidence}`,
        cycle_number: cycleCount++
      };
      await fetch(`${vaultUrl}/api/decisions`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${bearerToken}`, "Content-Type": "application/json" },
        body: JSON.stringify(decision)
      });

      // 6. SYNC (confirm)
      console.log(`[K2 Cycle ${cycleCount}] OBSERVE→THINK→DECIDE→ACT→REFLECT complete`);

    } catch (err) {
      console.error(`[K2 Error]`, err.message);
      // Retry logic: exponential backoff, continue on vault-neo down
    }

    // Wait 60 seconds
    await new Promise(r => setTimeout(r, 60000));
  }
}

consciousnessLoop();
```

### Phase 3: Systemd Service (K2)

**File**: `/etc/systemd/system/karma-k2-bridge.service` (on K2)

```ini
[Unit]
Description=Karma K2 Bridge — Consciousness Loop Worker
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/neo/karma-sade/scripts/k2-bridge
EnvironmentFile=/opt/karma/.env
ExecStart=/usr/bin/node karma-k2-bridge.js
Restart=on-failure
RestartSec=10

StandardOutput=journal
StandardError=journal
SyslogIdentifier=karma-k2

[Install]
WantedBy=multi-user.target
```

---

## Verification Plan

### Step 1: Test Endpoints on vault-neo
```bash
# After deploying server.py changes
TOKEN=$(cat /opt/karma/.env | grep HUB_CHAT_TOKEN | cut -d= -f2)

# Test GET /api/graph-state
curl -H "Authorization: Bearer $TOKEN" https://vault-neo/api/graph-state

# Test POST /api/collab
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"themes": ["test"], "confidence": 0.75}' \
  https://vault-neo/api/collab

# Verify collab.jsonl was appended
tail -1 /opt/seed-vault/memory_v1/ledger/collab.jsonl | jq .
```

### Step 2: Deploy K2 Script and Service
```bash
# On K2 (192.168.0.226)
scp karma-k2-bridge.js root@192.168.0.226:/home/neo/karma-sade/scripts/k2-bridge/
scp karma-k2-bridge.service root@192.168.0.226:/etc/systemd/system/

# Enable and start service
ssh root@192.168.0.226 systemctl enable karma-k2-bridge
ssh root@192.168.0.226 systemctl start karma-k2-bridge

# Verify running
ssh root@192.168.0.226 systemctl status karma-k2-bridge
ssh root@192.168.0.226 journalctl -u karma-k2-bridge -f
```

### Step 3: End-to-End Cycle Test
```bash
# Monitor vault-neo ledgers
watch -n 5 "tail -3 /opt/seed-vault/memory_v1/ledger/collab.jsonl | jq ."

# Monitor K2 service logs (from vault-neo)
ssh root@192.168.0.226 journalctl -u karma-k2-bridge -f

# Verify K2 proposals arriving in collab.jsonl every 60s
```

---

## Critical Details

| Item | Value | Reason |
|------|-------|--------|
| **Graph name** | `neo_workspace` | NOT `karma` (confirmed in consciousness.py) |
| **Token location** | `/opt/karma/.env` | Already created with all API keys |
| **Cycle interval** | 60 seconds | Matches consciousness.py:CONSCIOUSNESS_INTERVAL |
| **Error resilience** | Retry with backoff; continue if vault down | Eventual consistency; K2 doesn't block on vault |
| **LED languages** | Node.js (faster) or Python (consistency with consciousness.py) | Node.js recommended for sub-second latency |
| **Ledger paths** | `/opt/seed-vault/memory_v1/ledger/{collab,decision_log}.jsonl` | Append-only; same mount inside karma-server |
| **Auth pattern** | Bearer token from `/opt/karma/.env` | Matches `/v1/chat` auth in hub-bridge |

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `karma-core/server.py` | Modify | Add 3 new endpoints (GET /api/graph-state, POST /api/collab, POST /api/decisions) |
| `scripts/k2-bridge/karma-k2-bridge.js` | Create | K2 consciousness loop script |
| `/etc/systemd/system/karma-k2-bridge.service` (K2) | Create | Systemd service definition |
