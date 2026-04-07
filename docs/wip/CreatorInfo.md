# CreatorInfo

*Converted from: CreatorInfo.pdf*



---
*Page 1*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
Open in app
the file that ma Write
The File That Made the Creator of
Claude Code Go Viral
Ayesha Mughal Following 7 min read · 13 hours ago
2
In January 2026, Boris Cherny posted a thread about his development
workflow.
https://medium.com/p/e01b039e5602 1/16


---
*Page 2*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
By the next morning, it had been covered by VentureBeat, InfoQ, and
Fortune. Developers were calling it “a watershed moment.” A product leader
named Aakash Gupta read it and wrote four words that got reshared
hundreds of times:
“Every mistake becomes a rule.”
The whole thread was about one file.
Not an MCP server. Not a multi-agent orchestration system. Not a custom
framework.
A single Markdown file called CLAUDE.md.
If you’ve been using Claude Code without it — or you have one but wrote it
wrong….this post is for you.
🤔
What Is CLAUDE.md?
Here’s the thing nobody explains clearly:
Every time you open Claude Code, it starts completely fresh. No memory. No
context. No idea who you are, what your project does, or how your team
likes to work.
You tell it things. It helps you. You close the terminal.
Tomorrow? Blank slate. You explain everything again.
CLAUDE.md is the file that fixes this.
https://medium.com/p/e01b039e5602 2/16


---
*Page 3*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
It’s a plain Markdown file that Claude Code reads automatically at the start of
every session. Before you type a single word. It’s your permanent
instructions — your project’s constitution, your team’s rules, your personal
preferences — all loaded into Claude’s context before the conversation even
begins.
The one-line definition: CLAUDE.md is the file where you write everything
you want Claude to know and never want to explain again.
📍
Where Does It Live? (There Are Two Locations)
This is where most tutorials stop explaining, so pay attention.
CLAUDE.md can live in two different places, and they serve different
purposes:
Location 1: Global (~/.claude/CLAUDE.md)
~/.claude/
└── CLAUDE.md ← applies to EVERY project on your machine
This is your personal preferences. Your communication style. Things you
always want from Claude regardless of what project you’re in.
Example contents:
“Always explain what you’re about to do before doing it”
“I prefer TypeScript over JavaScript”
https://medium.com/p/e01b039e5602 3/16


---
*Page 4*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
“Never use any types"
“When you’re unsure, ask — don’t guess”
Location 2: Project-level (your-project/CLAUDE.md)
your-project/
├── CLAUDE.md ← applies only to this project
├── src/
└── package.json
This is project-specific knowledge. Architecture decisions. Tech stack.
Conventions. Rules your team has established for this particular codebase.
Example contents:
“This is a Next.js 15 app using Drizzle ORM and Tailwind”
“API routes live in /app/api — never create routes elsewhere”
“We use Zod for all validation — never write manual validation”
Both files load together. Global first, project-level second. Global = who you
are, project-level = what this codebase is.
🚀
Generate Your First CLAUDE.md in 30 Seconds
You don’t have to write it from scratch. Claude Code can analyze your
codebase and generate a starter file automatically.
Open Claude Code inside your project and run:
https://medium.com/p/e01b039e5602 4/16


---
*Page 5*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
/init
Claude will scan your project — detecting your framework, build system, test
setup, dependencies — and generate a CLAUDE.md with what it found.
It won’t be perfect. But it’s 80% of the way there and takes 30 seconds instead
of 30 minutes.
After it generates, read it carefully and remove anything wrong. Then start
building on top of it.
✍
What Should Actually Be In It?
Here’s the structure that works, based on real CLAUDE.md files from
experienced Claude Code users — including Boris Cherny’s own team at
Anthropic.
Section 1: Project Overview (3–5 lines max)
# CLAUDE.md
## Project Overview
This is a SaaS billing dashboard built with Next.js 15, Prisma, and Stripe.
Backend is a separate FastAPI service in /api-service.
Frontend and backend communicate via REST - no GraphQL.
Short. Just enough for Claude to understand what it’s working with.
https://medium.com/p/e01b039e5602 5/16


---
*Page 6*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
Section 2: Tech Stack & Conventions
## Tech Stack
- Framework: Next.js 15 (App Router — NOT pages router)
- Database: PostgreSQL via Prisma ORM
- Auth: Clerk
- Styling: Tailwind CSS only — no inline styles, no CSS modules
- Payments: Stripe — never mock Stripe in tests, always use test mode keys
## Code Conventions
- All components are functional - no class components
- Use TypeScript strict mode - `any` is banned
- Validation: Zod everywhere - never write manual if/else validation
- Error handling: All async functions must have try/catch
This section prevents the most common Claude mistakes: using the wrong
router, wrong ORM pattern, wrong styling approach.
Section 3: File Structure Rules
## File Structure
- Components: /components/<ComponentName>/index.tsx
- API routes: /app/api/<route>/route.ts
- Types: /types/<domain>.ts (never inline complex types)
- Utils: /lib/utils/ (pure functions only, no side effects)
Do NOT create files outside these conventions without asking
first.
Section 4: Behavioral Rules (The Most Important Section)
https://medium.com/p/e01b039e5602 6/16


---
*Page 7*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
This is where Boris Cherny’s insight lives. These are the rules you add one
mistake at a time:
## Behavioral Rules
- Always run `npm run typecheck` before telling me a task is done
- Never modify package.json without showing me the change first
- If you're unsure whether to create a new file or modify an existing one, ask
- Always commit in small logical units — never one giant commit
- When fixing a bug, explain the root cause before writing the fix
- Never assume environment variables — ask me if you don't see them in .env.example
 
Every line here is a mistake that happened once and will never happen
again.
🔑
The Boris Cherny Method — “Every Mistake Becomes a
Rule”
This is the insight that made his thread go viral, and it’s worth understanding
deeply.
Most developers treat CLAUDE.md like a setup file — you write it once
during project setup and forget about it.
Cherny treats it like a living document that his entire team maintains
together.
The workflow:
1. Claude makes a mistake (wrong pattern, wrong file, bad assumption)
2. Developer catches it during PR review
https://medium.com/p/e01b039e5602 7/16


---
*Page 8*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
3. Developer doesn’t just fix the code
4. Developer also adds a rule to CLAUDE.md so it never happens again
That’s it. That’s the whole system.
The result: the longer a team works this way, the smarter Claude gets in that
specific codebase. By month six, Claude is producing output that matches
your exact team standards from a single-sentence prompt — because every
correction over those six months became a permanent rule.
Cherny described it exactly: “Anytime we see Claude do something incorrectly
we add it to the CLAUDE.md, so Claude knows not to do it next time.”
Your CLAUDE.md in month one will be 20 lines. In month six, it’ll be 100+
lines — each one representing a real mistake that won’t happen twice.
⚠
The Most Common Mistake — Don’t Bloat It
Here’s what kills CLAUDE.md effectiveness, and most people do it:
They write too much.
Cherny’s own CLAUDE.md is approximately 2,500 tokens — roughly one
page of text. That’s the sweet spot.
Why does size matter? Claude Code reliably follows around 100–150 custom
instructions per session. Your system prompt already uses about 50. That
leaves 100–150 slots for your project rules.
https://medium.com/p/e01b039e5602 8/16


---
*Page 9*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
If your CLAUDE.md is 500 lines of documentation, Claude won’t ignore it —
it’ll try to follow all of it, get overwhelmed, and start dropping the rules
buried in the middle.
CLAUDE.md should be a constitution, not a manual.
Rules: yes. Documentation: no. Background context: no. Step-by-step
guides: no.
🧾
One-line test: If a rule requires more than 2–3 lines to explain, it doesn’t
belong in CLAUDE.md. Move it to a SKILL.md or a separate document and
reference it.
📁
Real Example — A Production CLAUDE.md
Here’s what a well-structured CLAUDE.md actually looks like for a real
project:
# CLAUDE.md
## Project
E-commerce platform. Next.js 15 (App Router), TypeScript strict, PostgreSQL via
Drizzle ORM, Stripe for payments, Resend for email, Vercel deployment.
## Non-negotiables
- App Router only — pages/ directory does not exist
- Drizzle for all DB queries — no raw SQL unless discussing a migration
- Zod for all input validation
- All currency in cents (integer) — never floats, never strings
- All dates in UTC — display conversion happens at the UI layer only
## File Conventions
- Server actions: /app/actions/<domain>.ts
- DB queries: /db/queries/<domain>.ts
- Components: /components/<Domain>/<ComponentName>.tsx
- Types: /types/<domain>.ts
## Behavioral Rules
- Run `npm run build` before calling any task complete
- Never modify /db/schema.ts - show me what you'd change and I'll decide
https://medium.com/p/e01b039e5602 9/16


---
*Page 10*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
- If you need an env variable that's not in .env.example, stop and ask
- Commit message format: "feat/fix/refactor: short description"
- Never install new packages without listing what they're for and asking approval
## Current Sprint Context
Working on checkout flow. Stripe integration is done. Bug: discount codes
aren't being applied before tax calculation. Start here if context is unclear.
Notice what’s missing: no documentation, no explanations, no tutorials. Just
rules.
🤝
Sharing CLAUDE.md With Your Team
If your CLAUDE.md is in your project root — which it should be — it’s in your
Git repository. Everyone who clones the repo gets it automatically. Every rule
you add benefits your entire team instantly.
This is Claude Code becoming a team-shared knowledge system, not just a
personal assistant.
 
When a junior developer joins your team, they don’t just get the codebase —
they get six months of accumulated wisdom about how Claude works in
your specific project. Every mistake you’ve already made, pre-corrected.
🔄
One More Thing — CLAUDE.md + Slash Commands = Full
Workflow Automation
CLAUDE.md handles the what (what Claude should know and follow). Slash
commands handle the when (specific workflows you trigger manually).
They work together. Here’s a quick example:
https://medium.com/p/e01b039e5602 10/16


---
*Page 11*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
# .claude/commands/pr.md
Review all changed files since the last commit.
Check against CLAUDE.md conventions.
List any violations.
Then create a commit and open a PR with a descriptive title.
Now type /pr inside Claude Code and that entire workflow runs with one
command. Cherny uses /commit-push-pr dozens of times daily.
Your CLAUDE.md teaches Claude your standards. Your slash commands
make triggering those standards instant.
📋
Your Action Plan — Start Today
If you have no CLAUDE.md yet:
cd your-project
claude # open Claude Code
/init # generate starter CLAUDE.md
Then read what it generated. Remove anything wrong. Add 3–5 behavioral
rules you wish Claude already knew.
If you have one but it’s long: Trim it. Aim for under 150 lines. Move
documentation out, keep only rules. Run /context inside Claude Code to
check your token usage.
https://medium.com/p/e01b039e5602 11/16


---
*Page 12*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
If you want to build the Cherny system: Add this to your team’s PR review
checklist: “Did Claude make a mistake? Add a rule to CLAUDE.md.”
Do that for 30 days. You’ll have a smarter agent than you could have built any
other way.
Next up: Slash Commands — how to turn a one-line command into a full multi-
step workflow that your entire team can use
Claude Code AI Programming Productivity
Written by Ayesha Mughal
Following
104 followers · 3 following
Coding with a Spark of ChaosIT student 💡 | Code lover 💻 | Tea addict ☕|
Dreaming in dark mode 🌒Building logic, chasing stars ✨ — one line of code at
a time.
No responses yet
Rae Steele
What are your thoughts?
https://medium.com/p/e01b039e5602 12/16


---
*Page 13*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
More from Ayesha Mughal
InArtificial Intelligence in Plain E… by Ayesha Mu… InAI Advancesby Nov Tech
Unlocking AI Potential: Exploring 3 $830 Billion Vanished in One Week
Essential Prompting Techniques f… — Because This AI Found 500…
In the rapidly evolving world of artificial Claude Opus 4.6 discovered zero-day
intelligence, large language models (LLMs)… vulnerabilities autonomously, and Wall Street…
Oct 16, 2025 1 Feb 8 2.6K 53
https://medium.com/p/e01b039e5602 13/16


---
*Page 14*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
InAI Advancesby Nov Tech InArtificial Intelligence in Plain E… by Ayesha Mu…
🎯
OpenAI Just Dropped Three Temperature, Top-p & Top-k
Bombs, and One of Them Might… The Secret Settings That Control…
While everyone’s distracted by leadership A super easy guide to making AI more
drama, OpenAI quietly launched features tha… creative or more accurate — your choice ✨
Jan 28 2K 88 Oct 30, 2025
See all from Ayesha Mughal
Recommended from Medium
https://medium.com/p/e01b039e5602 14/16


---
*Page 15*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
InGenerative AIby Jim Clyde Monge Will Lockett
5 Interesting Things About OpenAI Is Totally Cooked
OpenClaw You Probably Didn’t…
What a s**tshow.
Here are five things about OpenClaw that
every user must know.
Feb 19 377 4 Feb 23 2.6K 40
InEntrepreneurship Handbook by Joe Procopio Civil Learning
Databricks CEO Just Dropped The How NASA Writes Code That
Most Honest Advice About The… Actually Can’t Fail
Data company leaders aren’t interested in You know what’s wild? The code running on
histrionics and hand-waving spacecraft right now, literally flying through…
Feb 23 1.8K 58 Feb 21 484 14
Rekhi Can Artuc
Why Replacing Developers with AI Linux 7.0: Google’s $1M Bug Finally
is Going Horribly Wrong Fixed
Something Weird Is Happening in Tech Right Google paid $1M in iouring bounties and
Now disabled it on Chrome OS. A maintainer calle…
https://medium.com/p/e01b039e5602 15/16


---
*Page 16*


3/5/26, 10:38 AM The File That Made the Creator of Claude Code Go Viral | by Ayesha Mughal | Mar, 2026 | Medium
Feb 15 2.1K 115 Feb 21 1.93K 16
See more recommendations
https://medium.com/p/e01b039e5602 16/16