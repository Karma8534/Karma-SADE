import type { Metadata } from 'next';
import Link from 'next/link';
import { CompliancePageShell } from '@/components/compliance-page-shell';

export const metadata: Metadata = {
  title: 'Karma SMS Privacy Policy',
  description: 'Privacy policy for the Karma by ArkNexus SMS program, including data collection, use, and opt-out details.',
};

export default function KarmaSmsPrivacyPage() {
  return (
    <CompliancePageShell
      eyebrow="Privacy Policy"
      title="Karma SMS Privacy Policy"
      description="This page explains what information Karma by ArkNexus collects for SMS communications, how it is used, and how it is protected."
      accent="Privacy"
      sidebarTitle="Data handling"
      sidebarBody={
        <>
          <p>We collect your mobile number and SMS interaction data only to deliver the requested messaging service.</p>
          <p>Marketing sharing is excluded.</p>
          <p>Opt-out and support instructions are provided on every page and in the SMS experience.</p>
        </>
      }
      footerLinks={[
        { href: '/karma-sms', label: 'Program page' },
        { href: '/karma-sms-terms', label: 'Terms and Conditions' },
      ]}
    >
      <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
        <p className="text-xs uppercase tracking-[0.28em] text-sky-200/80">Information collected</p>
        <p className="mt-3 text-sm leading-7 text-slate-300">
          Karma by ArkNexus collects your mobile number and SMS interaction data to provide conversational support,
          project updates, and system notifications that you request.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-sky-200/80">Use of information</p>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            Message frequency varies based on your interaction. Message and data rates may apply.
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-sky-200/80">Sharing limits</p>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            No mobile information will be shared with third parties or affiliates for marketing or promotional
            purposes. Text messaging originator opt-in data and consent will not be shared with any third parties
            except vendors that help us provide messaging services.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
        <p className="text-xs uppercase tracking-[0.28em] text-sky-200/80">Help and opt-out</p>
        <p className="mt-3 text-sm leading-7 text-slate-300">
          For help, reply HELP or call <span className="font-semibold text-white">+1 484 806 1591</span>. To opt
          out, reply STOP.
        </p>
      </section>
    </CompliancePageShell>
  );
}
