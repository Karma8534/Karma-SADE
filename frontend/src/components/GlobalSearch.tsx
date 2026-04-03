'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { useKarmaStore } from '@/store/karma';

interface SearchResult {
  source: 'memory' | 'file' | 'message';
  title: string;
  snippet: string;
  id?: string | number;
  path?: string;
}

export function GlobalSearch({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const token = useKarmaStore((s) => s.token);
  const messages = useKarmaStore((s) => s.messages);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const doSearch = useCallback(async (q: string) => {
    if (!q.trim()) { setResults([]); return; }
    setLoading(true);
    const allResults: SearchResult[] = [];

    // Search conversation messages (local, instant)
    messages.forEach((m) => {
      if (m.content.toLowerCase().includes(q.toLowerCase())) {
        allResults.push({
          source: 'message',
          title: `${m.role} · ${new Date(m.timestamp).toLocaleTimeString()}`,
          snippet: m.content.slice(0, 120),
        });
      }
    });

    // Search claude-mem
    try {
      const res = await fetch('/v1/memory/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ query: q, limit: 10 }),
      });
      if (res.ok) {
        const data = await res.json();
        for (const obs of (data.results || data.observations || [])) {
          allResults.push({
            source: 'memory',
            title: obs.title || 'Memory',
            snippet: (obs.text || obs.narrative || '').slice(0, 120),
            id: obs.id,
          });
        }
      }
    } catch {}

    setResults(allResults);
    setLoading(false);
  }, [token, messages]);

  // Keyboard: Esc closes, Enter searches
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  const sourceIcon = (s: string) => {
    if (s === 'memory') return '\uD83E\uDDE0';
    if (s === 'file') return '\uD83D\uDCC4';
    return '\uD83D\uDCAC';
  };

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-start justify-center pt-[15vh]" onClick={onClose}>
      <div className="bg-karma-surface border border-karma-border w-[560px] max-h-[60vh] flex flex-col shadow-2xl" onClick={(e) => e.stopPropagation()}>
        {/* Search input */}
        <div className="flex items-center gap-2 px-3 py-2 border-b border-karma-border">
          <span className="text-karma-muted text-[12px]">/</span>
          <input
            ref={inputRef}
            className="flex-1 bg-transparent text-karma-text text-[13px] font-mono outline-none placeholder:text-karma-border"
            placeholder="Search messages, memories, files..."
            value={query}
            onChange={(e) => { setQuery(e.target.value); doSearch(e.target.value); }}
            onKeyDown={(e) => e.key === 'Enter' && doSearch(query)}
          />
          {loading && <span className="text-karma-muted text-[10px]">searching...</span>}
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto">
          {results.length === 0 && query && !loading && (
            <div className="p-4 text-karma-muted text-[11px] text-center">No results</div>
          )}
          {results.map((r, i) => (
            <div key={i} className="flex items-start gap-2 px-3 py-2 hover:bg-karma-bg cursor-pointer border-b border-karma-border/30">
              <span className="text-[12px] mt-0.5">{sourceIcon(r.source)}</span>
              <div className="flex-1 min-w-0">
                <div className="text-karma-text text-[11px] font-mono truncate">{r.title}</div>
                <div className="text-karma-muted text-[10px] line-clamp-2">{r.snippet}</div>
              </div>
              <span className="text-[8px] text-karma-border tracking-wider flex-shrink-0 mt-1">{r.source.toUpperCase()}</span>
            </div>
          ))}
        </div>

        {/* Footer hint */}
        <div className="px-3 py-1.5 border-t border-karma-border text-[9px] text-karma-muted flex gap-3">
          <span><kbd className="bg-karma-bg px-1 rounded">Enter</kbd> search</span>
          <span><kbd className="bg-karma-bg px-1 rounded">Esc</kbd> close</span>
        </div>
      </div>
    </div>
  );
}
