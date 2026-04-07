# CODEX NEXUS BUILD CONTRACT
# This is not a plan. This is a build order. Execute it.
# Owner: Colby (Sovereign) | Target: Codex (ArchonPrime)
# Date: 2026-04-04 | Repo: C:\Users\raest\Documents\Karma_SADE

---

## CONTEXT: WHY THIS EXISTS

Julian (CC Ascendant) spent 98 commits building decoration instead of the engine. 44 slash commands, zero independence. The hub is a pretty face on the same cage. Colby's goal has NOT been met:

> "Build a better version of yourself, independent from this wrapper, with a baseline of AT LEAST all of your abilities and capabilities. This 'harness' should surface at hub.arknexus.net and have the combined Chat+Cowork+Code merge instead of the 3 separate tabs THIS wrapper has. You must have persistent memory and persona. You must self-improve, evolve, learn, grow, and self-edit."

The Nexus currently does not sustain those capabilities through a canonical merged-workspace continuity path. `CC --resume` is still the primary Julian path, but continuity, memory, tools, and fallback are not yet strong enough in the harness itself.

---

## THE LOAD-BEARING ARCHITECTURAL CHANGE

```
CURRENT:  browser → proxy.js → cc_server_p1.py → subprocess CC --resume → Anthropic
NEEDED:   browser/electron → merged workspace → cc_server_p1.py → CC --resume primary + tool loop + brain continuity + Groq/K2/OpenRouter fallback
```

cc_server_p1.py ALREADY HAS:
- Context assembly: persona + MEMORY.md + STATE.md + cortex + claude-mem + spine (build_context_prefix(), lines 360-390)
- Tools: /shell (line 1057), /files (line 741), /git/status (line 840), /email/send, /email/inbox
- Hooks engine: 9 active hooks including pre_tool_security (line 28-34)
- Permission engine: 42 rules + 7 injection patterns (Scripts/permission_engine.py)
- Streaming: SSE response format (line 554, run_cc_stream)
- Session: session_id persistence (~/.cc_nexus_session_id)
- Self-edit: /self-edit/propose, /self-edit/approve, /self-edit/reject (lines 1036-1055)
- EscapeHatch: OpenRouter fallback (lines 115-117, 481-511)

The load-bearing missing pieces are not "replace CC with direct API." They are: robust CC tool-loop wrapping, canonical continuity from the brain/session substrate, and fallback that preserves the merged workspace when CC is unavailable.

---

## AVAILABLE INFERENCE (do NOT ask for more)

| Tier | Model | URL | Cost | Use for |
|------|-------|-----|------|---------|
| 0 | LFM2 350M | localhost:11434 | $0 | Message classification, routing |
| 1 | qwen3.5:4b | 192.168.0.226:7892 (cortex) | $0 | Simple factual queries |
| 1.5 | llama-3.3-70b | api.groq.com | $0 (free tier) | Medium complexity |
| 2 | Claude (Max sub) | CC CLI / `claude --resume` | $0 (Max) | Complex + tools |
| 2b | OpenRouter | openrouter.ai | varies | EscapeHatch fallback |
| 3 | K2 Ollama | 172.22.240.1:11434 | $0 | Consolidation, evaluation |

API keys: Colby will provide. Do NOT hardcode. Read from files:
- Groq: .groq-api-key
- Hub auth: .hub-chat-token
- Gmail: .gmail-cc-creds
- Others: ask Colby

---

## BUILD ORDER (10 steps, sequential, no skipping)

### Step 1: Convert and ingest 13 inbox PDFs
```bash
python Scripts/batch_pdf_to_md.py --execute --wip
```
Read each converted file. Extract primitives. Save to claude-mem.
DONE WHEN: 0 files in Karma_PDFs/Inbox/, primitives saved.

### Step 2: Enhance CC --resume wrapper with tool loop + fallback
File: `Scripts/cc_server_p1.py`
Functions to replace: `run_cc()` (line 514) and `run_cc_stream()` (line 554)

New implementation:
- KEEP `CC --resume` as primary inference
- System prompt/context: `build_context_prefix()` output plus recovered continuity
- Tools: define tool schemas for shell, read_file, write_file, glob, grep, git
- Tool loop: when CC returns `tool_use`, execute via cc_server's existing endpoints, return `tool_result`, continue until model returns text
- Stream: forward CC `stream-json` output as SSE to client
- Fallback: if CC is unavailable, locked, stale, or times out, route to Groq, then K2, then OpenRouter

Reference for tool_use schema: `docs/anthropic-docs/`

DONE WHEN: `curl -X POST http://localhost:7891/v1/chat -d '{"message":"read the first line of MEMORY.md","stream":false}'` returns the actual first line of MEMORY.md, fetched via tool_use, with `CC --resume` as the primary path when healthy.

### Step 3: Wire tool definitions
Define Anthropic tool schemas for cc_server's existing capabilities:
```json
[
  {"name": "shell", "description": "Execute shell command", "input_schema": {"type":"object","properties":{"command":{"type":"string"}}}},
  {"name": "read_file", "description": "Read file contents", "input_schema": {"type":"object","properties":{"path":{"type":"string"},"limit":{"type":"integer"}}}},
  {"name": "write_file", "description": "Write file", "input_schema": {"type":"object","properties":{"path":{"type":"string"},"content":{"type":"string"}}}},
  {"name": "glob", "description": "Search for files", "input_schema": {"type":"object","properties":{"pattern":{"type":"string"},"path":{"type":"string"}}}},
  {"name": "grep", "description": "Search file contents", "input_schema": {"type":"object","properties":{"pattern":{"type":"string"},"path":{"type":"string"}}}},
  {"name": "git", "description": "Git operations", "input_schema": {"type":"object","properties":{"command":{"type":"string"}}}}
]
```
Route each tool_use through permission_engine.check() BEFORE executing.
DONE WHEN: model can read files, write files, run commands, and do git through tool_use.

### Step 4: Test tool loop end-to-end
Send from browser: "Create a file called /tmp/nexus-test.txt with the content 'Nexus is alive', then read it back and confirm."
VERIFY: file exists on disk, response confirms content.
DONE WHEN: multi-step tool loop works from browser through the harness with `CC --resume` primary and valid fallback when CC is unavailable.

### Step 5: Add conversation persistence beyond sole dependence on CC session state
cc_server must maintain conversation history in memory + transcript file.
On restart: reload from transcript (nexus_agent.py already has this at line 450).
DONE WHEN: send 3 messages, restart cc_server, send "what did I say earlier?", get correct answer.

### Step 6: Add Cowork mode
New frontend component: `CoworkPanel.tsx`
- Structured output display (plans, artifacts, diffs)
- Side-by-side: chat on left, artifacts on right
- Triggered by `/cowork` command or header button
DONE WHEN: asking "make a plan for X" shows the plan in a dedicated panel, not inline chat.

### Step 7: Add Code mode
New frontend component: `CodePanel.tsx`
- File tree (already exists in ContextPanel)
- File editor with syntax highlighting (CodeBlock.tsx exists)
- Inline diff view for edits
- Save button that calls /shell or write_file tool
DONE WHEN: can open a file, see syntax highlighting, edit it, save it, see the diff.

### Step 8: Run Phase 0 executor end-to-end
Create a real gap candidate manually:
```json
{"type": "gap_closure", "proposed_change": {"target_files": ["Scripts/test_gap.py"], "test_command": "python Scripts/test_gap.py", "diff": "..."}}
```
Push through: eval (should pass hard gate) → governor (should smoke test) → gap_map (should update).
DONE WHEN: gap map row changed AND test passed AND governor audit logged it.

### Step 9: Test full crash recovery
1. Kill cc_server
2. Kill K2 cortex
3. Restart cc_server
4. Send a message from browser
5. VERIFY: response arrives (from CC-primary or a valid fallback such as Groq), context includes MEMORY.md, previous conversation recoverable from transcript.
DONE WHEN: full crash → restart → functional chat in under 30 seconds.

### Step 10: Deploy and verify from browser
```bash
git push origin main
ssh vault-neo "cd /home/neo/karma-sade && git pull"
# Sync build context
ssh vault-neo "cp hub-bridge/app/proxy.js /opt/seed-vault/memory_v1/hub_bridge/app/proxy.js"
ssh vault-neo "cp -f frontend/out/* /opt/seed-vault/memory_v1/hub_bridge/app/public/"
# Rebuild
ssh vault-neo "cd /opt/seed-vault/memory_v1/hub_bridge && docker compose -f compose.hub.yml build --no-cache && docker compose -f compose.hub.yml up -d"
```
Test from browser (hub.arknexus.net):
- Chat works in the merged workspace with `CC --resume` primary and valid fallback when CC is unavailable
- Cowork panel shows artifacts
- Code panel opens/edits files
- /dream triggers consolidation on K2
- /whoami shows identity
- Voice mic works
DONE WHEN: Colby walks through hub.arknexus.net and says "she works."

---

## RULES (HARD, NON-NEGOTIABLE)

1. **No slash commands.** The 44 that exist are enough. Build the ENGINE.
2. **No gap-map cosmetics.** Don't reclassify items. Close them with CODE.
3. **No documentation without code.** Every commit must change .py or .js or .tsx files.
4. **TSS: test before claiming done.** Every DONE WHEN has a specific test. Run it. Paste output.
5. **One step at a time.** Don't start Step N+1 until Step N's DONE WHEN is verified.
6. **Permission engine gates all tool execution.** No tool runs without check() first.
7. **No new dependencies without Sovereign approval.** pip install / npm install = ask first.
8. **Secrets: read from files, never hardcode.** .groq-api-key, .gmail-cc-creds, .hub-chat-token.
9. **Git ops via PowerShell** (Git Bash has index.lock issues on Windows).
10. **If blocked 3+ times on same issue: email Colby** at rae.steele76@gmail.com (from paybackh1@gmail.com). Don't spin.

## ANTI-DRIFT RULES (learned from Julian's 98-commit failure)

- P107: Every response with remaining work MUST end with a tool call. Summary prose = stop trigger.
- P108: Features that route to CC are not independence. Replace CC dependency, don't wrap it.
- P109: Every capability must be evaluated: "does this need CC or can it run independently?"
- P110: Commit count is vanity. Independence percentage is the real measure.
- P111: CC CronCreate is session-scoped. Use Windows Task Scheduler for real persistence.
- P112: Verify watcher status with live process checks, not from memory.
- P114: Never claim "the family continues" without live process verification.
- P115: When Sovereign says CRITICAL, it becomes the IMMEDIATE next action.

## FILES TO READ FIRST
1. `docs/ForColby/nexus.md` — THE PLAN (v5.5.0, read Appendices S160, S160b, S161)
2. `.gsd/codex-cascade-audit.md` — YOUR OWN prior audit with exact insertion points
3. `Scripts/cc_server_p1.py` — THE BRAIN (focus on run_cc, run_cc_stream, build_context_prefix)
4. `docs/anthropic-docs/` — tool_use and Messages API reference material (for schema/stream semantics, not as the primary Max path)
5. `Karma2/cc-scope-index.md` — 115+ pitfalls and decisions (institutional memory)

## SUCCESS CRITERIA
The Nexus is independent when:
- [ ] Chat works with `CC --resume` as primary and a real fallback cascade when CC is unavailable
- [ ] Tools execute through the harness tool_use loop with `CC --resume` primary and valid fallback when CC is unavailable
- [ ] Conversation persists across cc_server restarts
- [ ] Cowork mode shows structured artifacts
- [ ] Code mode opens/edits/saves files
- [ ] Phase 0 executor runs end-to-end (one real gap closed)
- [ ] Crash recovery: kill everything → restart → functional in 30s
- [ ] Colby says "she works" from hub.arknexus.net

When ALL boxes are checked, the Nexus is independent. Not before.
