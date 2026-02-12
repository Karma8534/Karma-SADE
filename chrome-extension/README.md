# Universal AI Memory - Chrome Extension

## Overview

Captures conversation turns from Claude.ai, ChatGPT, and Gemini for persistent memory storage in your personal Vault.

**Phase 1 MVP Features:**
- ✅ Automatic conversation capture from 3 AI platforms
- ✅ Secure bearer token authentication
- ✅ Real-time sync to Hub → Vault pipeline
- ✅ Capture statistics tracking
- ✅ Easy enable/disable toggle

## Architecture

```
┌─────────────────┐
│  Chrome         │
│  Extension      │
│  (This Code)    │
└────────┬────────┘
         │
         │ HTTPS POST
         │ Bearer Token Auth
         ▼
┌─────────────────┐
│  Hub API        │
│  hub.arknexus.  │
│  net/v1/chatlog │
└────────┬────────┘
         │
         │ Internal
         ▼
┌─────────────────┐
│  Vault API      │
│  PostgreSQL DB  │
└─────────────────┘
```

## Installation

### 1. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select this directory: `C:\Users\raest\Documents\Karma_SADE\chrome-extension`

### 2. Configure Vault Token

1. Click the extension icon in Chrome toolbar
2. Enter your Vault bearer token
3. Toggle "Memory Capture" to ON
4. Click "Save Configuration"

### 3. Get Your Vault Token

SSH to your droplet:
```bash
ssh neo@arknexus.net
grep VAULT_BEARER /opt/seed-vault/memory_v1/.env
```

Copy the token value (everything after `VAULT_BEARER=`)

## How It Works

### Content Scripts

Each AI platform has a dedicated content script:

- **content-claude.js** - Monitors Claude.ai conversations
- **content-openai.js** - Monitors ChatGPT conversations
- **content-gemini.js** - Monitors Gemini conversations

Each script:
1. Uses `MutationObserver` to detect new messages
2. Extracts user/assistant message pairs
3. Sends to background script for processing

### Background Script

**background.js** handles:
- Authentication with Hub API
- HTTP POST requests to `/v1/chatlog`
- Statistics tracking (captured/failed counts)
- Configuration management

### Popup UI

**popup.html** provides:
- Enable/disable toggle
- Token configuration
- Live statistics
- Status messages

## Data Flow

1. User has conversation on Claude.ai/ChatGPT/Gemini
2. Content script detects new messages via DOM observation
3. Script pairs user message with assistant response
4. Sends to background.js with metadata:
   - Provider (claude/openai/gemini)
   - URL and thread ID
   - Timestamp
   - Full message content
5. Background makes POST to Hub API
6. Hub validates and forwards to Vault
7. Vault stores in PostgreSQL
8. Extension updates statistics

## Captured Data Format

```json
{
  "provider": "claude",
  "url": "https://claude.ai/chat/abc-123",
  "timestamp": "2026-02-12T22:30:00Z",
  "user_message": "User's question or prompt",
  "assistant_message": "AI's response",
  "thread_id": "abc-123",
  "metadata": {
    "page_title": "Chat - Claude",
    "captured_at": "2026-02-12T22:30:05Z"
  }
}
```

## Testing

### Manual Test

1. Install and configure extension
2. Visit Claude.ai, ChatGPT, or Gemini
3. Start a conversation
4. Check extension popup for updated statistics
5. Check browser console (F12) for logs:
   - `[UAI Memory] Turn captured successfully`

### Verify in Vault

```bash
ssh neo@arknexus.net
docker exec anr-vault-db psql -U memory -d memoryvault -c "SELECT id, type, tags, timestamp FROM memories WHERE tags @> ARRAY['capture'] ORDER BY timestamp DESC LIMIT 5;"
```

## File Structure

```
chrome-extension/
├── manifest.json           # Extension configuration (Manifest V3)
├── background.js           # Service worker (API communication)
├── content-claude.js       # Claude.ai content script
├── content-openai.js       # ChatGPT content script
├── content-gemini.js       # Gemini content script
├── popup.html              # Extension popup UI
├── popup.js                # Popup logic and config management
├── icons/
│   ├── icon16.png         # 16x16 toolbar icon
│   ├── icon48.png         # 48x48 extension page icon
│   └── icon128.png        # 128x128 Chrome Web Store icon
└── README.md              # This file
```

## Current Status

**Phase 1: Capture MVP**
- ✅ Extension code complete
- ✅ All 3 platform scrapers implemented
- ⏳ Hub endpoint deployed (schema fix pending)
- ⏳ End-to-end testing
- ⏳ 100 conversation turns captured

**Known Issues:**
1. Hub endpoint has Vault schema mismatch (fix documented in `/tmp/CHATLOG_ENDPOINT_FIX.md`)
2. Icons are placeholders (functional but not polished)
3. DOM selectors may need adjustment as platforms update

## Phase 2 (Future)

- Embeddings generation (API or local)
- Semantic search/retrieval
- Context injection into new conversations
- Memory visualization dashboard

## Troubleshooting

### No messages captured

1. Check console logs (F12): Look for `[UAI Memory]` messages
2. Verify token is configured correctly
3. Check "Memory Capture" toggle is ON
4. Refresh the AI platform page

### "Vault write failed" errors

Check Hub logs:
```bash
ssh neo@arknexus.net
docker logs anr-hub-bridge --tail 50
```

### Extension not loading

1. Verify all files are present
2. Check `chrome://extensions/` for errors
3. Reload extension after code changes

## Development

### Make Changes

1. Edit files locally
2. Go to `chrome://extensions/`
3. Click reload icon on the extension
4. Test changes

### View Logs

- Extension background: `chrome://extensions/` → "Service worker" → "Inspect views"
- Content script: Open page → F12 → Console
- Network: F12 → Network tab (filter by "chatlog")

## Success Criteria (Phase 1)

- [ ] 100 conversation turns captured
- [ ] 0% data loss (all turns stored)
- [ ] All 3 platforms working
- [ ] Average capture time < 1 second
- [ ] No user-visible errors

## Cost

**Monthly:** $24 droplet + $0 (capture-only, no embeddings yet) = **$24/month**

Phase 2 will add $5-10/month for embeddings (or $0 if using local embeddings).
