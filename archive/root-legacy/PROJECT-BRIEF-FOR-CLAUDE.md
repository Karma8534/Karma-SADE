# Universal AI Memory System - Project Brief

## Overview
I'm building a Chrome extension that captures my conversations from Claude.ai, ChatGPT, and Gemini, storing them in a personal Vault on my DigitalOcean droplet. This creates a unified, permanent memory across all AI platforms that I own and control.

## Architecture
```
Chrome Extension (browser)
    ↓ HTTPS POST + Bearer Token
Hub API (hub.arknexus.net/v1/chatlog)
    ↓ Internal API
Vault API (FastAPI)
    ↓ Append-only ledger
JSONL File (/opt/seed-vault/memory_v1/ledger/memory.jsonl)
```

## Current Status: Phase 1 - Capture MVP (95% Complete)

### What's Working ✅
1. **Chrome Extension** - Fully built and installed
   - 7 files: manifest.json, background.js, 3 content scripts, popup UI
   - Monitors claude.ai, chatgpt.com, gemini.google.com
   - Uses MutationObserver for real-time conversation detection
   - Bearer token authentication
   - Stats tracking (captured/failed)

2. **Hub API Endpoint** - Deployed and tested
   - URL: https://hub.arknexus.net/v1/chatlog
   - Schema validated (type: log, correct field structure)
   - Test capture verified in ledger
   - Authentication working

3. **Vault Storage** - Operational
   - JSONL append-only ledger
   - Currently: 4 captures total (2 real, 2 test)
   - Located: /opt/seed-vault/memory_v1/ledger/memory.jsonl

### Current Issue ⚠️
Extension shows 0 captured / 0 failed in popup UI. This means:
- Extension installed but content scripts haven't detected/captured any live conversations yet
- Need to test by having actual conversations on Claude.ai/ChatGPT/Gemini
- Extension should automatically detect new messages and capture them

### What I Need to Test Now
1. Have a conversation here on Claude.ai (this one counts!)
2. Check extension popup - should show "1 CAPTURED"
3. Verify in Vault: `ssh vault-neo "tail -1 /opt/seed-vault/memory_v1/ledger/memory.jsonl | jq ."`
4. Repeat on ChatGPT and Gemini
5. Target: 100 total conversation turns captured

## Phase Breakdown

### Phase 1: Capture MVP (Current) - $24/mo
**Goal**: Capture and store 100+ conversations with 0% data loss

**Components**:
- Chrome extension (complete)
- Hub API endpoint (complete)
- Vault storage (complete)
- Testing: 4/100 captures

**Success Criteria**:
- [ ] 100 conversation turns captured
- [ ] All 3 platforms working (Claude, ChatGPT, Gemini)
- [ ] 0% data loss
- [ ] Stats showing in extension popup

### Phase 2: Embeddings & Semantic Search - $29-34/mo
**Goal**: Make memories searchable

**Will Add**:
- Embeddings generation (OpenAI API or local)
- Vector database (ChromaDB or FAISS)
- Semantic search endpoint
- Query: "How did I solve X last time?"

**Not Started Yet**

### Phase 3: Context Injection - Same cost
**Goal**: Auto-inject relevant memories into new conversations

**Will Add**:
- Memory retrieval on conversation start
- Relevance ranking
- Context window management
- "You mentioned this 2 weeks ago..." capability

**Not Started Yet**

### Phase 4: Autonomous Agent - TBD
**Goal**: AI that remembers everything and acts proactively

**Vision**:
- Monitors all conversations
- Learns patterns and preferences
- Proactively suggests actions
- Cross-platform continuity

**Future Exploration**

## Technical Details

### Data Format (Per Capture)
```json
{
  "id": "chatlog_[timestamp]_[random]",
  "type": "log",
  "tags": ["capture", "claude", "extension", "conversation"],
  "content": {
    "provider": "claude",
    "url": "https://claude.ai/chat/abc-123",
    "thread_id": "abc-123",
    "user_message": "User's question...",
    "assistant_message": "AI's response...",
    "metadata": {},
    "captured_at": "2026-02-12T19:30:00Z"
  },
  "source": {
    "kind": "tool",
    "ref": "chrome-extension:claude"
  },
  "confidence": 1.0,
  "verification": {
    "verifier": "hub-bridge-chatlog-endpoint",
    "status": "verified"
  }
}
```

### Extension Token
Bearer: `6a5ba4cdc661886d33e7a19741be3d9c2847451b88029be1f4a51b6da929fc78`
(Stored in: `chrome-extension/.vault-token`)

### How Content Scripts Work
1. MutationObserver watches DOM for new message elements
2. When assistant responds, pairs user message + assistant message
3. Sends to background.js via chrome.runtime.sendMessage
4. Background makes HTTPS POST to Hub API
5. Hub forwards to Vault API
6. Vault appends to JSONL ledger
7. Extension updates stats

### Files Structure
```
chrome-extension/
├── manifest.json          # Chrome extension config
├── background.js          # API communication service worker
├── content-claude.js      # Claude.ai DOM scraper
├── content-openai.js      # ChatGPT DOM scraper
├── content-gemini.js      # Gemini DOM scraper
├── popup.html             # Extension popup UI
├── popup.js               # Stats and config management
└── icons/                 # 16px, 48px, 128px icons
```

## Supporting Systems (Already Built)

### Local Karma Memory System
- Separate system for Open WebUI (local Ollama conversations)
- Scripts: karma_chat_extractor.py, karma_memory.py
- Also syncs to same Vault
- Runs every 30 minutes via Task Scheduler
- Status: Fully operational

### Karma SADE Backend
- Multi-API AI routing system
- 5 AI backends with smart routing (Ollama, Gemini, OpenAI, etc.)
- Dashboard at localhost:9401
- Separate from this Chrome extension project

## Cost Analysis
- **Phase 1**: $24/mo (droplet only)
- **Phase 2**: $29-34/mo (adds embeddings API)
- **Phase 3**: Same as Phase 2 (no new costs)
- **Phase 4**: TBD (depends on agent architecture)

Annual: $288/yr (Phase 1) → $348-408/yr (Phase 2+)

## Next Immediate Steps
1. Have this conversation on Claude.ai (tests extension)
2. Check extension popup for capture confirmation
3. Verify in Vault ledger
4. Repeat on ChatGPT and Gemini
5. Accumulate 96 more captures to hit 100

## Why This Matters
- **Zero vendor lock-in**: I own all my data
- **Cross-platform memory**: One unified memory across all AIs
- **Foundation for autonomy**: Enables future AI agent that truly remembers
- **Privacy**: No third-party has access to my conversations
- **Permanence**: Conversations never lost, always searchable

## Repository
https://github.com/Karma8534/Karma-SADE.git

## Server Access
SSH: `ssh vault-neo`
Droplet: arknexus.net (DigitalOcean NYC3, 4GB RAM)

## Current Session Goal
Debug why extension shows 0/0 despite infrastructure being ready, then validate with real conversation captures.
