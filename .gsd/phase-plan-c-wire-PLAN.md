# Phase: Plan-C Wire — Implementation Plan
**Created:** 2026-03-23 (Session 137 wrap)
**Context:** `.gsd/phase-plan-c-wire-CONTEXT.md`
**Spec:** `Karma2/PLAN-C-wire.md`

---

## Task 1: Check claude-mem network binding options (C1 setup) <done>Session 138</done>

**Action:** Check if claude-mem supports --host binding:
```bash
claude-mem --help 2>&1 | grep -i host
# Also check: claude-mem serve --help
# Also check config file location
```

<verify>Know whether claude-mem supports --host. Know the current binding (localhost only vs. 0.0.0.0).</verify>

---

## Task 2: Expose claude-mem to vault-neo (C1) <done>Session 138</done>

**If --host supported:**
```bash
# Restart claude-mem bound to Tailscale IP
claude-mem serve --host 100.124.194.102 --port 37777
```
Update KarmaClaudeMem (or equivalent startup) to use the new binding.

**If not supported (fallback):**
Add hub-bridge proxy: `POST /memory/search` → `http://100.124.194.102:37777/search`

<verify>From vault-neo: `curl http://100.124.194.102:37777/health` → responds.</verify>

---

## Task 3: Add /memory endpoints to hub-bridge (C3) <done>Session 139 — partial</done>

**Action:** Add to hub-bridge server.js:
- `POST /memory/search` → proxy to P1:7891/memory/search via Tailscale ✅ routing works, 503 due to zombie socket
- `POST /memory/save` → proxy to P1:7891/memory/save via Tailscale ✅ routing works
- `GET /memory/context` → cc_identity_spine.json from K2 via ARIA_URL/api/exec ✅ VERIFIED returns resume_block

Auth: same Bearer token. Deployed hub-bridge v2.12.0.

**BLOCKER:** /memory/search + /memory/save return 503 "claude-mem unavailable" — zombie socket (PID 21240 dead, 127.0.0.1:37777 ghost). Fix: restart Claude Code to clear zombie.

<verify>
After CC restart, run:
```bash
curl -X POST https://hub.arknexus.net/memory/search \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "zombie processes cc_server"}'
# → returns observations from Julian's session history
```
/memory/context is already verified (returns CC resume_block from spine v38).
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
- [ ] vault-neo can reach claude-mem (C1)
- [ ] Chrome Inspector shows WebMCP tools on hub pages (C2)
- [ ] `/memory/search` returns Julian's history from hub.arknexus.net (C3)
- [ ] Hub UI sessions survive browser restart, context restored (C4)
