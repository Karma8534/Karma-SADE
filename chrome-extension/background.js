// Universal AI Memory - Background Service Worker
// Handles message passing and API communication

const HUB_API_URL = 'https://hub.arknexus.net/v1/chatlog';

// ---- batching / queue constants ----
const CAPTURE_QUEUE_KEY = 'captureQueue_v1';
const CAPTURE_QUEUE_META_KEY = 'captureQueueMeta_v1';
const FLUSH_ALARM_NAME = 'uaiMemoryCaptureFlush';
const BATCH_WINDOW_MS = 30_000;       // 30s debounce window (optimal for your chat cadence)
const MAX_BATCH_ITEMS = 200;          // hub supports up to 200
const FLUSH_WHEN_QUEUE_GE = 25;       // flush early on bursts
const MAX_QUEUE_ITEMS = 2000;         // hard cap to avoid unbounded growth
const BACKOFF_BASE_MS = 2_000;        // retry base
const BACKOFF_MAX_MS = 60_000;        // retry ceiling

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'CAPTURE_CONVERSATION') {
    handleConversationCapture(message.data)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async response
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
  // Get tokens + enabled state
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
  // Prepare payload (single item)
  const payload = {
    provider: data.provider,
    url: data.url,
    timestamp: data.timestamp || new Date().toISOString(),
    user_message: data.user_message,
    assistant_message: data.assistant_message,
    thread_id: data.thread_id || null,
    metadata: data.metadata || {}
  };
  // Enqueue durably (storage.local so it survives service worker sleep/restart)
  await enqueueCapture(payload);
  // Ensure flush alarm exists (MV3-friendly scheduling)
  await ensureFlushAlarm();
  // Optionally flush early on bursts
  const { size, oldestTs } = await getQueueStats();
  const ageMs = oldestTs ? (Date.now() - oldestTs) : 0;
  if (size >= FLUSH_WHEN_QUEUE_GE || ageMs >= BATCH_WINDOW_MS) {
    // Fire-and-forget; do not block capture path
    flushCaptureQueue().catch(err => console.warn('[UAI Memory] flushCaptureQueue failed:', err));
  }
  // Update local stats as "captured" meaning "queued"
  await updateStats('captured');
  return { ok: true, queued: true, queue_size: size };
}

// ---- queue helpers (durable) ----
async function enqueueCapture(item) {
  const { [CAPTURE_QUEUE_KEY]: queueRaw } = await chrome.storage.local.get([CAPTURE_QUEUE_KEY]);
  const queue = Array.isArray(queueRaw) ? queueRaw : [];
  // Cap queue size (drop oldest if exceeded)
  while (queue.length >= MAX_QUEUE_ITEMS) queue.shift();
  queue.push(item);
  // Track meta for batching age/backoff
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
  return { size: queue.length, oldestTs: meta.oldestTs || null };
}

async function ensureFlushAlarm() {
  // Create/refresh the alarm. Period is in minutes; 0.5 => 30 seconds.
  // If the platform clamps, we still flush on next event; this is best-effort.
  try {
    await chrome.alarms.create(FLUSH_ALARM_NAME, { periodInMinutes: 0.5 });
  } catch (e) {
    // Some Chrome versions may not support 0.5; fall back to 1 minute
    await chrome.alarms.create(FLUSH_ALARM_NAME, { periodInMinutes: 1 });
  }
}

// Listen for alarm ticks (MV3 service worker-safe)
chrome.alarms.onAlarm.addListener((alarm) => {
  if (!alarm || !alarm.name) return;
  if (alarm.name === FLUSH_ALARM_NAME) {
    flushCaptureQueue().catch(err => console.warn('[UAI Memory] flushCaptureQueue (alarm) failed:', err));
    return;
  }
  // Keepalive branch (prevents MV3 service worker from going fully cold for long stretches)
  if (alarm.name === 'keepalive') {
    // Minimal storage read/write (no secrets, no network)
    chrome.storage.local.get(['__uai_keepalive']).then(() => {
      // no-op
    }).catch(() => {
      // ignore
    });
  }
});

// ---- flush logic ----
async function flushCaptureQueue() {
  // Single-flight guard (avoid overlapping flushes)
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
      // reset meta
      await chrome.storage.local.set({ [CAPTURE_QUEUE_META_KEY]: { oldestTs: null, backoffMs: 0, nextAttemptAt: 0 } });
      return;
    }
    const now = Date.now();
    if (meta.nextAttemptAt && now < meta.nextAttemptAt) {
      return; // still backing off
    }
    const batch = queue.slice(0, MAX_BATCH_ITEMS);
    const response = await fetch(HUB_API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({ batch })
    });
    if (response.status === 429) {
      // Rate limited: compute backoff
      const retryAfter = parseInt(response.headers.get('retry-after') || '', 10);
      const retryAfterMs = Number.isFinite(retryAfter) ? retryAfter * 1000 : 0;
      const prev = Number(meta.backoffMs || 0);
      const next = Math.min(BACKOFF_MAX_MS, prev ? prev * 2 : BACKOFF_BASE_MS);
      const backoffMs = Math.max(next, retryAfterMs);
      meta.backoffMs = backoffMs;
      meta.nextAttemptAt = now + backoffMs;
      await chrome.storage.local.set({ [CAPTURE_QUEUE_META_KEY]: meta });
      console.warn('[UAI Memory] Hub rate_limited; backing off ms=', backoffMs);
      await updateStats('failed');
      return;
    }
    if (!response.ok) {
      const errorText = await response.text().catch(() => '');
      console.warn('[UAI Memory] Hub API error:', response.status, errorText.slice(0, 200));
      await updateStats('failed');
      // Do not drop items; keep them queued and retry on next alarm
      return;
    }
    const result = await response.json().catch(() => ({}));
    // On success: drop sent items
    const remaining = queue.slice(batch.length);
    // Reset/adjust meta
    const newMeta = {
      oldestTs: remaining.length ? (meta.oldestTs || now) : null,
      backoffMs: 0,
      nextAttemptAt: 0
    };
    await chrome.storage.local.set({
      [CAPTURE_QUEUE_KEY]: remaining,
      [CAPTURE_QUEUE_META_KEY]: newMeta
    });
    console.log('[UAI Memory] Batch flush success:', {
      sent: batch.length,
      remaining: remaining.length,
      hub: result
    });
  } finally {
    globalThis.__uaiFlushInFlight = false;
  }
}

// Update capture statistics
async function updateStats(type) {
  const stats = await chrome.storage.local.get(['stats']) || { stats: { captured: 0, failed: 0 } };
  const currentStats = stats.stats || { captured: 0, failed: 0 };
  currentStats[type] = (currentStats[type] || 0) + 1;
  await chrome.storage.local.set({ stats: currentStats });
}

// Keep-alive: MV3 service workers die after 30s of inactivity.
// A periodic alarm wakes it back up so content script messages always have a listener.
chrome.alarms.create('keepalive', { periodInMinutes: 0.4 });

// Installation handler
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('[UAI Memory] Extension installed');
    // Set default config
    chrome.storage.sync.set({
      enabled: false, // Disabled by default until token is configured
      vaultToken: '',
      captureToken: ''
    });

    // Initialize stats
    chrome.storage.local.set({
      stats: { captured: 0, failed: 0 }
    });

    // Open setup page
    chrome.tabs.create({ url: 'popup.html' });
  }
});
