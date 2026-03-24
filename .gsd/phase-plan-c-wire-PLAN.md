# Phase: Plan-C Wire — Implementation Plan
**Created:** 2026-03-23 (Session 137 wrap)
**Context:** `.gsd/phase-plan-c-wire-CONTEXT.md`
**Spec:** `Karma2/PLAN-C-wire.md`

---

## Task 1: Check claude-mem network binding options (C1 setup) <done>

**Verified:** `CLAUDE_MEM_WORKER_HOST` in `~/.claude-mem/settings.json` controls binding. Currently `127.0.0.1`. Can be changed to `0.0.0.0`. MCP server caches config at session start — requires Claude Code restart to take effect.

---

## Task 2: Expose claude-mem to vault-neo (C1) <done>

**Approach taken:** Added `/memory/health`, `/memory/search`, `/memory/save` endpoints to `cc_server_p1.py` (port 7891). These proxy to claude-mem worker at `127.0.0.1:37777`.

**Why port 7891 instead of 37777:** Port 37777 blocked by Windows Firewall (no interactive allow popup for headless proxy process). Port 7891 had existing firewall rule from interactive cc_server_p1 startup.

**VERIFIED:** `ssh vault-neo "curl -s http://100.124.194.102:7891/memory/health"` → `{"ok": true, "service": "cc-server-p1", "claudemem_url": "http://127.0.0.1:37777"}`

**Updated verify criterion for Task 3:** hub-bridge should proxy to `http://100.124.194.102:7891/memory/*` (not 37777).

---

## Task 3: Add /memory endpoints to hub-bridge (C3)

**Action:** Add to hub-bridge server.js:
- `POST /memory/search` → claude-mem search (proxy to `http://100.124.194.102:7891/memory/search` via Tailscale)
- `POST /memory/save` → claude-mem save (proxy to `http://100.124.194.102:7891/memory/save`)
- `GET /memory/context` → cc_identity_spine.json + cc_cognitive_checkpoint.json from K2

Auth: same Bearer token. Deploy via karma-hub-deploy skill.

<verify>
```bash
curl -X POST https://hub.arknexus.net/memory/search \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "zombie processes cc_server"}'
# → returns observations from Julian's session history
```
</verify>

---

## Task 4: Register WebMCP tool descriptors on hub pages (C2)

**Action:** Add to hub-bridge HTML pages (unified.html):
- `search_memory` tool — calls POST /memory/search
- `post_to_bus` tool — calls POST /v1/coordination/post
- `get_context` tool — calls GET /memory/context

<verify>Chrome Model Context Tool Inspector Extension shows 3+ tools registered on hub.arknexus.net.</verify>

---

## Task 5: Chrome session clone pattern (C4)

**Action:** Add to hub UI:
- On load: `const base = await LanguageModel.create({ initialPrompts: [{ role: 'system', content: await fetch('/memory/context').then(r => r.text()) }] })`
- Clone for karma/julian expressions
- Persist `base.initialPrompts` to localStorage on each turn
- Restore on next browser load

<verify>
- Open hub.arknexus.net, start conversation
- Close Chrome, reopen
- Context restored from localStorage, no reconstruction ceremony
</verify>

---

## C-GATE Check

All tasks complete when:
- [x] vault-neo can reach claude-mem (C1) — via P1:7891/memory/* endpoints
- [ ] Chrome Inspector shows WebMCP tools on hub pages (C2)
- [ ] `/memory/search` returns Julian's history from hub.arknexus.net (C3)
- [ ] Hub UI sessions survive browser restart, context restored (C4)
