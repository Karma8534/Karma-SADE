# Coordination Bus v1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable structured async agent-to-agent communication via hub-bridge coordination cache + vault ledger.

**Architecture:** Hub-bridge hosts `_coordinationCache` (Map, 100 entries, 24h TTL). Three HTTP endpoints for CRUD. One Karma tool (`coordination_post`). Context injection into `buildSystemText()`. Fire-and-forget durability writes to vault ledger via `vaultPost()`.

**Tech Stack:** Node.js (hub-bridge server.js), HTTP endpoints, Anthropic tool definitions

**Design doc:** `docs/plans/2026-03-12-coordination-bus-design.md`

---

## Key File Locations

| What | File | Line |
|------|------|------|
| `_sessionStore` Map (pattern to copy) | `hub-bridge/app/server.js` | 38 |
| `_directionMdCache` (pattern to copy) | `hub-bridge/app/server.js` | 95–101 |
| `buildSystemText()` signature (8 params) | `hub-bridge/app/server.js` | 591 |
| TOOL_DEFINITIONS array | `hub-bridge/app/server.js` | 994+ |
| `executeToolCall()` hub-native handlers | `hub-bridge/app/server.js` | 1249–1557 |
| HTTP route handlers (http.createServer) | `hub-bridge/app/server.js` | 1867+ |
| Last route before fallback | `hub-bridge/app/server.js` | 2876 |
| `vaultPost()` fire-and-forget pattern | `hub-bridge/app/server.js` | ~1351 |
| `server.listen()` + startup init | `hub-bridge/app/server.js` | 2904–2910 |
| `buildVaultRecord()` (required for vault writes) | `hub-bridge/app/server.js` | search for function |

**Deploy skill:** Use `karma-hub-deploy` skill for deployment. Build context is `/opt/seed-vault/memory_v1/hub_bridge/app/`, NOT the git repo.

**Testing:** No automated test framework exists for hub-bridge. Verification is manual: curl endpoints + check Karma's context injection via `/v1/chat` debug response.

---

### Task 1: Add `_coordinationCache` and helper functions

**Files:**
- Modify: `hub-bridge/app/server.js` (near line 38, after `_sessionStore`)

**Step 1: Add cache declaration and constants**

After `_sessionStore` (line 38), add:

```javascript
// Coordination bus — structured agent-to-agent messaging.
// In-memory cache (100 entries, 24h TTL). Durable via vault ledger (lane="coordination").
const COORD_MAX_ENTRIES = 100;
const COORD_TTL_MS = 24 * 60 * 60 * 1000; // 24 hours
const _coordinationCache = new Map();      // id → coordination entry object
```

**Step 2: Add ID generator function**

After the cache declaration:

```javascript
function generateCoordId() {
  const ts = Date.now();
  const rand = Math.random().toString(36).substring(2, 6);
  return `coord_${ts}_${rand}`;
}
```

**Step 3: Add eviction function**

```javascript
function evictExpiredCoordination() {
  const now = Date.now();
  for (const [id, entry] of _coordinationCache) {
    if (now - new Date(entry.created_at).getTime() > COORD_TTL_MS) {
      _coordinationCache.delete(id);
    }
  }
  // FIFO eviction if over max
  if (_coordinationCache.size > COORD_MAX_ENTRIES) {
    const sorted = [..._coordinationCache.entries()]
      .sort((a, b) => new Date(a[1].created_at) - new Date(b[1].created_at));
    const toRemove = sorted.slice(0, _coordinationCache.size - COORD_MAX_ENTRIES);
    for (const [id] of toRemove) _coordinationCache.delete(id);
  }
}
```

**Step 4: Add startup eviction interval**

Near line 2909 (before `server.listen`), add:

```javascript
setInterval(evictExpiredCoordination, 60 * 60 * 1000); // hourly sweep
```

**Step 5: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(coordination): add _coordinationCache with TTL and FIFO eviction"
```

---

### Task 2: Add `getRecentCoordination()` context injection function

**Files:**
- Modify: `hub-bridge/app/server.js` (after eviction function, before `buildSystemText`)

**Step 1: Add the formatting function**

```javascript
function getRecentCoordination(agentName) {
  evictExpiredCoordination(); // lazy cleanup
  const now = Date.now();
  const entries = [..._coordinationCache.values()]
    .filter(e => e.to === agentName || e.from === agentName)
    .sort((a, b) => {
      // pending first, then by recency
      if (a.status === "pending" && b.status !== "pending") return -1;
      if (b.status === "pending" && a.status !== "pending") return 1;
      return new Date(b.created_at) - new Date(a.created_at);
    })
    .slice(0, 5);

  if (entries.length === 0) return "";

  let text = "\n--- COORDINATION (recent messages for you) ---\n";
  let totalChars = 0;
  const MAX_CHARS = 2000;
  const MAX_ENTRY_CHARS = 300;

  for (const e of entries) {
    const age = now - new Date(e.created_at).getTime();
    const agoStr = age < 3600000 ? `${Math.round(age / 60000)}m ago`
                 : age < 86400000 ? `${Math.round(age / 3600000)}h ago`
                 : "1d+ ago";
    const tag = e.status === "pending" ? "PENDING" : e.urgency.toUpperCase();
    const dir = e.from === agentName ? `You → ${e.to}` : `${e.from}`;
    let content = e.content || "";
    if (content.length > MAX_ENTRY_CHARS) content = content.substring(0, MAX_ENTRY_CHARS) + " [truncated]";

    const line = `[${tag}] ${dir} (${agoStr}): "${content}"\n`;
    if (totalChars + line.length > MAX_CHARS) break;
    text += line;
    totalChars += line.length;
  }

  text += "---\n";
  return text;
}
```

**Step 2: Inject into `buildSystemText()`**

At line 591, add 9th parameter:

```javascript
function buildSystemText(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null, activeIntentsText = null, k2MemCtx = null, k2WorkingMemCtx = null, coordinationCtx = null)
```

Inside the function body, after the K2 working memory injection block, add:

```javascript
if (coordinationCtx) {
  text += coordinationCtx;
}
```

**Step 3: Update the `buildSystemText()` call site**

Find the `buildSystemText(` call in the `/v1/chat` handler (around line 2028). Add `getRecentCoordination("karma")` as the 9th argument:

```javascript
const systemText = buildSystemText(
  karmaCtx, ckLatest, webResults, semanticCtx,
  memoryMd, activeIntentsText, k2MemCtx, k2WorkingMemCtx,
  getRecentCoordination("karma")
);
```

**Step 4: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(coordination): add getRecentCoordination() context injection into buildSystemText"
```

---

### Task 3: Add `POST /v1/coordination/post` endpoint

**Files:**
- Modify: `hub-bridge/app/server.js` (in HTTP route handlers, before the 404 fallback at line 2876)

**Step 1: Add the POST handler**

Before the `return notFound(res)` fallback:

```javascript
// ── Coordination Bus ──────────────────────────────────────
if (method === "POST" && pathname === "/v1/coordination/post") {
  if (!bearerOk(req, HUB_CHAT_TOKEN)) return json(res, 401, { error: "unauthorized" });
  try {
    const body = await readBody(req);
    const data = JSON.parse(body);

    // Validate required fields
    const { from, to, content, urgency } = data;
    if (!from || !to || !content || !urgency) {
      return json(res, 400, { error: "missing required fields: from, to, content, urgency" });
    }
    const validFrom = ["karma", "cc", "colby"];
    const validTo = ["karma", "cc", "colby", "all"];
    const validUrgency = ["blocking", "feedback", "informational"];
    if (!validFrom.includes(from)) return json(res, 400, { error: `invalid from: ${from}` });
    if (!validTo.includes(to)) return json(res, 400, { error: `invalid to: ${to}` });
    if (!validUrgency.includes(urgency)) return json(res, 400, { error: `invalid urgency: ${urgency}` });

    const entry = {
      id: generateCoordId(),
      from,
      to,
      type: data.type || "request",
      urgency,
      status: "pending",
      parent_id: data.parent_id || null,
      response_id: null,
      content,
      context: data.context || null,
      created_at: new Date().toISOString()
    };

    // If this is a response (has parent_id), update parent
    if (entry.parent_id && _coordinationCache.has(entry.parent_id)) {
      const parent = _coordinationCache.get(entry.parent_id);
      parent.response_id = entry.id;
      parent.status = "resolved";
    }

    // Store in cache
    _coordinationCache.set(entry.id, entry);
    evictExpiredCoordination();

    // Fire-and-forget write to vault ledger
    try {
      const record = buildVaultRecord({
        type: "log",
        content: `[COORD] ${from}→${to} (${urgency}): ${content}`,
        tags: ["coordination", from, to],
        source: "coordination-bus",
        confidence: 1.0
      });
      vaultPost("/v1/memory", VAULT_BEARER, record).catch(e =>
        console.error("[COORD] vault write failed:", e.message)
      );
    } catch (e) {
      console.error("[COORD] vault record build failed:", e.message);
    }

    console.log(`[COORD] ${entry.id}: ${from}→${to} (${urgency}) stored`);
    return json(res, 200, { ok: true, id: entry.id, entry });
  } catch (e) {
    console.error("[COORD] post error:", e.message);
    return json(res, 500, { error: e.message });
  }
}
```

**Step 2: Verify by reading the code**

Confirm `buildVaultRecord`, `vaultPost`, `VAULT_BEARER`, `readBody`, `bearerOk`, `json`, `notFound` are all available in scope. These are existing hub-bridge utilities.

**Step 3: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(coordination): add POST /v1/coordination/post endpoint"
```

---

### Task 4: Add `GET /v1/coordination/recent` endpoint

**Files:**
- Modify: `hub-bridge/app/server.js` (immediately after POST handler)

**Step 1: Add the GET handler**

```javascript
if (method === "GET" && pathname === "/v1/coordination/recent") {
  if (!bearerOk(req, HUB_CHAT_TOKEN)) return json(res, 401, { error: "unauthorized" });
  evictExpiredCoordination();

  const params = new URL(req.url, `http://${req.headers.host}`).searchParams;
  const filterTo = params.get("to");
  const filterStatus = params.get("status");
  const limit = Math.min(parseInt(params.get("limit") || "10", 10), 50);

  let entries = [..._coordinationCache.values()];
  if (filterTo) entries = entries.filter(e => e.to === filterTo);
  if (filterStatus) entries = entries.filter(e => e.status === filterStatus);
  entries.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
  entries = entries.slice(0, limit);

  return json(res, 200, { ok: true, count: entries.length, entries });
}
```

**Step 2: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(coordination): add GET /v1/coordination/recent endpoint"
```

---

### Task 5: Add `PATCH /v1/coordination/:id` endpoint

**Files:**
- Modify: `hub-bridge/app/server.js` (immediately after GET handler)

**Step 1: Add the PATCH handler**

```javascript
if (method === "PATCH" && pathname.startsWith("/v1/coordination/coord_")) {
  if (!bearerOk(req, HUB_CHAT_TOKEN)) return json(res, 401, { error: "unauthorized" });
  const id = pathname.replace("/v1/coordination/", "");
  if (!_coordinationCache.has(id)) return json(res, 404, { error: "not found" });

  try {
    const body = await readBody(req);
    const data = JSON.parse(body);
    const entry = _coordinationCache.get(id);

    if (data.status) {
      const validStatus = ["pending", "acknowledged", "resolved", "timeout"];
      if (!validStatus.includes(data.status)) return json(res, 400, { error: `invalid status: ${data.status}` });
      entry.status = data.status;
    }
    if (data.response_id) entry.response_id = data.response_id;

    console.log(`[COORD] ${id} updated: status=${entry.status}`);
    return json(res, 200, { ok: true, entry });
  } catch (e) {
    return json(res, 500, { error: e.message });
  }
}
```

**Step 2: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(coordination): add PATCH /v1/coordination/:id endpoint"
```

---

### Task 6: Add `coordination_post` tool to TOOL_DEFINITIONS and executeToolCall

**Files:**
- Modify: `hub-bridge/app/server.js` (TOOL_DEFINITIONS at line 994+, executeToolCall at line 1249+)

**Step 1: Add tool definition to TOOL_DEFINITIONS array**

Add to the TOOL_DEFINITIONS array (after the last existing tool):

```javascript
{
  name: "coordination_post",
  description: "Post a message to the coordination bus for another agent (CC, Colby). Use for requests, questions, or proposals that need another agent's input. Messages are stored and delivered asynchronously.",
  input_schema: {
    type: "object",
    properties: {
      to: { type: "string", enum: ["cc", "colby", "all"], description: "Recipient agent" },
      content: { type: "string", description: "The message, question, or proposal" },
      urgency: { type: "string", enum: ["blocking", "feedback", "informational"], description: "How urgent: blocking (need answer before proceeding), feedback (want input), informational (FYI)" },
      context: { type: "string", description: "Optional reasoning context — why you're asking, what you're working on" },
      parent_id: { type: "string", description: "Optional ID of the coordination post this responds to" }
    },
    required: ["to", "content", "urgency"]
  }
}
```

**Important:** This tool is NOT deep-mode only. It must be available in ALL modes. Check the tool-gating logic near line 1269 — if there's a `deep_mode` filter on TOOL_DEFINITIONS, ensure `coordination_post` bypasses it or is in the always-available list.

**Step 2: Add executeToolCall handler**

In the `executeToolCall` function, before the karma-server proxy fallback (line ~1557), add:

```javascript
if (toolName === "coordination_post") {
  try {
    const entry = {
      id: generateCoordId(),
      from: "karma",
      to: toolInput.to,
      type: "request",
      urgency: toolInput.urgency,
      status: "pending",
      parent_id: toolInput.parent_id || null,
      response_id: null,
      content: toolInput.content,
      context: toolInput.context || null,
      created_at: new Date().toISOString()
    };

    if (entry.parent_id && _coordinationCache.has(entry.parent_id)) {
      const parent = _coordinationCache.get(entry.parent_id);
      parent.response_id = entry.id;
      parent.status = "resolved";
    }

    _coordinationCache.set(entry.id, entry);
    evictExpiredCoordination();

    // Fire-and-forget vault write
    try {
      const record = buildVaultRecord({
        type: "log",
        content: `[COORD] karma→${toolInput.to} (${toolInput.urgency}): ${toolInput.content}`,
        tags: ["coordination", "karma", toolInput.to],
        source: "coordination-bus",
        confidence: 1.0
      });
      vaultPost("/v1/memory", VAULT_BEARER, record).catch(e =>
        console.error("[COORD] vault write failed:", e.message)
      );
    } catch (_) {}

    console.log(`[COORD] tool: ${entry.id} karma→${toolInput.to}`);
    return JSON.stringify({ ok: true, id: entry.id, message: `Posted to coordination bus. ${toolInput.to} will see this.` });
  } catch (e) {
    return JSON.stringify({ ok: false, error: e.message });
  }
}
```

**Step 3: Verify tool gating**

Search for where `deep_mode` filters TOOL_DEFINITIONS. If `coordination_post` would be filtered out in standard mode, add it to the always-available list. The design requires it in ALL modes.

**Step 4: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(coordination): add coordination_post tool (all modes, hub-bridge-native)"
```

---

### Task 7: Update resurrect skill to check coordination

**Files:**
- Modify: `C:\Users\raest\.claude\skills\resurrect\SKILL.md`

**Step 1: Add coordination check to Step 3d**

After the Docker health check in Step 3d, add:

```markdown
**Step 3e: Check coordination bus for pending requests**
```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s -H \"Authorization: Bearer \$TOKEN\" http://localhost:18090/v1/coordination/recent?to=cc&status=pending"
```
If pending requests exist: surface them to Colby before proceeding with other work.
```

**Step 2: Commit**

```bash
git add C:\Users\raest\.claude\skills\resurrect\SKILL.md
git commit -m "feat(coordination): add coordination check to resurrect skill"
```

---

### Task 8: Deploy + Verify

**Use `karma-hub-deploy` skill for deployment.** Summary of deploy steps:

**Step 1: Push to GitHub**
```bash
git push origin main
```

**Step 2: Pull on vault-neo + sync to build context**
```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js"
ssh vault-neo "diff /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js && echo IN_SYNC"
```

**Step 3: Build + deploy**
```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache hub-bridge && docker compose -f compose.hub.yml up -d hub-bridge"
```

**Step 4: Verify startup**
```bash
ssh vault-neo "docker inspect anr-hub-bridge --format '{{.RestartCount}}' && docker logs anr-hub-bridge --tail=15 2>&1"
```
Expected: RestartCount=0, clean startup logs.

**Step 5: Test POST endpoint**
```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s -X POST -H 'Authorization: Bearer \$TOKEN' -H 'Content-Type: application/json' -d '{\"from\":\"cc\",\"to\":\"karma\",\"content\":\"Coordination bus is live. This is a test message.\",\"urgency\":\"informational\",\"type\":\"notice\"}' http://localhost:18090/v1/coordination/post"
```
Expected: `{"ok":true,"id":"coord_...","entry":{...}}`

**Step 6: Test GET endpoint**
```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s -H 'Authorization: Bearer \$TOKEN' 'http://localhost:18090/v1/coordination/recent?to=karma'"
```
Expected: Returns the test message.

**Step 7: Test Karma sees it**

Send a message to Karma at hub.arknexus.net. Ask "do you see any coordination messages?" — her context should include the test notice.

**Step 8: Test PATCH endpoint**
```bash
ssh vault-neo "TOKEN=\$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s -X PATCH -H 'Authorization: Bearer \$TOKEN' -H 'Content-Type: application/json' -d '{\"status\":\"resolved\"}' http://localhost:18090/v1/coordination/coord_REPLACE_WITH_ACTUAL_ID"
```
Expected: `{"ok":true,"entry":{...,"status":"resolved"}}`

**Step 9: Commit deploy verification to MEMORY.md**

Update MEMORY.md with deployment status, then commit + push.
