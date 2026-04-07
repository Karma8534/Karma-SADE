import type { Metadata } from 'next';
import Link from 'next/link';
import { CompliancePageShell } from '@/components/compliance-page-shell';

export const metadata: Metadata = {
  title: 'Karma SMS Terms and Conditions',
  description: 'Terms and conditions for the Karma by ArkNexus SMS program, including consent, message frequency, and opt-out terms.',
};

export default function KarmaSmsTermsPage() {
  return (
    <CompliancePageShell
      eyebrow="Terms and Conditions"
      title="Karma SMS Terms and Conditions"
      description="These terms describe the SMS program, consent requirements, message frequency, rates, and the subscriber controls available to users."
      accent="Terms"
      sidebarTitle="Subscriber terms"
      sidebarBody={
        <>
          <p>Consent is required before messages are sent.</p>
          <p>Message and data rates may apply.</p>
          <p>HELP and STOP keywords are supported for user control.</p>
        </>
      }
      footerLinks={[
        { href: '/karma-sms', label: 'Program page' },
        { href: '/karma-sms-privacy', label: 'Privacy Policy' },
      ]}
    >
      <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
        <p className="text-xs uppercase tracking-[0.28em] text-amber-200/80">Program details</p>
        <p className="mt-3 text-sm leading-7 text-slate-300">
          <span className="font-semibold text-white">Program name:</span> Karma SMS
          <br />
          <span className="font-semibold text-white">Program description:</span> Karma by ArkNexus sends customer
          support, project updates, and system notifications by SMS to users who have opted in.
        </p>
      </section>

      <section className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-amber-200/80">Consent</p>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            Consent to receive SMS messages is not a condition of purchase. By opting in, you agree to receive recurring
            automated text messages from Karma by ArkNexus at the mobile number you provided.
          </p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
          <p className="text-xs uppercase tracking-[0.28em] text-amber-200/80">Frequency and rates</p>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            Message frequency varies based on user interaction. Message and data rates may apply.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
        <p className="text-xs uppercase tracking-[0.28em] text-amber-200/80">Support and opt-out</p>
        <p className="mt-3 text-sm leading-7 text-slate-300">
          For help, reply HELP or call <span className="font-semibold text-white">+1 484 806 1591</span>. To opt
          out, reply STOP.
        </p>
      </section>
    </CompliancePageShell>
  );
}
