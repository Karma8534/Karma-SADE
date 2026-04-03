# Phase: Karma Emergency Fix — PLAN

## Date: 2026-03-12
## Session: 85

---

### Task 1: Fix system prompt contradictions + add K2 ownership
**File:** `Memory/00-karma-system-prompt-live.md`

- [ ] Remove line 254's "no tools in standard mode" claim
- [ ] Remove "deep-mode only" labels from tool descriptions
- [ ] Add K2 ownership directive (K2 = Karma's resource, delegate heavy work there)
- [ ] Simplify capabilities section (merge CAN/CANNOT)
- [ ] Audit all sections for internal consistency
- [ ] Make fetch_url behavior explicit

<verify>System prompt has no tools contradiction. K2 ownership section exists. No "deep-mode only" labels.</verify>

### Task 2: Fix MEMORY_MD_TAIL_CHARS
**File:** `hub-bridge/app/server.js` line 81

- [ ] Change `const MEMORY_MD_TAIL_CHARS = 800;` → `const MEMORY_MD_TAIL_CHARS = 2000;`

<verify>`grep MEMORY_MD_TAIL hub-bridge/app/server.js` shows 2000</verify>

### Task 3: Fix K2 memory query
**File:** `hub-bridge/app/server.js` line 1820

- [ ] Change `fetchK2MemoryGraph("Colby")` → `fetchK2MemoryGraph(userMessage)`

<verify>`grep fetchK2MemoryGraph hub-bridge/app/server.js` shows userMessage</verify>

### Task 4: Wire K2 working memory (scratchpad + shadow)
**File:** `hub-bridge/app/server.js`

- [ ] Add `fetchK2WorkingMemory()` function (POST /api/exec, reads both files, 5min cache, 4000 char cap)
- [ ] Add 8th param `k2WorkingMemCtx` to `buildSystemText()`
- [ ] Add injection point after K2 memory graph section
- [ ] Add to Promise.all at line 1817

<verify>`grep fetchK2WorkingMemory hub-bridge/app/server.js` exists. `grep 'K2 WORKING MEMORY' hub-bridge/app/server.js` exists.</verify>

### Task 5: Deploy system prompt (Phase 1)
- [ ] git commit + push
- [ ] `ssh vault-neo "cd /home/neo/karma-sade && git pull"`
- [ ] `docker restart anr-hub-bridge`

<verify>Chat with Karma, share a URL → she calls fetch_url</verify>

### Task 6: Deploy hub-bridge (Phases 2+3)
- [ ] Sync: `cp /home/neo/karma-sade/hub-bridge/app/server.js /opt/seed-vault/memory_v1/hub_bridge/app/server.js`
- [ ] Rebuild: `cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d`

<verify>hub-bridge logs show K2-MEM with variable query. Ask Karma "what's in your scratchpad?" — she answers.</verify>

### Task 7: End-to-end verification
- [ ] Multi-turn conversation at hub.arknexus.net
- [ ] Verify tools work (fetch_url, graph_query)
- [ ] Verify K2 working memory visible in context
- [ ] Verify MEMORY.md tail adequate

<verify>Karma maintains coherence, uses tools, references recent state.</verify>

### Task 8: Update docs + commit
- [ ] Update .gsd/STATE.md
- [ ] Update .gsd/ROADMAP.md
- [ ] Update MEMORY.md
- [ ] Write phase-karma-emergency-SUMMARY.md
- [ ] Final commit + push

<verify>All docs current. git status clean.</verify>
