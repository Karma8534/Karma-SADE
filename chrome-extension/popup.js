// Universal AI Memory - Popup UI Controller

// Load current configuration
document.addEventListener('DOMContentLoaded', () => {
  loadConfig();
  loadStats();
});

// Load configuration from storage
function loadConfig() {
  chrome.storage.sync.get(['vaultToken', 'enabled'], (config) => {
    document.getElementById('vaultToken').value = config.vaultToken || '';
    document.getElementById('enableToggle').checked = config.enabled || false;
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
  const vaultToken = document.getElementById('vaultToken').value.trim();
  const enabled = document.getElementById('enableToggle').checked;

  if (!vaultToken) {
    showStatus('Please enter a vault token', 'error');
    return;
  }

  // Save to storage
  chrome.storage.sync.set({
    vaultToken: vaultToken,
    enabled: enabled
  }, () => {
    if (chrome.runtime.lastError) {
      showStatus('Failed to save: ' + chrome.runtime.lastError.message, 'error');
    } else {
      showStatus('Configuration saved successfully!', 'success');

      // Reload stats in case toggle changed
      setTimeout(() => {
        loadStats();
      }, 100);
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
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

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
