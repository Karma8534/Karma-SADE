// Universal AI Memory - Background Service Worker
// Handles message passing and API communication

const HUB_API_URL = 'https://hub.arknexus.net/v1/chatlog';

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CAPTURE_CONVERSATION') {
    handleConversationCapture(message.data)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
  }

  if (message.type === 'GET_CONFIG') {
    chrome.storage.sync.get(['vaultToken', 'enabled'], (config) => {
      sendResponse(config);
    });
    return true;
  }
});

// Handle conversation capture and send to Hub
async function handleConversationCapture(data) {
  // Get vault token from storage
  const config = await chrome.storage.sync.get(['vaultToken', 'enabled']);

  if (!config.enabled) {
    console.log('[UAI Memory] Capture disabled, skipping');
    return { skipped: true, reason: 'disabled' };
  }

  if (!config.vaultToken) {
    console.error('[UAI Memory] No vault token configured');
    return { error: 'No vault token configured' };
  }

  // Prepare payload
  const payload = {
    provider: data.provider,
    url: data.url,
    timestamp: data.timestamp || new Date().toISOString(),
    user_message: data.user_message,
    assistant_message: data.assistant_message,
    thread_id: data.thread_id || null,
    metadata: data.metadata || {}
  };

  console.log('[UAI Memory] Sending capture:', {
    provider: payload.provider,
    url: payload.url,
    user_length: payload.user_message.length,
    assistant_length: payload.assistant_message.length
  });

  // Send to Hub
  try {
    const response = await fetch(HUB_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${config.vaultToken}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Hub API error (${response.status}): ${errorText}`);
    }

    const result = await response.json();
    console.log('[UAI Memory] Capture successful:', result);

    // Update stats
    await updateStats('captured');

    return result;
  } catch (error) {
    console.error('[UAI Memory] Capture failed:', error);
    await updateStats('failed');
    throw error;
  }
}

// Update capture statistics
async function updateStats(type) {
  const stats = await chrome.storage.local.get(['stats']) || { stats: { captured: 0, failed: 0 } };
  const currentStats = stats.stats || { captured: 0, failed: 0 };
  currentStats[type] = (currentStats[type] || 0) + 1;
  await chrome.storage.local.set({ stats: currentStats });
}

// Installation handler
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('[UAI Memory] Extension installed');
    // Set default config
    chrome.storage.sync.set({
      enabled: false, // Disabled by default until token is configured
      vaultToken: ''
    });

    // Initialize stats
    chrome.storage.local.set({
      stats: { captured: 0, failed: 0 }
    });

    // Open setup page
    chrome.tabs.create({ url: 'popup.html' });
  }
});
