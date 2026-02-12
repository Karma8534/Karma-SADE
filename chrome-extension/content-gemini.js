// Universal AI Memory - Gemini Content Script
// Captures conversation turns from gemini.google.com

console.log('[UAI Memory] Gemini content script loaded');

let lastProcessedMessageCount = 0;
let observerActive = false;

// Start observing after page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

function init() {
  console.log('[UAI Memory] Initializing Gemini observer');

  // Wait for chat container to exist
  const checkContainer = setInterval(() => {
    const chatContainer = document.querySelector('chat-window') ||
                          document.querySelector('[class*="conversation"]') ||
                          document.querySelector('main');

    if (chatContainer) {
      clearInterval(checkContainer);
      console.log('[UAI Memory] Found chat container, starting observer');
      startObserver(chatContainer);
      // Also do initial scan
      scanForNewMessages();
    }
  }, 1000);

  // Timeout after 30 seconds
  setTimeout(() => clearInterval(checkContainer), 30000);
}

function startObserver(container) {
  if (observerActive) return;
  observerActive = true;

  const observer = new MutationObserver((mutations) => {
    // Debounce: only check after mutations stop for 500ms
    clearTimeout(observer.debounceTimer);
    observer.debounceTimer = setTimeout(() => {
      scanForNewMessages();
    }, 500);
  });

  observer.observe(container, {
    childList: true,
    subtree: true
  });

  console.log('[UAI Memory] MutationObserver active');
}

function scanForNewMessages() {
  try {
    // Find all message pairs
    const messages = extractMessages();

    if (messages.length > lastProcessedMessageCount) {
      console.log('[UAI Memory] New messages detected:', messages.length - lastProcessedMessageCount);

      // Process new messages
      for (let i = lastProcessedMessageCount; i < messages.length; i++) {
        const turn = messages[i];
        if (turn.user && turn.assistant) {
          captureConversationTurn(turn);
        }
      }

      lastProcessedMessageCount = messages.length;
    }
  } catch (error) {
    console.error('[UAI Memory] Error scanning messages:', error);
  }
}

function extractMessages() {
  const turns = [];

  // Gemini uses message-content with data-test-id or similar
  // Try multiple selectors
  const userMessages = document.querySelectorAll('[data-test-id*="user"], .user-message, [class*="user-query"]');
  const assistantMessages = document.querySelectorAll('[data-test-id*="model"], .model-response, [class*="model-response"]');

  // Match them pairwise
  const maxPairs = Math.min(userMessages.length, assistantMessages.length);

  for (let i = 0; i < maxPairs; i++) {
    const userText = userMessages[i].innerText.trim();
    const assistantText = assistantMessages[i].innerText.trim();

    if (userText && assistantText) {
      turns.push({
        user: userText,
        assistant: assistantText
      });
    }
  }

  return turns;
}

function captureConversationTurn(turn) {
  // Extract thread ID from URL (Gemini format varies)
  const urlMatch = window.location.pathname.match(/\/app\/([a-f0-9-]+)/) ||
                   window.location.search.match(/[?&]thread=([a-f0-9-]+)/);
  const threadId = urlMatch ? urlMatch[1] : null;

  const data = {
    provider: 'gemini',
    url: window.location.href,
    timestamp: new Date().toISOString(),
    user_message: turn.user,
    assistant_message: turn.assistant,
    thread_id: threadId,
    metadata: {
      page_title: document.title,
      captured_at: new Date().toISOString()
    }
  };

  console.log('[UAI Memory] Capturing turn:', {
    thread_id: threadId,
    user_length: turn.user.length,
    assistant_length: turn.assistant.length
  });

  // Send to background script
  chrome.runtime.sendMessage({
    type: 'CAPTURE_CONVERSATION',
    data: data
  }, (response) => {
    if (chrome.runtime.lastError) {
      console.error('[UAI Memory] Message error:', chrome.runtime.lastError);
      return;
    }

    if (response.success) {
      console.log('[UAI Memory] Turn captured successfully');
    } else {
      console.error('[UAI Memory] Capture failed:', response.error);
    }
  });
}
