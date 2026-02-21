# Universal AI Memory — Current State

## Active Phase
Karma Core — OPERATIONAL. Multi-model routing + consciousness loop. 4 LLM providers active (MiniMax + GLM-5 + Groq + OpenAI).

## Phase Status
| Phase | Status | Summary |
|-------|--------|---------|
| 1 | ✅ Complete | Capture MVP — extension, hub, vault, JSONL ledger |
| 2 | ✅ Complete | Embeddings & semantic search via ChromaDB (verified operational) |
| 3 | ✅ Complete | Auto-reindexing on new entries |
| 4 | ✅ Complete | Context injection — manual (popup) + autonomous (auto-inject with preview UI) |
| Karma | ✅ Operational | Brain stack + terminal chat + real-time learning + desktop shortcut |
| Consciousness | ✅ Active | 60s OBSERVE/THINK/DECIDE/ACT/REFLECT loop — ambient awareness |
| Multi-Model | ✅ Active | MiniMax M2.5 (primary — coding/speed/general), GLM-5 (reasoning/analysis specialist, priority -1), Groq (fallback), OpenAI (final fallback). |

## Current Task
Hub-bridge v2.4.1 — token budget tuned for gpt-5-mini reasoning model. Karma Window is live and working correctly (Colby + Ollie). Next: Consider PDF/research ingestion pipeline if Colby confirms interest; otherwise, just use Karma and let Graphiti ingest from real conversations.

## Blockers
- Twilio A2P campaign under review — SMS delivery blocked until approved.

## Hub-Bridge History
- v2.1.1: capture auth split, batch chatlog, rate limits, auto-handoff
- v2.2.0: STATE_PRELUDE_V0_1, prelude trimming, token budget, telemetry
- v2.3.0: KARMA_BRIEF in PROMOTE (plain-language session summary for Karma)
- v2.4.0: FalkorDB context via karma-server /raw-context injected into /v1/chat. Luna→Ollie fixed. PROMOTE: ckpt_20260221T064445_vw28bT
- v2.4.1: Token budget raised (DEFAULT 1200→2000, CAP 1600→3000), KARMA_CTX_MAX_CHARS 1800→1200. Fixes (empty_assistant_text) on gpt-5-mini. Karma Window: Enter-to-send, no Send button.

## Karma Core Status (2026-02-21)
- **State**: OPERATIONAL + CONSCIOUS + MULTI-MODEL — 4 LLM providers, task-based routing
- **Stats**: 496 entities, 620 episodes, 4256 relationships in FalkorDB (neo_workspace graph)
- **Batch ingest**: 359/366 episodes processed (7 errors — RediSearch syntax + timeouts). Script: karma-core/batch_ingest.py
- **FalkorDB tuning**: TIMEOUT raised from 1s→5s (graph grew 3x, queries need more time). MAX_QUEUED=25.
- **Test passed**: Tell Karma "My name is Colby" → quit → new session → "What is my real name?" → "Colby"
- **Test passed**: "Adopted a cat named Luna" → quit → new session → "Do I have pets?" → "Luna"
- **Desktop shortcut**: `C:\Users\raest\Desktop\Talk to Karma.lnk` — one-click terminal chat
- **Real-time learning**: Every chat turn → background Graphiti ingest → entities/relationships updated in ~5-8s
- **Identity system**: Structured real_name/alias extraction from FalkorDB. Context outputs `REAL NAME: Colby` with explicit instruction to use it for greetings. Aliases labeled as secondary. Personal facts filtered to Colby entity only (pets, family, life events).
- **Query filter**: Read-only questions (/ask with "what/who/how...") skip graph ingestion to prevent self-reinforcing loops
- **Consciousness loop**: 60s background cycle — OBSERVE/THINK/DECIDE/ACT/REFLECT
  - Idle cycles: 0 LLM calls, ~2ms, $0 cost
  - Active cycles: gpt-4o-mini analysis, ~443ms, logs insights to consciousness.jsonl
  - Insights surface naturally in next chat via context injection
  - **Journal → Graph ingestion**: Active reflections auto-ingest into FalkorDB as episodes (source: karma-consciousness)
  - **SMS alerts**: High-confidence insights (>0.8) trigger SMS to Colby via Twilio. Throttle: 3/hr, 10/day.
  - Commands: /consciousness shows loop metrics
  - Config: CONSCIOUSNESS_ENABLED, CONSCIOUSNESS_INTERVAL, CONSCIOUSNESS_JOURNAL
  - Design doc: karma-core/CONSCIOUSNESS-DESIGN.md
- **Multi-model router**: 4 models, task-based routing with intelligent fallback
  - MiniMax M2.5 (priority 0): PRIMARY for coding, speed, general (80.2% SWE-Bench)
  - GLM-5 (priority -1): REASONING + ANALYSIS specialist (BigModel/Z.ai, deep thinking). Funded 2026-02-17. Tested: 57s response time, excellent quality.
  - Groq (llama-3.3-70b-versatile, priority 5): fallback for speed/general
  - OpenAI gpt-4o-mini (priority 10): final fallback + consciousness analysis
  - `<think>` CoT tags auto-stripped from MiniMax responses
  - Classification: keyword-based (zero LLM cost), deterministic
  - Fallback chain: tries all providers for task type, then any enabled provider
  - Routing: reasoning → GLM-5 → MiniMax → Groq → OpenAI
  - Commands: /models shows providers + usage stats
  - Ledger logs which model handled each message
  - File: karma-core/router.py
- **Ollama integration explored**: `ollama pull minimax-m2.5:cloud` works locally (✅). Exposes OpenAI-compatible API at http://localhost:11434/v1/chat/completions. Server installation blocked by sudo requirement on vault-neo. Current decision: Continue with direct MiniMax API (proven, no additional setup needed). Revisit if credit-saving strategy for cloud models is verified.
- **SMS proactive triggers**: Fully implemented and tested (2026-02-17). Consciousness loop → high-confidence insight detected → SMSManager.notify() → Twilio API. Trigger flow: `consciousness.py` line 386-399 calls `sms_notify()` for ALERT/INSIGHT/GROWTH actions with confidence-based categorization. Server logs show "SMS: ACTIVE (→ 5322)". Awaiting Twilio A2P campaign approval to allow outbound SMS delivery.
- **OpenAI-compatible proxy** (`/v1/chat/completions`): Added 2026-02-17 for Claude Code integration.
  - Endpoint: `POST http://localhost:8340/v1/chat/completions`
  - Accepts OpenAI-compatible JSON format (messages, max_tokens, temperature)
  - Forces `task_type="coding"` → GLM-5 routing via priority system
  - Logs requests to ledger with `source="openai-proxy"` for analytics
  - Returns OpenAI-compatible JSON response format
  - Documentation: CLAUDE_CODE_SETUP.md (configure local Claude Code CLI)
  - Cost optimization: Redirects Claude Code from Haiku API ($0.80/1M input) to $30/mo GLM-5 unlimited

## Karma Brain Stack
- **FalkorDB**: Running on vault-neo (Docker, port 3000/7687), temporal knowledge graph
- **Graphiti**: graphiti-core[falkordb] — entity/relationship extraction, real-time episode ingestion
- **PostgreSQL**: analysis schema with 94 records (facts + preferences)
- **Chat Server**: FastAPI + WebSocket on port 8340 (karma-server container)
  - GET /health, GET /status, GET /ask?q=..., WebSocket /chat, POST /sms/webhook, POST /v1/chat/completions
  - **Remote access**: https://karma.arknexus.net (Caddy auto-TLS, bearer token auth)
  - Bearer token: KARMA_BEARER env var in /opt/seed-vault/memory_v1/compose/.env
  - Public endpoints: /health, /privacy, /terms, /sms/webhook
  - Commands: /status, /goals, /graph, /reflect, /consciousness, /models, /know, /rel
  - Logs conversations to JSONL ledger
  - Queries FalkorDB for context, PostgreSQL for preferences
  - Multi-model routing: MiniMax M2.5 (primary), Groq (fallback), OpenAI (final fallback)
  - Real-time Graphiti ingestion after every chat turn (non-blocking background task)
- **SMS**: Twilio-powered via karma-core/sms.py — **OPERATIONAL**
  - Outbound: breakthrough insights, problem prevention, cross-platform synthesis, timing-sensitive, self-improvement
  - Triggers: Consciousness loop detects high-value insights (confidence ≥ 0.8) and queues SMS via `sms_notify()`
  - Throttle: 3/hr, 10/day, confidence >= 0.8 (enforced in SMSManager)
  - Two-way: Colby texts back → Karma generates response → TwiML reply
  - Webhook: POST /sms/webhook (configure in Twilio console → https://karma.arknexus.net/sms/webhook)
  - FROM: +14848061591 → TO: +14845165322
  - Status: Twilio client initialized ✅, credentials configured ✅, A2P campaign approval ⏳ (pending)
- **CLI Client**: karma-core/cli.py (karma chat, karma status, karma ask)
- **Desktop Shortcut**: karma-chat.ps1 → SSH → docker exec → cli.py chat
- **Files**: karma-core/Dockerfile, requirements.txt, config.py, bootstrap.py, server.py, consciousness.py, router.py, sms.py, cli.py, karma-chat.ps1, create-shortcut.ps1, karma-icon.ico
- **Architecture doc**: KARMA-ARCHITECTURE.md

## Phase 4 Completion Notes (Autonomous Context Injection)
- **Step 1**: Auto-inject toggle in popup (chrome.storage.sync, real-time listener)
- **Step 2**: New conversation detector (Claude: data-test-render-count, ChatGPT: data-message-author-role, Gemini: model-response/user-query)
- **Step 3**: Input monitor with 1.5s debounce, 10-char minimum, first-50-words query extraction
- **Step 4**: Inline preview UI — dark-themed fixed-position floating div above input, shows result count + content preview + Tab/Esc hints
- **Step 5**: Keyboard handlers — Tab injects context + marks conversation injected, Esc dismisses preview
- **Bug fix**: Changed from position:absolute (clipped by overflow:auto parent) to position:fixed with calculated coordinates + body append
- sessionStorage prevents re-injection within same conversation
- All 3 platforms tested and verified via ChromeMCP

## Phase 3 Completion Notes (Manual Injection)
- Search API exposed at https://hub.arknexus.net/v1/search with CORS for claude.ai, chatgpt.com, gemini.google.com
- content-context.js: popup-triggered search → preview modal → DOM injection
- Platform-specific injection: Claude (contenteditable), ChatGPT (ProseMirror div), Gemini (Quill ql-editor)
- Fixed field name mismatches (similarity_score, content_preview, platform)

## Infrastructure
- Server: arknexus.net (vault-neo), 7 Docker containers running
- Containers: karma-server, falkordb, anr-vault-search, anr-vault-api, anr-hub-bridge, anr-vault-db, anr-vault-caddy
- FalkorDB: ~150-300MB RAM, Redis protocol on 6379 internal / 7687 external
- Cost: ~$26/mo (droplet $24 + OpenAI ~$1-2 for analysis)
- Ledger entries: check with `ssh vault-neo "wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"`

## Hub-Bridge v2.1.0 (2026-02-19)
- `/v1/chatlog`: capture auth split from vault bearer → `HUB_CAPTURE_TOKEN` (new secret). Batch ingest (1–200 items). Route-scoped rate limits (240rpm+120burst for capture).
- `/v1/handoff/save` + `/v1/handoff/latest`: atomic file write to `/data/handoff`, `HUB_HANDOFF_TOKEN` auth.
- Tokens: `hub.capture.token.txt`, `hub.handoff.token.txt` in `/opt/seed-vault/memory_v1/hub_auth/`
- Chrome extension `background.js`: durable queue (`storage.local`), batch flush (30s alarm), single-flight guard, exponential backoff on 429. Reads `captureToken || vaultToken` (backward compat).

## Vault API Dual-Tier Rate Limit (2026-02-19)
- `isPrivateIp()`: detects 10.x, 172.16-31.x, 192.168.x, 127.x, ::1 — strips `::ffff:` prefix (Docker bridge IPv4-mapped IPv6)
- `pickRlLimits(req)`: public=30rpm+10burst, internal=240rpm+120burst
- Compose: `RL_RATE_INTERNAL=240`, `RL_BURST_INTERNAL=120` in `anr-vault-api` environment
- Proof: 75/75 sequential burst test succeeded (hub-bridge → vault, private IP path)

## Extension v2.0.0 Canonical (2026-02-19)
- Duplicate extension instances eliminated: removed stale worktree (elegant-solomon) load from Chrome
- manifest.json: v1.0.0 → v2.0.0, content-context.js per-platform (not catch-all), alarms permission retained
- background.js: captureToken preferred over vaultToken, explicit authToken variable, diagnostic log (lengths only)
- captureToken configured in extension popup (64-char hex), verified via storage.sync
- e2e smoke test: chatlog_1771535912555_kjkvknexqy landed in vault ledger ✓
- auth log: `{enabled:true, captureTokenLen:64, vaultTokenLen:0, using:'captureToken'}` ✓

## Last Updated
2026-02-21 — Neo alias purge: Fixed 2 Neo Entity nodes, 2 Colby entity summaries, 3 User entity summaries in FalkorDB neo_workspace. Fixed 4 PostgreSQL analysis.user_preferences (user_name, preferred_nickname, response_style, change_management_rules). Zero Neo leaks in raw-context. Hub-bridge v2.4.1 token budget live.
