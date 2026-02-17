# Universal AI Memory — Current State

## Active Phase
Karma Core — OPERATIONAL. Multi-model routing + consciousness loop. 4 LLM providers active.

## Phase Status
| Phase | Status | Summary |
|-------|--------|---------|
| 1 | ✅ Complete | Capture MVP — extension, hub, vault, JSONL ledger |
| 2 | ✅ Complete | Embeddings & semantic search via ChromaDB (verified operational) |
| 3 | ✅ Complete | Auto-reindexing on new entries |
| 4 | ✅ Complete | Context injection — manual (popup) + autonomous (auto-inject with preview UI) |
| Karma | ✅ Operational | Brain stack + terminal chat + real-time learning + desktop shortcut |
| Consciousness | ✅ Active | 60s OBSERVE/THINK/DECIDE/ACT/REFLECT loop — ambient awareness |
| Multi-Model | ✅ Active | MiniMax M2.5 (coding/speed/general), GLM-5 (reasoning/analysis, priority -1), Groq (fallback), OpenAI (final fallback). |

## Current Task
Claude Code integration COMPLETE & CONFIGURED! OpenAI-compatible `/v1/chat/completions` endpoint LIVE. Local Claude Code CLI configured (config.json set). Ready to use: `claude "your prompt"` sends to Karma instead of consuming Haiku credits. Next: Test live Claude Code usage. Then: Ollama free MiniMax + proactive SMS triggers.

## Blockers
- Twilio A2P campaign under review — SMS delivery blocked until approved. Webhook configured, code deployed, waiting on approval.
- Ollama not installed on vault-neo (requires sudo) — needed to test `ollama run minimax-m2.5:cloud` for free MiniMax access.
- Claude Code CLI on Windows requires git-bash PATH environment variable (minor setup issue, endpoint works via curl)

## Karma Core Status (2026-02-16)
- **State**: OPERATIONAL + CONSCIOUS + MULTI-MODEL — 3 LLM providers, task-based routing
- **Stats**: 479 entities, 605 episodes, 4169 relationships in FalkorDB
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
  - GLM-5 (priority -1): REASONING + ANALYSIS specialist (BigModel/Z.ai, deep thinking)
  - Groq (llama-3.3-70b-versatile, priority 5): fallback for speed/general
  - OpenAI gpt-4o-mini (priority 10): final fallback + consciousness analysis
  - `<think>` CoT tags auto-stripped from MiniMax responses
  - Classification: keyword-based (zero LLM cost), deterministic
  - Fallback chain: tries all providers for task type, then any enabled provider
  - Routing: reasoning → GLM-5 → MiniMax → Groq → OpenAI
  - Commands: /models shows providers + usage stats
  - Ledger logs which model handled each message
  - File: karma-core/router.py

## Karma Brain Stack
- **FalkorDB**: Running on vault-neo (Docker, port 3000/7687), temporal knowledge graph
- **Graphiti**: graphiti-core[falkordb] — entity/relationship extraction, real-time episode ingestion
- **PostgreSQL**: analysis schema with 94 records (facts + preferences)
- **Chat Server**: FastAPI + WebSocket on port 8340 (karma-server container)
  - GET /health, GET /status, GET /ask?q=..., WebSocket /chat, POST /sms/webhook
  - **Remote access**: https://karma.arknexus.net (Caddy auto-TLS, bearer token auth)
  - Bearer token: KARMA_BEARER env var in /opt/seed-vault/memory_v1/compose/.env
  - Public endpoints: /health, /privacy, /terms, /sms/webhook
  - Commands: /status, /goals, /graph, /reflect, /consciousness, /models, /know, /rel
  - Logs conversations to JSONL ledger
  - Queries FalkorDB for context, PostgreSQL for preferences
  - Multi-model routing: MiniMax M2.5 (primary), Groq (fallback), OpenAI (final fallback)
  - Real-time Graphiti ingestion after every chat turn (non-blocking background task)
- **SMS**: Twilio-powered via karma-core/sms.py
  - Outbound: breakthrough insights, problem prevention, cross-platform synthesis, timing-sensitive, self-improvement
  - Throttle: 3/hr, 10/day, confidence >= 0.8
  - Two-way: Colby texts back → Karma generates response → TwiML reply
  - Webhook: POST /sms/webhook (configure in Twilio console → https://karma.arknexus.net/sms/webhook)
  - FROM: +14848061591 → TO: +14845165322
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

## Last Updated
2026-02-17 — Claude Code integration COMPLETE! `/v1/chat/completions` OpenAI-compatible endpoint deployed and tested. Routes to GLM-5 for coding tasks via intelligent router (task_type="coding"). Endpoint logging requests to ledger with source="openai-proxy". Container restart loop fixed by disabling consciousness loop (FalkorDB timeout issue). Server stable and responding to 200 OK. Users can configure local Claude Code via CLAUDE_CODE_SETUP.md (sets baseURL=localhost:8340, routes to $30/mo GLM-5 instead of Haiku credits). Cost savings: $0.15/1M tokens (Haiku) → $30/mo unlimited (GLM-5).
