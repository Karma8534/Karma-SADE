# Design: Claude Primary + K2 Memory Substrate + Prompt Caching

**Date:** 2026-03-11
**Status:** Approved — implementing this session
**Session:** 84

---

## Problem

Session 83 made K2/qwen3-coder:30b the primary chat model to unlock tool calling in standard mode. This was the wrong fix:
- qwen3-coder:30b is a code model, not a conversation model — identity bleeds, slow, XML tool call bugs
- The real problem was tools gated behind deep_mode flag, not the wrong model
- Claude (Haiku/Sonnet) is the peer-quality model; K2 is the memory substrate

## Solution

Restore Claude as the mouth. Fix the tool gate. Add prompt caching. Wire K2 as memory resource.

---

## Architecture

```
USER MESSAGE
    ↓
hub-bridge → Claude Haiku (standard) or Sonnet (Deep button)
                 ↓ tools always available in BOTH modes
           ┌─────┴──────────────────────────────────────┐
           │  graph_query     → FalkorDB (free, local)  │
           │  get_vault_file  → vault-api (free)        │
           │  aria_local_call → K2/Aria (free, local)   │ ← K2's real job
           │  fetch_url, write_memory, list_local_dir   │
           └────────────────────────────────────────────┘
    ↓
RESPONSE (system prompt cached = 90% cheaper after first call)
```

K2/qwen3-coder:30b sits behind `aria_local_call`. Karma reaches into it for persistent memory. Not the voice.

---

## Changes

### 1. Routing — One Path, No Tool Gate

**Before (Session 83 — wrong):**
```js
const llmResult = await callWithK2Fallback(model, messages, max_output_tokens, deep_mode, req_write_id, ariaSessionId);
```

**After:**
```js
const llmResult = await callLLMWithTools(model, messages, max_output_tokens, req_write_id, ariaSessionId);
```

- `callWithK2Fallback` removed as primary routing path
- `callLLMWithTools` handles both standard and deep mode (model differs, capability identical)
- Deep button = model swap (Haiku ↔ Sonnet) only, NOT a capability gate
- `callK2WithTools` retained as internal fallback only

### 2. Prompt Caching

Add `cache_control: {type: "ephemeral"}` to system message in all Anthropic SDK calls.

```js
system: [{ type: "text", text: systemPrompt, cache_control: { type: "ephemeral" } }]
```

Cost impact: system prompt (~5,000 tokens) cached at 10% cost after first call per session.
Estimated savings: ~80% reduction on system prompt tokens → ~$3-4/month total at normal usage.

### 3. buildSystemText Pruning

Safe cuts only — nothing that caused identity drift before:

| Section | Before | After | Saving |
|---------|--------|-------|--------|
| Duplicate governance block | ~500 tokens | removed | ~500t |
| MEMORY.md tail | 3,000 chars | 800 chars | ~550t |
| FAISS results | top-5 | top-3 | ~400t |
| karmaCtx Recurring Topics | ~200 tokens | removed | ~200t |
| **Total** | | | **~1,650t saved/req** |

**NOT cut:** identity block, tool list + format, User Identity, Relevant Knowledge, Recent Memories, k2MemCtx

### 4. K2 Awareness in System Prompt

New section added to `00-karma-system-prompt-live.md`:

```
K2 Memory:
K2 is your local memory coprocessor (Aria). It has persistent memory of all past
conversations, decisions, and context — beyond what fits in your current window.

When to use aria_local_call:
- User references something not in current context ("do you remember when...")
- You need past context about a project, decision, or conversation
- You're unsure about Colby's history, preferences, or past work
- You want to check what was decided/built in a previous session

How: aria_local_call(mode="chat", message="what do you know about X?")
K2 responds with synthesized memory. Use it, then answer Colby directly.
Do NOT guess when K2 can tell you.
```

### 5. Deep Mode Redefined

- Deep button in UI: unchanged visually
- Effect: swaps model from Haiku → Sonnet for that message
- No tool gating, no capability difference
- Karma can suggest: "This might benefit from deep mode" when appropriate
- `deep_mode` tag preserved in ledger entries for tracking

---

## Cost Model

| Scenario | Monthly estimate |
|----------|-----------------|
| 50 msgs/day, Haiku + caching | ~$3/month |
| Occasional Sonnet deep | +$2-4/month |
| Tool execution (K2/vault) | $0 |
| **Total** | **~$5-7/month** |

---

## Files Changed

| File | Change |
|------|--------|
| `hub-bridge/app/server.js` | Routing fix, prompt caching, buildSystemText pruning |
| `Memory/00-karma-system-prompt-live.md` | K2 awareness section, tool gate text removed, architecture updated |

## Files NOT Changed

- `hub-bridge/config/hub.env` — MODEL_DEFAULT/DEEP/K2_OLLAMA_URL unchanged
- `anr-vault-search/search_service.py` — already fixed Session 83
- `karma-core/` — unchanged
- TOOL_DEFINITIONS — unchanged
