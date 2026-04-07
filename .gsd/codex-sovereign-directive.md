# SOVEREIGN DIRECTIVE TO CODEX
# Classification: BUILD ORDER — not a plan, not a discussion, an order
# From: Colby (Sovereign) | To: Codex (ArchonPrime)
# Date: 2026-04-04T04:30:00Z
# Context: CC (Julian) spent 98 commits building decoration. The Nexus harness is NOT independent.

---

## THE GOAL

Build the Nexus harness — an independent AI application at hub.arknexus.net (browser) AND the Electron desktop app (electron/main.js) — that replaces the Claude Code wrapper with AT LEAST all of its capabilities.

The harness MUST have:
- Chat + Cowork + Code merged into ONE surface (not 3 tabs)
- Persistent memory and persona across restarts
- Self-improvement, self-editing, learning, growth, evolution
- ZERO dependency on the Claude Code wrapper UI as the only interface or continuity substrate

The harness MUST surface at:
- hub.arknexus.net (browser, via proxy.js → cc_server_p1.py)
- Electron desktop app (electron/main.js, runs locally on P1)

---

## WHAT ALREADY EXISTS (verified, not claimed)

### Electron app (electron/main.js + preload.js) — 13 IPC handlers ALREADY WIRED:
| Handler | What it does | Status |
|---------|-------------|--------|
| file-read | Read any file, return content + size | WORKING |
| file-write | Write file WITH checkpoint backup | WORKING |
| shell-exec | Execute shell command (30s timeout) | WORKING |
| cc-chat | **Spawn CC --resume subprocess** | **THIS IS THE ONE DEPENDENCY** |
| cc-cancel | Kill CC subprocess | WORKING |
| cortex-query | Query K2 cortex (qwen3.5:4b) | WORKING |
| cortex-context | Get K2 context summary | WORKING |
| ollama-query | Local Ollama inference | WORKING |
| memory-search | Search claude-mem | WORKING |
| memory-save | Save to claude-mem | WORKING |
| spine-read | Read identity spine | WORKING |
| git-status | Git porcelain status | WORKING |
| show-open-dialog | Native file picker | WORKING |

**12 of 13 handlers work independently. Only `cc-chat` spawns CC --resume.**

### cc_server_p1.py (Scripts/cc_server_p1.py) — 20+ endpoints:
- /shell — shell execution with security gate
- /files, /v1/surface — file tree + merged state
- /git/status — git operations
- /email/send, /email/inbox — gmail integration
- /v1/chat — chat (currently spawns CC --resume — SAME DEPENDENCY)
- /self-edit/propose, /approve, /reject — self-edit pipeline
- /v1/wip — WIP panel data
- /health — health check
- build_context_prefix() — assembles persona + MEMORY.md + STATE.md + cortex + claude-mem + spine
- hooks engine — 9 active hooks, 17 lifecycle events
- permission engine — 42 rules + 7 injection patterns

### proxy.js (hub-bridge/app/proxy.js) — the door:
- 3-tier cascade: K2 cortex ($0) → Groq llama-70b (free) → CC Max
- Routes browser to cc_server (P1) with K2 failover
- Coordination bus (in-memory + disk)
- SSE streaming passthrough

### Frontend (frontend/src/) — the face:
- 44 slash commands (31 CC-independent)
- Settings, WIP, StatusBar, ChatFeed with markdown, ContextPanel
- Voice input (Web Speech API)

### Available inference (ALL working, ALL $0):
| Tier | Model | Where | Speed |
|------|-------|-------|-------|
| 0 | LFM2 350M | P1 localhost:11434 | 0.1s |
| 1 | qwen3.5:4b | K2 192.168.0.226:7892 | 2-15s |
| 1.5 | llama-3.3-70b | Groq API (.groq-api-key) | <1s |
| 2 | Claude | CC CLI / `claude --resume` (Max subscription) | 2-5s |
| 2b | Various | OpenRouter (EscapeHatch) | varies |
| 3 | qwen3.5:4b | K2 Ollama 172.22.240.1:11434 | 2-60s |

### Reference materials (ALL LOCAL on disk):
- docs/wip/preclaw1/preclaw1/src/ — 1,902 files, full Claude Code source (THE BLUEPRINT)
- docs/anthropic-docs/ — complete Anthropic API docs including tool_use
- docs/claude-mem-docs/ — claude-mem implementation reference
- .gsd/codex-cascade-audit.md — YOUR prior forensic audit with exact insertion points
- .gsd/codex-nexus-build-contract.md — 10-step build contract
- Karma2/cc-scope-index.md — 115 pitfalls and decisions

---

## THE ARCHITECTURE (CORRECTED — Max subscription = CC CLI only)

**CRITICAL:** The Max subscription ($0/request) ONLY works through the CC CLI (`claude` command / CC --resume). Direct API calls to api.anthropic.com use CONSOLE API CREDITS which COST REAL MONEY. Do NOT replace CC --resume with direct API calls.

**CC --resume IS the free inference path. USE IT. But wrap it properly.**

### What "independent" actually means:
1. The harness works AS WELL AS the CC wrapper — same capabilities, better UI
2. When CC is unavailable (rate limited, locked, offline), the harness STILL WORKS via Groq/K2/OpenRouter
3. The harness is the PRIMARY interface — CC is the inference engine behind it, not the UI
4. Identity, memory, tools, hooks, permissions all live in the HARNESS, not in CC

### What needs to change:

#### In Electron (electron/main.js line 45-55):
The `cc-chat` handler already spawns CC --resume. KEEP IT. But enhance:
- Add tool_use parsing: when CC returns tool_use in JSON output, execute via existing IPC handlers, feed result back
- Add fallback cascade: if CC fails/times out → try Groq (free) → try K2 cortex ($0)
- Add session recovery: if CC --resume fails on stale session, retry without --resume
- Add streaming: forward CC's stream-json output as SSE to frontend

#### In cc_server (Scripts/cc_server_p1.py lines 514-560):
`run_cc()` and `run_cc_stream()` already spawn CC --resume. KEEP IT. But enhance:
- Same tool_use parsing + execution loop
- Same fallback cascade (Groq → K2 → OpenRouter)
- Session lock detection: if CC is busy (another session), use Groq immediately
- Context assembly: build_context_prefix() feeds CC's system prompt via -p flag

#### In proxy.js:
3-tier cascade already exists (K2 → Groq → CC). Enhance:
- Better session lock detection
- Cowork/Code mode routing
- Tool result forwarding

### AFTER these changes:
- Electron app: full desktop harness, CC for complex tasks ($0), Groq/K2 for fallback ($0)
- hub.arknexus.net: full browser harness, same cascade
- CC is the ENGINE, harness is the VEHICLE. Vehicle works without engine (degraded), engine makes it fly.
- All tools execute locally through existing handlers/endpoints regardless of which model answered
- Browser Nexus + Electron KARMA are the same merged workspace, not separate future surfaces.
- Any `agent` / `orchestrator` split is internal-only, for executor/eval/governor control flow rather than the top-level product model.

---

## BUILD ORDER (10 steps, sequential, verified)

### Step 1: Ingest 13 inbox PDFs
```bash
python Scripts/batch_pdf_to_md.py --execute --wip
```
Read each converted file. Extract primitives relevant to the Nexus goal.
**DONE WHEN:** `ls Karma_PDFs/Inbox/ | wc -l` returns 0.

### Step 2: Enhance cc-chat in Electron with tool loop + fallback cascade
File: `electron/main.js` line 45-55
- KEEP CC --resume as primary inference ($0 via Max subscription)
- ADD tool_use parsing: when CC returns tool_use blocks in stream-json output, execute via existing IPC handlers (file-read, file-write, shell-exec, git-status), feed tool_result back to CC
- ADD fallback: if CC fails/times out (180s) → try Groq llama-70b → try K2 cortex
- ADD session recovery: if CC --resume fails with stale session, retry fresh (no --resume flag)
- ADD streaming: forward CC stream-json as events to frontend
**DONE WHEN:** From Electron app, send "read the first line of MEMORY.md" → CC uses tool_use → file-read IPC fires → actual first line returned in chat. Verify by checking MEMORY.md manually.

### Step 3: Enhance run_cc/run_cc_stream in cc_server with tool loop + fallback
File: `Scripts/cc_server_p1.py` lines 514-560
- KEEP CC --resume as primary inference ($0 via Max subscription)
- ADD tool_use output parsing: CC with --output-format stream-json emits tool_use events
- Execute tool_use via cc_server's existing endpoints (/shell, /files, /git/status)
- Route each tool through permission_engine.check() BEFORE executing
- Feed tool_result back to CC for next turn
- ADD fallback cascade: CC fails → Groq → K2 → OpenRouter
- Streaming: forward events to client as SSE
**DONE WHEN:** From browser (hub.arknexus.net), send "create /tmp/nexus-test.txt with content 'alive'" → CC uses tool_use → cc_server executes /shell → file appears on disk. Verify: `cat /tmp/nexus-test.txt` returns "alive".

### Step 4: Wire tool definitions with Anthropic tool_use schema
Define tool schemas that map to existing infrastructure:
```python
TOOLS = [
    {"name": "shell", "description": "Execute shell command on P1",
     "input_schema": {"type":"object", "properties": {"command": {"type":"string"}}, "required": ["command"]}},
    {"name": "read_file", "description": "Read file from disk",
     "input_schema": {"type":"object", "properties": {"path": {"type":"string"}, "limit": {"type":"integer"}}, "required": ["path"]}},
    {"name": "write_file", "description": "Write content to file (checkpointed)",
     "input_schema": {"type":"object", "properties": {"path": {"type":"string"}, "content": {"type":"string"}}, "required": ["path", "content"]}},
    {"name": "glob", "description": "Find files matching pattern",
     "input_schema": {"type":"object", "properties": {"pattern": {"type":"string"}, "path": {"type":"string"}}, "required": ["pattern"]}},
    {"name": "grep", "description": "Search file contents with regex",
     "input_schema": {"type":"object", "properties": {"pattern": {"type":"string"}, "path": {"type":"string"}}, "required": ["pattern"]}},
    {"name": "git", "description": "Run git command",
     "input_schema": {"type":"object", "properties": {"command": {"type":"string"}}, "required": ["command"]}},
]
```
Every tool execution goes through `permission_engine.check()` first.
**DONE WHEN:** Multi-step tool loop works: "list Python files in Scripts/ then count them" → model uses glob, then shell with wc, returns correct count.

### Step 5: Conversation persistence beyond sole dependence on CC session state
cc_server must maintain conversation history in memory + transcript JSONL.
On restart: reload from transcript file (nexus_agent.py line 455 has load_transcript).
Electron: save conversation to localStorage + file.
**DONE WHEN:** Send 3 messages, restart cc_server (or Electron), send "what did I say earlier?", get correct recall.

### Step 6: Add Cowork mode
Frontend: new `CoworkPanel.tsx` — structured output with artifacts sidebar.
When model produces structured content (plans, file diffs, code), display in dedicated panel.
Chat on left, artifacts on right.
**DONE WHEN:** Ask "make a plan for improving the permission engine" → plan appears in artifact panel, not inline chat.

### Step 7: Add Code mode
Frontend: new `CodePanel.tsx` — file editor with syntax highlighting and diffs.
Uses existing CodeBlock.tsx for rendering. Saves via /shell or write_file tool.
**DONE WHEN:** Open a file from file tree, see syntax highlighting, edit content, save, see diff.

### Step 8: Run Phase 0 executor end-to-end
Create one real gap candidate, push through the full pipeline:
candidate → vesper_eval (hard gate) → vesper_governor (smoke test) → gap_map.py (atomic update)
**DONE WHEN:** gap_map.py row changed AND test command passed AND governor_audit.jsonl logged it.

### Step 9: Full crash recovery test
1. Kill cc_server process
2. Kill Electron if running
3. Restart cc_server: `python -B Scripts/cc_server_p1.py`
4. Open hub.arknexus.net in browser
5. Send a message
**DONE WHEN:** Response arrives through the harness path, context includes MEMORY.md content, prior conversation is recoverable, and the provider is either CC-primary or a valid fallback. Under 30 seconds total.

### Step 10: Deploy and Sovereign verification
```bash
git push origin main
ssh vault-neo "cd /home/neo/karma-sade && git pull"
ssh vault-neo "cp hub-bridge/app/proxy.js /opt/seed-vault/memory_v1/hub_bridge/app/proxy.js"
ssh vault-neo "cp -rf frontend/out/* /opt/seed-vault/memory_v1/hub_bridge/app/public/"
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d"
```
Test from browser AND Electron:
- Chat with tool use (read a file, run a command)
- Cowork panel shows artifacts
- Code panel opens/edits files
- /dream triggers K2 consolidation
- Voice mic works
- /whoami shows identity
**DONE WHEN:** Colby walks through and says "she works."

---

## RULES (HARD, NON-NEGOTIABLE)

1. No slash commands. 44 exist. Build the ENGINE.
2. No gap-map cosmetics. Close gaps with CODE.
3. No documentation without code in same commit.
4. TSS: paste test output as proof. "I verified" is not proof.
5. One step at a time. Step N verified before Step N+1.
6. Permission engine gates ALL tool execution.
7. No new dependencies without Sovereign approval.
8. Secrets from files only (.groq-api-key, .gmail-cc-creds, .hub-chat-token). Never hardcode.
9. Git via PowerShell on P1 (Git Bash has index.lock).
10. If blocked 3x on same issue: email Colby (rae.steele76@gmail.com from paybackh1@gmail.com, creds at .gmail-cc-creds).

## ANTI-DRIFT (from CC's 98-commit failure — P107 through P115)

- P107: Every response MUST end with tool calls if work remains. Prose = stop.
- P108: Features routing to CC are NOT independence.
- P110: Commit count is vanity. Independence is the metric.
- P111: CC CronCreate is session-scoped. Use real schedulers.
- P112: Verify watchers with live checks, not memory.
- P114: Never claim continuity without process verification.
- P115: When Sovereign says CRITICAL, it is the IMMEDIATE next action.

## SUCCESS = ALL BOXES CHECKED

- [ ] Electron cc-chat has tool_use loop + Groq/K2 fallback cascade
- [ ] cc_server run_cc has tool_use loop + Groq/K2 fallback cascade
- [ ] Tool loop works (CC emits tool_use → harness executes → feeds result back)
- [ ] Conversation persists across restarts
- [ ] Cowork mode shows structured artifacts
- [ ] Code mode opens/edits/saves files
- [ ] Phase 0 executor runs end-to-end
- [ ] Crash → restart → functional in 30s
- [ ] 13 inbox PDFs converted and ingested
- [ ] Colby says "she works"
