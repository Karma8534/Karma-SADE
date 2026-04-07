import type { Metadata } from 'next';
import Link from 'next/link';
import { CompliancePageShell } from '@/components/compliance-page-shell';

export const metadata: Metadata = {
  title: 'Karma SMS Program',
  description: 'Public disclosure for the Karma by ArkNexus SMS program, including opt-in, opt-out, and message details.',
};

export default function KarmaSmsPage() {
  return (
    <CompliancePageShell
      eyebrow="Karma SMS Program"
      title="Karma SMS Program"
      description="This page explains how users opt in to receive SMS messages from Karma by ArkNexus, what the messages cover, and how to review the related policy pages."
      accent="ArkNexus / SMS"
      sidebarTitle="Program summary"
      sidebarBody={
        <>
          <p>Program purpose: customer support, project updates, and system notifications.</p>
          <p>Opt-in method: text KARMA to +1 484 806 1591.</p>
          <p>Delivery: recurring automated SMS messages, frequency based on user interaction.</p>
        </>
      }
      footerLinks={[
        { href: '/karma-sms-terms', label: 'Terms and Conditions' },
        { href: '/karma-sms-privacy', label: 'Privacy Policy' },
      ]}
    >
      <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/80">Overview</p>
        <p className="mt-3 text-sm leading-7 text-slate-300">
          Karma by ArkNexus provides conversational support, project updates, and system notifications by SMS.
        </p>
      </section>

      <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/80">Opt in</p>
        <p className="mt-3 text-sm leading-7 text-slate-300">
          To subscribe, text <span className="font-semibold text-white">KARMA</span> to{' '}
          <span className="font-semibold text-white">+1 484 806 1591</span>.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/80">Message terms</p>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            By opting in, you agree to receive recurring SMS messages from Karma by ArkNexus. Message frequency varies
            based on your interaction. Message and data rates may apply.
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/80">Short code actions</p>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            Reply HELP for help. Reply STOP to opt out.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-cyan-400/20 bg-cyan-400/8 p-5">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-200/80">Legal links</p>
        <div className="mt-3 flex flex-wrap gap-3 text-sm">
          <Link href="/karma-sms-terms" className="rounded-full border border-cyan-300/20 bg-white/5 px-4 py-2 text-slate-100 transition hover:bg-cyan-300/10">
            Terms and Conditions
          </Link>
          <Link href="/karma-sms-privacy" className="rounded-full border border-cyan-300/20 bg-white/5 px-4 py-2 text-slate-100 transition hover:bg-cyan-300/10">
            Privacy Policy
          </Link>
        </div>
      </section>
    </CompliancePageShell>
  );
}
