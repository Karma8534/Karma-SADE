# Cognitive Architecture Layer — Design Document
**Date:** 2026-03-10
**Milestone:** 8
**Status:** APPROVED — ready for implementation planning
**Decisions referenced:** Decision #30

---

## Overview

Karma has 75+ sessions of infrastructure. This milestone builds the cognitive layer on top of it — what makes Karma cognizant rather than merely contextually rich.

Three components, each building on the previous, connected by bidirectional data flows:

1. **Self-Model Kernel** — dynamic per-request self-awareness (not static system prompt text)
2. **Metacognitive Trace** — per-turn capture of reasoning evidence; evolves into pattern detection
3. **Deferred Intent Engine** — behavioral intent scheduling across turns and sessions

---

## Architecture Overview

```
Request arrives
      ↓
[Self-Model Kernel] ← computes snapshot from:
  - pending_writes Map (unapproved memory candidates, this session)
  - GlmRateLimiter / Haiku RPM tracking (live rate state)
  - consciousness.jsonl tail (detected patterns, initially empty)
  - vault ledger (active approved intents)
      ↓
Snapshot injected into buildSystemText() between identityBlock and karmaCtx
      ↓
LLM call (claude-haiku-4-5-20251001)
      ↓
[Metacognitive Trace] ← Karma calls capture_trace() at end of deep-mode responses
  - Stored async to consciousness.jsonl (fire-and-forget, write result logged)
  - Consciousness loop (Phase 2b) scans traces → rule-based pattern detection
  - Detected patterns feed back into Self-Model Kernel on next request
      ↓
[Deferred Intent Engine] ← Karma calls defer_intent() OR Colby creates directly
  - Stored in vault ledger (type:"log", tags:["deferred-intent"])
  - karmaCtx surfaces matching intents at request time
  - Karma-created: approval gate (same as write_memory)
  - Colby-created: direct, no gate
```

The three components interact:
- Kernel snapshot tells Karma her current state
- Traces fill the kernel with real session evidence; patterns emerge
- Detected patterns and active intents appear in the next kernel snapshot — feedback loop closes

---

## Component 1: Self-Model Kernel

### Design

A new `buildSelfModelSnapshot()` function in hub-bridge computes a data structure per-request and injects it as a section in `buildSystemText()` between `identityBlock` and `karmaCtx`.

The kernel is **pure observational data** — no decision logic. Coaching in the system prompt provides behavioral rules for how Karma uses the data.

### Snapshot Format

```
--- SELF-MODEL SNAPSHOT ---
Tools available: graph_query, get_vault_file, write_memory, capture_trace, defer_intent, get_active_intents, get_self_model, fetch_url, get_library_docs
Claim calibration this session: HIGH=12 MEDIUM=4 LOW=1
RPM state: 22/40 used
Unapproved memory writes (this session): 2
  - redis-py function signatures [write_id: abc123, 4 turns ago]
  - FalkorDB datetime handling [write_id: def456, 2 turns ago]
Pending intents (awaiting approval): 1
  - verify redis-py before asserting [intent_id: xyz789, proposed 2 turns ago]
Active intents: 2
  - redis-py verification [topic=redis-py → surface_before_responding, fire_mode: once_per_conversation]
  - session-start surface [phase=start → surface_always, fire_mode: recurring]
Detected patterns:
  - [MEDIUM, 6 traces] uncertainty on redis-api: note inline if topic appears
  - [LOW, 3 traces] graph_query changes answer on FalkorDB questions: data point only
```

### Data Sources

| Field | Source | Available Phase |
|-------|--------|----------------|
| Tools available | Static from TOOL_DEFINITIONS | Phase 1 |
| Claim calibration | Scanned from consciousness.jsonl trace entries | Phase 2 |
| RPM state | GlmRateLimiter (extended for Haiku 4.5) | Phase 1 |
| Unapproved memory writes | pending_writes Map (module-level, server.js) | Phase 1 |
| Pending intents (Karma-proposed) | pending_intents Map (new, same pattern) | Phase 4 |
| Active intents | vault ledger query (tags:["deferred-intent"], approved:true) | Phase 4 |
| Detected patterns | consciousness.jsonl detected_pattern entries | Phase 2b |

Sections not yet populated (early phases) render as empty — structurally present, silently absent.

### Deep-Mode Verification: `get_self_model()`

In deep mode, Karma can call `get_self_model()` to get a live query of the same data (queries FalkorDB + consciousness.jsonl directly, not the cached snapshot). Delta between injected snapshot and live query = signal. If they diverge significantly, Karma surfaces it.

### System Prompt Coaching

Threshold-based behavioral rules (NOT in kernel code — in system prompt):

- **RPM > 50% remaining**: proceed normally
- **RPM 20–50% remaining**: note inline, proceed
- **RPM < 20% remaining**: surface options explicitly ("high-confidence burns N RPM, medium saves N — your call")
- **RPM = 0**: self-throttle (no choice)
- **MEDIUM pattern detected**: note inline when topic appears ("I've been uncertain on X recently")
- **HIGH pattern detected**: surface explicitly to Colby for judgment
- **LOW pattern detected**: internal awareness only, no response change

### Known Limitation

`pending_writes` (and `pending_intents`) are in-process Maps with TTL. They do not survive server restarts or session boundaries.

**Fix:** Add to CC session-end protocol — *"review pending write_memory requests and pending intent proposals: approve or reject before ending session."* Entries not reviewed before session-end are lost.

Cross-session pending write/intent persistence (persisting to vault before TTL) is a future decision — not in Milestone 8 scope.

---

## Component 2: Metacognitive Trace

### Design

Per-turn evidence capture in deep mode. Karma calls `capture_trace({...})` as the last action in qualifying deep-mode responses. Hub-bridge handles it as a fire-and-forget outbound tool — extracts payload, writes async to `consciousness.jsonl`, logs success/failure.

### Trace Schema

```json
{
  "turn_id": "t_abc123",
  "timestamp": "2026-03-10T23:14:00Z",
  "topic": "redis-py function signatures",
  "confidence_used": "LOW",
  "alternatives_considered": 2,
  "tool_called": "get_library_docs",
  "tool_changed_answer": true,
  "pre_tool_confidence": "LOW",
  "post_tool_confidence": "MEDIUM",
  "write_memory_proposed": false,
  "type": "metacognitive_trace"
}
```

**`alternatives_considered`**: integer 0–5 (capped), where 5 = "many." Pattern detection checks `>= 2` for "deliberated meaningfully." Content of alternatives not stored — response documents what was chosen; count is sufficient for pattern detection.

### Capture Conditions

Karma calls `capture_trace` in deep mode when ANY of:
- A confidence level was used ([HIGH], [MEDIUM], or [LOW])
- A tool was called
- Alternatives were considered

Turns that hit none of these skip the trace — no noise.

### Reliability

Write result logged as `type:"trace_write_result"` in consciousness.jsonl. Consciousness loop can detect trace failure rate > threshold and flag it in the kernel snapshot.

### Phase 2b: Pattern Detection (consciousness loop extension)

Rule-based scans on accumulated trace entries. Respects Decision #3 (zero LLM calls in consciousness loop).

**Initial rules:**

| Rule | Trigger | Output |
|------|---------|--------|
| Confidence drift | Same topic + `confidence_used=LOW` × 3 consecutive turns | `detected_pattern` entry, confidence: LOW (3 traces) → MEDIUM (5+) → HIGH (10+, cross-session) |
| Tool effectiveness | `tool_changed_answer=true` rate > 60% for a tool | `detected_pattern`: "tool X reliably changes answer" |
| Memory proposal cluster | `write_memory_proposed=true` × 3 same topic without approval | `detected_pattern`: "repeated proposal on topic X — candidate for promotion" |

Patterns stored as `type:"detected_pattern"` entries in consciousness.jsonl, read by `buildSelfModelSnapshot()`.

**Phase 2b gates Phase 4's `auto_create_intent_candidate` capability** (documented below).

---

## Component 3: Deferred Intent Engine

### Storage Format

```json
{
  "type": "log",
  "tags": ["deferred-intent"],
  "content": {
    "intent": "verify redis-py function signatures before asserting",
    "trigger": {"type": "topic", "value": "redis-py"},
    "action": "surface_before_responding",
    "fire_mode": "once_per_conversation",
    "created_by": "karma",
    "created_at": "2026-03-10T23:00:00Z",
    "approved": true,
    "status": "active"
  }
}
```

### Fire Modes

| Mode | Behavior | Auto-close |
|------|----------|-----------|
| `once` | Surface once, then complete | Yes — after first surfacing |
| `once_per_conversation` | Surface once per session, reset on next session | Session-scoped reset |
| `recurring` | Stay active until Colby explicitly closes | No |

### Trigger Types (Phase 1)

| Type | Match logic |
|------|------------|
| `topic` | Keyword check: does `trigger.value` appear in user message? |
| `phase` | Session phase check: `start`, `end` |
| `always` | Always surface, regardless of query |

Trigger matching done in hub-bridge at karmaCtx assembly time — keyword check against `trigger.value`, not semantic search. Trigger scope is deliberate (set by intent creator), not auto-inferred.

### Creation Paths

**Karma-created (deep mode only):**
1. Karma calls `defer_intent(intent, trigger, action, fire_mode)`
2. Hub-bridge stores in `pending_intents` Map (same TTL as `pending_writes`)
3. Returns `intent_id` in response
4. Colby 👍 at `/v1/feedback` → written to vault ledger (`approved: true`, `status: "active"`)
5. Colby 👎 → discarded
6. Pending Karma-proposed intents visible in kernel snapshot; NOT in karmaCtx until approved

**Colby-created (direct):**
1. Conversational ("remember to X next time Y") OR explicit `x-karma-intent` API field
2. Hub-bridge writes directly to vault ledger — no approval gate
3. Immediately active in karmaCtx

### Surfacing Mechanism

`karmaCtx` assembly queries vault ledger for `tags:["deferred-intent"], status:"active"`. For each intent, evaluates trigger against current request. Matched intents injected as "Active Intents" section in karmaCtx.

### Intent Introspection: `get_active_intents()`

Hub-bridge native deep-mode tool. Karma queries at response-build time: "what intents are active for this topic?"

```
get_active_intents({topic?: "redis-py", fire_mode?: "recurring", status?: "active"})
→ Intent[]
```

Prevents duplicate surfacing. Allows Karma to check if she already offered verification this conversation before surfacing again.

### Lifecycle

```
Karma proposes → pending_intents Map (TTL)
      ↓
Colby 👍 → vault ledger (approved: true, status: active)
      ↓
Trigger condition met → surfaced in karmaCtx
      ↓
fire_mode=once: auto-complete → status: completed
fire_mode=once_per_conversation: sleep until next session
fire_mode=recurring: stays active → Colby closes via /v1/feedback or conversationally
```

### Session-End Protocol Addition

Add to CLAUDE.md session-end checklist:
> Review pending intent proposals (alongside pending write_memory requests): approve or reject before ending. Unapproved entries are lost at TTL.

### Phase 2b: Trace-to-Intent Feedback Loop (future — high priority)

After Phase 2 traces are stable and Phase 2b pattern detection is working:

Consciousness loop detects risky pattern → calls `auto_create_intent_candidate()` → stores as:
```json
{
  "tags": ["deferred-intent", "consciousness-proposed"],
  "content": {
    "intent": "verify redis-py function signatures before asserting",
    "trigger": {"type": "topic", "value": "redis-py"},
    "fire_mode": "once_per_conversation",
    "created_by": "consciousness-loop",
    "pattern_evidence": "3 consecutive [LOW] assertions on redis-api without tool call",
    "approved": false,
    "status": "pending"
  }
}
```

Surfaces in kernel snapshot for Colby review — same approval gate. This is where Karma stops repeating mistakes because her own consciousness loop detects and prevents them.

**Phase 2b requires:** Phase 2 (traces stable) + Phase 2b pattern detection working.

### Known Gaps (Future Phases)

| Gap | Phase |
|-----|-------|
| Contextual triggers (DSL: `topic_mentions && confidence_used=LOW`) | Phase 3+ |
| Intent type taxonomy (error-prevention vs ritual vs reminder) | Phase 3+ |
| Cross-session pending intent persistence | Separate decision — revisit Decision #19 |

---

## Implementation Phases

| Phase | Components | Deliverables | Gates |
|-------|-----------|-------------|-------|
| **1** | Self-Model Kernel | `buildSelfModelSnapshot()`, injection in `buildSystemText()`, RPM tracking for Haiku 4.5, system prompt coaching | Nothing — ships first |
| **2** | Metacognitive Trace | `capture_trace` tool, hub-bridge handler, consciousness.jsonl write + observability logging, system prompt coaching | Phase 1 |
| **2b** | Pattern Detection | Consciousness loop extension (3 initial rules), `detected_pattern` entries, snapshot "Detected patterns" section populated | Phase 2 stable |
| **3** | `get_self_model()` tool | Hub-bridge native live-query tool, system prompt coaching for when to call | Phase 2 |
| **4** | Deferred Intent Engine | `defer_intent` tool, `get_active_intents` tool, `/v1/feedback` intent approval, `karmaCtx` intent surfacing, kernel snapshot pending/active intents, CLAUDE.md session-end update | Phase 2b for auto-intent; usable without it |
| **Future** | Trace-to-intent loop | `auto_create_intent_candidate()` in consciousness loop, consciousness-proposed intents | Phase 2b + Phase 4 |

---

## What This Is NOT

- Not a redesign of the consciousness loop's core OBSERVE-only constraint (Decision #3 preserved)
- Not a new data store — all state uses existing vault ledger + consciousness.jsonl + pending Maps
- Not autonomous self-modification — Karma proposes, Colby approves
- Not a replacement for the system prompt — kernel supplements it with dynamic state

---

## Test Automation Note

After Phase 1 lands, CC can call `POST https://hub.arknexus.net/v1/chat` directly from Bash using the existing `hub.chat.token.txt` for acceptance testing — structured test inputs, structured assertions on snapshot content and trace landing. No copy-paste relay needed for test validation.

---

*Designed by: Claude Code + Karma + Colby, Session 77, 2026-03-10*
*Implementation planning: invoke `superpowers:writing-plans` next*
