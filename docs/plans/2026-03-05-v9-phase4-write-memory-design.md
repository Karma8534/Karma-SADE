# v9 Phase 4 — Karma Write Agency Design
**Date:** 2026-03-05
**Status:** APPROVED — ready for implementation planning
**Session:** 68

---

## Problem

Karma can read her own memory (via `get_vault_file`) and query her graph (via `graph_query`), but cannot write anything back. Every insight she surfaces dies at session end. Phase 4 gives Karma a gated write path: she can propose a memory write, and Colby approves or rejects it via thumbs up/down. The gate simultaneously accumulates DPO preference pairs for future fine-tuning.

---

## Decisions Locked In

- **Tool scope:** `write_memory` only (Phase 4). `annotate_entity` and `flag_pattern` deferred.
- **Optional note:** UI adds inline textarea after 👎 — user can specify what Karma should have said.
- **DPO storage:** Append to `memory.jsonl` via `/v1/ambient` with `dpo-pair` tag. Zero new infrastructure.
- **Gate mechanism:** In-process `pending_writes` Map (Approach A). No vault round-trip. Acceptable failure mode: hub-bridge restart clears pending writes (30-second window).

---

## Architecture & Data Flow

```
[deep-mode /v1/chat]
  Karma calls write_memory(content)
        │
        ▼
  hub-bridge intercepts tool call
  → stores {turn_id, content, timestamp} in pending_writes Map
  → returns tool result: "Memory write proposed. Awaiting your approval."
  → LLM generates final response referencing the proposed write
        │
        ▼
  /v1/chat response includes assistant_text + canonical.turn_id (unchanged)
  UI renders Karma's message + 👍👎 buttons (already wired in unified.html)
        │
    ┌───┴───┐
    │       │
   👍       👎
    │       │
    │   inline textarea appears below bubble
    │   "What should Karma have said? (optional)"
    │       │
    ▼       ▼
POST /v1/feedback {turn_id, signal, note?}
    │       │
    │       ├─ note present → append to corrections-log.md
    │       └─ always → write DPO pair to ledger (tag: dpo-pair)
    │
    ├─ 👍 → PATCH /v1/vault-file/MEMORY.md {append: note || content}
    └─ 👎 → discard pending_writes[turn_id]
```

**Pending write TTL:** Entries older than 30 minutes pruned lazily on next `/v1/feedback` call.

---

## Component Specs

### 1. `write_memory` Tool (hub-bridge server.js)

**Tool definition** (alongside `graph_query`, `get_vault_file`):
```js
{
  name: "write_memory",
  description: "Propose a memory write to MEMORY.md. Requires user approval via thumbs up before the write executes.",
  parameters: {
    type: "object",
    properties: {
      content: { type: "string", description: "Concise note to append to MEMORY.md" }
    },
    required: ["content"]
  }
}
```

**In `executeToolCall()`:**
```js
case "write_memory": {
  const { content } = args;
  pending_writes.set(turn_id, { content, ts: Date.now() });
  return { proposed: true, message: "Memory write proposed. Awaiting your approval via 👍." };
}
```

**`pending_writes` declaration** (module-level, alongside existing Maps):
```js
const pending_writes = new Map(); // turn_id → { content, ts }
```

**hooks.py:** Add `"write_memory"` to `ALLOWED_TOOLS` set.

---

### 2. POST `/v1/feedback` Endpoint (hub-bridge server.js)

**Request:** `{ turn_id: string, signal: "up"|"down", note?: string }`

**Response:** `{ ok: true }` (always — don't surface errors to UI)

**Logic:**
```
1. Auth check (HUB_CHAT_TOKEN)
2. Prune pending_writes entries older than 30min
3. Look up pending = pending_writes.get(turn_id)
4. Determine write_content = note (if present) || pending?.content || null

if signal === "up":
  - if write_content: PATCH /v1/vault-file/MEMORY.md {append: write_content}
  - store DPO pair: {type:"dpo-pair", signal:"up", proposed: pending?.content, preferred: write_content, turn_id, ts}
  - pending_writes.delete(turn_id)

if signal === "down":
  - if note: append to corrections-log.md
  - store DPO pair: {type:"dpo-pair", signal:"down", proposed: pending?.content, preferred: note||null, turn_id, ts}
  - pending_writes.delete(turn_id)

5. Write DPO pair to ledger via POST to vault /v1/memory:
   { tags: ["dpo-pair"], content: JSON.stringify(dpo_pair), source: "feedback" }
```

**DPO pair ledger format:**
```json
{
  "type": "dpo-pair",
  "tags": ["dpo-pair"],
  "turn_id": "chatlog_...",
  "signal": "up",
  "proposed": "Colby prefers dark mode in all tools",
  "preferred": "Colby prefers dark mode in all tools",
  "ts": "2026-03-05T20:00:00Z"
}
```

---

### 3. UI Changes (unified.html, ~15 lines)

**After 👎 click** — inject feedback note div below the message bubble:
```html
<div class="feedback-note" id="fn-{turnId}">
  <textarea placeholder="What should Karma have said? (optional)" rows="2"></textarea>
  <button>Submit</button>
</div>
```

**Submit behavior:** Sends `{ turn_id, signal: "down", note: textarea.value || undefined }`, collapses the div.

**👍 behavior:** Unchanged — sends immediately with no textarea.

**CSS addition** (~4 lines): style `.feedback-note` inline, collapsed by default.

---

### 4. System Prompt Coaching (Memory/00-karma-system-prompt-live.md)

One paragraph appended to the "How to Use Your Context Data" section:

> **Memory writes:** In deep-mode conversations, when you learn something worth remembering — a preference, a correction, a new fact about Colby or the system — call `write_memory(content)` with a concise note. The write requires Colby's approval before executing. Do not call it every turn; use it when you would genuinely want this fact available in the next session. Good triggers: explicit preferences stated by Colby, corrections to something you got wrong, facts about the project that aren't in MEMORY.md yet.

**Deploy:** git pull + `docker restart anr-hub-bridge` only (no rebuild needed — KARMA_IDENTITY_PROMPT is file-loaded).

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| `turn_id` not in pending_writes | `/v1/feedback` still stores DPO pair (signal without write), returns `ok:true` |
| MEMORY.md write fails | Log error, return `ok:true` to UI (don't expose filesystem errors) |
| Ledger write fails | Log warning, return `ok:true` — feedback signal not critical path |
| Hub-bridge restart clears pending_writes | Pending write lost. 👍 click stores DPO pair with `proposed: null`. Acceptable. |
| No note on 👎 | DPO pair stored with `preferred: null` — valid incomplete pair, still useful signal |

---

## Testing

**Acceptance tests (manual):**
1. Send a deep-mode message → Karma calls write_memory → response includes proposed write text
2. Click 👍 → MEMORY.md contains the appended note → ledger has `dpo-pair` entry with `signal:"up"`
3. Click 👎 with note → MEMORY.md unchanged → ledger has `dpo-pair` with `signal:"down"` + `preferred` text → corrections-log.md updated
4. Click 👎 without note → MEMORY.md unchanged → ledger has `dpo-pair` with `preferred: null`
5. Standard (non-deep) chat → write_memory NOT in tool list → Karma cannot propose writes

**Unit-testable:** `/v1/feedback` routing logic, pending_writes TTL cleanup, DPO pair format.

---

## What This Is NOT

- Not a FalkorDB write (MEMORY.md only — graph writes are Phase 5)
- Not autonomous (every write requires explicit 👍)
- Not a training pipeline (accumulating pairs toward 20-pair threshold; actual training is separate)
- Not `annotate_entity` or `flag_pattern` (deferred)

---

## Files Changed

| File | Change |
|------|--------|
| `hub-bridge/app/server.js` | Add `pending_writes` Map, `write_memory` tool, `/v1/feedback` endpoint |
| `hub-bridge/app/public/unified.html` | Add feedback-note textarea after 👎 click |
| `karma-core/hooks.py` | Add `"write_memory"` to `ALLOWED_TOOLS` |
| `Memory/00-karma-system-prompt-live.md` | Add write_memory coaching paragraph |

**Deploy order:** karma-server rebuild (hooks.py) → hub-bridge rebuild (server.js) → git pull + docker restart (system prompt) → UI live immediately (static file).
