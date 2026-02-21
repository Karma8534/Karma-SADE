// Universal AI Memory - Popup UI Controller
// E2E Debug Pack: one-click proof of DOM→Queue→POST→Receipt→Stats

document.addEventListener('DOMContentLoaded', () => {
  loadConfig();
  loadStats();
  loadDebugDisplay();
  setupDebugButtons();
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

// Load and display debug information
function loadDebugDisplay() {
  chrome.storage.local.get(['debugLog_v1', 'lastReceipt'], (result) => {
    const log = result.debugLog_v1 || [];
    const lastReceipt = result.lastReceipt || null;

    // Update receipt summary if present
    if (lastReceipt) {
      document.getElementById('receiptSummary').style.display = 'block';
      document.getElementById('receiptId').textContent = lastReceipt.receipt_id || '—';
      document.getElementById('receiptAccepted').textContent = lastReceipt.accepted || 0;
      document.getElementById('receiptRejected').textContent = lastReceipt.rejected || 0;
    }

    // Display last 20 events
    const recentEvents = log.slice(-20);
    const debugLogEl = document.getElementById('debugLog');
    if (recentEvents.length === 0) {
      debugLogEl.innerHTML = '<div style="color: #999;">No events yet...</div>';
    } else {
      const lines = recentEvents.map(event => {
        const ts = event.ts ? new Date(event.ts).toLocaleTimeString() : '?';
        const traceStr = event.trace_id ? ` [${event.trace_id}]` : '';
        return `[${ts}] ${event.kind}${traceStr}: ${JSON.stringify(event.data)}`;
      });
      debugLogEl.textContent = lines.join('\n');
    }
  });
}

// Setup debug buttons
function setupDebugButtons() {
  const copyBtn = document.getElementById('copyDebugPackBtn');
  const clearBtn = document.getElementById('clearDebugBtn');

  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      const debugPack = await buildDebugPack();
      const packJson = JSON.stringify(debugPack, null, 2);

      // Copy to clipboard
      try {
        await navigator.clipboard.writeText(packJson);
        showStatus('Debug Pack copied to clipboard. Paste into ChatGPT.', 'success');
      } catch (err) {
        showStatus('Failed to copy: ' + err.message, 'error');
      }
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener('click', () => {
      chrome.storage.local.set({ debugLog_v1: [], lastReceipt: null, lastPost: null }, () => {
        document.getElementById('debugLog').innerHTML = '<div style="color: #999;">No events yet...</div>';
        document.getElementById('receiptSummary').style.display = 'none';
        showStatus('Debug log cleared', 'success');
      });
    });
  }
}

// Build a complete Debug Pack for easy diagnosis
async function buildDebugPack() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(['captureToken', 'vaultToken', 'enabled'], (config) => {
      chrome.storage.local.get(['stats', 'debugLog_v1', 'lastPost', 'lastReceipt', 'captureQueue_v1', 'captureQueueMeta_v1'], (local) => {
        const stats = local.stats || { captured: 0, failed: 0 };
        const queue = local.captureQueue_v1 || [];
        const meta = local.captureQueueMeta_v1 || { oldestTs: null, backoffMs: 0, nextAttemptAt: 0 };
        const debugLog = local.debugLog_v1 || [];
        const lastPost = local.lastPost || null;
        const lastReceipt = local.lastReceipt || null;

        const pack = {
          ts: new Date().toISOString(),
          extension: {
            name: 'Universal AI Memory',
            version: '2.0.0',
            manifest_version: 3
          },
          config: {
            enabled: config.enabled || false,
            captureTokenLen: (config.captureToken || '').length,
            vaultTokenLen: (config.vaultToken || '').length
          },
          queue: {
            size: queue.length,
            meta: meta
          },
          stats: stats,
          last_post: lastPost,
          last_receipt: lastReceipt,
          debugLog: debugLog
        };

        resolve(pack);
      });
    });
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

  setTimeout(() => {
    statusEl.className = 'status';
  }, 4000);
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

// Auto-refresh debug display every 2 seconds
setInterval(() => {
  loadDebugDisplay();
  loadStats();
}, 2000);
