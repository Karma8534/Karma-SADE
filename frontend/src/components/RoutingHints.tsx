'use client';

export function RoutingHints() {
  return (
    <div className="flex-shrink-0 px-5 py-1 text-[10px] text-karma-muted flex gap-6">
      <span>default &rarr; <span className="text-karma-accent font-bold">KARMA</span></span>
      <span>@regent &rarr; <span className="text-karma-accent font-bold">REGENT</span></span>
      <span>@cc &rarr; <span className="text-karma-accent font-bold">CC</span></span>
      <span>@codex &rarr; <span className="text-karma-accent font-bold">CODEX</span></span>
    </div>
  );
}
