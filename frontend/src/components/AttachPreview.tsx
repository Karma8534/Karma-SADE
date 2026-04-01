'use client';

import { useKarmaStore } from '@/store/karma';

export function AttachPreview() {
  const pendingFiles = useKarmaStore((s) => s.pendingFiles);
  const removeFile = useKarmaStore((s) => s.removeFile);

  if (pendingFiles.length === 0) return null;

  return (
    <div className="flex gap-2 items-center flex-wrap mb-1">
      {pendingFiles.map((f, i) => (
        <span
          key={`${f.name}-${i}`}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded
                     bg-karma-surface border border-karma-accent text-karma-text text-[11px]"
        >
          {f.name}
          <span
            className="cursor-pointer text-karma-muted hover:text-karma-danger ml-1"
            onClick={() => removeFile(i)}
          >
            x
          </span>
        </span>
      ))}
    </div>
  );
}
