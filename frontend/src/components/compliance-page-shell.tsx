import Link from 'next/link';
import type { ReactNode } from 'react';

type CompliancePageShellProps = {
  eyebrow: string;
  title: string;
  description: string;
  accent: string;
  children: ReactNode;
  sidebarTitle: string;
  sidebarBody: ReactNode;
  footerLinks: Array<{
    href: string;
    label: string;
  }>;
};

export function CompliancePageShell({
  eyebrow,
  title,
  description,
  accent,
  children,
  sidebarTitle,
  sidebarBody,
  footerLinks,
}: CompliancePageShellProps) {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#0f0f13] text-slate-100">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.16),_transparent_22%),radial-gradient(circle_at_top_right,_rgba(56,189,248,0.14),_transparent_24%),radial-gradient(circle_at_70%_20%,_rgba(16,185,129,0.08),_transparent_18%),linear-gradient(180deg,_#14141a_0%,_#09090d_100%)]" />
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />
      <div className="absolute left-10 top-10 h-44 w-44 rounded-full bg-amber-300/10 blur-3xl" />
      <div className="absolute right-10 top-28 h-56 w-56 rounded-full bg-cyan-300/10 blur-3xl" />

      <div className="relative mx-auto max-w-6xl px-6 py-10 lg:px-10 lg:py-14">
        <div className="mb-8 flex items-start justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-[1.1rem] border border-white/10 bg-white/[0.06] text-sm font-semibold tracking-[0.22em] text-white shadow-[0_14px_40px_rgba(0,0,0,0.28)]">
              KA
            </div>
            <div className="pt-0.5">
              <p className="text-[0.68rem] uppercase tracking-[0.42em] text-slate-400">
                ArkNexus Compliance
              </p>
              <p className="mt-1 text-sm text-slate-300">
                Public SMS program disclosure
              </p>
            </div>
          </div>

          <div className="hidden rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-[0.7rem] uppercase tracking-[0.32em] text-slate-300 md:block">
            {accent}
          </div>
        </div>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,1.55fr)_minmax(320px,0.72fr)]">
          <article className="rounded-[2.5rem] border border-white/10 bg-white/[0.055] p-6 shadow-[0_24px_90px_rgba(0,0,0,0.4)] backdrop-blur-2xl sm:p-8 lg:p-10">
            <div className="mb-7 flex flex-wrap items-center gap-3">
              <span className="rounded-full border border-white/10 bg-white/[0.05] px-3 py-1 text-xs uppercase tracking-[0.3em] text-slate-300">
                {eyebrow}
              </span>
              <span className="rounded-full border border-amber-400/20 bg-amber-400/10 px-3 py-1 text-xs uppercase tracking-[0.22em] text-amber-100">
                SMS compliance page
              </span>
            </div>

            <h1 className="max-w-3xl font-serif text-4xl font-semibold tracking-tight text-white sm:text-5xl lg:text-6xl">
              {title}
            </h1>
            <p className="mt-5 max-w-3xl text-base leading-8 text-slate-300 sm:text-lg">
              {description}
            </p>

            <div className="mt-8 grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-white/10 bg-white/[0.035] px-4 py-3">
                <p className="text-[0.65rem] uppercase tracking-[0.3em] text-slate-400">Channel</p>
                <p className="mt-1 text-sm text-white">SMS</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/[0.035] px-4 py-3">
                <p className="text-[0.65rem] uppercase tracking-[0.3em] text-slate-400">Brand</p>
                <p className="mt-1 text-sm text-white">Karma by ArkNexus</p>
              </div>
              <div className="rounded-2xl border border-white/10 bg-white/[0.035] px-4 py-3">
                <p className="text-[0.65rem] uppercase tracking-[0.3em] text-slate-400">Status</p>
                <p className="mt-1 text-sm text-white">Public page</p>
              </div>
            </div>

            <div className="mt-8 space-y-5">{children}</div>

            <div className="mt-10 border-t border-white/10 pt-6">
              <div className="flex flex-wrap gap-3">
                {footerLinks.map((link) => (
                  <Link
                    key={link.href}
                    href={link.href}
                    className="rounded-full border border-white/10 bg-white/[0.045] px-4 py-2 text-sm text-slate-200 transition hover:border-amber-300/40 hover:bg-amber-300/10 hover:text-white"
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          </article>

          <aside className="space-y-6">
            <section className="rounded-[2.25rem] border border-white/10 bg-[#11131a]/85 p-6 shadow-[0_18px_60px_rgba(0,0,0,0.28)] backdrop-blur-2xl">
              <p className="text-xs uppercase tracking-[0.32em] text-amber-200/80">Program brief</p>
              <h2 className="mt-3 text-xl font-semibold text-white">{sidebarTitle}</h2>
              <div className="mt-5 space-y-4 text-sm leading-7 text-slate-300">{sidebarBody}</div>
            </section>

            <section className="rounded-[2.25rem] border border-white/10 bg-white/[0.035] p-6 shadow-[0_18px_60px_rgba(0,0,0,0.2)]">
              <p className="text-xs uppercase tracking-[0.32em] text-slate-400">Contact controls</p>
              <div className="mt-4 space-y-3 text-sm leading-7 text-slate-300">
                <p>Help keyword: <span className="text-white">HELP</span></p>
                <p>Opt-out keyword: <span className="text-white">STOP</span></p>
                <p>Phone: <span className="text-white">+1 484 806 1591</span></p>
              </div>
            </section>
          </aside>
        </section>
      </div>
    </main>
  );
}
