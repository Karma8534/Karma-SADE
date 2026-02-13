// Universal AI Memory - ChatGPT Content Script
// Captures conversation turns from chatgpt.com

console.log('[UAI Memory] ChatGPT content script loaded');

let lastProcessedMessageCount = 0;
let observerActive = false;
let capturedTurns = new Set();

function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash;
}

// Start observing after page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

function init() {
  console.log('[UAI Memory] Initializing ChatGPT observer');

  // Wait for chat container to exist
  const checkContainer = setInterval(() => {
    const chatContainer = document.querySelector('[role="presentation"]') ||
                          document.querySelector('main') ||
                          document.querySelector('.flex.flex-col');

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

  // ChatGPT uses data-message-author-role attribute
  const messageElements = document.querySelectorAll('[data-message-author-role]');

  let currentTurn = { user: null, assistant: null };

  messageElements.forEach((elem) => {
    const role = elem.getAttribute('data-message-author-role');
    // Use textContent instead of innerText — assistant messages may be
    // lazy-rendered with display:none, causing innerText to return empty
    const text = elem.textContent.trim();
    if (!text) return;

    if (role === 'user') {
      // If we have a previous turn, save it
      if (currentTurn.user && currentTurn.assistant) {
        turns.push({...currentTurn});
      }
      // Start new turn
      currentTurn = { user: text, assistant: null };
    } else if (role === 'assistant' && currentTurn.user) {
      currentTurn.assistant = text;
    }
  });

  // Add last turn if complete
  if (currentTurn.user && currentTurn.assistant) {
    turns.push(currentTurn);
  }

  return turns;
}

function captureConversationTurn(turn) {
  // Deduplicate using hash of user message
  const turnHash = hashString(turn.user.substring(0, 100));
  if (capturedTurns.has(turnHash)) {
    console.log('[UAI Memory] Skipping duplicate turn (already captured)');
    return;
  }

  // Extract thread ID from URL
  const urlMatch = window.location.pathname.match(/\/c\/([a-f0-9-]+)/);
  const threadId = urlMatch ? urlMatch[1] : null;

  const data = {
    provider: 'openai',
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
      capturedTurns.add(turnHash);
    } else {
      console.error('[UAI Memory] Capture failed:', response.error);
    }
  });
}
