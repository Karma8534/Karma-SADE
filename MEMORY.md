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
| Multi-Model | ✅ Active | Groq (speed), MiniMax (coding), GLM-5 (reasoning), OpenAI (fallback) |

## Current Task
Identity prioritization fix deployed. Next: fund GLM-5 account, process remaining ~380 captures, expose port 8340 via Caddy for remote CLI.

## Blockers
- GLM-5 (Z.ai) account has insufficient balance — reasoning tasks fall back to OpenAI. Need to fund the BigModel account.

## Karma Core Status (2026-02-16)
- **State**: OPERATIONAL + CONSCIOUS + MULTI-MODEL — 4 LLM providers, task-based routing
- **Stats**: 126 entities, 134 episodes, 819 relationships in FalkorDB
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
  - Commands: /consciousness shows loop metrics
  - Config: CONSCIOUSNESS_ENABLED, CONSCIOUSNESS_INTERVAL, CONSCIOUSNESS_JOURNAL
  - Design doc: karma-core/CONSCIOUSNESS-DESIGN.md
- **Multi-model router**: Task-based routing to best model per message
  - Groq (llama-3.3-70b-versatile): speed/simple chat, ~700ms
  - MiniMax M2.5: coding/technical tasks, 80.2% SWE-Bench
  - GLM-5 (Z.ai/BigModel): reasoning/analysis — **NEEDS BALANCE** (falls back to OpenAI)
  - OpenAI gpt-4o-mini: fallback for all task types, consciousness analysis
  - Classification: keyword-based (zero LLM cost), deterministic
  - Automatic fallback on provider failure
  - Commands: /models shows providers + usage stats
  - Ledger logs which model handled each message
  - File: karma-core/router.py

## Karma Brain Stack
- **FalkorDB**: Running on vault-neo (Docker, port 3000/7687), temporal knowledge graph
- **Graphiti**: graphiti-core[falkordb] — entity/relationship extraction, real-time episode ingestion
- **PostgreSQL**: analysis schema with 94 records (facts + preferences)
- **Chat Server**: FastAPI + WebSocket on port 8340 (karma-server container)
  - GET /health, GET /status, GET /ask?q=..., WebSocket /chat
  - Commands: /status, /goals, /graph, /reflect, /consciousness, /models, /know, /rel
  - Logs conversations to JSONL ledger
  - Queries FalkorDB for context, PostgreSQL for preferences
  - Multi-model routing: Groq (speed), MiniMax (code), GLM-5 (reasoning), OpenAI (fallback)
  - Real-time Graphiti ingestion after every chat turn (non-blocking background task)
- **CLI Client**: karma-core/cli.py (karma chat, karma status, karma ask)
- **Desktop Shortcut**: karma-chat.ps1 → SSH → docker exec → cli.py chat
- **Files**: karma-core/Dockerfile, requirements.txt, config.py, bootstrap.py, server.py, consciousness.py, router.py, cli.py, karma-chat.ps1, create-shortcut.ps1, karma-icon.ico
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
2026-02-16 — Identity prioritization fix: Karma now greets as "Colby" (real name) instead of "Neo" (alias). Structured identity context in system prompt.
