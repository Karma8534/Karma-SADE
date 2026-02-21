// Universal AI Memory - Background Service Worker
// Handles message passing and API communication
// E2E Proof: trace_id + item_hash + receipts

const HUB_API_URL = 'https://hub.arknexus.net/v1/chatlog';

// ---- batching / queue constants ----
const CAPTURE_QUEUE_KEY = 'captureQueue_v1';
const CAPTURE_QUEUE_META_KEY = 'captureQueueMeta_v1';
const FLUSH_ALARM_NAME = 'uaiMemoryCaptureFlush';
const BATCH_WINDOW_MS = 30_000;
const MAX_BATCH_ITEMS = 200;
const FLUSH_WHEN_QUEUE_GE = 25;
const MAX_QUEUE_ITEMS = 2000;
const BACKOFF_BASE_MS = 2_000;
const BACKOFF_MAX_MS = 60_000;
const DEBUG_LOG_KEY = 'debugLog_v1';
const MAX_DEBUG_EVENTS = 200;

// ---- crypto helpers ----
async function sha256(text) {
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
  return Array.from(new Uint8Array(buf)).map(x => x.toString(16).padStart(2, '0')).join('');
}

function randomBase36(len) {
  return Math.random().toString(36).substring(2, 2 + len);
}

// ---- debug ring buffer ----
async function logEvent(kind, data, trace_id) {
  const { [DEBUG_LOG_KEY]: logRaw } = await chrome.storage.local.get([DEBUG_LOG_KEY]);
  const log = Array.isArray(logRaw) ? logRaw : [];
  const event = {
    ts: new Date().toISOString(),
    kind: kind,
    data: data
  };
  if (trace_id) event.trace_id = trace_id;
  log.push(event);
  while (log.length > MAX_DEBUG_EVENTS) log.shift();
  await chrome.storage.local.set({ [DEBUG_LOG_KEY]: log });
}

// ---- trace ID generation ----
async function generateItemTrace(provider, threadId, role, normalizedText) {
  const trace_id = randomBase36(10);
  const hashInput = `${provider}:${threadId}:${role}:${normalizedText}`;
  const item_hash = await sha256(hashInput);
  return { trace_id, item_hash };
}

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CAPTURE_CONVERSATION') {
    handleConversationCapture(message.data)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }

  if (message.type === 'GET_CONFIG') {
    chrome.storage.sync.get(['captureToken', 'vaultToken', 'enabled'], (config) => {
      sendResponse(config);
    });
    return true;
  }

  if (message.type === 'RESET_STATS') {
    chrome.storage.local.set({ stats: { captured: 0, failed: 0 } }, () => {
      console.log('[UAI Memory] Stats reset');
      sendResponse({ success: true });
    });
    return true;
  }
});

// Handle conversation capture and send to Hub
async function handleConversationCapture(data) {
  const config = await chrome.storage.sync.get(['captureToken', 'vaultToken', 'enabled']);
  if (!config.enabled) {
    console.log('[UAI Memory] Capture disabled, skipping');
    return { skipped: true, reason: 'disabled' };
  }
  const authToken = (config.captureToken && config.captureToken.trim().length)
    ? config.captureToken.trim()
    : (config.vaultToken || '').trim();
  console.log('[UAI Memory] auth token selected', {
    enabled: !!config.enabled,
    captureTokenLen: (config.captureToken || '').trim().length,
    vaultTokenLen: (config.vaultToken || '').trim().length,
    using: (config.captureToken && config.captureToken.trim().length) ? 'captureToken' : 'vaultToken'
  });
  if (!authToken) {
    console.error('[UAI Memory] No capture token configured');
    return { error: 'No capture token configured' };
  }

  // Generate trace + hash for this item
  const userNorm = (data.user_message || '').toLowerCase().replace(/\s+/g, ' ').substring(0, 100);
  const { trace_id, item_hash } = await generateItemTrace(
    data.provider,
    data.thread_id || 'unknown',
    'user',
    userNorm
  );

  const payload = {
    provider: data.provider,
    url: data.url,
    timestamp: data.timestamp || new Date().toISOString(),
    user_message: data.user_message,
    assistant_message: data.assistant_message,
    thread_id: data.thread_id || null,
    metadata: data.metadata || {},
    trace_id: trace_id,
    item_hash: item_hash
  };

  await enqueueCapture(payload);
  await logEvent('ENQUEUE_OK', { queue_size: (await getQueueStats()).size }, trace_id);

  await ensureFlushAlarm();
  const { size, oldestTs } = await getQueueStats();
  const ageMs = oldestTs ? (Date.now() - oldestTs) : 0;
  if (size >= FLUSH_WHEN_QUEUE_GE || ageMs >= BATCH_WINDOW_MS) {
    flushCaptureQueue().catch(err => console.warn('[UAI Memory] flushCaptureQueue failed:', err));
  }

  // Don't update "Captured" stat here; wait for Hub acceptance
  return { ok: true, queued: true, queue_size: size, trace_id };
}

// ---- queue helpers (durable) ----
async function enqueueCapture(item) {
  const { [CAPTURE_QUEUE_KEY]: queueRaw } = await chrome.storage.local.get([CAPTURE_QUEUE_KEY]);
  const queue = Array.isArray(queueRaw) ? queueRaw : [];
  while (queue.length >= MAX_QUEUE_ITEMS) queue.shift();
  queue.push(item);
  const { [CAPTURE_QUEUE_META_KEY]: metaRaw } = await chrome.storage.local.get([CAPTURE_QUEUE_META_KEY]);
  const meta = (metaRaw && typeof metaRaw === 'object') ? metaRaw : {};
  if (!meta.oldestTs) meta.oldestTs = Date.now();
  if (!meta.backoffMs) meta.backoffMs = 0;
  if (!meta.nextAttemptAt) meta.nextAttemptAt = 0;
  await chrome.storage.local.set({
    [CAPTURE_QUEUE_KEY]: queue,
    [CAPTURE_QUEUE_META_KEY]: meta
  });
}

async function getQueueStats() {
  const { [CAPTURE_QUEUE_KEY]: queueRaw, [CAPTURE_QUEUE_META_KEY]: metaRaw } =
    await chrome.storage.local.get([CAPTURE_QUEUE_KEY, CAPTURE_QUEUE_META_KEY]);
  const queue = Array.isArray(queueRaw) ? queueRaw : [];
  const meta = (metaRaw && typeof metaRaw === 'object') ? metaRaw : {};
  return { size: queue.length, oldestTs: meta.oldestTs || null, meta };
}

async function ensureFlushAlarm() {
  try {
    await chrome.alarms.create(FLUSH_ALARM_NAME, { periodInMinutes: 0.5 });
  } catch (e) {
    await chrome.alarms.create(FLUSH_ALARM_NAME, { periodInMinutes: 1 });
  }
}

// Listen for alarm ticks
chrome.alarms.onAlarm.addListener((alarm) => {
  if (!alarm || !alarm.name) return;
  if (alarm.name === FLUSH_ALARM_NAME) {
    flushCaptureQueue().catch(err => console.warn('[UAI Memory] flushCaptureQueue failed:', err));
    return;
  }
  if (alarm.name === 'keepalive') {
    chrome.storage.local.get(['__uai_keepalive']).then(() => {
      // no-op
    }).catch(() => {
      // ignore
    });
  }
});

// ---- flush logic ----
async function flushCaptureQueue() {
  if (globalThis.__uaiFlushInFlight) return;
  globalThis.__uaiFlushInFlight = true;
  try {
    const config = await chrome.storage.sync.get(['captureToken', 'vaultToken', 'enabled']);
    if (!config.enabled) return;
    const authToken = (config.captureToken && config.captureToken.trim().length)
      ? config.captureToken.trim()
      : (config.vaultToken || '').trim();
    console.log('[UAI Memory] auth token selected', {
      enabled: !!config.enabled,
      captureTokenLen: (config.captureToken || '').trim().length,
      vaultTokenLen: (config.vaultToken || '').trim().length,
      using: (config.captureToken && config.captureToken.trim().length) ? 'captureToken' : 'vaultToken'
    });
    if (!authToken) return;

    const store = await chrome.storage.local.get([CAPTURE_QUEUE_KEY, CAPTURE_QUEUE_META_KEY]);
    const queue = Array.isArray(store[CAPTURE_QUEUE_KEY]) ? store[CAPTURE_QUEUE_KEY] : [];
    const meta = (store[CAPTURE_QUEUE_META_KEY] && typeof store[CAPTURE_QUEUE_META_KEY] === 'object')
      ? store[CAPTURE_QUEUE_META_KEY]
      : { oldestTs: null, backoffMs: 0, nextAttemptAt: 0 };

    if (queue.length === 0) {
      await chrome.storage.local.set({ [CAPTURE_QUEUE_META_KEY]: { oldestTs: null, backoffMs: 0, nextAttemptAt: 0 } });
      return;
    }

    const now = Date.now();
    if (meta.nextAttemptAt && now < meta.nextAttemptAt) {
      return;
    }

    const batch = queue.slice(0, MAX_BATCH_ITEMS);
    await logEvent('FLUSH_START', { queue_size: queue.length, meta });

    let response;
    try {
      response = await fetch(HUB_API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ batch })
      });

      await logEvent('POST_RESULT', { status: response.status });

      if (response.status === 429) {
        const retryAfter = parseInt(response.headers.get('retry-after') || '', 10);
        const retryAfterMs = Number.isFinite(retryAfter) ? retryAfter * 1000 : 0;
        const prev = Number(meta.backoffMs || 0);
        const next = Math.min(BACKOFF_MAX_MS, prev ? prev * 2 : BACKOFF_BASE_MS);
        const backoffMs = Math.max(next, retryAfterMs);
        meta.backoffMs = backoffMs;
        meta.nextAttemptAt = now + backoffMs;
        await chrome.storage.local.set({ [CAPTURE_QUEUE_META_KEY]: meta });
        await logEvent('POST_429_BACKOFF', { backoffMs });
        console.warn('[UAI Memory] Hub rate_limited; backing off ms=', backoffMs);

        // Write lastPost immediately for rate limit
        await chrome.storage.local.set({
          lastPost: {
            ts: new Date().toISOString(),
            status: response.status,
            ok: false,
            sent: batch.length,
            remaining: queue.length - batch.length,
            error: 'rate_limited'
          }
        });

        await updateStatsBy('failed', 1);
        return;
      }

      if (!response.ok) {
        const errorText = await response.text().catch(() => '');
        await logEvent('POST_NONOK', { status: response.status });
        console.warn('[UAI Memory] Hub API error:', response.status, errorText.slice(0, 200));

        // Write lastPost immediately for non-ok status
        await chrome.storage.local.set({
          lastPost: {
            ts: new Date().toISOString(),
            status: response.status,
            ok: false,
            sent: batch.length,
            remaining: queue.length - batch.length,
            error: `http_${response.status}`
          }
        });

        await updateStatsBy('failed', 1);
        return;
      }

      const result = await response.json().catch(() => ({}));
      const remaining = queue.slice(batch.length);
      const newMeta = {
        oldestTs: remaining.length ? (meta.oldestTs || now) : null,
        backoffMs: 0,
        nextAttemptAt: 0
      };
      await chrome.storage.local.set({
        [CAPTURE_QUEUE_KEY]: remaining,
        [CAPTURE_QUEUE_META_KEY]: newMeta
      });

      // Write lastPost immediately for success
      await chrome.storage.local.set({
        lastPost: {
          ts: new Date().toISOString(),
          status: response.status,
          ok: true,
          sent: batch.length,
          remaining: remaining.length
        }
      });

      // Save receipt if provided
      if (result.receipt_id) {
        await chrome.storage.local.set({
          lastReceipt: {
            ts: new Date().toISOString(),
            receipt_id: result.receipt_id,
            accepted: result.accepted || 0,
            rejected: result.rejected || 0,
            items: result.items || []
          }
        });
        await logEvent('RECEIPT_SAVED', { receipt_id: result.receipt_id, accepted: result.accepted, rejected: result.rejected });

        // Update stats: count accepted items from receipt
        const acceptedCount = result.accepted || 0;
        if (acceptedCount > 0) {
          await updateStatsBy('captured', acceptedCount);
        }
      } else {
        // No receipt_id provided: assume all items in batch were accepted (fallback behavior)
        await logEvent('NO_RECEIPT_FALLBACK', { assumed_accepted: batch.length });
        await updateStatsBy('captured', batch.length);
      }

      await logEvent('POST_OK', { sent: batch.length, remaining: remaining.length });
      console.log('[UAI Memory] Batch flush success:', {
        sent: batch.length,
        remaining: remaining.length,
        hub: result
      });
    } catch (fetchError) {
      // Network error, DNS failure, or other fetch exception
      const errMsg = String(fetchError && fetchError.message ? fetchError.message : fetchError).slice(0, 120);
      await logEvent('FETCH_THROW', { error: errMsg });
      console.error('[UAI Memory] Fetch error:', fetchError.message);

      // Write lastPost immediately for fetch exception
      await chrome.storage.local.set({
        lastPost: {
          ts: new Date().toISOString(),
          status: null,
          ok: false,
          sent: batch.length,
          remaining: queue.length - batch.length,
          error: `fetch_exception: ${errMsg}`
        }
      });

      await updateStatsBy('failed', 1);
      return;
    }
  } finally {
    globalThis.__uaiFlushInFlight = false;
  }
}

// Load stats object
async function loadStatsObj() {
  const result = await chrome.storage.local.get(['stats']) || { stats: { captured: 0, failed: 0 } };
  return result.stats || { captured: 0, failed: 0 };
}

// Update stats by delta (single read, single write)
async function updateStatsBy(type, delta) {
  const stats = await loadStatsObj();
  stats[type] = (stats[type] || 0) + delta;
  await chrome.storage.local.set({ stats });
}

// Keep-alive: MV3 service workers die after 30s of inactivity
chrome.alarms.create('keepalive', { periodInMinutes: 0.4 });

// Installation handler
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('[UAI Memory] Extension installed');
    chrome.storage.sync.set({
      enabled: false,
      vaultToken: '',
      captureToken: ''
    });
    chrome.storage.local.set({
      stats: { captured: 0, failed: 0 },
      debugLog_v1: [],
      lastPost: null,
      lastReceipt: null
    });
    chrome.tabs.create({ url: 'popup.html' });
  }
});
