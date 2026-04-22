'use client';

import { useState, useEffect } from 'react';
import { useKarmaStore } from '@/store/karma';
import { apiFetch } from '@/lib/api';

interface TodoItem {
  id?: string;
  content: string;
  status: 'pending' | 'in_progress' | 'completed' | 'rejected';
  source?: string;
  updated_at?: string;
}

interface Primitive {
  id: string;
  title: string;
  source: string;
  preview?: string;
  primitives?: string[];
  what?: string;
  impact_if_merged?: string;
  dismiss_reason?: string;
  updated_at?: string;
  size_kb?: number;
  relevance: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'pending' | 'approved' | 'rejected' | 'merged' | 'dismissed';
}

export function WipPanel({ onClose }: { onClose: () => void }) {
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [primitives, setPrimitives] = useState<Primitive[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'todos' | 'primitives'>('todos');
  const [newTodo, setNewTodo] = useState('');
  const token = useKarmaStore((s) => s.token);

  useEffect(() => {
    loadData();
  }, [token]);

  async function loadData() {
    setLoading(true);
    try {
      const res = await apiFetch('/v1/wip', { token }).catch(() => null);

      if (res?.ok) {
        const data = await res.json();
        if (data.todos) setTodos(data.todos);
        if (data.primitives) setPrimitives(data.primitives);

        // If state-backed todos are empty, project pending coordination tasks as WIP rows.
        if ((!Array.isArray(data.todos) || data.todos.length === 0)) {
          const busRes = await apiFetch('/v1/coordination/recent?limit=20', { token }).catch(() => null);
          if (busRes?.ok) {
            const busData = await busRes.json();
            const entries = Array.isArray(busData.entries) ? busData.entries : [];
            const busTodos: TodoItem[] = entries
              .filter((e: Record<string, unknown>) => e && (e.status === 'pending' || e.status === 'open'))
              .slice(0, 20)
              .map((e: Record<string, unknown>) => ({
                content: `${String(e.from || 'unknown')} → ${String(e.to || 'unknown')}: ${String(e.content || '').slice(0, 120)}`,
                status: 'pending',
                source: 'coordination',
              }));
            if (busTodos.length) setTodos(busTodos);
          }
        }
      }
    } catch {}
    setLoading(false);
  }

  async function approvePrimitive(id: string) {
    // Send approval to CC via bus
    try {
      await apiFetch('/v1/coordination/post', {
        method: 'POST',
        token,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          from: 'sovereign',
          to: 'cc',
          type: 'directive',
          urgency: 'normal',
          content: `APPROVE primitive ${id} for surgical merge. Julian: choose optimal method and execute.`,
        }),
      });
      await setPrimitiveStatus(id, 'approved');
    } catch {}
  }

  async function rejectPrimitive(id: string) {
    await setPrimitiveStatus(id, 'rejected');
  }

  async function setPrimitiveStatus(id: string, status: Primitive['status']) {
    try {
      await apiFetch('/v1/wip/primitive-status', {
        method: 'POST',
        token,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, status }),
      });
      setPrimitives(prev => prev.map(p => p.id === id ? { ...p, status } : p));
    } catch {}
  }

  async function setTodoStatus(todo: TodoItem, status: TodoItem['status']) {
    try {
      await apiFetch('/v1/wip/todo-status', {
        method: 'POST',
        token,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: todo.id, content: todo.content, status }),
      });
      setTodos((prev) => prev.map((t) => {
        const sameId = todo.id && t.id && todo.id === t.id;
        const sameContent = !todo.id && t.content === todo.content;
        return (sameId || sameContent) ? { ...t, status } : t;
      }));
    } catch {}
  }

  async function addTodo() {
    const content = newTodo.trim();
    if (!content) return;
    try {
      await apiFetch('/v1/wip/todo-add', {
        method: 'POST',
        token,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content }),
      });
      setNewTodo('');
      await loadData();
    } catch {}
  }

  const statusIcon = (s: string) => {
    if (s === 'completed' || s === 'merged') return '\u2713';
    if (s === 'in_progress') return '\u25B6';
    if (s === 'rejected') return '\u2717';
    return '\u25CB';
  };

  const statusColor = (s: string) => {
    if (s === 'completed' || s === 'merged' || s === 'approved') return 'text-karma-accent2';
    if (s === 'in_progress') return 'text-karma-accent';
    if (s === 'rejected' || s === 'dismissed') return 'text-karma-danger';
    return 'text-karma-muted';
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="bg-karma-surface border border-karma-border w-[560px] max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-karma-border">
          <div className="flex items-center gap-3">
            <span className="text-karma-accent text-[11px] tracking-[2px] font-bold">WIP</span>
            <div className="flex gap-1">
              {(['todos', 'primitives'] as const).map(t => (
                <button
                  key={t}
                  className={`px-2 py-0.5 text-[9px] tracking-[1px] border cursor-pointer
                    ${tab === t ? 'border-karma-accent text-karma-accent bg-karma-accent/10' : 'border-karma-border text-karma-muted bg-transparent'}`}
                  onClick={() => setTab(t)}
                >
                  {t.toUpperCase()}
                </button>
              ))}
            </div>
            <button
              onClick={loadData}
              className="px-2 py-0.5 text-[9px] border border-karma-border text-karma-muted hover:text-karma-accent cursor-pointer bg-transparent"
            >
              REFRESH
            </button>
          </div>
          <button onClick={onClose} className="text-karma-muted hover:text-karma-danger cursor-pointer bg-transparent border-none">x</button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-3 text-[11px]">
          {loading ? (
            <div className="text-karma-muted text-center p-4">Loading...</div>
          ) : tab === 'todos' ? (
            <div className="flex flex-col gap-1">
              <div className="flex items-center gap-2 mb-2">
                <input
                  className="flex-1 bg-karma-bg border border-karma-border text-karma-text px-2 py-1 text-[10px] font-mono outline-none focus:border-karma-accent placeholder:text-karma-border"
                  placeholder="Add a todo..."
                  value={newTodo}
                  onChange={(e) => setNewTodo(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addTodo()}
                />
                <button
                  onClick={addTodo}
                  disabled={!newTodo.trim()}
                  className="px-2 py-1 text-[9px] border border-karma-accent text-karma-accent bg-transparent hover:bg-karma-accent/20 cursor-pointer disabled:opacity-40"
                >
                  ADD
                </button>
              </div>
              {todos.length === 0 ? (
                <div className="text-karma-muted text-center p-4">
                  No active todos. Julian is either idle or between tasks.
                  <br />
                  <span className="text-[9px]">Todos update dynamically during CC sessions.</span>
                </div>
              ) : (
                todos.map((t, i) => (
                  <div key={i} className="flex items-center gap-2 px-2 py-1 hover:bg-karma-bg">
                  <span className={`${statusColor(t.status)} text-[10px]`}>{statusIcon(t.status)}</span>
                    <span className={(t.status === 'completed' || t.status === 'rejected') ? 'line-through text-karma-muted' : 'text-karma-text'}>{t.content}</span>
                    {t.source && <span className="text-[9px] text-karma-muted ml-auto">{t.source}</span>}
                    <div className="flex items-center gap-1 ml-auto">
                      <button onClick={() => setTodoStatus(t, 'pending')} className="px-1.5 py-0.5 text-[8px] border border-karma-border text-karma-muted hover:border-karma-accent cursor-pointer bg-transparent">PEND</button>
                      <button onClick={() => setTodoStatus(t, 'in_progress')} className="px-1.5 py-0.5 text-[8px] border border-karma-border text-karma-muted hover:border-karma-accent cursor-pointer bg-transparent">DO</button>
                      <button onClick={() => setTodoStatus(t, 'completed')} className="px-1.5 py-0.5 text-[8px] border border-karma-accent text-karma-accent hover:bg-karma-accent/20 cursor-pointer bg-transparent">DONE</button>
                      <button onClick={() => setTodoStatus(t, 'rejected')} className="px-1.5 py-0.5 text-[8px] border border-karma-danger text-karma-danger hover:bg-karma-danger/20 cursor-pointer bg-transparent">NO</button>
                    </div>
                  </div>
                ))
              )}
            </div>
          ) : (
            <div className="flex flex-col gap-2">
              {primitives.length === 0 ? (
                <div className="text-karma-muted text-center p-4">
                  No primitives pending review.
                  <br />
                  <span className="text-[9px]">Drop files in docs/wip/ or use /primitives to extract from URLs.</span>
                </div>
              ) : (
                primitives.map((p) => (
                  <div key={p.id} className="border border-karma-border rounded p-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-karma-text font-mono">{p.title}</span>
                      <span className={`text-[9px] tracking-[1px] ${
                        p.relevance === 'HIGH' ? 'text-karma-accent' :
                        p.relevance === 'MEDIUM' ? 'text-yellow-400' : 'text-karma-muted'
                      }`}>{p.relevance}</span>
                    </div>
                    <div className="text-[9px] text-karma-muted">{p.source}{p.size_kb ? ` (${p.size_kb}KB)` : ''}</div>
                    {p.what && <div className="text-[9px] text-karma-accent mt-1">WHAT: <span className="text-karma-text">{p.what}</span></div>}
                    {p.impact_if_merged && <div className="text-[9px] text-karma-accent2 mt-0.5">IMPACT: <span className="text-karma-text">{p.impact_if_merged}</span></div>}
                    {Array.isArray(p.primitives) && p.primitives.length > 0 && (
                      <div className="text-[9px] text-karma-text/70 mt-1">
                        {p.primitives.slice(0, 3).map((line, idx) => (
                          <div key={idx}>- {line}</div>
                        ))}
                      </div>
                    )}
                    {p.dismiss_reason && <div className="text-[9px] text-karma-danger mt-0.5">DISMISS: {p.dismiss_reason}</div>}
                    {!p.what && p.preview && <div className="text-[9px] text-karma-text/60 mt-0.5 line-clamp-2">{p.preview}</div>}
                    {p.status === 'pending' ? (
                      <div className="flex gap-2 justify-end">
                        <button
                          onClick={() => rejectPrimitive(p.id)}
                          className="px-2 py-0.5 text-[9px] border border-karma-border text-karma-muted hover:border-karma-danger hover:text-karma-danger cursor-pointer bg-transparent"
                        >NO</button>
                        <button
                          onClick={() => approvePrimitive(p.id)}
                          className="px-2 py-0.5 text-[9px] border border-karma-accent text-karma-accent hover:bg-karma-accent/20 cursor-pointer bg-transparent"
                        >YES \u2192 MERGE</button>
                      </div>
                    ) : (
                      <div className={`text-[9px] text-right ${statusColor(p.status)}`}>
                        {p.status.toUpperCase()}
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-4 py-2 border-t border-karma-border text-[9px] text-karma-muted">
          {tab === 'todos'
            ? `${todos.filter(t => t.status === 'completed').length}/${todos.length} complete`
            : `${primitives.filter(p => p.status === 'approved' || p.status === 'merged').length}/${primitives.length} approved`}
        </div>
      </div>
    </div>
  );
}
