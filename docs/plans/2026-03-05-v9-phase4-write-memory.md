# v9 Phase 4 — write_memory + /v1/feedback Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Give Karma a gated write path — she can propose a MEMORY.md append in deep-mode conversations, and Colby approves/rejects via thumbs up/down. Rejections with a note accumulate DPO preference pairs in the ledger.

**Architecture:** In-process `pending_writes` Map keyed by a request-scoped `write_id` generated before the LLM call. The write_id threads through callLLMWithTools → callGPTWithTools → executeToolCall. The `/v1/feedback` endpoint looks up the write_id, executes or discards, and always stores a DPO pair in the vault ledger. The UI already has thumbs up/down; we add a ~15-line textarea after 👎.

**Tech Stack:** Node.js (hub-bridge server.js), Python (karma-core/hooks.py), vanilla JS (unified.html), node:test for tests.

**Design doc:** `docs/plans/2026-03-05-v9-phase4-write-memory-design.md`

---

## Key Facts (read before touching code)

- `hub-bridge/app/server.js` — monolithic request handler, ~1900 lines. All changes are additive.
- `TOOL_DEFINITIONS` array is around line 808. `executeToolCall()` is around line 858.
- `callLLMWithTools(model, messages, maxTokens)` and `callGPTWithTools(messages, maxTokens, model)` — note **different param order**.
- `/v1/chat` handler starts around line 1157. `turn_id` comes from vault response AFTER the LLM call — do NOT use it as the pending_writes key.
- `pending_writes` keyed by `write_id` (generated pre-LLM). `write_id` is returned in the `/v1/chat` response only if a write was proposed.
- `fs` is already imported: look for `import fs from "fs"` or `readFileSync` usage near top.
- `MEMORY.md` write path: `VAULT_FILE_ALIASES["MEMORY.md"]` = `/karma/MEMORY.md` (rw volume mount).
- DPO pairs stored via `vaultPost("/v1/memory", VAULT_BEARER, record)` — same pattern as chat storage.
- `corrections-log.md` is NOT accessible from hub-bridge (repo mount is read-only). Skip it. DPO pair with `signal:"down"` + `preferred: note` IS the correction record.
- **Deploy order:** karma-server rebuild first (hooks.py) → hub-bridge rebuild (server.js + unified.html) → system prompt update (git pull + docker restart only).
- **No worktree:** work directly on main branch, commit each task.

---

## Task 1: Extract feedback logic to `hub-bridge/lib/feedback.js`

This is the only new lib file. Everything else goes in existing files. Extracting makes the logic unit-testable without spinning up a server.

**Files:**
- Create: `hub-bridge/lib/feedback.js`
- Create: `hub-bridge/tests/test_feedback.js`

**Step 1: Write the failing tests**

```js
// hub-bridge/tests/test_feedback.js
import { test } from "node:test";
import assert from "node:assert/strict";
import { processFeedback, prunePendingWrites } from "../lib/feedback.js";

// ── prunePendingWrites ────────────────────────────────────────────────────────

test("prune: removes entries older than max_age_ms", () => {
  const map = new Map();
  map.set("old", { content: "x", ts: Date.now() - 60_000 });
  map.set("new", { content: "y", ts: Date.now() });
  prunePendingWrites(map, 30_000);
  assert.equal(map.has("old"), false);
  assert.equal(map.has("new"), true);
});

test("prune: no-op when all entries are fresh", () => {
  const map = new Map();
  map.set("a", { content: "x", ts: Date.now() });
  prunePendingWrites(map, 30_000);
  assert.equal(map.size, 1);
});

// ── processFeedback: thumbs up ────────────────────────────────────────────────

test("up without note: write_content is pending content", () => {
  const map = new Map();
  map.set("wr_1", { content: "Colby prefers dark mode", ts: Date.now() });
  const result = processFeedback(map, "wr_1", "up", undefined);
  assert.equal(result.write_content, "Colby prefers dark mode");
  assert.equal(result.dpo_pair.signal, "up");
  assert.equal(result.dpo_pair.proposed, "Colby prefers dark mode");
  assert.equal(result.dpo_pair.preferred, "Colby prefers dark mode");
  assert.equal(result.delete_key, "wr_1");
});

test("up with note: write_content is user's note instead", () => {
  const map = new Map();
  map.set("wr_1", { content: "Karma's phrasing", ts: Date.now() });
  const result = processFeedback(map, "wr_1", "up", "Colby's better phrasing");
  assert.equal(result.write_content, "Colby's better phrasing");
  assert.equal(result.dpo_pair.preferred, "Colby's better phrasing");
  assert.equal(result.dpo_pair.proposed, "Karma's phrasing");
});

// ── processFeedback: thumbs down ─────────────────────────────────────────────

test("down without note: write_content is null, DPO pair has null preferred", () => {
  const map = new Map();
  map.set("wr_1", { content: "bad write", ts: Date.now() });
  const result = processFeedback(map, "wr_1", "down", undefined);
  assert.equal(result.write_content, null);
  assert.equal(result.dpo_pair.signal, "down");
  assert.equal(result.dpo_pair.preferred, null);
  assert.equal(result.dpo_pair.proposed, "bad write");
});

test("down with note: write_content is null, preferred is user's note", () => {
  const map = new Map();
  map.set("wr_1", { content: "bad write", ts: Date.now() });
  const result = processFeedback(map, "wr_1", "down", "Here is the correct version");
  assert.equal(result.write_content, null);
  assert.equal(result.dpo_pair.preferred, "Here is the correct version");
});

// ── processFeedback: unknown write_id ────────────────────────────────────────

test("unknown write_id: no write_content, DPO pair has null proposed", () => {
  const map = new Map();
  const result = processFeedback(map, "unknown", "up", undefined);
  assert.equal(result.write_content, null);
  assert.equal(result.dpo_pair.proposed, null);
  assert.equal(result.delete_key, null);
});
```

**Step 2: Run tests to verify they fail**

```bash
cd hub-bridge && node --test tests/test_feedback.js 2>&1
```
Expected: `SyntaxError` or `Cannot find module` — `feedback.js` doesn't exist yet.

**Step 3: Write `hub-bridge/lib/feedback.js`**

```js
// lib/feedback.js — pure logic for /v1/feedback endpoint (no I/O)

/**
 * Remove pending_writes entries older than max_age_ms.
 * Called lazily at the start of each /v1/feedback request.
 */
export function prunePendingWrites(map, max_age_ms = 30 * 60 * 1000) {
  const cutoff = Date.now() - max_age_ms;
  for (const [key, entry] of map.entries()) {
    if (entry.ts < cutoff) map.delete(key);
  }
}

/**
 * Process a feedback signal for a pending write.
 * Returns { write_content, dpo_pair, delete_key } — all I/O is caller's responsibility.
 *
 * @param {Map} pending_writes - module-level map from write_id → {content, ts}
 * @param {string} write_id    - from /v1/feedback request body
 * @param {"up"|"down"} signal - feedback signal
 * @param {string|undefined} note - optional user correction text
 * @returns {{ write_content: string|null, dpo_pair: object, delete_key: string|null }}
 */
export function processFeedback(pending_writes, write_id, signal, note) {
  const entry = pending_writes.get(write_id) || null;
  const proposed = entry?.content || null;
  const preferred = note || (signal === "up" ? proposed : null);
  const write_content = signal === "up" ? (note || proposed) : null;

  const dpo_pair = {
    type: "dpo-pair",
    tags: ["dpo-pair"],
    write_id,
    signal,
    proposed,
    preferred,
    ts: new Date().toISOString(),
  };

  return {
    write_content,
    dpo_pair,
    delete_key: entry ? write_id : null,
  };
}
```

**Step 4: Run tests to verify they pass**

```bash
cd hub-bridge && node --test tests/test_feedback.js 2>&1
```
Expected: all 7 tests PASS.

**Step 5: Commit**

```bash
git add hub-bridge/lib/feedback.js hub-bridge/tests/test_feedback.js
git commit -m "feat(v9-p4): feedback.js lib — processFeedback + prunePendingWrites, 7 tests green"
```

---

## Task 2: Add `write_memory` tool to hub-bridge server.js

Four additive changes to server.js: `pending_writes` Map, tool definition, executeToolCall case, write_id threading.

**Files:**
- Modify: `hub-bridge/app/server.js`

**Step 1: Add `pending_writes` Map (module level)**

Find the block where module-level Maps/state are declared. Search for `const sessionHistory` or `const glmRateLimiter`. Add immediately after:

```js
// Pending memory writes — keyed by write_id, awaiting /v1/feedback approval
const pending_writes = new Map();
```

**Step 2: Add `write_memory` to `TOOL_DEFINITIONS`**

Find the end of the `TOOL_DEFINITIONS` array (after `get_vault_file` definition, before the closing `];`). Add:

```js
  {
    name: "write_memory",
    description: "Propose appending a note to MEMORY.md. The write is gated — it only executes if Colby approves via 👍. Use only in deep-mode when you learn something worth preserving across sessions: a preference, a correction, a fact not yet in MEMORY.md. Do not call on every turn.",
    input_schema: {
      type: "object",
      properties: {
        content: { type: "string", description: "Concise note to append to MEMORY.md (1-3 sentences max)" },
      },
      required: ["content"],
    },
  },
```

**Step 3: Add `write_memory` case to `executeToolCall`**

`executeToolCall` currently has signature `async function executeToolCall(toolName, toolInput)`.
Change signature to accept `writeId`:

```js
async function executeToolCall(toolName, toolInput, writeId = null) {
```

Then add the `write_memory` handler at the TOP of the try block, before the `get_vault_file` check:

```js
    // write_memory — propose a MEMORY.md append, gated by /v1/feedback
    if (toolName === "write_memory") {
      const content = (toolInput.content || "").trim();
      if (!content) return { error: "empty_content", message: "content is required" };
      const id = writeId || `wr_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      pending_writes.set(id, { content, ts: Date.now() });
      console.log(`[TOOL-API] write_memory proposed: write_id=${id}, ${content.length} chars`);
      return { proposed: true, write_id: id, message: "Memory write proposed. Awaiting your approval via 👍 — or 👎 to discard." };
    }
```

**Step 4: Thread `writeId` through callLLMWithTools and callGPTWithTools**

Find `async function callLLMWithTools(model, messages, maxTokens)`. Change to:
```js
async function callLLMWithTools(model, messages, maxTokens, writeId = null) {
```

Inside it, find `if (!isAnthropicModel(model)) return callGPTWithTools(messages, maxTokens, model);`. Change to:
```js
  if (!isAnthropicModel(model)) return callGPTWithTools(messages, maxTokens, model, writeId);
```

Find all calls to `executeToolCall(toolUse.name, toolUse.input)` inside `callLLMWithTools`. Change to:
```js
      const toolResult = await executeToolCall(toolUse.name, toolUse.input, writeId);
```

Find `async function callGPTWithTools(messages, maxTokens, model)`. Change to:
```js
async function callGPTWithTools(messages, maxTokens, model, writeId = null) {
```

Find all calls to `executeToolCall(toolCall.function.name, ...)` inside `callGPTWithTools`. Change to:
```js
        const toolResult = await executeToolCall(toolCall.function.name, toolArgs, writeId);
```

**Step 5: Generate write_id in /v1/chat handler and thread to callLLMWithTools**

In the `/v1/chat` handler, find the line where `callLLMWithTools` or `callLLM` is called (around line 1271):
```js
      const llmResult = deep_mode
        ? await callLLMWithTools(model, messages, max_output_tokens)
        : await callLLM(model, messages, max_output_tokens);
```

Add `req_write_id` BEFORE this block:
```js
      const req_write_id = `wr_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
      const llmResult = deep_mode
        ? await callLLMWithTools(model, messages, max_output_tokens, req_write_id)
        : await callLLM(model, messages, max_output_tokens);
```

**Step 6: Include write_id in /v1/chat response**

After `const turn_id = vpJson?.id || null;`, add:
```js
      // Include write_id if a memory write was proposed this turn
      const proposed_write_id = pending_writes.has(req_write_id) ? req_write_id : null;
```

Add `write_id: proposed_write_id` to BOTH the 207 (vault failed) and 200 (success) response objects. Find the two `return json(res, 200, {...})` and `return json(res, 207, {...})` calls and add the field alongside `canonical`.

**Step 7: Smoke test manually**

```bash
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "Remember that I prefer concise responses. Please use write_memory to save this preference."}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('write_id:', r.get('write_id'), '\ntext:', r.get('assistant_text','')[:200])"
```
Expected: `write_id: wr_...` present in response, assistant_text references the proposed write.

**Step 8: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(v9-p4): write_memory tool — pending_writes Map + tool def + executeToolCall case + write_id threading"
```

---

## Task 3: Add POST `/v1/feedback` endpoint to server.js

**Files:**
- Modify: `hub-bridge/app/server.js`

**Step 1: Add import for `processFeedback` and `prunePendingWrites`**

Near the top of server.js, find the existing imports. Add:
```js
import { processFeedback, prunePendingWrites } from "./lib/feedback.js";
```

**Step 2: Add the endpoint**

Find the block `// --- POST /v1/chatlog (single or batch) ---` (around line 1412). Add the feedback endpoint BEFORE it:

```js
    // --- POST /v1/feedback ---
    // Approve or reject a pending write_memory proposal. Always stores a DPO pair.
    if (req.method === "POST" && req.url === "/v1/feedback") {
      const token = bearerToken(req);
      if (!HUB_CHAT_TOKEN || !token || token !== HUB_CHAT_TOKEN) {
        return json(res, 401, { ok: false, error: "unauthorized" });
      }

      const raw = await parseBody(req, 50000);
      let body;
      try { body = JSON.parse(raw || "{}"); } catch { return json(res, 400, { ok: false, error: "invalid_json" }); }

      const { write_id, signal, note } = body;
      if (!write_id || !["up", "down"].includes(signal)) {
        return json(res, 400, { ok: false, error: "missing_fields", hint: "write_id and signal ('up'|'down') required" });
      }

      // Lazy prune: remove writes older than 30 minutes
      prunePendingWrites(pending_writes, 30 * 60 * 1000);

      // Process feedback — pure logic, no I/O
      const { write_content, dpo_pair, delete_key } = processFeedback(pending_writes, write_id, signal, note);

      // Execute write if approved
      if (write_content) {
        try {
          const filePath = VAULT_FILE_ALIASES["MEMORY.md"];
          const timestamp = new Date().toISOString();
          fs.appendFileSync(filePath, `\n[${timestamp}] [KARMA-WRITE] ${write_content}`);
          console.log(`[FEEDBACK] 👍 write executed: ${write_content.length} chars appended to MEMORY.md`);
        } catch (e) {
          console.error(`[FEEDBACK] MEMORY.md write failed: ${e.message}`);
          // Don't surface filesystem error to UI — still store DPO pair
        }
      } else {
        console.log(`[FEEDBACK] 👎 write discarded for write_id=${write_id}`);
      }

      // Store DPO pair in vault ledger
      try {
        const dpoRecord = {
          content: JSON.stringify(dpo_pair),
          tags: ["dpo-pair"],
          source: "feedback",
          metadata: { write_id, signal, has_note: !!note },
        };
        await vaultPost("/v1/memory", VAULT_BEARER, dpoRecord);
        console.log(`[FEEDBACK] DPO pair stored: signal=${signal}, has_note=${!!note}`);
      } catch (e) {
        console.error(`[FEEDBACK] DPO vault write failed: ${e.message}`);
        // Non-critical — don't fail the request
      }

      // Cleanup
      if (delete_key) pending_writes.delete(delete_key);

      return json(res, 200, { ok: true, signal, wrote: !!write_content });
    }

```

**Step 3: Verify `fs` is available as a named import**

Search server.js for how `fs` is used in the PATCH MEMORY.md handler (around line 1900). It uses `fs.appendFileSync`. Check the import at the top:
- If `import fs from "fs"` exists: nothing to do.
- If `const { appendFileSync } = await import("fs")` is used inline: the endpoint above uses `fs.appendFileSync` — add `import fs from "fs"` at top of file alongside other imports.

**Step 4: Test the feedback endpoint manually (requires Task 2 deployed)**

```bash
# Get a write_id from a deep-mode chat first (from Task 2 step 7)
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
WRITE_ID="wr_REPLACE_WITH_ACTUAL_ID"

# Test thumbs up
curl -s -X POST https://hub.arknexus.net/v1/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"write_id\": \"$WRITE_ID\", \"signal\": \"up\"}" \
  | python3 -m json.tool
# Expected: {"ok": true, "signal": "up", "wrote": true}

# Verify MEMORY.md was updated
ssh vault-neo "tail -3 /home/neo/karma-sade/MEMORY.md"
# Expected: last line contains [KARMA-WRITE] and the proposed content

# Verify DPO pair in ledger
ssh vault-neo "tail -5 /opt/seed-vault/memory_v1/ledger/memory.jsonl | python3 -c \"import sys; [print(l) for l in sys.stdin if 'dpo-pair' in l]\""
# Expected: a JSON line with tags including dpo-pair
```

**Step 5: Test thumbs down with note**

```bash
# Send a new deep-mode message to get a fresh write_id
# (repeat Task 2 step 7 to get a new WRITE_ID)
curl -s -X POST https://hub.arknexus.net/v1/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"write_id\": \"$WRITE_ID\", \"signal\": \"down\", \"note\": \"Karma should have said: Colby prefers bullet points over paragraphs\"}" \
  | python3 -m json.tool
# Expected: {"ok": true, "signal": "down", "wrote": false}

# Verify DPO pair has preferred set
ssh vault-neo "tail -5 /opt/seed-vault/memory_v1/ledger/memory.jsonl | python3 -c \"import sys,json; [print(json.loads(l).get('content','')[:300]) for l in sys.stdin if 'dpo-pair' in l]\""
# Expected: preferred field contains the note text
```

**Step 6: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(v9-p4): POST /v1/feedback endpoint — pending write gate + DPO pair ledger storage"
```

---

## Task 4: Update hooks.py (karma-server)

**Files:**
- Modify: `karma-core/hooks.py`

**Step 1: Add `write_memory` to ALLOWED_TOOLS**

Find line ~161 in `karma-core/hooks.py`:
```python
    ALLOWED_TOOLS = {"read_file", "write_file", "edit_file", "bash",
                     ...,
                     "graph_query", "get_vault_file"}
```

Add `"write_memory"` to the set:
```python
    ALLOWED_TOOLS = {"read_file", "write_file", "edit_file", "bash",
                     ...,
                     "graph_query", "get_vault_file", "write_memory"}
```

Note: `write_memory` is handled in hub-bridge (not proxied to karma-server), but hooks.py gates ALL tool names before they can be considered. Adding it here is belt-and-suspenders.

**Step 2: Commit**

```bash
git add karma-core/hooks.py
git commit -m "feat(v9-p4): add write_memory to hooks.py ALLOWED_TOOLS"
```

---

## Task 5: Deploy karma-server (hooks.py change)

**Step 1: Follow karma-server-deploy skill**

```bash
# Sync updated file to build context
ssh vault-neo "cp /home/neo/karma-sade/karma-core/hooks.py /opt/seed-vault/memory_v1/karma-core/hooks.py"

# Rebuild and redeploy
ssh vault-neo "cd /opt/seed-vault/memory_v1/compose && docker compose build --no-cache karma-server && docker compose up -d karma-server"

# Verify (follow karma-verify skill — karma-server section)
ssh vault-neo "docker inspect karma-server --format '{{.RestartCount}}'"
# Expected: 0
```

---

## Task 6: Deploy hub-bridge (server.js change)

**Step 1: Follow karma-hub-deploy skill**

```bash
# Sync to build context
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js"

# Also sync the new lib file
ssh vault-neo "mkdir -p /opt/seed-vault/memory_v1/hub_bridge/app/lib && cp /home/neo/karma-sade/hub-bridge/lib/feedback.js /opt/seed-vault/memory_v1/hub_bridge/app/lib/feedback.js"

# Rebuild and redeploy
ssh vault-neo "cd /opt/seed-vault/memory_v1/compose && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d"

# Verify (follow karma-verify skill — hub-bridge section)
ssh vault-neo "docker inspect anr-hub-bridge --format '{{.RestartCount}}'"
# Expected: 0
ssh vault-neo "docker logs anr-hub-bridge --tail=20 2>&1 | grep -E 'listening|ERROR|identity|WARN'"
# Expected: listening + identity loaded, no ERROR
```

**Step 2: Verify write_memory is now live in a deep-mode chat**

```bash
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "I prefer short responses. Please save this preference using write_memory."}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('write_id:', r.get('write_id'), '\ntext:', r.get('assistant_text','')[:300])"
```
Expected: `write_id` present, text mentions proposed write.

---

## Task 7: Add textarea to unified.html (UI update)

**Files:**
- Modify: `hub-bridge/app/public/unified.html`

**Step 1: Update `sendFeedback` to handle write_id**

Find `async function sendFeedback(turnId, signal, btnEl)` in unified.html. The current call sends `{ turn_id: turnId, signal }`. For write_memory flows, we need to send `write_id` instead. Modify to:

```js
  async function sendFeedback(writeId, signal, btnEl) {
    const token = getToken();
    if (!token) return;
    const btns = btnEl.parentElement;
    btns.querySelectorAll('button').forEach(b => b.classList.remove('active'));
    btnEl.classList.add('active');

    if (signal === 'down') {
      // Show inline textarea for optional correction note
      showFeedbackNote(writeId, btns);
      return; // Don't send yet — wait for textarea submit
    }

    // Thumbs up: send immediately
    try {
      await fetch('/v1/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
        body: JSON.stringify({ write_id: writeId, signal: 'up' }),
      });
    } catch (err) {
      console.warn('[UI] Feedback send failed:', err.message);
    }
  }
```

**Step 2: Add `showFeedbackNote` function**

Add immediately after `sendFeedback`:

```js
  function showFeedbackNote(writeId, btns) {
    // Remove any existing note box
    const existing = btns.parentElement.querySelector('.feedback-note');
    if (existing) existing.remove();

    const box = document.createElement('div');
    box.className = 'feedback-note';
    box.innerHTML = '<textarea placeholder="What should Karma have said? (optional)" rows="2"></textarea><button>Submit</button>';
    btns.parentElement.appendChild(box);

    box.querySelector('button').onclick = async function() {
      const note = box.querySelector('textarea').value.trim() || undefined;
      const token = getToken();
      try {
        await fetch('/v1/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token },
          body: JSON.stringify({ write_id: writeId, signal: 'down', note }),
        });
      } catch (err) {
        console.warn('[UI] Feedback send failed:', err.message);
      }
      box.remove();
    };
  }
```

**Step 3: Update `addMessage` to pass `write_id` (not `turn_id`) to feedback buttons**

Find `addMessage` function. Find where it sets up the thumbs up/down buttons:
```js
      btns.querySelector('.up').onclick = function() { sendFeedback(turnId, 'up', this); };
      btns.querySelector('.down').onclick = function() { sendFeedback(turnId, 'down', this); };
```

Change `addMessage` signature from `addMessage(role, text, turnId)` to `addMessage(role, text, turnId, writeId)`. Update the onclick handlers:
```js
      const feedbackId = writeId || turnId;
      btns.querySelector('.up').onclick = function() { sendFeedback(feedbackId, 'up', this); };
      btns.querySelector('.down').onclick = function() { sendFeedback(feedbackId, 'down', this); };
```

**Step 4: Update `handleMessage` to extract `write_id`**

Find `handleMessage(data)`. Update to pass `write_id` to `addMessage`:
```js
  function handleMessage(data) {
    hideTyping();
    if (data.assistant_text || data.response || data.content) {
      const text = data.assistant_text || data.response || data.content;
      const turnId = data.canonical?.turn_id || data.vault_write?.id || null;
      const writeId = data.write_id || null;  // ADD THIS
      addMessage('karma', text, turnId, writeId);  // PASS writeId
      updateSidebar(data);
      setConnStatus('Connected', true);
    } else if (data.error) {
      addMessage('system', 'Error: ' + data.error);
      setConnStatus('Error', false);
    }
  }
```

**Step 5: Add `.feedback-note` CSS**

Find the `.feedback-btns button` CSS block (around line 128). Add after it:
```css
  .feedback-note { margin-top: 4px; display: flex; gap: 4px; align-items: flex-start; }
  .feedback-note textarea { flex: 1; font-size: 12px; padding: 4px; border: 1px solid var(--border); background: var(--bg-secondary); color: var(--text); border-radius: 3px; resize: vertical; }
  .feedback-note button { font-size: 12px; padding: 4px 8px; border: 1px solid var(--border); background: var(--accent); color: var(--bg); border-radius: 3px; cursor: pointer; white-space: nowrap; }
```

**Step 6: Verify the UI changes in unified.html**

Open `https://hub.arknexus.net/unified.html` in browser. Send a deep-mode message that triggers write_memory. Confirm:
- 👍 and 👎 buttons appear next to Karma's response
- Clicking 👍 sends feedback immediately (check browser Network tab for POST /v1/feedback)
- Clicking 👎 shows the textarea below the message
- Typing in textarea and clicking Submit sends feedback with note
- The textarea disappears after submit

**Step 7: Commit**

```bash
git add hub-bridge/app/public/unified.html
git commit -m "feat(v9-p4): UI — write_id feedback flow + thumbs-down textarea for correction note"
```

---

## Task 8: Add system prompt coaching

**Files:**
- Modify: `Memory/00-karma-system-prompt-live.md`

**Step 1: Add coaching paragraph**

Open `Memory/00-karma-system-prompt-live.md`. Find the section `## How to Use Your Context Data` (added in v9 Phase 3). At the end of that section, append:

```markdown
### Memory Writes (deep-mode only)

When you learn something worth preserving across sessions — a preference Colby states, a correction to something you got wrong, a fact about the project that isn't in MEMORY.md yet — call `write_memory(content)` with a concise note (1-3 sentences).

The write requires Colby's approval before it executes. You will see "Memory write proposed" in your tool result. Do not call `write_memory` on every turn. Good triggers:
- Colby explicitly states a preference ("I prefer X", "always do Y")
- Colby corrects a factual error you made
- You learn a project fact that will matter next session and isn't already in your context
```

**Step 2: Verify file length**

```bash
wc -c Memory/00-karma-system-prompt-live.md
```
Expected: ~12,100–12,300 chars (was 11,850 before this addition).

**Step 3: Commit**

```bash
git add Memory/00-karma-system-prompt-live.md MEMORY.md
git commit -m "feat(v9-p4): system prompt coaching — write_memory usage guidance"
```

**Step 4: Deploy system prompt (NO rebuild needed)**

```bash
# git pull on vault-neo picks up the new system prompt
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"

# docker restart re-reads the file at startup (no rebuild needed per Decision #10)
ssh vault-neo "docker restart anr-hub-bridge"

# Verify identity block loaded
ssh vault-neo "docker logs anr-hub-bridge --tail=10 2>&1 | grep -E 'identity|KARMA_IDENTITY|WARN'"
```
Expected: `[INIT] KARMA_IDENTITY_PROMPT loaded` (or similar), no WARN.

---

## Task 9: Re-deploy hub-bridge with UI changes (Task 7)

The unified.html changes from Task 7 are static files served by hub-bridge. They need a container rebuild to pick them up (static files are COPYed into the image).

**Step 1: Sync unified.html to build context**

```bash
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html"
```

**Step 2: Rebuild hub-bridge**

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/compose && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d"
```

**Step 3: Run karma-verify (hub-bridge section)**

```bash
# RestartCount
ssh vault-neo "docker inspect anr-hub-bridge --format '{{.RestartCount}}'"
# Expected: 0

# Smoke test
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "ping"}' \
  | python3 -c 'import sys,json; r=json.load(sys.stdin); print("ok" if r.get("assistant_text") else "FAILED")'
# Expected: ok
```

---

## Task 10: End-to-end acceptance test

**Step 1: Full write_memory flow**

```bash
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")

# 1. Deep-mode chat that triggers write_memory
RESP=$(curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "Remember that I drink coffee every morning before starting work. Please save this with write_memory."}')

echo $RESP | python3 -m json.tool | grep -E "write_id|assistant_text"
# Expected: write_id is present, assistant_text mentions proposed write

WRITE_ID=$(echo $RESP | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('write_id',''))")
echo "write_id: $WRITE_ID"
```

**Step 2: Approve via 👍**

```bash
curl -s -X POST https://hub.arknexus.net/v1/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"write_id\": \"$WRITE_ID\", \"signal\": \"up\"}"
# Expected: {"ok": true, "signal": "up", "wrote": true}

# Verify MEMORY.md updated
ssh vault-neo "tail -3 /home/neo/karma-sade/MEMORY.md"
# Expected: [KARMA-WRITE] line with coffee preference
```

**Step 3: Verify DPO pair in ledger**

```bash
ssh vault-neo "tail -20 /opt/seed-vault/memory_v1/ledger/memory.jsonl" \
  | python3 -c "import sys,json; [print(json.dumps(json.loads(l), indent=2)) for l in sys.stdin if 'dpo-pair' in l]" \
  | head -30
# Expected: JSON with type:dpo-pair, signal:up, proposed and preferred present
```

**Step 4: Thumbs down with note**

```bash
# Get a new write_id from a fresh deep-mode message
RESP2=$(curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "Save that I work from home on Thursdays."}')
WRITE_ID2=$(echo $RESP2 | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('write_id',''))")

curl -s -X POST https://hub.arknexus.net/v1/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"write_id\": \"$WRITE_ID2\", \"signal\": \"down\", \"note\": \"More accurately: I work from home every day, not just Thursdays\"}"
# Expected: {"ok": true, "signal": "down", "wrote": false}

# Verify MEMORY.md was NOT changed for this one
ssh vault-neo "tail -3 /home/neo/karma-sade/MEMORY.md"
# Expected: still shows coffee preference, no Thursday entry
```

**Step 5: Standard mode does NOT offer write_memory**

```bash
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Save that I like tea using write_memory."}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('write_id:', r.get('write_id'), '| deep:', r.get('deep_mode'))"
# Expected: write_id: None (not present), deep_mode: False
```

**Step 6: Commit final session docs**

```bash
# Update MEMORY.md with Phase 4 completion
git add MEMORY.md
git commit -m "feat(v9-p4): complete — write_memory + /v1/feedback + UI textarea + system prompt coaching"

# Push
git push origin main
```

---

## Deployment Summary

| Order | What | Trigger |
|-------|------|---------|
| 1 | karma-server | hooks.py ALLOWED_TOOLS change |
| 2 | hub-bridge (server.js + lib/) | write_memory tool + /v1/feedback endpoint |
| 3 | hub-bridge (unified.html) | UI textarea changes — requires rebuild |
| 4 | System prompt | git pull + docker restart anr-hub-bridge (no rebuild) |

Steps 2 and 3 can be combined into one rebuild if both changes are committed before deploying.
