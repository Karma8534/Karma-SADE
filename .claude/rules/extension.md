# Chrome Extension — Development Reference

## File Structure
```
chrome-extension/
├── manifest.json          v2.0.0, Manifest V3
├── background.js          Service worker — API communication, stats tracking
├── content-claude.js      Claude.ai DOM scraper (MutationObserver)
├── content-openai.js      ChatGPT DOM scraper
├── content-gemini.js      Gemini DOM scraper
├── content-context.js     Phase 4 — context injection
├── popup.html             Extension popup UI
├── popup.js               Stats display and config management
├── test-selectors.js      DOM selector testing utility
└── icons/                 16px, 48px, 128px extension icons
```

## Content Script Pattern (All 3 Providers)
Each content script follows the same pattern:
1. MutationObserver watches for new DOM elements in the chat container
2. On mutation, scan for message elements using provider-specific selectors
3. Classify each message as "user" or "assistant" based on DOM attributes/classes
4. When an assistant message completes, pair it with the preceding user message
5. Send the pair via chrome.runtime.sendMessage({type: 'CAPTURE', ...})
6. background.js receives and POSTs to hub API

## Known Issue — Selector Drift
AI platform frontends update their DOM structure frequently without notice.
When captures stop working (popup shows 0/0), the first thing to check is
whether the CSS selectors and DOM attribute checks in the content scripts
still match the current frontend. Use test-selectors.js or browser DevTools
Elements panel to inspect the live DOM structure.

## Testing Workflow
1. Make changes to content script or background.js
2. Go to chrome://extensions
3. Click reload button on the extension card
4. Open target site (claude.ai, chatgpt.com, or gemini.google.com)
5. Open DevTools Console, filter for [UAI Memory] log prefix
6. Have a conversation — watch for capture logs
7. Check popup for updated stats
8. Verify on server: `ssh vault-neo "tail -1 /opt/seed-vault/memory_v1/ledger/memory.jsonl | jq ."`

## Manifest Permissions
- activeTab, storage, tabs
- Host permissions: claude.ai, chatgpt.com, gemini.google.com
- Content scripts injected at document_idle on matching URLs

## Extension State
- Stats stored in chrome.storage.local under key 'stats' ({captured: N, failed: N})
- Config stored in chrome.storage.local under key 'config' ({enabled: bool, vaultToken: string})
- Token loaded from .vault-token file during extension build/install
