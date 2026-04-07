# CheapLocal

*Converted from: CheapLocal.pdf*



---
*Page 1*


Open in app
Search Write
Member-only story
I Deployed My Own
OpenClaw AI Agent in 4
Minutes — It Now Runs
My Life From a $5
Server
There’s a moment every developer knows. The
one where you see a tool and think “okay this
is cool but it’s probably overhyped” — and
then three days later you realize you haven’t
opened half your apps because the tool —
OpenClaw — replaced them.
Phil | Rentier Digital 9 min · Feb 12,
Following
Automation read 2026
738 16


---
*Page 2*


OpenClaw did that to me.
O ne WhatsApp message to clear 200+ emails.
One Telegram command to monitor all my
GitHub repos. A weekly cron job set up in natural
language while I was walking my dog. And the
thing that really got me: a proactive reminder
about a deadline I’d casually mentioned two days
earlier — because this agent remembers
everything.
🚨
If Medium’s paywall is giving you the “pay me or
perish” screen — here’s the friend link. Because the
only wall between you and your own personal Jarvis
should be the one you choose.
100,000 GitHub stars in eight weeks. The fastest-
growing open-source project anyone can
remember. And the wildest part? I had it running
on my own server in under 5 minutes, for less than
the price of a coffee per month.


---
*Page 3*


Here’s exactly how — and why every developer
should do this before the weekend.
What the Hell is OpenClaw (And Why Is
Everyone Losing Their Mind)
If you’ve been anywhere near tech Twitter this past
🦞
month, you’ve seen the lobster emoji
everywhere.
OpenClaw (formerly Clawdbot, then Moltbot — the
project changes names more often than I refactor
my side projects) is an open-source AI agent
created by Peter Steinberger that does something


---
*Page 4*


deceptively simple: it runs on your own hardware
and talks to you through the chat apps you already
use.
WhatsApp. Telegram. Discord. Slack. Signal.
iMessage. You pick.
But here’s where it gets interesting. This isn’t
another chatbot that tells you jokes and generates
haikus. OpenClaw actually does things. It reads
your files. Manages your calendar. Monitors your
GitHub repos. Executes shell commands. Controls
your smart home. Checks you in for flights. And it
remembers everything across conversations with
persistent memory.
what Siri should have been
Think of it as having a junior developer who never
sleeps, works for free (well, for API tokens), and is
available on every messaging platform
simultaneously.


---
*Page 5*


The “Lobster” workflow shell chains multiple
capabilities into pipelines. You send one message
like “Every Monday 9 AM, pull GitHub issues tagged
urgent, create a Notion page with summary, send to
#dev-team Slack” — and it just… does it. It searches
its skill library, finds the right integration, installs
it if needed, configures API access, and starts
working.
Over 50 integrations. Community-built skills on
ClawHub. And it can even write its own skills
when it doesn’t find what it needs. One user
described it as “what Siri should have been.”
Another put it better: “It’s like running Linux vs
Windows 20 years ago. You’re in control.”
The Problem: Self-Hosting Used to Be a
Pain
Here’s where most people give up.
The typical OpenClaw setup involves SSH-ing into
a server, installing Docker, pulling images,


---
*Page 6*


configuring environment variables, setting up
firewalls, creating SSH tunnels… You know the
drill. About 20 commands and 30–45 minutes of
terminal work if everything goes right.
And let’s be honest — when does everything go
right on a fresh VPS at 3 AM?
Running it on your laptop works for testing, but
your AI agent goes offline every time your
MacBook goes to sleep. Running it on a Raspberry
Pi is cool for the nerd cred, but your agent needs to
be always on — responding to messages whether
you’re awake or not. That’s the whole point.
You need a VPS. Running 24/7. With enough RAM
to not crash (OpenClaw needs a minimum of 2GB,
4GB recommended). And ideally with a one-click
setup so you can skip the part where you debug
Docker networking at midnight.
Enter Contabo’s One-Click OpenClaw
Add-On


---
*Page 7*


Contabo recently dropped something that made
me do a double take: a free one-click OpenClaw
add-on for their VPS and VDS plans. Not a paid
add-on. Not a “free trial.” A free pre-configured
deployment that handles the entire Docker setup
automatically.
Here’s the actual process — and I timed it:
Step 1: Order a VPS — Head to the Contabo
OpenClaw hosting page. Pick the Cloud VPS 10
(the entry-level plan). We’re talking 4 vCPU
cores, 8 GB RAM, and 75 GB NVMe storage.
That’s way more than OpenClaw needs, with
headroom for other services.
Step 2: Select OpenClaw during your order —
There’s literally a checkbox. Check it. That’s your
“one click.”
Step 3: Wait for provisioning — Mine took about
3 minutes. Your mileage may vary.


---
*Page 8*


Step 4: SSH in and run the onboarding wizard —
OpenClaw doesn’t expose a public web interface
by default (which is good — more on that later).
You connect via SSH and the onboarding wizard
starts automatically. If it doesn’t, one command:
openclaw onboard --install-daemon
Step 5: Connect your messaging channels — The
wizard walks you through connecting Telegram,
WhatsApp, Discord, or whatever you prefer. Pick
your LLM provider (Claude, GPT, local models
via Ollama — your choice), enter your API key,
and you’re live.
Total time from clicking “Order” to sending my
first message to my agent on Telegram: under 5
minutes.
The price? The Cloud VPS 10 starts at €5.36/month
(roughly $4.95 USD). The OpenClaw add-on itself
costs nothing — you only pay for the server. Your
AI assistant running 24/7 for less than a fancy
coffee.


---
*Page 9*


For power users, Contabo offers beefier tiers too —
Cloud VPS 20 at €8.33/month for heavier
workloads, and up from there. But for a personal
OpenClaw instance, the entry-level plan is more
than enough.
The First 48 Hours: What My Agent
Actually Did
Let me walk you through what happened once I
had OpenClaw running.
Hour 1 — Email triage. I connected Gmail and
told my agent via WhatsApp: “Clean up my inbox.
Archive everything that’s not actionable.
Summarize the important ones.” It processed
hundreds of emails and sent me a neat
summary. Then I told it to set up a weekly cron
job to do the same thing every Sunday night.
Done.
Hour 3 — GitHub monitoring. I pointed it at my
repos with a simple message: “Monitor my
GitHub repos for new issues and PRs. Send me a


---
*Page 10*


summary on Telegram if anything tagged urgent
comes in.” It found the GitHub skill, configured
it, and started watching.
Hour 8 — Smart routing. I configured model
routing so it uses Haiku for simple tasks (quick
answers, basic automation) and Sonnet/Opus for
complex work (code review, long-form analysis).
This keeps API costs manageable — and
Anthropic’s auto-applied prompt caching helps
cut repeat costs further.
Hour 24 — It started surprising me. OpenClaw
has this “heartbeat” feature where it proactively
reaches out during check-ins. I got a Telegram
message I didn’t expect: a reminder about a
deadline I’d mentioned in passing two days
earlier. The persistent memory across sessions is
no joke.
Hour 48 — I stopped opening half my apps.
Calendar? Ask the agent. Todo list? Ask the
agent. Quick web search? Agent. It became the


---
*Page 11*


single interface for a dozen tools I used to
context-switch between.
One user on X put it perfectly: “It feels magical.
Built a website from my phone in minutes.” Another
turned a dusty Mac Studio into “a 24/7 AI agent
helping me run three businesses.”
The Security Elephant in the Room (Don’t
Skip This)
Now here’s where I put on my serious face,
because this matters.
⚠
Last week, SecurityScorecard’s STRIKE team
discovered over 135,000 internet-exposed
OpenClaw instances. That number was 40,000
when they published their report and it
skyrocketed within hours. Over 50,000 were
vulnerable to a known remote code execution bug
that was already patched. Over 12,000 instances
had public exploit code available.


---
*Page 12*


The headline from The Register didn’t mince
words: “Another OpenClaw cybersecurity disaster.”
Here’s what’s happening: OpenClaw, by default,
binds to 0.0.0.0:18789 — meaning it listens on all
network interfaces, including the public internet.
People are deploying it, not changing that default,
and walking away. When someone compromises
your OpenClaw instance, they get access to
everything it can access: your credential store,
filesystem, messaging platforms, browser, and
personal data cache.
On top of that, Bitdefender found nearly 900
malicious skills on ClawHub (roughly 20% of all
packages). VirusTotal has since partnered with
OpenClaw to scan skills automatically, but the
supply chain risk is real.
Here’s what you need to do (and what the Contabo
setup makes easier):


---
*Page 13*


Bind to localhost. Change the default from
0.0.0.0 to 127.0.0.1. This is step one, non-
negotiable.
Use SSH tunnels to access the Control UI. The
command is straightforward: ssh -N -L
18789:127.0.0.1:18789 root@<your-server-ip> —
this forwards the web interface to your local
machine without exposing it publicly.
Set up a firewall. UFW on Ubuntu is your friend.
Block everything except SSH.
Enable authentication. The 2026.2.6 release
made authentication mandatory for the web UI.
Make sure you’re on the latest version.
Vet your skills. Don’t install random skills from
ClawHub without checking them. The VirusTotal
integration helps, but trust-but-verify is the right
posture.
Use the official Ansible playbook if you want
hardened setup: it includes Tailscale VPN, UFW
firewall, and Docker isolation out of the box.


---
*Page 14*


The Contabo deployment doesn’t expose a public
web interface by default, which is already a step in
the right direction. But the configuration is your
responsibility after installation. Take the 15
minutes to lock it down. Your future self will thank
you.
The Real Cost Breakdown
Let’s talk money, because the pricing on this whole
stack is surprisingly sane.
Infrastructure: €5.36/month on Contabo’s Cloud
VPS 10. That’s your 24/7 server. Done.
The real cost is the AI model API. This varies
wildly depending on your usage and model choice.
Smart model routing helps: use cheap models
(Claude Haiku, GPT-4o Mini) for simple tasks,
expensive ones (Claude Opus, GPT-4) for complex
work. Enable prompt caching. The latest
OpenClaw releases added a token consumption


---
*Page 15*


dashboard so you can actually see where your
money goes.
Or go fully local. If you have 16GB+ RAM to spare,
you can run local LLMs via Ollama for zero API
cost. The trade-off is quality — a local 7B model
won’t match Claude Opus — but for basic
automation tasks, it works.
Realistic estimate for moderate use with smart
routing: $15–30/month total (server + API). That’s
for a personal AI agent running 24/7 across all your
messaging platforms, with persistent memory, 50+
integrations, and the ability to write its own skills.
Compare that to managed solutions like official
OpenClaw Hosting at $29+/month (without the VPS
flexibility), or fully managed alternatives at $19–
99/month. The Contabo self-hosted route is the
best value if you’re comfortable with basic server
management — and if you’re reading this article,
you probably are.


---
*Page 16*


Who This Is Actually For
Let me be direct: OpenClaw isn’t for everyone. If
you’re not comfortable running ssh commands
and editing config files, the managed hosting
options exist for a reason.
But if you’re a developer who wants a personal AI
agent that actually executes tasks, monitors repos,
and runs Claude Code loops from your phone —
this is your new best friend.
If you’re an indie hacker juggling multiple projects
and tired of context-switching between 15 apps —
one WhatsApp message to your agent replaces half
of them.
If you’re a SaaS builder who already runs n8n,
Supabase, or other self-hosted tools — OpenClaw
fits right into that stack on the same VPS.
And if you’re the kind of person who names their
AI agent Jarvis and gets daily briefings via


---
*Page 17*


Telegram — welcome home. We’ve been waiting
for you.
Get Started
The fastest path from “I want this” to “my AI agent
is responding on Telegram” is about 5 minutes:
→ Deploy OpenClaw on Contabo — One-Click
Setup
Pick the Cloud VPS 10, check the OpenClaw box,
and follow the onboarding wizard. Remember to
lock down security before you walk away.
The Contabo blog also has a detailed guide on what
OpenClaw is and how to set it up if you want to
read more before diving in.
If this saved you the 3 AM rabbit hole I went through
— follow me for more field-tested guides on building
with AI agents, Claude Code, and self-hosted tools.


---
*Page 18*


Next up: how I connected OpenClaw to my Convex
backend to build a self-healing SaaS monitoring
pipeline. You don’t want to miss that one.
Openclaw Openclaw Tutorial AI Agent Ai Agent Tutorial
Openclaw Bot
Written by Phil | Rentier Digital
Following
Automation
1.1K followers · 1 following
Claude Code in production. What works, what
breaks, what ships.
Responses (16)
To respond to this story,
get the free Medium app.


---
*Page 19*


nova motum think•ai - Volker Kohl he/him
Feb 14 (edited)
The article correctly highlights the advantages and an obvious mistake -
exposing OpenClaw to the public internet - but it stops there. Running
an autonomous AI agent with filesystem access, shell execution, API
tokens to Gmail and GitHub, and… more
102 3 replies
Uriah Dailey
5 days ago
BTW folks this article had been up for about a full day and every
comment so far is about security. Take that seriously. Read the comments
for info how to protect yourself.
34
Dr Shibichakravarthy Kannan MBBS PhD
6 days ago
It's a security nightmare, everyday we are learning some new
vulnerability and hackers rejoice. Now that openclaw is in the custody of
OpenAI let's see what the future brings. I am not jumping on the band
wagon until it is deemed safe for all scenarios. Which is highly unlikely
21
See all responses


---
*Page 20*


More from Phil | Rentier Digital Automation
Phil | Rentier Digital Automation Phil | Rentier Digital Automation
33 OpenClaw 21 OpenClaw
A t ti Y C A t ti N b d
While you were reading this After I published “33
titl ’ l b t O Cl A t ti ”
Feb 1 Feb 14
Phil | Rentier Digital Automation Phil | Rentier Digital Automation
Y Combinator Just Told I Tried Running
Y E tl H t O l (
Your agency is about to “Run your own AI assistant
b ft l ll ! N API t ! P i !
Feb 5 Jan 25


---
*Page 21*


See all from Phil | Rentier Digital Automation
Recommended from Medium
Phil | Rentier Digital Automation In by
Activated Thin… Shane Coll…
21 OpenClaw
Why the Smartest
A t ti N b d
P l i T h A
After I published “33
The water is rising fast, and
O Cl A t ti ”
f i f Ch tGPT
Feb 14 Feb 13
Steve Yegge In by
CodeX MayhemCode


---
*Page 22*


The Anthropic Hive Why Thousands Are
Mi d B i M Mi i t
As you’ve probably noticed, Something strange happened
thi i h i i l 2026 A l t
Feb 15
Feb 6
In by Will Lockett
AI Advanc… Jose Crespo, P…
Musk Just Started The
Anthropic is Killing
W lkb k Of Th
Bit i
Overpromise and
The AI-native currency
d d li t i
l d i t hidi i
6d ago Feb 15
See more recommendations