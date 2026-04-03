// Karma Nexus Content Script — runs on every page
// Captures page context and provides Karma integration

// Right-click selected text → send to Karma
document.addEventListener('mouseup', () => {
  const selection = window.getSelection().toString().trim();
  if (selection.length > 20 && selection.length < 5000) {
    // Store selection for popup/sidepanel to access
    chrome.storage.local.set({ 'karma-selection': selection });
  }
});

// Listen for messages from popup/sidepanel
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_PAGE_CONTEXT') {
    sendResponse({
      url: window.location.href,
      title: document.title,
      selection: window.getSelection().toString().trim(),
      text: document.body.innerText.slice(0, 2000),
    });
    return true;
  }
});
