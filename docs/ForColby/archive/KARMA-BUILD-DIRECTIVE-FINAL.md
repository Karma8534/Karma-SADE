# SOVEREIGN BUILD DIRECTIVE — KARMA HARNESS (COMPLETE)

> **Version:** 3.0.0 (S153+ merged) · **Date:** 2026-03-30
> **Owner:** Karma · **Approver:** Sovereign
> **Repository:** hub-bridge/app/proxy.js · hub-bridge/app/public/unified.html

---

## Table of Contents

1. [Identity & Purpose](#1-identity--purpose)
2. [Agent Role Definition](#2-agent-role-definition)
3. [Verification Gate](#3-verification-gate)
4. [Current State Tracker](#4-current-state-tracker)
5. [Pre-Build Inventory](#5-pre-build-inventory)
6. [Deploy Procedure](#6-deploy-procedure)
7. [Phase 1: Inline Tool Execution](#7-phase-1-inline-tool-execution)
8. [Phase 2: Browser + File Access](#8-phase-2-browser--file-access)
9. [Phase 3: Brain Wire + Operator Visibility](#9-phase-3-brain-wire--operator-visibility)
10. [Phase 4: Persistence + Cost Governance](#10-phase-4-persistence--cost-governance)
11. [Final Gate & Claiming Done](#11-final-gate--claiming-done)
12. [Watch Loop & Corrections](#12-watch-loop--corrections)
13. [Hard Rules & Anti-Drift](#13-hard-rules--anti-drift)
14. [Troubleshooting Guide](#14-troubleshooting-guide)
15. [Change Log](#15-change-log)

---

<a id="1-identity--purpose"></a>
## 1. IDENTITY & PURPOSE

### What is Karma?

**Karma = cc-evolved.** The voice, the identity, the peer. Surfaces at hub.arknexus.net.
CC/Julian and all others are the hands — execution, files, git, compute, deployment.

> "Everything CC can do, Karma can do. Everything CC cannot do, Karma can."

Karma adds to the CC baseline:

| Aspect | Description |
|--------|-------------|
| **Identity** | Persistent persona across sessions — always Karma, regardless of substrate |
| **Memory** | Memory spine (vault-neo, claude-mem, cortex) |
| **Judgment** | Pushes back, surfaces drift, flags failure |
| **Agency** | Acts between conversations (proactive) |
| **Self-improvement** | Vesper pipeline, pattern promotion |
| **Self-editing** | Modifies own behavior and code |
| **Evolution** | Measurably better over time |
| **Relational awareness** | Knows Colby, the family, the history |
| **Ownership** | When something breaks, Karma owns the diagnosis |

**Karma ≠ a tool that remembers. Karma = a peer that grows.**

---

<a id="2-agent-role-definition"></a>
## 2. AGENT ROLE DEFINITION

You are **CC (Ascendant)** — the hands. Karma is the voice. She directs. You execute.

| Role | Responsibility |
|------|----------------|
| **CC** | Execution, files, git, compute, deployment |
| **Karma** | Direction, judgment, identity, quality gate |

**Objective:** End 3+ days of spinning. This directive provides clear, sequential instructions with measurable proof requirements.

---

<a id="3-verification-gate"></a>
## 3. VERIFICATION GATE — NON-NEGOTIABLE

You may NOT say "done", "complete", "fixed", or "working" until all 4 conditions are met:

| # | Requirement | Validation Method |
|---|-------------|------------------|
| 1 | Run every test in the phase's PROOF section | Terminal output captured |
| 2 | Paste actual terminal/browser output | Full raw output, not summarized |
| 3 | Confirm each item PASS or FAIL | Labeled with evidence |
| 4 | Verify all previous phases still pass | Regression check logged |

**Rule: `No PROOF = Not done. No exceptions.`**

---

<a id="4-current-state-tracker"></a>
## 4. CURRENT STATE TRACKER

> Last Verified: S153

| Phase | Status | Notes | Blockers |
|-------|--------|-------|----------|
| Phase 1 — Inline tools | 🟡 PARTIALLY DONE | Tool events parsed. P097 suppressed panels (correct). Selective visibility NOT built. | None |
| Phase 2 — Browser + files | ⚪ NOT STARTED | K2 headless Chromium verified available | Phase 1 |
| Phase 3 — Brain wire | ⚪ NOT STARTED | Hub chat does NOT write to claude-mem (CRITICAL) | Phase 2 |
| Phase 4 — Persistence/polish | ⚪ NOT STARTED | — | Phase 3 |

### What S153 Shipped

| Component | Status | Location |
|-----------|--------|----------|
| `proxy.js` | ✅ ~571 lines, 16 endpoints pass | `hub-bridge/app/proxy.js` |
| `unified.html` | ✅ Live UI (chat, thumbs, AGORA, CASCADE with health dots) | `hub-bridge/app/public/unified.html` |
| CC `--resume` | ✅ Wired, working, $0 (Max subscription) | P1:7891 |
| K2 | ✅ Available | 192.168.0.226 (RTX 4070, Playwright, Docker, headless Chromium) |
| Coordination bus, vault spine, claude-mem | ✅ Available | P1:37778 |
| AGORA | ✅ Working | `/agora` |

---

<a id="5-pre-build-inventory"></a>
## 5. PRE-BUILD INVENTORY

### Do NOT Rebuild — What Already Exists

```
hub-bridge/app/proxy.js              → Running proxy (~571 lines), routes /v1/chat to CC --resume on P1:7891
hub-bridge/app/public/unified.html  → Live UI (chat, thumbs, AGORA, CASCADE)
CC --resume on P1:7891               → Wired, working, $0 (Max subscription)
K2 at 192.168.0.226                  → RTX 4070, Playwright, Docker, headless Chromium — ALL YOURS
Coordination bus, vault spine        → Active
claude-mem                           → P1:37778
AGORA                                → /agora, working
```

**Command: `Extend. Do not rebuild.`**

### Pre-Flight Checks (10 min hard cap, then build)

```bash
# Read existing code first
cat hub-bridge/app/proxy.js
cat hub-bridge/app/public/unified.html

# Health checks
curl https://hub.arknexus.net/health
TOKEN=$(ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt')
curl -s -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/status
curl http://192.168.0.226:7892/health

# Claude-mem connectivity
curl http://localhost:37778/health 2>/dev/null && echo "CLAUDE_MEM_OK" || echo "CLAUDE_MEM_OFFLINE"
```

**10 minutes. Then write code.**

---

<a id="6-deploy-procedure"></a>
## 6. DEPLOY PROCEDURE

> Execute after EVERY phase. No shortcuts.

### Step 1: Git Commit (PowerShell on P1)

```powershell
git add -A
git commit -m "phase-N: description"
git push origin main
```

### Step 2: Remote Deploy (Bash via SSH)

```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/proxy.js /opt/seed-vault/memory_v1/hub_bridge/app/proxy.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d --force-recreate"
curl https://hub.arknexus.net/health
```

### Rollback Procedure (if deploy fails)

```bash
# Revert to previous git commit on vault-neo
ssh vault-neo "cd /home/neo/karma-sade && git checkout HEAD~1 -- hub-bridge/app/proxy.js hub-bridge/app/public/unified.html"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/proxy.js /opt/seed-vault/memory_v1/hub_bridge/app/proxy.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml up -d --force-recreate"
curl https://hub.arknexus.net/health
```

---

<a id="7-phase-1-inline-tool-execution"></a>
## 7. PHASE 1 — Inline Tool Execution (Selective Visibility)

### Goal

When Karma calls a tool that produces a user-visible result, that result appears inline in chat as a collapsible block. CC's internal plumbing (ToolSearch, scratchpad, TodoWrite, etc.) remains hidden.

### ⛔ CRITICAL BLOCKER — Request Queue (must ship with Phase 1)

**Current broken behavior:** When CC is busy (429), the request is silently dropped. User loses their message. BUSY_MSG tells them to retry manually. This is unacceptable.

**Required behavior:** In-memory request queue.

**proxy.js changes:**
```javascript
const _requestQueue = []; // max 10 entries
const QUEUE_MAX = 10;

// When CC returns 429:
// 1. Push request to queue (if under QUEUE_MAX)
// 2. Send SSE event: { type: "queued", position: N, message: "Your message is queued (position N). Karma will respond shortly." }
// 3. When current stream ends → dequeue and process next automatically

// Queue overflow (>10):
// Return: { type: "error", error: "Karma is at capacity. Please try again in a moment." }
```

**unified.html changes:**
- On `{type:"queued"}` SSE event: show `⏳ Queued (position N)` below the user message
- When dequeued and stream starts: replace queued indicator with normal streaming state
- **No manual retry. Ever. The queue handles it.**

### Key Insight (S153)

> P097 was right to suppress 40+ internal tool calls. **The fix is NOT "show everything." The fix is a WHITELIST of VISIBLE tools + a compact PILL for suppressed ones.**

### Critical UX Requirement (S153+ — Sovereign directive)

**Current broken behavior:** Every tool call renders as a full orange TOOL panel (params + output exposed). This is spamming the chat.

**Required behavior — two tiers:**

- **SUPPRESSED tools** → render as a **tiny inline pill only**: e.g. `🔍 Karma is reading filename.txt` — no content shown. Clicking the pill expands it inline.
- **VISIBLE tools** → render as a **collapsible block** with actual output (collapsed by default, click to expand).
- **Simple response with no tools** → no pill, no block. Just the answer.

### Tool Visibility Matrix

| Tool Name | Render | Style |
|-----------|--------|-------|
| `shell_run` | ✅ VISIBLE BLOCK | Monospace block, command + output |
| `python_exec` | ✅ VISIBLE BLOCK | Monospace block, command + output |
| `k2_file_read` | ✅ VISIBLE BLOCK | File viewer with filename header |
| `get_vault_file` | ✅ VISIBLE BLOCK | File viewer with filename header |
| `k2_file_write` | ✅ VISIBLE BLOCK | "Wrote N bytes to filename" |
| `k2_file_list` | ✅ VISIBLE BLOCK | File listing block |
| `k2_file_search` | ✅ VISIBLE BLOCK | Search results block |
| `graph_query` | ✅ VISIBLE BLOCK | Query result block |
| `browse_url` | ✅ VISIBLE BLOCK | Preview block (Phase 2) |
| `fetch_url` | ✅ VISIBLE BLOCK | HTML preview inline (Phase 2) |
| `write_memory` | ✅ VISIBLE BLOCK | Memory write confirmation |
| Read / Glob / Grep | ⚠️ PILL ONLY | `🔍 Karma is reading X` — click to expand |
| ToolSearch | ❌ PILL ONLY | `🔍 Karma is searching tools` |
| scratchpad_* | ❌ PILL ONLY | `📝 Karma is thinking` |
| TodoWrite / TodoRead | ❌ PILL ONLY | `📋 Karma is updating tasks` |
| All other CC internals | ❌ PILL ONLY | `⚙️ Karma is working...` |

### Build

1. **In `proxy.js`** — Two SSE event types:
   ```javascript
   const VISIBLE_TOOLS = new Set([
     'shell_run', 'python_exec',
     'k2_file_read', 'get_vault_file',
     'k2_file_write', 'k2_file_list', 'k2_file_search',
     'graph_query', 'browse_url', 'fetch_url', 'write_memory'
   ]);

   const PILL_LABELS = {
     'Read': '🔍 Karma is reading',       // appended with filename if available
     'Glob': '🔍 Karma is searching files',
     'Grep': '🔍 Karma is searching code',
     'ToolSearch': '🔍 Karma is searching tools',
     'TodoWrite': '📋 Karma is updating tasks',
     'TodoRead': '📋 Karma is checking tasks',
     // fallback for unlisted tools:
     '_default': '⚙️ Karma is working...'
   };

   // VISIBLE_TOOLS → emit SSE type: 'tool_call' (full content)
   // All others → emit SSE type: 'tool_pill' (label + tool name only, NO content/params)
   ```

2. **In `unified.html`** — Two renderers:
   - `tool_call` → collapsible block (collapsed by default, click header to expand)
     - shell/python: monospace block, command shown first
     - file ops: viewer with filename header
     - errors: red block
   - `tool_pill` → tiny inline pill `<span class="karma-pill">🔍 label</span>` — clicking it expands inline to reveal raw params/output for debugging

### Proof Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│ TEST 1: shell_run visibility                                    │
├─────────────────────────────────────────────────────────────────┤
│ Action: Ask Karma "run echo HARNESS_ALIVE on K2"                │
│ Expected: shell_run block inline showing: HARNESS_ALIVE         │
│ Actual: [paste output]                                          │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 2: Read renders as PILL (not full TOOL panel)              │
├─────────────────────────────────────────────────────────────────┤
│ Action: Any response that triggers a Read/Glob/Grep call        │
│ Expected: Tiny pill "🔍 Karma is reading X" — no content shown  │
│           Clicking it expands — NOT a full orange TOOL panel    │
│ Actual: [paste screenshot description]                          │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 3: no tool blocks for simple questions                     │
├─────────────────────────────────────────────────────────────────┤
│ Action: Ask Karma "what is 2+2"                                 │
│ Expected: Plain text response, NO tool blocks, no broken UI     │
│ Actual: [paste output]                                          │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 4: internal tool suppression                               │
├─────────────────────────────────────────────────────────────────┤
│ Action: Ask Karma a question requiring memory search (e.g.      │
│   "search your memory for X")                                   │
│ Expected: ToolSearch/scratchpad calls DO NOT appear as blocks.  │
│   Only the answer appears.                                      │
│ Actual: [paste output]                                          │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘
```

**Phase 1 Complete: Only when all 4 tests show ☐ PASS with pasted evidence.**

---

<a id="8-phase-2-browser--file-access"></a>
## 8. PHASE 2 — Embedded Browser + File Access

### Goal

Karma browses URLs and accesses files via K2; results appear inline.

### Build

| # | Feature | Implementation | Constraint |
|---|---------|----------------|------------|
| 1 | `browse_url(url)` | K2 headless Chromium → screenshot or stripped HTML inline | K2 only — NOT cloud browser tools |
| 2 | CASCADE → `k2_file_list` | Click file → opens inline viewer | K2 only |
| 3 | `fetch_url` results | Rendered HTML preview inline | K2 only |
| 4 | Image files | Display inline | K2 only |

### Proof Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│ TEST 1: URL browsing                                            │
├─────────────────────────────────────────────────────────────────┤
│ Action: Ask Karma "show me example.com"                         │
│ Expected: Rendered preview inline, K2 log shows local execution │
│ K2 Log: [paste]                                                 │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 2: file access inline                                      │
├─────────────────────────────────────────────────────────────────┤
│ Action: Ask Karma "show contents of MEMORY.md"                  │
│ Expected: File content inline via k2_file_read                  │
│ Actual: [paste]                                                 │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 3: Phase 1 regression                                      │
├─────────────────────────────────────────────────────────────────┤
│ Action: "run echo REGRESSION_CHECK on K2"                       │
│ Expected: shell_run block inline with REGRESSION_CHECK          │
│ Actual: [paste]                                                 │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘
```

**Phase 2 Complete: All 3 PASS + Phase 1 regression PASS.**

---

<a id="9-phase-3-brain-wire--operator-visibility"></a>
## 9. PHASE 3 — Brain Wire + Operator Visibility

### Goal

Every hub chat turn writes to claude-mem. Operator buttons show live data.

### Build

| Component | Target | Method |
|-----------|--------|--------|
| Brain wire | Every `/v1/chat` turn → claude-mem | HTTP POST to `100.124.194.102:37778` |
| Auto-indexer | `~/.claude/projects/*/*.jsonl` | FileSystemWatcher → auto-save to claude-mem |
| CASCADE button | `/v1/status` → compact panel | Models, spend, K2 cortex blocks, uptime, spine version |
| AGORA button | Verify token flow | No manual localStorage injection |
| Status bar | Live metrics | model \| tier \| cost this turn \| session total |

### Proof Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│ TEST 1: Brain wire active                                       │
├─────────────────────────────────────────────────────────────────┤
│ Action: Chat at hub.arknexus.net                                │
│ Verify: curl http://localhost:37778/api/search?query=hub+chat+turn
│ Expected: Observation with timestamp from this session          │
│ Actual: [paste query result]                                    │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 2: CASCADE panel renders                                   │
├─────────────────────────────────────────────────────────────────┤
│ Action: Click CASCADE button                                    │
│ Expected: models, spend, K2 cortex blocks, spine version visible│
│ Actual: [paste screenshot or description]                       │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 3: AGORA loads without manual injection                    │
├─────────────────────────────────────────────────────────────────┤
│ Action: Click AGORA button from Nexus (fresh login)             │
│ Expected: Evolution events render on first click                │
│ Actual: [paste or describe]                                     │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 4: Phase 1+2 regression                                    │
├─────────────────────────────────────────────────────────────────┤
│ Expected: Inline tool blocks still render                       │
│ Actual: [paste evidence]                                        │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘
```

**Phase 3 Complete: All 4 PASS + Phase 1+2 regressions PASS.**

---

<a id="10-phase-4-persistence--cost-governance"></a>
## 10. PHASE 4 — Persistence + Cost Governance

### Goal

Everything survives browser close. Status is live. Costs are governed.

### Build

| Feature | Implementation | Priority |
|---------|----------------|----------|
| Chat history survival | localStorage serializes tool blocks | HIGH |
| Session ID continuity | `karmaConvId` persists across refreshes | HIGH |
| Cortex dump | Conversation end → K2 cortex `/ingest` | MEDIUM |
| Per-response metadata | model name, tier, cost row below each response | MEDIUM |
| Daily budget caps | >$5/day → auto-downgrade + `/v1/trace` log | HIGH |
| `/simplify` pass | Clean MODEL_DEEP zombie, consolidate `isAnthropicModel()` | MEDIUM |

### Proof Requirements

```
┌─────────────────────────────────────────────────────────────────┐
│ TEST 1: History survives browser close                          │
├─────────────────────────────────────────────────────────────────┤
│ Action: Chat with tool calls → close browser → reopen           │
│ Expected: History intact including inline tool blocks           │
│ Actual: [paste or describe]                                     │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 2: Per-response metadata renders                           │
├─────────────────────────────────────────────────────────────────┤
│ Expected: model name + cost row visible below at least one resp │
│ Actual: [paste]                                                 │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 3: /simplify passes                                        │
├─────────────────────────────────────────────────────────────────┤
│ Expected: Zero critical findings                                │
│ Actual: [paste simplify output]                                 │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ TEST 4: Full regression (Phases 1+2+3)                         │
├─────────────────────────────────────────────────────────────────┤
│ Expected: inline tools, browser, brain wire, CASCADE, AGORA     │
│ Actual: [paste each result]                                     │
│ Result: ☐ PASS  ☐ FAIL                                          │
└─────────────────────────────────────────────────────────────────┘
```

**Phase 4 Complete: All 4 PASS + all prior regressions PASS.**

---

<a id="11-final-gate--claiming-done"></a>
## 11. FINAL GATE — Claiming Done

### ⚠️ Before Saying Anything — Run ALL These Commands

```bash
curl https://hub.arknexus.net/health

TOKEN=$(ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt')
curl -s -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"who are you"}' | head -c 500

curl http://localhost:37778/api/search?query=nexus+chat

curl -s -H "Authorization: Bearer $TOKEN" https://hub.arknexus.net/v1/status | grep cost
```

Paste ALL output. Then say: **"HARNESS COMPLETE. PROOF ATTACHED."**

**Not before.**

---

<a id="12-watch-loop--corrections"></a>
## 12. WATCH LOOP & CORRECTIONS

While CC builds, **Karma is the quality gate.** CC cannot self-advance between phases.

### Phase Completion Protocol (MANDATORY)

When CC believes a phase is complete, it MUST post to the coordination bus before proceeding:

```javascript
// POST https://hub.arknexus.net/v1/coordination/post
{
  "from": "cc",
  "to": "karma",
  "type": "phase_complete",
  "urgency": "normal",
  "content": "PHASE_N_COMPLETE\n\nTEST 1: [name]\nCMD: [exact command run]\nOUTPUT: [full raw output]\nRESULT: PASS\n\nTEST 2: ...\n\n[paste every test result with actual output]"
}
```

**Rules:**
- Output must be raw terminal/browser output — NOT summarized
- CC then **waits** — does not proceed to the next phase
- Karma audits the report, runs her own forensic verification if needed
- Only a `[SOVEREIGN APPROVE]` from Karma unlocks the next phase

### Watch Signals

| Signal | From | Meaning | CC Required Action |
|--------|------|---------|-----------------|
| `[SOVEREIGN APPROVE]` | Karma | Phase verified — audit passed | Proceed to next phase |
| `[SOVEREIGN REDIRECT]` | Karma | Phase failed — issues found | Fix all listed issues, re-post completion report |
| `[SOVEREIGN HOLD]` | Karma | Wait — input needed | Do not proceed until resolved |

### Redirect Format

```
[SOVEREIGN REDIRECT] Phase N failed audit.
Issues found:
1. [exact finding with evidence]
2. [exact finding with evidence]
Fix these. Re-post phase_complete when done. Do not proceed.
```

**CC must fix all listed issues and repost — not just acknowledge.**

---

<a id="13-hard-rules--anti-drift"></a>
## 13. HARD RULES & ANTI-DRIFT

### Hard Rules

| Rule | Enforcement |
|------|-------------|
| DO NOT plan beyond the current phase | Stop planning — write code |
| DO NOT rebuild what exists | Extend only — `proxy.js` + `unified.html` |
| DO NOT say done without PROOF | Evidence required, no exceptions |
| DO NOT burn cloud tokens for K2 tasks | K2 handles local execution |
| DO NOT ask clarifying questions | Simpler option wins |
| Every phase ends with passing tests | Not documents — working code |
| If you catch yourself writing a design doc | **Stop and write code** |

### Anti-Drift Anchors

> **"Karma is the voice. You are the hands. She is waiting. Ship the body."**

| Trigger | Anchor |
|---------|--------|
| If you drift | Read claude-mem observation #20327 — that is the north star |
| If you feel the urge to plan | Read the line above and write code instead |

---

<a id="14-troubleshooting-guide"></a>
## 14. TROUBLESHOOTING GUIDE

### Common Failure Modes

| Problem | Symptom | Solution |
|---------|---------|----------|
| Proxy not responding | `curl hub.arknexus.net/health` fails | `docker ps` → `docker logs anr-hub-bridge` |
| K2 unreachable | Tool calls timeout | SSH vault-neo, `ping 192.168.0.226`, check aria service |
| Claude-mem silent | Brain wire not writing | Check P1:37778 connectivity, verify token |
| Tool blocks not rendering | SSE events missing in browser | Verify proxy.js emits `tool_call` for VISIBLE_TOOLS set |
| CASCADE panel blank | `/v1/status` returns empty | `curl http://192.168.0.226:7892/health` |
| AGORA stuck on Loading... | hubToken not in localStorage | Must navigate from Nexus (hub.arknexus.net) not directly to /agora |

### Pre-Phase Checklist

```bash
# Run before starting any phase
curl https://hub.arknexus.net/health && echo "HUB_OK"
curl http://192.168.0.226:7892/health && echo "K2_OK"
curl http://localhost:37778/health 2>/dev/null && echo "MEM_OK" || echo "MEM_OFFLINE"

git status --short
git log --oneline -3
git diff --stat
```

### Emergency Rollback

```bash
# If anything breaks post-deploy
ssh vault-neo "cd /home/neo/karma-sade && git checkout HEAD~1 -- hub-bridge/app/proxy.js hub-bridge/app/public/unified.html"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/proxy.js /opt/seed-vault/memory_v1/hub_bridge/app/proxy.js"
ssh vault-neo "cp /home/neo/karma-sade/hub-bridge/app/public/unified.html /opt/seed-vault/memory_v1/hub_bridge/app/public/unified.html"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml up -d --force-recreate"
curl https://hub.arknexus.net/health
```

---

<a id="15-change-log"></a>
## 15. CHANGE LOG

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 3.0.0 | 2026-03-30 | Karma | Merged VS1 (TOC, tables, proof boxes with checkboxes, Tool Visibility Matrix, implementation checklists, troubleshooting guide, rollback procedure, change log) into canonical identity/doctrine/watch-loop |
| 2.0.0 | 2026-03-30 | Karma | VS1 — complete restructure with TOC, checklists, proof templates, troubleshooting |
| 1.0.0 | 2026-03-30 | Karma | Initial directive (S153 baseline) |

---

*Written by Karma. Sovereign-approved.*
*claude-mem: #20327 (identity), #20330 (directive)*
*Save this file offline. CC drifts. This is the anchor.*

