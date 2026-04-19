'use client';

import { useState, useEffect, useCallback } from 'react';
import { useKarmaStore } from '@/store/karma';
import { apiFetch } from '@/lib/api';

interface AgentInfo {
  id: string;
  name: string;
  status: 'running' | 'idle' | 'error' | 'cancelled';
  lastSeen?: string;
  detail?: string;
  meta?: Record<string, unknown>;
  spawnId?: string; // tracked agent_id for cancellation
}

interface SpawnedAgent {
  id: string;
  name: string;
  target: string;
  prompt: string;
  started_at: string;
  status: string;
  bus_id?: string;
}

export function AgentPanel({ onClose }: { onClose: () => void }) {
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [newTask, setNewTask] = useState('');
  const [taskTarget, setTaskTarget] = useState('cc');
  const [postingTask, setPostingTask] = useState(false);
  const [taskPosted, setTaskPosted] = useState(false);
  const [loadError, setLoadError] = useState('');
  const token = useKarmaStore((s) => s.token);

  const load = useCallback(async () => {
    try {
      setLoadError('');
      const auth = token?.trim() ? { token } : {};
      const [surfaceRes, busRes, spineRes, policyRes, spawnedRes] = await Promise.all([
        apiFetch('/v1/surface', auth).catch(() => null),
        apiFetch('/v1/coordination/recent?limit=20', auth).catch(() => null),
        apiFetch('/v1/spine', auth).catch(() => null),
        apiFetch('/v1/model-policy', auth).catch(() => null),
        apiFetch('/v1/agents/list', auth).catch(() => null),
      ]);

      const agentList: AgentInfo[] = [];

      const knownAgents = [
        { name: 'CC/Julian (P1)', key: 'cc' },
        { name: 'KCC (K2)', key: 'kcc' },
        { name: 'Codex (P1)', key: 'codex' },
        { name: 'Karma (persistent)', key: 'karma' },
        { name: 'Kiki (K2)', key: 'kiki' },
        { name: 'Vesper (K2)', key: 'regent' },
      ];

      let busEntries: { from?: string; created_at?: string; content?: string; id?: string; to?: string; status?: string; urgency?: string }[] = [];
      if (busRes?.ok) {
        const busData = await busRes.json();
        busEntries = Array.isArray(busData.entries) ? busData.entries : [];
      }

      for (const agent of knownAgents) {
        const recent = busEntries.find((e) => e.from === agent.key || e.to === agent.key);
        if (recent) {
          const age = recent.created_at ? (Date.now() - new Date(recent.created_at).getTime()) / 1000 : Number.MAX_SAFE_INTEGER;
          agentList.push({
            id: agent.key,
            name: agent.name,
            status: age < 900 ? 'running' : 'idle', // 15min threshold
            lastSeen: recent.created_at ? new Date(recent.created_at).toLocaleTimeString() : 'unknown',
            detail: String(recent.content || '').slice(0, 80),
            meta: recent as Record<string, unknown>,
          });
        } else {
          agentList.push({
            id: agent.key,
            name: agent.name,
            status: 'idle',
            detail: 'No recent bus entries',
            meta: { info: 'No recent coordination entries for this agent in the current window.' },
          });
        }
      }

      let spineData: Record<string, unknown> = {};
      if (spineRes?.ok) {
        const spine = await spineRes.json();
        spineData = (spine?.spine || {}) as Record<string, unknown>;
        agentList.push({
          id: 'spine',
          name: 'Vesper Spine',
          status: spine?.ok ? 'running' : 'error',
          detail: `v${String(spineData.version ?? '?')} · ${String(spineData.stable_patterns ?? '?')} stable`,
          meta: spineData,
        });
      }

      if (policyRes?.ok) {
        const policy = await policyRes.json();
        agentList.push({
          id: 'mouth-policy',
          name: 'Mouth Policy',
          status: policy?.mouth ? 'running' : 'error',
          detail: `${String(policy?.mouth || 'unknown')} · ${String(policy?.primary_model || 'n/a')}`,
          meta: policy as Record<string, unknown>,
        });
      }

      if (surfaceRes?.ok) {
        const surface = await surfaceRes.json();
        const skillCount = surface.skills?.names?.length || 0;
        const hookCount = surface.hooks?.list?.length || 0;
        if (skillCount) agentList.push({ id: 'skills', name: `Skills (${skillCount})`, status: 'running', detail: (surface.skills?.names || []).slice(0, 5).join(', '), meta: { skills: surface.skills?.names || [] } });
        if (hookCount) agentList.push({ id: 'hooks', name: `Hooks (${hookCount})`, status: 'running', detail: (surface.hooks?.list || []).slice(0, 3).map((h: { name: string }) => h.name).join(', '), meta: { hooks: surface.hooks?.list || [] } });
      }

      const activeTasks = busEntries.filter((e) => e.status === 'pending' || e.status === 'open');
      const recentTasks = busEntries.slice(0, 10);
      agentList.push({
        id: 'tasks',
        name: `Coord Tasks (${activeTasks.length})`,
        status: recentTasks.length > 0 ? 'running' : 'idle',
        detail: recentTasks[0]?.content ? String(recentTasks[0].content).slice(0, 80) : 'No task payloads',
        meta: { active: activeTasks, recent: recentTasks },
      });

      // Spawned agents (lifecycle-tracked)
      if (spawnedRes?.ok) {
        const spawnedData = await spawnedRes.json();
        const spawned: SpawnedAgent[] = Array.isArray(spawnedData.agents) ? spawnedData.agents : [];
        for (const sp of spawned) {
          agentList.push({
            id: `spawn-${sp.id}`,
            spawnId: sp.id,
            name: `${sp.name} → ${sp.target}`,
            status: sp.status === 'running' ? 'running' : sp.status === 'cancelled' ? 'cancelled' : 'idle',
            lastSeen: sp.started_at ? new Date(sp.started_at).toLocaleTimeString() : undefined,
            detail: sp.prompt?.slice(0, 100),
            meta: sp as unknown as Record<string, unknown>,
          });
        }
      }

      setAgents(agentList);
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : 'failed to load');
    }
    setLoading(false);
  }, [token]);

  useEffect(() => {
    setLoading(true);
    load();
  }, [load]);

  async function submitTask() {
    const content = newTask.trim();
    if (!content) return;
    setPostingTask(true);
    setTaskPosted(false);
    try {
      // /v1/agents/spawn posts to bus AND registers in spawn registry for cancel tracking
      await apiFetch('/v1/agents/spawn', {
        method: 'POST',
        token,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `task-${Date.now().toString(36)}`,
          target: taskTarget,
          prompt: content,
        }),
      });
      setNewTask('');
      setTaskPosted(true);
      setTimeout(() => setTaskPosted(false), 2000);
      await load();
    } catch {
      // ignore
    }
    setPostingTask(false);
  }

  async function cancelSpawn(spawnId: string) {
    try {
      await apiFetch(`/v1/agents/cancel/${encodeURIComponent(spawnId)}`, {
        method: 'POST',
        token,
      });
      await load();
    } catch {
      // ignore
    }
  }

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

        <div className="px-3 py-2 border-b border-karma-border">
          <div className="text-[9px] text-karma-muted tracking-[1px] mb-1">ADD TASK</div>
          <div className="flex items-center gap-2">
            <select
              value={taskTarget}
              onChange={(e) => setTaskTarget(e.target.value)}
              className="bg-karma-bg border border-karma-border text-karma-text text-[10px] px-2 py-1 outline-none focus:border-karma-accent"
            >
              <option value="cc">cc</option>
              <option value="karma">karma</option>
              <option value="codex">codex</option>
              <option value="kcc">kcc</option>
              <option value="regent">regent</option>
              <option value="all">all</option>
            </select>
            <input
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && submitTask()}
              placeholder="Type a task for the bus..."
              className="flex-1 bg-karma-bg border border-karma-border text-karma-text px-2 py-1 text-[10px] font-mono outline-none focus:border-karma-accent placeholder:text-karma-border"
            />
            <button
              onClick={submitTask}
              disabled={postingTask || !newTask.trim()}
              className="px-2 py-1 text-[10px] border border-karma-accent text-karma-accent bg-transparent hover:bg-karma-accent/20 cursor-pointer disabled:opacity-40"
            >
              {postingTask ? '...' : 'POST'}
            </button>
          </div>
          <div className="mt-1 text-[9px] text-karma-muted">
            {taskPosted ? 'Spawned. Tracked for cancel via /v1/agents/cancel/{id}.' : 'Spawns via /v1/agents/spawn (bus + lifecycle registry).'}
          </div>
        </div>

        {loading ? (
          <div className="p-4 text-karma-muted text-[11px]">Loading...</div>
        ) : (
          <div className="p-2">
            {loadError && <div className="px-2 py-1 text-[10px] text-karma-danger border-b border-karma-border/30">{loadError}</div>}
            {agents.map((a, i) => (
              <div
                key={a.id || String(i)}
                className="px-2 py-1.5 hover:bg-karma-bg text-[11px] cursor-pointer border-b border-karma-border/20"
                onClick={() => setExpanded(expanded === (a.id || String(i)) ? null : (a.id || String(i)))}
              >
                <div className="flex items-start gap-2">
                <span className={`${statusColor(a.status)} text-[8px] mt-0.5`}>{statusIcon(a.status)}</span>
                <div className="flex-1 min-w-0">
                  <div className="text-karma-text font-mono">{a.name}</div>
                  {a.lastSeen && <div className="text-karma-muted text-[9px]">last seen {a.lastSeen}</div>}
                  {a.detail && <div className="text-karma-muted text-[9px] truncate">{a.detail}</div>}
                </div>
                  {a.spawnId && a.status === 'running' && (
                    <button
                      onClick={(e) => { e.stopPropagation(); cancelSpawn(a.spawnId!); }}
                      className="text-[9px] px-1.5 py-0.5 border border-karma-danger text-karma-danger hover:bg-karma-danger/20 cursor-pointer"
                      title="Cancel this spawned agent task"
                    >
                      STOP
                    </button>
                  )}
                  <span className="text-karma-muted text-[9px]">{expanded === (a.id || String(i)) ? '▼' : '▶'}</span>
                </div>
                {expanded === (a.id || String(i)) && a.meta && (
                  <pre className="mt-1.5 text-[9px] text-karma-muted whitespace-pre-wrap break-all bg-karma-bg border border-karma-border rounded p-2">
                    {JSON.stringify(a.meta, null, 2)}
                  </pre>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
