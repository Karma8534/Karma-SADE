// Universal AI Memory - Claude.ai Content Script
// Captures conversation turns from Claude.ai

console.log('[UAI Memory] Claude content script loaded');

let lastProcessedMessageCount = 0;
let observerActive = false;

// Start observing after page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

function init() {
  console.log('[UAI Memory] Initializing Claude observer');

  // Wait for chat container to exist
  const checkContainer = setInterval(() => {
    const chatContainer = document.querySelector('[data-testid="conversation"]') ||
                          document.querySelector('.font-user-message') ||
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

  // Claude uses font-user-message and font-claude-message classes
  // Or data-testid attributes
  const messageElements = document.querySelectorAll('.font-user-message, .font-claude-message, [class*="Message"]');

  let currentTurn = { user: null, assistant: null };

  messageElements.forEach((elem) => {
    const text = elem.innerText.trim();
    if (!text) return;

    const isUser = elem.classList.contains('font-user-message') ||
                   elem.querySelector('[data-testid="user-message"]') ||
                   elem.classList.contains('user-message');

    const isAssistant = elem.classList.contains('font-claude-message') ||
                        elem.querySelector('[data-testid="assistant-message"]') ||
                        elem.classList.contains('assistant-message');

    if (isUser) {
      // If we have a previous turn, save it
      if (currentTurn.user && currentTurn.assistant) {
        turns.push({...currentTurn});
      }
      // Start new turn
      currentTurn = { user: text, assistant: null };
    } else if (isAssistant && currentTurn.user) {
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
  // Extract thread ID from URL
  const urlMatch = window.location.pathname.match(/\/chat\/([a-f0-9-]+)/);
  const threadId = urlMatch ? urlMatch[1] : null;

  const data = {
    provider: 'claude',
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
