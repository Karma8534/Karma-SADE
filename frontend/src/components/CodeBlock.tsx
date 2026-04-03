'use client';

import { useState, useCallback } from 'react';

interface Props {
  code: string;
  language?: string;
  diff?: boolean;
}

// Simple keyword-based highlighting (no external deps)
const KEYWORDS = new Set([
  'const', 'let', 'var', 'function', 'return', 'if', 'else', 'for', 'while',
  'class', 'import', 'export', 'from', 'default', 'async', 'await', 'try',
  'catch', 'throw', 'new', 'this', 'true', 'false', 'null', 'undefined',
  'def', 'self', 'None', 'True', 'False', 'print', 'raise', 'with', 'as',
  'elif', 'except', 'finally', 'lambda', 'yield', 'pass', 'break', 'continue',
]);

function highlightLine(line: string): JSX.Element {
  // Comments
  if (line.trimStart().startsWith('//') || line.trimStart().startsWith('#')) {
    return <span className="text-karma-muted italic">{line}</span>;
  }

  // Tokenize and highlight
  const tokens = line.split(/(\b\w+\b|"[^"]*"|'[^']*'|`[^`]*`|\s+|[^\w\s])/g);
  return (
    <>
      {tokens.map((token, i) => {
        if (!token) return null;
        // Strings
        if (/^["'`]/.test(token)) return <span key={i} className="text-karma-accent2">{token}</span>;
        // Keywords
        if (KEYWORDS.has(token)) return <span key={i} className="text-karma-accent">{token}</span>;
        // Numbers
        if (/^\d+/.test(token)) return <span key={i} className="text-[#f78c6c]">{token}</span>;
        return <span key={i}>{token}</span>;
      })}
    </>
  );
}

function renderDiffLine(line: string, idx: number): JSX.Element {
  if (line.startsWith('+')) {
    return (
      <div key={idx} className="bg-karma-accent2/10 text-karma-accent2">
        <span className="inline-block w-6 text-right mr-2 text-karma-muted text-[9px]">{idx + 1}</span>
        {line}
      </div>
    );
  }
  if (line.startsWith('-')) {
    return (
      <div key={idx} className="bg-karma-danger/10 text-karma-danger">
        <span className="inline-block w-6 text-right mr-2 text-karma-muted text-[9px]">{idx + 1}</span>
        {line}
      </div>
    );
  }
  return (
    <div key={idx}>
      <span className="inline-block w-6 text-right mr-2 text-karma-muted text-[9px]">{idx + 1}</span>
      {highlightLine(line)}
    </div>
  );
}

export function CodeBlock({ code, language, diff }: Props) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [code]);

  const lines = code.split('\n');

  return (
    <div className="relative group my-2 border border-karma-border rounded overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-1 bg-karma-bg border-b border-karma-border text-[9px]">
        <span className="text-karma-muted tracking-wider">{language || 'code'}</span>
        <button
          onClick={handleCopy}
          className="text-karma-muted hover:text-karma-accent cursor-pointer bg-transparent border-none text-[9px]"
        >
          {copied ? 'copied!' : 'copy'}
        </button>
      </div>

      {/* Code */}
      <pre className="px-3 py-2 overflow-x-auto text-[11px] font-mono leading-relaxed bg-karma-surface m-0">
        {diff
          ? lines.map((line, i) => renderDiffLine(line, i))
          : lines.map((line, i) => (
              <div key={i}>
                <span className="inline-block w-6 text-right mr-2 text-karma-muted text-[9px] select-none">
                  {i + 1}
                </span>
                {highlightLine(line)}
              </div>
            ))}
      </pre>
    </div>
  );
}
