// Universal AI Memory - Context Injection
// Listens for injection requests from popup, fetches relevant context, displays preview
// Also handles Phase 4 auto-injection on new conversations
const SEARCH_ENDPOINT = 'https://hub.arknexus.net/v1/search';
let vaultToken = null;
let autoInjectEnabled = false;

// Get token and settings from storage
chrome.storage.sync.get(['vaultToken', 'autoInjectEnabled'], (result) => {
  vaultToken = result.vaultToken;
  autoInjectEnabled = result.autoInjectEnabled || false;
  console.log('[UAI Memory] Context script loaded. autoInject:', autoInjectEnabled);
});

// Listen for settings changes in real-time
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'sync') {
    if (changes.autoInjectEnabled) {
      autoInjectEnabled = changes.autoInjectEnabled.newValue;
      console.log('[UAI Memory] autoInject toggled:', autoInjectEnabled);
      if (autoInjectEnabled) initAutoInject();
    }
    if (changes.vaultToken) {
      vaultToken = changes.vaultToken.newValue;
    }
  }
});

// Listen for injection trigger from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'INJECT_CONTEXT') {
    handleContextInjection(message.query, message.limit || 3)
      .then(sendResponse)
      .catch(err => sendResponse({ success: false, error: err.message }));
    return true; // Keep channel open for async response
  }
});

// ─── Phase 4: Auto-Injection ─────────────────────────────────────────

function detectNewConversation() {
  const platform = detectPlatform();

  if (platform === 'claude') {
    // div[data-test-render-count] wraps each message turn
    // A fresh /new page has 0; a conversation with the welcome prompt may have 1
    const turns = document.querySelectorAll('[data-test-render-count]');
    const isNew = turns.length <= 1;
    console.log('[UAI Memory] Claude turns:', turns.length, '→ new:', isNew);
    return isNew;
  }

  if (platform === 'chatgpt') {
    // data-message-author-role appears on each message bubble
    const messages = document.querySelectorAll('[data-message-author-role]');
    const isNew = messages.length === 0;
    console.log('[UAI Memory] ChatGPT messages:', messages.length, '→ new:', isNew);
    return isNew;
  }

  if (platform === 'gemini') {
    // model-response elements appear once the assistant has replied
    const responses = document.querySelectorAll('model-response');
    const queries = document.querySelectorAll('user-query');
    const isNew = responses.length === 0 && queries.length === 0;
    console.log('[UAI Memory] Gemini queries:', queries.length, 'responses:', responses.length, '→ new:', isNew);
    return isNew;
  }

  return false;
}

function initAutoInject() {
  if (!autoInjectEnabled) {
    console.log('[UAI Memory] Auto-inject disabled, skipping init');
    return;
  }

  // Don't re-init if already injected this conversation
  if (sessionStorage.getItem('uai-conversation-injected') === 'true') {
    console.log('[UAI Memory] Already injected this conversation, skipping');
    return;
  }

  const isNew = detectNewConversation();
  if (!isNew) {
    console.log('[UAI Memory] Existing conversation, auto-inject skipped');
    return;
  }

  console.log('[UAI Memory] New conversation detected — setting up input monitor');
  sessionStorage.setItem('uai-conversation-injected', 'false');
  setupInputMonitor(); // Step 3 will implement this
}

// ─── Step 3: Input Monitor with Debounce ─────────────────────────────

let autoInjectDebounceTimer = null;
let autoInjectResults = null; // Stash results for inline preview / keyboard handler

function getInputElement() {
  const platform = detectPlatform();
  if (platform === 'claude') return document.querySelector('div[contenteditable="true"]');
  if (platform === 'chatgpt') return document.querySelector('#prompt-textarea');
  if (platform === 'gemini') {
    return document.querySelector('.ql-editor[aria-label*="prompt"]')
      || document.querySelector('rich-textarea .ql-editor')
      || document.querySelector('div[contenteditable="true"][role="textbox"]');
  }
  return null;
}

function extractQuery(text, maxWords) {
  // Take first N words, trim whitespace
  return text.trim().split(/\s+/).slice(0, maxWords).join(' ');
}

function setupInputMonitor() {
  const inputEl = getInputElement();
  if (!inputEl) {
    console.log('[UAI Memory] Input element not found — retrying in 2s');
    setTimeout(setupInputMonitor, 2000);
    return;
  }

  console.log('[UAI Memory] Input monitor attached to', inputEl.tagName, inputEl.id || inputEl.className?.substring(0, 30));

  const onInput = () => {
    // Guard: already injected this conversation
    if (sessionStorage.getItem('uai-conversation-injected') === 'true') {
      console.log('[UAI Memory] Already injected, removing input monitor');
      inputEl.removeEventListener('input', onInput);
      return;
    }

    // Clear previous debounce
    if (autoInjectDebounceTimer) clearTimeout(autoInjectDebounceTimer);

    autoInjectDebounceTimer = setTimeout(async () => {
      const text = inputEl.textContent?.trim() || inputEl.value?.trim() || '';
      console.log('[UAI Memory] Debounce fired, text length:', text.length);

      // Minimum length guard
      if (text.length < 10) {
        console.log('[UAI Memory] Text too short (<10 chars), skipping');
        return;
      }

      // Extract first 50 words as query
      const query = extractQuery(text, 50);
      console.log('[UAI Memory] Auto-inject triggered, query:', query);

      try {
        const results = await searchVault(query, 3);
        if (!results || results.length === 0) {
          console.log('[UAI Memory] No results found, skipping preview');
          return;
        }

        console.log('[UAI Memory] Found', results.length, 'results — showing inline preview');
        autoInjectResults = results;
        showInlinePreview(results); // Step 4 will build the real UI
      } catch (err) {
        console.error('[UAI Memory] Auto-inject search failed:', err.message);
      }
    }, 1500); // 1.5s debounce
  };

  inputEl.addEventListener('input', onInput);
}

// Placeholder for Step 4 — inline preview UI
function showInlinePreview(results) {
  console.log('[UAI Memory] Inline preview placeholder — will be implemented in Step 4');
  console.log('[UAI Memory] Results to show:', results.map(r => truncate(r.content_preview || '', 60)));
}

// Initialize auto-inject after DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    // Small delay to let platform JS render initial elements
    setTimeout(initAutoInject, 1500);
  });
} else {
  // Already loaded (content scripts run at document_idle)
  setTimeout(initAutoInject, 1500);
}

// ─── Manual Injection (Phase 3) ──────────────────────────────────────

async function handleContextInjection(query, limit) {
  // Step 1: Search for relevant context
  const results = await searchVault(query, limit);

  if (!results || results.length === 0) {
    return { success: false, error: 'No relevant context found' };
  }

  // Step 2: Show preview modal
  const approved = await showPreviewModal(results);

  if (!approved) {
    return { success: false, error: 'User cancelled' };
  }

  // Step 3: Inject into chat input
  const injected = injectIntoInput(formatContext(results));

  return { success: injected, count: results.length || 0 };
}

async function searchVault(query, limit) {
  const response = await fetch(SEARCH_ENDPOINT, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${vaultToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query, limit })
  });

  if (!response.ok) {
    throw new Error(`Search failed: ${response.status}`);
  }

  const data = await response.json();
  return data.results || [];
}

function showPreviewModal(results) {
  return new Promise((resolve) => {
    const modal = document.createElement('div');
    modal.id = 'vault-context-preview';
    modal.innerHTML = `
      <div style="position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                  background: white; border: 2px solid #333; border-radius: 8px;
                  padding: 20px; max-width: 600px; max-height: 70vh; overflow-y: auto;
                  box-shadow: 0 4px 20px rgba(0,0,0,0.3); z-index: 10000;">
        <h3 style="margin: 0 0 15px 0;">Found ${results.length} relevant context${results.length > 1 ? 's' : ''}</h3>
        <div style="margin-bottom: 15px;">
          ${results.map((r, i) => `
            <div style="padding: 10px; margin: 8px 0; background: #f5f5f5; border-radius: 4px;">
              <div style="font-size: 12px; color: #666; margin-bottom: 5px;">
                ${r.platform || 'unknown'} • Relevance: ${((r.similarity_score || 0) * 100).toFixed(0)}%
              </div>
              <div style="font-size: 14px;">${truncate(r.content_preview || '', 200)}</div>
            </div>
          `).join('')}
        </div>
        <div style="display: flex; gap: 10px; justify-content: flex-end;">
          <button id="vault-cancel" style="padding: 8px 16px; border: 1px solid #ccc;
                  background: white; border-radius: 4px; cursor: pointer;">Cancel</button>
          <button id="vault-inject" style="padding: 8px 16px; border: none;
                  background: #0066cc; color: white; border-radius: 4px; cursor: pointer;">Inject Context</button>
        </div>
      </div>
      <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                  background: rgba(0,0,0,0.5); z-index: 9999;"></div>
    `;

    document.body.appendChild(modal);

    document.getElementById('vault-inject').onclick = () => {
      modal.remove();
      resolve(true);
    };

    document.getElementById('vault-cancel').onclick = () => {
      modal.remove();
      resolve(false);
    };
  });
}

function formatContext(results) {
  const context = results.map(r =>
    `[Previous context from ${r.platform || 'chat'}]\n${r.content_preview || ''}`
  ).join('\n\n');

  return `${context}\n\n---\n\n`;
}

function injectIntoInput(text) {
  // Platform-specific injection
  const platform = detectPlatform();
  console.log('[Vault] Platform detected:', platform);

  if (platform === 'claude') {
    const editor = document.querySelector('div[contenteditable="true"]');
    console.log('[Vault] Looking for Claude input element...');
    console.log('[Vault] Element found:', !!editor);
    if (!editor) return false;
    editor.textContent = text + editor.textContent;
    editor.dispatchEvent(new Event('input', { bubbles: true }));
    return true;
  }

  if (platform === 'chatgpt') {
    // ChatGPT uses a ProseMirror contenteditable div, not a textarea
    const editor = document.querySelector('#prompt-textarea');
    console.log('[Vault] Looking for ChatGPT input element...');
    console.log('[Vault] Element found:', !!editor, editor?.tagName, editor?.contentEditable);
    if (!editor) return false;
    // Build ProseMirror-compatible paragraph nodes
    const lines = text.split('\n');
    const html = lines.map(line => `<p>${line || '<br>'}</p>`).join('');
    editor.innerHTML = html + editor.innerHTML;
    editor.dispatchEvent(new InputEvent('input', { bubbles: true }));
    return true;
  }

  if (platform === 'gemini') {
    // Gemini uses Quill editor — target the ql-editor div inside rich-textarea
    const editor = document.querySelector('.ql-editor[aria-label*="prompt"]')
      || document.querySelector('rich-textarea .ql-editor')
      || document.querySelector('div[contenteditable="true"][role="textbox"]');
    console.log('[Vault] Looking for Gemini input element...');
    console.log('[Vault] Element found:', !!editor, editor?.className?.substring(0, 60));
    if (!editor) return false;
    // Build Quill-compatible paragraph nodes
    const lines = text.split('\n');
    const html = lines.map(line => `<p>${line || '<br>'}</p>`).join('');
    editor.innerHTML = html + editor.innerHTML;
    editor.classList.remove('ql-blank');
    editor.dispatchEvent(new InputEvent('input', { bubbles: true }));
    return true;
  }

  console.log('[Vault] Unknown platform, cannot inject');
  return false;
}

function detectPlatform() {
  const hostname = window.location.hostname;
  if (hostname.includes('claude.ai')) return 'claude';
  if (hostname.includes('chatgpt.com')) return 'chatgpt';
  if (hostname.includes('gemini.google.com')) return 'gemini';
  return 'unknown';
}

function truncate(text, length) {
  if (!text) return '';
  return text.length > length ? text.substring(0, length) + '...' : text;
}
