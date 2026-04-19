/**
 * Boot Hydration Tests
 * Tests for deterministic persona and history loading on app launch.
 * Phase Ascendance 1, Step 1, Task 1
 */

describe('Boot Hydration', () => {

  // Mock fetch globally
  global.fetch = jest.fn();

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('bootHydration function', () => {

    test('should exist as a callable function', () => {
      expect(typeof bootHydration).toBe('function');
    });

    test('should make parallel requests to all three canonical endpoints', async () => {
      // Mock responses
      global.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => ({ persona: 'Karma' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ session_id: '123' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ turns: [] }) });

      const result = await bootHydration();

      // Verify all three endpoints were called
      expect(global.fetch).toHaveBeenCalledTimes(3);
      expect(global.fetch).toHaveBeenCalledWith('/memory/wakeup');
      expect(global.fetch).toHaveBeenCalledWith('/memory/session');
      expect(global.fetch).toHaveBeenCalledWith(expect.stringMatching(/^\/v1\/session\//));
    });

    test('should return object with persona, session, and turns properties', async () => {
      const mockPersona = { name: 'Karma', status: 'ready' };
      const mockSession = { id: 'sess-123', created_at: '2026-04-18T10:00:00Z' };
      const mockTurns = [
        { role: 'user', text: 'hello' },
        { role: 'assistant', text: 'hi there' },
        { role: 'user', text: 'how are you' }
      ];

      global.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => mockPersona })
        .mockResolvedValueOnce({ ok: true, json: async () => mockSession })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ turns: mockTurns }) });

      const result = await bootHydration();

      expect(result).toHaveProperty('persona');
      expect(result).toHaveProperty('session');
      expect(result).toHaveProperty('turns');
      expect(result.turns).toHaveLength(3);
    });

    test('should return exactly last 3 turns from session', async () => {
      const allTurns = [
        { role: 'user', text: 'message 1' },
        { role: 'assistant', text: 'response 1' },
        { role: 'user', text: 'message 2' },
        { role: 'assistant', text: 'response 2' },
        { role: 'user', text: 'message 3' },
        { role: 'assistant', text: 'response 3' }
      ];
      const lastThree = allTurns.slice(-3);

      global.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => ({ persona: 'Karma' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 'sess-123' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ turns: allTurns }) });

      const result = await bootHydration();

      expect(result.turns).toEqual(lastThree);
      expect(result.turns).toHaveLength(3);
    });

    test('should gracefully handle missing persona data', async () => {
      global.fetch
        .mockResolvedValueOnce({ ok: false })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 'sess-123' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ turns: [] }) });

      const result = await bootHydration();

      expect(result).toHaveProperty('persona');
      expect(result.persona).toBe(null); // Graceful fallback, not undefined or fake data
    });

    test('should gracefully handle missing session data', async () => {
      global.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => ({ persona: 'Karma' }) })
        .mockResolvedValueOnce({ ok: false })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ turns: [] }) });

      const result = await bootHydration();

      expect(result).toHaveProperty('session');
      expect(result.session).toBe(null);
    });

    test('should use session_id from /memory/session for /v1/session/{id} fetch', async () => {
      const sessionId = 'test-session-456';

      global.fetch
        .mockResolvedValueOnce({ ok: true, json: async () => ({ persona: 'Karma' }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ session_id: sessionId }) })
        .mockResolvedValueOnce({ ok: true, json: async () => ({ turns: [] }) });

      const result = await bootHydration();

      // Verify the third call used the session_id from the second response
      const thirdCall = global.fetch.mock.calls[2][0];
      expect(thirdCall).toContain(sessionId);
    });

    test('should complete boot in under 2000ms', async () => {
      global.fetch
        .mockResolvedValue({ ok: true, json: async () => ({}) });

      const startTime = Date.now();
      await bootHydration();
      const endTime = Date.now();

      expect(endTime - startTime).toBeLessThan(2000);
    });
  });

  describe('persona rendering', () => {

    test('should render persona name when available', () => {
      const persona = { name: 'Karma', status: 'active' };
      const personaElement = renderPersona(persona);

      expect(personaElement.textContent).toContain('Karma');
      expect(personaElement.textContent).not.toContain('Unknown');
    });

    test('should render generic persona when data missing', () => {
      const personaElement = renderPersona(null);

      expect(personaElement.textContent).toContain('Karma');
      expect(personaElement.className).toContain('generic');
    });

    test('should never render hardcoded placeholder text', () => {
      const personaElement = renderPersona(null);

      expect(personaElement.textContent).not.toMatch(/TODO|PLACEHOLDER|placeholder|temp|TBD/i);
    });
  });

  describe('history rendering', () => {

    test('should render exactly 3 turns from session', () => {
      const turns = [
        { role: 'user', text: 'hello' },
        { role: 'assistant', text: 'hi' },
        { role: 'user', text: 'how are you' }
      ];

      const historyElement = renderHistory(turns);
      const turnElements = historyElement.querySelectorAll('[data-turn]');

      expect(turnElements.length).toBe(3);
    });

    test('should maintain turn order (oldest to newest)', () => {
      const turns = [
        { role: 'user', text: 'first' },
        { role: 'assistant', text: 'second' },
        { role: 'user', text: 'third' }
      ];

      const historyElement = renderHistory(turns);
      const texts = Array.from(historyElement.querySelectorAll('[data-turn]')).map(el => el.textContent.trim());

      expect(texts).toEqual(['first', 'second', 'third']);
    });

    test('should render empty state gracefully if no turns', () => {
      const historyElement = renderHistory([]);

      expect(historyElement).toBeDefined();
      expect(historyElement.textContent).not.toContain('null');
      expect(historyElement.textContent).not.toContain('undefined');
    });

    test('should never hardcode history data', () => {
      const historyElement = renderHistory([]);

      expect(historyElement.textContent).not.toMatch(/example|sample|test message/i);
    });
  });

  describe('timing instrumentation', () => {

    test('should expose boot timing metrics', async () => {
      global.fetch
        .mockResolvedValue({ ok: true, json: async () => ({}) });

      const result = await bootHydration();

      expect(result).toHaveProperty('timing');
      expect(result.timing).toHaveProperty('window_visible_ms');
      expect(result.timing).toHaveProperty('boot_fetch_start_ms');
      expect(result.timing).toHaveProperty('boot_fetch_end_ms');
      expect(result.timing).toHaveProperty('persona_paint_ms');
    });

    test('should measure fetch duration accurately', async () => {
      global.fetch
        .mockImplementation(() => {
          // Simulate 100ms fetch delay
          return new Promise(resolve =>
            setTimeout(() => resolve({ ok: true, json: async () => ({}) }), 100)
          );
        });

      const result = await bootHydration();

      expect(result.timing.boot_fetch_end_ms - result.timing.boot_fetch_start_ms).toBeGreaterThan(0);
    });
  });
});
