'use client';

import { useState, useEffect, useCallback } from 'react';
import { useKarmaStore } from '@/store/karma';

type Tab = 'files' | 'memory' | 'agents' | 'preview';

interface FileNode {
  name: string;
  type: 'file' | 'dir';
  path: string;
  size?: number;
  children?: FileNode[];
}

interface MemoryItem {
  id: number;
  title: string;
  created_at: string;
  text?: string;
}

export function ContextPanel() {
  const [isOpen, setIsOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<Tab>('files');
  const [width, setWidth] = useState(320);

  if (!isOpen) {
    return (
      <button
        className="fixed right-0 top-1/2 -translate-y-1/2 bg-karma-surface border border-karma-border
                   border-r-0 text-karma-muted px-1 py-4 cursor-pointer hover:text-karma-accent
                   hover:border-karma-accent text-[10px] writing-mode-vertical"
        style={{ writingMode: 'vertical-rl' }}
        onClick={() => setIsOpen(true)}
      >
        CONTEXT
      </button>
    );
  }

  return (
    <div
      className="flex flex-col border-l border-karma-border bg-karma-bg flex-shrink-0 h-full"
      style={{ width }}
    >
      {/* Tab bar */}
      <div className="flex border-b border-karma-border flex-shrink-0">
        {(['files', 'memory', 'agents', 'preview'] as Tab[]).map((tab) => (
          <button
            key={tab}
            className={`flex-1 py-1.5 text-[10px] tracking-wider cursor-pointer border-none
                       ${activeTab === tab
                         ? 'bg-karma-surface text-karma-accent border-b-2 border-karma-accent'
                         : 'bg-karma-bg text-karma-muted hover:text-karma-text'}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.toUpperCase()}
          </button>
        ))}
        <button
          className="px-2 text-karma-muted hover:text-karma-danger cursor-pointer bg-transparent border-none text-[12px]"
          onClick={() => setIsOpen(false)}
        >
          x
        </button>
      </div>

      {/* Tab content */}
      <div className="flex-1 overflow-y-auto p-2 text-[11px]">
        {activeTab === 'files' && <FileTreeTab />}
        {activeTab === 'memory' && <MemoryTab />}
        {activeTab === 'agents' && <AgentTab />}
        {activeTab === 'preview' && <PreviewTab />}
      </div>
    </div>
  );
}

// ── File Tree Tab ─────────────────────────────────────────────────────────────

function FileTreeTab() {
  const [tree, setTree] = useState<FileNode[]>([]);
  const [loading, setLoading] = useState(true);
  const token = useKarmaStore((s) => s.token);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/v1/files', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (data.ok) setTree(data.tree || []);
      } catch {
        // ignore
      }
      setLoading(false);
    }
    load();
  }, [token]);

  if (loading) return <div className="text-karma-muted">Loading files...</div>;

  return (
    <div>
      {tree.map((node) => (
        <FileTreeNode key={node.path} node={node} depth={0} />
      ))}
    </div>
  );
}

function FileTreeNode({ node, depth }: { node: FileNode; depth: number }) {
  const [expanded, setExpanded] = useState(depth < 1);

  const indent = depth * 12;

  if (node.type === 'dir') {
    return (
      <div>
        <div
          className="flex items-center gap-1 py-0.5 cursor-pointer text-karma-muted hover:text-karma-accent"
          style={{ paddingLeft: indent }}
          onClick={() => setExpanded(!expanded)}
        >
          <span className="text-[10px]">{expanded ? '\u25BC' : '\u25B6'}</span>
          <span>{node.name}/</span>
        </div>
        {expanded && node.children?.map((child) => (
          <FileTreeNode key={child.path} node={child} depth={depth + 1} />
        ))}
      </div>
    );
  }

  return (
    <div
      className="py-0.5 cursor-pointer text-karma-text hover:text-karma-accent hover:bg-karma-surface"
      style={{ paddingLeft: indent + 16 }}
      onClick={() => {
        // Send "Read <path>" to chat
        const store = useKarmaStore.getState();
        store.addMessage({
          id: Date.now().toString(36),
          role: 'user',
          content: `Read ${node.path}`,
          timestamp: new Date().toISOString(),
        });
      }}
      title={`${node.path} (${formatSize(node.size || 0)})`}
    >
      {node.name}
      <span className="text-karma-muted text-[9px] ml-1">{formatSize(node.size || 0)}</span>
    </div>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes}B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}K`;
  return `${(bytes / 1024 / 1024).toFixed(1)}M`;
}

// ── Memory Tab ────────────────────────────────────────────────────────────────

function MemoryTab() {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const token = useKarmaStore((s) => s.token);

  const doSearch = useCallback(async (query: string) => {
    setLoading(true);
    try {
      const res = await fetch('/v1/memory/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ query: query || 'recent', limit: 20 }),
      });
      const data = await res.json();
      setMemories(data.results || data.observations || []);
    } catch {
      // ignore
    }
    setLoading(false);
  }, [token]);

  useEffect(() => { doSearch(''); }, [doSearch]);

  return (
    <div className="flex flex-col gap-2">
      <input
        className="bg-karma-surface border border-karma-border text-karma-text px-2 py-1
                   text-[11px] outline-none focus:border-karma-accent placeholder:text-karma-border"
        placeholder="Search memories..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && doSearch(search)}
      />
      {loading && <div className="text-karma-muted">Searching...</div>}
      {memories.map((m) => (
        <div key={m.id} className="border-b border-karma-border pb-1">
          <div className="text-karma-accent text-[10px] font-bold">{m.title}</div>
          <div className="text-karma-muted text-[9px]">{m.created_at}</div>
          {m.text && <div className="text-karma-text text-[10px] mt-0.5 line-clamp-2">{m.text}</div>}
        </div>
      ))}
    </div>
  );
}

// ── Agent Tab ─────────────────────────────────────────────────────────────────

function AgentTab() {
  const [spine, setSpine] = useState<Record<string, unknown> | null>(null);
  const [agents, setAgents] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const token = useKarmaStore((s) => s.token);

  useEffect(() => {
    async function load() {
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = `Bearer ${token}`;
      try {
        const [spineRes, agentsRes] = await Promise.all([
          fetch('/v1/spine').catch(() => null),
          fetch('/v1/agents-status', { headers }).catch(() => null),
        ]);
        if (spineRes?.ok) setSpine(await spineRes.json());
        if (agentsRes?.ok) setAgents(await agentsRes.json());
      } catch { /* ignore */ }
      setLoading(false);
    }
    load();
  }, [token]);

  if (loading) return <div className="text-karma-muted">Loading...</div>;

  const spineData = (spine?.spine as Record<string, unknown>) || {};
  const pipelineData = (spine?.pipeline as Record<string, unknown>) || {};
  const mcpServers = (agents?.mcp_servers as string[]) || [];
  const skills = (agents?.skills as string[]) || [];
  const hooks = (agents?.hooks as Record<string, string[]>) || {};

  return (
    <div className="flex flex-col gap-2 text-[10px]">
      {/* Vesper Pipeline */}
      <div className="text-karma-accent font-bold">Vesper Pipeline</div>
      <div className="grid grid-cols-2 gap-1">
        <span className="text-karma-muted">Spine:</span>
        <span className="text-karma-text">v{String(spineData.version ?? '?')} · {String(spineData.total_promotions ?? '?')} promotions</span>
        <span className="text-karma-muted">Patterns:</span>
        <span className="text-karma-text">{String(spineData.stable_patterns ?? '?')} stable</span>
        <span className="text-karma-muted">Self-improving:</span>
        <span className={spineData.self_improving ? 'text-karma-accent2' : 'text-karma-danger'}>
          {String(spineData.self_improving ?? '?')}
        </span>
      </div>

      {/* MCP Servers (#20) */}
      <div className="text-karma-accent font-bold mt-2">MCP Servers ({mcpServers.length})</div>
      {mcpServers.length > 0 ? (
        <div className="flex flex-wrap gap-1">
          {mcpServers.map((s) => (
            <span key={s} className="bg-karma-surface px-1.5 py-0.5 rounded text-karma-text border border-karma-border">{s}</span>
          ))}
        </div>
      ) : <span className="text-karma-muted">None detected</span>}

      {/* Skills (#21) */}
      <div className="text-karma-accent font-bold mt-2">Skills ({skills.length})</div>
      {skills.length > 0 ? (
        <div className="flex flex-wrap gap-1">
          {skills.map((s) => (
            <span key={s} className="bg-karma-surface px-1.5 py-0.5 rounded text-karma-text border border-karma-border">{s}</span>
          ))}
        </div>
      ) : <span className="text-karma-muted">None detected</span>}

      {/* Hooks (#22) */}
      <div className="text-karma-accent font-bold mt-2">Hooks ({Object.keys(hooks).length} events)</div>
      {Object.entries(hooks).map(([event, handlers]) => (
        <div key={event} className="ml-1">
          <span className="text-karma-accent2">{event}</span>
          <span className="text-karma-muted"> ({(handlers as string[]).length})</span>
          <div className="ml-2 text-karma-muted">
            {(handlers as string[]).map((h, i) => <div key={i}>· {h}</div>)}
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Preview Tab ───────────────────────────────────────────────────────────────

function PreviewTab() {
  const messages = useKarmaStore((s) => s.messages);

  // Find last URL or image in messages
  const lastUrl = (() => {
    for (let i = messages.length - 1; i >= 0; i--) {
      const msg = messages[i];
      const urlMatch = msg.content.match(/https?:\/\/\S+/);
      if (urlMatch) return urlMatch[0];
    }
    return null;
  })();

  if (!lastUrl) {
    return <div className="text-karma-muted text-center mt-4">No preview content yet.</div>;
  }

  return (
    <div className="flex flex-col gap-2">
      <div className="text-karma-muted text-[10px] truncate">{lastUrl}</div>
      <iframe
        src={lastUrl}
        className="w-full flex-1 min-h-[300px] border border-karma-border rounded bg-white"
        sandbox="allow-scripts allow-same-origin"
        title="Preview"
      />
    </div>
  );
}
