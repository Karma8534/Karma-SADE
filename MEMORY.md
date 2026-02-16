# Universal AI Memory — Current State

## Active Phase
Karma Brain Stack — Foundation installed, bootstrap complete

## Phase Status
| Phase | Status | Summary |
|-------|--------|---------|
| 1 | ✅ Complete | Capture MVP — extension, hub, vault, JSONL ledger |
| 2 | ✅ Complete | Embeddings & semantic search via ChromaDB (verified operational) |
| 3 | ✅ Complete | Auto-reindexing on new entries |
| 4 | ✅ Complete | Context injection — manual (popup) + autonomous (auto-inject with preview UI) |
| Karma | 🔧 In progress | Brain stack foundation — FalkorDB + Graphiti + PostgreSQL analysis |

## Current Task
Karma bootstrap complete. Next: Process remaining 387 captures, build LangGraph consciousness loop, connect to Chrome extension for real-time awareness.

## Blockers
None

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

## Karma Brain Stack (Installed 2026-02-16)
- **FalkorDB**: Running on vault-neo (Docker, port 3000/7687), 101 entities + 100 episodes
- **Graphiti**: graphiti-core[falkordb] for entity/relationship extraction from conversations
- **PostgreSQL**: analysis schema with 94 records (83 facts + 13 preferences, deduped to 86+5+3)
- **karma-core**: Docker image built, bootstrap.py completed successfully
- **Knowledge extracted**: Entities (Neo, Claude Code, Chrome Extension, Docker, FalkorDB, etc.), 475 MENTIONS + 222 RELATES_TO relationships
- **Files**: karma-core/Dockerfile, requirements.txt, config.py, bootstrap.py
- **Architecture doc**: KARMA-ARCHITECTURE.md

## Infrastructure
- Server: arknexus.net (vault-neo), Docker running, ledger operational
- FalkorDB: ~150-300MB RAM, Redis protocol on 6379 internal / 7687 external
- Cost: ~$26/mo (droplet $24 + OpenAI ~$1-2 for analysis)
- Ledger entries: check with `ssh vault-neo "wc -l /opt/seed-vault/memory_v1/ledger/memory.jsonl"`

## Last Updated
2026-02-16 — Karma Brain Stack foundation installed: FalkorDB + Graphiti + PostgreSQL analysis engine, bootstrap complete (100 episodes processed, 94 facts/preferences seeded)
