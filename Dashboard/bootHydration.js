/**
 * Boot Hydration Module
 * Deterministic persona and history loading on app launch
 * Phase Ascendance 1, Step 1, Task 1
 */

/**
 * Fetch persona, session, and history in parallel
 * @returns {Promise<{persona: Object|null, session: Object|null, turns: Array, timing: Object}>}
 */
async function bootHydration() {
  const timing = {
    fetch_start_ms: Date.now(),
    fetch_end_ms: null,
    paint_ms: null
  };

  try {
    // Step 1: Parallel requests to canonical endpoints
    const [wakeupRes, sessionRes] = await Promise.all([
      fetch('/memory/wakeup').catch(() => ({ ok: false })),
      fetch('/memory/session').catch(() => ({ ok: false }))
    ]);

    let persona = null;
    let session = null;
    let sessionId = null;

    // Step 2: Parse responses gracefully
    if (wakeupRes.ok) {
      try {
        persona = await wakeupRes.json();
      } catch (e) {
        console.error('Failed to parse persona:', e);
        persona = null;
      }
    }

    if (sessionRes.ok) {
      try {
        session = await sessionRes.json();
        sessionId = session?.session_id;
      } catch (e) {
        console.error('Failed to parse session:', e);
        session = null;
      }
    }

    // Step 3: Fetch session turns using session_id
    let turns = [];
    if (sessionId) {
      try {
        const turnsRes = await fetch(`/v1/session/${sessionId}`).catch(() => ({ ok: false }));
        if (turnsRes.ok) {
          const turnsData = await turnsRes.json();
          // Extract last 3 turns deterministically
          turns = (turnsData.turns || []).slice(-3);
        }
      } catch (e) {
        console.error('Failed to fetch session turns:', e);
        turns = [];
      }
    }

    timing.fetch_end_ms = Date.now();

    return {
      persona: persona || null,
      session: session || null,
      turns: turns,
      timing: timing,
      source: {
        persona: persona ? 'remote' : 'null',
        session: session ? 'remote' : 'null',
        turns: turns.length > 0 ? 'remote' : 'empty'
      }
    };
  } catch (error) {
    console.error('Boot hydration failed:', error);
    timing.fetch_end_ms = Date.now();
    return {
      persona: null,
      session: null,
      turns: [],
      timing: timing,
      error: error.message,
      source: { persona: 'error', session: 'error', turns: 'error' }
    };
  }
}

/**
 * Render persona block in UI
 * @param {Object|null} persona - Persona data or null
 * @returns {HTMLElement}
 */
function renderPersona(persona) {
  const container = document.createElement('div');
  container.className = persona ? 'persona-block' : 'persona-block generic';
  container.setAttribute('data-test', 'persona-block');

  if (persona && persona.name) {
    container.innerHTML = `
      <div class="persona-name">${escapeHtml(persona.name)}</div>
      <div class="persona-status">${escapeHtml(persona.status || 'ready')}</div>
    `;
  } else {
    container.innerHTML = `
      <div class="persona-name">Karma</div>
      <div class="persona-status">—</div>
    `;
    container.classList.add('generic');
  }

  return container;
}

/**
 * Render history (last 3 turns) in UI
 * @param {Array} turns - Array of turn objects {role, text}
 * @returns {HTMLElement}
 */
function renderHistory(turns) {
  const container = document.createElement('div');
  container.className = 'history-block';
  container.setAttribute('data-test', 'history-block');

  if (!turns || turns.length === 0) {
    container.innerHTML = '<div class="history-empty">No prior session</div>';
    return container;
  }

  const historyHtml = turns
    .map((turn, idx) => `
      <div class="turn" data-turn="${idx}">
        <div class="turn-role">${escapeHtml(turn.role)}</div>
        <div class="turn-text">${escapeHtml(turn.text || '')}</div>
      </div>
    `)
    .join('');

  container.innerHTML = `<div class="turns">${historyHtml}</div>`;
  return container;
}

/**
 * Render timing info for debugging
 * @param {Object} timing - Timing data with fetch_start_ms, fetch_end_ms
 * @returns {HTMLElement}
 */
function renderTiming(timing) {
  const container = document.createElement('div');
  container.className = 'timing-block';
  container.setAttribute('data-test', 'timing-block');

  const fetchDuration = timing.fetch_end_ms - timing.fetch_start_ms;
  const paintDuration = timing.paint_ms || 0;

  container.innerHTML = `
    <div class="timing-metric">Fetch: ${fetchDuration}ms</div>
    <div class="timing-metric">Paint: ${paintDuration}ms</div>
  `;

  return container;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text
 * @returns {string}
 */
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

/**
 * Initialize boot hydration on page load
 * Integrates with unified.html dashboard
 */
async function initializeBootHydration() {
  const startPaint = Date.now();

  // Fetch all data
  const hydrationData = await bootHydration();

  // Record paint timing
  hydrationData.timing.paint_ms = Date.now() - startPaint;

  // Find or create containers in unified.html
  const personaContainer = document.querySelector('[data-section="persona"]') ||
                          document.querySelector('.persona-section');
  const historyContainer = document.querySelector('[data-section="history"]') ||
                          document.querySelector('.history-section');
  const timingContainer = document.querySelector('[data-section="timing"]') ||
                         document.querySelector('.timing-debug');

  // Render components
  if (personaContainer) {
    personaContainer.innerHTML = '';
    personaContainer.appendChild(renderPersona(hydrationData.persona));
  }

  if (historyContainer) {
    historyContainer.innerHTML = '';
    historyContainer.appendChild(renderHistory(hydrationData.turns));
  }

  if (timingContainer) {
    timingContainer.innerHTML = '';
    timingContainer.appendChild(renderTiming(hydrationData.timing));
  }

  // Export metrics for evidence generation
  window.__bootMetrics = {
    persona: hydrationData.persona,
    session: hydrationData.session,
    turns: hydrationData.turns,
    timing: hydrationData.timing,
    source: hydrationData.source
  };

  // Log for verification
  console.log('[Boot Hydration]', {
    persona: hydrationData.persona?.name || 'null',
    turns: hydrationData.turns.length,
    fetch_ms: hydrationData.timing.fetch_end_ms - hydrationData.timing.fetch_start_ms,
    paint_ms: hydrationData.timing.paint_ms,
    passed: hydrationData.timing.paint_ms < 2000
  });

  return hydrationData;
}

// Auto-initialize if DOM is ready, otherwise defer
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeBootHydration);
} else {
  // DOM already loaded
  initializeBootHydration().catch(err => console.error('[Boot Hydration Error]', err));
}
