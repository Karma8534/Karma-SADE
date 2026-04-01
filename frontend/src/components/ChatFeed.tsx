'use client';

import { useEffect, useRef } from 'react';
import { useKarmaStore, type ChatMessage, isVisibleTool, getPillLabel } from '@/store/karma';

export function ChatFeed() {
  const messages = useKarmaStore((s) => s.messages);
  const isStreaming = useKarmaStore((s) => s.isStreaming);
  const feedRef = useRef<HTMLDivElement>(null);

  // Auto-scroll on new messages
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [messages, isStreaming]);

  return (
    <div
      ref={feedRef}
      className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-3"
      onDragOver={(e) => { e.preventDefault(); e.currentTarget.classList.add('drag-active'); }}
      onDragLeave={(e) => e.currentTarget.classList.remove('drag-active')}
      onDrop={(e) => {
        e.preventDefault();
        e.currentTarget.classList.remove('drag-active');
        const files = e.dataTransfer.files;
        if (files.length) {
          for (const file of Array.from(files)) {
            const reader = new FileReader();
            reader.onload = () => {
              useKarmaStore.getState().addFile({
                name: file.name,
                type: file.type,
                data: reader.result as string,
              });
            };
            reader.readAsDataURL(file);
          }
        }
      }}
    >
      {messages.length === 0 && (
        <div className="flex-1 flex items-center justify-center text-karma-muted text-[12px] tracking-[2px]">
          Message Karma to begin.
        </div>
      )}
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      {isStreaming && (
        <div className="text-karma-accent text-[12px] animate-pulse">
          Karma is thinking...
        </div>
      )}
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const { role, content, timestamp, toolName, toolInput, toolOutput } = message;

  const time = new Date(timestamp).toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true,
  });

  // Tool evidence block
  if (role === 'tool-evidence' && toolName) {
    if (isVisibleTool(toolName)) {
      return (
        <details className="tool-block">
          <summary>
            {cleanToolName(toolName)}
            {toolInput && formatToolDetail(toolName, toolInput)}
          </summary>
          <pre>{toolOutput || '(running...)'}</pre>
        </details>
      );
    }
    // Pill for non-visible tools
    return (
      <span className="tool-pill">{getPillLabel(toolName)}</span>
    );
  }

  // User message
  if (role === 'user') {
    return (
      <div className="flex flex-col items-end gap-0.5">
        <div className="text-karma-muted text-[10px]">{time} YOU</div>
        <div className="bg-karma-surface border border-karma-border rounded px-4 py-2.5 max-w-[80%] whitespace-pre-wrap">
          {content}
        </div>
      </div>
    );
  }

  // System message
  if (role === 'system') {
    return (
      <div className="text-center text-karma-muted text-[11px] italic py-1">
        {content}
      </div>
    );
  }

  // Karma message
  return (
    <div className="flex flex-col items-start gap-0.5">
      <div className="text-karma-accent text-[11px] font-bold">
        KARMA <span className="text-karma-muted font-normal text-[10px]">{time}</span>
      </div>
      <div className="bg-karma-surface border border-karma-accent/30 rounded px-4 py-2.5 max-w-[85%] whitespace-pre-wrap">
        {content}
      </div>
    </div>
  );
}

function cleanToolName(name: string): string {
  const parts = name.split('__');
  return parts[parts.length - 1] || name;
}

function formatToolDetail(name: string, input: Record<string, unknown>): string {
  const clean = cleanToolName(name);
  const path = (input.file_path || input.path || input.pattern || input.command || '') as string;
  if (!path) return '';
  return ` \u2014 ${path.length > 60 ? '...' + path.slice(-57) : path}`;
}
