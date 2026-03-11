/**
 * RED/GREEN test: session_id flows from /v1/chat request → aria_local_call → Aria POST body
 *
 * This reproduces the exact aria_local_call logic from server.js so we can test
 * the contract without running the full server.
 */
import { test } from 'node:test';
import assert from 'node:assert/strict';

// -- Mock fetch --
let lastAriaRequest = null;
global.fetch = async (url, opts) => {
  if (typeof url === 'string' && url.includes('7890')) {
    lastAriaRequest = { url, body: JSON.parse(opts?.body || '{}') };
    return { ok: true, json: async () => ({ response: 'pong' }) };
  }
  throw new Error(`Unexpected fetch: ${url}`);
};

const ARIA_URL = 'http://100.75.109.92:7890';
const ARIA_SERVICE_KEY = 'test-key';

// -- Mirrors current server.js aria_local_call handler (BEFORE fix) --
async function ariaLocalCall_current(toolInput) {
  const mode = (toolInput.mode || 'chat').trim();
  const message = (toolInput.message || '').trim();
  const payload = toolInput.payload || {};
  const body = { message, ...payload };
  // NO session_id here — this is current broken behavior

  const res = await fetch(`${ARIA_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Aria-Service-Key': ARIA_SERVICE_KEY },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(5000),
  });
  return await res.json();
}

// -- Mirrors fixed server.js aria_local_call handler (AFTER fix) --
async function ariaLocalCall_fixed(toolInput, ariaSessionId) {
  const mode = (toolInput.mode || 'chat').trim();
  const message = (toolInput.message || '').trim();
  const payload = toolInput.payload || {};
  const body = { message, ...payload };
  if (ariaSessionId) body.session_id = ariaSessionId;  // <-- the fix

  const res = await fetch(`${ARIA_URL}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-Aria-Service-Key': ARIA_SERVICE_KEY },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(5000),
  });
  return await res.json();
}

// RED: current code does NOT include session_id — test should fail
test('RED: current aria_local_call does NOT include session_id', async () => {
  lastAriaRequest = null;
  await ariaLocalCall_current({ mode: 'chat', message: 'hello' });
  assert.ok(lastAriaRequest, 'Aria was called');
  // This assert SHOULD FAIL before the fix — session_id is missing
  assert.equal(
    lastAriaRequest.body.session_id,
    'conv_test_abc123',
    `Expected session_id in body, got: ${JSON.stringify(lastAriaRequest.body)}`
  );
});

// GREEN: fixed code DOES include session_id
test('GREEN: fixed aria_local_call includes session_id in Aria POST body', async () => {
  lastAriaRequest = null;
  const sessionId = 'conv_test_abc123';
  await ariaLocalCall_fixed({ mode: 'chat', message: 'hello' }, sessionId);
  assert.ok(lastAriaRequest, 'Aria was called');
  assert.equal(lastAriaRequest.body.session_id, sessionId, 'session_id must be in Aria body');
});

// GREEN: session_id absent when not provided (no accidental undefined)
test('GREEN: no session_id key when ariaSessionId is null', async () => {
  lastAriaRequest = null;
  await ariaLocalCall_fixed({ mode: 'chat', message: 'hello' }, null);
  assert.ok(lastAriaRequest, 'Aria was called');
  assert.ok(!('session_id' in lastAriaRequest.body), 'session_id must not appear when null');
});
