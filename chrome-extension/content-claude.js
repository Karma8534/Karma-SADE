// Universal AI Memory - Claude.ai Content Script
// Captures conversation turns from Claude.ai

console.log('[UAI Memory] Claude content script loaded');

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
  console.log('[UAI Memory] Initializing Claude observer');

  // Wait for chat container to exist
  const checkContainer = setInterval(() => {
    // Look for the scrollable conversation area
    const chatContainer = document.querySelector('.overflow-y-scroll') ||
                          document.querySelector('main') ||
                          document.body;

    if (chatContainer) {
      clearInterval(checkContainer);
      console.log('[UAI Memory] Found chat container:', chatContainer.tagName, chatContainer.className?.substring(0, 60));
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

  // Claude.ai renders messages inside div[data-test-render-count] containers
  // User messages contain a div.bg-bg-300 bubble
  // Assistant messages contain a div[data-is-streaming] with div.font-claude-response
  const renderDivs = document.querySelectorAll('[data-test-render-count]');

  console.log('[UAI Memory] Found', renderDivs.length, 'render containers');

  const messages = [];

  renderDivs.forEach((div) => {
    // Check if this is a user message (has bg-bg-300 bubble)
    const userBubble = div.querySelector('.bg-bg-300');
    if (userBubble) {
      const text = userBubble.textContent.trim();
      if (text.length > 0) {
        messages.push({ type: 'user', text });
        return;
      }
    }

    // Check if this is an assistant message (has data-is-streaming or font-claude-response)
    const assistantBlock = div.querySelector('[data-is-streaming]');
    if (assistantBlock) {
      // Prefer font-claude-response for cleaner text (excludes action buttons)
      const responseEl = assistantBlock.querySelector('.font-claude-response') || assistantBlock;
      const text = responseEl.textContent.trim();
      if (text.length > 0) {
        messages.push({ type: 'assistant', text });
        return;
      }
    }
  });

  console.log('[UAI Memory] Identified', messages.length, 'typed messages');

  // Pair user + assistant messages into turns
  let currentTurn = { user: null, assistant: null };

  messages.forEach(msg => {
    if (msg.type === 'user') {
      if (currentTurn.user && currentTurn.assistant) {
        turns.push({...currentTurn});
      }
      currentTurn = { user: msg.text, assistant: null };
    } else if (msg.type === 'assistant' && currentTurn.user) {
      currentTurn.assistant = msg.text;
    }
  });

  if (currentTurn.user && currentTurn.assistant) {
    turns.push(currentTurn);
  }

  console.log('[UAI Memory] Extracted', turns.length, 'complete turns');

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
      capturedTurns.add(turnHash);
    } else {
      console.error('[UAI Memory] Capture failed:', response.error);
    }
  });
}
