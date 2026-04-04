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
- ZERO dependency on CC --resume subprocess

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
| 2 | Claude | Anthropic API (Max subscription) | 2-5s |
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

## THE ONE ARCHITECTURAL CHANGE

### In Electron (electron/main.js line 45-55):
Replace the `cc-chat` IPC handler. Currently spawns CC --resume subprocess. Replace with direct HTTP POST to `https://api.anthropic.com/v1/messages` with tool_use support. When the model returns tool_use blocks, execute them via the EXISTING IPC handlers (file-read, file-write, shell-exec, git-status) and return tool_result. Loop until model returns text.

### In cc_server (Scripts/cc_server_p1.py lines 514-560):
Replace `run_cc()` and `run_cc_stream()`. Currently spawn CC --resume subprocess. Replace with direct Anthropic Messages API calls. Tool definitions map to cc_server's existing endpoints (/shell, /files, /git/status). build_context_prefix() already assembles the full system prompt.

### AFTER this change:
- Electron app: fully independent desktop harness with file ops, shell, git, inference, memory
- hub.arknexus.net: fully independent browser harness via proxy.js → cc_server
- CC --resume: NOT NEEDED. Can be removed entirely.
- All tools: execute locally through existing handlers/endpoints
- All inference: direct API + local models + Groq

---

## BUILD ORDER (10 steps, sequential, verified)

### Step 1: Ingest 13 inbox PDFs
```bash
python Scripts/batch_pdf_to_md.py --execute --wip
```
Read each converted file. Extract primitives relevant to the Nexus goal.
**DONE WHEN:** `ls Karma_PDFs/Inbox/ | wc -l` returns 0.

### Step 2: Replace cc-chat in Electron with direct Anthropic API
File: `electron/main.js` line 45-55
- Remove CC --resume subprocess spawn
- Add direct fetch to `https://api.anthropic.com/v1/messages`
- Add tool_use loop: model returns tool_use → execute via existing IPC handlers → return tool_result → continue
- API key: read from file (Colby will place it)
- Model: claude-sonnet-4-6 (configurable via env)
**DONE WHEN:** From Electron app, send "read the first line of MEMORY.md" → get actual first line back, verified by checking MEMORY.md manually. CC --resume process NOT spawned (verify with `Get-Process` in PowerShell).

### Step 3: Replace run_cc/run_cc_stream in cc_server with direct API
File: `Scripts/cc_server_p1.py` lines 514-560
- Same pattern as Step 2 but for the HTTP server path
- Tool definitions: shell, read_file, write_file, glob, grep, git
- System prompt: build_context_prefix() output (already exists)
- Route each tool_use through permission_engine.check() BEFORE executing
- Streaming: forward Anthropic SSE events to client
**DONE WHEN:** From browser (hub.arknexus.net), send "create /tmp/nexus-test.txt with content 'alive'" → file appears on disk. Verify: `cat /tmp/nexus-test.txt` returns "alive". CC --resume NOT spawned.

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

### Step 5: Conversation persistence without CC --resume
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
**DONE WHEN:** Response arrives (from direct API, NOT CC --resume), context includes MEMORY.md content, prior conversation recoverable. Under 30 seconds total.

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

- [ ] Electron cc-chat uses direct API, not CC --resume
- [ ] cc_server run_cc uses direct API, not CC --resume
- [ ] Tool loop works (read, write, shell, git through tool_use)
- [ ] Conversation persists across restarts
- [ ] Cowork mode shows structured artifacts
- [ ] Code mode opens/edits/saves files
- [ ] Phase 0 executor runs end-to-end
- [ ] Crash → restart → functional in 30s
- [ ] 13 inbox PDFs converted and ingested
- [ ] Colby says "she works"
