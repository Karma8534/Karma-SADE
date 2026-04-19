'use client';

import { useEffect, useMemo, useState } from 'react';
import { createPatch } from 'diff';
import { useKarmaStore } from '@/store/karma';
import { CodeBlock } from '@/components/CodeBlock';
import { apiFetch } from '@/lib/api';

interface OpenCodeEventDetail {
  path: string;
}

function detectLanguage(path: string): string {
  const ext = path.split('.').pop()?.toLowerCase() || '';
  const map: Record<string, string> = {
    ts: 'typescript',
    tsx: 'tsx',
    js: 'javascript',
    jsx: 'jsx',
    py: 'python',
    json: 'json',
    md: 'markdown',
    css: 'css',
    html: 'html',
    sh: 'bash',
    ps1: 'powershell',
  };
  return map[ext] || 'text';
}

function buildDiff(original: string, edited: string, filePath: string): string {
  // LCS-based unified diff via jsdiff — proper alignment for inserts/deletes mid-file
  const name = filePath || 'file';
  const patch = createPatch(name, original, edited, 'original', 'edited', { context: 3 });
  return patch;
}

export function CodePanel() {
  const token = useKarmaStore((s) => s.token);
  const [filePath, setFilePath] = useState('');
  const [original, setOriginal] = useState('');
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const listener = (event: Event) => {
      const detail = (event as CustomEvent<OpenCodeEventDetail>).detail;
      if (detail?.path) setFilePath(detail.path);
    };
    window.addEventListener('karma-open-code', listener as EventListener);
    return () => window.removeEventListener('karma-open-code', listener as EventListener);
  }, []);

  useEffect(() => {
    if (!filePath) return;
    let active = true;
    async function loadFile() {
      setLoading(true);
      setError('');
        try {
        const res = await apiFetch(`/v1/file?path=${encodeURIComponent(filePath)}`, { token });
        const data = await res.json();
        if (!active) return;
        if (!res.ok || data.ok === false) {
          setError(data.error || 'Failed to read file');
          return;
        }
        const content = data.content || '';
        setOriginal(content);
        setDraft(content);
      } catch (err) {
        if (!active) return;
        setError(err instanceof Error ? err.message : 'Failed to read file');
      } finally {
        if (active) setLoading(false);
      }
    }
    loadFile();
    return () => { active = false; };
  }, [filePath, token]);

  const diffText = useMemo(() => buildDiff(original, draft, filePath), [original, draft, filePath]);
  const language = detectLanguage(filePath);
  const dirty = draft !== original;

  async function save() {
    setSaving(true);
    setError('');
    try {
      const res = await apiFetch('/v1/file', {
        method: 'POST',
        token,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: filePath, content: draft }),
      });
      const data = await res.json();
      if (!res.ok || data.ok === false) {
        setError(data.error || 'Save failed');
        return;
      }
      setOriginal(draft);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Save failed');
    } finally {
      setSaving(false);
    }
  }

  if (!filePath) return null;

  return (
    <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center" onClick={() => setFilePath('')}>
      <div
        className="w-[min(1200px,92vw)] h-[min(820px,88vh)] bg-karma-surface border border-karma-border flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="px-4 py-2 border-b border-karma-border flex items-center justify-between">
          <div>
            <div className="text-karma-accent text-[11px] tracking-[2px] font-bold">CODE</div>
            <div className="text-karma-muted text-[10px]">{filePath}</div>
          </div>
          <div className="flex items-center gap-2">
            <button
              className="px-3 py-1 text-[10px] border border-karma-border text-karma-muted bg-transparent cursor-pointer"
              onClick={() => setDraft(original)}
              disabled={!dirty}
            >
              RESET
            </button>
            <button
              className="px-3 py-1 text-[10px] border border-karma-accent text-karma-accent bg-transparent cursor-pointer"
              onClick={save}
              disabled={!dirty || saving}
            >
              {saving ? 'SAVING' : 'SAVE'}
            </button>
            <button
              className="px-2 py-1 text-[10px] border border-karma-border text-karma-muted bg-transparent cursor-pointer"
              onClick={() => setFilePath('')}
            >
              X
            </button>
          </div>
        </div>

        {error && <div className="px-4 py-2 text-[11px] text-karma-danger border-b border-karma-border">{error}</div>}

        <div className="flex-1 min-h-0 grid grid-cols-2">
          <div className="border-r border-karma-border flex flex-col min-h-0">
            <div className="px-3 py-2 text-[10px] text-karma-muted border-b border-karma-border">Editor</div>
            {loading ? (
              <div className="p-4 text-karma-muted text-[11px]">Loading...</div>
            ) : (
              <textarea
                className="flex-1 bg-karma-bg text-karma-text font-mono text-[12px] p-3 resize-none outline-none"
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                spellCheck={false}
              />
            )}
          </div>

          <div className="min-h-0 overflow-y-auto">
            <div className="px-3 py-2 text-[10px] text-karma-muted border-b border-karma-border">Diff Preview</div>
            <div className="p-3">
              <CodeBlock code={dirty ? diffText : draft} language={dirty ? 'diff' : language} diff={dirty} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
