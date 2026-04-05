'use client';

import React, { useState, useEffect } from 'react';
import { useKarmaStore, type EffortLevel } from '@/store/karma';

type SettingsTab = 'general' | 'model' | 'privacy' | 'hooks' | 'permissions' | 'plugins' | 'advanced';

type Provider = 'anthropic-max' | 'groq' | 'k2-ollama' | 'p1-ollama' | 'openrouter';

const PROVIDERS: { id: Provider; label: string; desc: string }[] = [
  { id: 'anthropic-max', label: 'Anthropic (Max $0)', desc: 'CC --resume via Max subscription. Primary.' },
  { id: 'groq', label: 'Groq (Free)', desc: 'llama-3.3-70b. Fast fallback. Free tier.' },
  { id: 'k2-ollama', label: 'K2 Ollama ($0)', desc: 'qwen3.5:4b on K2. Local. 32K context.' },
  { id: 'p1-ollama', label: 'P1 Ollama ($0)', desc: 'LFM2 350M. 0.1s routing. Classification only.' },
  { id: 'openrouter', label: 'OpenRouter', desc: 'Multi-model. EscapeHatch fallback.' },
];

const OUTPUT_STYLES = ['auto', 'concise', 'detailed', 'technical', 'creative'];
const LANGUAGES = ['english', 'spanish', 'french', 'german', 'japanese', 'portuguese', 'chinese', 'korean'];

export function SettingsPanel({ onClose }: { onClose: () => void }) {
  const [tab, setTab] = useState<SettingsTab>('general');
  const effortLevel = useKarmaStore((s) => s.effortLevel);
  const setEffort = useKarmaStore((s) => s.setEffort);
  const theme = useKarmaStore((s) => s.theme);
  const setTheme = useKarmaStore((s) => s.setTheme);
  const outputStyle = useKarmaStore((s) => s.outputStyle);
  const setOutputStyle = useKarmaStore((s) => s.setOutputStyle);
  const personalPreferences = useKarmaStore((s) => s.personalPreferences);
  const setPersonalPreferences = useKarmaStore((s) => s.setPersonalPreferences);
  const surface = useKarmaStore((s) => s.surface);
  const fetchSurface = useKarmaStore((s) => s.fetchSurface);

  // Local state for settings that persist to localStorage
  const [primaryProvider, setPrimaryProvider] = useState<Provider>(() =>
    (typeof window !== 'undefined' ? localStorage.getItem('karma-primary-provider') : null) as Provider || 'anthropic-max'
  );
  const [fallbackProvider, setFallbackProvider] = useState<Provider>(() =>
    (typeof window !== 'undefined' ? localStorage.getItem('karma-fallback-provider') : null) as Provider || 'groq'
  );
  const [language, setLanguage] = useState(() =>
    typeof window !== 'undefined' ? localStorage.getItem('karma-language') || 'english' : 'english'
  );
  const [thinkingEnabled, setThinkingEnabled] = useState(() =>
    typeof window !== 'undefined' ? localStorage.getItem('karma-thinking') !== 'false' : true
  );
  const [promptSuggestions, setPromptSuggestions] = useState(() =>
    typeof window !== 'undefined' ? localStorage.getItem('karma-prompt-suggestions') !== 'false' : true
  );

  useEffect(() => { if (!surface) fetchSurface(); }, [surface, fetchSurface]);

  const saveSetting = (key: string, value: string) => {
    if (typeof window !== 'undefined') localStorage.setItem(key, value);
  };

  const tabs: { id: SettingsTab; label: string }[] = [
    { id: 'general', label: 'GENERAL' },
    { id: 'model', label: 'MODEL' },
    { id: 'privacy', label: 'PRIVACY' },
    { id: 'hooks', label: 'HOOKS' },
    { id: 'permissions', label: 'PERMISSIONS' },
    { id: 'plugins', label: 'PLUGINS' },
    { id: 'advanced', label: 'ADVANCED' },
  ];

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="bg-karma-surface border border-karma-border w-[600px] max-h-[85vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
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

            {/* ── GENERAL ─────────────────────────────────────────── */}
            {tab === 'general' && (
              <div className="flex flex-col gap-3">
                <div className="text-karma-accent font-bold mb-1">Effort Level</div>
                <div className="flex gap-1">
                  {(['', 'low', 'medium', 'high', 'max'] as EffortLevel[]).map((level) => (
                    <button key={level || 'auto'}
                      className={`px-2 py-1 text-[10px] border cursor-pointer ${effortLevel === level ? 'border-karma-accent text-karma-accent bg-karma-accent/10' : 'border-karma-border text-karma-muted bg-transparent hover:text-karma-text'}`}
                      onClick={() => setEffort(level)}
                    >{level || 'auto'}</button>
                  ))}
                </div>
                <div className="text-karma-muted text-[9px]">Controls reasoning depth. auto = model decides. max = extended thinking.</div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Theme</div>
                <div className="flex gap-1">
                  {(['dark', 'light'] as const).map((t) => (
                    <button key={t}
                      className={`px-2 py-1 text-[10px] border cursor-pointer ${theme === t ? 'border-karma-accent text-karma-accent bg-karma-accent/10' : 'border-karma-border text-karma-muted bg-transparent hover:text-karma-text'}`}
                      onClick={() => setTheme(t)}
                    >{t}</button>
                  ))}
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Output Style</div>
                <select className="bg-karma-bg border border-karma-border text-karma-text text-[10px] px-2 py-1 outline-none cursor-pointer focus:border-karma-accent"
                  value={outputStyle} onChange={(e) => setOutputStyle(e.target.value as typeof outputStyle)}>
                  {OUTPUT_STYLES.map((s) => <option key={s} value={s === 'auto' ? '' : s}>{s}</option>)}
                </select>
                <div className="text-karma-muted text-[9px]">concise = short answers. detailed = thorough. technical = code-focused. creative = expressive.</div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Language</div>
                <select className="bg-karma-bg border border-karma-border text-karma-text text-[10px] px-2 py-1 outline-none cursor-pointer focus:border-karma-accent"
                  value={language} onChange={(e) => { setLanguage(e.target.value); saveSetting('karma-language', e.target.value); }}>
                  {LANGUAGES.map((l) => <option key={l} value={l}>{l}</option>)}
                </select>

                <div className="text-karma-accent font-bold mt-3 mb-1">Extended Thinking</div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={thinkingEnabled} onChange={(e) => { setThinkingEnabled(e.target.checked); saveSetting('karma-thinking', String(e.target.checked)); }}
                    className="accent-karma-accent" />
                  <span className="text-karma-text text-[10px]">Enable extended thinking (deeper reasoning, slower)</span>
                </label>

                <div className="text-karma-accent font-bold mt-3 mb-1">Prompt Suggestions</div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={promptSuggestions} onChange={(e) => { setPromptSuggestions(e.target.checked); saveSetting('karma-prompt-suggestions', String(e.target.checked)); }}
                    className="accent-karma-accent" />
                  <span className="text-karma-text text-[10px]">Show suggested prompts when idle</span>
                </label>

                <div className="text-karma-accent font-bold mt-3 mb-1">Personal Preferences</div>
                <textarea className="w-full bg-karma-bg border border-karma-border text-karma-text text-[10px] p-2 resize-y min-h-[60px] outline-none focus:border-karma-accent"
                  placeholder="Tell Karma about yourself — preferences, context, working style."
                  value={personalPreferences} onChange={(e) => setPersonalPreferences(e.target.value)} rows={3} />
                <div className="text-karma-muted text-[9px]">Injected into every conversation.</div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Keyboard Shortcuts</div>
                <div className="grid grid-cols-2 gap-1 text-[10px]">
                  <span className="text-karma-muted">Send</span><span className="font-mono">Enter</span>
                  <span className="text-karma-muted">New line</span><span className="font-mono">Shift+Enter</span>
                  <span className="text-karma-muted">Cancel</span><span className="font-mono">Esc</span>
                  <span className="text-karma-muted">Commands</span><span className="font-mono">/</span>
                  <span className="text-karma-muted">Search</span><span className="font-mono">Ctrl+K</span>
                </div>
              </div>
            )}

            {/* ── MODEL / PROVIDER ────────────────────────────────── */}
            {tab === 'model' && (
              <div className="flex flex-col gap-3">
                <div className="text-karma-accent font-bold mb-1">Primary Provider</div>
                <select className="bg-karma-bg border border-karma-border text-karma-text text-[10px] px-2 py-1 outline-none cursor-pointer focus:border-karma-accent w-full"
                  value={primaryProvider} onChange={(e) => { const v = e.target.value as Provider; setPrimaryProvider(v); saveSetting('karma-primary-provider', v); }}>
                  {PROVIDERS.map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
                </select>
                <div className="text-karma-muted text-[9px]">
                  {PROVIDERS.find(p => p.id === primaryProvider)?.desc}
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Fallback Provider</div>
                <select className="bg-karma-bg border border-karma-border text-karma-text text-[10px] px-2 py-1 outline-none cursor-pointer focus:border-karma-accent w-full"
                  value={fallbackProvider} onChange={(e) => { const v = e.target.value as Provider; setFallbackProvider(v); saveSetting('karma-fallback-provider', v); }}>
                  {PROVIDERS.filter(p => p.id !== primaryProvider).map((p) => <option key={p.id} value={p.id}>{p.label}</option>)}
                </select>
                <div className="text-karma-muted text-[9px]">
                  Used when primary is unavailable, rate-limited, or session-locked.
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Inference Cascade</div>
                <div className="bg-karma-bg border border-karma-border rounded p-2 text-[10px]">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-karma-accent2">1.</span>
                    <span className="text-karma-text">{PROVIDERS.find(p => p.id === primaryProvider)?.label}</span>
                    <span className="text-karma-muted text-[9px]">primary</span>
                  </div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-yellow-400">2.</span>
                    <span className="text-karma-text">{PROVIDERS.find(p => p.id === fallbackProvider)?.label}</span>
                    <span className="text-karma-muted text-[9px]">fallback</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-karma-muted">3.</span>
                    <span className="text-karma-muted">K2 Cortex (always available, $0)</span>
                    <span className="text-karma-muted text-[9px]">last resort</span>
                  </div>
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Available Models</div>
                <div className="grid grid-cols-3 gap-1 text-[10px]">
                  <span className="text-karma-muted font-bold">Provider</span>
                  <span className="text-karma-muted font-bold">Model</span>
                  <span className="text-karma-muted font-bold">Cost</span>
                  <span className="text-karma-text">Anthropic</span><span className="font-mono">claude-sonnet-4-6</span><span className="text-karma-accent2">$0 (Max)</span>
                  <span className="text-karma-text">Groq</span><span className="font-mono">llama-3.3-70b</span><span className="text-karma-accent2">$0 (free)</span>
                  <span className="text-karma-text">K2 Ollama</span><span className="font-mono">qwen3.5:4b</span><span className="text-karma-accent2">$0</span>
                  <span className="text-karma-text">P1 Ollama</span><span className="font-mono">LFM2-350M</span><span className="text-karma-accent2">$0</span>
                  <span className="text-karma-text">OpenRouter</span><span className="font-mono">configurable</span><span className="text-yellow-400">varies</span>
                </div>
              </div>
            )}

            {/* ── PRIVACY ─────────────────────────────────────────── */}
            {tab === 'privacy' && (
              <div className="flex flex-col gap-3">
                <div className="text-karma-accent font-bold mb-1">Data Persistence</div>
                <div className="text-karma-muted text-[9px] mb-2">Controls what Karma remembers between conversations.</div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" defaultChecked className="accent-karma-accent" />
                  <span className="text-karma-text text-[10px]">Save conversations to transcript</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" defaultChecked className="accent-karma-accent" />
                  <span className="text-karma-text text-[10px]">Auto-save to claude-mem (cross-session memory)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" defaultChecked className="accent-karma-accent" />
                  <span className="text-karma-text text-[10px]">Sync to vault-neo spine (permanent record)</span>
                </label>

                <div className="text-karma-accent font-bold mt-3 mb-1">Content Filtering</div>
                <div className="text-karma-muted text-[9px] mb-2">Wrap sensitive content in {'<private>'} tags to prevent persistence.</div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" defaultChecked className="accent-karma-accent" />
                  <span className="text-karma-text text-[10px]">Strip {'<private>'} tags before saving to memory</span>
                </label>

                <div className="text-karma-accent font-bold mt-3 mb-1">Injection Protection</div>
                <div className="text-karma-muted text-[9px]">
                  Permission engine detects 7 injection patterns (identity hijack, instruction override, jailbreak attempts).
                  Runs OUTSIDE context window — cannot be overridden by prompt injection.
                </div>
              </div>
            )}

            {/* ── HOOKS ───────────────────────────────────────────── */}
            {tab === 'hooks' && (
              <div className="flex flex-col gap-2">
                <div className="text-karma-accent font-bold mb-1">Active Hooks</div>
                <div className="text-karma-muted text-[9px] mb-2">Lifecycle event handlers. Fire before/after tool execution, session events.</div>
                {(surface?.hooks?.list as { name: string; event: string }[] || []).length > 0 ? (
                  (surface?.hooks?.list as { name: string; event: string }[]).map((h, i) => (
                    <div key={i} className="flex items-center gap-2 px-2 py-1 bg-karma-bg rounded">
                      <span className="text-karma-accent2 text-[9px] font-mono w-[100px]">{h.event}</span>
                      <span className="text-karma-text">{h.name}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-karma-muted">No hooks data. Click refresh below.</div>
                )}
                <button onClick={fetchSurface} className="text-[9px] px-2 py-1 border border-karma-border text-karma-muted bg-transparent hover:border-karma-accent cursor-pointer mt-2 w-fit">
                  REFRESH
                </button>
              </div>
            )}

            {/* ── PERMISSIONS ─────────────────────────────────────── */}
            {tab === 'permissions' && (
              <div className="flex flex-col gap-2">
                <div className="text-karma-accent font-bold mb-1">Permission Rules (42 rules + 7 injection patterns)</div>
                <div className="text-karma-muted text-[9px] mb-2">Zero-trust model. Unrecognized commands default-deny. Hot-reloadable from config/permission_rules.json.</div>
                <div className="grid grid-cols-3 gap-1 text-[10px]">
                  <span className="text-karma-muted font-bold">Category</span>
                  <span className="text-karma-muted font-bold">Action</span>
                  <span className="text-karma-muted font-bold">Count</span>
                  {[
                    { cat: 'Safe read ops', action: 'allow', count: 'Read, Glob, Grep, ls, cat' },
                    { cat: 'Git operations', action: 'allow', count: 'status, log, diff, commit, push' },
                    { cat: 'Shell execution', action: 'allow', count: 'python, npm, ssh, curl (known hosts)' },
                    { cat: 'File operations', action: 'allow', count: 'mkdir, cp, mv, touch, chmod' },
                    { cat: 'Docker ops', action: 'allow', count: 'logs, ps, inspect, compose' },
                    { cat: 'Destructive commands', action: 'deny', count: 'rm -rf, format, dd, mkfs, fork bomb' },
                    { cat: 'Secret exposure', action: 'deny', count: 'cat .env, echo token/password' },
                    { cat: 'Unsafe network', action: 'deny', count: 'curl|sh, wget|sh' },
                    { cat: 'System admin', action: 'deny', count: 'passwd, iptables, crontab -r' },
                    { cat: 'Write to system dirs', action: 'deny', count: 'C:\\Windows, /etc/, /usr/' },
                    { cat: 'Unknown Bash', action: 'deny', count: 'Default deny (fail-closed)' },
                  ].map((r, i) => (
                    <React.Fragment key={i}>
                      <span className="text-karma-text">{r.cat}</span>
                      <span className={r.action === 'allow' ? 'text-karma-accent2' : 'text-karma-danger'}>{r.action}</span>
                      <span className="text-karma-muted text-[9px]">{r.count}</span>
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )}

            {/* ── PLUGINS ─────────────────────────────────────────── */}
            {tab === 'plugins' && (
              <div className="flex flex-col gap-2">
                <div className="text-karma-accent font-bold mb-1">Plugin System</div>
                <div className="text-karma-muted text-[9px] mb-2">Drop a directory with manifest.json in plugins/. Auto-discovered on load.</div>

                <div className="text-karma-accent font-bold mt-2 mb-1">Trust Levels</div>
                <div className="grid grid-cols-2 gap-1 text-[10px]">
                  <span className="text-karma-accent2 font-bold">local</span><span className="text-karma-muted">Created by family. Full access.</span>
                  <span className="text-yellow-400 font-bold">verified</span><span className="text-karma-muted">Sovereign-approved. Gated access.</span>
                  <span className="text-karma-danger font-bold">untrusted</span><span className="text-karma-muted">Third-party. Sandboxed. No shell/network.</span>
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Installed Plugins</div>
                <div className="px-2 py-1 bg-karma-bg rounded text-[10px]">
                  <span className="text-karma-accent2">●</span> gap-tracker v1.0.0 <span className="text-karma-muted">[local]</span> — gap_status, gap_missing
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">MCP Servers</div>
                {((surface?.agents as Record<string, unknown>)?.mcp_servers as string[] || []).length > 0 ? (
                  ((surface?.agents as Record<string, unknown>)?.mcp_servers as string[]).map((s, i) => (
                    <div key={i} className="flex items-center gap-2 px-2 py-1 bg-karma-bg rounded text-[10px]">
                      <span className="text-karma-accent2">●</span>
                      <span className="text-karma-text font-mono">{s}</span>
                    </div>
                  ))
                ) : (
                  <div className="text-karma-muted text-[10px]">No MCP servers detected.</div>
                )}
              </div>
            )}

            {/* ── ADVANCED ────────────────────────────────────────── */}
            {tab === 'advanced' && (
              <div className="flex flex-col gap-3">
                <div className="text-karma-accent font-bold mb-1">Infrastructure</div>
                <div className="grid grid-cols-2 gap-1 text-[10px]">
                  <span className="text-karma-muted">P1 (PAYBACK)</span><span className="text-karma-text">cc_server:7891, claude-mem:37778</span>
                  <span className="text-karma-muted">K2 (Julian)</span><span className="text-karma-text">cortex:7892, Ollama:11434</span>
                  <span className="text-karma-muted">vault-neo</span><span className="text-karma-text">hub-bridge, karma-server, FalkorDB</span>
                  <span className="text-karma-muted">Hub URL</span><span className="text-karma-text font-mono">hub.arknexus.net</span>
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Diagnostics</div>
                <div className="text-karma-muted text-[9px]">Use /doctor command for full system diagnostics. Use /stats for live metrics.</div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Data Paths</div>
                <div className="grid grid-cols-2 gap-1 text-[9px]">
                  <span className="text-karma-muted">MEMORY.md</span><span className="font-mono text-karma-text">MEMORY.md (repo root)</span>
                  <span className="text-karma-muted">STATE.md</span><span className="font-mono text-karma-text">.gsd/STATE.md</span>
                  <span className="text-karma-muted">Transcripts</span><span className="font-mono text-karma-text">tmp/transcripts/*.jsonl</span>
                  <span className="text-karma-muted">Consolidation DB</span><span className="font-mono text-karma-text">tmp/consolidation.db</span>
                  <span className="text-karma-muted">Permission rules</span><span className="font-mono text-karma-text">config/permission_rules.json</span>
                  <span className="text-karma-muted">Plugins</span><span className="font-mono text-karma-text">plugins/*/manifest.json</span>
                </div>

                <div className="text-karma-accent font-bold mt-3 mb-1">Version</div>
                <div className="text-karma-muted text-[10px]">Nexus v5.3.0 | S160 | 44 commands | 42+7 permission rules</div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}
