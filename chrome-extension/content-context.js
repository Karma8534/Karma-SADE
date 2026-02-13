// Universal AI Memory - Context Injection
// Listens for injection requests from popup, fetches relevant context, displays preview
const SEARCH_ENDPOINT = 'https://hub.arknexus.net/v1/search';
let vaultToken = null;

// Get token from storage
chrome.storage.sync.get(['vaultToken'], (result) => {
  vaultToken = result.vaultToken;
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
    const input = document.querySelector('rich-textarea[aria-label*="prompt"]');
    console.log('[Vault] Looking for Gemini input element...');
    console.log('[Vault] Element found:', !!input);
    if (!input) return false;
    input.textContent = text + input.textContent;
    input.dispatchEvent(new Event('input', { bubbles: true }));
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
