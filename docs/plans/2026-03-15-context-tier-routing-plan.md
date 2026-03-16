# Context Tier Routing — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reduce /v1/chat input context from ~47K to ~6-20K chars for non-deep messages, saving ~$8/month.

**Architecture:** Three-tier message classification (LIGHT/STANDARD/DEEP) gates which context components are fetched and injected. New standard identity prompt (~10K) sits between existing local (3K) and full (34K).

**Tech Stack:** Node.js (server.js), Markdown (prompt files), Docker (hub-bridge rebuild)

---

### Task 1: Create Standard Identity Prompt

**Files:**
- Read: `Memory/00-karma-system-prompt-live.md` (vault-neo, 34K — the full prompt)
- Read: `Memory/00-karma-local-prompt.md` (3K — the minimal prompt, for reference)
- Create: `Memory/01-karma-standard-prompt.md` (~10K)

**Step 1: Read the full system prompt from vault-neo**

```bash
ssh vault-neo 'cat /home/neo/karma-sade/Memory/00-karma-system-prompt-live.md' > /tmp/full-prompt.md
```

**Step 2: Create the standard prompt**

Extract these sections from the full prompt into `Memory/01-karma-standard-prompt.md`:
- Core identity header ("You are Karma...")
- About Colby (name, location, preferences, decision style)
- Behavioral contract (6 rules — evidence, honesty, concise, no filler, peer-level, surface errors)
- Family hierarchy table (Sovereign/Ascendant/ArchonPrime/Archon/Initiate)
- Tool capabilities summary (deep-mode tools: graph_query, get_vault_file, write_memory, fetch_url, get_library_docs, get_local_file — listed but not documented in detail)
- Memory rules (use context, address as Colby, honest about uncertainty)
- Improvement pipeline (ASSIMILATE/DEFER/DISCARD)

Do NOT include:
- Architecture internals (data model, capture sources, consciousness loop)
- K2 compute substrate docs
- Self-audit protocol
- Deferred intent engine
- FalkorDB schema
- State-write triggers
- Detailed tool parameter documentation

Target: ~10K chars (~2,500 tokens).

**Step 3: Verify sizes**

```bash
wc -c Memory/01-karma-standard-prompt.md  # expect 8000-12000
wc -c Memory/00-karma-local-prompt.md     # expect ~3000 (reference)
```

**Step 4: Commit**

```bash
powershell -Command "git add Memory/01-karma-standard-prompt.md; git commit -m 'feat: standard identity prompt for context tier routing (10K)'"
```

---

### Task 2: Add Tier Classification Function to server.js

**Files:**
- Modify: `hub-bridge/app/server.js` — insert after line ~900 (before buildSystemText)

**Step 1: Add the classifyMessageTier function**

Insert this BEFORE the `buildSystemText` function (around line 900):

```javascript
// ── Context Tier Routing ─────────────────────────────────────────────────────
// Tier 1 (LIGHT):    short casual messages — minimal context, local identity prompt
// Tier 2 (STANDARD): medium messages or keyword-triggered — standard identity, most context
// Tier 3 (DEEP):     deep mode, long messages, or complex keywords — full context (current behavior)
const TIER3_KEYWORDS = /\b(deep|analy[sz]e|architecture|design|explain\s+in\s+detail|diagnos[ei])\b/i;
const TIER2_KEYWORDS = /\b(kiki|codex|k2|deploy|build|code|file|graph|debug|fix|bug|test|checkpoint|phase|plan|remember|memory|forget|tool|vault|ledger|falkor)\b/i;

function classifyMessageTier(userMessage, deepMode) {
  if (deepMode) return 3;
  const len = userMessage.length;
  if (len > 500) return 3;
  if (TIER3_KEYWORDS.test(userMessage)) return 3;
  if (TIER2_KEYWORDS.test(userMessage)) return 2;
  if (len >= 100) return 2;
  return 1;
}
```

**Step 2: Add identity prompt loader**

Insert after the KARMA_IDENTITY_PROMPT loading (around line 1281):

```javascript
// Tiered identity prompts — lighter prompts for simpler messages
let KARMA_STANDARD_PROMPT = "";
let KARMA_LOCAL_PROMPT = "";
const KARMA_STANDARD_PROMPT_PATH = "/karma/repo/Memory/01-karma-standard-prompt.md";
const KARMA_LOCAL_PROMPT_PATH = "/karma/repo/Memory/00-karma-local-prompt.md";
try { KARMA_STANDARD_PROMPT = readFileTrim(KARMA_STANDARD_PROMPT_PATH); console.log("[INIT] KARMA_STANDARD_PROMPT loaded, length:", KARMA_STANDARD_PROMPT.length); } catch (e) { console.warn("[INIT] KARMA_STANDARD_PROMPT not found — Tier 2 will use full identity"); }
try { KARMA_LOCAL_PROMPT = readFileTrim(KARMA_LOCAL_PROMPT_PATH); console.log("[INIT] KARMA_LOCAL_PROMPT loaded, length:", KARMA_LOCAL_PROMPT.length); } catch (e) { console.warn("[INIT] KARMA_LOCAL_PROMPT not found — Tier 1 will use standard/full identity"); }

function getIdentityForTier(tier) {
  if (tier === 1) return KARMA_LOCAL_PROMPT || KARMA_STANDARD_PROMPT || KARMA_IDENTITY_PROMPT;
  if (tier === 2) return KARMA_STANDARD_PROMPT || KARMA_IDENTITY_PROMPT;
  return KARMA_IDENTITY_PROMPT;
}
```

**Step 3: Verify syntax locally**

```bash
node -c hub-bridge/app/server.js
```

Expected: no output (valid syntax)

**Step 4: Commit**

```bash
powershell -Command "git add hub-bridge/app/server.js; git commit -m 'feat: add classifyMessageTier + tiered identity loaders'"
```

---

### Task 3: Modify buildSystemText for Tier-Gated Context

**Files:**
- Modify: `hub-bridge/app/server.js` — `buildSystemText()` function (line ~901)

**Step 1: Add tier parameter to buildSystemText**

Change function signature from:
```javascript
function buildSystemText(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null, activeIntentsText = null, k2MemCtx = null, k2WorkingMemCtx = null, coordinationCtx = null) {
```
To:
```javascript
function buildSystemText(karmaCtx, ckLatest = null, webResults = null, semanticCtx = null, memoryMd = null, activeIntentsText = null, k2MemCtx = null, k2WorkingMemCtx = null, coordinationCtx = null, tier = 3) {
```

**Step 2: Replace identity block selection**

Change:
```javascript
  const identityBlock = KARMA_IDENTITY_PROMPT
    ? KARMA_IDENTITY_PROMPT + "\n\n---\n\n"
    : "";
```
To:
```javascript
  const tierIdentity = getIdentityForTier(tier);
  const identityBlock = tierIdentity
    ? tierIdentity + "\n\n---\n\n"
    : "";
```

**Step 3: Gate context sections by tier**

Replace the context injection section. Each component gets a tier gate:

```javascript
  // Semantic memory — Tier 2+
  if (tier >= 2 && semanticCtx) {
    text += `\n\n${semanticCtx}`;
  }

  // Web search results — Tier 2+ (only fires if search intent detected)
  if (tier >= 2 && webResults) {
    text += `\n\n--- WEB SEARCH RESULTS ---\n${webResults}\n---\nUse these results to inform your response. Cite the source URL inline when drawing from a specific result.`;
  }

  // Checkpoint karma_brief — Tier 3 only
  if (tier >= 3 && ckLatest && ckLatest.karma_brief) {
    const ckId = ckLatest.checkpoint_id || ckLatest.latest_checkpoint_fact?.content?.value?.checkpoint_id || 'latest';
    text += `\n\n--- KARMA SELF-KNOWLEDGE (${ckId}) ---\n${ckLatest.karma_brief}\n---`;
  }

  // Graph distillation — Tier 3 only
  if (tier >= 3 && ckLatest && ckLatest.distillation_brief) {
    text += `\n\n--- KARMA GRAPH SYNTHESIS ---\n${ckLatest.distillation_brief}\n---`;
  }

  // Session brief — Tier 2+
  if (tier >= 2 && _sessionBriefCache) {
    text += `\n\n--- CURRENT SESSION CONTEXT ---\n${_sessionBriefCache}\n---`;
  }

  // Memory spine — always (all tiers)
  if (memoryMd) {
    text += `\n\n--- KARMA MEMORY SPINE (recent) ---\n${memoryMd}\n---`;
  }

  // K2 memory graph — Tier 3 only
  if (tier >= 3 && k2MemCtx) {
    text += `\n\n--- ARIA K2 MEMORY GRAPH ---\n${k2MemCtx}\n---`;
  }

  // K2 working memory — Tier 2+ (conditionally fetched based on keywords)
  if (tier >= 2 && k2WorkingMemCtx) {
    text += `\n\n--- K2 WORKING MEMORY + KIKI STATE ---\n${k2WorkingMemCtx}\n---`;
  }

  // Coordination — Tier 2+ (conditionally fetched)
  if (tier >= 2 && coordinationCtx) {
    text += coordinationCtx;
  }
```

Also gate direction block:
```javascript
  // Direction — Tier 3 only (large, architectural context not needed for casual chat)
  const directionBlock = (tier >= 3 && _directionMdCache)
    ? `\n--- KARMA DIRECTION (current architecture & stage) ---\n${_directionMdCache}\n---\n\n`
    : "";
```

**Step 4: Verify syntax**

```bash
node -c hub-bridge/app/server.js
```

**Step 5: Commit**

```bash
powershell -Command "git add hub-bridge/app/server.js; git commit -m 'feat: tier-gated context injection in buildSystemText'"
```

---

### Task 4: Modify /v1/chat Handler for Tier-Aware Fetching

**Files:**
- Modify: `hub-bridge/app/server.js` — `/v1/chat` handler (line ~2460)

**Step 1: Add tier classification before fetch block**

Insert BEFORE the `Promise.all` block (around line 2467):

```javascript
      const tier = classifyMessageTier(userMessage, deep_mode);
```

**Step 2: Replace the Promise.all block with tier-aware fetching**

Replace the current block (lines ~2468-2475):
```javascript
      const [karmaCtx, semanticCtx, k2MemCtx, k2WorkingMemCtx] = await Promise.all([
        fetchKarmaContext(userMessage),
        fetchSemanticContext(userMessage),
        fetchK2MemoryGraph(userMessage),
        fetchK2WorkingMemory(),
      ]);
```

With:
```javascript
      let karmaCtx = null, semanticCtx = null, k2MemCtx = null, k2WorkingMemCtx = null;
      if (tier === 1) {
        // LIGHT — only karmaCtx (fast, often cached)
        karmaCtx = await fetchKarmaContext(userMessage);
      } else if (tier === 2) {
        // STANDARD — skip k2MemCtx (Aria graph), keep karmaCtx + semanticCtx + conditional k2WorkingMem
        const needsK2Working = TIER2_KEYWORDS.test(userMessage) && /\b(kiki|k2|codex)\b/i.test(userMessage);
        const fetches = [
          fetchKarmaContext(userMessage),
          fetchSemanticContext(userMessage),
          needsK2Working ? fetchK2WorkingMemory() : Promise.resolve(null),
        ];
        [karmaCtx, semanticCtx, k2WorkingMemCtx] = await Promise.all(fetches);
      } else {
        // DEEP — full fetch (unchanged)
        [karmaCtx, semanticCtx, k2MemCtx, k2WorkingMemCtx] = await Promise.all([
          fetchKarmaContext(userMessage),
          fetchSemanticContext(userMessage),
          fetchK2MemoryGraph(userMessage),
          fetchK2WorkingMemory(),
        ]);
      }
```

**Step 3: Skip checkpoint fetch for Tier 1**

Change the checkpoint fetch (around line 2462):
```javascript
      let ckLatestData = null;
      if (tier >= 3) {
        try {
          ckLatestData = await fetchCheckpointLatestFromVault();
        } catch (e) { /* non-fatal */ }
      }
```

**Step 4: Skip statePrelude for Tier 1-2**

Change the statePrelude block (around line 2500):
```javascript
      let statePrelude = "";
      if (tier >= 3) {
        try {
          statePrelude = buildStatePrelude(ckLatestData, userMessage.length);
        } catch (e) {
          statePrelude = "=== STATE PRELUDE (vault unavailable) ===";
        }
      }
```

**Step 5: Pass tier to buildSystemText**

Change the buildSystemText call (around line 2491):
```javascript
      const systemParts = buildSystemText(karmaCtx, ckLatestData, webSearchResults, semanticCtx, _memoryMdCache || null, activeIntentsText || null, k2MemCtx || null, k2WorkingMemCtx || null, getRecentCoordination(tier >= 2 ? "karma" : null), tier);
```

Note: `getRecentCoordination(null)` returns "" — no coordination for Tier 1.

**Step 6: Add telemetry**

Find the response JSON object (around line 2629) and add:
```javascript
        debug_context_tier: tier,
```

Also add in the non-deep response path (around line 2707):
```javascript
        debug_context_tier: tier,
```

**Step 7: Verify syntax**

```bash
node -c hub-bridge/app/server.js
```

**Step 8: Commit**

```bash
powershell -Command "git add hub-bridge/app/server.js; git commit -m 'feat: tier-aware fetch routing in /v1/chat handler'"
```

---

### Task 5: Deploy and Verify

**Files:**
- Deploy: `hub-bridge/app/server.js`, `Memory/01-karma-standard-prompt.md`, `Memory/00-karma-local-prompt.md`

**Step 1: Push to GitHub**

```bash
powershell -Command "git push origin main"
```

**Step 2: Sync to vault-neo and rebuild**

Use the `/deploy` skill or manually:
```bash
ssh vault-neo 'cd /home/neo/karma-sade && git pull origin main'
ssh vault-neo 'cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js'
ssh vault-neo 'cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d'
```

**Step 3: Verify container starts**

```bash
ssh vault-neo 'docker logs anr-hub-bridge --tail 20 2>&1 | grep -E "INIT|KARMA|listening|ERROR"'
```

Expected output should include:
- `[INIT] KARMA_IDENTITY_PROMPT loaded, length: 33994`
- `[INIT] KARMA_STANDARD_PROMPT loaded, length: ~10000`
- `[INIT] KARMA_LOCAL_PROMPT loaded, length: ~2984`
- `listening on 18090`

**Step 4: Test Tier 1 (simple message)**

```bash
ssh vault-neo 'TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s -X POST https://hub.arknexus.net/v1/chat -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "{\"message\":\"How are you?\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(\"tier:\",d.get(\"debug_context_tier\"),\"chars:\",d.get(\"debug_input_chars\"))"'
```

Expected: `tier: 1` and `debug_input_chars` significantly lower than previous ~47K.

**Step 5: Test Tier 2 (keyword message)**

```bash
ssh vault-neo 'TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s -X POST https://hub.arknexus.net/v1/chat -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d "{\"message\":\"What is kiki working on?\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(\"tier:\",d.get(\"debug_context_tier\"),\"chars:\",d.get(\"debug_input_chars\"))"'
```

Expected: `tier: 2` and lower than ~47K but higher than Tier 1.

**Step 6: Test Tier 3 (deep mode)**

```bash
ssh vault-neo 'TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s -X POST https://hub.arknexus.net/v1/chat -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -H "x-karma-deep: true" -d "{\"message\":\"Hi\"}" | python3 -c "import sys,json; d=json.load(sys.stdin); print(\"tier:\",d.get(\"debug_context_tier\"),\"chars:\",d.get(\"debug_input_chars\"))"'
```

Expected: `tier: 3` and `debug_input_chars` approximately unchanged from before.

**Step 7: Verify Karma responds coherently at all tiers**

Check that each test above also returned a sensible `assistant_text` — Karma should still know who Colby is, still be warm and direct, still reference memory when relevant.

**Step 8: Commit MEMORY.md + post bus**

Update MEMORY.md with deployment status. Post PROOF to coordination bus.

```bash
powershell -Command "git add MEMORY.md; git commit -m 'docs: context tier routing deployed and verified'"
```
