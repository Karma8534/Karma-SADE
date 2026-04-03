'use client';

import React, { useState, useEffect } from 'react';
import { useKarmaStore, type EffortLevel } from '@/store/karma';

type SettingsTab = 'general' | 'model' | 'hooks' | 'mcp' | 'permissions';

export function SettingsPanel({ onClose }: { onClose: () => void }) {
  const [tab, setTab] = useState<SettingsTab>('general');
  const effortLevel = useKarmaStore((s) => s.effortLevel);
  const setEffort = useKarmaStore((s) => s.setEffort);
  const theme = useKarmaStore((s) => s.theme);
  const setTheme = useKarmaStore((s) => s.setTheme);
  const personalPreferences = useKarmaStore((s) => s.personalPreferences);
  const setPersonalPreferences = useKarmaStore((s) => s.setPersonalPreferences);
  const surface = useKarmaStore((s) => s.surface);
  const fetchSurface = useKarmaStore((s) => s.fetchSurface);

  useEffect(() => { if (!surface) fetchSurface(); }, [surface, fetchSurface]);

  const tabs: { id: SettingsTab; label: string }[] = [
    { id: 'general', label: 'GENERAL' },
    { id: 'model', label: 'MODEL' },
    { id: 'hooks', label: 'HOOKS' },
    { id: 'mcp', label: 'MCP' },
    { id: 'permissions', label: 'PERMISSIONS' },
  ];

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="bg-karma-surface border border-karma-border w-[560px] max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-karma-border">
          <span className="text-karma-accent text-[11px] tracking-[2px] font-bold">SETTINGS</span>
          <button onClick={onClose} className="text-karma-muted hover:text-karma-danger cursor-pointer bg-transparent border-none">x</button>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Tab sidebar */}
          <div className="w-[120px] border-r border-karma-border py-2 flex-shrink-0">
            {tabs.map((t) => (
              <button
                key={t.id}
                className={`block w-full text-left px-3 py-1.5 text-[10px] tracking-[1px] border-none cursor-pointer
                           ${tab === t.id ? 'bg-karma-bg text-karma-accent' : 'bg-transparent text-karma-muted hover:text-karma-text'}`}
                onClick={() => setTab(t.id)}
              >
                {t.label}
              </button>
            ))}
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 text-[11px]">
            {tab === 'general' && (
              <div className="flex flex-col gap-3">
                <div className="text-karma-accent font-bold mb-1">Effort Level</div>
                <div className="flex gap-1">
                  {(['', 'low', 'medium', 'high', 'max'] as EffortLevel[]).map((level) => (
                    <button
                      key={level || 'auto'}
                      className={`px-2 py-1 text-[10px] border cursor-pointer
                                 ${effortLevel === level
                                   ? 'border-karma-accent text-karma-accent bg-karma-accent/10'
                                   : 'border-karma-border text-karma-muted bg-transparent hover:text-karma-text'}`}
                      onClick={() => setEffort(level)}
                    >
                      {level || 'auto'}
                    </button>
                  ))}
                </div>
                <div className="text-karma-muted text-[9px]">
                  Controls CC reasoning depth. auto = model decides. max = extended thinking.
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Theme</div>
                <div className="flex gap-1">
                  {(['dark', 'light'] as const).map((t) => (
                    <button
                      key={t}
                      className={`px-2 py-1 text-[10px] border cursor-pointer
                                 ${theme === t
                                   ? 'border-karma-accent text-karma-accent bg-karma-accent/10'
                                   : 'border-karma-border text-karma-muted bg-transparent hover:text-karma-text'}`}
                      onClick={() => setTheme(t)}
                    >
                      {t}
                    </button>
                  ))}
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Personal Preferences</div>
                <textarea
                  className="w-full bg-karma-bg border border-karma-border text-karma-text text-[10px] p-2 resize-y min-h-[60px] outline-none focus:border-karma-accent"
                  placeholder="Tell Karma about yourself — preferences, context, working style. This is injected into every conversation."
                  value={personalPreferences}
                  onChange={(e) => setPersonalPreferences(e.target.value)}
                  rows={3}
                />
                <div className="text-karma-muted text-[9px]">
                  Injected as context into every conversation. Helps Karma understand your preferences.
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Keyboard Shortcuts</div>
                <div className="grid grid-cols-2 gap-1 text-[10px]">
                  <span className="text-karma-muted">Send message</span><span className="font-mono">Enter</span>
                  <span className="text-karma-muted">New line</span><span className="font-mono">Shift+Enter</span>
                  <span className="text-karma-muted">Cancel/Stop</span><span className="font-mono">Esc</span>
                  <span className="text-karma-muted">Commands</span><span className="font-mono">/</span>
                </div>
              </div>
            )}

            {tab === 'model' && (
              <div className="flex flex-col gap-2">
                <div className="text-karma-accent font-bold mb-1">Active Model</div>
                <div className="text-karma-text font-mono">cc-sovereign (Max subscription, $0/request)</div>
                <div className="text-karma-muted text-[9px] mt-1">
                  CC --resume uses your Max subscription. No per-request API cost.
                  EscapeHatch: CC rate limit → OpenRouter (sonnet) → gemini-flash → nexus_agent.
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Inference Tiers</div>
                <div className="grid grid-cols-2 gap-1 text-[10px]">
                  <span className="text-karma-muted">Tier 0:</span><span>K2 Ollama (qwen3.5:4b, $0)</span>
                  <span className="text-karma-muted">Tier 1:</span><span>CC --resume (Max sub, $0)</span>
                  <span className="text-karma-muted">Tier 2:</span><span>OpenRouter (sonnet, fallback)</span>
                  <span className="text-karma-muted">Tier 3:</span><span>nexus_agent (own loop)</span>
                </div>
              </div>
            )}

            {tab === 'hooks' && (
              <div className="flex flex-col gap-2">
                <div className="text-karma-accent font-bold mb-1">Active Hooks</div>
                {(surface?.hooks?.list as { name: string; event: string }[] || []).length > 0 ? (
                  (surface?.hooks?.list as { name: string; event: string }[]).map((h, i) => (
                    <div key={i} className="flex items-center gap-2 px-2 py-1 bg-karma-bg rounded">
                      <span className="text-karma-accent2 text-[9px]">{h.event}</span>
                      <span className="text-karma-text">{h.name}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-karma-muted">No hooks data. Refresh surface.</div>
                )}
              </div>
            )}

            {tab === 'mcp' && (
              <div className="flex flex-col gap-2">
                <div className="text-karma-accent font-bold mb-1">MCP Servers</div>
                <div className="text-karma-muted text-[9px] mb-2">CC manages MCP servers natively. This view is read-only.</div>
                {((surface?.agents as Record<string, unknown>)?.mcp_servers as string[] || []).length > 0 ? (
                  ((surface?.agents as Record<string, unknown>)?.mcp_servers as string[]).map((s, i) => (
                    <div key={i} className="flex items-center gap-2 px-2 py-1 bg-karma-bg rounded text-[10px]">
                      <span className="text-karma-accent2">●</span>
                      <span className="text-karma-text font-mono">{s}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-karma-muted">No MCP server data.</div>
                )}
              </div>
            )}

            {tab === 'permissions' && (
              <div className="flex flex-col gap-2">
                <div className="text-karma-accent font-bold mb-1">Permission Rules</div>
                <div className="text-karma-muted text-[9px] mb-2">Tool permission levels. Managed via CC settings.</div>
                <div className="grid grid-cols-3 gap-1 text-[10px]">
                  <span className="text-karma-muted font-bold">Tool</span>
                  <span className="text-karma-muted font-bold">Level</span>
                  <span className="text-karma-muted font-bold">Status</span>
                  {[
                    { tool: 'Read/Glob/Grep', level: 'allow', status: 'auto' },
                    { tool: 'Write/Edit', level: 'gate', status: 'logged' },
                    { tool: 'Bash/Shell', level: 'gate', status: 'logged' },
                    { tool: 'SelfEdit', level: 'gate', status: 'logged' },
                    { tool: 'WebFetch', level: 'ask', status: 'confirm' },
                  ].map((r, i) => (
                    <React.Fragment key={i}>
                      <span className="text-karma-text font-mono">{r.tool}</span>
                      <span className={r.level === 'allow' ? 'text-karma-accent2' : r.level === 'gate' ? 'text-yellow-400' : 'text-karma-accent'}>{r.level}</span>
                      <span className="text-karma-muted">{r.status}</span>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
