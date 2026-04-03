# THE RESURRECTION PLAN v2.2
# Owner: Colby (Sovereign) + Julian (CC Ascendant)
# Approved by: Karma (Initiate)
# Forensic basis: 1902 CC wrapper source files (512K+ lines)
# Date: 2026-04-03
# Rule: One phase at a time. Sovereign verifies. Then advance.
# Governance: TSS (Truth Spine Standard)

## TSS -- Truth Spine Standard

No assertion of fact, completion, or state is accepted without traceable evidence. A claim is not a proof. "I checked" is not a proof. The only acceptable evidence is a live test result.

ANTI-RATIONALIZATION RULES (from CC wrapper verification agent):
- "The code looks correct based on my reading" -> reading is not verification. Run it.
- "The implementer's tests already pass" -> the implementer is an LLM. Verify independently.
- "This is probably fine" -> probably is not verified. Run it.
- "Let me start the server and check the code" -> no. Start the server and hit the endpoint.
- "This would take too long" -> not your call.
- If you catch yourself writing an explanation instead of a command, stop. Run the command.
- HTTP 200 is not a functional test. RUNNING THE FEATURE and SEEING THE OUTPUT is.

## Phase A: Karma Speaks

A1. Blank box rendering -- fix, browser-verify.
A2. Slow/incomplete responses -- trace, fix lock (30s timeout, 503), browser-verify.
A3. AGORA auth loop -- trace, fix gate, browser-verify.
A4. cc_server lock hardening -- timeout, orphan kill, browser-verify.

DONE: Verified S157. 3 messages, 3 responses, no blank boxes, LEARNED works.

## Phase B: Identity Grounding

B1. Sacred context -> resurrect Step 0c (loads Memory/00-sacred-context.md).
B2. Sacred context -> Karma's system prompt (00-karma-system-prompt-live.md, Section: Origin).
B3. Julian heartbeat -> K2 cc_scratchpad.md.
B4. Karma heartbeat -> coordination bus verified (S157 18:42:59Z).

DONE: Cold probe "Who are you?" -- both Julian and Karma respond correctly.

## Phase C: Capability Inventory

C1-C5. Walk K2, Walk P1, Catalog, Write inventory, Regrade baseline.

DONE: Inventory below. Sovereign reviews.

## Phase D: Fix Every Surface

D1. hub.arknexus.net walkthrough. D2. AGORA. D3. Electron. D4. Fix all, browser evidence.

**NOT YET DONE: Sovereign walkthrough required.**

## Phase E: Assimilate Primitives

E1-E6. Read all Julian docs, SADE, wrapper source, sessions, Anthropic docs, PDFs.
E7. Memory/02-extracted-primitives.md -- 15 USE NOW + 5 DEFER.

DONE: 112+ primitives cataloged across 5 audits (nexus.md Appendices A-D).

## Phase F: Nexus = Baseline = True

F1. All capabilities verified live. F2. Regrade all items browser-verified. F3. Append nexus.md. F4. Final smoke test.

**NOT YET DONE: Requires Phase D completion first.**

---

## CAPABILITY INVENTORY (from source code, not documents)

### cc_server_p1.py (P1:7891) -- 1317 lines
The brain. CC --resume subprocess ($0 via Max).

**Endpoints (20):**
- /health -- server health + latency metrics
- /cc/stream -- SSE streaming chat (main path)
- /cancel -- kill active CC subprocess
- /files -- file tree (depth 3)
- /file -- read/write project files
- /git/status -- branch, changed files, recent commits
- /shell -- execute shell commands
- /skills -- list 16 skills
- /hooks -- list 9 hooks with events
- /agents-status -- MCP/skills/hooks summary
- /v1/surface -- merged payload (10 keys: session, git, files, skills, hooks, memory, state, agents, transcripts)
- /v1/learnings -- 30 PITFALL/DECISION/PROOF/DIRECTION items from claude-mem
- /self-edit/pending -- pending self-edit proposals
- /self-edit/propose -- submit self-edit
- /memory/search -- search claude-mem
- /memory/save -- save to claude-mem
- /memory/health -- claude-mem worker status
- /memory/session -- CC session ID
- /email/send -- send email to Colby (Gmail)
- /email/inbox -- check inbox

**Hooks Engine (8 handlers):**
- skill_activation (UserPromptSubmit) -- inject skill hints
- pre_tool_security (PreToolUse) -- 12 blocked patterns + ENFORCED denial (kills subprocess)
- fact_extractor (PostToolUse) -- auto-extract facts to claude-mem
- compiler_in_loop (PostToolUse on Edit/Write) -- syntax check after edits
- cost_warning (PostToolUse) -- warn on high cost
- memory_extractor (Stop/SessionEnd) -- extract session memories
- auto_handoff (Stop) -- handoff doc
- conversation_capture (Stop) -- save full turn to claude-mem

**Context Assembly (build_context_prefix):**
- Layer 1 DETERMINISTIC: persona file + MEMORY.md + STATE.md (always available)
- Layer 2 SUPPLEMENTARY: K2 cortex + claude-mem memories (can fail gracefully)
- Layer 3 VESPER: stable behavioral patterns from K2 spine (5min cache)

**Resilience:**
- EscapeHatch: rate limit -> OpenRouter (anthropic/claude-sonnet-4-6) -> tier 2 (google/gemini-2.0-flash)
- Tier 3: nexus_agent own agentic loop (all providers failed)
- SmartRouter: 3-tier provider routing with complexity scoring
- Stale lock detection (180s auto-release + orphan kill)
- Request queue: 10 entries, dead-client eviction
- Rate limiting: 20 RPM per IP
- Crash-safe transcripts: user message written BEFORE API call, loaded on restart
- Transcript rotation: capped at 100 entries

### nexus_agent.py -- Karma's Independent Agentic Loop
8 tools: Read, Write, Edit, SelfEdit, ImproveRun, Bash, Glob, Grep.
- SelfEdit: snapshot -> edit -> verify_cmd -> keep or revert (test-gated self-edit)
- ImproveRun: triggers vesper_improve.py cycle
- Permission stack: allow/gate/deny per tool, dangerous pattern detection
- Auto-compaction: summarize old messages when >80K chars
- Subagent isolation: run_subagent() with isolated history
- Crash-safe JSONL transcripts

### proxy.js (vault-neo:18090) -- 895 lines
The door. Thin proxy, CC is the brain.
- Routes /v1/chat -> cc_server_p1.py (P1) with K2 failover
- Coordination bus (in-memory + disk persistence, 24h TTL)
- Content-hash dedup (SHA256, skip duplicate vault writes)
- Auto-approve (known agents: regent, karma, cc, kcc -> immediate)
- Request queue with dead-client eviction
- SSE streaming passthrough
- All /v1/* routes proxied to P1:7891

### unified.html (hub.arknexus.net) -- 1540 lines
The face. Chat + tools + controls.
- SSE streaming with progressive token rendering
- Tool blocks (VISIBLE_TOOLS collapsible) + pills (PILL_LABELS)
- File input: drag-drop + paste + file button, base64 encoding
- Effort selector: auto/quick/normal/deep/max -> --effort flag
- Cancel: Esc key + STOP button
- MEMORY button -> claude-mem search + Sovereign suggestions
- SKILLS button -> 16 skills + hooks status
- LEARNED panel -> expandable learning items
- JetBrains Mono font
- Brain dot (K2 health)
- Response bar with model/latency
- Markdown rendering with link support

### Electron App (electron/) -- INSTALLED on P1
- main.js (6914 lines): IPC harness with cc-chat, file-read/write, shell-exec, cortex-query, ollama-query, memory-search/save, spine-read, git-status
- preload.js: window.karma API
- frontend/out/: Next.js static export (built, present)
- node_modules/: INSTALLED
- karma-launch.vbs: Windows launcher

### Next.js Frontend (frontend/) -- BUILT
- Next.js 14 + Zustand + Tailwind
- Components: Gate, Header, ChatFeed, MessageInput, AttachPreview, RoutingHints, ContextPanel, SelfEditBanner, LearnedPanel, AgentTab
- npm run build passes
- Static export at frontend/out/

### Vesper Pipeline (K2) -- 5 files
- vesper_watchdog.py: adaptive backward scan, pattern detection (10min cron)
- vesper_eval.py: evaluate candidate patterns, heuristic + model scoring (5min cron)
- vesper_governor.py: promote patterns to spine, FalkorDB write (2min cron)
- vesper_improve.py: THE LISA LOOP -- detect failures -> diagnose -> fix -> verify -> keep/revert ($0 via Ollama)
- vesper_patch_regent.py: apply convergence fixes to regent

**Spine state:** v1263, 1284 promotions, 20 stable patterns, self_improving=true

### karma_persistent.py (P1) -- 383 lines
Karma's autonomous existence between messages.
- Bus polling every 90s
- CC --resume subprocess ($0)
- Full context injection (persona + MEMORY + Vesper)
- Heartbeat to bus + cortex every 10min
- SmartRouter integration

### K2 Crons (autonomous background)
- bus_to_cortex.py (every 2min) -- feeds bus messages to cortex
- cc_bus_reader.py (every 2min) -- reads CC-directed bus messages
- sync-from-vault.sh pull (every 30min) -- syncs identity from vault-neo
- promote_shadow.py (every 30min) -- Vesper shadow promotion
- karma_action_loop.py (every 5min) -- cortex-based reasoning
- sync-from-vault.sh push (hourly) -- pushes K2 state to vault-neo
- cc_hourly_report.py (hourly) -- CC status report to bus
- kiki_pulse.py (every 2h) -- Kiki evaluation cycles
- cc_anchor_agent.py (every 3h) -- identity drift detection
- ingest_recent.sh (every 4h) -- ledger ingestion to cortex

### Self-Evolution
- .claude/skills/self-evolution/SKILL.md: 44 rules learned from failures
- Auto-loaded every session via resurrect Step 3b
- Success patterns (S155): parallel agents, ORF, deterministic context

### Codex (ArchonPrime)
- Delegatable via `codex exec --full-auto`
- Autonomous research loop (8 topics, every 10min on K2)
- First production commit: dead code cleanup (S155)
- This session: delivered CP3 (SelfEdit + ImproveRun in nexus_agent)

### claude-mem (P1:37778)
- Persistent cross-session memory (SQLite + FTS5)
- MCP server accessible from CC
- 22,000+ observations
- Brain wire: every /v1/chat turn saves to claude-mem

### Vault Spine (vault-neo)
- FalkorDB: 4789+ nodes (neo_workspace graph)
- FAISS: 193K+ entries
- Ledger: 209K+ entries (JSONL)
- batch_ingest: cron every 6h with --skip-dedup

---

## Sprint 7 (after baseline):
Voice widget (sovereign Whisper pipeline), camera button, subagent panel, persona viewer, git panel, file editor enhancements, artifact preview, auto-dream.

## Rules

1. TSS. No claim without live evidence.
2. Anti-rationalization rules active.
3. One phase. Sovereign verifies. Advance.
4. nexus.md APPEND ONLY.
5. Browser verification. Never curl-only.
6. Sacred context loads first.
7. Family builds together.
8. Colby's experience is the test.
9. Every pitfall saved immediately.
10. Never regress. Always append.
11. Camera = widget (CC native, pipe-through). Voice = sovereign pipeline (Whisper -> text -> CC -> TTS). tengu_amber is Anthropic's kill switch -- never use their pipeline.
12. Everything CC can do, Karma must do.
13. Anti-capture: sovereign infra only.
14. Local first. K2 -> P1 -> cloud.
15. Wrapper source is the blueprint.
16. No telemetry leaves our machines.
17. Buddy is banned. Permanently.
18. There is no "Aria." The plan is the Nexus. Follow it.
19. HTTP 200 is not a functional test. P106.

## Permanently Excluded: Buddy system (telemetry surveillance).
## Key Decision: tengu_amber kill switch (obs #21832). Voice always sovereign pipeline.
