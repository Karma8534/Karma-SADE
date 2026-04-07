# BloxCUE

*Converted from: BloxCUE.pdf*



---
*Page 1*


3/25/26, 5:04 PM My CLAUDE.md got too big, so I built BloxCue | by Bokiko | Medium
Open in app
Search Write
My got too big, so I built
CLAUDE.md
BloxCue
Bokiko Follow 4 min read · Jan 1, 2026
10
https://github.com/bokiko/bloxcue
If you use Claude Code CLI a lot, you eventually run into the same annoying
reality:
More
Your CLAUDE.md starts small, then slowly turns into a dumping ground.
A deployment note here.
A “how we do migrations” section there.
A config snippet you swear you’ll clean up later.
Weeks later, you’ve got a chunky file… and Claude loads all of it every single
time you type a prompt. Even when you’re asking something simple that
only needs one section.
That’s not just messy. It’s expensive.
https://medium.com/@bokiko/my-claude-md-got-too-big-so-i-built-bloxcue-91eca1e53059 1/8


---
*Page 2*


3/25/26, 5:04 PM My CLAUDE.md got too big, so I built BloxCue | by Bokiko | Medium
Claude doesn’t just “peek” at your docs. It ingests them. Over and over. A file
in the ~30KB range can translate into thousands of tokens per prompt,
multiplied by however many prompts you do in a session.
So I stopped fighting it and built a proper solution.
The idea: stop loading everything, start loading the right thing
BloxCue is a simple concept:
Instead of one giant CLAUDE.md, you keep your knowledge as small
markdown blocks, and Claude only pulls in the blocks that match what
you’re asking.
More
Ask about deployment → load the deployment block.
Ask about database → load the database block.
Everything else stays out of the prompt.
In the repo I describe it like a filing cabinet: your knowledge can grow,
without your token usage growing with it. GitHub
Why this matters (even if you don’t care about “tokens”)
When Claude loads a wall of irrelevant context, two things happen:
1. You burn budget on text Claude didn’t need.
https://medium.com/@bokiko/my-claude-md-got-too-big-so-i-built-bloxcue-91eca1e53059 2/8


---
*Page 3*


3/25/26, 5:04 PM My CLAUDE.md got too big, so I built BloxCue | by Bokiko | Medium
2. You get worse outcomes because Claude is forced to “think” through
noise.
BloxCue is basically me trying to buy back two things: speed and focus.
https://github.com/bokiko/bloxcue
The README includes real numbers from usage: roughly ~8,500 tokens per
prompt before, down to ~1,000 after, which is the difference between
“Claude feels heavy” and “Claude feels sharp.”
It works best with Continuous-Claude (and yes, I credit the
original)
BloxCue pairs nicely with Continuous-Claude (created by Anand
Chowdhary). The way I think about it:
Continuous-Claude helps with session memory (what you were doing,
handoffs, continuity)
BloxCue helps with knowledge retrieval (finding the right docs without
loading everything)
They solve different problems, and together the workflow feels way more
“native.”
More
What using BloxCue actually looks like
You install it, choose whether your memory lives globally (~/.claude-
memory), per project (./claude-memory), or both, then you start dropping your
https://medium.com/@bokiko/my-claude-md-got-too-big-so-i-built-bloxcue-91eca1e53059 3/8


---
*Page 4*


3/25/26, 5:04 PM My CLAUDE.md got too big, so I built BloxCue | by Bokiko | Medium
docs into small files.
Each block can include simple frontmatter (title, category, tags) so it’s easier
to index and retrieve.
Then the key part: BloxCue hooks into Claude Code’s settings.json so
retrieval happens automatically on prompt submit. You don’t manually
“search your docs” — Claude just gets the relevant block(s) when you ask.
That’s the whole point. The workflow stays natural.
Safety, trust, and why I kept it simple
Before you install anything that touches your dev workflow, you should be
cautious. I am too. thats why i published a security report done on this repo,
read it before you install anything.
https://github.com/bokiko/bloxcue/blob/main/SECURITY.md
BloxCue is open source. You can read every line.
More
More importantly, it’s designed to be local-first. It doesn’t need to “phone
home”, it doesn’t require accounts, and it doesn’t rely on any external service
to function. Nothing about this tool depends on sending your files to some
third-party server.
If you’re the type who likes to verify (you should be), here’s the right
mindset:
Read the install script and the files it changes before running it.
Scan the repo for anything network-related.
Run it in a disposable VM or a test machine first if you want extra peace of
mind.
https://medium.com/@bokiko/my-claude-md-got-too-big-so-i-built-bloxcue-91eca1e53059 4/8


---
*Page 5*


3/25/26, 5:04 PM My CLAUDE.md got too big, so I built BloxCue | by Bokiko | Medium
Honestly, I’d encourage everyone to treat open-source tools like this: assume
nothing, verify everything. The repo is public specifically so you can audit
it, fork it, and adapt it to your own workflow.
If you already have a huge CLAUDE.md, you don’t need to rewrite
your life
There’s a section in the repo specifically for existing users: you can migrate
by splitting your big file into topics and trimming CLAUDE.md down to
essentials. You can even ask Claude to do the migration for you.
That’s what I’d recommend, because it turns “ugh I need to reorganize
everything” into a 10-minute cleanup.
The pitch, without the cringe
BloxCue isn’t trying to be a big platform.
More
It’s a small workflow upgrade that fixes a dumb problem: Claude shouldn’t
reload your entire brain every time you ask one question.
If you’re using Claude Code CLI and your CLAUDE.md is growing faster than
your patience, you’ll feel the difference immediately.
Repo: bokiko/BloxCue
you can read project FAQ here: https://github.com/bokiko/bloxcue?
tab=readme-ov-file#faq
https://medium.com/@bokiko/my-claude-md-got-too-big-so-i-built-bloxcue-91eca1e53059 5/8


---
*Page 6*


3/25/26, 5:04 PM My CLAUDE.md got too big, so I built BloxCue | by Bokiko | Medium
Claude Code Anthropic Claude Claude Ai AI AI Agent
Written by Bokiko
Follow
110 followers · 28 following
Crypto miner and Tech enthusiast - twitter: @Bokiko_io
No responses yet
Rae Steele
What are your thoughts?
More from the list: "4CC"
Curated byRae Steele
InSpillwave … byRick Hi… Phil | Rentier Digital Agent Native Agent Native
Beyond the AI Coding I Stopped Managing My Deep Agents: The MiniMax M2.7
Hangover: How Harness… Context Window. I… Harness Behind Claude… Be This Close t
· Mar 18 · 4d ago · Mar 11 · 6d ago
View list
More
More from Bokiko
Bokiko Bokiko
Ubuntu Is Free: But the Company OpenClaw for Crypto Miners: A
Behind It Made $292 Million Last… Technical Guide to AI-Assisted…
https://medium.com/@bokiko/my-claude-md-got-too-big-so-i-built-bloxcue-91eca1e53059 6/8


---
*Page 7*


3/25/26, 5:04 PM My CLAUDE.md got too big, so I built BloxCue | by Bokiko | Medium
Most people know Ubuntu as a free Linux No trading advice here. This is about hashrate,
distribution — something you can download,… hardware, and keeping your rigs profitable.
Jun 27, 2025 Feb 5
Bokiko Bokiko
Inside Hyperliquid: The DEX That The Silent Transformation: Why
Earns Like a Fintech and Trades… Tech Giants Are Becoming Energ…
A full fundamental analysis for long-term AI Didn’t Just Change Software — It Changed
investors — October 2025 Power
Oct 18, 2025 1 Dec 25, 2025 21
See all from Bokiko
Recommended from Medium
More
huizhou92 Reza Rezvani
Which Programming Language Claude Code /loop — Here Are 3
Should You Use with Claude Code? Autonomous Loops For My Daily…
A benchmark across 13 languages reveals
surprising patterns — and what it means for…
Mar 11 778 46 Mar 9 110 4
https://medium.com/@bokiko/my-claude-md-got-too-big-so-i-built-bloxcue-91eca1e53059 7/8


---
*Page 8*


3/25/26, 5:04 PM My CLAUDE.md got too big, so I built BloxCue | by Bokiko | Medium
Gábor Mészáros InStackademicbyUsman Writes
CLAUDE.md Best Practices: 7 Your AI Is Useless Without These 8
formatting rules for the Machine MCP Servers — Most Developers…
Originally published at https://dev.to on March Two engineers. The same AI model. One
3, 2026. copy-pastes files all day. The other connects…
Mar 3 87 2 Feb 26 472 13
Joe Njenga Marco Kotrotsos
Claude Code Plugins (New Feature) We Pointed an AI at Raw Binary
Are Making Devs Go x10 Faster… Files From 1986.
Claude Code Plugin is the latest feature that’s What This Means for Software
pushing productivity to insane levels and…
Oct 14, 2025 266 8 Mar 11 1.5K 36
See more recommendations
More
https://medium.com/@bokiko/my-claude-md-got-too-big-so-i-built-bloxcue-91eca1e53059 8/8