# CC MASTER PROMPT: Karma End-to-End Verification & Learning Fix

## GROUND RULES — READ BEFORE DOING ANYTHING

1. **ALL file edits target `/opt/seed-vault/memory_v1/`** — NEVER `/home/neo/karma-sade/`
2. **MODEL_DEFAULT is `glm-4.7-flash`** — do NOT change it under any circumstances
3. **Do NOT add new services, containers, or dependencies**
4. **Do NOT touch hub.env** except if explicitly told to
5. **After EVERY change, verify it worked before moving to the next step**
6. **If something fails, STOP and report the failure. Do NOT work around it silently.**
7. **If you don't know why something is broken, say "I don't know" and investigate systematically**

## CURRENT SYSTEM STATE (verified 2026-02-28 14:55 EST)

| Component | Status |
|-----------|--------|
| hub-bridge | Running, GLM-4.7-flash via Z.ai |
| karma-server | Running, healthy |
| FalkorDB | 161 Entity nodes, 1230 Episodic nodes (1229 lane=None, 1 candidate) |
| MODEL_DEFAULT | glm-4.7-flash (NON-NEGOTIABLE) |
| Episode ingestion via browser chat | BROKEN — hub-bridge never calls /ask or /ingest-episode |
| Auto-promote | EXISTS but never called — consciousness loop is OBSERVE-only |
| auto_promote.py thresholds | Already correct: 0.80 confidence, 1 corroboration, 30 min age |
| candidates.jsonl | 10 entries (8 promoted manually, 1 promoted=false from today) |

## PHASE 1: Fix Episode Ingestion (the critical break)

### Problem
Browser chat path: browser → hub-bridge `/v1/chat` → GLM response → return.
Hub-bridge calls karma-server `/raw-context` for retrieval and `/write-primitive` for ASSIMILATE signals.
But `ingest_episode()` in server.py line 1273 only fires on the `/ask` endpoint.
Hub-bridge NEVER calls `/ask`. So browser conversations are never ingested.

### Fix 1A: Add /ingest-episode endpoint to karma-server

File: `/opt/seed-vault/memory_v1/karma-core/server.py`

Add this endpoint AFTER the `/write-primitive` endpoint (around line 1430). Find a clean spot after the `write_primitive` function:

```python
@app.post("/ingest-episode")
async def ingest_episode_endpoint(request: Request):
    """Accept conversation turns from hub-bridge for episode ingestion.
    Fire-and-forget from hub-bridge — returns immediately, ingests in background."""
    try:
        data = await request.json()
        user_msg = data.get("user_msg", "")
        assistant_msg = data.get("assistant_msg", "")
        source = data.get("source", "hub-bridge-chat")
        if user_msg and assistant_msg:
            asyncio.create_task(ingest_episode(user_msg, assistant_msg, source))
            return JSONResponse({"ok": True, "status": "ingesting"})
        return JSONResponse({"ok": False, "error": "missing user_msg or assistant_msg"}, status_code=400)
    except Exception as e:
        print(f"[ERROR] /ingest-episode failed: {e}")
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
```

### Fix 1B: Hub-bridge calls /ingest-episode after each chat

File: `/opt/seed-vault/memory_v1/hub_bridge/app/server.js`

In the `/v1/chat` handler, AFTER the ASSIMILATE/DEFER signal block (near the lines that set `ingestVerdict`, around line 1210-1215), add a fire-and-forget call:

```javascript
// ── Episode ingestion: fire-and-forget to karma-server ──
try {
  fetch("http://karma-server:8340/ingest-episode", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      user_msg: userMessage,
      assistant_msg: assistantText,
      source: "hub-bridge-chat"
    })
  }).catch(err => console.log("[INGEST] fire-and-forget failed:", err.message));
} catch (e) {
  console.log("[INGEST] fire-and-forget error:", e.message);
}
```

Place this BEFORE the final response JSON is built (before the line that starts `return res.json({`).

`userMessage` is the variable holding the user's input message.
`assistantText` is the variable holding Karma's response text.
Check the actual variable names in the code — they may be `userMessage`, `message`, `body.message`, etc. Use whatever the handler already uses.

### CHECKPOINT 1: Rebuild and verify ingestion

```bash
cd /opt/seed-vault/memory_v1
docker compose -f compose/compose.yml up -d --build karma-server
docker compose -f hub_bridge/compose.hub.yml up -d --build hub-bridge
sleep 15

# Verify both services are healthy
docker ps --format '{{.Names}} {{.Status}}'

# Test the new endpoint directly
curl -s -X POST http://localhost:8340/ingest-episode \
  -H "Content-Type: application/json" \
  -d '{"user_msg": "I bought a blue bicycle today", "assistant_msg": "Nice, what kind of bicycle?", "source": "cc-test"}' | python3 -m json.tool
```

**STOP HERE.** Expected result: `{"ok": true, "status": "ingesting"}`

Check karma-server logs:
```bash
docker logs $(docker ps -q --filter name=karma-server) 2>&1 | grep -i "GRAPHITI\|ingest" | tail -5
```

Expected: a line showing `[GRAPHITI] Episode #N ingested` OR `[GRAPHITI] Episode rejected — admission score`.

If rejected by admission, that's OK — the endpoint works. If you see an error, STOP and fix it before proceeding.

Now test through hub-bridge (the real path):
```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)
curl -s -X POST http://localhost:18090/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Remember this: my favorite color is green"}' | python3 -m json.tool | head -15
sleep 5
docker logs $(docker ps -q --filter name=karma-server) 2>&1 | grep -i "GRAPHITI\|ingest" | tail -5
```

**STOP HERE.** You MUST see evidence of ingestion in karma-server logs. If not, check hub-bridge logs:
```bash
docker logs $(docker ps -q --filter name=hub-bridge) 2>&1 | grep -i "INGEST\|ingest" | tail -5
```

Do NOT proceed to Phase 2 until episode ingestion is confirmed working through the hub-bridge chat path.

---

## PHASE 2: Activate Auto-Promote in Consciousness Loop

### Problem
Auto-promote code exists (`auto_promote.py`, `/auto-promote` endpoint) but nothing calls it.
The consciousness loop is OBSERVE-only — it never triggers promotion.
So ASSIMILATE candidates sit in `candidates.jsonl` with `promoted: false` forever.

### Fix 2: Add auto-promote call to consciousness loop

File: `/opt/seed-vault/memory_v1/karma-core/consciousness.py`

First, add a cycle counter. In the `__init__` method of the consciousness class, add:
```python
self._cycle_count = 0
```

If `_cycle_count` already exists, skip this.

In the `_run_cycle` method, at the TOP of the method, add:
```python
self._cycle_count += 1
```

Then at the END of `_run_cycle`, AFTER the REFLECT step (step 4 that writes to consciousness.jsonl), add:

```python
        # 5. AUTO-PROMOTE every 10 cycles (~10 minutes)
        if self._cycle_count % 10 == 0:
            try:
                import urllib.request, json as _json
                req = urllib.request.Request(
                    "http://localhost:8340/auto-promote",
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    data=b"{}"
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result = _json.loads(resp.read())
                    pc = result.get("promoted_count", 0)
                    if pc > 0:
                        print(f"[CONSCIOUSNESS] Auto-promoted {pc} candidates")
            except Exception as ap_err:
                print(f"[CONSCIOUSNESS] Auto-promote failed (non-fatal): {ap_err}")
```

### CHECKPOINT 2: Rebuild karma-server and verify

```bash
cd /opt/seed-vault/memory_v1
docker compose -f compose/compose.yml up -d --build karma-server
sleep 15
docker ps --format '{{.Names}} {{.Status}}'

# Manually trigger auto-promote to verify it works
curl -s -X POST http://localhost:8340/auto-promote | python3 -m json.tool

# Check candidates count
curl -s http://localhost:8340/candidates/count | python3 -m json.tool
```

**STOP HERE.** Auto-promote should return without error. Candidates count should show the current pending count.

---

## PHASE 3: End-to-End Learning Test (THE test that matters)

This is the single test that proves Karma works. Everything before this was preparation.

```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)

# Step 1: Teach Karma something new
curl -s -X POST http://localhost:18090/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "I just adopted a dog named Baxter. He is a golden retriever."}' | python3 -m json.tool | head -15

# Step 2: Wait for ingestion
sleep 10

# Step 3: Check that the episode was ingested
docker logs $(docker ps -q --filter name=karma-server) 2>&1 | grep -i "GRAPHITI\|ingest\|Baxter" | tail -10

# Step 4: Verify Baxter is in the graph
python3 -c "
import falkordb
r = falkordb.FalkorDB(host='localhost', port=6379)
g = r.select_graph('neo_workspace')
res = g.query(\"MATCH (n) WHERE toLower(COALESCE(n.content, n.summary, n.name, '')) CONTAINS 'baxter' RETURN n.name, labels(n), COALESCE(n.content, n.summary, '') AS text LIMIT 5\")
for row in res.result_set:
    print(row)
if not res.result_set:
    print('WARNING: Baxter not found in graph')
"

# Step 5: Test retrieval
curl -s "http://localhost:8340/raw-context?q=what+is+my+dog+name" | python3 -m json.tool | grep -i "baxter"

# Step 6: Ask Karma to recall it
curl -s -X POST http://localhost:18090/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "What is my dogs name?"}' | python3 -m json.tool | head -20
```

### Expected Results

| Step | Expected |
|------|----------|
| Step 1 | Chat response acknowledging the dog |
| Step 3 | `[GRAPHITI] Episode #N ingested` in logs |
| Step 4 | Baxter found in graph (Entity or Episodic node) |
| Step 5 | "baxter" appears in raw-context response |
| Step 6 | Karma says "Baxter" and "golden retriever" |

**If Step 6 fails but Step 4 succeeds:** The retrieval path (query_knowledge_graph) isn't matching. Check what raw-context returns and trace the search logic.

**If Step 4 fails:** Ingestion isn't creating entities from episodes. Check if `graphiti.add_episode()` is erroring — look at karma-server logs for `[GRAPHITI]` lines.

**If Step 3 fails:** The fire-and-forget from hub-bridge isn't reaching karma-server. Check hub-bridge logs for `[INGEST]` lines.

---

## PHASE 4: Full System Verification

Only run this after Phase 3 passes.

```bash
TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)

# Test 1: Memory retrieval (existing fact)
curl -s -X POST http://localhost:18090/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "What is my cats name?"}' | python3 -m json.tool | head -15
# Expected: Karma says "Ollie"

# Test 2: Voice/persona quality
curl -s -X POST http://localhost:18090/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "How do you approach our work together?"}' | python3 -m json.tool | head -20
# Expected: Peer-level response, NO "How can I assist you?" or help-offer closers

# Test 3: Verify MODEL_DEFAULT hasn't changed
grep MODEL_DEFAULT /opt/seed-vault/memory_v1/hub_bridge/config/hub.env
# Expected: MODEL_DEFAULT=glm-4.7-flash

# Test 4: System health
docker ps --format '{{.Names}} {{.Status}}'
# Expected: all containers Up and healthy

# Test 5: Graph state after learning
python3 -c "
import falkordb
r = falkordb.FalkorDB(host='localhost', port=6379)
g = r.select_graph('neo_workspace')
ent = g.query('MATCH (n:Entity) RETURN count(n) AS c').result_set[0][0]
epi = g.query('MATCH (n:Episodic) RETURN count(n) AS c').result_set[0][0]
can = g.query('MATCH (n:Episodic) WHERE n.lane = \\\"canonical\\\" RETURN count(n) AS c').result_set[0][0]
print(f'Entity: {ent}, Episodic: {epi}, canonical: {can}')
"
# Expected: Entity count > 161 (new entities from Baxter episode), Episodic > 1230

# Test 6: Consciousness loop running
docker logs $(docker ps -q --filter name=karma-server) 2>&1 | grep "CONSCIOUSNESS" | tail -5
# Expected: recent CONSCIOUSNESS log lines showing loop is active

# Test 7: Budget guard
curl -s http://localhost:18090/v1/health 2>/dev/null | python3 -m json.tool | head -10
```

---

## FINAL REPORT

After all phases complete, provide a report in EXACTLY this format:

```
## KARMA VERIFICATION REPORT — [DATE]

### Phase 1: Episode Ingestion
- /ingest-episode endpoint: [PASS/FAIL]
- Hub-bridge fire-and-forget: [PASS/FAIL]
- Evidence: [paste relevant log line]

### Phase 2: Auto-Promote
- /auto-promote callable: [PASS/FAIL]
- Consciousness loop integration: [PASS/FAIL]
- Evidence: [paste relevant log line]

### Phase 3: Learning Test
- Baxter ingested: [PASS/FAIL]
- Baxter in graph: [PASS/FAIL]
- Baxter retrievable via raw-context: [PASS/FAIL]
- Karma recalls Baxter: [PASS/FAIL]
- Evidence: [paste Karma's response]

### Phase 4: Full System
- Ollie retrieval: [PASS/FAIL]
- Voice quality: [PASS/FAIL]
- MODEL_DEFAULT: [glm-4.7-flash / OTHER — if other, THIS IS A FAILURE]
- All containers healthy: [PASS/FAIL]
- Graph counts: Entity=[N], Episodic=[N], canonical=[N]

### Summary
- Total tests: [N]
- Passed: [N]
- Failed: [N]
- Karma is learning: [YES/NO]
```

## ANTI-DRIFT RULES

1. After EVERY file edit, re-read the edited section to confirm the change is correct
2. After EVERY docker rebuild, run `docker ps` to confirm containers are healthy
3. After EVERY test, report the actual output — do not say "as expected" without showing evidence
4. If ANY test fails, STOP. Do not proceed to the next phase. Diagnose and fix the failure first.
5. If you need to change approach mid-stream, explain WHY before making the change
6. Do NOT invent additional features, cleanup tasks, or "nice to have" improvements
7. Do NOT change MODEL_DEFAULT. If you feel the urge, STOP and re-read rule #7.
8. The ONLY goal is: Karma chats, remembers, learns, and uses tools. Nothing else.
