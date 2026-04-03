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
    // Send the slash command as a message — CC handles it natively
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
