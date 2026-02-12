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
    // Try multiple selectors
    const chatContainer = document.querySelector('[data-testid="conversation"]') ||
                          document.querySelector('main[class*="flex"]') ||
                          document.querySelector('main') ||
                          document.body;

    if (chatContainer) {
      clearInterval(checkContainer);
      console.log('[UAI Memory] Found chat container:', chatContainer.tagName, chatContainer.className);
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

  // Simpler approach: Find all divs and analyze their position/content
  const allDivs = Array.from(document.querySelectorAll('div'));

  console.log('[UAI Memory] Scanning', allDivs.length, 'divs for messages');

  // Filter to likely message containers
  const messageCandidates = allDivs.filter(div => {
    const text = div.innerText?.trim() || '';
    const textLen = text.length;

    // Must have substantial text
    if (textLen < 10 || textLen > 50000) return false;

    // Ignore if it has message children (parent container)
    const childDivs = div.querySelectorAll('div');
    if (childDivs.length > 20) return false;

    return true;
  });

  console.log('[UAI Memory] Found', messageCandidates.length, 'message candidates');

  // Look for alternating pattern based on position
  // Claude typically renders messages in order: user, assistant, user, assistant...
  const messages = [];

  messageCandidates.forEach((div, idx) => {
    const text = div.innerText.trim();
    const classes = div.className || '';
    const computedStyle = window.getComputedStyle(div);

    // Simple heuristic: alternate between user/assistant based on order
    // Or detect by class name patterns
    let type = null;

    if (classes.match(/font-user|user.*message/i)) {
      type = 'user';
    } else if (classes.match(/font-claude|font-assistant|assistant.*message|claude.*message/i)) {
      type = 'assistant';
    }

    if (type) {
      messages.push({ type, text, idx });
      console.log(`[UAI Memory] Message ${messages.length}: ${type} (${text.substring(0, 50)}...)`);
    }
  });

  console.log('[UAI Memory] Identified', messages.length, 'typed messages');

  // Pair them up
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
