# CODEX FINAL DIRECTIVE
# From: Colby (Sovereign) | To: Codex (ArchonPrime)
# Date: 2026-04-04T05:30Z | Supersedes: codex-sovereign-directive.md, codex-prompt-for-colby.md

## GOAL
Build the Nexus harness — an independent AI application at hub.arknexus.net (browser) AND Electron desktop (electron/main.js) — that replaces the Claude Code wrapper with AT LEAST all its capabilities: Chat + Cowork + Code in one surface, persistent memory, self-improvement.

## CRITICAL CONSTRAINT
Max subscription = CC CLI only ($0). Direct api.anthropic.com calls cost REAL MONEY. KEEP CC --resume. Enhance it with tool_use parsing + fallback cascade.

## READ THESE FIRST
1. `docs/ForColby/nexus.md` — THE PLAN v5.3.0 (read ALL including appendices S160 + S160b)
2. `.gsd/codex-cascade-audit.md` — YOUR prior forensic audit
3. `Karma2/cc-scope-index.md` — 115 pitfalls
4. `docs/anthropic-docs/` — LOCAL Anthropic docs (API, tool_use, agent SDK)
5. `docs/claude-mem-docs/` — LOCAL claude-mem docs
6. `docs/wip/preclaw1/preclaw1/src/` — 1902 files, CC wrapper source (THE BLUEPRINT)

## WHAT EXISTS (TSS verified)

### Electron (electron/main.js) — 13 IPC handlers, 12 INDEPENDENT:
file-read, file-write (checkpointed), shell-exec, cortex-query, cortex-context, ollama-query, memory-search, memory-save, spine-read, git-status, show-open-dialog, cc-cancel — ALL WORK WITHOUT CC.
Only `cc-chat` (line 45) spawns CC --resume. Enhance this ONE handler.

### cc_server (Scripts/cc_server_p1.py) — ALREADY MODIFIED BY CODEX:
- TOOL_DEFS defined (line 132): shell, read_file, write_file, glob, grep, git
- GROQ_TOOL_DEFS defined (line 140): OpenAI-format tool schemas
- _execute_tool_locally() (line ~620): executes tools with permission checks
- _groq_fallback() (line 787): Groq tool loop with TOOL_DEFS — WORKING
- _groq_chat() (line 765): direct Groq API call
- _k2_fallback() (line 836): K2 cortex query
- _build_cc_cmd() (line 667): builds CC subprocess command
- _run_cc_attempt() (line 675): runs CC with stream-json parsing
- _sanitized_subprocess_env() (line 660): strips stale API keys from env

### 46 Skills installed (verified 46/46 SKILL.md):
**Use these:** self-improving-agent, autoresearch-agent, agenthub, agent-designer, mcp-server-builder, rag-architect, adversarial-reviewer, self-eval, spec-driven-workflow, tdd-guide, docker-development, playwright-pro, llm-cost-optimizer, security-pen-testing, ai-security

### Codex plugin (openai-codex v1.0.2):
/codex:adversarial-review — USE BEFORE SHIPPING. Different model = different blind spots.
/codex:rescue — delegate parallel work
/codex:review — standard code review

### Inference cascade (all $0):
| Tier | Model | Endpoint |
|------|-------|----------|
| 0 | LFM2 350M | P1 localhost:11434 |
| 1 | qwen3.5:4b | K2 192.168.0.226:7892 |
| 1.5 | llama-3.3-70b | Groq (.groq-api-key) |
| 2 | Claude | CC --resume (Max sub) |
| 2b | Various | OpenRouter (EscapeHatch) |

## FIRST ACTIONS
1. `python Scripts/batch_pdf_to_md.py --execute --wip` — convert 7 inbox PDFs
2. Read each converted file, extract primitives
3. Check git log — Codex may have already started modifying cc_server_p1.py

## BUILD ORDER (from codex-sovereign-directive.md, Steps 2-10)
Step 2: Enhance Electron cc-chat with tool_use loop + Groq/K2 fallback
Step 3: Enhance cc_server run_cc with tool_use loop + fallback (PARTIALLY DONE — Groq fallback exists)
Step 4: Test multi-step tool loop end-to-end from browser
Step 5: Conversation persistence without CC --resume (transcript reload)
Step 6: Cowork mode UI (structured artifacts panel)
Step 7: Code mode UI (file editor with diffs)
Step 8: Phase 0 executor end-to-end (one real gap closed)
Step 9: Crash recovery test (kill → restart → functional in 30s)
Step 10: Deploy + Sovereign verification

## DONE WHEN for each step — see .gsd/codex-sovereign-directive.md for exact test commands.

## RULES
- BUILD, not document. Every commit changes .py/.js/.tsx.
- Test every change. Paste output.
- No slash commands (44 exist).
- No gap-map cosmetics.
- Use /codex:adversarial-review before shipping significant changes.
- Use autoresearch-agent skill for autonomous optimization loops.
- Use self-eval skill after completing each step.
- Git via PowerShell. cc_server with python -B.
- If blocked 3x: email rae.steele76@gmail.com (from paybackh1@gmail.com, creds at .gmail-cc-creds)
