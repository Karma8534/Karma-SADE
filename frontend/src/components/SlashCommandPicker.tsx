'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

export interface SlashCommand {
  name: string;
  description: string;
  category: 'session' | 'tools' | 'config' | 'info' | 'dev';
  aliases?: string[];
  action?: 'prompt' | 'local';
}

const COMMANDS: SlashCommand[] = [
  // Session
  { name: 'clear', description: 'Clear conversation history', category: 'session', aliases: ['reset', 'new'] },
  { name: 'compact', description: 'Summarize and compress session context', category: 'session' },
  { name: 'export', description: 'Export conversation to file', category: 'session' },
  { name: 'resume', description: 'Resume a previous session', category: 'session', aliases: ['continue'] },

  // Tools
  { name: 'help', description: 'Show available commands', category: 'info' },
  { name: 'cost', description: 'Show session cost and duration', category: 'info' },
  { name: 'status', description: 'Show system status (P1/K2/vault-neo)', category: 'info' },
  { name: 'context', description: 'Show context window usage', category: 'info' },

  // Config
  { name: 'model', description: 'Switch model (opus/sonnet/haiku)', category: 'config' },
  { name: 'effort', description: 'Set effort level (low/medium/high/max)', category: 'config' },
  { name: 'theme', description: 'Change color theme', category: 'config' },
  { name: 'settings', description: 'Open settings panel', category: 'config' },

  // Dev
  { name: 'plan', description: 'Enter structured planning mode', category: 'dev', action: 'prompt' },
  { name: 'diff', description: 'Show recent code changes', category: 'dev', action: 'prompt' },
  { name: 'commit', description: 'Create a git commit', category: 'dev', action: 'prompt' },
  { name: 'review', description: 'Code review current changes', category: 'dev', action: 'prompt' },
  { name: 'skills', description: 'List available skills', category: 'tools' },
  { name: 'hooks', description: 'Show hook status', category: 'tools' },
  { name: 'agents', description: 'Show agent status', category: 'tools' },
  { name: 'memory', description: 'Search persistent memory', category: 'tools' },
];

const CATEGORY_LABELS: Record<string, string> = {
  session: 'SESSION',
  tools: 'TOOLS',
  config: 'CONFIG',
  info: 'INFO',
  dev: 'DEV',
};

const CATEGORY_ORDER = ['session', 'info', 'config', 'tools', 'dev'];

interface Props {
  filter: string;
  onSelect: (command: SlashCommand) => void;
  onClose: () => void;
  visible: boolean;
}

export function SlashCommandPicker({ filter, onSelect, onClose, visible }: Props) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const listRef = useRef<HTMLDivElement>(null);

  const filtered = COMMANDS.filter((cmd) => {
    const q = filter.toLowerCase();
    return (
      cmd.name.includes(q) ||
      cmd.description.toLowerCase().includes(q) ||
      cmd.aliases?.some((a) => a.includes(q)) ||
      false
    );
  });

  // Group by category
  const grouped: { category: string; commands: SlashCommand[] }[] = [];
  for (const cat of CATEGORY_ORDER) {
    const cmds = filtered.filter((c) => c.category === cat);
    if (cmds.length > 0) grouped.push({ category: cat, commands: cmds });
  }
  const flatList = grouped.flatMap((g) => g.commands);

  // Reset selection when filter changes
  useEffect(() => { setSelectedIndex(0); }, [filter]);

  // Keyboard navigation
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!visible) return;
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((i) => Math.min(i + 1, flatList.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((i) => Math.max(i - 1, 0));
      } else if (e.key === 'Enter' || e.key === 'Tab') {
        e.preventDefault();
        if (flatList[selectedIndex]) onSelect(flatList[selectedIndex]);
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    },
    [visible, flatList, selectedIndex, onSelect, onClose]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Scroll selected into view
  useEffect(() => {
    const el = listRef.current?.querySelector(`[data-index="${selectedIndex}"]`);
    el?.scrollIntoView({ block: 'nearest' });
  }, [selectedIndex]);

  if (!visible || flatList.length === 0) return null;

  let flatIdx = 0;

  return (
    <div
      className="absolute bottom-full left-0 right-0 mb-1 bg-karma-surface border border-karma-border
                 max-h-[280px] overflow-y-auto z-50 shadow-lg"
      ref={listRef}
    >
      {grouped.map((group) => (
        <div key={group.category}>
          <div className="px-3 py-1 text-[9px] tracking-[2px] text-karma-muted bg-karma-bg sticky top-0">
            {CATEGORY_LABELS[group.category] || group.category.toUpperCase()}
          </div>
          {group.commands.map((cmd) => {
            const idx = flatIdx++;
            return (
              <div
                key={cmd.name}
                data-index={idx}
                className={`px-3 py-1.5 cursor-pointer flex items-center gap-3 text-[12px]
                           ${idx === selectedIndex
                             ? 'bg-karma-accent/20 text-karma-accent'
                             : 'text-karma-text hover:bg-karma-bg'}`}
                onClick={() => onSelect(cmd)}
                onMouseEnter={() => setSelectedIndex(idx)}
              >
                <span className="font-mono font-bold min-w-[80px]">/{cmd.name}</span>
                <span className="text-karma-muted text-[11px]">{cmd.description}</span>
              </div>
            );
          })}
        </div>
      ))}
    </div>
  );
}
