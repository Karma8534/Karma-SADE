'use client';

import { useState, useCallback } from 'react';
import { useKarmaStore } from '@/store/karma';

interface MemoryItem {
  id: number;
  title: string;
  created_at: string;
  text?: string;
  type?: string;
}

export function MemoryPanel({ onClose }: { onClose: () => void }) {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [saveText, setSaveText] = useState('');
  const [saveTitle, setSaveTitle] = useState('');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const token = useKarmaStore((s) => s.token);

  const doSearch = useCallback(async (query: string) => {
    setLoading(true);
    try {
      const res = await fetch('/v1/memory/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ query: query || 'recent', limit: 20 }),
      });
      const data = await res.json();
      setMemories(data.results || data.observations || []);
    } catch {}
    setLoading(false);
  }, [token]);

  const doSave = useCallback(async () => {
    if (!saveText.trim()) return;
    setSaving(true);
    try {
      await fetch('/v1/memory/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          action: 'save',
          text: saveText,
          title: saveTitle || 'Sovereign note',
          project: 'Karma_SADE',
        }),
      });
      setSaved(true);
      setSaveText('');
      setSaveTitle('');
      setTimeout(() => setSaved(false), 2000);
    } catch {}
    setSaving(false);
  }, [saveText, saveTitle, token]);

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="bg-karma-surface border border-karma-border w-[520px] max-h-[80vh] flex flex-col" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-karma-border">
          <span className="text-karma-accent text-[11px] tracking-[2px] font-bold">MEMORY</span>
          <div className="flex gap-2 items-center">
            <a
              href="http://localhost:37778"
              target="_blank"
              rel="noopener noreferrer"
              className="text-karma-muted text-[9px] hover:text-karma-accent"
            >
              full viewer
            </a>
            <button onClick={onClose} className="text-karma-muted hover:text-karma-danger cursor-pointer bg-transparent border-none">x</button>
          </div>
        </div>

        {/* Search */}
        <div className="px-3 py-2 border-b border-karma-border">
          <div className="flex gap-2">
            <input
              className="flex-1 bg-karma-bg border border-karma-border text-karma-text px-2 py-1
                         text-[11px] font-mono outline-none focus:border-karma-accent placeholder:text-karma-border"
              placeholder="Search memories..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && doSearch(search)}
            />
            <button
              onClick={() => doSearch(search)}
              className="px-2 py-1 text-[10px] border border-karma-border text-karma-muted hover:text-karma-accent
                         hover:border-karma-accent cursor-pointer bg-transparent"
            >
              SEARCH
            </button>
          </div>
        </div>

        {/* Results */}
        <div className="flex-1 overflow-y-auto p-2 min-h-[200px]">
          {loading && <div className="text-karma-muted text-[11px] p-2">Searching...</div>}
          {!loading && memories.length === 0 && (
            <div className="text-karma-muted text-[11px] p-2 text-center">
              Search memories or type a note below to save.
            </div>
          )}
          {memories.map((m) => (
            <div key={m.id} className="border-b border-karma-border px-2 py-1.5 hover:bg-karma-bg">
              <div className="flex items-center gap-2">
                <span className="text-karma-accent text-[10px] font-bold flex-1 truncate">{m.title}</span>
                <span className="text-karma-muted text-[9px] flex-shrink-0">#{m.id}</span>
              </div>
              <div className="text-karma-muted text-[9px]">{m.created_at}</div>
              {m.text && <div className="text-karma-text text-[10px] mt-0.5 line-clamp-3">{m.text}</div>}
            </div>
          ))}
        </div>

        {/* Sovereign input — save notes/directions/corrections */}
        <div className="border-t border-karma-border px-3 py-2">
          <div className="text-[9px] text-karma-muted tracking-[1px] mb-1">SOVEREIGN NOTE</div>
          <input
            className="w-full bg-karma-bg border border-karma-border text-karma-text px-2 py-1
                       text-[10px] font-mono outline-none focus:border-karma-accent placeholder:text-karma-border mb-1"
            placeholder="Title (optional)"
            value={saveTitle}
            onChange={(e) => setSaveTitle(e.target.value)}
          />
          <div className="flex gap-2">
            <textarea
              className="flex-1 bg-karma-bg border border-karma-border text-karma-text px-2 py-1
                         text-[10px] font-mono outline-none focus:border-karma-accent placeholder:text-karma-border
                         resize-none"
              rows={2}
              placeholder="Direction, correction, suggestion, or note for Julian/Karma..."
              value={saveText}
              onChange={(e) => setSaveText(e.target.value)}
            />
            <button
              onClick={doSave}
              disabled={saving || !saveText.trim()}
              className={`px-3 text-[10px] border cursor-pointer self-end
                         ${saved
                           ? 'border-karma-accent2 text-karma-accent2 bg-transparent'
                           : 'border-karma-accent text-karma-accent bg-transparent hover:bg-karma-accent/20'
                         } ${(!saveText.trim() || saving) ? 'opacity-40 cursor-not-allowed' : ''}`}
            >
              {saved ? 'SAVED' : saving ? '...' : 'SAVE'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
