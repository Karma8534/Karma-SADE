'use client';

import { useState, useEffect } from 'react';
import { useKarmaStore } from '@/store/karma';

interface GitStatus {
  branch: string;
  changed: number;
  files: string[];
  recent_commits: string[];
}

export function GitPanel({ onClose }: { onClose: () => void }) {
  const [git, setGit] = useState<GitStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const token = useKarmaStore((s) => s.token);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch('/v1/git/status', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setGit(data);
        }
      } catch {}
      setLoading(false);
    }
    load();
  }, [token]);

  const fileIcon = (f: string) => {
    if (f.startsWith(' M') || f.startsWith('M ')) return { icon: '\u270F', color: 'text-yellow-400' }; // modified
    if (f.startsWith('A ') || f.startsWith('??')) return { icon: '+', color: 'text-karma-accent2' }; // added
    if (f.startsWith(' D') || f.startsWith('D ')) return { icon: '-', color: 'text-karma-danger' }; // deleted
    if (f.startsWith('R')) return { icon: '\u2192', color: 'text-karma-accent' }; // renamed
    return { icon: '\u00B7', color: 'text-karma-muted' };
  };

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="bg-karma-surface border border-karma-border w-[520px] max-h-[70vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between px-4 py-2 border-b border-karma-border">
          <div className="flex items-center gap-2">
            <span className="text-karma-accent text-[11px] tracking-[2px] font-bold">GIT STATUS</span>
            <button
              onClick={() => { onClose(); window.dispatchEvent(new CustomEvent('karma-send-message', { detail: '/diff' })); }}
              className="text-[9px] px-2 py-0.5 border border-karma-border text-karma-muted bg-transparent hover:border-karma-accent hover:text-karma-accent cursor-pointer"
            >DIFF</button>
            <button
              onClick={() => { onClose(); window.dispatchEvent(new CustomEvent('karma-send-message', { detail: '/commit' })); }}
              className="text-[9px] px-2 py-0.5 border border-karma-accent text-karma-accent bg-transparent hover:bg-karma-accent/10 cursor-pointer"
            >COMMIT</button>
          </div>
          <button onClick={onClose} className="text-karma-muted hover:text-karma-danger cursor-pointer bg-transparent border-none">x</button>
        </div>

        {loading ? (
          <div className="p-4 text-karma-muted text-[11px]">Loading...</div>
        ) : git ? (
          <div className="p-3 text-[11px]">
            {/* Branch */}
            <div className="flex items-center gap-2 mb-3">
              <span className="text-karma-muted">branch:</span>
              <span className="text-karma-accent font-mono font-bold">{git.branch}</span>
              <span className="text-karma-muted ml-auto">{git.changed} changed</span>
            </div>

            {/* Changed files */}
            {git.files.length > 0 && (
              <>
                <div className="text-[9px] tracking-[2px] text-karma-muted mb-1">CHANGES</div>
                <div className="border border-karma-border rounded mb-3">
                  {git.files.map((f, i) => {
                    const { icon, color } = fileIcon(f);
                    const path = f.slice(3).trim();
                    return (
                      <div key={i} className="flex items-center gap-2 px-2 py-0.5 hover:bg-karma-bg font-mono text-[10px]">
                        <span className={`${color} w-3 text-center`}>{icon}</span>
                        <span className="text-karma-text truncate">{path}</span>
                      </div>
                    );
                  })}
                </div>
              </>
            )}

            {/* Recent commits */}
            {git.recent_commits.length > 0 && (
              <>
                <div className="text-[9px] tracking-[2px] text-karma-muted mb-1">RECENT COMMITS</div>
                <div className="border border-karma-border rounded">
                  {git.recent_commits.map((c, i) => {
                    const [hash, ...rest] = c.split(' ');
                    return (
                      <div key={i} className="flex items-start gap-2 px-2 py-1 hover:bg-karma-bg text-[10px]">
                        <span className="text-karma-accent font-mono flex-shrink-0">{hash}</span>
                        <span className="text-karma-text">{rest.join(' ')}</span>
                      </div>
                    );
                  })}
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="p-4 text-karma-muted text-[11px]">Git status unavailable</div>
        )}
      </div>
    </div>
  );
}
