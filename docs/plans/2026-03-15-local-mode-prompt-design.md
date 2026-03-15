# Local-Mode Prompt Design — K2 Ollama Activation

**Date:** 2026-03-15
**Status:** PROMPT CREATED, INTEGRATION PENDING
**Author:** CC (Ascendant)

## Problem

Current Karma system prompt is 33,994 chars. K2's qwen3:8b (8GB VRAM) cannot handle this — inference is too slow and context overflows the model's effective window. This blocks K2 Ollama from serving as a cost-reduction layer for simple conversations.

## Solution

Static reduced prompt: `Memory/00-karma-local-prompt.md` (2,984 chars, ~750 tokens).

### What's Kept
- Core identity (who Karma is, not a stateless assistant)
- About Colby (personality preferences, decision style)
- Behavioral contract (6 rules, peer-level voice)
- Family hierarchy table
- Improvement pipeline (ASSIMILATE/DEFER/DISCARD)

### What's Dropped (30K chars removed)
- K2 compute substrate instructions (K2 IS the local mode — no self-reference needed)
- Kiki autonomous body (loop instructions irrelevant in chat context)
- State-write triggers (no tool-calling in local mode)
- Tool documentation (no tools available in local mode)
- Memory architecture internals (how hub-bridge works — model doesn't need this)
- Self-audit protocol (too complex for 8B model)
- Data model corrections (specific to tool-calling scenarios)
- Confidence levels (simplified to "say I don't know")
- Deferred intent engine (requires tool-calling)
- Current system state table (stale quickly, not needed for chat)

## Integration Plan (hub-bridge changes)

### 1. Load local prompt at startup
```javascript
// In server.js, alongside KARMA_IDENTITY_PROMPT loading
const KARMA_LOCAL_PROMPT = (() => {
  try {
    return fs.readFileSync('/karma/repo/Memory/00-karma-local-prompt.md', 'utf8');
  } catch (e) {
    console.warn('[WARN] Local prompt not found, K2 routing will use full prompt');
    return null;
  }
})();
```

### 2. buildLocalSystemText() function
```javascript
function buildLocalSystemText(memoryMd) {
  // Local mode: reduced prompt + tail of MEMORY.md only
  // No karmaCtx, no semanticCtx, no web results (too large for 8B model)
  const parts = [KARMA_LOCAL_PROMPT || KARMA_IDENTITY_PROMPT];
  if (memoryMd) {
    parts.push('\n---\n## Recent Memory\n' + memoryMd.slice(-1500));
  }
  return parts.join('\n');
}
```

### 3. Route selection at line ~2548
```javascript
// When callWithK2Fallback is wired as primary:
// - Simple messages → K2 Ollama with buildLocalSystemText()
// - Deep mode / complex → Anthropic with full buildSystemText()
const isSimple = !deep_mode && messageLength < 500;
if (isSimple && K2_OLLAMA_URL && KARMA_LOCAL_PROMPT) {
  systemText = buildLocalSystemText(_memoryMdCache);
  // route to K2 Ollama
} else {
  systemText = buildSystemText(karmaCtx, ckLatest, webResults, semanticCtx, memoryMd);
  // route to Anthropic
}
```

### 4. Simplicity heuristic
Simple = not deep mode AND message < 500 chars AND no tool-triggering keywords (file, code, graph, deploy, build).

## Cost Impact

- Simple conversations (~40% of traffic): $0 (K2 local)
- Complex/deep conversations: unchanged (Anthropic)
- Estimated monthly savings: ~$12-15 of $60 cap (20-25% reduction)

## Blocked By

- K2 hardware: qwen3:8b on 8GB VRAM is marginal. K2 upgrade (RTX 3060 12GB + 32GB RAM) would enable qwen3:30b which handles this prompt comfortably.
- Until upgrade: local routing should be conservative (only very simple messages).

## Files

- `Memory/00-karma-local-prompt.md` — the local-mode prompt (2,984 chars) ✅ CREATED
- `hub-bridge/app/server.js` — integration points (lines ~50, ~400, ~2548) — PENDING
