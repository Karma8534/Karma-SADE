'use client';

import { useState } from 'react';
import { useKarmaStore } from '@/store/karma';

export function Gate() {
  const [input, setInput] = useState('');
  const [error, setError] = useState('');
  const setToken = useKarmaStore((s) => s.setToken);

  async function handleSubmit() {
    if (!input.trim()) return;
    // Validate token by hitting the API
    try {
      const res = await fetch('/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${input.trim()}`,
        },
        body: JSON.stringify({ message: 'ping', stream: false }),
      });
      if (res.status === 401) {
        setError('Token rejected.');
        return;
      }
      setToken(input.trim());
    } catch {
      // If fetch fails, still accept (might be CORS in dev)
      setToken(input.trim());
    }
  }

  return (
    <div className="flex flex-col items-center justify-center h-screen gap-3.5">
      <div className="text-[11px] tracking-[6px] text-karma-accent uppercase mb-1">
        SovereignPeer
      </div>
      <h1 className="text-[28px] text-karma-accent tracking-[8px] font-light">KARMA</h1>
      <div className="text-karma-muted text-[11px] tracking-[2px]">
        Ascendant . Always Present
      </div>
      <input
        className="bg-karma-surface border border-karma-border text-karma-text
                   px-3.5 py-2.5 w-[420px] font-mono text-[13px] outline-none
                   focus:border-karma-accent-active mt-3
                   placeholder:text-karma-border"
        placeholder="Enter token"
        type="password"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
      />
      <button
        className="bg-karma-accent text-karma-text border-none px-7 py-2.5
                   cursor-pointer font-mono text-[13px] font-bold tracking-[2px]
                   hover:bg-karma-border-active transition-colors"
        onClick={handleSubmit}
      >
        ENTER
      </button>
      {error && <div className="text-karma-danger text-[12px]">{error}</div>}
    </div>
  );
}
