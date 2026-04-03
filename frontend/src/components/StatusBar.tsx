'use client';

import { useState, useEffect } from 'react';
import { useKarmaStore } from '@/store/karma';

interface SystemHealth {
  p1: boolean;
  k2: boolean;
  vault: boolean;
}

export function StatusBar() {
  const sessionCost = useKarmaStore((s) => s.sessionCost);
  const messages = useKarmaStore((s) => s.messages);
  const [health, setHealth] = useState<SystemHealth>({ p1: false, k2: false, vault: false });
  const [model, setModel] = useState('cc-sovereign');
  const [contextChars, setContextChars] = useState(0);
  const [monthlyCost, setMonthlyCost] = useState(0);
  const token = useKarmaStore((s) => s.token);

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch('/v1/status', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setHealth({
            p1: data.harness?.p1?.healthy ?? false,
            k2: data.harness?.k2?.healthy ?? false,
            vault: data.ok ?? false,
          });
          if (data.harness?.p1?.healthy) setModel('cc-sovereign (Max $0)');
          if (data.monthly_cost_usd != null) setMonthlyCost(data.monthly_cost_usd);
        }
      } catch {}
    }
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, [token]);

  // Estimate context size from messages
  useEffect(() => {
    const chars = messages.reduce((sum, m) => sum + (m.content?.length || 0), 0);
    setContextChars(chars);
  }, [messages]);

  const contextKB = (contextChars / 1024).toFixed(1);
  const contextPct = Math.min(100, (contextChars / 128000) * 100).toFixed(0);

  const dot = (ok: boolean) => (
    <span className={`inline-block w-1.5 h-1.5 rounded-full ${ok ? 'bg-karma-accent2' : 'bg-karma-danger'}`} />
  );

  return (
    <div className="flex items-center gap-4 text-[10px] text-karma-muted px-4 py-1 border-t border-karma-border bg-karma-bg">
      {/* Model badge */}
      <span className="text-karma-accent font-mono">{model}</span>

      {/* Session cost */}
      <span>
        ${sessionCost.toFixed(4)}
        <span className="text-karma-border ml-1">session</span>
      </span>

      {/* Monthly cost */}
      {monthlyCost > 0 && (
        <span>
          ${monthlyCost.toFixed(2)}
          <span className="text-karma-border ml-1">/mo</span>
          <span className={`ml-1 ${monthlyCost > 50 ? 'text-karma-danger' : 'text-karma-accent2'}`}>
            {monthlyCost > 50 ? 'WARN' : 'OK'}
          </span>
        </span>
      )}

      {/* Context budget */}
      <span>
        {contextKB}KB
        <span className="text-karma-border ml-1">ctx</span>
        <span className={`ml-1 ${Number(contextPct) > 80 ? 'text-yellow-400' : 'text-karma-accent2'}`}>
          {contextPct}%
        </span>
      </span>

      {/* Message count */}
      <span>{messages.length} msgs</span>

      {/* System health dots */}
      <span className="flex items-center gap-1.5 ml-auto">
        {dot(health.p1)} <span>P1</span>
        {dot(health.k2)} <span>K2</span>
        {dot(health.vault)} <span>vault</span>
      </span>
    </div>
  );
}
