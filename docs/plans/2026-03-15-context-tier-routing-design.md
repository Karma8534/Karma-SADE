# Context Tier Routing — Reduce /v1/chat Input Cost

**Date:** 2026-03-15
**Status:** DESIGN APPROVED (autonomous evolution directive)
**Author:** CC (Ascendant)

## Problem

Every `/v1/chat` request injects ~47K chars of context regardless of message complexity.
A simple "How are you?" gets the same 34K identity prompt + 6K kiki state + 2K coordination
+ 2K MEMORY.md + semantic search + checkpoint data as a complex architecture question.

At $0.80/M input tokens, this costs ~$0.01 per simple message. With ~40% of traffic being
simple conversational messages, this wastes ~$8-10/month of the $60 cap.

## Solution

Three-tier context routing based on message length + keyword detection.

### Tier Classification

```
classifyMessageTier(userMessage, deepMode):
  if deepMode → return 3
  if msg.length > 500 → return 3

  TIER3_KEYWORDS = [deep, analyze, architecture, design, "explain in detail"]
  if any TIER3_KEYWORDS in msg → return 3

  TIER2_KEYWORDS = [kiki, codex, k2, deploy, build, code, file, graph,
                    debug, fix, bug, test, checkpoint, phase, plan,
                    remember, memory, forget]
  if any TIER2_KEYWORDS in msg → return 2
  if msg.length >= 100 → return 2

  return 1
```

### Context Per Tier

| Component | Tier 1 (LIGHT) | Tier 2 (STANDARD) | Tier 3 (DEEP) |
|---|---|---|---|
| Identity prompt | Local (3K) | Standard (10K) | Full (34K) |
| karmaCtx | Yes (1.2K) | Yes (1.2K) | Yes (1.2K) |
| semanticCtx | No | Yes (1.2K) | Yes (1.2K) |
| memoryMd | Yes (2K) | Yes (2K) | Yes (2K) |
| k2WorkingMemCtx | No | Conditional* (6K) | Yes (6K) |
| k2MemCtx | No | No | Yes |
| coordinationCtx | No | Conditional** (2K) | Yes (2K) |
| ckLatest | No | No | Yes |
| webResults | No | If search intent | Yes |
| activeIntents | No | Yes | Yes |
| statePrelude | No | No | Yes |
| **Total (max)** | **~6.2K** | **~23.4K** | **~47K+** |

*k2WorkingMemCtx included if message contains kiki/k2/codex keywords
**coordinationCtx included if message contains agent name keywords

### New Asset: Standard Identity Prompt

File: `Memory/01-karma-standard-prompt.md` (~10K chars)

Derived from full 34K prompt. Keeps:
- Core identity block (who Karma is)
- About Colby (preferences, decision style, location)
- Behavioral contract (6 rules)
- Family hierarchy table
- Tool documentation (deep-mode tools list)
- Key behavioral rules (honesty, memory writes, uncertainty handling)

Drops (~24K):
- Architecture internals (data model schema, consciousness loop)
- K2 compute substrate documentation
- Self-audit protocol (too complex for standard mode)
- Deferred intent engine details
- Capture source tables
- FalkorDB schema documentation
- State-write trigger specifications

The local-mode prompt (`Memory/00-karma-local-prompt.md`, 3K) already exists for K2 Ollama.

### Implementation Changes (server.js only)

1. **Load prompts at startup:**
```javascript
const KARMA_LOCAL_PROMPT = loadFileOrNull('/karma/repo/Memory/00-karma-local-prompt.md');
const KARMA_STANDARD_PROMPT = loadFileOrNull('/karma/repo/Memory/01-karma-standard-prompt.md');
// KARMA_IDENTITY_PROMPT already exists (full 34K)
```

2. **New function: `classifyMessageTier(msg, deepMode)`** — returns 1, 2, or 3.

3. **New function: `getIdentityForTier(tier)`** — returns local/standard/full prompt with fallback chain.

4. **Modified: `buildSystemText()`** — gains `tier` param. Each context section is gated:
```javascript
if (tier >= 2 && semanticCtx) { text += semanticCtx; }
if (tier >= 3 && k2WorkingMemCtx) { text += k2WorkingMemCtx; }
// etc.
```

5. **Modified: `/v1/chat` handler** — calls `classifyMessageTier()`, passes tier to `buildSystemText()`, skips unnecessary `Promise.all` fetches for lower tiers.

6. **Telemetry:** `debug_context_tier: tier` added to response JSON.

### Fetch Optimization

For Tier 1, skip expensive fetches entirely:
```javascript
const tier = classifyMessageTier(userMessage, deep_mode);

if (tier === 1) {
  // Only fetch karmaCtx (fast, already cached)
  const karmaCtx = await fetchKarmaContext(userMessage);
  systemParts = buildSystemText(karmaCtx, null, null, null, _memoryMdCache, null, null, null, null, tier);
} else if (tier === 2) {
  // Skip k2MemCtx, ckLatest, statePrelude
  const [karmaCtx, semanticCtx, k2WorkingMemCtx] = await Promise.all([...]);
  systemParts = buildSystemText(karmaCtx, null, webResults, semanticCtx, _memoryMdCache, activeIntentsText, null, k2WorkingMemCtx, coordCtx, tier);
} else {
  // Full fetch — unchanged from current behavior
}
```

This saves 2-3 network round-trips on Tier 1 messages (K2 working memory, K2 mem graph,
checkpoint fetch).

### Cost Impact

| Traffic segment | % of traffic | Current cost/msg | Optimized cost/msg | Monthly savings |
|---|---|---|---|---|
| Tier 1 (simple) | ~40% | $0.010 | $0.002 | ~$4.80 |
| Tier 2 (standard) | ~40% | $0.010 | $0.005 | ~$3.00 |
| Tier 3 (deep) | ~20% | $0.010 | $0.010 | $0 |
| **Total** | | | | **~$7.80/month** |

Estimated 13% of $60 monthly cap.

### Safety

- Tier 3 is exactly current behavior — zero regression risk for complex queries
- Keyword detection only bumps UP tiers, never down
- Missing prompt files fall through: standard → full, local → standard → full
- `debug_context_tier` in response enables monitoring and tuning
- No behavior change for deep mode (always Tier 3)

### Files

| File | Action |
|---|---|
| `Memory/01-karma-standard-prompt.md` | CREATE (~10K, derived from 00-karma-system-prompt-live.md) |
| `hub-bridge/app/server.js` | MODIFY (add tier routing, ~80 lines) |
| `Memory/00-karma-local-prompt.md` | EXISTS (3K, used for Tier 1) |
| `Memory/00-karma-system-prompt-live.md` | UNCHANGED (34K, used for Tier 3) |

### Blocked By

Nothing — all dependencies exist. Can implement immediately.
