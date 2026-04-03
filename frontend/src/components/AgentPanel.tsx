'use client';

import { useState, useEffect } from 'react';
import { useKarmaStore } from '@/store/karma';

interface AgentInfo {
  name: string;
  status: 'running' | 'idle' | 'error';
  lastSeen?: string;
  detail?: string;
}

export function AgentPanel({ onClose }: { onClose: () => void }) {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const token = useKarmaStore((s) => s.token);

  useEffect(() => {
    async function load() {
      try {
        // Fetch from surface (agents key) + coordination bus for live agent status
        const [surfaceRes, busRes] = await Promise.all([
          fetch('/v1/surface', { headers: { Authorization: `Bearer ${token}` } }).catch(() => null),
          fetch('/v1/coordination/recent?limit=20', { headers: { Authorization: `Bearer ${token}` } }).catch(() => null),
        ]);

        const agentList: AgentInfo[] = [];

        // Known agents from architecture
        const knownAgents = [
          { name: 'CC/Julian (P1)', key: 'cc' },
          { name: 'KCC (K2)', key: 'kcc' },
          { name: 'Codex (P1)', key: 'codex' },
          { name: 'Karma (persistent)', key: 'karma' },
          { name: 'Kiki (K2)', key: 'kiki' },
          { name: 'Vesper (K2)', key: 'regent' },
        ];

        // Check bus for recent heartbeats
        let busEntries: { from: string; created_at: string; content: string }[] = [];
        if (busRes?.ok) {
          const busData = await busRes.json();
          busEntries = busData.entries || [];
        }

        for (const agent of knownAgents) {
          const recent = busEntries.find((e) => e.from === agent.key);
          if (recent) {
            const age = (Date.now() - new Date(recent.created_at).getTime()) / 1000;
            agentList.push({
              name: agent.name,
              status: age < 900 ? 'running' : 'idle', // 15min threshold
              lastSeen: new Date(recent.created_at).toLocaleTimeString(),
              detail: recent.content.slice(0, 80),
            });
          } else {
            agentList.push({ name: agent.name, status: 'idle' });
          }
        }

        // Add skills + hooks count from surface
        if (surfaceRes?.ok) {
          const surface = await surfaceRes.json();
          const skillCount = surface.skills?.names?.length || 0;
          const hookCount = surface.hooks?.list?.length || 0;
          if (skillCount) agentList.push({ name: `Skills (${skillCount})`, status: 'running', detail: (surface.skills?.names || []).slice(0, 5).join(', ') });
          if (hookCount) agentList.push({ name: `Hooks (${hookCount})`, status: 'running', detail: (surface.hooks?.list || []).slice(0, 3).map((h: { name: string }) => h.name).join(', ') });
        }

        setAgents(agentList);
      } catch {}
      setLoading(false);
    }
    load();
  }, [token]);

  const statusIcon = (s: string) => {
    if (s === 'running') return '\u25CF'; // filled circle
    if (s === 'error') return '\u25CF';
    return '\u25CB'; // hollow circle
  };
  const statusColor = (s: string) => {
    if (s === 'running') return 'text-karma-accent2';
    if (s === 'error') return 'text-karma-danger';
    return 'text-karma-muted';
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="bg-karma-surface border border-karma-border w-[480px] max-h-[70vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-2 border-b border-karma-border">
          <span className="text-karma-accent text-[11px] tracking-[2px] font-bold">AGENTS & TASKS</span>
          <button onClick={onClose} className="text-karma-muted hover:text-karma-danger cursor-pointer bg-transparent border-none">x</button>
        </div>

        {loading ? (
          <div className="p-4 text-karma-muted text-[11px]">Loading...</div>
        ) : (
          <div className="p-2">
            {agents.map((a, i) => (
              <div key={i} className="flex items-start gap-2 px-2 py-1.5 hover:bg-karma-bg text-[11px]">
                <span className={`${statusColor(a.status)} text-[8px] mt-0.5`}>{statusIcon(a.status)}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-karma-text font-mono">{a.name}</div>
                  {a.lastSeen && <div className="text-karma-muted text-[9px]">last seen {a.lastSeen}</div>}
                  {a.detail && <div className="text-karma-muted text-[9px] truncate">{a.detail}</div>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
