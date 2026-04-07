# 4dayAssist

*Converted from: 4dayAssist.pdf*



---
*Page 1*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
Member-only story
Agentic AI Coding Stack: How
OpenClaw + Claude Code Built a
SaaS MVP in 4 Days
CTO’s production journal on orchestrating my 3 AI agents with
OpenClaw and Claude Code — and what most “vibe coding” articles
cannot explain to you
Reza Rezvani Following 10 min read · 3 days ago
154
The billing tab was broken. Not “slightly off” broken — fundamentally,
embarrassingly broken. The API returned plan limits that contradicted the
database, the usage meters showed zero across the board, and the dark mode
toggle crashed the entire component.
I scored it a 2 out of 10. On my own dashboard.
https://medium.com/p/95b4ec20dcbb 1/17


---
*Page 2*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
AI Coding Stack: Orchestrator + Coding Agent + Parallel Helper | Image Generated with Gemini 3 Pro ©
Transparency: AI assisted with research structure and flow. The experiments, code,
observations, and analysis are from my own practice.
It was Saturday afternoon, 16 hours into a sprint that was supposed to prove
a thesis: that a single developer, armed with the right AI stack, could ship a
production SaaS product in a long weekend. Not a landing page. Not a
prototype with hardcoded data. A working product with authentication, a
NeonDB database, 14 API endpoints, AI-powered content generation, and a
responsive dashboard with 8 functional tabs.
By Sunday evening, I had 34 commits, roughly 10,000 lines of shipped code,
and a billing tab that now scored 9 out of 10. The thesis held — but not for
the reasons most AI coding articles would have you believe.
This is the honest story of what worked, what broke, and why the
orchestration layer matters more than the coding agent.
https://medium.com/p/95b4ec20dcbb 2/17


---
*Page 3*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
The Stack Nobody Writes About
Every “I built X with AI” article focuses on the coding tool. Claude Code did
this. Cursor did that. But the coding agent is only one piece — and honestly,
not the most important one.
Here is the actual AI stack:
Leo (OpenClaw — The agents name I chose) — my AI orchestrator and
thinking partner. Leo does not write code. Leo thinks. It holds the full project
context, decomposes problems into surgical tasks, crafts implementation
prompts, and reviews output. Think of it as the tech lead who never writes a
line but makes everyone around them 3x more productive.
Claude Code — the primary coding agent. With the Superpowers plugin
installed and auto-memory enabled, Claude Code became a disciplined
engineer rather than a helpful autocomplete. It writes tests before code,
follows structured debugging flows, and — critically — remembers project-
specific patterns across sessions.
Codex CLI — the secondary engineer for parallel work. When Claude Code
was deep in a complex refactor, Codex CLI handled independent tasks on
separate branches. Not a replacement. A teammate.
The key insight is not about any individual tool. It is about the orchestration
pattern — how these tools connect, who holds context, and who executes.
Why Orchestration Beats Raw Coding Power
I stopped talking to Claude Code directly somewhere around month eight of
using it. That single shift changed everything.
https://medium.com/p/95b4ec20dcbb 3/17


---
*Page 4*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
The old workflow looked like this: open Claude Code, describe what I want,
watch it struggle with context, correct it three times, accept a mediocre
result. If you have read my 7-month experience article, you know exactly
what I mean — I spent months fighting the tool before learning to work with
it.
The new workflow:
Leo analyzes the problem →
Leo crafts a precise implementation prompt →
Claude Code executes in the workspace →
Claude Code escalates questions (never guesses) →
Leo reviews the output
Claude Code does not see my full conversation context. It gets a surgical
prompt with clear acceptance criteria.
Something like: “Implement the billing usage API. The endpoint must return
plan-aware limits using PLAN_METERING_LIMITS, include estimated usage
fallbacks when monthly tracker shows 0, and pass TypeScript strict mode.”
This matters because the prompt is not a wish — it is a specification. And
specifications produce better code than conversations.
Claude Code Superpowers Plugin: Discipline Over Features
The Superpowers plugin by Jesse Vincent is not flashy. It does not add new
capabilities. It adds discipline — and discipline is what most AI coding
workflows desperately lack.
https://medium.com/p/95b4ec20dcbb 4/17


---
*Page 5*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
Here is what changed in practice during the sprint:
TDD enforcement. Claude Code does not just write code anymore. It writes
the test first, watches it fail, then implements until the test passes. When I
sent it after the broken billing tab (the one scoring 2 out of 10), the
Superpowers-influenced approach was: verify the current API response,
identify the data contradiction, write a failing test for the expected behavior,
fix the source, confirm the test passes. Systematic. Not heroic.
Structured debugging. When the Gemini API returned 404 errors during
content generation setup, Claude Code did not try random model names. It
followed a diagnostic flow: list available models via the API, identify that
gemini-2.5-flash was the correct identifier, update the configuration. One
attempt. Done. No trial-and-error loops burning through context.
Brainstorming before committing. When designing the AI content pipeline,
Claude Code explored multiple approaches — direct API calls, SDK
wrappers, queue-based processing — before recommending the simplest
path that met requirements.
The plugin enforces this “explore before you build” pattern, which is exactly
what a good senior engineer does naturally.
I wrote about configuring Claude Code with the right plugins months ago.
Superpowers has since become non-negotiable in my setup.
Claude Code Auto-Memory: The Feature That Pays for Itself on
Day One
https://medium.com/p/95b4ec20dcbb 5/17


---
*Page 6*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
Claude Code has autoMemoryEnabled in its settings. If you have not turned it
on yet, stop reading and do it now:
// Add to ~/.claude/settings.json
{
"autoMemoryEnabled": true
}
Here is why this matters. Every Claude Code session starts fresh. Without
memory, the agent re-discovers your build commands, your project
structure, your debugging patterns, your environment quirks. With auto-
memory, it retains learned knowledge across sessions:
npx next build requires DATABASE_URL at build time (not just runtime)
TypeScript strict mode means no any types — ever
The project uses Tailwind v4 (no tailwind.config.ts file)
Bash compatibility: use PASS=$((PASS+1)) not ((PASS++))
The NeonDB connection needs SSL mode enabled for production
None of these are in documentation. These are lessons learned from failures
— from the times Claude Code hit an error, diagnosed the fix, and wrote it
down for next time.
Over the 4-day sprint, the memory file grew organically. By day three, Claude
Code was solving problems faster because it already knew the project’s
gotchas.
https://medium.com/p/95b4ec20dcbb 6/17


---
*Page 7*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
This is the closest thing I have seen to genuine institutional knowledge in an
AI tool. If you want to understand the broader picture of how Claude Code’s
memory and configuration systems connect, my CLAUDE.md configuration
guide breaks down the architecture.
Agent Teams: Honest Assessment
Claude Code’s experimental Agent Teams feature
(CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1) enables spawning sub-agents for
parallel work. In theory, three agents working on three branches
simultaneously. I had explored multi-agent patterns extensively before this
sprint, so I went in with realistic expectations.
The honest assessment: Leo’s orchestration worked better for this project.
Here is why.
Agent Teams is designed for independent parallel tasks. But most real engineering
work is sequential with dependencies.
The billing fix depends on understanding the content API, which depends
on the database schema, which depends on the auth flow. You cannot
parallelize a dependency chain.
What worked instead: Leo as orchestrator + Claude Code as executor +
Codex CLI for genuinely independent tasks. Leo holds the full context,
decomposes the problem, crafts specific prompts, and sends Claude Code
on focused missions. Meanwhile, Codex CLI handles tasks that truly have no
dependencies — writing documentation, creating test fixtures, setting up CI
configuration.
https://medium.com/p/95b4ec20dcbb 7/17


---
*Page 8*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
This is not a criticism of Agent Teams. I used it selectively for independent
bug fixes across separate components, and it performed well there. The
lesson is simpler: match the tool to the task shape. Dependent work needs a
single context holder. Independent work can parallelize.
The Numbers
Because vague claims destroy trust, here are the actual metrics:
Performance Overview Table | OpenClaw + Claude Code | Image by Alireza Rezvani ©
For context: building this same product without AI assistance would have
taken me 2 to 3 weeks of focused work. That is not a guess — I have shipped
similar dashboards before the AI tooling era, and I know my velocity.
https://medium.com/p/95b4ec20dcbb 8/17


---
*Page 9*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
Where This Approach Falls Short
This section matters more than the success metrics.
Context limits are real. Around the 15-file modification mark in a single
session, I noticed accuracy dropping. Claude Code’s memory helps across
sessions, but within a session, you still hit the context ceiling. The
workaround: shorter, more focused sessions with clear scope boundaries.
Orchestration overhead is not zero. Having Leo craft prompts for Claude
Code adds a layer. For simple changes — a CSS tweak, a copy update — the
orchestration pattern is overkill. I still jump into Claude Code directly for
small fixes. The overhead pays off for anything touching 3 or more files or
requiring architectural understanding.
Debugging AI-generated code is a different skill. When something breaks in
AI-written code, the debugging process is different from debugging your own
code. You do not have the mental model of why the code was written that
way. This is solvable — good tests help enormously — but it is a real
adjustment.
Cost adds up. Running Claude Opus 4.6 for orchestration plus Claude
Sonnet 4.5 for coding plus Gemini for content generation is not cheap. I did
not track exact API costs for this sprint, but my monthly AI tooling spend is
Open in app
north of $150. For a side project, that is a meaningful investment.
opencla Write
What I Would Tell You to Try
Five specific recommendations, ordered by impact:
https://medium.com/p/95b4ec20dcbb 9/17


---
*Page 10*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
Enable auto-memory today. Add "autoMemoryEnabled": true to
~/.claude/settings.json. The return on investment is immediate — Claude
Code starts accumulating project knowledge from your very first session.
Install the Superpowers plugin. Run /plugin marketplace add
obra/superpowers-marketplace then /plugin install superpowers@superpowers-
marketplace in Claude Code. It is not about adding capabilities. It is about
adding the discipline that turns a code generator into a software engineer.
Stop using Claude Code as a chatbot. Give it a workspace, a clear task with
acceptance criteria, and let it work. Review the output, do not micromanage
the process. This single shift — which took me 7 months to learn — produces
better results than any configuration trick.
Pair your coding agent with an orchestrator. Whether that orchestrator is
you with a notepad, a structured CLAUDE.md file, or an AI assistant like
OpenClaw — someone needs to hold the big picture while the coding agent
holds the codebase. I have documented how CTO-level orchestration works
if you want a deeper look at the pattern.
Use Agent Teams and parallel tools selectively. They are powerful for truly
independent work — separate bug fixes, parallel test suites, independent
documentation tasks. They are not yet the right tool for building a feature
from top to bottom where every piece depends on the last.
The Uncomfortable Truth
This stack did not replace me. It amplified me.
https://medium.com/p/95b4ec20dcbb 10/17


---
*Page 11*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
I am still the one who chose NeonDB over Supabase because connection
pooling mattered more than real-time subscriptions for this use case. I
decided on class-based dark mode because it avoids the flash-of-unstyled-
content problem. I spotted the security leak in the integrations API that
Claude Code missed entirely — a missing auth check on a webhook
endpoint.
The 34 commits, the 14 APIs, the responsive themes, the AI content pipeline
— that is throughput I could not achieve alone in a weekend. Not even close.
But throughput without judgment is just fast failure.
The tools are ready. The question is whether your workflow is. And by
workflow, I do not mean which model you are using or which plugin you
installed.
I mean: who holds the context? Who makes the architectural decisions? Who
catches the things the AI does not know it missed?
If you cannot answer those questions, no amount of AI tooling will save your
sprint.
Frequently Asked Questions About AI Coding Stacks
What is the best AI coding stack for solo developers in 2026? Based on my
production experience, the combination of an orchestration layer (like
OpenClaw), a primary coding agent (Claude Code with the Superpowers plugin),
and auto-memory produces the highest-quality output.
https://medium.com/p/95b4ec20dcbb 11/17


---
*Page 12*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
The key is not any single tool but the pattern: separate thinking from
executing, and preserve learned knowledge across sessions.
How does OpenClaw work with Claude Code? OpenClaw acts as a strategic
orchestrator — it analyzes problems, decomposes them into specific tasks,
and crafts precise prompts for Claude Code to execute. Claude Code then
works inside the actual codebase with file access, terminal capabilities, and
test execution.
The separation ensures Claude Code receives focused, specification-grade
instructions rather than open-ended conversation.
Is the Superpowers plugin worth installing for Claude Code? Yes.
Superpowers enforces test-driven development, structured debugging, and
brainstorming-before-building patterns. In my sprint, it was the difference
between Claude Code guessing at solutions and Claude Code following a
systematic engineering methodology. Installation takes under a minute via
the plugin marketplace.
Can you actually build a SaaS product with AI coding tools in a weekend?
You can build a functional MVP — 14 API endpoints, 8 dashboard tabs,
authentication, database integration, AI-powered features — in roughly 16
hours of focused work. But you need production engineering experience to
make the architectural decisions the AI cannot make, and you need an
orchestration workflow that prevents the AI from drifting off track.
https://medium.com/p/95b4ec20dcbb 12/17


---
*Page 13*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
✨
Thanks for reading! If you want more production-tested AI engineering
patterns, subscribe to my newsletter for weekly insights.
I am genuinely curious: what orchestration pattern are you using with your AI
coding tools? Are you talking directly to the agent, or have you found a way to
separate thinking from executing? Drop your setup in the comments.
About the Author
I am Alireza Rezvani (Reza), CTO building AI development systems for
engineering teams. I write about turning individual expertise into collective
infrastructure through practical automation.
Connect: Website | LinkedIn | Newsletter
Read more on Medium: Alireza Rezvani
Openclaw Claude Code Software Development AI Agent Agentic Ai
Written by Reza Rezvani
Following
4.4K followers · 76 following
As CTO of a Berlin AI MedTech startup, I tackle daily challenges in
healthcare tech. With 2 decades in tech, I drive innovations in human
motion analysis.
https://medium.com/p/95b4ec20dcbb 13/17


---
*Page 14*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
No responses yet
Rae Steele
What are your thoughts?
More from Reza Rezvani
Reza Rezvani Reza Rezvani
10 SOUL.md Practical Cases in A 141 Claude Code Agents: The Setup
Guide for MoltBot (CLAWDBOT):… That Actually Works. A Complete…
The difference between a chatbot and an After 6 months building agents in production,
assistant is persistence. Here’s how to build… here’s the 10-team structure, 8 autonomous…
Jan 29 195 5 Jan 25 230 8
https://medium.com/p/95b4ec20dcbb 14/17


---
*Page 15*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
Reza Rezvani Reza Rezvani
OpenClaw / Moltbot IDENTITY.md: The Only 3 Things You Need to
How I Built Professional AI… Start with Claude Code (Everythin…
SOUL.md defines who your AI is. Claude Code Skills. Agents. Hooks. MCPs.
IDENTITY.md defines how the world… Commands. Subagents. Plugins.
Jan 30 48 2 Jan 19 313 6
See all from Reza Rezvani
Recommended from Medium
https://medium.com/p/95b4ec20dcbb 15/17


---
*Page 16*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
InRealworld AI Use Casesby Chris Dunlop Reza Rezvani
Senior Developers — The World Claude Code Remote Control: The
Owes You an Apology Practical Guide to Coding From…
Why senior developers still matter in the age Setup walkthrough, real-world workflows, and
of AI coding tools — and what junior… honest limitations — from same-day testing …
5d ago 950 42 Feb 26 99 3
Henrique Siebert Domareski InData Science Colle… by Han HELOIR YAN, Ph.…
Claude Code — A Practical Guide to A Senior Engineer’s Concern That
Automating Your Development… Revealed the Most Important Role…
Claude Code is an agentic coding assistant Agentic Systems That Actually Ship
developed by Anthropic that runs directly in…
Feb 7 146 4 6d ago 936 14
InGenerative… by Phil | Rentier Digital Automa… InSpillwave Solutionsby Rick Hightower
Every Claude Code Tutorial What Is GSD? Spec-Driven
Teaches You the Same 5 Things.… Development Without the…
CLAUDE.md, slash commands, multi-Claude How AI agents forget what they’re building ,
worktrees, headless mode, “think hard.” Eve… and how to fix it
https://medium.com/p/95b4ec20dcbb 16/17


---
*Page 17*


3/5/26, 2:40 PM Agentic AI Coding Stack: How OpenClaw + Claude Code Built a SaaS MVP in 4 Days | by Reza Rezvani | Mar, 2026 | Medium
Feb 22 191 3 Feb 22 74 1
See more recommendations
https://medium.com/p/95b4ec20dcbb 17/17