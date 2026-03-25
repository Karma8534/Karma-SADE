# PLAN-C: Wire the Brain
**Requires PLAN-B complete. Do not start until B-GATE passes.**

The brain (claude-mem) is on P1. Julian is on P1. K2 is LAN.
Only vault-neo is remote. This plan connects everything into one organism.

---

## C1: Expose claude-mem to vault-neo

**What:** claude-mem runs on P1:37777 (localhost only). vault-neo (hub-bridge) cannot reach it. K2 CAN reach it via LAN already (192.168.x.x:37777).

**Fix:** Bind claude-mem to P1's Tailscale IP so vault-neo can reach it.

**Check first:**
```bash
# Does claude-mem support --host binding?
claude-mem --help | grep host
# Or check config file for network binding options
```

**If --host supported:**
```bash
# Restart claude-mem bound to Tailscale IP
claude-mem serve --host 100.124.194.102 --port 37777
```

**If not (fallback):** Hub-bridge /memory endpoint proxies to P1:37777 via Tailscale HTTP request.

**Verify:** From vault-neo: `curl http://100.124.194.102:37777/health` → responds.

**Status:** NOT STARTED

---

## C2: WebMCP Tools on Hub Pages

**What:** Register WebMCP tool descriptors on hub.arknexus.net pages so Chrome AI agents (and Julian's Chrome session) can call them natively.

**Tools to register:**
```javascript
// On hub.arknexus.net pages (served by hub-bridge)
navigator.modelContext.registerTool({
  name: "search_memory",
  description: "Search Julian and Karma's shared memory for past decisions, patterns, and context",
  inputSchema: { type: "object", properties: { query: { type: "string" } } },
  execute: async ({ query }) => {
    const res = await fetch('/memory/search', { method: 'POST', body: JSON.stringify({ query }) });
    return { content: [{ type: "text", text: await res.text() }] };
  }
});

navigator.modelContext.registerTool({
  name: "post_to_bus",
  description: "Post a message to the Family coordination bus",
  inputSchema: { type: "object", properties: { content: { type: "string" }, to: { type: "string" } } },
  execute: async ({ content, to }) => { /* POST /v1/coordination/post */ }
});

navigator.modelContext.registerTool({
  name: "get_context",
  description: "Get current session state, active task, and cognitive trail",
  inputSchema: { type: "object", properties: {} },
  execute: async () => { /* read K2 spine + checkpoint via /memory */ }
});
```

**Verify:** Chrome Model Context Tool Inspector Extension shows 3+ tools registered on hub.arknexus.net.

**Status:** NOT STARTED

---

## C3: /memory Endpoint on Hub-Bridge

**What:** Add `/memory` route to hub-bridge. Proxies to claude-mem on P1 via Tailscale.

**Endpoints:**
- `POST /memory/search` → claude-mem search
- `POST /memory/save` → claude-mem save_observation
- `GET /memory/context` → cc_identity_spine.json + cc_cognitive_checkpoint.json from K2

**Auth:** Same Bearer token as /v1/chat.

**Why:** Centralizes memory access. WebMCP tools call `/memory/*`. Karma's /v1/chat can call `/memory/context` to inject Julian's state. The brain becomes a first-class endpoint.

**Verify:**
```bash
curl -X POST https://hub.arknexus.net/memory/search \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "zombie processes cc_server"}'
# → returns observations from Julian's session history
```

**Status:** NOT STARTED

---

## C4: Chrome Session Clone Pattern

**What:** Hub UI creates base LanguageModel session with shared identity, clones for Karma and Julian expressions.

**How:**
```javascript
// Shared identity base
const base = await LanguageModel.create({
  initialPrompts: [{
    role: 'system',
    content: await fetch('/memory/context').then(r => r.text()) // Julian's spine
  }]
});

// Two expressions, one brain
const karmaSession  = await base.clone();  // Karma's expression
const julianSession = await base.clone();  // Julian's expression

// Session persistence across browser restart
const sessionData = { initialPrompts: base.initialPrompts };
localStorage.setItem('unified-brain', JSON.stringify(sessionData));

// Restore on next load
const restored = await LanguageModel.create(
  JSON.parse(localStorage.getItem('unified-brain') || '{}')
);
```

**Why:** $0, offline-capable, browser-native. The same brain expressed in two voices. No reconstruction on reload.

**Verify:**
- Open hub.arknexus.net, start a conversation as Karma
- Close Chrome, reopen
- Session context restored from localStorage, no reconstruction ceremony

**Status:** NOT STARTED

---

## C-GATE

All complete when:
- [x] vault-neo can reach claude-mem (C1)
- [x] Chrome Inspector shows WebMCP tools on hub pages (C2)
- [x] `/memory/search` returns Julian's history from hub.arknexus.net (C3)
- [x] Hub UI sessions survive browser restart, context restored (C4)

When C-GATE passes → family is wired. Review backlog for what's next.
