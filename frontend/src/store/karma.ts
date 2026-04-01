import { create } from 'zustand';

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

  // Tool tracking (for stream)
  activeToolCalls: Map<string, ToolCall>;

  // Self-edit
  selfEditProposals: SelfEditProposal[];

  // Cost
  sessionCost: number;

  // Status
  lastSeen: string;
  k2Active: boolean;
  brainOk: boolean;
  error: string | null;

  // Actions
  setToken: (token: string) => void;
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
  addToolCall: (tc: ToolCall) => void;
  updateToolResult: (id: string, output: string) => void;
  addSelfEditProposal: (p: SelfEditProposal) => void;
  approveSelfEdit: (id: number) => void;
  rejectSelfEdit: (id: number) => void;
  addCost: (usd: number) => void;
  setStatus: (status: { lastSeen?: string; k2Active?: boolean; brainOk?: boolean }) => void;
  setError: (err: string | null) => void;
  clearMessages: () => void;
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

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
  activeToolCalls: new Map(),
  selfEditProposals: [],
  sessionCost: 0,
  lastSeen: '',
  k2Active: false,
  brainOk: false,
  error: null,

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
  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),
  updateLastMessage: (content) =>
    set((s) => {
      const msgs = [...s.messages];
      if (msgs.length > 0) msgs[msgs.length - 1] = { ...msgs[msgs.length - 1], content };
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
      return { messages: msgs };
    }),
  clearMessages: () => set({ messages: [] }),

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

  // Status
  setStatus: (status) =>
    set((s) => ({
      lastSeen: status.lastSeen ?? s.lastSeen,
      k2Active: status.k2Active ?? s.k2Active,
      brainOk: status.brainOk ?? s.brainOk,
    })),

  // Error
  setError: (err) => set({ error: err }),
}));
