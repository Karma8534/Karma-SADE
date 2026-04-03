// Karma Nexus Chrome Extension — Background Service Worker
// Connects browser to hub.arknexus.net for context capture and memory

const HUB_URL = 'https://hub.arknexus.net';

// Open side panel on extension icon click
chrome.action.onClicked.addListener((tab) => {
  chrome.sidePanel.open({ tabId: tab.id });
});

// Listen for messages from content script and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CAPTURE_CONTEXT') {
    captureToHub(message.data).then(sendResponse);
    return true; // async response
  }
  if (message.type === 'QUERY_KARMA') {
    queryKarma(message.query).then(sendResponse);
    return true;
  }
  if (message.type === 'GET_STATUS') {
    getHubStatus().then(sendResponse);
    return true;
  }
});

async function getToken() {
  const result = await chrome.storage.local.get('karma-token');
  return result['karma-token'] || '';
}

async function captureToHub(data) {
  const token = await getToken();
  if (!token) return { ok: false, error: 'No token configured' };
  try {
    const res = await fetch(`${HUB_URL}/v1/ambient`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        type: 'log',
        content: data.content,
        tags: ['chrome-capture', 'browser', ...(data.tags || [])],
        source: 'karma-nexus-extension',
      }),
    });
    return await res.json();
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

async function queryKarma(query) {
  const token = await getToken();
  if (!token) return { ok: false, error: 'No token configured' };
  try {
    const res = await fetch(`${HUB_URL}/v1/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message: query, stream: false }),
    });
    return await res.json();
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

async function getHubStatus() {
  const token = await getToken();
  if (!token) return { ok: false, error: 'No token configured' };
  try {
    const res = await fetch(`${HUB_URL}/health`);
    return await res.json();
  } catch (e) {
    return { ok: false, error: e.message };
  }
}
