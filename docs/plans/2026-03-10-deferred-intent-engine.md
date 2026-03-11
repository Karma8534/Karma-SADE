# Deferred Intent Engine — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a behavioral intent scheduling system to hub-bridge so Karma and Colby can create named, trigger-based behavioral intents that persist across requests and surface in Karma's context when conditions are met.

**Architecture:** New `hub-bridge/lib/deferred_intent.js` holds pure logic (trigger matching, ID generation, text rendering). `server.js` adds a `pending_intents` Map (same TTL pattern as `pending_writes`), an in-process `_activeIntentsMap` loaded from the vault ledger, two new deep-mode tools (`defer_intent`, `get_active_intents`), and extends `/v1/feedback` to handle intent approval. Active matched intents are injected into `buildSystemText()` as a new 6th parameter.

**Tech Stack:** Node.js ESM, node:test + node:assert/strict for tests. Reads vault ledger JSONL at `/karma/ledger/memory.jsonl` for startup load. Writes to vault via existing `vaultPost()` + `buildVaultRecord()`. No new dependencies. No karma-server changes.

**Design doc:** `docs/plans/2026-03-10-cognitive-architecture-design.md` (Section: Component 3)
**Context doc:** `.gsd/phase-deferred-intent-CONTEXT.md`

---

## Pre-flight

Read these before starting:
- `hub-bridge/app/server.js` lines 155–168 (`pending_writes` Map + TTL cleanup — mirror pattern for `pending_intents`)
- `hub-bridge/app/server.js` lines 424–485 (`buildSystemText` — add 6th param)
- `hub-bridge/app/server.js` lines 801–868 (`TOOL_DEFINITIONS` — add 2 new tools)
- `hub-bridge/app/server.js` lines 888–898 (`executeToolCall` write_memory handler — mirror for `defer_intent`)
- `hub-bridge/app/server.js` lines 1553–1612 (`/v1/feedback` handler — extend for `intent_id`)
- `hub-bridge/app/server.js` lines 665–687 (`buildVaultRecord` + `vaultPost` — vault write pattern)
- `hub-bridge/lib/feedback.js` (full file — mirror `processFeedback` + `prunePendingWrites` pattern)
- `hub-bridge/tests/test_system_text.js` (full file — test pattern)

**Key facts:**
- `pending_writes` Map: `{ content, ts }` → mirror as `pending_intents`: `{ intent, trigger, action, fire_mode, ts }`
- Vault ledger path (hub-bridge container): `/karma/ledger/memory.jsonl`
- Vault write: `type:"log"`, `tags:["deferred-intent"]`, content is the intent object
- Intent in vault: stored as `.content` field of the vault record
- To "complete" an intent: append new vault record with same `intent_id`, status="completed"
- On load: for each `intent_id`, use the latest status (last wins in JSONL scan)

**Run a test:** `node --test hub-bridge/tests/test_deferred_intent.js`
**Run all tests:** `node --test hub-bridge/tests/`

---

## Task 1: `hub-bridge/lib/deferred_intent.js` — pure logic

Pure functions with no I/O. Three exports used by server.js.

**Files:**
- Create: `hub-bridge/lib/deferred_intent.js`

**Step 1: Create the file**

```js
// lib/deferred_intent.js — pure logic for Deferred Intent Engine (no I/O)

/**
 * Generate a unique intent ID.
 */
export function generateIntentId() {
  return "int_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
}

/**
 * Check if a trigger condition matches the current request.
 *
 * @param {{ type: string, value?: string }} trigger
 * @param {string} userMessage
 * @param {string} sessionPhase  — "start" | "active" | "end"
 * @returns {boolean}
 */
export function triggerMatches(trigger, userMessage, sessionPhase = "active") {
  if (!trigger || !trigger.type) return false;

  switch (trigger.type) {
    case "always":
      return true;

    case "topic": {
      if (!trigger.value) return false;
      const needle = trigger.value.toLowerCase();
      return (userMessage || "").toLowerCase().includes(needle);
    }

    case "phase":
      return trigger.value === sessionPhase;

    default:
      return false;
  }
}

/**
 * Build the "Active Intents" text block for injection into buildSystemText().
 *
 * @param {Array} matchedIntents  — intents whose trigger matched
 * @returns {string}
 */
export function buildActiveIntentsText(matchedIntents) {
  if (!matchedIntents || matchedIntents.length === 0) return "";

  const lines = ["--- ACTIVE INTENTS ---"];
  for (const intent of matchedIntents) {
    const mode = intent.fire_mode || "recurring";
    const action = intent.action || "surface_before_responding";
    lines.push(`- [${action}] ${intent.intent} (fire_mode: ${mode}, id: ${intent.intent_id || "?"})`);
  }
  lines.push("--- END ACTIVE INTENTS ---");
  return lines.join("\n");
}

/**
 * Filter active intents by trigger match. Returns only intents that should surface.
 *
 * @param {Map} activeIntentsMap  — intent_id → intent object
 * @param {Set} firedThisSession  — intent_ids that have already fired this session
 * @param {string} userMessage
 * @param {string} sessionPhase
 * @returns {Array}
 */
export function getSurfaceIntents(activeIntentsMap, firedThisSession, userMessage, sessionPhase = "active") {
  const result = [];
  for (const [id, intent] of activeIntentsMap) {
    if (intent.status !== "active") continue;
    // once_per_conversation: skip if already fired this session
    if (intent.fire_mode === "once_per_conversation" && firedThisSession.has(id)) continue;
    if (triggerMatches(intent.trigger, userMessage, sessionPhase)) {
      result.push(intent);
    }
  }
  return result;
}
```

**Step 2: Verify syntax**

```
node --check hub-bridge/lib/deferred_intent.js
```
Expected: no output (clean)

**Step 3: Commit**

```bash
git add hub-bridge/lib/deferred_intent.js
git commit -m "feat(intent): add deferred_intent.js pure logic — Phase 4 Task 1"
```

---

## Task 2: Tests for `deferred_intent.js`

**Files:**
- Create: `hub-bridge/tests/test_deferred_intent.js`

**Step 1: Write the tests**

```js
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  generateIntentId,
  triggerMatches,
  buildActiveIntentsText,
  getSurfaceIntents,
} from "../lib/deferred_intent.js";

// --- generateIntentId ---

test("generateIntentId returns string starting with int_", () => {
  const id = generateIntentId();
  assert.ok(id.startsWith("int_"), "must start with int_");
});

test("generateIntentId returns unique IDs", () => {
  const ids = new Set(Array.from({ length: 10 }, generateIntentId));
  assert.equal(ids.size, 10, "all IDs must be unique");
});

// --- triggerMatches ---

test("triggerMatches always returns true for type=always", () => {
  assert.equal(triggerMatches({ type: "always" }, "", "active"), true);
  assert.equal(triggerMatches({ type: "always" }, "anything", "start"), true);
});

test("triggerMatches type=topic: returns true when keyword in message", () => {
  assert.equal(triggerMatches({ type: "topic", value: "redis-py" }, "how does redis-py handle keys?", "active"), true);
});

test("triggerMatches type=topic: case-insensitive", () => {
  assert.equal(triggerMatches({ type: "topic", value: "Redis-Py" }, "tell me about redis-py", "active"), true);
});

test("triggerMatches type=topic: returns false when keyword absent", () => {
  assert.equal(triggerMatches({ type: "topic", value: "redis-py" }, "tell me about mongodb", "active"), false);
});

test("triggerMatches type=phase: matches sessionPhase=start", () => {
  assert.equal(triggerMatches({ type: "phase", value: "start" }, "", "start"), true);
  assert.equal(triggerMatches({ type: "phase", value: "start" }, "", "active"), false);
});

test("triggerMatches unknown type returns false", () => {
  assert.equal(triggerMatches({ type: "semantic", value: "redis" }, "redis stuff", "active"), false);
});

test("triggerMatches null trigger returns false", () => {
  assert.equal(triggerMatches(null, "any message", "active"), false);
});

// --- buildActiveIntentsText ---

test("buildActiveIntentsText returns empty string for empty array", () => {
  assert.equal(buildActiveIntentsText([]), "");
  assert.equal(buildActiveIntentsText(null), "");
});

test("buildActiveIntentsText contains ACTIVE INTENTS header", () => {
  const text = buildActiveIntentsText([{ intent: "verify redis", action: "surface_before_responding", fire_mode: "once", intent_id: "int_123" }]);
  assert.ok(text.includes("--- ACTIVE INTENTS ---"), "must have header");
  assert.ok(text.includes("--- END ACTIVE INTENTS ---"), "must have footer");
});

test("buildActiveIntentsText includes intent description", () => {
  const text = buildActiveIntentsText([{ intent: "verify redis", action: "surface_before_responding", fire_mode: "once", intent_id: "int_abc" }]);
  assert.ok(text.includes("verify redis"), "must include intent text");
  assert.ok(text.includes("int_abc"), "must include intent_id");
  assert.ok(text.includes("surface_before_responding"), "must include action");
});

// --- getSurfaceIntents ---

test("getSurfaceIntents returns matching active intent", () => {
  const map = new Map([
    ["int_1", { status: "active", fire_mode: "once", intent: "verify redis", intent_id: "int_1", trigger: { type: "topic", value: "redis" } }]
  ]);
  const results = getSurfaceIntents(map, new Set(), "I need help with redis", "active");
  assert.equal(results.length, 1);
});

test("getSurfaceIntents skips once_per_conversation already fired", () => {
  const map = new Map([
    ["int_1", { status: "active", fire_mode: "once_per_conversation", intent: "greet", intent_id: "int_1", trigger: { type: "always" } }]
  ]);
  const fired = new Set(["int_1"]);
  const results = getSurfaceIntents(map, fired, "hello", "active");
  assert.equal(results.length, 0, "already-fired once_per_conversation must not surface");
});

test("getSurfaceIntents skips completed intents", () => {
  const map = new Map([
    ["int_1", { status: "completed", fire_mode: "once", intent: "check logs", intent_id: "int_1", trigger: { type: "always" } }]
  ]);
  const results = getSurfaceIntents(map, new Set(), "check the logs", "active");
  assert.equal(results.length, 0, "completed intent must not surface");
});

test("getSurfaceIntents returns multiple matching intents", () => {
  const map = new Map([
    ["int_1", { status: "active", fire_mode: "recurring", intent: "check redis", intent_id: "int_1", trigger: { type: "topic", value: "redis" } }],
    ["int_2", { status: "active", fire_mode: "recurring", intent: "always greet", intent_id: "int_2", trigger: { type: "always" } }],
    ["int_3", { status: "active", fire_mode: "recurring", intent: "check mongo", intent_id: "int_3", trigger: { type: "topic", value: "mongo" } }],
  ]);
  const results = getSurfaceIntents(map, new Set(), "redis question here", "active");
  assert.equal(results.length, 2, "should match redis + always but not mongo");
});
```

**Step 2: Run to verify all pass**

```
node --test hub-bridge/tests/test_deferred_intent.js
```
Expected: 16 passing

**Step 3: Commit**

```bash
git add hub-bridge/tests/test_deferred_intent.js
git commit -m "test(intent): add test_deferred_intent.js — Phase 4 Task 2"
```

---

## Task 3: Add `pending_intents` Map and in-process intent state to server.js

**Files:**
- Modify: `hub-bridge/app/server.js`

**Step 1: Add `pending_intents` Map + `_activeIntentsMap` + `_firedThisSession` Set**

In `hub-bridge/app/server.js`, after line 157 (`const pending_writes = new Map();`), add:

```js
// Pending intent proposals -- keyed by intent_id, awaiting /v1/feedback approval
const pending_intents = new Map();

// Approved active intents -- loaded from vault ledger at startup, updated on approval
// intent_id → intent object (status:"active")
const _activeIntentsMap = new Map();

// Tracks once_per_conversation intents that have already fired this server session
const _firedThisSession = new Set();
```

**Step 2: Add TTL cleanup to the existing setInterval (line 159)**

Inside the existing `setInterval(() => { ... })` after the `pending_writes` expiry loop (line 165–167), add:

```js
  // Expire pending intent proposals older than 30 minutes
  for (const [k, v] of pending_intents) {
    if (now - v.ts > 30 * 60 * 1000) pending_intents.delete(k);
  }
```

**Step 3: Add `loadActiveIntentsFromLedger()` function**

After the `fetchKarmaContext` function (around line 400), add:

```js
/**
 * Load active intents from vault ledger JSONL file.
 * Scans for deferred-intent tagged entries; uses latest status per intent_id.
 * Returns Map: intent_id → intent object.
 */
function loadActiveIntentsFromLedger() {
  const LEDGER_PATH = "/karma/ledger/memory.jsonl";
  const latestByIntentId = new Map(); // intent_id → { status, ...intent }

  let lines;
  try {
    lines = fs.readFileSync(LEDGER_PATH, "utf8").split("\n").filter(Boolean);
  } catch (e) {
    console.warn("[INTENT] Cannot read ledger for intent load:", e.message);
    return new Map();
  }

  for (const line of lines) {
    try {
      const entry = JSON.parse(line);
      if (!Array.isArray(entry.tags) || !entry.tags.includes("deferred-intent")) continue;
      const intent = entry.content;
      if (!intent || !intent.intent_id) continue;
      // Last entry for this intent_id wins (JSONL is append-only)
      latestByIntentId.set(intent.intent_id, intent);
    } catch { /* skip malformed */ }
  }

  const active = new Map();
  for (const [id, intent] of latestByIntentId) {
    if (intent.status === "active") active.set(id, intent);
  }
  console.log(`[INTENT] Loaded ${active.size} active intents from ledger`);
  return active;
}
```

**Step 4: Add cache refresh + populate on startup**

After the `loadActiveIntentsFromLedger` function, add:

```js
let _activeIntentsCacheTs = 0;
const ACTIVE_INTENTS_CACHE_MS = 5 * 60 * 1000; // 5 minutes

function refreshActiveIntentsCache() {
  const now = Date.now();
  if (now - _activeIntentsCacheTs < ACTIVE_INTENTS_CACHE_MS) return; // not stale yet
  const loaded = loadActiveIntentsFromLedger();
  // Merge: new load wins for known IDs; preserve in-session updates for others
  for (const [id, intent] of loaded) {
    _activeIntentsMap.set(id, intent);
  }
  _activeIntentsCacheTs = now;
}

// Populate on startup
try {
  const initial = loadActiveIntentsFromLedger();
  for (const [id, intent] of initial) _activeIntentsMap.set(id, intent);
  _activeIntentsCacheTs = Date.now();
} catch (e) {
  console.warn("[INTENT] Startup intent load failed:", e.message);
}
```

**Step 5: Verify server.js syntax**

```
node --check hub-bridge/app/server.js
```
Expected: no output (clean)

**Step 6: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(intent): add pending_intents Map + activeIntentsMap + ledger load — Phase 4 Task 3"
```

---

## Task 4: Import `deferred_intent.js` + extend `buildSystemText`

**Files:**
- Modify: `hub-bridge/app/server.js`

**Step 1: Add import at top of file**

In `hub-bridge/app/server.js`, after line 10 (`import { resolveLibraryUrl } from "./lib/library_docs.js";`), add:

```js
import { triggerMatches, buildActiveIntentsText, getSurfaceIntents } from "./lib/deferred_intent.js";
```

**Step 2: Update `buildSystemText` signature (line 424)**

```js
// BEFORE:
function buildSystemText(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null) {

// AFTER:
function buildSystemText(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null, activeIntentsText = null) {
```

**Step 3: Inject `activeIntentsText` inside `buildSystemText`**

After the `selfKnowledge` line (line 438 area, the `const selfKnowledge = ...` line), add:

```js
  // Active Intents injection — behavioral rules matched to this request.
  // Injected before karmaCtx so Karma reads her intents before reasoning.
  const intentBlock = activeIntentsText ? activeIntentsText + "\n\n" : "";
```

Then change the `let text =` line (line 440 area) to include `intentBlock`:

```js
  // BEFORE:
  let text = identityBlock + selfKnowledge + base + "\n\nTools available...";

  // AFTER: insert intentBlock after selfKnowledge, before base
  let text = identityBlock + selfKnowledge + intentBlock + base + "\n\nTools available...";
```

**Step 4: Add intent surfacing to `/v1/chat` call site (line 1370)**

Find the `const systemText = buildSystemText(...)` call in the `/v1/chat` handler and update it:

```js
// BEFORE:
const systemText = buildSystemText(karmaCtx, ckLatestData, webSearchResults, semanticCtx, _memoryMdCache || null);

// AFTER:
refreshActiveIntentsCache();
const surfacedIntents = getSurfaceIntents(_activeIntentsMap, _firedThisSession, userMessage, "active");
// Mark once_per_conversation intents as fired
for (const intent of surfacedIntents) {
  if (intent.fire_mode === "once_per_conversation") _firedThisSession.add(intent.intent_id);
}
const activeIntentsText = buildActiveIntentsText(surfacedIntents);
const systemText = buildSystemText(karmaCtx, ckLatestData, webSearchResults, semanticCtx, _memoryMdCache || null, activeIntentsText || null);
```

**Step 5: Verify syntax**

```
node --check hub-bridge/app/server.js
```
Expected: clean

**Step 6: Add injection test to test_system_text.js**

Add at the END of `hub-bridge/tests/test_system_text.js`:

```js
// ── Active Intents injection ───────────────────────────────────────────────────

function buildSystemTextWithIntents(karmaCtx, activeIntentsText = null) {
  const identityBlock = "IDENTITY\n\n---\n\n";
  const selfKnowledge = "[Self-knowledge: backbone=test]\n\n";
  const intentBlock = activeIntentsText ? activeIntentsText + "\n\n" : "";
  const base = karmaCtx
    ? `You are Karma.\n\n${karmaCtx}\n\nMemory rules.`
    : "You are Karma. No context.";
  return identityBlock + selfKnowledge + intentBlock + base;
}

test("active intents injected when activeIntentsText provided", () => {
  const text = buildSystemTextWithIntents("ctx", "--- ACTIVE INTENTS ---\n- verify redis\n--- END ACTIVE INTENTS ---");
  assert.ok(text.includes("ACTIVE INTENTS"), "must include intents block");
  assert.ok(text.includes("verify redis"), "must include intent text");
});

test("no intents block when activeIntentsText is null", () => {
  const text = buildSystemTextWithIntents("ctx", null);
  assert.ok(!text.includes("ACTIVE INTENTS"), "null must not inject");
});

test("intents appear AFTER identity block", () => {
  const text = buildSystemTextWithIntents("ctx", "--- ACTIVE INTENTS ---\ndata\n---");
  const identityPos = text.indexOf("IDENTITY");
  const intentPos = text.indexOf("ACTIVE INTENTS");
  assert.ok(intentPos > identityPos, "intents must appear after identity block");
});
```

**Step 7: Run all tests**

```
node --test hub-bridge/tests/
```
Expected: all tests pass (including 3 new in test_system_text.js)

**Step 8: Commit**

```bash
git add hub-bridge/app/server.js hub-bridge/tests/test_system_text.js
git commit -m "feat(intent): import deferred_intent.js + inject active intents into buildSystemText — Phase 4 Task 4"
```

---

## Task 5: Add `defer_intent` tool

**Files:**
- Modify: `hub-bridge/app/server.js`

**Step 1: Add `defer_intent` to `TOOL_DEFINITIONS` (after `get_library_docs` entry, before closing `]`)**

```js
  {
    name: "defer_intent",
    description: "Propose a behavioral intent to be remembered across requests. Karma-created intents require Colby approval (👍 at /v1/feedback with intent_id). Use when you notice a recurring gap or behavioral need that a specific trigger should address. Returns intent_id in response.",
    input_schema: {
      type: "object",
      properties: {
        intent:     { type: "string", description: "What should happen — e.g. 'verify redis-py signatures before asserting'" },
        trigger:    {
          type: "object",
          description: "When to surface — e.g. {type:'topic',value:'redis-py'} or {type:'always'} or {type:'phase',value:'start'}",
          properties: {
            type:  { type: "string", enum: ["topic", "phase", "always"] },
            value: { type: "string" },
          },
          required: ["type"],
        },
        action:    { type: "string", description: "What Karma does when triggered — use 'surface_before_responding'", default: "surface_before_responding" },
        fire_mode: { type: "string", enum: ["once", "once_per_conversation", "recurring"], description: "once=fires once then completes; once_per_conversation=fires once per session; recurring=stays active until Colby closes" },
      },
      required: ["intent", "trigger", "fire_mode"],
    },
  },
```

**Step 2: Add `defer_intent` handler in `executeToolCall` (after `write_memory` handler, before `get_vault_file`)**

```js
    // defer_intent -- propose a behavioral intent, gated by /v1/feedback
    if (toolName === "defer_intent") {
      const { intent, trigger, action = "surface_before_responding", fire_mode } = toolInput;
      if (!intent || !trigger || !fire_mode) return { error: "missing_fields", message: "intent, trigger, and fire_mode are required" };
      if (!["once", "once_per_conversation", "recurring"].includes(fire_mode)) {
        return { error: "invalid_fire_mode", message: "fire_mode must be once, once_per_conversation, or recurring" };
      }
      if (!["topic", "phase", "always"].includes(trigger.type)) {
        return { error: "invalid_trigger_type", message: "trigger.type must be topic, phase, or always" };
      }
      const id = "int_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
      pending_intents.set(id, {
        intent_id: id,
        intent,
        trigger,
        action,
        fire_mode,
        created_by: "karma",
        created_at: new Date().toISOString(),
        status: "pending",
        ts: Date.now(),
      });
      console.log("[TOOL-API] defer_intent proposed: intent_id=" + id + ", intent=" + intent.slice(0, 60));
      return { proposed: true, intent_id: id, message: "Intent proposed. Awaiting Colby approval via thumbs-up (intent_id: " + id + ") — or thumbs-down to discard." };
    }
```

**Step 3: Verify syntax**

```
node --check hub-bridge/app/server.js
```
Expected: clean

**Step 4: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(intent): add defer_intent tool to TOOL_DEFINITIONS + executeToolCall — Phase 4 Task 5"
```

---

## Task 6: Add `get_active_intents` tool

**Files:**
- Modify: `hub-bridge/app/server.js`

**Step 1: Add `get_active_intents` to `TOOL_DEFINITIONS` (after `defer_intent` entry)**

```js
  {
    name: "get_active_intents",
    description: "Query active intents. Use in deep mode before responding on topics where you have recurring behavioral rules, to verify which intents are active. Optionally filter by topic keyword or fire_mode.",
    input_schema: {
      type: "object",
      properties: {
        topic:     { type: "string", description: "Optional keyword filter — returns intents whose trigger value contains this string" },
        fire_mode: { type: "string", description: "Optional filter by fire_mode: once | once_per_conversation | recurring" },
      },
    },
  },
```

**Step 2: Add `get_active_intents` handler in `executeToolCall` (after `defer_intent` handler)**

```js
    // get_active_intents -- live query of active approved intents
    if (toolName === "get_active_intents") {
      const { topic, fire_mode: filterMode } = toolInput || {};
      refreshActiveIntentsCache();
      let intents = [..._activeIntentsMap.values()].filter(i => i.status === "active");
      if (filterMode) intents = intents.filter(i => i.fire_mode === filterMode);
      if (topic) {
        const needle = topic.toLowerCase();
        intents = intents.filter(i => {
          const v = (i.trigger?.value || "").toLowerCase();
          const desc = (i.intent || "").toLowerCase();
          return v.includes(needle) || desc.includes(needle);
        });
      }
      // Also include pending (unapproved) Karma-proposed intents
      const pending = [...pending_intents.values()].map(i => ({ ...i, _pending: true }));
      console.log(`[TOOL-API] get_active_intents: ${intents.length} active, ${pending.length} pending`);
      return { active: intents, pending, total_active: intents.length, total_pending: pending.length };
    }
```

**Step 3: Verify syntax**

```
node --check hub-bridge/app/server.js
```
Expected: clean

**Step 4: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(intent): add get_active_intents tool — Phase 4 Task 6"
```

---

## Task 7: Extend `/v1/feedback` to handle intent approval

**Files:**
- Modify: `hub-bridge/app/server.js`

**Step 1: Find the `/v1/feedback` handler (line 1553)**

Locate the block: `const { write_id, signal, note, turn_id } = body;`

**Step 2: Update the destructuring to extract `intent_id`**

```js
// BEFORE:
const { write_id, signal, note, turn_id } = body;
if ((!write_id && !turn_id) || !["up", "down"].includes(signal)) {
  return json(res, 400, { ok: false, error: "missing_fields", hint: "write_id or turn_id required, plus signal ('up'|'down')" });
}

// AFTER:
const { write_id, intent_id, signal, note, turn_id } = body;
if ((!write_id && !turn_id && !intent_id) || !["up", "down"].includes(signal)) {
  return json(res, 400, { ok: false, error: "missing_fields", hint: "write_id, intent_id, or turn_id required, plus signal ('up'|'down')" });
}
```

**Step 3: Add intent approval/rejection branch after the existing DPO cleanup block (after `if (delete_key) pending_writes.delete(delete_key);`)**

```js
      // Intent approval/rejection — independent of write_memory flow
      if (intent_id) {
        const intentEntry = pending_intents.get(intent_id);
        if (!intentEntry) {
          return json(res, 404, { ok: false, error: "intent_not_found", hint: `No pending intent with intent_id=${intent_id}` });
        }

        if (signal === "up") {
          // Approve: write to vault ledger + add to active map
          const approvedIntent = { ...intentEntry, status: "active", approved: true, approved_at: new Date().toISOString() };
          delete approvedIntent.ts; // remove internal TTL timestamp
          try {
            const record = buildVaultRecord({
              type: "log",
              content: approvedIntent,
              tags: ["deferred-intent"],
              source: "intent-approval",
              confidence: 1.0,
            });
            const vResult = await vaultPost("/v1/memory", VAULT_BEARER, record);
            if (vResult.status >= 300) throw new Error(`vault ${vResult.status}: ${vResult.text.slice(0, 120)}`);
            _activeIntentsMap.set(intent_id, approvedIntent);
            _activeIntentsCacheTs = Date.now(); // invalidate cache
            console.log(`[FEEDBACK] 👍 intent approved: intent_id=${intent_id}, intent="${intentEntry.intent.slice(0, 60)}"`);
          } catch (e) {
            console.error(`[FEEDBACK] Intent vault write failed: ${e.message}`);
            return json(res, 500, { ok: false, error: "vault_write_failed", message: e.message });
          }
        } else {
          console.log(`[FEEDBACK] 👎 intent rejected: intent_id=${intent_id}`);
        }

        pending_intents.delete(intent_id);
        return json(res, 200, { ok: true, signal, intent_id, approved: signal === "up" });
      }
```

Note: place this block BEFORE the final `return json(res, 200, { ok: true, signal, wrote: !!write_content });` line.

**Step 4: Verify syntax**

```
node --check hub-bridge/app/server.js
```
Expected: clean

**Step 5: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(intent): extend /v1/feedback to handle intent approval — Phase 4 Task 7"
```

---

## Task 8: System prompt coaching

**Files:**
- Modify: `Memory/00-karma-system-prompt-live.md`

**Step 1: Read the system prompt to find the coaching/tools section**

```
Read Memory/00-karma-system-prompt-live.md
```
Find the section that discusses tools or behavioral rules.

**Step 2: Add `defer_intent` coaching section near the end (before any closing section)**

```markdown
## Deferred Intent Engine — Creating Behavioral Intents

When you notice a recurring behavioral need — a check you keep forgetting, a verification you should always run on a topic — use `defer_intent` to propose it. Colby approves via thumbs-up.

**When to call `defer_intent`:**
- You caught yourself asserting something you weren't sure about → propose to always verify that topic
- A recurring mistake pattern in the conversation → propose a once_per_conversation reminder
- Colby says "remember to always X when Y" → propose it immediately

**Format:**
```
defer_intent({
  intent: "verify redis-py function signatures before asserting",   // what to do
  trigger: { type: "topic", value: "redis-py" },                   // when to fire
  action: "surface_before_responding",                             // always use this
  fire_mode: "once_per_conversation"                               // or "recurring" or "once"
})
```

**Fire mode selection:**
- `once` — one-time reminder (e.g., "remind Colby about the deployment check after this task")
- `once_per_conversation` — fires once per session, then stays silent until next restart
- `recurring` — stays active indefinitely (e.g., "always verify X when Y appears")

**Active Intents in your system prompt:**
The `--- ACTIVE INTENTS ---` section shows intents matching this request. Read it before responding on the topic.

**`get_active_intents()` tool:**
Use in deep mode to query all active intents, optionally filtered by topic or fire_mode. Call before proposing a new intent on a topic to avoid duplicates.

**Important:**
- Proposed intents are NOT active until Colby approves (👍 with intent_id)
- Do NOT repeat a `defer_intent` call for the same intent this conversation
- If the snapshot shows a pending intent, inform Colby it's awaiting approval — don't re-propose
```

**Step 3: Verify character count**

```bash
wc -c Memory/00-karma-system-prompt-live.md
```
Expected: reasonable increase. If total > 20,000 chars, flag for trimming.

**Step 4: Commit**

```bash
git add Memory/00-karma-system-prompt-live.md
git commit -m "feat(intent): add defer_intent coaching to system prompt — Phase 4 Task 8"
```

---

## Task 9: Deploy and acceptance test

**Files:** No code changes — deploy + test only.

**Step 1: Run all tests locally**

```
node --test hub-bridge/tests/
```
Expected: all passing (existing + new)

**Step 2: Push to GitHub**

```bash
git push origin main
```

**Step 3: Pull to vault-neo and sync build context**

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/lib/deferred_intent.js /opt/seed-vault/memory_v1/hub_bridge/lib/deferred_intent.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js"
ssh vault-neo "cp /home/neo/karma-sade/Memory/00-karma-system-prompt-live.md /opt/seed-vault/memory_v1/hub_bridge/Memory/00-karma-system-prompt-live.md 2>/dev/null || true"
```

**Step 4: Rebuild and deploy**

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d"
```

**Step 5: Verify startup**

```bash
ssh vault-neo "docker logs anr-hub-bridge --tail=20"
```
Expected: `[INTENT] Loaded N active intents from ledger`, no SyntaxError, no `[CONFIG ERROR]`.

**Step 6: Acceptance test — propose intent via deep mode**

```bash
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "Please propose an intent: whenever I mention redis-py, you should verify function signatures before asserting. Use fire_mode recurring."}' | jq '{ok, write_id, intent_id: .intent_id, assistant_text: .assistant_text}'
```
Expected: response includes `intent_id` field, assistant text confirms the proposal.

**Step 7: Acceptance test — approve intent**

```bash
# Use intent_id from previous response
INTENT_ID="<intent_id from above>"
curl -s -X POST https://hub.arknexus.net/v1/feedback \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"intent_id\": \"${INTENT_ID}\", \"signal\": \"up\"}" | jq .
```
Expected: `{"ok": true, "signal": "up", "approved": true}`

**Step 8: Acceptance test — intent surfaces on trigger**

```bash
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "What does redis-py use for the get() method signature?"}' | jq '.assistant_text' | head -10
```
Expected: Karma's response references the active intent or shows verification behavior.

**Step 9: Acceptance test — `get_active_intents` tool works**

```bash
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "Call get_active_intents and tell me what intents you have."}' | jq '.assistant_text'
```
Expected: Karma calls `get_active_intents` and lists the approved redis-py intent.

**Step 10: Update STATE.md and commit docs**

```bash
git add .gsd/STATE.md MEMORY.md
git commit -m "docs: Phase 4 Deferred Intent Engine deployed — update STATE.md"
git push origin main
```

---

## Completion Criteria

- [ ] `node --test hub-bridge/tests/` — all tests pass (existing + new)
- [ ] `docker logs anr-hub-bridge` — shows `[INTENT] Loaded N active intents from ledger` on startup
- [ ] `defer_intent` tool callable in deep mode — returns `intent_id`
- [ ] `/v1/feedback` with `intent_id` + `signal:"up"` approves intent (vault write + active map update)
- [ ] Approved intent surfaces as `--- ACTIVE INTENTS ---` block in next matching request
- [ ] `get_active_intents` tool returns current active + pending intents
- [ ] `fire_mode=once_per_conversation` intent fires once then goes silent in same session
- [ ] STATE.md updated with Phase 4 status

---

## Known Limitations (MVP)

- `pending_intents` not persisted across server restarts (TTL Map only)
- `fire_mode=once` completion not persisted across restarts (only in `_firedThisSession`... actually: once intents auto-complete per below note)
- `_firedThisSession` resets on restart — once_per_conversation intents may re-fire after deployment
- Colby-created intents via natural language NOT implemented in Phase 4 (requires NLP pattern matching — deferred)
- `once` fire_mode: after surfacing, the intent should be marked completed in vault. **Implementation note:** In `getSurfaceIntents`, `fire_mode=once` intents are included but hub-bridge must call `markIntentCompleted()` after they surface. Add this to the `/v1/chat` handler after systemText is built: for each surfaced intent with `fire_mode=once`, append completed record to vault async. (Can be deferred to Phase 4b if needed for MVP.)

---

*Plan authored: 2026-03-10 — Session 78*
*Next phase: Phase 1 (Self-Model Kernel) and Phase 2 (Metacognitive Trace) can proceed in parallel*
