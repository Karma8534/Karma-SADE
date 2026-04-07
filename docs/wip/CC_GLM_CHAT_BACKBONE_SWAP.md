# GLM-4.7-Flash Chat Backbone Swap — Hub-Bridge Integration

## Context
Hub-bridge currently uses the OpenAI Node.js SDK client (`new OpenAI({ apiKey })`) which points at api.openai.com. All non-Anthropic models route through this client. When we set MODEL_DEFAULT to a GLM model, it 404s because OpenAI doesn't serve GLM models.

**Fix:** Add a second OpenAI SDK client instance pointing at Z.ai's OpenAI-compatible endpoint, and route GLM model names through it.

Z.ai's API is fully OpenAI SDK compatible:
- Base URL: `https://api.z.ai/api/paas/v4/`
- Auth: `Authorization: Bearer <ZAI_API_KEY>`
- Model ID: `glm-4.7-flash` (free tier, zero cost)
- Format: Standard `/v1/chat/completions` — same request/response shape as OpenAI

## All work happens on the droplet at /opt/seed-vault/memory_v1

---

## Phase 1: Add Z.ai Client to hub-bridge/server.js

**File:** `/opt/seed-vault/memory_v1/hub-bridge/server.js`

Find this block (around line 819-820):
```javascript
const openai    = new OpenAI({ apiKey: OPENAI_KEY });
const anthropic = ANTHROPIC_KEY ? new Anthropic({ apiKey: ANTHROPIC_KEY }) : null;
```

Add IMMEDIATELY AFTER those two lines:
```javascript
// ── Z.ai client for GLM models (OpenAI-compatible endpoint) ───────────────
const ZAI_API_KEY = process.env.ZAI_API_KEY || "";
const zai = ZAI_API_KEY
  ? new OpenAI({ apiKey: ZAI_API_KEY, baseURL: "https://api.z.ai/api/paas/v4/" })
  : null;
if (zai) console.log("[INIT] Z.ai client ready — GLM models available");
else console.warn("[INIT] ZAI_API_KEY not set — GLM models will fall back to OpenAI (will 404)");
```

## Phase 2: Route GLM Models Through Z.ai Client

### 2a: Modify callLLM() function

Find `async function callLLM(model, messages, maxTokens)` (around line 1057).

Find the "OpenAI path" section which looks like:
```javascript
  // OpenAI path
  const completion = await openai.chat.completions.create({ model, messages, max_completion_tokens: maxTokens });
```

Replace that single line with:
```javascript
  // Route: GLM models → Z.ai client, everything else → OpenAI
  const isZaiModel = model.startsWith("glm-");
  const client = (isZaiModel && zai) ? zai : openai;
  const providerName = (isZaiModel && zai) ? "zai" : "openai";
  const completion = await client.chat.completions.create({ model, messages, max_completion_tokens: maxTokens });
```

Also in the return object of that same function, change:
```javascript
    provider:     "openai",
```
to:
```javascript
    provider:     providerName,
```

### 2b: Modify callLLMWithTools() function

Find `async function callLLMWithTools(model, messages, maxTokens)` (around line 945).

Inside the try block, find the openai.chat.completions.create call (around line 1011):
```javascript
      const resp = await openai.chat.completions.create({
```

Add this routing logic BEFORE that line:
```javascript
      const isZaiModel = model.startsWith("glm-");
      const toolClient = (isZaiModel && zai) ? zai : openai;
```

Then change the call from:
```javascript
      const resp = await openai.chat.completions.create({
```
to:
```javascript
      const resp = await toolClient.chat.completions.create({
```

## Phase 3: Add ZAI_API_KEY to Hub-Bridge Environment

### 3a: Hub-bridge compose environment

**File:** `/opt/seed-vault/memory_v1/hub-bridge/compose.hub.yml`

Add to the `environment` section of the hub-bridge service:
```yaml
      ZAI_API_KEY: "${ZAI_API_KEY}"
```

### 3b: Shared .env file

**File:** `/opt/seed-vault/memory_v1/compose/.env`

Check if ZAI_API_KEY already exists (it was added for karma-server). If not, add:
```
ZAI_API_KEY=47d6a0c23e494a319961ed5469e17a14.GNauf9TFcyOdq9g1
```

If hub-bridge uses a DIFFERENT .env path, find it and add the key there too.

### 3c: Set MODEL_DEFAULT

In the same env file or compose environment, set:
```
MODEL_DEFAULT=glm-4.7-flash
```

## Phase 4: Rebuild Hub-Bridge

```bash
cd /opt/seed-vault/memory_v1
docker compose -f hub-bridge/compose.hub.yml up -d --build
```

Wait 15 seconds, then verify:
```bash
docker logs $(docker ps -q --filter name=hub-bridge) 2>&1 | tail -20
```

You should see: `[INIT] Z.ai client ready — GLM models available`

If you see the WARN about ZAI_API_KEY not set, the env var isn't reaching the container. Debug with:
```bash
docker exec $(docker ps -q --filter name=hub-bridge) env | grep ZAI
docker exec $(docker ps -q --filter name=hub-bridge) env | grep MODEL
```

## Phase 5: Voice Tests

Run both tests through the hub-bridge chat endpoint:

**Test 1 — Substantive exchange:**
```bash
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)" \
  -d '{"message": "Explain your persona and how you approach our work together."}' \
  2>&1 | python3 -m json.tool | head -60
```

**Test 2 — Short exchange (the regression test):**
```bash
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)" \
  -d '{"message": "Stop with the exclamation marks, Karma."}' \
  2>&1 | python3 -m json.tool | head -30
```

**Test 3 — Memory retrieval:**
```bash
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt)" \
  -d '{"message": "What do you know about Ollie?"}' \
  2>&1 | python3 -m json.tool | head -40
```

**For each test, report:**
1. The full response text
2. The `provider` field in the response JSON (should say "zai", not "openai")
3. The `debug_karma_ctx` field (should say "ok" if memory retrieval is working)
4. Any errors in docker logs

## Phase 6: Verify & Commit

If all tests pass:
```bash
cd /opt/seed-vault/memory_v1
git add -A
git commit -m "feat: GLM-4.7-Flash as chat backbone via Z.ai (zero cost)"
git push
```

If GLM-4.7-Flash voice quality is poor (still chatbot-like), try `glm-4.7-flashx` instead ($0.07/$0.40 per 1M tokens — still very cheap). Change MODEL_DEFAULT and rebuild.

If GLM fails entirely, revert to:
```
MODEL_DEFAULT=gpt-4o
```

## Summary of Changes
- **hub-bridge/server.js**: Add Z.ai OpenAI client + route GLM models through it (~15 lines added)
- **hub-bridge/compose.hub.yml**: Add ZAI_API_KEY env var
- **compose/.env**: Add ZAI_API_KEY (if not present) + set MODEL_DEFAULT=glm-4.7-flash
- **Zero new dependencies** — uses existing OpenAI SDK with different baseURL
- **Cost impact**: From ~$2.50/$10.00 per 1M tokens (gpt-4o) to $0/$0 (glm-4.7-flash free tier)
