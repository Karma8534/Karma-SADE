# SecureClaw_ Dual stack open-source security plugin and skill for OpenClaw - Help Net Security

*Converted from: SecureClaw_ Dual stack open-source security plugin and skill for OpenClaw - Help Net Security.PDF*



---
*Page 1*


Help Net Security newsletters: Daily and weekly news, cybersecurity jobs, open source projects,
breaking news – subscribe here!
Mirko Zorz, Director of Content, Help Net Security Share
February 18, 2026
SecureClaw: Dual stack open-source security plugin and
skill for OpenClaw
AI agent frameworks are being used to automate work that involves tools, files, and external
services. That type of automation creates security questions around what an agent can access,
what it can change, and how teams can detect risky behavior.
SecureClaw is an open-source project that adds security auditing and rule-based controls to
OpenClaw agent environments. The tool is published by Adversa AI and is designed to work with
OpenClaw and related agents such as Moltbot and Clawdbot.


---
*Page 2*


SecureClaw in action
Alex Polyakov, co-founder of Adversa AI, told Help Net Security the current ecosystem around
OpenClaw security is fragmented.
“Most OpenClaw security tools I’ve seen solve one piece of the problem,” Polyakov said. “One tool
validates skills for supply chain risks. Another does DLP. Another hardens tool permissions. They’re


---
*Page 3*


point solutions tackling individual threats in isolation.”
A plugin plus a skill
SecureClaw is structured as two components: a plugin and a skill.
The plugin is designed to integrate into OpenClaw’s plugin system and provides automated security
auditing and hardening functions. The skill includes a set of rule definitions and scripts intended to
run alongside an agent.
SecureClaw covers configuration-level checks and operational controls that apply during agent use.
Polyakov said this two-part structure is meant to solve a weakness in many other approaches.
“The other critical difference is architecture. Most competing tools are skill-only, meaning the
security logic lives inside the agent’s context window as natural language instructions,” he said. “The
problem is that skills can be overridden by prompt injection: if an attacker can manipulate the
agent’s input, they can tell it to ignore the security skill.”
Polyakov said SecureClaw is designed as a layered approach.
“SecureClaw uses a two-layer defense model: a code-level plugin that enforces hardening at the
gateway and configuration level combined with a behavioral skill that gives the agent real-time
awareness,” he said. “You need both layers.”
Automated auditing and hardening
SecureClaw includes 55 audit checks that evaluate an OpenClaw installation for security conditions.
The project also includes hardening modules intended to apply changes based on audit findings.
The repository includes scripts for running audits and applying hardening actions through a
command-line workflow.
Polyakov said the project was built to align systematically with agent security frameworks.
“SecureClaw is the first to address the full attack surface systematically, mapped to all 10 OWASP
Agentic Security Initiative (ASI) Top,” he said. “That’s not a marketing checkbox; it means we
designed protections for each documented threat class rather than patching whichever vulnerability
made headlines that week.”


---
*Page 4*


Behavioral rules and pattern matching
SecureClaw also includes 15 behavioral rules packaged in the skill component. These rules are
designed to influence how an agent behaves when interacting with prompts, tools, and outputs.
The skill includes nine scripts and four JSON pattern databases used to support checks and
detection logic.
Polyakov said performance constraints shaped how SecureClaw was designed, particularly around
prompt length.
“Something I’m personally proud of is context window optimization. This is a technical detail that
matters more than people realize,” Polyakov said. “It’s easy to write a massive security skill prompt
that tries to filter everything, but in practice, large prompts fail for three reasons. First, LLMs lose
focus on instructions that appeared early in a long context window, the agent literally forgets its
security directives mid-conversation. Second, every token spent on security instructions is a token
not available for the agent’s actual functionality. Third, longer prompts increase latency and API cost
on every single interaction.”
“We optimized SecureClaw’s skill to approximately 1,150 tokens,” he added. “It directly impacts
whether the security instructions actually get followed by the model, how much the user pays per
interaction, and how much room the agent has to do its real job.”
Framework mapping
Polyakov said enterprise adoption of OpenClaw is expected to grow and SecureClaw is being
positioned to meet those requirements.
“With the OpenAI acquisition, we expect OpenClaw adoption to accelerate significantly in enterprise
environments,” he said. “We’ve already prepared for this: our latest update added formal mappings
to MITRE ATLAS agentic AI attack techniques (CoSAI) guidance, along with threat modeling
documentation, the kind of artifacts enterprise security teams need for compliance and risk
assessment.”
He said future work will go beyond skill-level guardrails.
“Looking ahead, we have a substantial roadmap focused on infrastructure-level hardening and
rigorous Red Teaming this solution with our AI Red Teaming platform,” Polyakov said.


---
*Page 5*


SecureClaw is available for free on GitHub.
Must read:
40 open-source tools redefining how security teams secure the stack
Firmware scanning time, cost, and where teams run EMBA
Subscribe to the Help Net Security ad-free monthly newsletter to stay informed on the essential
open-source cybersecurity tools. Subscribe here!
More about
Artificial intelligence cybersecurity open source OpenClaw plugin
Share
Featured news
China-linked hackers exploited Dell zero-day since 2024 (CVE-2026-22769)
The era of the Digital Parasite: Why stealth has replaced ransomware
Scammers exploit trust in Atlassian Jira to target organizations
Webinar: Power up your ISC2 exam prep


---
*Page 6*


Resources
Download: Evaluating Password Monitoring Vendors
eBook: A quarter century of Active Directory
Download: Strengthening Identity Security whitepaper
Don't miss
China-linked hackers exploited Dell zero-day since 2024 (CVE-2026-22769)
The era of the Digital Parasite: Why stealth has replaced ransomware
Scammers exploit trust in Atlassian Jira to target organizations
Notepad++ secures update channel in wake of supply chain compromise
One stolen credential is all it takes to compromise everything
CYBERSECURITY NEWS
HNS Daily HNS Newsletter


---
*Page 7*


Daily newsletter sent Monday-Friday Weekly newsletter sent on Mondays
InSecure Newsletter Breaking news
Editor's choice newsletter sent twice a Periodical newsletter released when
month there is breaking news
Cybersecurity jobs Open source
Weekly newsletter listing new Monthly newsletter focusing on open
cybersecurity job positions source cybersecurity tools
Please enter your e-mail address Subscribe
I have read and agree to the terms & conditions
© Copyright 1998-2026 by Help Net Security
Read our privacy policy|About us|Advertise
Follow us