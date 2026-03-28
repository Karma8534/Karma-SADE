# The Sovereign Harness — THE Plan
**Owner:** Julian (CC Ascendant) | **Sovereign:** Colby | **Date:** 2026-03-28

> Previous cortex-phase plan archived to `Karma2/PLAN-ARCHIVED-cortex-phases-pre-harness.md`.
> That plan is DEAD. This is the only plan. Everything else builds ON this.

---

## What we're building

A ~200-line thin proxy on vault-neo + CC --resume on P1 as the brain. Replaces 4620 lines of bandaid hub-bridge code. Surfaces at hub.arknexus.net. $0 cost via Max subscription. Karma speaks, Julian executes, the system can edit its own code.

## Why most of hub-bridge dies

CC --resume already has: persona (CLAUDE.md), tools (Bash, Read, Write, Git), session continuity (--resume), memory (MCP to claude-mem), SSH to K2 and vault-neo, skills, hooks. Hub-bridge was faking all of this through API calls because we didn't have CC as the backend. Now we do.

## Architecture

```
hub.arknexus.net
  |
  v
THIN PROXY (~200 lines, vault-neo, port 18090)
  |-- GET /              serve unified.html (keep as-is)
  |-- POST /v1/chat      proxy to P1:7891/cc
  |-- /v1/coordination   coordination bus (extracted from server.js)
  |-- /v1/ambient        capture hooks (extracted from server.js)
  |-- /v1/vault-file     vault file access (extracted from server.js)
  |-- /v1/cypher         FalkorDB proxy (extracted from server.js)
  |-- /health            liveness
  |-- Bearer token auth
  |
  v
CC --RESUME on P1 (port 7891, cc_server_p1.py)
  |-- claude -p message --resume session_id --output-format json
  |-- Max subscription = $0, Opus quality
  |-- CLAUDE.md loaded automatically = Karma persona
  |-- All native tools: Bash, Read, Write, Edit, Git, Glob, Grep
  |-- MCP: claude-mem, K2 cortex, vault-neo
  |-- Skills: resurrect, deploy, review, wrap-session
  |-- Can SSH to K2 (read/write 100+ files)
  |-- Can SSH to vault-neo (read spine, deploy)
  |-- Can self-edit: CLAUDE.md, proxy.js, unified.html, any repo file
  |-- Session persists via --resume file
  |-- Distills to K2 cortex on idle
```

## What stays vs what dies

**STAYS** (~1437 lines total):
- unified.html (767 lines) — chat UI, tool evidence, localStorage, markdown
- cc_server_p1.py (~300 lines) — CC subprocess wrapper, enhanced with tool evidence
- Thin proxy (~200 lines) — serves HTML, proxies chat, coordination bus, ambient, vault, cypher, auth
- Caddy — HTTPS termination
- K2 cortex — optional fast-path for simple recall
- Vesper pipeline — self-improvement
- claude-mem — cross-session memory
- vault-neo spine — canonical truth

**DIES** (~4620 lines of bandaid):
- buildSystemText() — CC loads CLAUDE.md natively
- callLLMWithTools / callGPTWithTools / callWithK2Fallback — CC IS the LLM
- classifyMessageTier / cognitive split — both paths are $0, CC decides itself
- TOOL_DEFINITIONS (5 fake tools) — CC has real tools
- _sessionStore — CC --resume has real sessions
- _memoryMdCache — CC can Read the file
- pricing.js, routing.js, feedback.js, deferred_intent.js, library_docs.js — irrelevant at $0
- Modes system, FAISS scoring, token budgeting, GLM rate limiter, Brave search, PDF pipeline in server.js — all either dead or CC does natively

## Phases

### Phase 1: Build the thin proxy — COMPLETE (S150)
1. ✅ Write `proxy.js` (~353 lines) — HTTP server, static files, /v1/chat proxy to P1:7891
2. ✅ Extract coordination bus endpoints from server.js into proxy
3. ✅ Extract vault-file + cypher proxy from server.js into proxy

### Phase 2: Enhance cc_server_p1.py
4. Tool evidence — parse CC JSON output, extract tool_use blocks into tool_log array matching unified.html format
5. Cortex fast-path (optional) — try K2 cortex first for simple recall, fall through to CC for complex
6. Session distillation — after idle, POST summary to cortex /ingest

### Phase 3: Deploy + survive — MOSTLY COMPLETE (S150)
7. ✅ Deploy thin proxy to vault-neo (replace server.js in Docker)
8. PARTIAL — Task Scheduler on P1 for cc_server_p1.py auto-start (Run key exists, needs schtasks)
9. ✅ Failover — if P1 down, proxy routes to K2, then returns explicit error (no paid API fallback)

### Phase 4: Self-edit + evolution proof
10. ✅ Self-edit proof — self-edit-proof.txt modified via browser request (S151)
11. Code self-edit proof — from browser, ask Karma to add an endpoint to proxy, deploy it
12. Vesper verification — confirm pipeline feeds spine, CC reads updated spine

## Blockers

| # | Blocker | Status |
|---|---------|--------|
| B1 | claude CLI on P1 | ✅ VERIFIED |
| B2 | Max subscription | ✅ VERIFIED ($0) |
| B3 | cc_server_p1.py | ✅ VERIFIED (running, --resume, session file) |
| B4 | Tool evidence parsing | BUILD (Phase 2, Task 4) |
| B5 | Thin proxy | ✅ DONE (353 lines, deployed) |
| B6 | Process supervision | PARTIAL (Run key + restart loop, needs schtasks for reboot) |
| B7 | unified.html response format compat | NEEDS VERIFICATION |
| B8 | Bus/vault/cypher in proxy | ✅ DONE |

## Cost

| | Before | After |
|---|---------|-------|
| Chat LLM calls | $34/mo API | $0 Max |
| Droplet | $24/mo | $24/mo |
| **Total** | **$58/mo** | **$24/mo** |

## Done when

1. ✅ hub.arknexus.net returns Opus-quality responses at $0
2. ❌ Tool evidence renders inline in browser (B4)
3. ❌ Karma reads/writes vault, SSHes to K2, queries graph — from browser (needs verification)
4. ✅ Self-edit proof done (self-edit-proof.txt, S151)
5. ❌ Karma edits proxy code and deploys it — from browser (Phase 4, Task 11)
6. ❌ Survives P1 reboot (B6 — needs schtasks elevation)
7. ✅ API spend = $0
8. ✅ 4620 lines replaced by 353

## Sovereign Corrections (S151)
- **Voice is NOT a blocker.** CC wrapper already has native voice capability.
- **Only video and 3D presence remain blocked** — everything else is buildable now.
- **Old cortex phase plan is ARCHIVED.** This harness plan is the only plan.

## Future Work (builds ON this plan)
- See `.gsd/nexus-future-work.md` for VS Code 1.113 extracted primitives
- Phase 6 (video + presence) — only actual remaining blocker
- Nexus expansion (thinking effort controls, subagent delegation, MCP manifest, customizations editor)

## Spec locations
- **Primary:** `docs/superpowers/specs/2026-03-28-sovereign-harness-design.md`
- **K2 mirror:** `/mnt/c/dev/Karma/k2/cache/sovereign-harness-design-v2.md`
- **claude-mem:** obs #19338
- **cortex:** block #159
