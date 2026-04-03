// Karma Nexus Popup Logic

document.addEventListener('DOMContentLoaded', async () => {
  const hubDot = document.getElementById('hub-dot');
  const hubStatus = document.getElementById('hub-status');
  const queryInput = document.getElementById('query');
  const sendBtn = document.getElementById('send');
  const captureBtn = document.getElementById('capture');
  const openHubBtn = document.getElementById('open-hub');
  const resultDiv = document.getElementById('result');
  const tokenInput = document.getElementById('token');
  const saveTokenBtn = document.getElementById('save-token');

  // Check hub status
  chrome.runtime.sendMessage({ type: 'GET_STATUS' }, (res) => {
    if (res && res.ok) {
      hubDot.classList.add('ok');
      hubStatus.textContent = 'hub online';
    } else {
      hubDot.classList.add('err');
      hubStatus.textContent = res?.error || 'hub offline';
    }
  });

  // Load existing token
  const stored = await chrome.storage.local.get('karma-token');
  if (stored['karma-token']) {
    tokenInput.value = '********';
    document.getElementById('token-section').style.opacity = '0.5';
  }

  // Save token
  saveTokenBtn.addEventListener('click', () => {
    const token = tokenInput.value.trim();
    if (token && token !== '********') {
      chrome.storage.local.set({ 'karma-token': token });
      tokenInput.value = '********';
      document.getElementById('token-section').style.opacity = '0.5';
    }
  });

  // Ask Karma
  sendBtn.addEventListener('click', () => {
    const query = queryInput.value.trim();
    if (!query) return;
    resultDiv.style.display = 'block';
    resultDiv.textContent = 'Thinking...';
    chrome.runtime.sendMessage({ type: 'QUERY_KARMA', query }, (res) => {
      if (res && res.ok !== false) {
        resultDiv.textContent = res.assistant_text || res.response || JSON.stringify(res);
      } else {
        resultDiv.textContent = 'Error: ' + (res?.error || 'unknown');
      }
    });
    queryInput.value = '';
  });

  queryInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendBtn.click();
  });

  // Capture page context
  captureBtn.addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    chrome.tabs.sendMessage(tab.id, { type: 'GET_PAGE_CONTEXT' }, (ctx) => {
      if (!ctx) {
        resultDiv.style.display = 'block';
        resultDiv.textContent = 'Could not capture page context';
        return;
      }
      const content = `[Browser Capture] ${ctx.title}\nURL: ${ctx.url}\n${ctx.selection || ctx.text.slice(0, 500)}`;
      chrome.runtime.sendMessage({
        type: 'CAPTURE_CONTEXT',
        data: { content, tags: ['page-capture'] },
      }, (res) => {
        resultDiv.style.display = 'block';
        resultDiv.textContent = res?.ok ? 'Captured to Karma memory' : 'Capture failed: ' + (res?.error || 'unknown');
      });
    });
  });

  // Open hub
  openHubBtn.addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://hub.arknexus.net' });
  });
});
