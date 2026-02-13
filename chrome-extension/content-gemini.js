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

  // Gemini DOM structure scan - try multiple approaches
  console.log('[UAI Memory] Starting message extraction...');

  // Get all potential message containers
  const allDivs = Array.from(document.querySelectorAll('div')).filter(div => {
    const text = div.innerText?.trim() || '';
    const textLen = text.length;

    // Must have text content
    if (textLen < 10) return false;

    // Check if it's a leaf message container (not too many children)
    const directChildren = Array.from(div.children);
    const divChildren = directChildren.filter(c => c.tagName === 'DIV');

    // Should have some structure but not be a massive container
    return textLen > 10 && textLen < 50000 && divChildren.length < 15;
  });

  console.log('[UAI Memory] Scanning', allDivs.length, 'divs for messages');

  // Identify messages by attributes and structure
  const messages = [];

  allDivs.forEach((div, idx) => {
    const text = div.innerText.trim();
    const dataset = div.dataset || {};
    const classes = div.className || '';
    const attributes = {};

    // Collect all data-* attributes
    for (let attr of div.attributes) {
      if (attr.name.startsWith('data-')) {
        attributes[attr.name] = attr.value;
      }
    }

    let type = null;

    // Check for Gemini-specific markers
    // Gemini uses different structures - try to detect patterns
    if (classes.includes('user') || dataset.role === 'user' || attributes['data-message-author'] === 'user') {
      type = 'user';
    } else if (classes.includes('model') || classes.includes('assistant') || dataset.role === 'model' || attributes['data-message-author'] === 'model') {
      type = 'assistant';
    }

    // Fallback: Check parent elements for indicators
    if (!type && text.length > 20) {
      let parent = div.parentElement;
      for (let i = 0; i < 3 && parent; i++) {
        const parentClasses = parent.className || '';
        const parentDataset = parent.dataset || {};

        if (parentClasses.includes('user') || parentDataset.role === 'user') {
          type = 'user';
          break;
        } else if (parentClasses.includes('model') || parentClasses.includes('assistant') || parentDataset.role === 'model') {
          type = 'assistant';
          break;
        }

        parent = parent.parentElement;
      }
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
  // Create a hash of user message to detect duplicates
  const turnHash = hashString(turn.user.substring(0, 100));

  if (capturedTurns.has(turnHash)) {
    console.log('[UAI Memory] Skipping duplicate turn (already captured)');
    return;
  }

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
      // Mark this turn as captured to prevent duplicates
      capturedTurns.add(turnHash);
    } else {
      console.error('[UAI Memory] Capture failed:', response.error);
    }
  });
}
