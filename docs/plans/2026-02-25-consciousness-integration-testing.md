# Consciousness Loop Integration Testing — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Verify consciousness loop autonomously uses tool-use to query droplet state, reason about observations, make decisions, and persist insights to decision_log.jsonl without user intervention.

**Architecture:**
Consciousness loop (_observe → _think → _decide → _act → _reflect) currently runs but only responds to control signals. We will modify the _think phase to actively query FalkorDB using the graph_query tool (already deployed), analyze the results, generate a decision, and write it to decision_log.jsonl using get_vault_file tool. This validates end-to-end autonomous reasoning with tool-use integration.

**Tech Stack:** Python, FalkorDB (Cypher queries), LLM (GLM-4.7 tier), JSONL ledger files

---

## Task 1: Understand Current Consciousness Loop Structure

**Files:**
- Read: `karma-core/consciousness.py` (full file, note lines 1-50, 150-200, _think method)
- Read: `karma-core/server.py` (find ConsciousnessLoop instantiation, how it's called)
- Reference: MEMORY.md (consciousness loop design, tier-aware routing)

**Step 1: Read consciousness.py to understand class structure**

Run: `ssh vault-neo "head -80 /opt/seed-vault/karma-core/consciousness.py"`

Expected: See imports, class definition, __init__, method names

**Step 2: Locate _think() method in consciousness.py**

Run: `ssh vault-neo "grep -n 'def _think' /opt/seed-vault/karma-core/consciousness.py"`

Expected: Output shows line number where _think() is defined

**Step 3: Read the _think() method completely**

Run: `ssh vault-neo "sed -n '[START_LINE],[END_LINE]p' /opt/seed-vault/karma-core/consciousness.py"`

Expected: See full _think() implementation (router.complete call, tier="sonnet", response handling)

**Step 4: Understand how router is passed to consciousness**

Run: `ssh vault-neo "grep -n 'ConsciousnessLoop' /opt/seed-vault/karma-core/server.py | head -5"`

Expected: See instantiation line with router parameter

**Step 5: Commit understanding (no code changes)**

Document findings in memory:
```bash
cat > /tmp/consciousness_findings.txt << 'EOF'
- _think() currently calls self._router.complete() with tier="sonnet"
- Router has complete() method that returns structured response
- ConsciousnessLoop has access to router but NOT to tool-use infrastructure
- Need to add: tool_call mechanism so consciousness can execute graph_query
EOF
```

---

## Task 2: Add Tool-Use Capability to Consciousness Loop

**Files:**
- Modify: `karma-core/consciousness.py` (add _execute_tool method)
- Reference: `hub-bridge/app/server.js` (how executeToolCall works)

**Step 1: Review hub-bridge tool execution pattern**

Run: `ssh vault-neo "sed -n '800,850p' /opt/seed-vault/hub-bridge/app/server.js"`

Expected: See executeToolCall function that handles graph_query, get_vault_file

**Step 2: Write the tool-use wrapper for consciousness**

Create method in consciousness.py:

```python
async def _execute_tool(self, tool_name: str, tool_input: dict):
    """Execute a tool from consciousness reasoning context."""
    if tool_name == "graph_query":
        cypher = tool_input.get("query", "")
        if not cypher:
            return {"error": "missing_query"}

        # Call graph endpoint
        import subprocess
        result = subprocess.run(
            ["curl", "-s", "-X", "POST",
             "-H", "authorization: Bearer " + os.getenv("VAULT_BEARER", ""),
             "-H", "content-type: application/json",
             "-d", json.dumps({"query": cypher}),
             "http://karma:8340/v1/cypher"],
            capture_output=True, text=True
        )
        return json.loads(result.stdout) if result.stdout else {"error": "empty_response"}

    elif tool_name == "get_vault_file":
        alias = tool_input.get("alias", "")
        # Similar implementation
        return {"error": "not_implemented"}

    return {"error": f"unknown_tool: {tool_name}"}
```

**Step 3: Test tool execution with graph_query**

Run: `ssh vault-neo "python3 << 'PYEOF'
import sys
sys.path.insert(0, '/opt/seed-vault')
from karma_core.consciousness import ConsciousnessLoop

# Create instance
loop = ConsciousnessLoop(...)  # with credentials
result = await loop._execute_tool('graph_query', {'query': 'MATCH (n) RETURN COUNT(n) AS count'})
print(result)
PYEOF
"`

Expected: Returns `{"result": [{"count": <number>}]}` or similar

**Step 4: Commit tool integration**

```bash
git add karma-core/consciousness.py
git commit -m "feat: Add _execute_tool method for consciousness graph_query and get_vault_file"
```

---

## Task 3: Modify _think() to Query Graph and Generate Insights

**Files:**
- Modify: `karma-core/consciousness.py` (_think method, lines TBD)

**Step 1: Design minimal "observe graph" query**

Create a Cypher query that consciousness will run:

```cypher
MATCH (n)
RETURN
  COUNT(DISTINCT n) AS total_entities,
  COUNT(DISTINCT (n)-[]-()) AS entities_with_relationships,
  apoc.agg.count(DISTINCT n) AS orphaned_count
```

**Step 2: Update _think() to call graph_query tool**

Replace the simple router.complete() call with:

```python
async def _think(self):
    # Execute graph observation
    graph_result = await self._execute_tool("graph_query", {
        "query": "MATCH (n) RETURN COUNT(DISTINCT n) AS entity_count, COUNT(DISTINCT (n)-[]-()) AS connected_count"
    })

    # Format observation
    observation = f"Graph state: {graph_result.get('result', [])}"

    # Call LLM to reason about observation
    messages = [
        {"role": "user", "content": f"I observed the following droplet state: {observation}. What insight should I log to decision_log.jsonl?"}
    ]

    response = await asyncio.to_thread(
        self._router.complete,
        messages=messages,
        tier="sonnet"
    )

    return {"observation": observation, "insight": response}
```

**Step 3: Test _think() method**

Run consciousness cycle manually:

```bash
ssh vault-neo "python3 << 'PYEOF'
import asyncio
from karma_core.consciousness import ConsciousnessLoop

async def test_think():
    loop = ConsciousnessLoop(...)
    result = await loop._think()
    print(result)

asyncio.run(test_think())
PYEOF
"`

Expected: Returns dict with "observation" (graph stats) and "insight" (LLM reasoning)

**Step 4: Commit**

```bash
git add karma-core/consciousness.py
git commit -m "feat: Modify _think to query graph and generate insights via LLM"
```

---

## Task 4: Implement Decision Persistence to decision_log.jsonl

**Files:**
- Create: `karma-core/decision_logger.py` (utility for writing decisions)
- Modify: `karma-core/consciousness.py` (_decide and _act methods)

**Step 1: Create decision_logger utility**

```python
# karma-core/decision_logger.py
import json
import os
from datetime import datetime

class DecisionLogger:
    def __init__(self, ledger_path: str = "/opt/seed-vault/memory_v1/ledger/decision_log.jsonl"):
        self.ledger_path = ledger_path

    async def log_decision(self, decision: str, observation: str, reasoning: str, action: str):
        """Append decision entry to decision_log.jsonl"""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": "CONSCIOUSNESS_DECISION",
            "decision": decision,
            "observation": observation,
            "reasoning": reasoning,
            "action": action,
            "source": "consciousness_loop"
        }

        # Append to JSONL
        with open(self.ledger_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return {"ok": True, "timestamp": entry["timestamp"]}
```

**Step 2: Update consciousness._act() to use DecisionLogger**

```python
async def _act(self, decision_insight: dict):
    """Persist decision to decision_log.jsonl"""
    from karma_core.decision_logger import DecisionLogger

    logger = DecisionLogger()
    result = await logger.log_decision(
        decision=decision_insight.get("decision", ""),
        observation=decision_insight.get("observation", ""),
        reasoning=decision_insight.get("reasoning", ""),
        action=decision_insight.get("action", "")
    )
    return result
```

**Step 3: Test decision persistence**

Manually append a test decision:

```bash
ssh vault-neo "python3 << 'PYEOF'
from karma_core.decision_logger import DecisionLogger
import asyncio

async def test():
    logger = DecisionLogger()
    result = await logger.log_decision(
        decision="Test decision",
        observation="Found 47 entities",
        reasoning="Testing persistence",
        action="Verify appears in ledger"
    )
    print(result)

asyncio.run(test())
PYEOF
"`

Expected: Returns `{"ok": True, "timestamp": "..."}`, and entry appears in decision_log.jsonl

**Step 4: Verify entry in ledger**

```bash
ssh vault-neo "tail -1 /opt/seed-vault/memory_v1/ledger/decision_log.jsonl | jq ."
```

Expected: JSON object with timestamp, decision, observation fields

**Step 5: Commit**

```bash
git add karma-core/decision_logger.py karma-core/consciousness.py
git commit -m "feat: Add decision persistence to decision_log.jsonl via DecisionLogger"
```

---

## Task 5: Wire Full OBSERVE/THINK/DECIDE/ACT/REFLECT Cycle

**Files:**
- Modify: `karma-core/consciousness.py` (main cycle method, integrate all phases)

**Step 1: Review current consciousness cycle structure**

```bash
ssh vault-neo "grep -n 'async def run\|async def _observe\|async def _think\|async def _decide\|async def _act\|async def _reflect' /opt/seed-vault/karma-core/consciousness.py"
```

Expected: See all 6 methods listed

**Step 2: Update main cycle to use new _think (with tool-use)**

Ensure the run() or main cycle method flows:

```python
async def run_cycle(self):
    # OBSERVE
    observation = await self._observe()  # reads ledger/FalkorDB
    if not observation:
        return  # no new data

    # THINK (NOW WITH TOOL-USE)
    thinking = await self._think()  # queries graph, LLM reasons

    # DECIDE
    decision = await self._decide(thinking)

    # ACT (PERSIST)
    act_result = await self._act(decision)

    # REFLECT
    reflection = await self._reflect(act_result)

    return reflection
```

**Step 3: Test full cycle**

Trigger consciousness loop manually:

```bash
ssh vault-neo "docker exec karma-server python3 << 'PYEOF'
import asyncio
from karma_core.consciousness import ConsciousnessLoop
from karma_core.router import MultiModelRouter

async def test_cycle():
    router = MultiModelRouter(...)
    consciousness = ConsciousnessLoop(router=router)
    result = await consciousness.run_cycle()
    print("Cycle result:", result)

asyncio.run(test_cycle())
PYEOF
"`

Expected:
- _observe returns current FalkorDB state
- _think queries graph + LLM reasoning
- _decide generates decision
- _act persists to decision_log.jsonl
- _reflect logs to consciousness.jsonl

**Step 4: Verify persistence**

```bash
ssh vault-neo "tail -5 /opt/seed-vault/memory_v1/ledger/decision_log.jsonl"
```

Expected: Last entry is the decision from the test cycle

**Step 5: Commit**

```bash
git add karma-core/consciousness.py
git commit -m "feat: Integrate full OBSERVE/THINK/DECIDE/ACT/REFLECT cycle with tool-use"
```

---

## Task 6: Verify End-to-End Integration (User can read consciousness insights)

**Files:**
- Create: `tests/consciousness_integration_test.py` (end-to-end test)

**Step 1: Create test that verifies consciousness writes to decision_log.jsonl**

```python
# tests/consciousness_integration_test.py
import asyncio
import json
import tempfile
from karma_core.consciousness import ConsciousnessLoop
from karma_core.decision_logger import DecisionLogger

async def test_consciousness_writes_decision_log():
    """Verify consciousness loop persists decisions to ledger"""

    # Run one cycle
    loop = ConsciousnessLoop(router=test_router)
    result = await loop.run_cycle()

    # Verify decision_log.jsonl has new entry
    with open("/opt/seed-vault/memory_v1/ledger/decision_log.jsonl") as f:
        lines = f.readlines()
        last_entry = json.loads(lines[-1])

    assert last_entry.get("source") == "consciousness_loop"
    assert "observation" in last_entry
    assert "reasoning" in last_entry
    return True
```

**Step 2: Run the integration test**

```bash
cd /opt/seed-vault && python3 -m pytest tests/consciousness_integration_test.py::test_consciousness_writes_decision_log -v
```

Expected: PASS with output showing decision_log entry created

**Step 3: Verify next user interaction can READ the insight via tool-use**

```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
curl -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What did consciousness learn recently?",
    "topic": "consciousness_loop"
  }'
```

Expected: Response includes summary of recent decision_log.jsonl entries (LLM calls get_vault_file tool to read ledger)

**Step 4: Commit test**

```bash
git add tests/consciousness_integration_test.py
git commit -m "test: Add integration test for consciousness loop decision persistence"
```

---

## Task 7: Deploy and Monitor

**Files:**
- Modify: `karma-core/server.py` (ensure ConsciousnessLoop uses updated consciousness.py)

**Step 1: Rebuild karma-core Docker image**

```bash
ssh vault-neo "cd /opt/seed-vault/karma-core && docker build -t karma-core:latest . --no-cache"
```

Expected: Build completes with no errors

**Step 2: Stop old karma container and start new one**

```bash
ssh vault-neo "docker stop karma-server && docker rm karma-server && docker run -d \
  --name karma-server \
  --network anr-vault-net \
  -e VAULT_BEARER=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) \
  -v /opt/seed-vault:/opt/seed-vault \
  karma-core:latest"
```

Expected: Container starts successfully

**Step 3: Monitor consciousness loop for 2-3 cycles**

```bash
ssh vault-neo "docker logs -f karma-server | grep -i consciousness"
```

Expected: See cycle start messages, no errors for 2+ cycles

**Step 4: Verify decision_log.jsonl has recent entries**

```bash
ssh vault-neo "tail -5 /opt/seed-vault/memory_v1/ledger/decision_log.jsonl | jq ."
```

Expected: Entries with recent timestamps, source="consciousness_loop"

**Step 5: Test /v1/chat can read insights**

Run the tool-use query from Task 6, Step 3

Expected: LLM responds with insights from decision_log.jsonl

**Step 6: Commit deployment**

```bash
git add karma-core/consciousness.py karma-core/decision_logger.py
git commit -m "phase-28: Consciousness loop integration testing — autonomous tool-use and decision persistence verified"
```

**Step 7: Push to GitHub**

```bash
git push origin main
```

---

## Summary

This plan implements end-to-end consciousness loop integration with tool-use:

1. **Task 1-2:** Understand current code, add tool-use capability
2. **Task 3:** Modify _think() to query graph and reason about observations
3. **Task 4:** Implement decision persistence to decision_log.jsonl
4. **Task 5:** Wire full OBSERVE/THINK/DECIDE/ACT/REFLECT cycle
5. **Task 6:** Verify end-to-end with integration test
6. **Task 7:** Deploy and monitor in production

**Success Criteria:**
- ✅ Consciousness autonomously calls graph_query tool (not user-triggered)
- ✅ Graph results properly feed into LLM reasoning (_think phase)
- ✅ Decisions persist to decision_log.jsonl with full metadata
- ✅ User interaction can read insights via /v1/chat + tool-use
- ✅ All commits pushed to main
