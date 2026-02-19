// Universal AI Memory - Popup UI Controller

// Load current configuration
document.addEventListener('DOMContentLoaded', () => {
  loadConfig();
  loadStats();
});

// Load configuration from storage
function loadConfig() {
  chrome.storage.sync.get(['captureToken', 'vaultToken', 'enabled', 'autoInjectEnabled'], (config) => {
    document.getElementById('captureToken').value = config.captureToken || '';
    document.getElementById('vaultToken').value = config.vaultToken || '';
    document.getElementById('enableToggle').checked = config.enabled || false;
    document.getElementById('autoInjectToggle').checked = config.autoInjectEnabled || false;
  });
}

// Load statistics from storage
function loadStats() {
  chrome.storage.local.get(['stats'], (result) => {
    const stats = result.stats || { captured: 0, failed: 0 };
    document.getElementById('capturedCount').textContent = stats.captured || 0;
    document.getElementById('failedCount').textContent = stats.failed || 0;
  });
}

// Save configuration
document.getElementById('saveBtn').addEventListener('click', () => {
  const captureToken = document.getElementById('captureToken').value.trim();
  const vaultToken = document.getElementById('vaultToken').value.trim();
  const enabled = document.getElementById('enableToggle').checked;

  if (!captureToken && !vaultToken) {
    showStatus('Enter a Capture Token (or legacy Vault Token)', 'error');
    return;
  }

  // Save to storage — captureToken is primary, vaultToken is legacy fallback
  chrome.storage.sync.set({
    captureToken: captureToken,
    vaultToken: vaultToken,
    enabled: enabled
  }, () => {
    if (chrome.runtime.lastError) {
      showStatus('Failed to save: ' + chrome.runtime.lastError.message, 'error');
    } else {
      console.log('[UAI Memory] popup saved', {
        captureTokenLen: captureToken.length,
        vaultTokenLen: vaultToken.length,
        enabled
      });
      showStatus('Configuration saved!', 'success');
      setTimeout(() => { loadStats(); }, 100);
    }
  });
});

// Toggle enable/disable
document.getElementById('enableToggle').addEventListener('change', (e) => {
  const enabled = e.target.checked;

  chrome.storage.sync.set({ enabled: enabled }, () => {
    if (enabled) {
      showStatus('Memory capture enabled', 'success');
    } else {
      showStatus('Memory capture disabled', 'error');
    }
  });
});

// Show status message
function showStatus(message, type) {
  const statusEl = document.getElementById('status');
  statusEl.textContent = message;
  statusEl.className = 'status ' + type;

  // Auto-hide after 3 seconds
  setTimeout(() => {
    statusEl.className = 'status';
  }, 3000);
}

// Auto-inject toggle
document.getElementById('autoInjectToggle').addEventListener('change', (e) => {
  const autoInjectEnabled = e.target.checked;

  chrome.storage.sync.set({ autoInjectEnabled }, () => {
    if (autoInjectEnabled) {
      showStatus('Auto-inject enabled (Beta)', 'success');
    } else {
      showStatus('Auto-inject disabled', 'error');
    }
  });
});

// Context injection button handler
const injectBtn = document.getElementById('inject-context-btn');
const queryInput = document.getElementById('context-query');

if (injectBtn && queryInput) {
  injectBtn.addEventListener('click', async () => {
    const query = queryInput.value.trim();

    if (!query) {
      showStatus('Enter a search query first', 'error');
      return;
    }

    injectBtn.disabled = true;
    injectBtn.textContent = 'Searching...';

    // Send message to active tab's content script
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tabs || tabs.length === 0) {
      injectBtn.disabled = false;
      injectBtn.textContent = 'Inject Context';
      showStatus('No active tab found', 'error');
      return;
    }
    const tab = tabs[0];

    chrome.tabs.sendMessage(tab.id, {
      type: 'INJECT_CONTEXT',
      query: query,
      limit: 3
    }, (response) => {
      injectBtn.disabled = false;
      injectBtn.textContent = 'Inject Context';

      if (chrome.runtime.lastError) {
        showStatus('Failed: ' + chrome.runtime.lastError.message, 'error');
        return;
      }

      if (response && response.success) {
        showStatus(`Injected ${response.count} contexts`, 'success');
        queryInput.value = '';
      } else {
        showStatus(response?.error || 'Injection failed', 'error');
      }
    });
  });
}
