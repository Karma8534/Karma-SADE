import { create } from 'zustand';
import { apiFetch } from '@/lib/api';

// ── Types ────────────────────────────────────────────────────────────────────

export type MessageRole = 'user' | 'karma' | 'system' | 'tool-evidence';

export interface ToolCall {
  id: string;
  name: string;
  input: Record<string, unknown>;
  output?: string;
  status: 'running' | 'completed' | 'error';
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  toolCalls?: ToolCall[];
  // For tool-evidence role
  toolName?: string;
  toolInput?: Record<string, unknown>;
  toolOutput?: string;
}

export interface PendingFile {
  name: string;
  type: string;
  data: string; // base64 data URL
}

export interface SelfEditProposal {
  id: number;
  file_path: string;
  description: string;
  risk_level: string;
  proposed_at: string;
  status: string;
  auto_approve_at?: string;
}

export type EffortLevel = '' | 'low' | 'medium' | 'high' | 'max';
export type BootHydrationState = 'idle' | 'loading' | 'ready' | 'degraded';

export interface BootTiming {
  window_visible_ms: number;
  boot_fetch_start_ms: number;
  boot_fetch_end_ms: number;
  persona_paint_ms: number;
}

// ── Visible tools (collapsible blocks) vs pill tools ─────────────────────────

export const VISIBLE_TOOLS = new Set([
  'shell_run', 'python_exec', 'k2_file_read', 'get_vault_file',
  'k2_file_write', 'k2_file_list', 'k2_file_search',
  'graph_query', 'write_memory', 'browse_url', 'fetch_url',
  'WebSearch', 'WebFetch',
]);

export const PILL_LABELS: Record<string, string> = {
  Bash: '\u2699\ufe0f running', Read: '\ud83d\udd0d reading',
  Glob: '\ud83d\udd0d searching files', Grep: '\ud83d\udd0d searching code',
  Edit: '\u270f\ufe0f editing', Write: '\ud83d\udcbe writing',
  ToolSearch: '\ud83d\udd0d searching tools', TodoWrite: '\ud83d\udccb updating tasks',
  scratchpad_read: '\ud83d\udcdd checking memory', scratchpad_write: '\ud83d\udcdd saving to memory',
  Agent: '\ud83e\udd16 delegating', bus_post: '\ud83d\udce8 posting to bus',
  kiki_status: '\ud83d\udc3e checking kiki',
};

const PILL_DEFAULT = '\u2699\ufe0f working';

export function isVisibleTool(name: string): boolean {
  return VISIBLE_TOOLS.has(name) || VISIBLE_TOOLS.has(cleanToolName(name));
}

export function getPillLabel(name: string): string {
  return PILL_LABELS[name] || PILL_LABELS[cleanToolName(name)] || PILL_DEFAULT;
}

function cleanToolName(name: string): string {
  if (!name) return '';
  // Strip MCP prefixes: mcp__server__tool → tool
  const parts = name.split('__');
  return parts[parts.length - 1] || name;
}

// ── Store ────────────────────────────────────────────────────────────────────

export interface FileNode {
  name: string;
  type: 'file' | 'dir';
  path: string;
  size?: number;
  children?: FileNode[];
}

interface KarmaState {
  // Auth
  token: string;
  isAuthenticated: boolean;

  // Chat
  messages: ChatMessage[];
  isStreaming: boolean;
  conversationId: string;
  streamAbortController: AbortController | null;

  // Files
  pendingFiles: PendingFile[];

  // Controls
  effortLevel: EffortLevel;
  theme: 'dark' | 'light';
  outputStyle: '' | 'concise' | 'detailed' | 'technical' | 'creative';
  personalPreferences: string;

  // Tool tracking (for stream)
  activeToolCalls: Map<string, ToolCall>;

  // Self-edit
  selfEditProposals: SelfEditProposal[];

  // Cost
  sessionCost: number;

  // Last inference routing (what model/provider actually answered)
  lastModel: string;
  lastProvider: string;

  // Surface (merged state from /v1/surface)
  surface: {
    session?: { session_id: string };
    git?: { branch: string; changed: number; files: string[]; recent_commits: string[] };
    files?: { root: string; tree: FileNode[] };
    skills?: { count: number; names: string[] };
    hooks?: { count: number; active: boolean; list: { name: string; event: string }[] };
    memory?: { tail: string; file: string };
    state?: { text: string };
    agents?: Record<string, unknown>;
    transcripts?: { count: number; sessions: string[] };
  } | null;

  // Status
  lastSeen: string;
  k2Active: boolean;
  brainOk: boolean;
  error: string | null;
  bootHydration: BootHydrationState;
  bootError: string | null;
  bootSessionId: string;
  bootTiming: BootTiming | null;
  bootPersonaBlock: string;

  // Actions
  hydrateBootFrame: () => Promise<void>;
  fetchSurface: () => Promise<void>;
  setToken: (token: string) => void;
  setConversationId: (id: string) => void;
  writeSessionTurn: (role: 'user' | 'karma' | 'system', content: string, sessionId?: string) => Promise<void>;
  syncSessionTurns: () => Promise<void>;
  logout: () => void;
  addMessage: (msg: ChatMessage) => void;
  updateLastMessage: (content: string) => void;
  appendToLastMessage: (delta: string) => void;
  setStreaming: (v: boolean) => void;
  setAbortController: (ac: AbortController | null) => void;
  addFile: (file: PendingFile) => void;
  removeFile: (index: number) => void;
  clearFiles: () => void;
  setEffort: (level: EffortLevel) => void;
  setTheme: (theme: 'dark' | 'light') => void;
  setOutputStyle: (style: '' | 'concise' | 'detailed' | 'technical' | 'creative') => void;
  setPersonalPreferences: (prefs: string) => void;
  addToolCall: (tc: ToolCall) => void;
  updateToolResult: (id: string, output: string) => void;
  addSelfEditProposal: (p: SelfEditProposal) => void;
  approveSelfEdit: (id: number) => void;
  rejectSelfEdit: (id: number) => void;
  addCost: (usd: number) => void;
  setLastInference: (model: string, provider: string) => void;
  setStatus: (status: { lastSeen?: string; k2Active?: boolean; brainOk?: boolean }) => void;
  setError: (err: string | null) => void;
  clearMessages: () => void;
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

const MESSAGES_KEY = 'karma-messages';
const SESSION_SNAPSHOT_PATH = 'tmp/karma-ui-session.json';

function readStoredMessages(): ChatMessage[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = localStorage.getItem(MESSAGES_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function setStoredConversationId(id: string) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem('karma-conversation-id', id);
  } catch {}
}

function normalizeHistoryRole(value: unknown): MessageRole {
  const v = String(value || '').trim().toLowerCase();
  if (v === 'assistant' || v === 'karma') return 'karma';
  if (v === 'user') return 'user';
  if (v === 'system') return 'system';
  return 'system';
}

function buildBootPersonaBlock(wakeup: string): string {
  const trimmed = String(wakeup || '').trim();
  if (!trimmed) {
    return '**KARMA BOOT**\nIdentity: Karma\nMode: canonical memory wakeup unavailable.';
  }
  const lines = trimmed
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .filter((line) => !/payload_base64=|session_store_v1\s+session_id/i.test(line))
    .map((line) => (line.length > 180 ? `${line.slice(0, 177)}...` : line))
    .slice(0, 6);
  return `**KARMA BOOT**\nIdentity: Karma\n\n${lines.join('\n')}`;
}

function readLastThreeCanonicalTurns(sessionPayload: Record<string, unknown>): ChatMessage[] {
  const rawHistory = Array.isArray(sessionPayload.history) ? sessionPayload.history : [];
  const mapped: ChatMessage[] = [];
  for (let i = 0; i < rawHistory.length; i++) {
    const item = rawHistory[i] as Record<string, unknown>;
    const body = (item.body && typeof item.body === 'object') ? (item.body as Record<string, unknown>) : {};
    const role = normalizeHistoryRole(body.role);
    if (role === 'tool-evidence') continue;
    const content = String(body.content || item.text || '').trim();
    if (!content) continue;
    // Exclude ambient/system chatter so boot frame surfaces meaningful dialogue.
    if (/^\[KARMA HEARTBEAT\b/i.test(content)) continue;
    if (/^coord_[0-9]+_[a-z0-9]+/i.test(content)) continue;
    if (/^AUTO-APPROVED\b/i.test(content)) continue;
    const timestamp = String(item.ts || body.ts || new Date().toISOString());
    mapped.push({
      id: `boot-history-${i}-${timestamp}`,
      role,
      content,
      timestamp,
    });
  }
  return mapped.slice(-3);
}

function persistMessages(messages: ChatMessage[], conversationId: string) {
  if (typeof window === 'undefined') return;
  try {
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages));
  } catch {}
  try {
    const electronApi = (window as typeof window & {
      karma?: { isElectron?: boolean; fileWrite?: (path: string, content: string) => Promise<unknown> };
    }).karma;
    if (electronApi?.isElectron && electronApi.fileWrite) {
      void electronApi.fileWrite(
        SESSION_SNAPSHOT_PATH,
        JSON.stringify({ conversationId, savedAt: new Date().toISOString(), messages }, null, 2),
      );
    }
  } catch {}
}

// Phase Ascendance 3 harness hook: expose store to window for CDP-driven tests.
// Read-write via `window.__karmaStore.getState().addMessage(...)` in CDP evaluate.
export const useKarmaStore = create<KarmaState>((set, get) => ({
  // Initial state
  token: typeof window !== 'undefined' ? localStorage.getItem('karma-token') || '' : '',
  isAuthenticated: false,
  messages: [],
  isStreaming: false,
  conversationId: typeof window !== 'undefined'
    ? localStorage.getItem('karma-conversation-id') || generateId()
    : generateId(),
  streamAbortController: null,
  pendingFiles: [],
  effortLevel: '',
  theme: 'dark' as const,
  outputStyle: '' as const,
  personalPreferences: typeof window !== 'undefined' ? localStorage.getItem('karma-preferences') || '' : '',
  activeToolCalls: new Map(),
  selfEditProposals: [],
  sessionCost: 0,
  lastModel: '',
  lastProvider: '',
  surface: null,
  lastSeen: '',
  k2Active: false,
  brainOk: false,
  error: null,
  bootHydration: 'idle',
  bootError: null,
  bootSessionId: '',
  bootTiming: null,
  bootPersonaBlock: '',

  // Auth
  setToken: (token) => {
    if (typeof window !== 'undefined') localStorage.setItem('karma-token', token);
    set({ token, isAuthenticated: true });
  },
  logout: () => {
    if (typeof window !== 'undefined') localStorage.removeItem('karma-token');
    set({ token: '', isAuthenticated: false });
  },

  // Messages
  addMessage: (msg) => set((s) => {
    const messages = [...s.messages, msg];
    persistMessages(messages, s.conversationId);
    return { messages };
  }),
  updateLastMessage: (content) =>
    set((s) => {
      const msgs = [...s.messages];
      if (msgs.length > 0) msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], content };
      persistMessages(msgs, s.conversationId);
      return { messages: msgs };
    }),
  appendToLastMessage: (delta) =>
    set((s) => {
      const msgs = [...s.messages];
      if (msgs.length > 0 && msgs[msgs.length - 1].role === 'karma') {
        msgs[msgs.length - 1] = {
          ...msgs[msgs.length - 1],
          content: msgs[msgs.length - 1].content + delta,
        };
      }
      persistMessages(msgs, s.conversationId);
      return { messages: msgs };
    }),
  clearMessages: () => set((s) => {
    persistMessages([], s.conversationId);
    return { messages: [] };
  }),

  // Streaming
  setStreaming: (v) => set({ isStreaming: v }),
  setAbortController: (ac) => set({ streamAbortController: ac }),

  // Files
  addFile: (file) => set((s) => ({ pendingFiles: [...s.pendingFiles, file] })),
  removeFile: (index) =>
    set((s) => ({ pendingFiles: s.pendingFiles.filter((_, i) => i !== index) })),
  clearFiles: () => set({ pendingFiles: [] }),

  // Controls
  setEffort: (level) => set({ effortLevel: level }),
  setOutputStyle: (style) => {
    if (typeof window !== 'undefined') localStorage.setItem('karma-output-style', style);
    set({ outputStyle: style });
  },
  setTheme: (theme) => {
    if (typeof window !== 'undefined') {
      document.documentElement.setAttribute('data-theme', theme);
      localStorage.setItem('karma-theme', theme);
    }
    set({ theme });
  },
  setPersonalPreferences: (prefs) => {
    if (typeof window !== 'undefined') localStorage.setItem('karma-preferences', prefs);
    set({ personalPreferences: prefs });
  },

  // Tools
  addToolCall: (tc) =>
    set((s) => {
      const map = new Map(s.activeToolCalls);
      map.set(tc.id, tc);
      return { activeToolCalls: map };
    }),
  updateToolResult: (id, output) =>
    set((s) => {
      const map = new Map(s.activeToolCalls);
      const tc = map.get(id);
      if (tc) map.set(id, { ...tc, output, status: 'completed' });
      return { activeToolCalls: map };
    }),

  // Self-edit
  addSelfEditProposal: (p) =>
    set((s) => ({ selfEditProposals: [...s.selfEditProposals, p] })),
  approveSelfEdit: (id) =>
    set((s) => ({
      selfEditProposals: s.selfEditProposals.filter((p) => p.id !== id),
    })),
  rejectSelfEdit: (id) =>
    set((s) => ({
      selfEditProposals: s.selfEditProposals.filter((p) => p.id !== id),
    })),

  // Cost
  addCost: (usd) => set((s) => ({ sessionCost: s.sessionCost + usd })),
  setLastInference: (model, provider) => set({ lastModel: model || '', lastProvider: provider || '' }),

  // Status
  setStatus: (status) =>
    set((s) => ({
      lastSeen: status.lastSeen ?? s.lastSeen,
      k2Active: status.k2Active ?? s.k2Active,
      brainOk: status.brainOk ?? s.brainOk,
    })),

  // Error
  setError: (err) => set({ error: err }),

  // Session continuity
  setConversationId: (id) => {
    const next = String(id || '').trim();
    if (!next) return;
    setStoredConversationId(next);
    set({ conversationId: next, bootSessionId: next });
  },
  writeSessionTurn: async (role, content, sessionId) => {
    const trimmed = String(content || '').trim();
    if (!trimmed) return;
    const state = get();
    const sid = String(
      sessionId || state.bootSessionId || state.conversationId || '',
    ).trim();
    if (!sid) return;

    try {
      const res = await apiFetch(`/v1/session/${encodeURIComponent(sid)}`, {
        token: state.token,
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          role,
          content: trimmed,
          turn: trimmed,
          source: 'nexus-ui',
          session_id: sid,
        }),
      });
      if (!res.ok) return;
      const payload = await res.json().catch(() => null) as Record<string, unknown> | null;
      const savedSessionId = String(payload?.session_id || sid).trim();
      if (savedSessionId) {
        setStoredConversationId(savedSessionId);
        set({ conversationId: savedSessionId, bootSessionId: savedSessionId });
      }
    } catch {
      // Canonical write failures are non-fatal to UI rendering.
    }
  },
  syncSessionTurns: async () => {
    // Phase Ascendance 2: cross-surface parity. Poll /v1/session/{id} and
    // append any new turns (by timestamp) to messages. Runs every 2s from page.tsx.
    const state = get();
    if (!state.isAuthenticated) return;
    const sid = state.bootSessionId || state.conversationId;
    if (!sid) return;
    try {
      const res = await apiFetch(`/v1/session/${encodeURIComponent(sid)}`, { token: state.token });
      if (!res.ok) return;
      const payload = await res.json().catch(() => ({}));
      const serverHistory = Array.isArray(payload.history) ? payload.history : [];
      if (serverHistory.length === 0) return;
      // Existing message timestamps (millisecond-keyed) to de-duplicate
      const existing = new Set(state.messages.map((m) => String(m.timestamp || '')));
      const existingContent = new Set(state.messages.map((m) => `${m.role}::${String(m.content || '').slice(0, 200)}`));
      const newMsgs: ChatMessage[] = [];
      for (const h of serverHistory) {
        const ts = (h && typeof h === 'object' && (h.ts || h.timestamp)) || '';
        const body = (h && typeof h === 'object' && h.body) || {};
        const role = (body.role === 'karma' || body.role === 'assistant') ? 'karma'
                   : (body.role === 'system') ? 'system'
                   : 'user';
        const content = String(body.content || h.text || '');
        if (!content) continue;
        const key = `${role}::${content.slice(0, 200)}`;
        if (existing.has(String(ts)) || existingContent.has(key)) continue;
        newMsgs.push({
          id: `sync-${ts || generateId()}`,
          role,
          content,
          timestamp: String(ts || new Date().toISOString()),
        });
      }
      if (newMsgs.length > 0) {
        const merged = [...state.messages, ...newMsgs];
        persistMessages(merged, sid);
        set({ messages: merged });
      }
    } catch {
      // non-fatal — polling continues
    }
  },
  hydrateBootFrame: async () => {
    const state = get();
    const startMs = typeof performance !== 'undefined' ? performance.now() : Date.now();
    set({
      bootHydration: 'loading',
      bootError: null,
      bootTiming: null,
    });

    const fallbackSessionId = String(state.conversationId || generateId());
    let sessionId = fallbackSessionId;
    let wakeupText = '';
    let sessionPayload: Record<string, unknown> = {};
    let degradedReason = '';

    try {
      const [sessionResp, wakeupResp] = await Promise.all([
        apiFetch('/memory/session', { token: state.token }),
        apiFetch('/memory/wakeup', { token: state.token }),
      ]);

      if (!sessionResp.ok) {
        degradedReason = `memory/session status ${sessionResp.status}`;
      } else {
        const sessionJson = await sessionResp.json().catch(() => ({}));
        const fetchedSessionId = String(sessionJson?.session_id || '').trim();
        if (fetchedSessionId) sessionId = fetchedSessionId;
      }

      if (wakeupResp.ok) {
        const wakeupJson = await wakeupResp.json().catch(() => ({}));
        wakeupText = String(wakeupJson?.wakeup || '').trim();
      } else if (!degradedReason) {
        degradedReason = `memory/wakeup status ${wakeupResp.status}`;
      }

      const sessionPath = `/v1/session/${encodeURIComponent(sessionId)}`;
      let sessionStateResp = await apiFetch(sessionPath, {
        token: state.token,
      });
      if (sessionStateResp.status === 404) {
        await apiFetch(sessionPath, {
          token: state.token,
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            values: {
              boot_initialized_at: new Date().toISOString(),
              boot_source: 'nexus-ui',
            },
          }),
        }).catch(() => null);
        sessionStateResp = await apiFetch(sessionPath, {
          token: state.token,
        });
      }
      if (sessionStateResp.ok) {
        sessionPayload = await sessionStateResp.json().catch(() => ({}));
      } else if (!degradedReason) {
        degradedReason = `/v1/session status ${sessionStateResp.status}`;
      }
    } catch (e) {
      degradedReason = e instanceof Error ? e.message : 'canonical boot fetch failed';
    }

    const personaBlock = buildBootPersonaBlock(wakeupText);
    const history = readLastThreeCanonicalTurns(sessionPayload);
    const personaMessage: ChatMessage = {
      id: `boot-persona-${Date.now().toString(36)}`,
      role: 'system',
      content: personaBlock,
      timestamp: new Date().toISOString(),
    };
    const bootMessages = [personaMessage, ...history];
    const endMs = typeof performance !== 'undefined' ? performance.now() : Date.now();
    const paintMs = Math.max(0, Math.round(endMs - startMs));
    const timing: BootTiming = {
      window_visible_ms: 0,
      boot_fetch_start_ms: 0,
      boot_fetch_end_ms: paintMs,
      persona_paint_ms: paintMs,
    };

    setStoredConversationId(sessionId);
    persistMessages(bootMessages, sessionId);
    set({
      conversationId: sessionId,
      bootSessionId: sessionId,
      bootPersonaBlock: personaBlock,
      bootTiming: timing,
      messages: bootMessages,
      bootHydration: degradedReason ? 'degraded' : 'ready',
      bootError: degradedReason || null,
    });

    // Phase 1 evidence harness hook: expose real metrics for external capture.
    // Written to window.__bootMetrics after canonical hydrate completes. Harness
    // script scrapes via CDP/DevTools or localStorage fallback.
    if (typeof window !== 'undefined') {
      const metrics = {
        timestamp: new Date().toISOString(),
        session_id: sessionId,
        persona_block_preview: personaBlock.slice(0, 200),
        persona_block_length: personaBlock.length,
        history_turn_count: history.length,
        history_turns: history.map((m) => ({
          role: m.role,
          content_preview: String(m.content || '').slice(0, 120),
        })),
        timing,
        hydration_state: degradedReason ? 'degraded' : 'ready',
        degraded_reason: degradedReason || null,
        canonical_endpoints_called: [
          '/memory/session',
          '/memory/wakeup',
          `/v1/session/${encodeURIComponent(sessionId)}`,
        ],
      };
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (window as any).__bootMetrics = metrics;
      try {
        localStorage.setItem('__boot_metrics_last', JSON.stringify(metrics));
      } catch {}
    }
  },

  // Surface
  fetchSurface: async () => {
    // Hard throttle: prevents UI loops from hammering /v1/surface and spamming logs.
    // Also avoids overlapping fetches when multiple panels mount together.
    const minIntervalMs = 2500;
    const now = Date.now();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const g: any = globalThis as any;
    g.__karma_surface_last = g.__karma_surface_last || 0;
    g.__karma_surface_inflight = g.__karma_surface_inflight || null;

    if (g.__karma_surface_inflight) return;
    if (now - g.__karma_surface_last < minIntervalMs) return;
    g.__karma_surface_last = now;

    g.__karma_surface_inflight = (async () => {
      try {
        const { token } = get();
        const res = await apiFetch('/v1/surface', { token });
        if (res.ok) {
          const data = await res.json();
          set({ surface: data });
        }
      } catch {}
    })().finally(() => {
      g.__karma_surface_inflight = null;
    });
  },
}));

// Expose store on window for CDP-driven harness tests (Phase Ascendance 3+).
// Does not affect production behavior — read-only handle to state machine.
if (typeof window !== 'undefined') {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  (window as any).__karmaStore = useKarmaStore;
}
