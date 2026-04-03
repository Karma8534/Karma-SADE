'use client';

import { useState, useRef, useCallback } from 'react';
import { useKarmaStore } from '@/store/karma';
import { useKarmaStream } from '@/hooks/useKarmaStream';
import { AttachPreview } from '@/components/AttachPreview';
import { SlashCommandPicker, type SlashCommand } from '@/components/SlashCommandPicker';

export function MessageInput() {
  const [text, setText] = useState('');
  const [showCommands, setShowCommands] = useState(false);
  const [commandFilter, setCommandFilter] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isStreaming = useKarmaStore((s) => s.isStreaming);
  const pendingFiles = useKarmaStore((s) => s.pendingFiles);
  const { sendMessage, cancelStream } = useKarmaStream();

  const handleCommandSelect = useCallback((cmd: SlashCommand) => {
    setShowCommands(false);
    setCommandFilter('');

    // Local commands handled in-browser
    if (cmd.name === 'help') {
      useKarmaStore.getState().addMessage({
        id: Date.now().toString(36),
        role: 'system',
        content: `**KARMA NEXUS — COMMANDS**

**Session:** /clear (reset) | /compact (compress context) | /export (save transcript)
**Info:** /help | /cost (show spend) | /status (system health) | /context (context budget)
**Config:** /model | /effort (thinking depth) | /theme | /settings (open panel)
**Dev:** /plan | /diff | /commit | /review | /skills | /hooks | /agents | /memory
**Doctor:** /doctor (run diagnostics)

**Shortcuts:** Enter=send | Shift+Enter=newline | Esc=cancel | /=commands | Ctrl+K=search

**Architecture:** P1 (CC brain) | K2 (cortex + regent) | vault-neo (spine)
**Identity:** Julian = Ascendant | Karma = Initiate | Colby = Sovereign
**The Goal:** Nexus = infinity. Persistent. Self-improving. Substrate-independent.`,
        timestamp: new Date().toISOString(),
      });
      setText('');
      return;
    }
    if (cmd.name === 'clear') {
      useKarmaStore.getState().clearMessages();
      setText('');
      return;
    }
    if (cmd.name === 'memory') {
      // Open MEMORY panel (same as header button)
      window.dispatchEvent(new CustomEvent('karma-open-memory'));
      setText('');
      return;
    }
    if (cmd.name === 'agents') {
      window.dispatchEvent(new CustomEvent('karma-open-agents'));
      setText('');
      return;
    }
    if (cmd.name === 'hooks') {
      // Show hooks inline from surface data
      const store = useKarmaStore.getState();
      const hooks = (store.surface?.hooks?.list as { name: string; event: string }[]) || [];
      const hookList = hooks.length > 0
        ? hooks.map(h => `  ${h.event} → ${h.name}`).join('\n')
        : '  No hooks loaded';
      store.addMessage({
        id: Date.now().toString(36), role: 'system',
        content: `**HOOKS** (${hooks.length} active)\n${hookList}`,
        timestamp: new Date().toISOString(),
      });
      setText('');
      return;
    }
    if (cmd.name === 'skills') {
      const store = useKarmaStore.getState();
      const skills = store.surface?.skills;
      const skillList = skills?.names?.length
        ? skills.names.map((n: string) => `  ${n}`).join('\n')
        : '  No skills loaded';
      store.addMessage({
        id: Date.now().toString(36), role: 'system',
        content: `**SKILLS** (${skills?.count || 0})\n${skillList}`,
        timestamp: new Date().toISOString(),
      });
      setText('');
      return;
    }
    if (cmd.name === 'effort') {
      // Cycle through effort levels
      const levels = ['', 'low', 'medium', 'high', 'max'] as const;
      const store = useKarmaStore.getState();
      const cur = levels.indexOf(store.effortLevel as typeof levels[number]);
      const next = levels[(cur + 1) % levels.length];
      store.setEffort(next);
      store.addMessage({
        id: Date.now().toString(36), role: 'system',
        content: `**EFFORT** set to **${next || 'auto'}**`,
        timestamp: new Date().toISOString(),
      });
      setText('');
      return;
    }
    if (cmd.name === 'theme') {
      const store = useKarmaStore.getState();
      const next = store.theme === 'dark' ? 'light' : 'dark';
      store.setTheme(next);
      store.addMessage({
        id: Date.now().toString(36), role: 'system',
        content: `**THEME** switched to **${next}**`,
        timestamp: new Date().toISOString(),
      });
      setText('');
      return;
    }
    if (cmd.name === 'status') {
      const store = useKarmaStore.getState();
      // Fire async health check and render result
      (async () => {
        let healthText = 'Checking...';
        try {
          const res = await fetch('/v1/status', {
            headers: { Authorization: `Bearer ${store.token}` },
          });
          if (res.ok) {
            const d = await res.json();
            const p1 = d.harness?.p1?.healthy ? 'UP' : 'DOWN';
            const k2 = d.harness?.k2?.healthy ? 'UP' : 'DOWN';
            healthText = `P1: ${p1} | K2: ${k2} | vault: ${d.ok ? 'UP' : 'DOWN'} | uptime: ${d.uptime || 'unknown'}`;
          } else {
            healthText = `Hub returned ${res.status}`;
          }
        } catch (e) {
          healthText = 'Hub unreachable';
        }
        store.addMessage({
          id: Date.now().toString(36),
          role: 'system',
          content: `**STATUS** | ${healthText}`,
          timestamp: new Date().toISOString(),
        });
      })();
      setText('');
      return;
    }
    if (cmd.name === 'cost') {
      const store = useKarmaStore.getState();
      useKarmaStore.getState().addMessage({
        id: Date.now().toString(36),
        role: 'system',
        content: `**COST** | Session: $${store.sessionCost.toFixed(4)} | Model: cc-sovereign (Max $0/request) | Infrastructure: $24/mo (droplet)`,
        timestamp: new Date().toISOString(),
      });
      setText('');
      return;
    }
    if (cmd.name === 'context') {
      const store = useKarmaStore.getState();
      const chars = store.messages.reduce((s, m) => s + (m.content?.length || 0), 0);
      const kb = (chars / 1024).toFixed(1);
      const pct = Math.min(100, (chars / 128000) * 100).toFixed(0);
      useKarmaStore.getState().addMessage({
        id: Date.now().toString(36),
        role: 'system',
        content: `**CONTEXT** | ${kb}KB used (${pct}% of 128K window) | ${store.messages.length} messages | Surface: ${store.surface ? 'loaded' : 'not loaded'}`,
        timestamp: new Date().toISOString(),
      });
      setText('');
      return;
    }
    if (cmd.name === 'settings') {
      // Trigger settings panel via a custom event
      window.dispatchEvent(new CustomEvent('karma-open-settings'));
      setText('');
      return;
    }

    // All other commands sent to CC
    sendMessage(`/${cmd.name}`);
    setText('');
  }, [sendMessage]);

  const handleTextChange = useCallback((value: string) => {
    setText(value);
    // Show command picker when typing / at start of input
    if (value.startsWith('/') && !value.includes(' ')) {
      setShowCommands(true);
      setCommandFilter(value.slice(1));
    } else {
      setShowCommands(false);
      setCommandFilter('');
    }
  }, []);

  const handleSend = useCallback(() => {
    if (isStreaming) {
      cancelStream();
      return;
    }
    if (showCommands) {
      setShowCommands(false);
      setCommandFilter('');
    }
    if (!text.trim() && pendingFiles.length === 0) return;
    sendMessage(text);
    setText('');
    if (textareaRef.current) textareaRef.current.style.height = 'auto';
  }, [text, isStreaming, pendingFiles, sendMessage, cancelStream, showCommands]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    // Let SlashCommandPicker handle arrow keys and Enter when visible
    if (showCommands && (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Tab')) {
      return; // SlashCommandPicker handles these via window listener
    }
    if (showCommands && e.key === 'Enter') {
      return; // SlashCommandPicker handles Enter selection
    }
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
    if (e.key === 'Escape') {
      if (showCommands) {
        setShowCommands(false);
        setCommandFilter('');
      } else if (isStreaming) {
        cancelStream();
      }
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;
    for (const item of Array.from(items)) {
      if (item.type.startsWith('image/')) {
        e.preventDefault();
        const file = item.getAsFile();
        if (file) addFileFromNative(file);
        return;
      }
    }
  };

  const addFileFromNative = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      useKarmaStore.getState().addFile({
        name: file.name,
        type: file.type,
        data: reader.result as string,
      });
    };
    reader.readAsDataURL(file);
  };

  const handleFileSelect = () => {
    const files = fileInputRef.current?.files;
    if (files) {
      for (const file of Array.from(files)) addFileFromNative(file);
      fileInputRef.current!.value = '';
    }
  };

  const autoGrow = (el: HTMLTextAreaElement) => {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 140) + 'px';
  };

  return (
    <div className="flex-shrink-0 px-5 pb-2 relative">
      <AttachPreview />
      <SlashCommandPicker
        filter={commandFilter}
        onSelect={handleCommandSelect}
        onClose={() => { setShowCommands(false); setCommandFilter(''); }}
        visible={showCommands}
      />
      <div className="flex items-end gap-2">
        {/* Attach button */}
        <button
          className="text-karma-muted hover:text-karma-accent text-lg pb-2 cursor-pointer
                     bg-transparent border-none"
          title="Attach file"
          onClick={() => fileInputRef.current?.click()}
        >
          +
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          hidden
          onChange={handleFileSelect}
        />

        {/* Message input */}
        <textarea
          ref={textareaRef}
          rows={1}
          className="flex-1 bg-karma-surface border border-karma-border text-karma-text
                     px-3 py-2 font-mono text-[13px] outline-none resize-none
                     focus:border-karma-accent placeholder:text-karma-border"
          placeholder={isStreaming ? 'Karma is working...' : 'Message Karma... (@cc @codex @regent \u2192 routes to AGORA)'}
          value={text}
          disabled={isStreaming}
          onChange={(e) => { handleTextChange(e.target.value); autoGrow(e.target); }}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
        />

        {/* Send / Stop button */}
        <button
          className={`px-6 py-2 font-mono text-[13px] font-bold tracking-[2px] border-none cursor-pointer
                     transition-colors ${
                       isStreaming
                         ? 'bg-karma-danger text-white'
                         : 'bg-karma-accent text-karma-text hover:bg-karma-border-active'
                     }`}
          onClick={handleSend}
        >
          {isStreaming ? 'STOP' : 'SEND'}
        </button>
      </div>
    </div>
  );
}
