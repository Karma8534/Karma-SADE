// Universal AI Memory - Gemini Content Script
// Captures conversation turns from gemini.google.com

console.log('[UAI Memory] Gemini content script loaded');

let lastProcessedMessageCount = 0;
let observerActive = false;
let capturedTurns = new Set(); // Track captured turn hashes to prevent duplicates

// Simple hash function for deduplication
function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32bit integer
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
        console.log('[UAI Memory] Processing turn', i + 1, '- has user:', !!turn.user, 'has assistant:', !!turn.assistant);
        if (turn.user && turn.assistant) {
          console.log('[UAI Memory] Capturing turn', i + 1);
          captureConversationTurn(turn);
        } else {
          console.log('[UAI Memory] Skipping incomplete turn', i + 1);
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

  // Gemini uses custom web components:
  // <user-query> for user messages, with clean text in p.query-text-line
  // <model-response> for assistant messages, with clean text in <message-content>
  const userQueries = document.querySelectorAll('user-query');
  const modelResponses = document.querySelectorAll('model-response');

  console.log('[UAI Memory] Found', userQueries.length, 'user queries and', modelResponses.length, 'model responses');

  // Build ordered message list by walking the DOM in order
  // user-query and model-response alternate as siblings inside the conversation
  const allMessages = [];

  // Collect user messages with their text
  userQueries.forEach((uq) => {
    // Prefer p.query-text-line for clean text (excludes "You said" prefix and file attachments)
    const queryLines = uq.querySelectorAll('p.query-text-line');
    let text = '';
    if (queryLines.length > 0) {
      text = Array.from(queryLines).map(p => p.textContent.trim()).join('\n');
    } else {
      // Fallback: use user-query-content
      const uqc = uq.querySelector('user-query-content');
      text = uqc ? uqc.textContent.trim() : uq.textContent.trim();
      // Strip common prefixes
      text = text.replace(/^\s*You said\s*/i, '');
    }
    if (text.length > 0) {
      allMessages.push({ type: 'user', text, el: uq });
    }
  });

  // Collect assistant messages with their text
  modelResponses.forEach((mr) => {
    // Prefer message-content for clean text (excludes "Gemini said", "Show thinking", action buttons)
    const messageContent = mr.querySelector('message-content');
    let text = '';
    if (messageContent) {
      text = messageContent.textContent.trim();
    } else {
      // Fallback: use .markdown class
      const markdown = mr.querySelector('.markdown');
      text = markdown ? markdown.textContent.trim() : mr.textContent.trim();
      // Strip common prefixes
      text = text.replace(/^\s*(Show thinking\s*)?(Gemini said\s*)?/i, '');
    }
    if (text.length > 0) {
      allMessages.push({ type: 'assistant', text, el: mr });
    }
  });

  // Sort by DOM order using compareDocumentPosition
  allMessages.sort((a, b) => {
    const pos = a.el.compareDocumentPosition(b.el);
    if (pos & Node.DOCUMENT_POSITION_FOLLOWING) return -1;
    if (pos & Node.DOCUMENT_POSITION_PRECEDING) return 1;
    return 0;
  });

  console.log('[UAI Memory] Identified', allMessages.length, 'typed messages (sorted)');

  // Pair user + assistant messages into turns
  let currentTurn = { user: null, assistant: null };

  allMessages.forEach(msg => {
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
  // Create a hash of user message to detect duplicates
  const turnHash = hashString(turn.user.substring(0, 100));

  if (capturedTurns.has(turnHash)) {
    console.log('[UAI Memory] Skipping duplicate turn (already captured)');
    return;
  }

  // Extract thread ID from URL (Gemini format: /app/[hex])
  const urlMatch = window.location.pathname.match(/\/app\/([a-f0-9]+)/);
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
      // Mark this turn as captured to prevent duplicates
      capturedTurns.add(turnHash);
    } else {
      console.error('[UAI Memory] Capture failed:', response.error);
    }
  });
}
