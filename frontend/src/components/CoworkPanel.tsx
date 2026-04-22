'use client';

import { useEffect, useMemo, useState } from 'react';
import { useKarmaStore } from '@/store/karma';

export interface CoworkArtifact {
  id: string;
  type: 'plan' | 'code' | 'diff';
  title: string;
  content: string;
  summary: string;
  timestamp: string;
}

export function detectCoworkArtifact(content: string, id: string, timestamp: string): CoworkArtifact | null {
  const text = (content || '').trim();
  if (!text) return null;
  // Filter stale ascendance ritual ledger blobs from historical chat so Cowork shows
  // actionable artifacts only.
  if (/\bascendance ritual\b/i.test(text) && /\buuids?\b/i.test(text)) return null;
  if (/\bcheckpoint uuids?\b/i.test(text) || /\britual continues to step\b/i.test(text)) return null;

  const hasDiff = /^diff --git/m.test(text) || /^@@/m.test(text) || /```diff[\s\S]+```/i.test(text);
  const hasCode = /```[\w-]*\n[\s\S]+```/.test(text);
  const planLines = text.split('\n').filter((line) => /^\d+\.\s+/.test(line.trim()));
  const hasPlan = planLines.length >= 2 || /\b(open questions|next steps|plan)\b/i.test(text);

  if (!hasDiff && !hasCode && !hasPlan) return null;

  const type: CoworkArtifact['type'] = hasDiff ? 'diff' : hasCode ? 'code' : 'plan';
  const title = type === 'diff'
    ? 'Proposed Diff'
    : type === 'code'
      ? 'Code Artifact'
      : 'Working Plan';
  const summarySource = type === 'plan' ? planLines.join(' ') || text : text;
  const summary = summarySource.replace(/\s+/g, ' ').slice(0, 140);

  return { id, type, title, content: text, summary, timestamp };
}

export function CoworkPanel({ onCollapse }: { onCollapse?: () => void }) {
  const messages = useKarmaStore((s) => s.messages);
  const artifacts = useMemo(
    () => messages
      .filter((msg) => msg.role === 'karma')
      .map((msg) => detectCoworkArtifact(msg.content, msg.id, msg.timestamp))
      .filter((artifact): artifact is CoworkArtifact => Boolean(artifact)),
    [messages],
  );
  const [selectedId, setSelectedId] = useState<string>('');

  useEffect(() => {
    if (!artifacts.length) {
      setSelectedId('');
      return;
    }
    if (!selectedId || !artifacts.some((artifact) => artifact.id === selectedId)) {
      setSelectedId(artifacts[artifacts.length - 1].id);
    }
  }, [artifacts, selectedId]);

  const selected = artifacts.find((artifact) => artifact.id === selectedId) || artifacts[artifacts.length - 1];

  return (
    <div className="w-[340px] border-l border-karma-border bg-karma-surface flex-shrink-0 flex flex-col">
      <div className="px-3 py-2 border-b border-karma-border">
        <div className="flex items-center justify-between gap-2">
          <div className="text-karma-accent text-[11px] tracking-[2px] font-bold">COWORK</div>
          {onCollapse && (
            <button
              onClick={onCollapse}
              className="text-[10px] px-1.5 py-0.5 border border-karma-border text-karma-muted hover:text-karma-accent bg-transparent cursor-pointer"
            >
              HIDE
            </button>
          )}
        </div>
        <div className="text-karma-muted text-[10px]">Structured plans, diffs, and code artifacts.</div>
      </div>

      {!artifacts.length ? (
        <div className="p-3 text-[11px] text-karma-muted">
          No artifacts yet. Ask for a plan, diff, or code draft.
        </div>
      ) : (
        <>
          <div className="max-h-[220px] overflow-y-auto border-b border-karma-border">
            {artifacts.slice().reverse().map((artifact) => (
              <button
                key={artifact.id}
                className={`w-full text-left px-3 py-2 border-none border-b border-karma-border/40 cursor-pointer ${
                  selected?.id === artifact.id ? 'bg-karma-bg' : 'bg-transparent hover:bg-karma-bg/60'
                }`}
                onClick={() => setSelectedId(artifact.id)}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="text-karma-text text-[11px]">{artifact.title}</span>
                  <span className="text-karma-muted text-[9px] uppercase">{artifact.type}</span>
                </div>
                <div className="text-karma-muted text-[10px] mt-1">{artifact.summary}</div>
              </button>
            ))}
          </div>

          {selected && (
            <div className="flex-1 overflow-y-auto p-3">
              <div className="text-karma-accent text-[11px] font-bold mb-2">{selected.title}</div>
              <pre className="whitespace-pre-wrap text-[11px] text-karma-text font-mono leading-5">
                {selected.content}
              </pre>
            </div>
          )}
        </>
      )}
    </div>
  );
}
