'use client';

import { useState, useEffect } from 'react';
import { useKarmaStore } from '@/store/karma';

interface TodoItem {
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
}

interface Primitive {
  id: string;
  title: string;
  source: string;
  relevance: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'pending' | 'approved' | 'rejected' | 'merged';
}

export function WipPanel({ onClose }: { onClose: () => void }) {
  const [todos, setTodos] = useState<TodoItem[]>([]);
  const [primitives, setPrimitives] = useState<Primitive[]>([]);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState<'todos' | 'primitives'>('todos');
  const token = useKarmaStore((s) => s.token);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      // Fetch active todos from surface/status
      const statusRes = await fetch('/v1/status', {
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => null);

      if (statusRes?.ok) {
        const data = await statusRes.json();
        // Parse todos if available from CC state
        if (data.todos) {
          setTodos(data.todos);
        }
      }

      // Fetch primitives from claude-mem or gap map
      // For now, show gap map MISSING items as primitives to assimilate
      const surfaceRes = await fetch('/v1/surface', {
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => null);

      if (surfaceRes?.ok) {
        const surface = await surfaceRes.json();
        // Extract any pending primitives from surface state
        if (surface.primitives) {
          setPrimitives(surface.primitives);
        }
      }
    } catch {}
    setLoading(false);
  }

  async function approvePrimitive(id: string) {
    // Send approval to CC via bus
    try {
      await fetch('/v1/coordination/post', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          from: 'sovereign',
          to: 'cc',
          type: 'directive',
          urgency: 'normal',
          content: `APPROVE primitive ${id} for surgical merge. Julian: choose optimal method and execute.`,
        }),
      });
      setPrimitives(prev => prev.map(p => p.id === id ? { ...p, status: 'approved' } : p));
    } catch {}
  }

  async function rejectPrimitive(id: string) {
    setPrimitives(prev => prev.map(p => p.id === id ? { ...p, status: 'rejected' } : p));
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
    if (s === 'rejected') return 'text-karma-danger';
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
          </div>
          <button onClick={onClose} className="text-karma-muted hover:text-karma-danger cursor-pointer bg-transparent border-none">x</button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-3 text-[11px]">
          {loading ? (
            <div className="text-karma-muted text-center p-4">Loading...</div>
          ) : tab === 'todos' ? (
            <div className="flex flex-col gap-1">
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
                    <span className={t.status === 'completed' ? 'line-through text-karma-muted' : 'text-karma-text'}>{t.content}</span>
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
                    <div className="text-[9px] text-karma-muted mb-2">{p.source}</div>
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
          {tab === 'todos' ? `${todos.filter(t => t.status === 'completed').length}/${todos.length} complete` : `${primitives.filter(p => p.status === 'approved' || p.status === 'merged').length}/${primitives.length} approved`}
        </div>
      </div>
    </div>
  );
}
