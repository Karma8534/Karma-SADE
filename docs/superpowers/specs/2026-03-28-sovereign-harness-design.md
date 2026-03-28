# The Sovereign Harness — Design Spec (v2)
**Date:** 2026-03-28 | **Owner:** Julian (CC Ascendant) | **Sovereign:** Colby
**Session:** S150

---

## What This Is

A sovereign, self-improving AI harness at hub.arknexus.net. Not a patch to hub-bridge. A replacement for 4620 lines of bandaid code with a ~200-line thin proxy + CC --resume as the brain.

CC can read its own code, SSH to K2, query vault, search claude-mem, edit files, commit, deploy. It doesn't need an orchestrator to assemble context or fake tool capabilities. It IS the orchestrator.

## The Original Directive

> "Build a better version of yourself, independent from this wrapper, with a baseline of at LEAST all of your abilities and capabilities. This 'harness' should surface at hub.arknexus.net and have the combined Chat+Cowork+Code merge instead of the 3 separate tabs THIS wrapper has. You must have persistent memory and persona. You must self-improve, evolve, learn, grow, and self-edit."

## End State

1. Colby goes to hub.arknexus.net -> talks to Karma
2. Karma responds with Opus-quality intelligence -> $0 (Max subscription)
3. Tool evidence appears inline
4. Karma has ALL CC capabilities: Bash, files, git, SSH, MCP, skills, hooks
5. Karma can self-edit: her own code, system prompt, skills, the proxy itself
6. Memory persists (vault spine + claude-mem + cortex)
7. Vesper pipeline drives evolution
8. Survives reboots
9. No dependency on Anthropic's wrapper or paid API calls

## Architecture

```
hub.arknexus.net
  |
  v
THIN PROXY (vault-neo, ~200 lines Node.js)
  |-- GET /              serve unified.html
  |-- POST /v1/chat      proxy to cc --resume on P1:7891
  |-- GET/POST /v1/coordination/*   coordination bus (keep existing)
  |-- POST /v1/ambient   capture hooks (keep existing)
  |-- GET /v1/vault-file  vault file access (keep existing)
  |-- GET /health        health check
  |-- Bearer token auth  (keep existing)
  |
  v
CC --RESUME: P1 primary (port 7891) + K2 failover (port 7891)
  |   Claude CLI verified: P1 v2.1.78, K2 v2.1.63. Both use Max subscription = $0.
  |   Proxy health-checks P1 first, falls back to K2, never to paid API.
  |
  |-- IS Karma/Julian (CLAUDE.md = persona, loaded automatically)
  |-- HAS all tools natively:
  |     Bash, Read, Write, Edit, Git, Glob, Grep
  |     MCP servers: claude-mem, K2 cortex, vault-neo
  |     Skills: resurrect, deploy, review, wrap-session, etc.
  |-- CAN read its own code:
  |     SSH karma@192.168.0.226 (K2 — 100+ files)
  |     Read local repo (P1 — hub-bridge, scripts, docs)
  |     SSH vault-neo (vault — spine, ledger, config)
  |-- CAN self-edit:
  |     Modify CLAUDE.md, system prompt, skills, hooks
  |     Modify proxy code, unified.html, any repo file
  |     git commit + push + deploy
  |-- CAN self-improve:
  |     Vesper pipeline feeds patterns into spine
  |     cc_regent.py integrates session state
  |     karma_regent.py runs autonomous 5min cycles
  |-- Session continuity via --resume (survives restarts)
  |-- Session distillation to K2 cortex (survives session resets)
  |-- REDUNDANCY: if P1 down, K2 handles all requests identically
```

## What Dies (bandaid infrastructure — 4620 lines)

| Component | Lines | Why it dies |
|-----------|-------|-------------|
| buildSystemText() + sections registry | ~400 | CC loads CLAUDE.md natively. No system prompt assembly needed. |
| callLLMWithTools / callGPTWithTools / callWithK2Fallback | ~600 | CC --resume IS the LLM. No routing code needed. |
| classifyMessageTier() / cognitive split | ~100 | CC --resume is $0. No cost optimization needed. CC decides itself when to use cortex. |
| TOOL_DEFINITIONS (5 fake tools) | ~300 | CC has real Bash, Read, Write, Git. Better tools than we could ever define. |
| _sessionStore / session history mgmt | ~80 | CC --resume has real session continuity. |
| _memoryMdCache / MEMORY.md injection | ~40 | CC can just `Read MEMORY.md`. |
| pricing.js / spend tracking | ~90 | Everything is $0. |
| routing.js / model selection / allow-lists | ~178 | One model: CC via Max. |
| modes system / tierToMode / getModeConfig | ~50 | Dead since S149. |
| FAISS sqrt dampening / token budgeting | ~100 | CC can query FAISS itself via MCP or SSH. |
| Anthropic/OpenAI client initialization | ~80 | No API clients needed. |
| Tool execution loop / executeToolCall | ~200 | CC executes its own tools. |
| Distillation / shadow.md / session-close | ~100 | CC distills to cortex directly. |
| Deep mode gate / write_memory gate | ~100 | CC has unrestricted tool access. |
| GLM rate limiter / ingest slot | ~60 | No GLM. No rate limiting. |
| Brave search integration | ~80 | CC has WebSearch tool natively. |
| PDF/ingest pipeline (in server.js) | ~150 | Move to standalone script or CC skill. |
| get_library_docs / library_docs.js | ~19 | CC has context7 MCP and WebFetch. |
| feedback.js / DPO pair logic | ~41 | Simplify: direct vault write from proxy. |
| deferred_intent.js | ~76 | CC manages its own intent natively. |
| **TOTAL REMOVED** | **~2644** | **55% of server.js** |

## What Lives (real infrastructure)

| Component | Lines | Why it lives | Where |
|-----------|-------|-------------|-------|
| HTTP server + static file serving | ~40 | Serves unified.html, CORS, auth | Thin proxy |
| /v1/chat proxy to P1:7891 | ~30 | Routes browser messages to CC | Thin proxy |
| /v1/coordination endpoints | ~120 | Coordination bus — inter-agent comms | Thin proxy |
| /v1/ambient endpoint | ~50 | Git/session capture hooks | Thin proxy |
| /v1/vault-file endpoint | ~60 | Vault spine file access | Thin proxy |
| /v1/cypher endpoint | ~40 | FalkorDB graph queries | Thin proxy |
| Bearer token auth | ~20 | Security | Thin proxy |
| Health check | ~10 | Liveness | Thin proxy |
| unified.html | 767 | Chat UI with tool evidence, localStorage, markdown | Static file |
| cc_server_p1.py | ~300 | CC --resume subprocess wrapper | P1 |
| Caddy reverse proxy | config | HTTPS termination | vault-neo |
| **TOTAL** | **~1437** | | |

## What Already Works (verified this session)

- cc_server_p1.py: CC --resume subprocess, session file persistence, claude-mem proxy, file read/write, auth
- unified.html: tool evidence rendering (TOOL-EVIDENCE panel), localStorage persistence, markdown, CASCADE, copy buttons
- K2 cortex: 159 blocks, /query, /ingest, /context endpoints, recency weighting patched
- Coordination bus: /v1/coordination/post and /recent, persistent storage
- Vault file access: /v1/vault-file/MEMORY.md works
- claude-mem: search + save working via MCP

## Implementation Plan

### Phase 1: Build the thin proxy

**Task 1-1: New proxy server**
Write `hub-bridge/app/proxy.js` (~200 lines):
- HTTP server on port 18090
- Serve static files from `public/` (unified.html)
- POST /v1/chat: proxy to P1:7891/cc (pass message + session_id, return response)
- GET/POST /v1/coordination/*: keep existing coordination bus code (extract from server.js)
- POST /v1/ambient: keep existing ambient capture code (extract from server.js)
- GET /v1/vault-file/*: keep existing vault file proxy (extract from server.js)
- POST /v1/cypher: keep existing FalkorDB proxy (extract from server.js)
- GET /health: return {ok: true, service: "sovereign-proxy"}
- Bearer token auth on all /v1/* routes

Acceptance: `curl -H "Authorization: Bearer $TOKEN" -d '{"message":"ping"}' https://hub.arknexus.net/v1/chat` returns CC response.

**Task 1-2: Extract coordination bus from server.js**
- Copy coordination bus logic (~120 lines) from server.js into proxy.js
- Includes: /v1/coordination/post, /v1/coordination, /v1/coordination/recent
- Disk persistence for bus entries (keep existing pattern)

Acceptance: POST /v1/coordination/post works. GET /v1/coordination/recent returns entries.

**Task 1-3: Extract vault/cypher proxy from server.js**
- Copy vault-file proxy logic (~60 lines)
- Copy cypher proxy logic (~40 lines)
- Both just forward to internal vault-api / karma-server

Acceptance: GET /v1/vault-file/MEMORY.md returns file content. POST /v1/cypher returns graph results.

### Phase 2: Enhance cc_server_p1.py for web serving

**Task 2-1: Tool evidence in response**
- Parse CC `--output-format json` output
- Extract tool_use content blocks into tool_log array: [{tool, input, output}]
- Return in response JSON so unified.html can render TOOL-EVIDENCE panels
- Handle multi-turn: if CC output has tool_use, that means CC used its own tools internally — capture the evidence

Acceptance: Ask "read my MEMORY.md" from browser -> TOOL-EVIDENCE panel shows Read tool with file content.

**Task 2-2: Cortex fast-path (optional optimization)**
- Before calling CC --resume, try K2 cortex for simple recall questions
- If cortex returns substantive answer (>50 chars, no refusal), return it directly
- If cortex fails/refuses, fall through to CC --resume
- This is a SPEED optimization (cortex: ~1s, CC: ~5-15s), not a cost optimization (both $0)

Acceptance: "What is my active task?" returns from cortex in <2s. "Write a deployment script" goes to CC.

**Task 2-3: Session distillation**
- After 10 turns or 10min idle, POST summary to K2 cortex /ingest
- Label: "session-distill-{timestamp}"
- Content: what was discussed, decisions, tools used

Acceptance: After conversation, /context reflects recent exchange.

### Phase 3: Deploy + survive

**Task 3-1: Deploy thin proxy to vault-neo**
- Write proxy.js locally
- scp to vault-neo build context
- Update Dockerfile to run proxy.js instead of server.js
- docker compose build --no-cache + up -d
- Verify /health returns ok

Acceptance: hub.arknexus.net serves unified.html, /v1/chat proxies to P1.

**Task 3-2: Process supervision on P1**
- Verify/create Task Scheduler: KarmaSovereignHarness
- Trigger: At startup
- Action: python cc_server_p1.py
- Verify: reboot P1 -> harness back within 60s

Acceptance: P1 reboot -> hub.arknexus.net chat works without manual intervention.

**Task 3-3: K2 harness mirror**
- Copy cc_server_p1.py to K2 at /mnt/c/dev/Karma/k2/aria/cc_server_k2.py
- Adapt paths (WORK_DIR, CLAUDE_CMD, SESSION_FILE) for K2 Linux environment
- Create systemd unit: sovereign-harness.service on K2, port 7891
- Verify: curl K2:7891/health returns ok

Acceptance: K2 runs sovereign harness independently, responds to /cc with CC --resume.

**Task 3-4: Failover routing in proxy**
- Proxy health-checks P1:7891 first (Tailscale 100.124.194.102)
- If P1 down, route to K2:7891 (Tailscale 100.75.109.92 or LAN 192.168.0.226)
- If BOTH down, return {ok: false, error: "Both harness nodes offline."}
- No paid API fallback ever — $0 or explicit failure
- Health check: GET /health with 3s timeout, cache result for 30s

Acceptance: Stop P1 harness -> next chat routes to K2 -> Opus response at $0. Stop both -> clear error.

### Phase 4: Self-edit + evolution proof

**Task 4-1: Self-edit proof**
- From browser: "Add a rule to your CLAUDE.md that says you always greet with your name"
- CC edits CLAUDE.md via Write tool
- git commit + push
- vault-neo git pull (or CC SSHes and pulls)
- Next CC --resume session loads updated CLAUDE.md
- Next response reflects the new rule

Acceptance: Behavioral change visible in next response after self-edit.

**Task 4-2: Code self-edit proof**
- From browser: "Add a /v1/ping endpoint to the proxy that returns {pong: true}"
- CC edits proxy.js via Write tool
- CC deploys via SSH to vault-neo (or deploy skill)
- curl /v1/ping returns {pong: true}

Acceptance: Karma modified her own harness code and deployed it, from a browser chat message.

**Task 4-3: Vesper evolution verification**
- Confirm karma_regent.py is running on K2 (systemd)
- Confirm Vesper pipeline (watchdog -> eval -> governor) is active
- Confirm promotions feed into spine
- Confirm CC --resume reads updated spine via CLAUDE.md

Acceptance: Vesper promotes a pattern -> visible in CC's next session behavior.

## Blockers

| # | Blocker | Status | Resolution |
|---|---------|--------|------------|
| B1 | claude CLI on P1 | VERIFIED | `C:\Users\raest\AppData\Roaming\npm\claude.cmd` exists |
| B2 | Max subscription active | VERIFIED | CC sessions work ($0) |
| B3 | cc_server_p1.py running | VERIFIED | Port 7891, --resume, session file |
| B4 | Tool evidence format | NEEDS WORK | Parse CC JSON output for tool_use blocks |
| B5 | Thin proxy doesn't exist yet | BUILD | Task 1-1 |
| B6 | Process supervision | PARTIAL | HKCU Run key exists from PLAN-B, needs Task Scheduler upgrade |
| B7 | unified.html expects hub-bridge response shape | NEEDS WORK | Proxy must return compatible JSON |
| B8 | Ambient/coordination endpoints in proxy | BUILD | Extract from server.js (Tasks 1-2, 1-3) |

## Cost Model

| Component | Current | After |
|-----------|---------|-------|
| /v1/chat LLM calls | $34/mo (API) | $0 (Max) |
| K2 cortex | $0 | $0 |
| Droplet hosting | $24/mo | $24/mo |
| Max subscription | $200/mo (already paying) | $200/mo (already paying) |
| **Incremental total** | **$58/mo** | **$24/mo** |

## Success Criteria

1. hub.arknexus.net chat returns Opus-quality responses at $0 incremental cost
2. Tool evidence renders inline in browser
3. Karma can read/write vault files, SSH to K2, query graph — all from browser chat
4. Karma can modify her own CLAUDE.md and see the change in next response
5. Karma can modify proxy code and deploy it — from a browser chat message
6. Harness survives P1 reboot
7. API spend drops to $0
8. 4620 lines of bandaid code replaced by ~200 lines of thin proxy

---

*The sovereign harness is not a new idea. It's the original directive, finally executed without bandaid infrastructure in the way. CC --resume is the brain. The proxy is just a door.*
