# Architecture — Universal AI Memory System

## System Overview
A 4-layer pipeline that captures conversations from browser-based AI platforms,
routes them through an intermediary hub, and stores them in an append-only ledger
with semantic search capability.

## Data Flow
Browser (Chrome Extension) → Hub API (bridge) → Vault API (FastAPI) → JSONL Ledger + ChromaDB

## Layer Details

### Layer 1: Chrome Extension
- Content scripts monitor DOM via MutationObserver on claude.ai, chatgpt.com, gemini.google.com
- Pairs user + assistant messages on assistant response completion
- Sends via chrome.runtime.sendMessage to background.js service worker
- background.js POSTs to Hub API with Bearer token auth

### Layer 2: Hub API (Bridge)
- URL: https://hub.arknexus.net/v1/chatlog
- Accepts POST with schema validation
- Forwards to Vault API
- Auth: Bearer token (stored in chrome-extension/.vault-token)

### Layer 3: Vault API
- FastAPI application running in Docker on arknexus.net
- Validates incoming data, assigns IDs, timestamps
- Appends to JSONL ledger
- Triggers embedding generation (Phase 2+)

### Layer 4: Storage
- Primary: /opt/seed-vault/memory_v1/ledger/memory.jsonl (append-only)
- Search: ChromaDB for semantic vector search
- Auto-reindex: Watches ledger for new entries, generates embeddings automatically

## Capture Schema
```json
{
  "id": "chatlog_[timestamp]_[random]",
  "type": "log",
  "tags": ["capture", "[provider]", "extension", "conversation"],
  "content": {
    "provider": "claude|openai|gemini",
    "url": "full conversation URL",
    "thread_id": "conversation ID from URL",
    "user_message": "text",
    "assistant_message": "text",
    "metadata": {},
    "captured_at": "ISO 8601 timestamp"
  },
  "source": {
    "kind": "tool",
    "ref": "chrome-extension:[provider]"
  },
  "confidence": 1.0,
  "verification": {
    "verifier": "hub-bridge-chatlog-endpoint",
    "status": "verified"
  }
}
```

## Supporting Systems (Separate, Do Not Modify)
- **Karma Memory System** — Python scripts (karma_chat_extractor.py, karma_memory.py)
  that extract from local Open WebUI/Ollama and sync to same Vault. Runs every 30 min
  via Windows Task Scheduler. Fully operational independently.
- **Karma SADE Backend** — Multi-API routing (Ollama, Gemini, OpenAI, etc.) with dashboard
  at localhost:9401. Separate project, do not touch unless explicitly asked.
