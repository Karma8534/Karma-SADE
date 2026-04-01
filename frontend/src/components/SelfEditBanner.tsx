'use client';

import { useState, useEffect } from 'react';
import { useKarmaStore } from '@/store/karma';

interface PendingEdit {
  id: number;
  file_path: string;
  description: string;
  risk_level: string;
  proposed_at: string;
  auto_approve_at: string | null;
  diff_preview: string;
}

export function SelfEditBanner() {
  const [pendingEdits, setPendingEdits] = useState<PendingEdit[]>([]);
  const [countdown, setCountdown] = useState('');
  const [expanded, setExpanded] = useState<number | null>(null);
  const token = useKarmaStore((s) => s.token);

  // Poll for pending edits every 30s
  useEffect(() => {
    async function fetchPending() {
      try {
        const res = await fetch('/v1/self-edit/pending', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        if (data.ok) setPendingEdits(data.proposals || []);
      } catch {
        // ignore
      }
    }
    fetchPending();
    const interval = setInterval(fetchPending, 30000);
    return () => clearInterval(interval);
  }, [token]);

  // Countdown timer
  useEffect(() => {
    if (pendingEdits.length === 0) return;

    const earliest = pendingEdits
      .filter((e) => e.auto_approve_at)
      .sort((a, b) => (a.auto_approve_at || '').localeCompare(b.auto_approve_at || ''))[0];

    if (!earliest?.auto_approve_at) {
      setCountdown('manual approval required');
      return;
    }

    const interval = setInterval(() => {
      const remaining = new Date(earliest.auto_approve_at!).getTime() - Date.now();
      if (remaining <= 0) {
        setCountdown('auto-approving...');
        return;
      }
      const mins = Math.floor(remaining / 60000);
      const secs = Math.floor((remaining % 60000) / 1000);
      setCountdown(`${mins}:${secs.toString().padStart(2, '0')}`);
    }, 1000);

    return () => clearInterval(interval);
  }, [pendingEdits]);

  async function handleApprove(id: number) {
    try {
      await fetch(`/v1/self-edit/approve/${id}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      setPendingEdits((prev) => prev.filter((e) => e.id !== id));
    } catch {
      // ignore
    }
  }

  async function handleReject(id: number) {
    try {
      await fetch(`/v1/self-edit/reject/${id}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      });
      setPendingEdits((prev) => prev.filter((e) => e.id !== id));
    } catch {
      // ignore
    }
  }

  async function handleApproveAll() {
    for (const edit of pendingEdits) {
      await handleApprove(edit.id);
    }
  }

  if (pendingEdits.length === 0) return null;

  return (
    <div className="bg-yellow-900/30 border-b border-yellow-700/50 px-5 py-2 flex-shrink-0">
      <div className="flex items-center gap-3 text-[11px]">
        <span className="text-yellow-400 font-bold">SELF-EDIT</span>
        <span className="text-yellow-200">
          {pendingEdits.length} pending edit{pendingEdits.length > 1 ? 's' : ''}
        </span>
        <span className="text-yellow-400/70">{countdown}</span>
        <div className="flex-1" />
        <button
          className="text-yellow-400 hover:text-yellow-200 bg-transparent border border-yellow-700
                     px-2 py-0.5 text-[10px] cursor-pointer"
          onClick={handleApproveAll}
        >
          Approve All
        </button>
      </div>

      {/* Edit list */}
      {pendingEdits.map((edit) => (
        <div key={edit.id} className="mt-1 flex items-start gap-2 text-[10px]">
          <span className={`px-1 rounded ${
            edit.risk_level === 'high' ? 'bg-red-900 text-red-300' :
            edit.risk_level === 'medium' ? 'bg-yellow-900 text-yellow-300' :
            'bg-green-900 text-green-300'
          }`}>
            {edit.risk_level}
          </span>
          <span className="text-yellow-200 font-mono">{edit.file_path}</span>
          <span className="text-karma-muted">{edit.description}</span>
          <div className="flex-1" />
          <button
            className="text-karma-muted hover:text-karma-text bg-transparent border-none cursor-pointer text-[10px]"
            onClick={() => setExpanded(expanded === edit.id ? null : edit.id)}
          >
            {expanded === edit.id ? 'hide' : 'review'}
          </button>
          <button
            className="text-green-400 hover:text-green-200 bg-transparent border-none cursor-pointer text-[10px]"
            onClick={() => handleApprove(edit.id)}
          >
            approve
          </button>
          <button
            className="text-red-400 hover:text-red-200 bg-transparent border-none cursor-pointer text-[10px]"
            onClick={() => handleReject(edit.id)}
          >
            reject
          </button>
          {expanded === edit.id && (
            <pre className="w-full mt-1 p-2 bg-karma-bg text-[9px] text-karma-muted overflow-x-auto whitespace-pre-wrap border border-karma-border rounded">
              {edit.diff_preview}
            </pre>
          )}
        </div>
      ))}
    </div>
  );
}
