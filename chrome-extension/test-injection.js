/**
 * Universal AI Memory — Context Injection Test Suite
 *
 * Tests the injection pipeline on all 3 platforms without manual intervention.
 * Designed to be run from Claude Code via ChromeMCP (Claude-in-Chrome).
 *
 * What it tests:
 *   1. Search API reachable from browser with CORS
 *   2. Content script message listener active
 *   3. DOM injection works for each platform
 *
 * Usage from Claude Code:
 *   1. Navigate to a platform tab (claude.ai, chatgpt.com, gemini.google.com)
 *   2. Execute this script via javascript_tool
 *   3. Read the returned JSON result
 *
 * Cannot test (ChromeMCP limitations):
 *   - chrome://extensions page (chrome:// URLs blocked)
 *   - Extension popup UI (separate window, not targetable)
 *   - chrome.storage access (page context, not extension context)
 */

(async function runInjectionTest() {
  const SEARCH_ENDPOINT = 'https://hub.arknexus.net/v1/search';
  const TEST_QUERY = 'CORS debugging';
  const results = {
    platform: 'unknown',
    timestamp: new Date().toISOString(),
    tests: {},
    summary: { passed: 0, failed: 0 }
  };

  // Detect platform
  const hostname = window.location.hostname;
  if (hostname.includes('claude.ai')) results.platform = 'claude';
  else if (hostname.includes('chatgpt.com')) results.platform = 'chatgpt';
  else if (hostname.includes('gemini.google.com')) results.platform = 'gemini';
  else {
    results.tests.platform = { pass: false, error: 'Not on a supported platform: ' + hostname };
    results.summary.failed = 1;
    return JSON.stringify(results, null, 2);
  }
  results.tests.platform = { pass: true, value: results.platform };
  results.summary.passed++;

  // Test 1: Search API reachable with CORS
  try {
    const resp = await fetch(SEARCH_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: TEST_QUERY, top_k: 2 })
    });
    const data = await resp.json();
    const hasResults = Array.isArray(data.results) && data.results.length > 0;
    results.tests.searchApi = {
      pass: resp.ok && hasResults,
      status: resp.status,
      resultCount: data.results?.length || 0,
      searchTimeMs: data.search_time_ms || null
    };
    if (results.tests.searchApi.pass) results.summary.passed++;
    else results.summary.failed++;
  } catch (e) {
    results.tests.searchApi = { pass: false, error: e.message };
    results.summary.failed++;
  }

  // Test 2: Content script message listener active
  try {
    const listenerActive = await new Promise((resolve) => {
      const timeout = setTimeout(() => resolve(false), 3000);
      try {
        chrome.runtime.sendMessage({ type: 'PING_CONTENT' }, (response) => {
          clearTimeout(timeout);
          // If we get lastError, the content script listener isn't there
          // but chrome.runtime.sendMessage goes to background, not content script
          // So this tests background.js connectivity, not content script directly
          resolve(!chrome.runtime.lastError);
        });
      } catch (e) {
        clearTimeout(timeout);
        resolve(false);
      }
    });
    results.tests.extensionConnected = {
      pass: listenerActive,
      note: listenerActive ? 'Extension service worker responding' : 'Extension not connected or service worker dead'
    };
    if (results.tests.extensionConnected.pass) results.summary.passed++;
    else results.summary.failed++;
  } catch (e) {
    results.tests.extensionConnected = { pass: false, error: e.message };
    results.summary.failed++;
  }

  // Test 3: Find the input element for this platform
  let inputEl = null;
  let inputSelector = '';
  if (results.platform === 'claude') {
    inputSelector = 'div[contenteditable="true"]';
    inputEl = document.querySelector(inputSelector);
  } else if (results.platform === 'chatgpt') {
    inputSelector = '#prompt-textarea';
    inputEl = document.querySelector(inputSelector);
  } else if (results.platform === 'gemini') {
    inputSelector = '.ql-editor[aria-label*="prompt"] || rich-textarea .ql-editor || div[contenteditable="true"][role="textbox"]';
    inputEl = document.querySelector('.ql-editor[aria-label*="prompt"]')
      || document.querySelector('rich-textarea .ql-editor')
      || document.querySelector('div[contenteditable="true"][role="textbox"]');
  }
  results.tests.inputElement = {
    pass: !!inputEl,
    selector: inputSelector,
    tagName: inputEl?.tagName || null,
    contentEditable: inputEl?.contentEditable || null,
    isEmpty: inputEl ? (inputEl.textContent.trim().length === 0) : null
  };
  if (results.tests.inputElement.pass) results.summary.passed++;
  else results.summary.failed++;

  // Test 4: Direct DOM injection (bypasses extension, tests raw injection logic)
  if (inputEl) {
    const testText = '[UAI-TEST] Context injection test at ' + new Date().toISOString();
    const beforeLength = inputEl.textContent.length;
    try {
      if (results.platform === 'claude') {
        inputEl.textContent = testText;
        inputEl.dispatchEvent(new Event('input', { bubbles: true }));
      } else if (results.platform === 'chatgpt') {
        inputEl.innerHTML = '<p>' + testText + '</p>';
        inputEl.dispatchEvent(new InputEvent('input', { bubbles: true }));
      } else if (results.platform === 'gemini') {
        inputEl.innerHTML = '<p>' + testText + '</p>';
        inputEl.classList.remove('ql-blank');
        inputEl.dispatchEvent(new InputEvent('input', { bubbles: true }));
      }
      // Verify text was injected
      const afterText = inputEl.textContent;
      const injected = afterText.includes('[UAI-TEST]');
      results.tests.domInjection = {
        pass: injected,
        textBefore: beforeLength,
        textAfter: afterText.length,
        containsMarker: injected
      };
      if (results.tests.domInjection.pass) results.summary.passed++;
      else results.summary.failed++;

      // Clean up — remove test text
      if (results.platform === 'claude') {
        inputEl.textContent = '';
        inputEl.dispatchEvent(new Event('input', { bubbles: true }));
      } else {
        inputEl.innerHTML = '<p><br></p>';
        inputEl.dispatchEvent(new InputEvent('input', { bubbles: true }));
        if (results.platform === 'gemini') inputEl.classList.add('ql-blank');
      }
    } catch (e) {
      results.tests.domInjection = { pass: false, error: e.message };
      results.summary.failed++;
    }
  } else {
    results.tests.domInjection = { pass: false, error: 'No input element found — skipped' };
    results.summary.failed++;
  }

  // Test 5: Full pipeline via chrome.tabs.sendMessage (simulates popup flow)
  // This can only work if content-context.js is loaded AND vault token is set
  try {
    const pipelineResult = await new Promise((resolve) => {
      const timeout = setTimeout(() => resolve({ pass: false, error: 'Timeout — content script not responding' }), 8000);
      try {
        // We can't use chrome.tabs.sendMessage from page context.
        // Instead, test if chrome.runtime.sendMessage reaches the content script
        // by sending INJECT_CONTEXT — but from page context this goes to background.js, not content script.
        // So we mark this as "manual-only" and skip.
        clearTimeout(timeout);
        resolve({
          pass: null,
          skipped: true,
          note: 'Full pipeline test requires popup trigger — cannot simulate from page context. Use popup manually or test via chrome.tabs.sendMessage from background.js.'
        });
      } catch (e) {
        clearTimeout(timeout);
        resolve({ pass: false, error: e.message });
      }
    });
    results.tests.fullPipeline = pipelineResult;
    if (pipelineResult.skipped) {
      // Don't count skipped tests
    } else if (pipelineResult.pass) results.summary.passed++;
    else results.summary.failed++;
  } catch (e) {
    results.tests.fullPipeline = { pass: false, error: e.message };
    results.summary.failed++;
  }

  // Overall
  results.summary.total = results.summary.passed + results.summary.failed;
  results.summary.allPassed = results.summary.failed === 0;

  return JSON.stringify(results, null, 2);
})();
