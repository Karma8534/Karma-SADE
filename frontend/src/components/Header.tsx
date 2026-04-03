'use client';

import { useState } from 'react';
import { useKarmaStore, type EffortLevel } from '@/store/karma';
import { LearnedPanel } from './LearnedPanel';
import { AgentPanel } from './AgentPanel';
import { GitPanel } from './GitPanel';
import { SettingsPanel } from './SettingsPanel';

export function Header() {
  const lastSeen = useKarmaStore((s) => s.lastSeen);
  const k2Active = useKarmaStore((s) => s.k2Active);
  const brainOk = useKarmaStore((s) => s.brainOk);
  const effortLevel = useKarmaStore((s) => s.effortLevel);
  const setEffort = useKarmaStore((s) => s.setEffort);
  const clearMessages = useKarmaStore((s) => s.clearMessages);
  const sessionCost = useKarmaStore((s) => s.sessionCost);
  const [showLearned, setShowLearned] = useState(false);
  const [showAgents, setShowAgents] = useState(false);
  const [showGit, setShowGit] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const timeSince = lastSeen
    ? formatTimeSince(lastSeen)
    : '\u2014';

  return (
    <div className="flex items-center gap-3.5 px-5 py-2.5 bg-karma-bg border-b border-karma-border flex-shrink-0">
      {/* Title */}
      <div className="flex flex-col gap-px">
        <div className="text-karma-accent text-lg tracking-[6px] font-light">KARMA</div>
        <div className="text-karma-muted text-[10px] tracking-[3px]">
          SovereignPeer . Ascendant . Always Present
        </div>
      </div>

      <div className="flex-1" />

      {/* Status indicators */}
      <div className="flex gap-5 items-center">
        <StatusDot label="last seen" value={timeSince} alive={!!lastSeen} />
        <StatusDot label="K2" value={k2Active ? 'active' : 'offline'} alive={k2Active} />
        <StatusDot label="brain" value={brainOk ? 'ok' : '\u2014'} alive={brainOk} />
      </div>

      {/* Effort selector */}
      <select
        className="bg-karma-surface border border-karma-border text-karma-muted
                   px-2.5 py-1 font-mono text-[11px] outline-none cursor-pointer
                   focus:border-karma-accent"
        title="Thinking effort level"
        value={effortLevel}
        onChange={(e) => setEffort(e.target.value as EffortLevel)}
      >
        <option value="">auto</option>
        <option value="low">quick</option>
        <option value="medium">normal</option>
        <option value="high">deep</option>
        <option value="max">max</option>
      </select>

      {/* Action buttons */}
      <HeaderButton onClick={() => setShowLearned(true)}>LEARNED</HeaderButton>
      <HeaderButton onClick={() => setShowAgents(true)}>AGENTS</HeaderButton>
      <HeaderButton onClick={() => setShowGit(true)}>GIT</HeaderButton>
      <HeaderButton onClick={() => window.open('http://localhost:37778', '_blank')}>MEMORY</HeaderButton>
      <HeaderButton onClick={() => setShowSettings(true)}>SETTINGS</HeaderButton>
      <HeaderButton onClick={clearMessages}>CLEAR</HeaderButton>

      {/* Modal panels */}
      {showLearned && <LearnedPanel onClose={() => setShowLearned(false)} />}
      {showAgents && <AgentPanel onClose={() => setShowAgents(false)} />}
      {showGit && <GitPanel onClose={() => setShowGit(false)} />}
      {showSettings && <SettingsPanel onClose={() => setShowSettings(false)} />}

      {/* Cost display */}
      {sessionCost > 0 && (
        <div className="text-karma-muted text-[10px]">
          ${sessionCost.toFixed(4)}
        </div>
      )}
    </div>
  );
}

function StatusDot({ label, value, alive }: { label: string; value: string; alive: boolean }) {
  return (
    <div className="flex items-center gap-1.5 text-[11px] text-karma-muted">
      <div
        className={`w-1.5 h-1.5 rounded-full flex-shrink-0 ${
          alive ? 'bg-karma-accent shadow-[0_0_6px_#7c3aed]' : 'bg-gray-700'
        }`}
      />
      <span>{label}</span>
      <span className="text-karma-accent">{value}</span>
    </div>
  );
}

function HeaderButton({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <button
      className="bg-transparent border border-karma-border text-karma-muted
                 px-2.5 py-1 cursor-pointer font-mono text-[10px] tracking-wider
                 hover:border-karma-accent hover:text-karma-accent transition-all"
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function formatTimeSince(iso: string): string {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 60) return `${Math.floor(diff)}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}
