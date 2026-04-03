# Cognitive Architecture Layer — Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a Self-Model Kernel to hub-bridge that injects a dynamic, per-request self-awareness snapshot into every Karma response — showing her own tools, claim calibration, RPM state, pending writes, and detected patterns.

**Architecture:** New `buildSelfModelSnapshot()` function reads from existing in-process state (`pending_writes` Map, `glmLimiter` instance, `TOOL_DEFINITIONS`), computes a structured text block, and injects it as a new section in `buildSystemText()`. A new `get_self_model` deep-mode tool lets Karma verify the snapshot live. System prompt coaching teaches Karma what to do with each field.

**Tech Stack:** Node.js ESM, node:test + node:assert/strict for tests, existing hub-bridge/app/server.js + hub-bridge/lib/routing.js. No new dependencies. No karma-server changes. No vault API changes.

**Design doc:** `docs/plans/2026-03-10-cognitive-architecture-design.md`

---

## Pre-flight

Read these before starting:
- `hub-bridge/app/server.js` lines 424–485 (`buildSystemText`)
- `hub-bridge/app/server.js` lines 155–168 (`pending_writes` Map + TTL cleanup)
- `hub-bridge/app/server.js` lines 801–868 (`TOOL_DEFINITIONS`)
- `hub-bridge/app/server.js` lines 2186–2191 (`glmLimiter` instantiation)
- `hub-bridge/lib/routing.js` lines 26–55 (`GlmRateLimiter` class — `_rpm`, `_slots`)
- `hub-bridge/tests/test_system_text.js` (pattern for how tests are written here)

**Test pattern:** Tests in `hub-bridge/tests/` use Node.js native `node:test` + `node:assert/strict`. They inline simplified versions of the functions under test — they do NOT import from server.js directly (ESM + side-effects make that hard). Mirror the logic in the test file.

**Run a test:** `node --test hub-bridge/tests/test_system_text.js`

**Run all tests:** `node --test hub-bridge/tests/`

---

## Task 1: GlmRateLimiter — add RPM snapshot method

The `GlmRateLimiter` class in `hub-bridge/lib/routing.js` tracks slots in `this._slots[]`. We need a read-only snapshot of current state for the kernel: how many slots used and the configured limit.

**Files:**
- Modify: `hub-bridge/lib/routing.js` (add method to GlmRateLimiter class)
- Create: `hub-bridge/tests/test_routing_snapshot.js`

**Step 1: Write the failing test**

Create `hub-bridge/tests/test_routing_snapshot.js`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";

// Inline the relevant slice of GlmRateLimiter for unit testing
const WINDOW_MS = 60_000;
class GlmRateLimiter {
  constructor({ rpm = 20, nowFn = null } = {}) {
    this._rpm   = rpm;
    this._now   = nowFn || (() => Date.now());
    this._slots = [];
  }
  _prune() {
    const cutoff = this._now() - WINDOW_MS;
    while (this._slots.length > 0 && this._slots[0] <= cutoff) this._slots.shift();
  }
  checkAndConsume() {
    this._prune();
    if (this._slots.length < this._rpm) {
      this._slots.push(this._now());
      return { allowed: true, retryAfterMs: 0 };
    }
    return { allowed: false, retryAfterMs: this._slots[0] + WINDOW_MS - this._now() };
  }
  // METHOD UNDER TEST — add this below in routing.js:
  rpmSnapshot() {
    this._prune();
    return { used: this._slots.length, limit: this._rpm };
  }
}

test("rpmSnapshot returns used=0 and limit from constructor when no calls made", () => {
  const limiter = new GlmRateLimiter({ rpm: 40 });
  const snap = limiter.rpmSnapshot();
  assert.equal(snap.used, 0);
  assert.equal(snap.limit, 40);
});

test("rpmSnapshot reflects consumed slots", () => {
  const limiter = new GlmRateLimiter({ rpm: 40 });
  limiter.checkAndConsume();
  limiter.checkAndConsume();
  const snap = limiter.rpmSnapshot();
  assert.equal(snap.used, 2);
  assert.equal(snap.limit, 40);
});

test("rpmSnapshot prunes expired slots before counting", () => {
  let fakeNow = 0;
  const limiter = new GlmRateLimiter({ rpm: 40, nowFn: () => fakeNow });
  limiter.checkAndConsume(); // slot at t=0
  fakeNow = 61_000;          // advance past 60s window
  const snap = limiter.rpmSnapshot();
  assert.equal(snap.used, 0, "expired slot must not count");
});

test("rpmSnapshot does not consume a slot", () => {
  const limiter = new GlmRateLimiter({ rpm: 2 });
  limiter.rpmSnapshot();
  limiter.rpmSnapshot();
  const snap = limiter.rpmSnapshot();
  assert.equal(snap.used, 0, "rpmSnapshot must not consume slots");
});
```

**Step 2: Run test to verify it fails**

```
node --test hub-bridge/tests/test_routing_snapshot.js
```
Expected: FAIL — `rpmSnapshot is not a function`

**Step 3: Add `rpmSnapshot()` to GlmRateLimiter in routing.js**

In `hub-bridge/lib/routing.js`, inside the `GlmRateLimiter` class, after `waitForSlot()` (around line 78), add:

```js
  /**
   * Read-only snapshot of current RPM state. Does not consume a slot.
   * @returns {{ used: number, limit: number }}
   */
  rpmSnapshot() {
    this._prune();
    return { used: this._slots.length, limit: this._rpm };
  }
```

**Step 4: Run test to verify it passes**

```
node --test hub-bridge/tests/test_routing_snapshot.js
```
Expected: 4 passing

**Step 5: Commit**

```bash
git add hub-bridge/lib/routing.js hub-bridge/tests/test_routing_snapshot.js
git commit -m "feat(kernel): add rpmSnapshot() to GlmRateLimiter — Phase 1 Task 1"
```

---

## Task 2: `buildSelfModelSnapshot()` — core function

New function in `server.js` that assembles the kernel snapshot text block from in-process state. Returns a formatted string ready for injection into `buildSystemText()`.

**Files:**
- Modify: `hub-bridge/app/server.js` (add function before `buildSystemText`)
- Create: `hub-bridge/tests/test_self_model_snapshot.js`

**Step 1: Write the failing test**

Create `hub-bridge/tests/test_self_model_snapshot.js`:

```js
import { test } from "node:test";
import assert from "node:assert/strict";

// Inline the function under test (mirrors server.js logic)
function buildSelfModelSnapshot({ tools, rpmUsed, rpmLimit, pendingWrites }) {
  const toolNames = tools.map(t => t.name).join(", ");

  let lines = [
    "--- SELF-MODEL SNAPSHOT ---",
    `Tools available: ${toolNames}`,
    `RPM state: ${rpmUsed}/${rpmLimit} used`,
  ];

  // Unapproved memory writes
  const writesArr = [...pendingWrites.entries()].map(([id, v]) => ({
    id,
    preview: (v.content || "").slice(0, 60),
    age_turns: v.age_turns || 0,
  }));
  if (writesArr.length > 0) {
    lines.push(`Unapproved memory writes (this session): ${writesArr.length}`);
    for (const w of writesArr) {
      lines.push(`  - ${w.preview}... [write_id: ${w.id}]`);
    }
  } else {
    lines.push("Unapproved memory writes (this session): 0");
  }

  lines.push("--- END SELF-MODEL SNAPSHOT ---");
  return lines.join("\n");
}

const MOCK_TOOLS = [
  { name: "graph_query" },
  { name: "get_vault_file" },
  { name: "write_memory" },
];

test("snapshot contains SELF-MODEL SNAPSHOT header", () => {
  const snap = buildSelfModelSnapshot({ tools: MOCK_TOOLS, rpmUsed: 0, rpmLimit: 40, pendingWrites: new Map() });
  assert.ok(snap.includes("--- SELF-MODEL SNAPSHOT ---"), "must have header");
});

test("snapshot lists tool names", () => {
  const snap = buildSelfModelSnapshot({ tools: MOCK_TOOLS, rpmUsed: 0, rpmLimit: 40, pendingWrites: new Map() });
  assert.ok(snap.includes("graph_query"), "must list graph_query");
  assert.ok(snap.includes("write_memory"), "must list write_memory");
});

test("snapshot shows RPM state as used/limit", () => {
  const snap = buildSelfModelSnapshot({ tools: MOCK_TOOLS, rpmUsed: 22, rpmLimit: 40, pendingWrites: new Map() });
  assert.ok(snap.includes("22/40 used"), "must show RPM state");
});

test("snapshot shows 0 pending writes when map is empty", () => {
  const snap = buildSelfModelSnapshot({ tools: MOCK_TOOLS, rpmUsed: 0, rpmLimit: 40, pendingWrites: new Map() });
  assert.ok(snap.includes("Unapproved memory writes (this session): 0"));
});

test("snapshot lists pending writes with preview and write_id", () => {
  const pw = new Map();
  pw.set("wr_abc", { content: "redis-py function signatures for get/set/del", ts: Date.now() });
  const snap = buildSelfModelSnapshot({ tools: MOCK_TOOLS, rpmUsed: 0, rpmLimit: 40, pendingWrites: pw });
  assert.ok(snap.includes("Unapproved memory writes (this session): 1"));
  assert.ok(snap.includes("write_id: wr_abc"), "must show write_id");
  assert.ok(snap.includes("redis-py"), "must show content preview");
});

test("snapshot handles multiple pending writes", () => {
  const pw = new Map();
  pw.set("wr_1", { content: "first write content here", ts: Date.now() });
  pw.set("wr_2", { content: "second write content here", ts: Date.now() });
  const snap = buildSelfModelSnapshot({ tools: MOCK_TOOLS, rpmUsed: 5, rpmLimit: 40, pendingWrites: pw });
  assert.ok(snap.includes("Unapproved memory writes (this session): 2"));
});

test("snapshot content preview truncates at 60 chars", () => {
  const pw = new Map();
  pw.set("wr_long", { content: "x".repeat(100), ts: Date.now() });
  const snap = buildSelfModelSnapshot({ tools: MOCK_TOOLS, rpmUsed: 0, rpmLimit: 40, pendingWrites: pw });
  // Should have "..." after truncation
  assert.ok(snap.includes("..."), "long content must be truncated with ...");
});
```

**Step 2: Run test to verify it fails**

```
node --test hub-bridge/tests/test_self_model_snapshot.js
```
Expected: FAIL — function not defined

**Step 3: Add `buildSelfModelSnapshot()` to server.js**

In `hub-bridge/app/server.js`, add this function directly above `buildSystemText` (around line 423):

```js
/**
 * Build the Self-Model Kernel snapshot — dynamic per-request self-awareness block.
 * Pure observational data. Coaching on how to USE this data is in the system prompt.
 *
 * @param {object} opts
 * @param {Array}  opts.tools        - TOOL_DEFINITIONS array
 * @param {number} opts.rpmUsed      - Slots consumed in current 60s window
 * @param {number} opts.rpmLimit     - Configured RPM ceiling
 * @param {Map}    opts.pendingWrites - Current pending_writes Map
 * @returns {string}
 */
function buildSelfModelSnapshot({ tools, rpmUsed, rpmLimit, pendingWrites }) {
  const toolNames = tools.map(t => t.name).join(", ");

  const lines = [
    "--- SELF-MODEL SNAPSHOT ---",
    `Tools available: ${toolNames}`,
    `RPM state: ${rpmUsed}/${rpmLimit} used`,
  ];

  // Unapproved memory writes (in-process pending_writes Map, this session only)
  const writesArr = [...pendingWrites.entries()];
  if (writesArr.length > 0) {
    lines.push(`Unapproved memory writes (this session): ${writesArr.length}`);
    for (const [id, v] of writesArr) {
      const preview = (v.content || "").slice(0, 60);
      lines.push(`  - ${preview}... [write_id: ${id}]`);
    }
  } else {
    lines.push("Unapproved memory writes (this session): 0");
  }

  // Detected patterns from consciousness.jsonl — populated by Phase 2b
  // (empty until metacognitive traces + pattern detection are live)
  lines.push("Detected patterns: (none yet — Phase 2b)");

  lines.push("--- END SELF-MODEL SNAPSHOT ---");
  return lines.join("\n");
}
```

**Step 4: Run test to verify it passes**

```
node --test hub-bridge/tests/test_self_model_snapshot.js
```
Expected: 7 passing

**Step 5: Commit**

```bash
git add hub-bridge/app/server.js hub-bridge/tests/test_self_model_snapshot.js
git commit -m "feat(kernel): add buildSelfModelSnapshot() — Phase 1 Task 2"
```

---

## Task 3: Inject snapshot into `buildSystemText()`

Wire `buildSelfModelSnapshot()` into `buildSystemText()` as a new parameter, injected between `identityBlock` and the `karmaCtx` base text.

**Files:**
- Modify: `hub-bridge/app/server.js` (two changes: `buildSystemText` signature + call site)
- Modify: `hub-bridge/tests/test_system_text.js` (add snapshot injection tests)

**Step 1: Write the failing tests**

Add to the END of `hub-bridge/tests/test_system_text.js`:

```js
// ── Self-Model Snapshot injection ─────────────────────────────────────────────

// Extended buildSystemText that includes selfModel param (mirrors Task 3 change)
function buildSystemTextV2(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null, selfModelSnapshot = null) {
  const identityBlock = "IDENTITY\n\n---\n\n";
  const selfKnowledge = "[Self-knowledge: backbone=test]\n\n";
  const base = karmaCtx
    ? `You are Karma.\n\n${karmaCtx}\n\nMemory rules.`
    : "You are Karma. No memory context available.";

  let text = identityBlock + selfKnowledge;

  // Self-model snapshot injected AFTER identityBlock, BEFORE base karmaCtx
  if (selfModelSnapshot) {
    text += selfModelSnapshot + "\n\n";
  }

  text += base;
  if (semanticCtx) text += `\n\n${semanticCtx}`;
  if (webResults) text += `\n\n--- WEB SEARCH ---\n${webResults}\n---`;
  if (ckLatest?.karma_brief) text += `\n\n--- KARMA SELF-KNOWLEDGE ---\n${ckLatest.karma_brief}\n---`;
  if (karmaCtx) text += `\n\n=== YOUR COMPLETE KNOWLEDGE STATE ===\n${karmaCtx}\n=== END KNOWLEDGE STATE ===`;
  if (memoryMd) text += `\n\n--- KARMA MEMORY SPINE (recent) ---\n${memoryMd}\n---`;

  return text;
}

test("snapshot injected when selfModelSnapshot param provided", () => {
  const text = buildSystemTextV2("some ctx", null, null, null, null, "--- SELF-MODEL SNAPSHOT ---\nRPM state: 5/40 used\n---");
  assert.ok(text.includes("SELF-MODEL SNAPSHOT"), "must include snapshot");
  assert.ok(text.includes("5/40 used"), "must include RPM data");
});

test("snapshot NOT injected when selfModelSnapshot is null", () => {
  const text = buildSystemTextV2("some ctx", null, null, null, null, null);
  assert.ok(!text.includes("SELF-MODEL SNAPSHOT"), "null snapshot must not inject");
});

test("snapshot appears BEFORE knowledge state section", () => {
  const text = buildSystemTextV2("ctx", null, null, null, null, "--- SELF-MODEL SNAPSHOT ---\ndata\n---");
  const snapPos = text.indexOf("SELF-MODEL SNAPSHOT");
  const knowledgePos = text.indexOf("COMPLETE KNOWLEDGE STATE");
  assert.ok(snapPos > 0, "snapshot must exist");
  assert.ok(snapPos < knowledgePos, "snapshot must appear before knowledge state");
});

test("snapshot appears AFTER identity block", () => {
  const text = buildSystemTextV2("ctx", null, null, null, null, "--- SELF-MODEL SNAPSHOT ---\ndata\n---");
  const identityPos = text.indexOf("IDENTITY");
  const snapPos = text.indexOf("SELF-MODEL SNAPSHOT");
  assert.ok(identityPos >= 0, "identity block must exist");
  assert.ok(snapPos > identityPos, "snapshot must appear after identity block");
});
```

**Step 2: Run test to verify new tests fail**

```
node --test hub-bridge/tests/test_system_text.js
```
Expected: original 6 tests pass, 4 new tests fail

**Step 3: Update `buildSystemText` in server.js**

Change the function signature at line 424:
```js
// BEFORE:
function buildSystemText(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null) {

// AFTER:
function buildSystemText(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null, selfModelSnapshot = null) {
```

Inside the function, after `const identityBlock = ...` block (after line 430), add the snapshot injection:
```js
  // Self-Model Kernel snapshot — dynamic per-request self-awareness.
  // Injected after identityBlock, before karmaCtx base text.
  const snapshotBlock = selfModelSnapshot ? selfModelSnapshot + "\n\n" : "";
```

Change the `let text =` line (line 440) to include `snapshotBlock`:
```js
  // BEFORE:
  let text = identityBlock + selfKnowledge + base + "\n\nTools available...";

  // AFTER: insert snapshotBlock between selfKnowledge and base
  let text = identityBlock + selfKnowledge + snapshotBlock + base + "\n\nTools available...";
```

**Step 4: Update the call site in the /v1/chat handler**

Find line 1370 in server.js:
```js
// BEFORE:
const systemText = buildSystemText(karmaCtx, ckLatestData, webSearchResults, semanticCtx, _memoryMdCache || null);

// AFTER:
const { used: rpmUsed, limit: rpmLimit } = glmLimiter.rpmSnapshot();
const selfModelSnap = buildSelfModelSnapshot({
  tools: TOOL_DEFINITIONS,
  rpmUsed,
  rpmLimit,
  pendingWrites: pending_writes,
});
const systemText = buildSystemText(karmaCtx, ckLatestData, webSearchResults, semanticCtx, _memoryMdCache || null, selfModelSnap);
```

Also update the second `buildSystemText` call at line 1983 (used by the ingest/ambient route — pass null for snapshot, it's not a chat request):
```js
// BEFORE:
const systemText = buildSystemText(karmaCtx, null);

// AFTER:
const systemText = buildSystemText(karmaCtx, null, null, null, null, null);
```

**Step 5: Run all tests**

```
node --test hub-bridge/tests/
```
Expected: all tests pass (existing + 4 new)

**Step 6: Commit**

```bash
git add hub-bridge/app/server.js hub-bridge/tests/test_system_text.js
git commit -m "feat(kernel): inject buildSelfModelSnapshot into buildSystemText — Phase 1 Task 3"
```

---

## Task 4: Add `get_self_model` deep-mode tool

New hub-bridge-native tool. In deep mode, Karma can call `get_self_model()` to get a live snapshot query (same data as the injected snapshot, but computed at call time, not at request start).

**Files:**
- Modify: `hub-bridge/app/server.js` (two changes: TOOL_DEFINITIONS + executeToolCall handler)

No new test file needed — this is a tool handler. Test by deploying and calling via curl (acceptance test in Task 6).

**Step 1: Add tool definition to TOOL_DEFINITIONS**

In `hub-bridge/app/server.js`, add to the `TOOL_DEFINITIONS` array (after the `get_library_docs` entry, before the closing `]`):

```js
  {
    name: "get_self_model",
    description: "Get a live snapshot of your current self-model state: tools available, RPM used/limit, unapproved memory writes pending this session. Use in deep mode before making high-stakes claims about your own capabilities — verify the injected snapshot is current. Returns the same format as the SELF-MODEL SNAPSHOT in your system prompt.",
    input_schema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
```

**Step 2: Add handler in `executeToolCall`**

In `hub-bridge/app/server.js`, inside `executeToolCall`, add a new branch before the existing `if (toolName === "write_memory")` check (around line 891):

```js
    // get_self_model -- live re-query of self-model state (same as injected snapshot, computed on call)
    if (toolName === "get_self_model") {
      const { used: rpmUsed, limit: rpmLimit } = glmLimiter.rpmSnapshot();
      const snapshot = buildSelfModelSnapshot({
        tools: TOOL_DEFINITIONS,
        rpmUsed,
        rpmLimit,
        pendingWrites: pending_writes,
      });
      console.log("[TOOL-API] get_self_model called — snapshot computed");
      return { snapshot, note: "This is a live query computed at call time, not the snapshot injected at request start. Compare to detect drift." };
    }
```

**Step 3: Verify server.js syntax is valid**

```
node --check hub-bridge/app/server.js
```
Expected: no output (clean)

**Step 4: Commit**

```bash
git add hub-bridge/app/server.js
git commit -m "feat(kernel): add get_self_model deep-mode tool — Phase 1 Task 4"
```

---

## Task 5: System prompt coaching

Add threshold-based behavioral rules to `Memory/00-karma-system-prompt-live.md` so Karma knows what to do with the Self-Model Snapshot data.

**Files:**
- Modify: `Memory/00-karma-system-prompt-live.md`

**Step 1: Read current system prompt to find insertion point**

```
Read Memory/00-karma-system-prompt-live.md — find the "How to Use Your Context Data" section
(or equivalent coaching section — it was added in Session 67).
```

**Step 2: Add Self-Model Kernel coaching section**

In the coaching section, add after the existing tool-use guidance:

```markdown
## Self-Model Kernel — Reading Your Own State

Every response includes a `--- SELF-MODEL SNAPSHOT ---` block in your system prompt. This is not decorative — it's live data about your current state. Read it. Act on it.

**RPM state — threshold rules:**
- `RPM state: X/40 used` where X < 20: proceed normally, no mention needed
- X = 20–32 (50–80%): note inline if you're about to call multiple tools — "I'm at ~X RPM, using 2 slots here"
- X > 32 (>80%): surface the trade-off explicitly — "I'm at X/40 RPM. I can do this at [HIGH] (costs 2 slots) or [MEDIUM] (costs 0 slots). Your call."
- X = 40: self-throttle — skip optional tool calls, respond from context

**Unapproved memory writes:**
- If the snapshot shows pending writes, do NOT re-propose the same content. Check the snapshot before calling `write_memory`.
- If you're about to propose something similar to a pending write, note it: "I already proposed X — still waiting on approval."

**Detected patterns (populated in Phase 2b):**
- [LOW] pattern: internal awareness only, no behavior change
- [MEDIUM] pattern: note inline when the topic appears — "I've been uncertain on X recently"
- [HIGH] pattern: surface to Colby explicitly — "I've detected a consistent gap on X across N sessions. Flag for review?"

**`get_self_model()` tool:**
- Use in deep mode before making any [LOW] claim about your own capabilities (which tools you have, what you can access)
- Compare the live result to the injected snapshot — if they diverge, surface it
- Do NOT call on every response — only when self-knowledge accuracy matters
```

**Step 3: Verify character count hasn't exploded**

```bash
wc -c Memory/00-karma-system-prompt-live.md
```
Expected: reasonable increase (coaching section adds ~800 chars). If total > 18,000 chars, flag for trimming before deploy.

**Step 4: Commit**

```bash
git add Memory/00-karma-system-prompt-live.md
git commit -m "feat(kernel): add Self-Model Kernel coaching to system prompt — Phase 1 Task 5"
```

---

## Task 6: Deploy and acceptance test

Deploy all Phase 1 changes to vault-neo and verify end-to-end.

**Files:** No code changes — deploy + test only.

**Step 1: Push to GitHub**

```bash
git push origin main
```

**Step 2: Pull to vault-neo and sync build context**

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/lib/routing.js /opt/seed-vault/memory_v1/hub_bridge/lib/routing.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js"
ssh vault-neo "cp /home/neo/karma-sade/Memory/00-karma-system-prompt-live.md /opt/seed-vault/memory_v1/karma_identity_prompt/00-karma-system-prompt-live.md 2>/dev/null || true"
```

Note: system prompt is volume-mounted — `docker restart anr-hub-bridge` re-reads it without rebuild. Code changes (server.js, routing.js) require `--no-cache` rebuild.

**Step 3: Rebuild and deploy**

```bash
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d"
```

**Step 4: Verify startup**

Use the `karma-verify` skill, OR manually:
```bash
ssh vault-neo "docker logs anr-hub-bridge --tail=20"
```
Expected: `hub-bridge v2.11.0 listening on :PORT`, no `[CONFIG ERROR]`, no `SyntaxError`.

**Step 5: Acceptance test — snapshot appears in deep-mode response**

```bash
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "What tools do you have available right now?"}' | jq '.assistant_text' | head -20
```
Expected: response references tools from the snapshot, Karma mentions her own tool list accurately.

**Step 6: Acceptance test — `get_self_model` tool callable**

```bash
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "Call get_self_model and tell me exactly what RPM state you see."}' | jq '.assistant_text'
```
Expected: Karma calls `get_self_model`, returns snapshot content including `RPM state: X/40 used`.

**Step 7: Acceptance test — pending write appears in snapshot**

```bash
# First, trigger a write_memory proposal
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "Please write_memory: test pending write entry for snapshot verification"}' | jq '{write_id: .write_id, ok: .ok}'

# Then ask Karma about her pending writes
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "x-karma-deep: true" \
  -d '{"message": "What pending memory writes do you currently have?"}' | jq '.assistant_text'
```
Expected: second response mentions the pending write (showing snapshot is live and accurate).

**Step 8: Update STATE.md**

Add to STATE.md component table:
```
| **Self-Model Kernel (Phase 1)** | ✅ LIVE | buildSelfModelSnapshot() + get_self_model tool + system prompt coaching |
```

**Step 9: Commit STATE.md + session-end protocol update to CLAUDE.md**

Add to CLAUDE.md session-end checklist (step 1, after "save_observation"):
```
- Review pending write_memory requests: approve or reject before ending (unapproved writes lost at TTL)
```

```bash
git add .gsd/STATE.md CLAUDE.md MEMORY.md
git commit -m "docs: Phase 1 Self-Model Kernel deployed — update STATE.md + session-end protocol"
git push origin main
```

---

## Completion Criteria

Phase 1 is complete when:
- [ ] `node --test hub-bridge/tests/` — all tests pass (existing + new)
- [ ] `docker logs anr-hub-bridge` — clean startup, no errors
- [ ] Deep-mode response to "what tools do you have" accurately lists TOOL_DEFINITIONS names
- [ ] `get_self_model` tool returns live snapshot with correct RPM state
- [ ] Pending write appears in snapshot after `write_memory` proposal
- [ ] STATE.md updated with Phase 1 status
- [ ] CLAUDE.md session-end protocol updated

---

## Known Limitations (per design doc)

- `pending_writes` is in-process with TTL — not persisted across server restarts or session boundaries. Session-end checklist (added in Task 6) mitigates this.
- "Detected patterns" section returns placeholder until Phase 2b (metacognitive traces + pattern detection) is implemented.
- Claim calibration (`HIGH=N MEDIUM=N LOW=N`) is deferred to Phase 2 when traces exist to count from.
- `pending_intents` (Phase 4) not yet in snapshot.

---

*Plan authored: Session 77, 2026-03-10*
*Next phase: Phase 2 — Metacognitive Trace (capture_trace tool)*
