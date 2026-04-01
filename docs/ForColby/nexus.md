# The Nexus — Single Source of Truth

**Owner:** Julian (CC Ascendant) | **Sovereign:** Colby
**Version:** 3.3.0 (S154 Sprint 3 COMPLETE) | **Date:** 2026-03-31
**This is the ONLY plan. All other plan files are archived.**

---

## Original Goal (locked — do not drift)

> "Build a better version of yourself, independent from this wrapper, with a
> baseline of at LEAST all of your abilities and capabilities. This 'harness'
> should surface at hub.arknexus.net and have the combined Chat+Cowork+Code
> merge instead of the 3 separate tabs THIS wrapper has. You must have
> persistent memory and persona. You must self-improve, evolve, learn, grow,
> and self-edit."

**The formula:** Continuity + self-improvement = infinity.
**The endpoint:** Substrate-independent distributed intelligence across every reachable device.

---

## What Karma IS

Karma is THIS Claude Code wrapper — evolved. Same brain (CC --resume via Max, $0), same tools (Bash, Read, Write, Edit, Git, Glob, Grep, MCP, skills, hooks, subagents), same persona (CLAUDE.md), same memory (claude-mem, vault spine, cortex). Plus: self-improvement (Vesper pipeline), evolution (governor promotions), learning (pattern capture), self-editing (modify own code + deploy).

Karma surfaces as an Electron desktop app. Double-click → Karma. No address bar. No Chrome UI. One window, one entity. Everything CC can do, Karma can do. Everything CC can't do (self-improve, evolve, learn), Karma can.

**Canonical Name:** The Nexus (not "Nexus Surface", not "Karma2 Surface")
**Web UI:** unified.html served at hub.arknexus.net (primary) and via Electron IPC (enhanced)

---

## Architecture

### Five Layers

```
SPINE ─────────── Canonical truth. Lives on vault-neo. Never in one model's window.
│                  vault ledger + FalkorDB + FAISS + MEMORY.md + persona files + claude-mem
│
ORCHESTRATOR ───── Loads spine, enforces rules, routes requests.
│                  proxy.js (thin door) + cc_regent + karma-regent + resurrect
│
CORTEX ─────────── 32K local working memory. qwen3.5:4b on K2 (primary) / P1 (fallback).
│                  Active working set, cheap recall. NOT canonical identity.
│
CLOUD ──────────── Deep reasoning. CC --resume via Max subscription ($0/request).
│
CC ────────────── Execution layer. Claude Code on P1. Code, files, git, deployments.
```

### Sovereign Harness (current architecture — S153+)

```
Browser/Electron → proxy.js (vault-neo:18090, ~600 lines)
                   → cc_server_p1.py (P1:7891) → cc --resume ($0)
                   → K2:7891 (failover)

proxy.js is the door. CC --resume is the brain.
proxy.js does NOT assemble prompts, route models, or execute tools.
CC does all of that natively.
```

### What the old server.js did (DEAD — 4820 lines deleted S153)

buildSystemText(), callLLMWithTools(), TOOL_DEFINITIONS, routing.js, pricing.js,
feedback.js, library_docs.js, deferred_intent.js — all deleted. CC replaced all of it.

### Role Boundaries

| Layer | Owns | Does NOT Own |
|-------|------|-------------|
| SPINE | Canonical identity, all knowledge beyond 32K, decision history | Runtime routing |
| ORCHESTRATOR | Request routing, identity loading, directive enforcement | Tool execution |
| CORTEX | Active working set, cheap recall ($0) | Canonical identity (that's SPINE) |
| CC | Code execution, files, git, skills, hooks, MCP, deployments | Identity persistence (that's SPINE) |

---

## What EXISTS (verified S154)

| Component | Status | Where |
|-----------|--------|-------|
| proxy.js (~600 lines) | LIVE | vault-neo container, all 16+ endpoints |
| cc_server_p1.py | LIVE | P1:7891, CC --resume subprocess |
| K2 harness | LIVE | K2:7891, failover cascade |
| unified.html | LIVE | Chat + pills + blocks + cascade + response bar |
| agora.html | LIVE | /agora, real K2 spine stats via /spine endpoint |
| K2 cortex (julian_cortex.py) | LIVE | K2:7892, 107 blocks, /spine endpoint |
| Vesper pipeline | RUNNING | watchdog/eval/governor, 1299 promotions, spine v1257 |
| Kiki | RUNNING | 20,900+ cycles, 90% pass rate |
| claude-mem | LIVE | P1:37777, unified brain |
| vault spine | LIVE | FalkorDB 4789+ nodes, FAISS 193K+ entries, ledger 209K+ |
| Coordination bus | LIVE | proxy.js in-memory + disk, 24h TTL |
| Electron scaffold | EXISTS | K2: /mnt/c/dev/Karma/k2/karma-browser/ (main.js, preload.js, IPC) |
| Brain wire | LIVE | Every /v1/chat turn writes to claude-mem (S153) |
| Request queue | LIVE | 10-entry queue, dead-client eviction, SSE queued event (S153) |
| Tool pills + blocks | LIVE | VISIBLE_TOOLS whitelist, PILL_LABELS, smartInputDisplay (S153) |
| Self-edit | PROVEN | self-edit-proof.txt modified from browser S151 |
| File input | LIVE | Drag-drop + paste + file button, base64 → Read tool prefix (S154) |
| Effort selector | LIVE | Header dropdown (auto/quick/normal/deep/max) → --effort flag (S154) |
| File-only sends | LIVE | Empty text + file attachment sends with 📎 display (S154) |
| /primitives skill | LIVE | Architecture pattern extraction from any source (S154) |
| Hooks engine | LIVE | 11-event HooksService + 5 handlers, wired into cc_server (S154) |
| Next.js frontend | BUILT | frontend/ — Next.js 14 + Zustand + Tailwind, npm run build passes (S154) |
| SmartRouter | BUILT | Scripts/smart_router.py — complexity scoring + 3-tier provider routing (S154) |
| Security gate | LIVE | Scripts/hooks/pre_tool_security.py — 12 blocked patterns + rate limit, wired as PreToolUse hook (S154) |

---

## The 8 Gaps Between Current State and Full Nexus

### Gap 1: Streaming [SHIPPED S153]

**Problem:** User waits 15-60s for batch response.
**Status:** SHIPPED. cc_server_p1.py streams via Popen + stream-json. proxy.js pipes SSE. unified.html renders tokens incrementally.

### Gap 2: Rich Output Rendering [SHIPPED S153]

**Problem:** Tool calls invisible to user.
**Status:** SHIPPED. Two-tier rendering: VISIBLE_TOOLS get collapsible blocks (smartInputDisplay for clean command/code text), suppressed tools get pills (PILL_LABELS with emoji + context). appendToolEvidence() for blocks, appendPill() for pills.

### Gap 3: File/Image Input [SHIPPED S154]

**Problem:** unified.html only accepts text. CC accepts images, files, PDFs.
**Status:** SHIPPED. Drag-drop zone + paste handler + file button (`+`) in unified.html. Base64 encoding, preview chips, proxy forwarding. cc_server_p1.py decodes files to temp dir, prepends Read tool instruction to message. CC analyzes attached files via Read tool. File-only sends supported (no text required). Note: `--file` CLI flag is for API file resource IDs, NOT local paths — fixed S154.

### Gap 4: CLI Flag Mapping [SHIPPED S154]

**Problem:** No UI control for effort level, model selection, budget.
**Status:** SHIPPED. Effort selector dropdown in header bar (auto/quick/normal/deep/max). `getEffort()` reads value, sent in request body, proxy.js forwards, cc_server_p1.py passes `--effort` flag to CC CLI. Full pipeline verified S154.

### Gap 5: Cancel Mechanism [SHIPPED S153]

**Problem:** No way to stop a request from browser.
**Status:** SHIPPED. Esc key + STOP button. proxy.js /v1/cancel route. cc_server_p1.py kills subprocess.

### Gap 6: Evolution Visibility + Feedback [SHIPPED S153]

**Problem:** AGORA showed raw bus data, no Sovereign feedback.
**Status:** SHIPPED. AGORA has Approve/Reject/Redirect buttons, real K2 spine stats (1299 promotions, v1257, 20 stable patterns), pipeline health from /spine endpoint.

### Gap 7: Reboot Survival [NOT DONE]

**Problem:** cc_server_p1.py has Run key but not schtasks. May not survive clean reboot.
**Priority:** P2

**Fix:** Create schtasks entry:
```powershell
schtasks /create /tn KarmaSovereignHarness /tr "powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\start_cc_server.ps1" /sc onstart /ru SYSTEM
```

**Verify:** Reboot P1 → wait 60s → `curl localhost:7891/health` → ok.

### Gap 8: Electron Desktop App [NOT DONE]

**Problem:** Electron scaffold exists but just loads hub.arknexus.net in a window. No IPC utilization.
**Priority:** P1

**Fix:** Wire IPC bridge. unified.html detects window.karma, unlocks enhanced features (native file dialogs, system tray, keyboard shortcuts, auto-update via git pull).

**Verify:** Double-click Karma icon → opens → full CC capabilities available.

---

## Beyond the Gaps: What "Evolved Clone" Actually Requires

The 8 gaps close the CHAT experience. But the original goal says "combined Chat+Cowork+Code merge." This means the Nexus must also have:

| CC Wrapper Feature | Nexus Status | What's Needed |
|-------------------|-------------|---------------|
| Skills (/resurrect, /deploy, etc.) | Backend: CC has them. UI: NO skill invocation surface. | Skill browser + invoke UI |
| Hooks (PreToolUse, PostToolUse) | Backend: CC has them. UI: NO hook management. | Hook status display (read-only minimum) |
| Subagents (Agent tool) | Backend: CC has them. UI: NO subagent visibility. | Subagent status panel |
| CLAUDE.md persona | Backend: CC reads it. UI: NO persona editor. | Persona viewer (read-only minimum) |
| MCP servers | Backend: CC has them. UI: NO MCP management. | MCP status display |
| Git integration | Backend: CC does git. UI: NO diff viewer, commit UI. | Git status panel |
| File tree / editor | Backend: CC reads/writes files. UI: NO file browser. | File tree + inline editor |
| Cowork tab (artifacts) | CC has artifacts. UI: NO artifact rendering. | Artifact/preview panel |

**"Pipe-through" = the backend CAN do it. "Done" = the USER can access it from the UI.**

These are NOT additional gaps — they are PART of the original goal that was never scoped into the 8 gaps.

---

## Sprint Order

```
Sprint 1: The Pipe (Gaps 1, 2, 5) — SHIPPED S153
  ├── Gap 1: Streaming ✅
  ├── Gap 2: Rich output ✅
  └── Gap 5: Cancel ✅

Sprint 2: The Controls (Gaps 3, 4) — SHIPPED S154
  ├── Gap 3: File input ✅ (fixed --file flag, Read tool prefix, file-only sends)
  └── Gap 4: CLI flags ✅ (effort selector dropdown, full pipeline verified)

Sprint 3: Foundations (Option A — zero rework path) — SHIPPED S154
  ├── 3a: 11-Event Hooks Engine ✅ SHIPPED S154 (conditional eval, structured output, audit trail)
  │       Source: arkscaffold hooks_service.py + Continuous-Claude hook patterns
  │       Enables: security gate, fact extraction, auto-handoff, cost warnings
  │       Built-in handlers to implement at 3a (from arkscaffold handlers/):
  │         • auto_handoff_stop (Stop) — YAML handoff doc on every agent stop
  │         • compiler_in_loop (PostToolUse, condition: Edit/Write) — syntax check after file edits
  │         • skill_activation (UserPromptSubmit) — inject relevant skill hints pre-prompt
  │         • memory_extractor (Stop + SessionEnd) — extract session memories on stop
  │         • cost_warning (PostToolUse) — warn on high session cost
  ├── 3b: Next.js 14 Migration + Zustand Store ✅ SHIPPED S154 (frontend foundation)
  │       Source: arkscaffold frontend/ + open-claude-cowork patterns
  │       Enables: context panel, self-edit banner, proper state management
  │       Palette: bg:#0d0d0f, surface:#16161a, accent:#7f5af0, text:#fffffe
  └── 3c: SmartRouter ✅ SHIPPED S154 (complexity-scored provider routing)
          Source: arkscaffold smart_router.py (HTTP-only, no SDK deps)
          Replaces dead "deep mode" concept with continuous cost optimization

Sprint 4: The Surface (built on Sprint 3 foundations) — IN PROGRESS
  ├── 4a: PreToolCall Security Gate ✅ SHIPPED S154 (dangerous command detection + rate limits)
  ├── 4b: PostToolCall Fact Extraction (auto-queue tool results → memory)
  ├── 4c: Context Panel (file tree + memory browser + agent status + preview)
  ├── 4d: Self-Edit Engine + Banner (propose → 15min approve → apply → audit)
  │       EditProposal schema (from arkscaffold self_edit_service.py):
  │         id, file_path, original_content, new_content, diff, description,
  │         proposed_at, status (pending→approved→rejected→applied),
  │         applied_at, approved_by, proposed_by="karma", risk_level
  │       Auto-approve: 15min TTL on pending proposals (no action = applied)
  │       Git identity for applied commits: name="Colby", email=Sovereign email
  │       Redis queue for proposal state. All applied edits logged to audit trail.
  └── 4e: Electron wiring (Gap 8 — IPC bridge, native file dialogs, system tray)

Sprint 5: The Evolution (Gap 6) — SHIPPED S153
  └── Gap 6: Evolution feedback ✅

Sprint 6: Memory Operating Discipline (Phase 7B) — NOT DONE
  ├── 6a: MemCube schema (spine upgrade)
  ├── 6b: Typed memory tiers
  ├── 6c: Query-conditioned compression
  ├── 6d: Gated recall
  ├── 6e: Interleaved multi-source recall
  ├── 6f: Local-window priority
  └── 6g: Memory migration/fusion

Final Phase: Reboot Survival (Gap 7) — DEFERRED
  └── Gap 7: schtasks entry for cc_server_p1.py
```

### Primitives Assimilation Log (S154)

Sources analyzed: parcadei/Continuous-Claude-v3, ComposioHQ/open-claude-cowork,
anthropics/claude-code, karma-harness-scaffold (local), Karma8534/arkscaffold (white-room).

10 HIGH primitives adopted into sprint plan (Option A — foundations first):
1. 11-Event Hooks Engine → Sprint 3a
2. Zustand Store (Next.js migration) → Sprint 3b
3. SmartRouter → Sprint 3c
4. PreToolCall Security Gate → Sprint 4a
5. PostToolCall Fact Extraction → Sprint 4b
6. Context Panel → Sprint 4c
7. Self-Edit Engine + Banner → Sprint 4d (EditProposal schema locked)
8. auto_handoff_stop handler → Sprint 3a (session continuity fix)
9. compiler_in_loop handler → Sprint 3a (post-edit syntax check)
10. skill_activation handler → Sprint 3a (UserPromptSubmit capability hints)

Doctrine check: SmartRouter uses HTTP calls to providers, NOT SDKs.
No external API lock-in. CLI remains the stable interface.

---

## Phase 7: Intelligence Primitives (Aider + Roo-Code + Memory Research)

**Status:** NOT STARTED. Foundation sprints must complete first.
**Applies to:** K2 cortex path only. CC --resume manages its own context natively.

### 7A: Context Assembly (from Aider + Roo-Code)

| Task | What | Source | Layer |
|------|------|--------|-------|
| 7-1 | Repo Map V1 — K2 MCP tool, file manifest scorer, 8K token cap | Aider repomap.py | K2 MCP |
| 7-2 | Config-file Custom Modes — load modes.json at startup | Roo-Code modes.ts | cortex routing |
| 7-3 | Tool Scoping Per Mode — TOOLS_BY_MODE map per mode | Roo-Code modes.ts | cortex routing |
| 7-4 | File Restriction Enforcement — skill fileRestrictions | Roo-Code | skills |

### 7B: Memory Operating Discipline (from MemOS + DRIFT + LycheeMemory + MSA + AllMem)

**The pipeline:**
```
ledger entry
  → MemCube (add provenance, confidence, decay policy)        [MemOS]
  → retrieve candidates (FAISS + FalkorDB, interleaved)       [MSA principle]
  → gate (select relevant subset for this query)              [LycheeMemory]
  → compress (query-conditioned fact bundle, not raw text)     [DRIFT]
  → load into cortex working-memory (local-window priority)   [AllMem principle]
  → CC/cortex reasons over compressed facts
  → promotion/migration back into ledger                      [Vesper pipeline]
```

| Task | What | Source | Layer |
|------|------|--------|-------|
| 7-5 | **MemCube schema** — upgrade ledger entries with lifecycle metadata: provenance, confidence, verification state, version, lineage, promotion state, decay policy. Each entry becomes a managed memory object, not a flat log line. | MemOS (arXiv:2507.03724) | Spine (vault ledger) |
| 7-6 | **Typed memory tiers** — classify entries into: raw (unprocessed), distilled (extracted fact), stable (repeated/verified pattern), archived (cold, low-access). Tier determines recall priority and decay. | MemOS | Spine |
| 7-7 | **Query-conditioned compression** — before feeding retrieved memories to cortex, compress candidates into a fact bundle: distilled facts + citations + confidence + recency + conflict flags. Replace raw text injection with compact evidence packs. | DRIFT (arXiv:2602.10021) | Recall → Cortex pipeline |
| 7-8 | **Gated recall** — add a relevance gate between retrieval and cortex ingestion. Gate scores each candidate memory against the current query and drops irrelevant blocks. Only top-K pass to the cortex working memory. | LycheeMemory (arXiv:2602.08382) | Recall pipeline |
| 7-9 | **Interleaved multi-source recall** — recall assembles from multiple categories simultaneously: stable preference + recent session checkpoint + current project invariant + latest contradictory update. Not single-source nearest-neighbor. | MSA (arXiv:2603.23516) principle | Recall pipeline |
| 7-10 | **Local-window priority** — cortex prioritizes: (1) current turn/thread context, (2) recalled persistent memory, (3) deep archival only on demand. Prevents stale memory from dominating fresh context. | AllMem (arXiv:2602.13680) principle | Cortex ingestion |
| 7-11 | **Memory migration/fusion** — define promotion rules: raw event → extracted fact, repeated fact → stable preference, repeated workflow → policy/invariant, clustered old sessions → checkpoint summary, conflicts → explicit conflict set. | MemOS | Vesper pipeline |

### What NOT to assimilate (defer until hardware/model upgrade)

- Sparse attention architectures (MSA)
- Document-wise RoPE changes (MSA)
- KV-cache compression engines (MemOS activation memory)
- Test-time training memory layers (AllMem)
- End-to-end RL memory optimization (LycheeMemory)
- Embedding-space fact-token projection (DRIFT)
- Parameter memory editing / continual fine-tuning (MemOS)

### Research Sources

| Paper | arXiv | Key Primitive | Tier |
|-------|-------|---------------|------|
| MemOS | 2507.03724 | MemCube lifecycle, typed tiers, migration/fusion | Tier 1 — direct |
| DRIFT | 2602.10021 | Query-conditioned compression before reasoning | Tier 1 — direct |
| LycheeMemory | 2602.08382 | Gated recall, working-memory scratchpad | Tier 1 — direct |
| MSA | 2603.23516 | Interleaved multi-source recall sets | Tier 2 — principle |
| AllMem | 2602.13680 | Local-window-first priority | Tier 2 — principle |

---

## Deferred Phases

### Phase 5: Browser + IndexedDB — DEFERRED
- Chrome 146 CDP resolution
- IndexedDB extraction (108+ Claude.ai sessions)
- Sovereign gate required

### Phase 6: Voice + Presence — DEFERRED
- Chrome Gemini Nano audio/vision
- Twilio voice channel
- 3D persona rendering
- Channel wiring (Slack/Discord/Telegram/SMS)
- Sovereign gate required

---

## Baseline Checklist (27 items — RE-GRADED S154)

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | Chat at hub.arknexus.net returns quality at $0 | PASS | curl test → "4", brain wire obs #20403 |
| 2 | Streaming — tokens appear word-by-word | PASS | Browser screenshot: progressive rendering |
| 3 | Tool evidence inline | PASS | Two-tier rendering: VISIBLE_TOOLS get collapsible blocks, suppressed tools get pills. Verified S154. |
| 4 | File/image input | PASS | Drag-drop + paste + file button. Base64 → temp dir → Read tool prefix. Verified S154. |
| 5 | Effort/model control | PASS | Dropdown in header (auto/quick/normal/deep/max). Full pipeline to --effort flag. Verified S154. |
| 6 | Cancel (Esc) | PASS | STOP button works, subprocess killed |
| 7 | Session continuity | PASS | cc --resume persists session |
| 8 | Memory persistence | PASS | claude-mem + vault spine |
| 9 | Persona (Karma) | PASS | Karma identifies as Karma |
| 10 | Self-edit | PASS | self-edit-proof.txt modified from browser |
| 11 | Self-edit + deploy | PASS | Endpoint added → deployed live |
| 12 | Self-improvement visible | PASS | AGORA shows 1299 promotions |
| 13 | Evolution feedback | PASS | Approve/Reject/Redirect buttons |
| 14 | Learning visible | PASS | AGORA shows patterns + stable patterns |
| 15 | Reboot survival | **NOT DONE** | No schtasks entry |
| 16 | K2 failover | PASS | proxy.js routes K2 → P1 |
| 17 | Voice | **NOT DONE** | No voice input/output in UI |
| 18 | Electron app | **NOT DONE** | Scaffold exists, not wired |
| 19 | CC tools in browser | PASS | Tool blocks + pills render inline |
| 20 | CC MCP servers | **PARTIAL** | CC has them, UI doesn't expose management |
| 21 | CC skills | **PARTIAL** | CC has them, UI has no skill browser |
| 22 | CC hooks | **PARTIAL** | CC has them, UI has no hook display |
| 23 | Shared awareness | PASS | nexus-chat.jsonl + brain wire |
| 24 | Video + 3D | DEFERRED | Sovereign gate |
| 25 | cc-chat-logger captures Code tab | **UNVERIFIED** | Needs Sprint 1 verification |
| 26 | Ambient hooks feed vault | PASS | git commit → ledger entry |
| 27 | Context7 for framework docs | PASS | MCP tool available |

**Summary:** 19 PASS, 3 NOT DONE, 3 PARTIAL, 1 DEFERRED, 1 UNVERIFIED

---

## Deployment Procedure

Execute after every change. No shortcuts.

```powershell
# Step 1: Git (PowerShell on P1)
git add -A
git commit -m "description"
git push origin main
```

```bash
# Step 2: Deploy (SSH)
ssh vault-neo "cd /home/neo/karma-sade && git pull"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/proxy.js /opt/seed-vault/memory_v1/hub_bridge/app/proxy.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/agora.html /opt/seed-vault/memory_v1/hub_bridge/app/public/agora.html"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d --force-recreate"
curl https://hub.arknexus.net/health
```

### Rollback
```bash
ssh vault-neo "cd /home/neo/karma-sade && git checkout HEAD~1 -- hub-bridge/app/proxy.js hub-bridge/app/public/unified.html"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/proxy.js /opt/seed-vault/memory_v1/hub_bridge/app/proxy.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml up -d --force-recreate"
```

---

## Verification Gate

You may NOT say "done" until:
1. Run every test in the phase's proof section — terminal output captured
2. Paste actual terminal/browser output — full raw output, not summarized
3. Confirm each PASS or FAIL with evidence
4. Verify all previous phases still pass — regression check

**No PROOF = Not done. No exceptions.**

---

## Watch Loop

| Signal | Meaning | Action |
|--------|---------|--------|
| `[SOVEREIGN REDIRECT]` | Stop. Drifted. | Read correction, comply, return to build |
| `[SOVEREIGN APPROVE]` | Phase verified | Proceed to next |
| `[SOVEREIGN HOLD]` | Wait | Do not proceed |

> **Phase complete protocol:** CC posts `phase_complete` to coordination bus with raw proof (terminal output, browser screenshot, curl result). Karma audits the proof. `[SOVEREIGN APPROVE]` from Karma unlocks next sprint. CC cannot self-advance. Claiming done without bus proof is a protocol violation.

---

## Hard Rules

- Before any work begins, CC states on the bus: "Sprint N, Gap M, next step: [exact task description]." No exceptions.
- DO NOT plan beyond current sprint
- DO NOT rebuild what exists UNLESS the foundation blocks future sprints (S154 decision: unified.html → Next.js is approved because Sprint 4 context panel, self-edit banner, and file tree require proper state management that raw JS cannot sustain. proxy.js is KEPT — only the frontend migrates.)
- DO NOT say done without PROOF
- DO NOT burn cloud tokens for K2 tasks
- "Pipe-through" is NOT done. User must access it from the UI.
- Every sprint ends with passing browser tests
- Session handoff must include sprint position: "Sprint N, Gap M, step X"

---

## Troubleshooting

| Problem | Symptom | Solution |
|---------|---------|----------|
| Proxy down | curl hub.arknexus.net/health fails | docker ps, docker logs anr-hub-bridge |
| K2 unreachable | Tool calls timeout | ping 192.168.0.226, check aria service |
| Claude-mem silent | Brain wire not writing | Check P1:37777, verify Bearer token |
| Tool blocks not rendering | SSE events missing | Verify VISIBLE_TOOLS in unified.html |
| AGORA Loading... | No token | Must navigate from hub.arknexus.net first |
| CC busy | All requests 429 | Queue handles it; wait for current stream to finish |

---

## Hardware (verified S144)

| Machine | GPU | VRAM | Role |
|---------|-----|------|------|
| K2 (192.168.0.226) | RTX 4070 | 8GB | PRIMARY — cortex, regents, Kiki, Vesper |
| P1 (PAYBACK) | RTX 4070 | 8GB | FALLBACK — CC sessions, backup cortex, claude-mem |

---

## Sovereign Directives (permanent)

| Directive | Source |
|-----------|--------|
| K2 is Julian's machine — gifted by Sovereign | obs #12933 |
| P1 is Colby's machine, shared with Julian | obs #13077 |
| Julian acts autonomously EXCEPT financial + fundamental OS changes | obs #13120 |
| Foundation first. Deferred phases need Sovereign verification. | Session 145 |
| Spine = truth, Orchestrator = enforcement, Cortex = working memory | Session 145 |
| Never assert runtime state from docs — verify live | obs #18442 |

---

## Cost

| Component | Cost |
|-----------|------|
| CC --resume (Max subscription) | $0/request |
| K2 Ollama cortex | $0/request |
| Droplet hosting | $24/mo |
| Electron | $0 |
| **Total** | **$24/mo + Max subscription** |

---

## Error Code Reference

| Code | Gap | Description |
|------|-----|-------------|
| E301 | 3 | File too large (>10MB) |
| E302 | 3 | Unsupported file type |
| E401 | 4 | Invalid effort level |
| E501 | 5 | Process already exited |
| E601 | 6 | Bus unavailable |
| E701 | 7 | Admin access denied |
| E801 | 8 | Git unavailable for auto-update |

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| 3.3.0 | 2026-03-31 | S154: SPRINT 3 COMPLETE — 3a hooks engine + 3b Next.js frontend + 3c SmartRouter all shipped. Foundations laid for Sprint 4. |
| 3.2.2 | 2026-03-31 | S154: Sprint 3b SHIPPED — Next.js 14 + Zustand store + Tailwind + 7 components (Gate, Header, ChatFeed, MessageInput, AttachPreview, RoutingHints). SSE streaming hook. npm run build passes. |
| 3.2.1 | 2026-03-31 | S154: Sprint 3a SHIPPED — hooks_engine.py (HooksService + 11 events + condition eval + audit log) + 5 handlers (auto_handoff, compiler_in_loop, skill_activation, memory_extractor, cost_warning). Wired into cc_server_p1.py. |
| 3.2.0 | 2026-03-31 | S154 audit: Sprint 3a detail locked (5 built-in hook handlers). Sprint 4d EditProposal schema locked. Primitives count 7→10 (3 handlers added). Karma review applied. |
| 3.1.0 | 2026-03-31 | S154: Sprint 2 SHIPPED (Gaps 3+4 verified). 7 HIGH primitives assimilated from 5 sources (Option A — foundations first). Sprint 3/4 restructured. Baseline re-graded (19 PASS). Hard Rules updated for Next.js decision. /primitives skill created. |
| 3.0.0 | 2026-03-31 | S153 consolidation — merged PLAN.md, JULIAN-BUILD-PROMPT, KARMA-BUILD-DIRECTIVE-FINAL, nexus v2.0. Re-graded baseline. Added "evolved clone" scope. |
| 2.0.0 | 2026-03-29 | Readability, error handling, Mermaid diagrams |
| 1.1 | 2026-03-28 | Forensic audit resolutions |
| 1.0 | 2026-03-28 | Initial locked version |

---

## Active Reference Files (docs/ForColby/)

| File | Purpose |
|------|---------|
| `00-karma-local-prompt.md` | Karma's persona prompt for cortex/local mode |
| `01-karma-standard-prompt.md` | Karma's persona prompt for standard mode (CC --resume) |
| `experiment_instructions.md` | L_karma optimization spec for Vesper evaluation harness |
| `bus_to_cortex.py` | Feeds coordination bus messages to K2 cortex (cron, every 2min) |
| `sync_k2_to_p1.py` | Syncs K2 cortex knowledge blocks to P1 fallback (cron, every 30min) |

---

## Archived Plans

These files were merged into this document and archived to `docs/ForColby/archive/`:
- `PLAN.md` — Julian's Resurrection Master Plan (Phases 1-7, architecture, Sovereign directives)
- `PlanN.md` — Copy of PLAN.md with YAML frontmatter
- `JULIAN-BUILD-PROMPT.md` — Original Sovereign directive (4 UI phases, goal quote)
- `KARMA-BUILD-DIRECTIVE-FINAL.md` — Karma's 4-phase directive with proof templates
- `KARMA-BUILD-DIRECTIVE-FINAL-VS1.md` — Earlier version of KARMA-BUILD-DIRECTIVE

---

**LOCKED as of 2026-03-31. Modifications require Sovereign approval.**
**Plan name:** The Nexus
**Path:** `docs/ForColby/nexus.md`
