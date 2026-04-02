'use client';

import { useState, useEffect, useCallback } from 'react';
import { useKarmaStore } from '@/store/karma';

interface Learning {
  id: string;
  content: string;
  from: string;
  created_at: string;
  type?: string;
}

export function LearnedPanel({ onClose }: { onClose: () => void }) {
  const [learnings, setLearnings] = useState<Learning[]>([]);
  const [loading, setLoading] = useState(true);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);
  const token = useKarmaStore((s) => s.token);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/v1/learnings', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setLearnings(data.entries || data.learnings || []);
      } catch {
        // ignore
      }
      setLoading(false);
    }
    load();
  }, [token]);

  async function submitDirection() {
    if (!input.trim()) return;
    setSending(true);
    try {
      await fetch('/v1/coordination/post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          from: 'colby',
          to: 'karma',
          type: 'directive',
          urgency: 'normal',
          content: input.trim(),
        }),
      });
      setInput('');
      setSent(true);
      setTimeout(() => setSent(false), 2000);
    } catch {
      // ignore
    }
    setSending(false);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-karma-bg border border-karma-accent/30 rounded w-[600px] max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-karma-border">
          <div className="text-karma-accent text-[12px] tracking-[3px] font-bold">LEARNED</div>
          <button
            className="text-karma-muted hover:text-karma-danger text-[14px] cursor-pointer bg-transparent border-none"
            onClick={onClose}
          >
            x
          </button>
        </div>

        {/* Sovereign Input */}
        <div className="px-4 py-3 border-b border-karma-border">
          <div className="text-karma-muted text-[10px] tracking-wider mb-1.5">SOVEREIGN DIRECTION</div>
          <textarea
            className="w-full bg-karma-surface border border-karma-border text-karma-text
                       px-3 py-2 text-[11px] outline-none resize-none
                       focus:border-karma-accent placeholder:text-karma-border"
            rows={3}
            placeholder="Suggestions, corrections, directions for Karma..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitDirection();
              }
            }}
          />
          <div className="flex items-center gap-2 mt-1.5">
            <button
              className="bg-karma-accent/20 border border-karma-accent text-karma-accent
                         px-3 py-1 text-[10px] tracking-wider cursor-pointer
                         hover:bg-karma-accent/30 disabled:opacity-50"
              disabled={sending || !input.trim()}
              onClick={submitDirection}
            >
              {sending ? 'SENDING...' : 'SEND TO KARMA'}
            </button>
            {sent && <span className="text-karma-accent2 text-[10px]">Sent to coordination bus</span>}
          </div>
        </div>

        {/* Learnings list */}
        <div className="flex-1 overflow-y-auto px-4 py-2">
          {loading && <div className="text-karma-muted text-[11px]">Loading learnings...</div>}
          {!loading && learnings.length === 0 && (
            <div className="text-karma-muted text-[11px] text-center py-4">No learnings yet.</div>
          )}
          {learnings.map((l) => (
            <LearningItem key={l.id} learning={l} />
          ))}
        </div>
      </div>
    </div>
  );
}

function LearningItem({ learning }: { learning: Learning }) {
  const [expanded, setExpanded] = useState(false);
  const l = learning;
  return (
    <div
      className="border-b border-karma-border py-2 cursor-pointer hover:bg-karma-surface/50"
      onClick={() => setExpanded(!expanded)}
    >
      <div className="flex items-center gap-2">
        <span className="text-karma-accent text-[10px] font-bold">{l.from || 'karma'}</span>
        <span className="text-karma-muted text-[9px]">
          {l.created_at ? new Date(l.created_at).toLocaleString() : ''}
        </span>
        {l.type && (
          <span className="text-karma-accent2 text-[9px] bg-karma-surface px-1 rounded">
            {l.type}
          </span>
        )}
        <span className="text-karma-muted text-[9px] ml-auto">{expanded ? '\u25BC' : '\u25B6'}</span>
      </div>
      <div className={`text-karma-text text-[11px] mt-0.5 ${expanded ? '' : 'line-clamp-1'}`}>
        {l.content}
      </div>
    </div>
  );
}
