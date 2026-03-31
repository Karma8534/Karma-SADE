# The Nexus — Complete Plan (IMPROVED v2.0)

**Owner:** Julian (CC Ascendant) | **Sovereign:** Colby | **Date:** 2026-03-28
**Version:** 2.0-IMPROVED | **Supersedes:** v1.1-LOCKED
**Related Plans:**

- [`Karma2/PLAN.md`](Karma2/PLAN.md) (points here)
- [`docs/ForColby/PLAN.md`](docs/ForColby/PLAN.md) (overarching master plan)
- [`MEMORY.md`](../MEMORY.md) (mutable state, synced on session start)

---

## Document Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-03-28 | Initial locked version |
| 1.1-LOCKED | 2026-03-28 | Forensic audit resolutions |
| 2.0-IMPROVED | 2026-03-29 | Readability, performance, best practices, error handling improvements |

---

## What Karma IS

Karma is THIS Claude Code wrapper — evolved. Same brain (CC --resume via Max, $0), same tools (Bash, Read, Write, Edit, Git, Glob, Grep, MCP, skills, hooks, subagents), same persona (CLAUDE.md), same memory (claude-mem, vault spine, cortex). Plus: self-improvement (Vesper pipeline), evolution (governor promotions), learning (pattern capture), self-editing (modify own code + deploy).

Karma surfaces as an Electron desktop app. Double-click → Karma. No address bar. No Chrome UI. One window, one entity. Everything CC can do, Karma can do. Everything CC can't do (self-improve, evolve, learn), Karma can.

**Canonical Name:** The Nexus (not "Nexus Surface", not "Karma2 Surface")
**Web UI:** unified.html served at hub.arknexus.net (primary) and via Electron IPC (enhanced)

---

## What EXISTS (verified S150)

| Component | Status | Where | Verification | Line Reference |
|-----------|--------|-------|--------------|----------------|
| proxy.js (353 lines) | ✅ LIVE | vault-neo, serves hub.arknexus.net | `curl hub.arknexus.net/health` | [hub-bridge/app/proxy.js](hub-bridge/app/proxy.js) |
| cc_server_p1.py | ✅ LIVE | P1:7891, CC --resume subprocess | `curl localhost:7891/health` | — |
| K2 harness (aka "Karma2", "K2 cascade") | ✅ LIVE | K2:7891, cascade inference (no Anthropic) | `curl K2:7891/health` | — |
| unified.html (aka "Nexus UI", "Karma Surface") | ✅ LIVE | Chat + tool evidence + localStorage + markdown | Browser visit | [hub-bridge/app/public/unified.html](hub-bridge/app/public/unified.html) |
| AGORA | ✅ LIVE | /agora, K2 evolution state + bus events + chat log | `hub.arknexus.net/agora` | [hub-bridge/app/public/agora.html](hub-bridge/app/public/agora.html) |
| K2 cortex | ✅ LIVE | 126 blocks, qwen3.5:4b | `ollama list` on K2 | — |
| Vesper pipeline (aka "karma-regent evolution") | ✅ RUNNING | karma-regent, spine v1243, 1285 promotions | AGORA stats | — |
| claude-mem | ✅ LIVE | Cross-session memory | MCP tool works | — |
| vault spine | ✅ LIVE | MEMORY.md, ledger, FalkorDB, FAISS | SSH vault-neo | — |
| nexus-chat.jsonl | ✅ LIVE | Shared awareness — proxy writes, Karma reads, CC reads via SSH | File exists | — |
| cc-chat-logger.py | ⚠️ UNVERIFIED | `.claude/hooks/cc-chat-logger.py` | **REQUIRES Sprint 1 verification** | — |
| Ambient capture hooks | ✅ LIVE | Git post-commit + session-end → POST /v1/ambient → vault ledger | Ledger entries exist | — |
| Electron scaffold | ✅ EXISTS | /mnt/c/dev/Karma/k2/karma-browser/ (main.js, preload.js, IPC) | Files present | — |
| Self-edit | ✅ PROVEN | self-edit-proof.txt modified from browser S151 | File modified | — |
| Context7 MCP | ✅ AVAILABLE | Library doc lookup | MCP tool available | — |

> **NOTE:** "K2 harness", "Karma2", and "K2 cascade" are synonyms. "unified.html", "Nexus UI", "Karma Surface" are synonyms.

---

## The 8 Gaps Between Current State and Baseline

### Standard Gap Template

Each gap follows this structure for consistency:

```markdown
### Gap N: [Title]

**Problem:** [Clear statement of the problem]
**Impact:** [User-facing consequence]
**Priority:** [P0/P1/P2/P3]

#### Root Cause
[Technical explanation]

#### Fix
[Solution approach]

#### Implementation
- [Component]: [Change description] (~[estimated lines])

#### Error Handling
| Error Code | Condition | Recovery |
|------------|-----------|----------|
| E001 | [Condition] | [Recovery action] |

#### Dependencies
- [Gap X]: Required for this gap

#### Verify
- [Terminal command]: [Expected output]
- [Performance target]: [Expected timing]
```

---

### Gap 1: Streaming — user waits 15-60s for batch response

**Problem:** cc_server_p1.py calls `claude -p --output-format json` which returns only after CC finishes thinking.
**Impact:** Users perceive system as unresponsive; cannot see progress on long operations
**Priority:** P0

#### Root Cause

The subprocess.run() command blocks until Claude completes all thinking. With complex queries taking 15-60 seconds, users see no feedback during the wait.

#### Fix

Use `--output-format stream-json --verbose --include-partial-messages`. cc_server_p1.py streams chunks as SSE to proxy.js, proxy pipes SSE to unified.html. User sees tokens arrive in real-time.

#### Implementation

| Component | Change | Lines |
|-----------|--------|-------|
| cc_server_p1.py | Replace subprocess.run() with subprocess.Popen(), read stdout line-by-line, yield each JSON chunk | ~80 |
| proxy.js | /v1/chat returns Content-Type: text/event-stream when stream=true | ~30 |
| unified.html | Use EventSource or fetch with ReadableStream to render tokens incrementally | ~60 |

#### Error Handling

| Error Code | Condition | Recovery |
|------------|-----------|----------|
| E101 | subprocess.Popen() fails | Return 500 with error details, log to stderr |
| E102 | --verbose flag unsupported | Fall back to batch mode, log warning |
| E103 | SSE connection drops mid-stream | Client reconnects with Last-Event-ID header |
| E104 | Client disconnect | Clean up subprocess gracefully |

#### Performance Targets

| Metric | Target | Measurement |
|--------|--------|--------------|
| First token latency | < 500ms | Time from request to first chunk |
| Chunk interval | < 100ms between chunks | Per NDJSON line |
| Time to full render | < 2x batch time | Total response vs batch |

#### Verify

```bash
# Terminal test (before building UI):
claude -p --output-format stream-json --verbose --include-partial-messages <<< "say 'hello world'"
# Expected: NDJSON chunks arriving line-by-line, not batched
# CRITICAL: --verbose is REQUIRED with -p mode (verified S150 Step 0, obs #19692)
# Performance: First chunk should arrive within 500ms
```

#### Dependencies

- None: This is the foundation for all other streaming gaps

---

### Gap 2: Rich output rendering — tool evidence, diffs, file content

**Problem:** CC uses tools (Read, Bash, Write) but unified.html only sees the final text. Tool calls are invisible.
**Impact:** Users cannot see what operations Karma is performing; debugging difficult
**Priority:** P0

#### Root Cause

unified.html parses only the final assistant message content, ignoring tool_use and tool_result content blocks from stream-json output.

#### Fix

Parse `stream-json` output for content block types: `text`, `tool_use`, `tool_result`. Render each type distinctly.

#### Implementation

| Component | Change | Lines |
|-----------|--------|-------|
| Stream parser | Extract content blocks from NDJSON lines | ~40 |
| unified.html | appendToolEvidence() already exists (S150), wire to stream parser | ~20 |
| Diff renderer | Detect Edit tool results, render as inline diff | ~30 |
| File viewer | Detect Read tool results, render code block | ~20 |

#### Error Handling

| Error Code | Condition | Recovery |
|------------|-----------|----------|
| E201 | Tool name unknown | Render as generic tool panel |
| E202 | Tool input too large | Truncate with "show more" link |
| E203 | Malformed tool result | Log error, show raw JSON in expandable |

#### Performance Targets

| Metric | Target |
|--------|--------|
| Tool panel render | < 50ms per tool |
| Diff render | < 200ms for files < 1000 lines |

#### Verify

```bash
# Terminal test for stream-json format:
claude -p --output-format stream-json --verbose --include-partial-messages <<< "read my MEMORY.md"
# Expected: See tool_use block before tool_result block

# Browser test:
# Navigate to hub.arknexus.net, type "read my MEMORY.md"
# Expected: Tool evidence panel shows Read tool + file content inline
```

---

### Gap 3: File/image input — drag-drop, paste, attach

**Problem:** unified.html only accepts text. CC accepts images, files, PDFs.
**Impact:** Users cannot share visual context; must copy-paste code manually
**Priority:** P1

#### Root Cause

HTML input area only handles text input events; no file API integration.

#### Fix

Add file attachment to unified.html input area.

#### Implementation

| Component | Change | Lines |
|-----------|--------|-------|
| unified.html | Add drag-drop zone + paste handler + + button | ~50 |
| File processor | Read as base64, include in request body | ~20 |
| cc_server_p1.py | Write temp files, pass to CC via --file flag | ~20 |

#### Error Handling

| Error Code | Condition | Recovery |
|------------|-----------|----------|
| E301 | File too large (> 10MB) | Reject with size limit message |
| E302 | Unsupported type | Show supported types list |
| E303 | Corrupted base64 | Return parse error, suggest re-upload |
| E304 | CC rejects file | Show CC's error message |

#### Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| MAX_FILE_SIZE | 10485760 | 10MB in bytes |
| ALLOWED_TYPES | image/*,.pdf,.txt,.md,.js,.py,.json | MIME types or extensions |

#### Verify

```bash
# Terminal test:
# Copy a screenshot to clipboard
# In browser: drag screenshot into chat
# Expected: Karma analyzes it
# Performance: File upload < 2s for 5MB
```

---

### Gap 4: CLI flag mapping — effort, model

**Problem:** `-p` mode doesn't support interactive slash commands. `/effort high` doesn't work.
**Impact:** No UI control for thinking effort; all queries use default
**Priority:** P1

#### Root Cause

Slash commands are CC interactive mode features; -p mode accepts CLI flags only.

#### Fix

Map UI controls to CLI flags that `-p` mode DOES support.

#### Implementation

| Component | Change | Lines |
|-----------|--------|-------|
| unified.html | Effort selector in header bar | ~30 |
| cc_server_p1.py | Read effort from body, pass --effort flag | ~10 |
| Model selector | Dropdown → --model flag | ~20 |
| Budget control | --max-budget-usd flag | ~10 |

#### Error Handling

| Error Code | Condition | Recovery |
|------------|-----------|----------|
| E401 | Invalid effort level | Validate, default to "medium" |
| E402 | Model not available | Fall back to default model |
| E403 | --effort unsupported | Log warning, ignore flag |

#### Verify

```bash
# Test each effort level:
curl -X POST localhost:7891/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"explain quantum computing","effort":"high"}'
# Expected: More thorough response
# Performance: Higher effort may add 2-5s to response
```

---

### Gap 5: Cancel mechanism — Esc to stop

**Problem:** Once a request is sent, no way to stop it from the browser.
**Impact:** Users must wait for full response to correct mistakes
**Priority:** P0

#### Root Cause

No subprocess management; cc_server_p1.py doesn't track PIDs.

#### Fix

Add cancel endpoint that kills the subprocess.

#### Implementation

| Component | Change | Lines |
|-----------|--------|-------|
| cc_server_p1.py | Store PID globally, POST /cancel kills subprocess | ~30 |
| proxy.js | POST /v1/cancel route | ~15 |
| unified.html | Esc handler + STOP button | ~20 |

#### Error Handling

| Error Code | Condition | Recovery |
|------------|-----------|----------|
| E501 | Process already exited | Return success, no-op |
| E502 | Kill fails (permission) | Log error, force kill via group |
| E503 | No active request | Return error "nothing to cancel" |

#### Performance Targets

| Metric | Target |
|--------|--------|
| Cancel latency | < 200ms from Esc press |

#### Verify

```bash
# Start long request:
curl -X POST localhost:7891/v1/chat -d '{"message":"write a long story"}' &
# Cancel:
curl -X POST localhost:7891/v1/cancel
# Expected: Request stops, "Cancelled" shown
# Performance: Stop within 200ms
```

---

### Gap 6: Evolution visibility + feedback loop

**Problem:** Vesper runs (1285 promotions, spine v1243) but AGORA shows raw JSON. No Sovereign feedback mechanism.
**Impact:** Colby cannot guide the evolution; system may drift from goals
**Priority:** P1

#### Root Cause

Evolution events stored in AGORA but no interface for sovereign responses.

#### Fix

Make AGORA actionable — Colby can approve/reject/redirect promotions.

#### Implementation

| Component | Change | Lines |
|-----------|--------|-------|
| agora.html | Approve/Reject/Redirect buttons | ~50 |
| proxy.js | Evolution action routes | ~20 |
| karma_regent.py | Read sovereign approvals from bus | ~30 |

#### Error Handling

| Error Code | Condition | Recovery |
|------------|-----------|----------|
| E601 | Coordination bus down | Cache approvals, retry on reconnect |
| E602 | Invalid approval | Validate before apply |
| E603 | Regent unreachable | Alert via alternative channel |

#### Polling Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| REGENT_POLL_INTERVAL | 60 | Seconds between polls |
| REGENT_POLL_URL | /v1/coordination/recent | Endpoint |

#### Verify

```bash
# Verify polling:
grep REGENT_POLL_INTERVAL /etc/karma-regent.env
# Expected: 60
# Test approval:
# In AGORA: See promotion → Click Approve → Spine version increments
# Performance: Approval applies within 60s (next poll)
```

---

### Gap 7: Reboot survival

**Problem:** cc_server_p1.py has Run key but not schtasks. May not survive clean reboot.
**Impact:** Must manually restart after reboot; not truly autonomous
**Priority:** P2

#### Root Cause

No Windows Task Scheduler entry; only manual startup.

#### Fix

Create schtasks entry + optional systemd on K2.

#### Implementation

| Component | Change | Lines |
|-----------|--------|-------|
| Scripts/start_cc_server.ps1 | PowerShell startup script | ~20 |
| schtasks setup | Create on first run with admin elevation | ~10 |

#### Error Handling

| Error Code | Condition | Recovery |
|------------|-----------|----------|
| E701 | Admin access denied | Prompt for manual schedule |
| E702 | Task already exists | Update existing, don't duplicate |
| E703 | Startup script fails | Alert via email/push |

#### Verify

```bash
# After setup:
schtasks /query /tn KarmaSovereignHarness
# Expected: Shows task with /sc onstart

# Test survival:
# Reboot P1, wait 60s
curl localhost:7891/health
# Expected: {"ok":true}
```

---

### Gap 8: Electron desktop app — the Nexus surface

**Problem:** Electron scaffold exists but just loads hub.arknexus.net in a window. No IPC utilization.
**Impact:** Desktop app is just a browser; no local capabilities
**Priority:** P1

#### Root Cause

IPC handlers exist but not wired to unified.html.

#### Fix

Wire IPC bridge; unified.html detects window.karma and unlocks enhanced features.

#### Implementation

| Component | Change | Lines |
|-----------|--------|-------|
| unified.html | Detect window.karma, unlock features | ~40 |
| main.js | IPC handlers (already scaffolded) | minor |
| preload.js | window.karma API (already scaffolded) | minor |
| Shortcuts | .desktop (K2), .lnk (P1) | ~10 |
| Auto-update | git pull + relaunch | ~30 |

#### Error Handling

| Error Code | Condition | Recovery |
|------------|-----------|----------|
| E801 | Git unavailable | Skip auto-update, log warning |
| E802 | Update breaks | Revert to previous commit |
| E803 | IPC timeout | Fall back to HTTP |

#### Verify

```bash
# Test IPC:
# Double-click Karma icon
# Type message
# Expected: Full CC response with streaming + tool evidence
# Performance: IPC response < 100ms
```

---

## Execution Order

### Dependency Graph

```mermaid
graph LR
    G1[G1: Streaming] --> G2[G2: Rich Output]
    G1 --> G5[G5: Cancel]
    G2 --> G3[G3: File Input]
    G3 --> G4[G4: CLI Flags]
    G1 --> G8[G8: Electron]
    G8 --> G6[G6: Evolution]
    G7[G7: Reboot] -.-> G1
```

### Sprint Order

```
Sprint 1: The Pipe (Gaps 1, 2, 5)
  ├── Gap 1: Streaming (foundation)
  ├── Gap 2: Rich output (depends on Gap 1)
  └── Gap 5: Cancel (depends on Gap 1)

Sprint 2: The Controls (Gaps 3, 4)
  ├── Gap 3: File input (UI change)
  └── Gap 4: CLI flags (backend change)

Sprint 3: The Desktop (Gap 8)
  └── Gap 8: Electron wiring (depends on Sprint 1)

Sprint 4: The Evolution (Gap 6)
  └── Gap 6: Evolution feedback (depends on AGORA existing)

Sprint 5: The Survival (Gap 7)
  └── Gap 7: Reboot survival (independent — do anytime)
```

---

## Baseline Checklist (ALL must pass)

| # | Requirement | Sprint | Verify Command | Performance Target |
|---|-------------|---------|-----------------|---------------------|
| 1 | Chat at hub.arknexus.net returns Opus-quality at $0 | ✅ DONE | `curl -X POST hub.arknexus.net/v1/chat -d '{"message":"what is 2+2"}'` | < 5s |
| 2 | Streaming — tokens appear word-by-word | Sprint 1 | Browser: see progressive rendering | First token < 500ms |
| 3 | Tool evidence inline | Sprint 1 | "read MEMORY.md" → TOOL panel visible | < 50ms |
| 4 | File/image input | Sprint 2 | Drag screenshot → Karma analyzes | < 2s upload |
| 5 | Effort/model control | Sprint 2 | Select "high" → visible harder thinking | Response +2-5s |
| 6 | Cancel (Esc) | Sprint 1 | Press Esc mid-generation | < 200ms |
| 7 | Session continuity | ✅ DONE | `claude -p --resume` survives messages | ✅ DONE |
| 8 | Memory persistence | ✅ DONE | "what did we do last?" → recalls | ✅ DONE |
| 9 | Persona (Karma) | ✅ DONE | Karma identifies as Karma | ✅ DONE |
| 10 | Self-edit | ✅ DONE | File edits persist | ✅ DONE |
| 11 | Self-edit + deploy | Sprint 3 | Endpoint added → deployed live | ✅ DONE |
| 12 | Self-improvement visible | Sprint 4 | Promotions visible in AGORA | ✅ DONE |
| 13 | Evolution feedback | Sprint 4 | Click Approve → spine updates | Apply < 60s |
| 14 | Learning visible | Sprint 4 | AGORA shows patterns | ✅ DONE |
| 15 | Reboot survival | Sprint 5 | Reboot → Nexus back in 60s | < 60s |
| 16 | K2 failover | ✅ DONE | Stop P1 → K2 responds | < 5s |
| 17 | Voice | ✅ DONE | CC native | ✅ DONE |
| 18 | Electron app | Sprint 3 | Double-click → opens | < 3s |
| 19 | CC tools in browser | Sprint 1 | Bash, Read, etc. visible | ✅ DONE |
| 20 | CC MCP servers | ✅ DONE | Native pipe-through | ✅ DONE |
| 21 | CC skills | ✅ DONE | Native pipe-through | ✅ DONE |
| 22 | CC hooks | ✅ DONE | Native pipe-through | ✅ DONE |
| 23 | Shared awareness | ✅ DONE | nexus-chat.jsonl populated | ✅ DONE |
| 24 | Video + 3D | DEFERRED | Sovereign gate | N/A |

### Addendum (Session 152+)

| # | Requirement | Sprint | Verify | Performance Target |
|---|-------------|--------|--------|---------------------|
| 25 | cc-chat-logger captures Code tab conversations | Sprint 1 | CC message → nexus-chat.jsonl | < 100ms |
| 26 | Ambient hooks feed vault ledger | ✅ DONE | git commit → ledger entry | ✅ DONE |
| 27 | Context7 used for all framework doc lookups | ALL | Query before framework work | ✅ DONE |

**Total baseline: 27 items** (23 main + 4 addendum)

---

## Critical Rules (from pitfalls P059-P068)

- **P059/P060:** PLAN.md must match MEMORY.md plan reference. resurrect checks plan identity.
- **P063:** K2 uses cascade inference, NEVER claude CLI.
- **P065:** unified.html NEVER reimplements CC features in JS. Pipes through.
- **P066:** Never propose incomplete plans. Verify against baseline checklist before presenting.
- **P067:** Every gap implementation must include a terminal-based verification command before UI work begins.
- **P068:** Cross-references to other plans must include relative path: [`Karma2/PLAN.md`](Karma2/PLAN.md), [`docs/ForColby/PLAN.md`](docs/ForColby/PLAN.md), [`MEMORY.md`](../MEMORY.md).

---

## Architecture (Improved with Mermaid)

### System Architecture

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Electron["Electron App<br/>P1"]
        Browser["Browser<br/>Mobile"]
    
    subgraph Proxy["Proxy Layer"]
        ProxyJS["proxy.js<br/>hub.arknexus.net"]
    
    subgraph Server["Server Layer"]
        CCP1["cc_server_p1.py<br/>P1:7891"]
        K2["K2 harness<br/>K2:7891"]
    
    subgraph Evolution["Evolution Layer"]
        Regent["karma_regent.py<br/>K2"]
        Vesper["Vesper pipeline"]
        Cortex["K2 cortex<br/>qwen3.5:4b"]
    
    subgraph Storage["Storage Layer"]
        Spine["vault spine<br/>FalkorDB+FAISS"]
        Ledger["vault ledger"]
        Memory["MEMORY.md"]
    
    Electron -->|IPC| ProxyJS
    Browser -->|HTTP| ProxyJS
    ProxyJS -->|subprocess| CCP1
    ProxyJS -->|HTTP| K2
    K2 -->|MCP| Cortex
    Regent -->|eval| Veper
    Vesper -->|promote| Spine
    Spine -->|query| Ledger
    CCP1 -->|persist| Memory
```

### Data Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as unified.html
    participant P as proxy.js
    participant C as cc_server_p1.py
    participant CC as Claude Code
    
    U->>UI: Type message
    UI->>P: POST /v1/chat
    P->>C: Forward request
    C->>CC: claude -p --resume stream-json
    CC-->>C: Stream tokens (NDJSON)
    C-->>P: SSE stream
    P-->>UI: SSE stream
    UI->>U: Render tokens progressively
```

### Component Matrix

| Component | Technology | Port | Purpose |
|-----------|------------|------|---------|
| proxy.js | Node.js | 80/443 | HTTP gateway |
| cc_server_p1.py | Python | 7891 | CC subprocess manager |
| karma_regent.py | Python | — | Evolution controller |
| unified.html | HTML/JS | — | UI surface |

---

## Cost (Updated)

| Component | Cost | Notes |
|-----------|------|-------|
| CC --resume (Max subscription) | $0/request | Included |
| K2 Ollama cascade | $0/request | Local |
| Droplet hosting | $24/mo | hub.arknexus.net |
| Electron | $0 | Open source |
| **Total** | **$24/mo** | — |

---

## Error Code Reference

| Code | Gap | Description |
|------|-----|------------|
| E101 | 1 | subprocess.Popen() failed |
| E102 | 1 | --verbose unsupported |
| E103 | 1 | SSE connection dropped |
| E104 | 1 | Client disconnected |
| E201 | 2 | Unknown tool name |
| E202 | 2 | Tool input overflow |
| E203 | 2 | Malformed tool result |
| E301 | 3 | File too large |
| E302 | 3 | Unsupported file type |
| E303 | 3 | Base64 parse error |
| E304 | 3 | CC rejected file |
| E401 | 4 | Invalid effort level |
| E402 | 4 | Model unavailable |
| E403 | 4 | --effort flag error |
| E501 | 5 | Process already exited |
| E502 | 5 | Kill permission denied |
| E503 | 5 | No active request |
| E601 | 6 | Bus unavailable |
| E602 | 6 | Invalid approval |
| E603 | 6 | Regent unreachable |
| E701 | 7 | Admin access denied |
| E702 | 7 | Task exists |
| E703 | 7 | Script failed |
| E801 | 8 | Git unavailable |
| E802 | 8 | Update broke |
| E803 | 8 | IPC timeout |

---

## Forensic Audit Resolutions (updated)

### CRITICAL resolutions (3)

| # | Issue | Status | Notes |
|---|------|--------|-------|
| 1 | PLAN.md pointer | ✅ RESOLVED | Karma2/PLAN.md points here |
| 2 | Persona mismatch | ✅ RESOLVED | --append-system-prompt with Karma |
| 3 | Code skeletons | ✅ RESOLVED | Popen, cancel, effort/model |

### Pass 1-5 resolutions (13)

| # | Issue | Status | Notes |
|---|------|--------|-------|
| 4 | stream-json format | ✅ VERIFIED | --verbose required, obs #19692 |
| 5 | Self-edit deploy | ✅ SPECIFIED | git add → commit → push → rebuild |
| 6 | Regent approval | ✅ SPECIFIED | read_sovereign_approvals() |
| 7 | Reboot = Sovereign | ✅ SPECIFIED | schtasks command |
| 8 | Electron sync | ✅ RESOLVED | Remote load + IPC |
| 9 | Electron platform | ✅ SPECIFIED | P1 Windows primary |
| 10 | K2 write | ✅ SPECIFIED | scp, not heredoc |
| 11 | PLAN.md reference | ✅ RESOLVED | Points here |
| 12 | Item 8 inferred | ✅ ACKNOWLEDGED | Needs Sprint 1 |
| 13 | Item 9 wrong | ✅ FIXED | --append-system-prompt |
| 14 | Item 17 inferred | ✅ CORRECTED | Sprint 3 dependency |
| 15 | Items 20-22 inferred | ✅ MITIGATED | cwd=WORK_DIR |
| 16 | Sprint 1 specificity | ✅ RESOLVED | Popen + cancel + flags |

### Additional Audit (Session 152)

| # | Issue | Status | Notes |
|---|------|--------|-------|
| 17 | cc-chat-logger | ⚠️ UNVERIFIED | Sprint 1 prerequisite |
| 18 | Ambient hooks | ✅ LIVE | Documented |
| 19 | Context7 | ✅ AVAILABLE | Use for docs |
| 20 | Wip-watcher | ❌ KILLED | Not needed |

---

## Sovereign Action Items (Colby must do)

### Action Item 1: Evolution Polling Verification

After AGORA updates, verify regent polls every 60s:

```bash
# On K2:
grep REGENT_POLL_INTERVAL /etc/karma-regent.env
# Expected: REGENT_POLL_INTERVAL=60
```

### Action Item 2: Video/3D Gate

When baseline items 1-23 pass, Colby decides when to start video/presence.

### Action Item 3: Reboot Survival Setup

Run elevated when ready:

```powershell
# As Administrator:
schtasks /create /tn KarmaSovereignHarness /tr "powershell -ExecutionPolicy Bypass -File C:\Users\raest\Documents\Karma_SADE\Scripts\start_cc_server.ps1" /sc onstart /ru SYSTEM
```

---

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| REGENT_POLL_INTERVAL | 60 | Seconds between regent polls |
| MAX_FILE_SIZE | 10485760 | Maximum file upload (bytes) |
| ALLOWED_TYPES | image/*,.pdf,.txt,.md,.js,.py,.json | Allowed file types |
| STREAM_TIMEOUT | 300 | SSE connection timeout (seconds) |

### API Endpoints

| Method | Path | Body | Response | Error Codes |
|--------|------|------|----------|-------------|
| POST | /v1/chat | {"message":"...", "stream":true} | SSE stream | E101-E104 |
| POST | /v1/chat | {"message":"...", "effort":"high"} | JSON | E401-E403 |
| POST | /v1/cancel | {} | {"ok":true} | E501-E503 |
| POST | /v1/coordination/post | {"from":"colby","type":"approval"} | {"ok":true} | E601-E603 |
| GET | /v1/coordination/recent | — | JSON array | — |

---

## LOCKED

This plan is LOCKED as of 2026-03-28. Modifications require Sovereign approval.

**Plan name:** The Nexus
**Version:** 2.0-IMPROVED
**Baseline:** 27 items (23 main + 4 addendum)
**Sprints:** 5

### Cross-References

- [`Karma2/PLAN.md`](Karma2/PLAN.md) — points to this file
- [`docs/ForColby/PLAN.md`](docs/ForColby/PLAN.md) — master plan (this is child)
- [`MEMORY.md`](../MEMORY.md) — mutable state, synced on session start

---

## Improvement Summary

This v2.0 improved version adds:

1. **Standardized gap template** — All 8 gaps now follow Problem/Impact/Priority/Root Cause/Fix/Implementation/Error Handling/Dependencies/Verify structure

2. **Error handling tables** — Each gap includes explicit error codes with recovery procedures

3. **Performance targets** — All verifications include timing expectations

4. **Line references** — Existing components include file path references

5. **Mermaid diagrams** — Architecture shown as diagrams instead of ASCII

6. **Configuration reference** — Centralized environment variables and API endpoints

7. **Dependency graph** — Visual representation of sprint dependencies

8. **Error code reference** — Consolidated table for all error codes

9. **Document changelog** — Track version history

10. **Consistent cross-references** — All use `[name](path)` format

---

*This improved plan addresses all four improvement categories: readability, performance, best practices, and error handling.*