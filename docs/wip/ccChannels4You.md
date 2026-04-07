# ccChannels4You

*Converted from: ccChannels4You.pdf*



---
*Page 1*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Member-only story
I Tested (New) Claude Code
Channels (Real OpenClaw Killer)
Joe Njenga Following 9 min read · 3 days ago
319 6
Claude Code channels the latest feature designed to replace OpenClaw in
Claude Code workflows, now giving you the freedom to launch from your
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 1/34


---
*Page 2*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
favourite app.
If you’ve been using OpenClaw to message your AI agent from Telegram or
Discord, you know the complex setup, security concerns, and the recent
Anthropic block on subscription tokens, making the experience frustrating.
Anthropic just shipped a similar but native solution.
If you are not a PAID Medium Member, read the
article here for FREE, but please consider joining
Medium to support my work — Thank you!
Here’s my first test message in a chat app for my Claude Code session, and
getting a response back
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 2/34


---
*Page 3*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
That’s a two-way conversation between my messaging app and a running
Claude Code session.
When I set this up with Telegram. I sent a task, Claude will pick it up, do the
work, and reply directly in Telegram.
This is Claude Code channels working!
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 3/34


---
*Page 4*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
So,
What is a Claude Code Channel?
A channel is an MCP server that pushes events into your running Claude
Code session.
You can send messages from Telegram or Discord, and Claude reacts while
you’re away, that's the same process as setting up OpenClaw to use Claude Code
right from your phone.
The flow is :
You message your bot on Telegram or Discord
The channel plugin forwards that message into your Claude Code session
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 4/34


---
*Page 5*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Claude reads it, does the work, and replies through the same channel
The reply shows up on your phone
Currently, Anthropic supports two platforms in the research preview —
Telegram and Discord.
There’s also a localhost demo called Fakechat for testing before you connect real
platforms.
Before we move to the setup and testing, we need to see how this solves the
OpenClaw problem.
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 5/34


---
*Page 6*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
OpenClaw Problem
OpenClaw became the fastest-growing open-source AI project for a good
reason. Developers want to talk to their AI agent from their phone; it’s a real
need.
Ideally, the process is to send a task from Telegram while commuting, and
check the build status from Discord while away from the desk.
But OpenClaw came with baggage:
Security risks — Researchers found over 135,000 exposed instances on the
public internet, with 50,000+ vulnerable to remote code execution. A ClawHub
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 6/34


---
*Page 7*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
audit revealed that around 12% of community skills were malicious.
Complex setup — You needed dedicated hardware (many developers bought
Mac Minis just for this), Docker configurations, and hours of tinkering. I did a
demo in earlier tutorials, setting it up on a Mac Mini and Windows.
Subscription block — Anthropic blocked third-party tools from riding on
Claude Pro/Max subscription tokens. OpenClaw’s cheapest path to Claude was
no longer working.
Founder departure — Peter Steinberger joined OpenAI, and the project moved
to a foundation. The future project direction remains uncertain.
Claude Code Channels addresses all of this natively. You don’t need third-party
agents, exposed instances, or subscription hacks.
You also get Anthropic’s security model built in; sender allowlists, per-
session opt-in with --channels, and enterprise controls for teams.
Since this is a complex topic, I will break it down in a series. In the series, I’ll
take you through the complete setup for Telegram and Discord, starting with a
quick Fakechat demo to understand the flow before connecting to platforms.
For this first article, we’ll cover:
Prerequisites and setting up all dependencies
Setting up the Fakechat demo (understand the flow first)
In the next tutorials will go deep into specific details of :
Connecting a Telegram bot to Claude Code (step by step)
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 7/34


---
*Page 8*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Connecting a Discord bot to Claude Code (step by step)
Security and access control (how to lock it down)
Channels vs OpenClaw (honest comparison)
Let’s start with the Fakechat demo.
Claude Code Channels Getting Started
The first step is to ensure Claude Code is updated and all other
dependencies are set up properly.
Prerequisites
Before setting up any channel, you need two things in place.
Claude Code v2.1.80 or later — Channels won’t work on older versions
Bun Runtime — All channel plugins run on Bun
Step 1: Verify Claude Code Version
Run this in your terminal:
claude --version
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 8/34


---
*Page 9*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Expected output: Version 2.1.80 or later
If your version is older, update first:
claude update
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 9/34


---
*Page 10*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Then check again using the same command.
Step 2: Verify Bun is Installed
Run:
bun --version
Open in app
Search Write
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 10/34


---
*Page 11*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Search Write
If you see a version number, you’re good; move to Step 3.
If it fails, as in my case above, install Bun:
Mac/Linux
curl -fsSL https://bun.sh/install | bash
Windows (PowerShell):
irm bun.sh/install.ps1 | iex
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 11/34


---
*Page 12*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
After installing, verify:
bun --version
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 12/34


---
*Page 13*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
One more thing; channels require a claude.ai login. Console and API key
authentication won’t work here. If you’re on a Team or Enterprise plan, your
admin needs to enable channels in managed settings before you can use them.
Step 3: Start Claude Code
You should still be inside the project folder, in my case its channels folder.
Start a Claude Code session:
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 13/34


---
*Page 14*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Wait for Claude Code to load.
If you get an auth error — make sure you’re logged in with a claude.ai account
(not API key or Console). Run /login if needed.
Fakechat — Test the Flow First
Before connecting to Telegram or Discord, I recommend starting with
Fakechat.
It’s a localhost demo that runs a chat UI in your browser with nothing to
authenticate and no external service to configure.
It shows you how the channel message flow works before you deal with bot
tokens and pairing codes.
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 14/34


---
*Page 15*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Step 1: Install the Fakechat Plugin
Start a Claude Code session and run:
/plugin install fakechat@claude-plugins-official
You will be presented with the plugin installation options. In my case, I will
install it in the User Scope:
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 15/34


---
*Page 16*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
If successful, you should see the message to reload to activate:
✓ Installed fakechat. Run /reload-plugins to activate.
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 16/34


---
*Page 17*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
To confirm the FakeChat plugin is enabled, run the /plugin command again
and navigate to the installed tab, and confirm.
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 17/34


---
*Page 18*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Installation Error
If you get an error about the marketplace not being found, run this first:
/plugin marketplace add anthropics/claude-plugins-official
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 18/34


---
*Page 19*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Step 2: Restart with Channels Enabled
Exit Claude Code, then restart with the --channels flag:
claude --channels plugin:fakechat@claude-plugins-official
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 19/34


---
*Page 20*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Look for a message confirming the Fakechat channel is active, as you can see
above. The Fakechat server starts and its listening.
Step 3: Open Fakechat in Your Browser
Keep the terminal running. Do NOT close it.
Open your browser and go to:
http://localhost:8787
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 20/34


---
*Page 21*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
You should see a simple chat interface as above. When you get to this step, the
setup is complete and ready to test.
Type a message:
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 21/34


---
*Page 22*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
hey, what's in my working directory?
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 22/34


---
*Page 23*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Hit send. Now watch your Claude Code terminal.
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 23/34


---
*Page 24*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
The message arrives as a <channel source="fakechat"> event. Claude reads it,
does the work, and calls Fakechat's reply tool and the answer shows up
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 24/34


---
*Page 25*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Quick Note on Permissions
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 25/34


---
*Page 26*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
If Claude hits a permission prompt while processing a channel message and
you’re not at the terminal, the session pauses.
It waits for your local approval before continuing.
For unattended use, there’s --dangerously-skip-permissions but only use this
in environments you fully trust. The name says it all.
Final Thoughts
After testing Fakechat, the channel flow works as I expected.
The message goes from the browser demo, into your Claude Code session,
Claude processes it, and the response comes back.
Fakechat demo proves the concept on localhost, but the value is when you
connect to Telegram or Discord and start sending tasks from your phone to a
running Claude Code session.
I also hope they can add support for platforms such as WhatsApp, Signal, and
more.
Keep in mind, Claude Code Channels is still in research preview. The --
channels flag syntax and protocol may change based on feedback.
Only plugins from the Anthropic-maintained allowlist are accepted during
the preview period.
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 26/34


---
*Page 27*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
But even at this early stage, it’s clear this is very useful.
So, in the next series, we will cover
1: Connecting Telegram to Claude Code
I’ll walk through the full Telegram setup, from creating a bot with BotFather
to pairing your account and sending real coding tasks from your phone.
2: Connecting Discord to Claude Code
The Discord setup, including bot creation, permissions, and the extra tools
Discord offers over Telegram (message history and attachment downloads).
I’ll also cover running both channels simultaneously, security lockdown,
enterprise controls, and an honest comparison between Channels and
OpenClaw.
Follow along so you don’t miss the next parts
Let me know what else you would like to see in this
series. Leave a comment below.
Claude Code Masterclass Course
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 27/34


---
*Page 28*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Every day, I’m working hard to build the ultimate Claude Code course, which
demonstrates how to create workflows that coordinate multiple agents for
complex development tasks. It’s due for release soon.
It will take what you have learned from this article to the next level of
complete automation.
New features are added to Claude Code daily, and keeping up is tough.
The course explores Agents, Hooks, advanced workflows, and productivity
techniques that many developers may not be aware of.
Once you join, you’ll receive all the updates as new features are rolled out.
This course will cover:
Advanced subagent patterns and workflows
Production-ready hook configurations
MCP server integrations for external tools
Team collaboration strategies
Enterprise deployment patterns
Real-world case studies from my consulting work
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 28/34


---
*Page 29*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
If you’re interested in getting notified when the Claude Code course
launches, click here to join the early access list →
( Currently, I have 26,000+ already signed-up developers)
I’ll share exclusive previews, early access pricing, and bonus materials with
people on the list.
Let’s Connect!
If you are new to my content, my name is Joe Njenga
Join thousands of other software engineers, AI engineers, and solopreneurs who
read my content daily on Medium and on YouTube, where I review the latest AI
engineering tools and trends. If you are more curious about my projects and
want to receive detailed guides and tutorials, join thousands of other AI
enthusiasts in my weekly AI Software Engineer newsletter
If you would like to connect directly, you can reach out here:
AI Integration Software Engineer (10+ Years Experience )
Software Engineer specializing in AI integration and automation.
Expert in building AI agents, MCP servers, RAG…
njengah.com
Follow me on Medium | YouTube Channel | X | LinkedIn
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 29/34


---
*Page 30*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Claude Code Openclaw Anthropic Claude Code Claude Claude Ai
Written by Joe Njenga
Following
19.4K followers · 97 following
Software & AI Automation Engineer, Tech Writer & Educator. Vision:
Enlighten, Educate, Entertain. One story at a time. Work with me:
mail.njengah@gmail.com
Responses (6)
Rae Steele
What are your thoughts?
Sebastian Buzdugan
3 days ago
curious how code channels handle auth and rate limits compared to openclaw, especially for multi-user discord
bots 🤔
5 Reply
ali
3 days ago
So, we need to have an active terminal in our machine to make it work.
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 30/34


---
*Page 31*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
5 Reply
Data Matric
3 days ago
Finally, a piece that cuts through the AI hype and shows what actually works in real coding workflows. The way
you broke down Claude Code Channels vs OpenClaw made the future of AI-powered development feel
practical, not theoretical.
Definitely one… more
7 Reply
See all responses
More from Joe Njenga
InAI Software Engineer by Joe Njenga Joe Njenga
Why Claude Weekly Limits Are I Finally Tested Claude Code /voice
Making Everyone Angry (And… — It’s Faster than Typing (Don’t…
Yesterday, I finally hit my weekly Claude limit, Anthropic has now rolled out Claude Code
and I wasn't surprised, since I see dozens of… /voice to all users, and I have just tested it for …
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 31/34


---
*Page 32*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Oct 19, 2025 705 62 Mar 13 214 4
Joe Njenga InAI Software Engineer by Joe Njenga
Everything Claude Code: The Repo Anthropic Just Solved AI Agent
That Won Anthropic Hackathon… Bloat — 150K Tokens Down to 2K…
If you slept through this or missed out, Anthropic just released smartest way to build
Everything Claude Code hit 900,000 views o… scalable AI agents, cutting token use by 98%,…
Jan 22 526 4 Nov 6, 2025 947 55
See all from Joe Njenga
Recommended from Medium
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 32/34


---
*Page 33*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Reza Rezvani Zoe Whitman
Claude Code /loop — Here Are 3 How I Finally Installed OpenClaw
Autonomous Loops For My Daily… Cleanly on a VPS (After 5 Failed…
After installing OpenClaw more than five
different times on fresh VPS environments, I…
Mar 9 98 3 Mar 9
InArtificial Intelligence in Plain E… by Rick Highto… Daniel Avila
Put Claude on Autopilot: Scheduled Claude Code has a hidden Agent for
Tasks with /loop and /schedule… answering questions about itself
How to use Claude Code’s /loop command There’s a built-in agent inside Claude Code
and Desktop scheduling to automate… you can invoke just by telling Claude to use…
Mar 11 11 1 Mar 9 4
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 33/34


---
*Page 34*


3/23/26, 4:59 PM I Tested (New) Claude Code Channels (Real OpenClaw Killer) | by Joe Njenga | Mar, 2026 | Medium
Joe Njenga Reza Rezvani
12 Little-Known Claude Code AI Agent Skills at Scale: What
Commands That Make You a Whiz Building 170 Skills Across 9…
What if I told you there are some Claude Code The AI skills ecosystem is converging in
commands that, although not very popular,… theory and fragmenting in practice. A practic…
Sep 21, 2025 377 6 Mar 13 32 3
See more recommendations
https://medium.com/@joe.njenga/i-just-tested-new-claude-code-channels-the-real-openclaw-killer-bc47a145b199 34/34