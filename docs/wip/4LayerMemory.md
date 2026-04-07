# 4LayerMemory

*Converted from: 4LayerMemory.PDF*



---
*Page 1*


Open in app
11
Search Write
Artificial Intellige…
Your AI Agent Has
Amnesia. Here’s the
Cure.
Ayesha Mughal Following 8 min read · 4 days ago
7


---
*Page 2*


Every morning your agent wakes up with no
memory of yesterday.
You spent two hours yesterday defining your
architecture. Explaining that you use Drizzle not
Prisma. That API routes live in /app/api not
/src/api. That you never use any in TypeScript.
That the auth flow has a specific pattern everyone
on the team follows.
Today? Gone. You explain it again. You lose 20
minutes re-establishing context you already paid
for yesterday.
This isn’t a Claude Code problem. It’s not a Cursor
problem. It’s not a context window problem.
Infinite context isn’t memory. It’s just a bigger
buffer.
A GitHub issue posted by Claude Code in
December 2025 received hundreds of reactions:
“starts every session with zero context. The
relationship doesn’t compound over time.”


---
*Page 3*


The relationship doesn’t compound. That’s the core
problem. And in 2026, it’s the most actively solved
problem in agentic engineering.
Here’s everything that works.
If you’re new here — I write the practical guides
professionals wish existed. Follow once, get the whole
series.
🧠
Why Agents Forget — The Actual
Architecture Problem
Most developers think the fix is a bigger context
window. It isn’t.
As agents have become more capable, the
bottleneck has shifted from “the agent does not
understand what I want” to “the agent does not
have the context it needs to do it well.”
These are different problems. The first is a
prompting problem. The second is an architecture
problem.


---
*Page 4*


Large language models are stateless by design.
Every API call starts with an empty context
window. The conversation history you see in your
terminal isn’t stored in the model — it’s re-injected
into the context on every call. When the session
ends, that history is gone.
True agent memory isn’t about how much text you
can cram into a prompt. It’s about how an
intelligent system accumulates, consolidates, and
evolves experience over time.
The distinction matters because the solution is
completely different. A bigger context window
means you can pack more into each session. A real
memory system means the agent accumulates
knowledge across sessions — the way a colleague
does, not the way a search engine does.
📁
Layer 1 — Project Memory Files (The
Foundation)


---
*Page 5*


This is the layer you can implement in the next 10
minutes.
Project memory files like CLAUDE.md give agents
persistent context about architecture, conventions,
and decisions. We covered CLAUDE.md in depth in
the Claude Code series — the same principle
applies to every agentic tool in your stack.
But CLAUDE.md is static. You write it, it stays the
same. The more powerful pattern is a session
handoff file — a living document that updates
every session.
.ai/memory.md — the file that makes your agent a
colleague instead of a temp:
# Project Memory
## Last Updated
[Agent updates this timestamp at the end of every ses
## Architecture Decisions
- Database: PostgreSQL via Drizzle ORM (NOT Prisma -
- Auth: Clerk (not NextAuth - switched in Feb 2026, s
- API routes: /app/api only - never create routes els
- Styling: Tailwind + shadcn/ui - no custom CSS files


---
*Page 6*


## Current Sprint
Building checkout flow. Stripe integration complete.
Bug: discount codes not applied before tax calculatio
Next: fix the discount calculation order in /app/api/
## Decisions Made This Week
- Chose optimistic UI for cart updates (discussed Tue
- Deferred email notifications to v1.1 (scope reducti
## Things Claude Keeps Getting Wrong
- Trying to use Prisma instead of Drizzle (stop this)
- Creating files in /src instead of /app
- Using `any` type - banned, always use proper types
The “Things Claude Keeps Getting Wrong” section
is the highest-value line in the file. Every mistake
that happens once goes here. It never happens
twice.
Add this to your CLAUDE.md:
## Session Continuity
At the start of each session, read .ai/memory.md if i
At the end of each session, update .ai/memory.md with
- Any architectural decisions made
- Current state of in-progress work
- Exact next step
- Any new mistakes to avoid


---
*Page 7*


The agent reads its own notes from yesterday. The
relationship compounds.
🔴
Layer 2 — The Four Memory Types
(What the Research Says)
The definitive survey Memory in the Age of AI
Agents (arXiv:2512.13564) defines four distinct
memory types. Understanding these changes how
you design your memory architecture.
Sensory Memory — raw input processing, what the
agent perceives in the current moment. This is the
immediate context window. Nothing you can
architect — it’s the model’s native capability.
Short-Term (Working) Memory — active task
context within a session. This is your conversation
history, the current task state, the files you’ve
opened. Managed by tools like Claude Code’s
/compact command and context window
management.


---
*Page 8*


Long-Term Memory — knowledge that persists
across sessions. This is what’s actually broken in
most agentic setups. Your .ai/memory.md is a simple
implementation of this. Dedicated memory
systems (Mem0, Zep, AgentCore) are the
production implementation.
Episodic Memory — specific past experiences.
“The last time we deployed on a Friday it broke
staging.” “This client always asks for the TypeScript
version even when you give them JavaScript.”
These are facts about events, not general
knowledge. The hardest to implement well, the
most valuable when done right.
Most developers only have Layer 1 (sensory) and
partially have Layer 2 (working). Layers 3 and 4 are
where the compound effect lives.
⚡
Layer 3 — Mem0 and Graph-Based
Memory (The Production Solution)


---
*Page 9*


In a study published by Mem0 on arXiv, the
approach achieved a 91% reduction in response
time compared to the full context method, while
maintaining high accuracy.
That’s not a small improvement. 91% faster
because the agent isn’t re-processing thousands of
tokens of conversation history — it’s retrieving the
specific memories relevant to the current
question.
How Mem0 works:
Instead of stuffing the entire conversation history
into context, Mem0 extracts structured memories
from conversations and stores them in a vector
database. When a new session starts, it retrieves
only the memories relevant to the current query.
from mem0 import Memory
m = Memory()
# After a session - extract and store memories
m.add("User prefers Drizzle over Prisma for database
m.add("API routes must be in /app/api, never /src/api


---
*Page 10*


m.add("TypeScript strict mode - any type is banned",
# At the start of next session - retrieve relevant me
memories = m.search("database query", user_id="ayesha
# Returns: ["User prefers Drizzle over Prisma for dat
# Not the full history - just what's relevant
The graph-based version, Mem0g, uses a directed
labeled graph to represent entities and
relationships between them. This means it doesn’t
just store facts — it stores relationships. “Drizzle is
preferred over Prisma” becomes a graph edge:
[Drizzle] --preferred_over--> [Prisma]. When you
ask about database choices, the graph traversal
finds connected facts automatically.
Zep and Graphiti take this further with temporal
knowledge graphs — facts are timestamped, so the
agent knows that “we used Prisma until February
2026, then switched to Drizzle.” The history of
decisions, not just the current state.
🏗
Layer 4 — Context Engineering (The
New Skill That Replaces Prompt
Engineering)


---
*Page 11*


Prompt engineering is about crafting the right
instruction for an AI. Context engineering is about
giving the AI the right information to work with.
This is the 2026 skill shift that most developers
haven’t internalized yet.
Prompt engineering optimizes the instruction.
Context engineering optimizes what the agent
knows before the instruction runs.
The four context engineering levers:
1. Project memory files — architecture,
conventions, decisions (CLAUDE.md,
.ai/memory.md)
2. Task-specific context injection — before starting
any task, give the agent the relevant files, API docs,
and examples it needs. Not everything — the
specific things relevant to this task.


---
*Page 12*


Before implementing the checkout route, read:
- /app/api/cart/route.ts (existing pattern to follow)
- /lib/stripe.ts (how we initialize Stripe)
- /types/checkout.ts (the types you'll use)
3. MCP servers — live access to databases, APIs,
documentation. Instead of pasting in your
database schema, the agent queries it. Instead of
pasting in library docs, Context7 MCP fetches them
live. Context stays accurate without manual
updates.
4. Workspace scoping — limit what the agent can
see to what’s relevant. An agent that can see your
entire monorepo for a single checkout bug is an
agent that will get distracted by unrelated files.
Scope it to the relevant directories.
Context engineering is about precision, not
volume. The right 2,000 tokens beats the wrong
200,000 tokens every time.


---
*Page 13*


🔄
The Memory Update Hook —
Automating What You’ll Forget to Do
The biggest problem with session handoff files:
you forget to update them.
You finish a long coding session. It’s late. You got
the feature working. You close the terminal.
Tomorrow the agent has no idea what you just
built.
Fix this with a Stop hook that runs automatically at
the end of every session:
.claude/hooks/update-memory.sh:
#!/bin/bash
INPUT=$(cat)
# Only run if there were actual changes this session
if git diff --quiet HEAD 2>/dev/null; then
exit 0
fi
# Ask Claude to update the memory file
claude -p "Read the conversation we just had and upda
1. Any architectural decisions made
2. Files modified and why
3. Current state of in-progress work


---
*Page 14*


4. The exact next step to continue
5. Any new mistakes or gotchas discovered
Be specific. The next session starts cold - give it e
echo "[memory] Session context saved to .ai/memory.md
Wire it in .claude/settings.json:
{
"hooks": {
"Stop": [
{
"hooks": [
{
"type": "command",
"command": ".claude/hooks/update-memory.s
}
]
}
]
}
}
Now every session ends by writing its own notes.
The agent is its own secretary. You never lose
context to a closed terminal again.
📊
Choosing Your Memory Stack


---
*Page 15*


Need Solution Complexity Just starting out
.ai/memory.md + session handoff hook Low Team
project, shared context CLAUDE.md in git +
.ai/memory.md gitignored Low Production agent,
many users Mem0 with vector storage Medium
Complex relationships, temporal facts Zep +
Graphiti graph memory High Enterprise, AWS
infrastructure Amazon AgentCore Memory High
Start with the file-based approach. It solves 80% of
the problem with 5 minutes of setup. Move to
Mem0 when you need cross-user memory or the
file approach stops scaling. Move to graph-based
memory when you need to track relationships
between facts and their history over time.
🎯
The One Thing That Changes
Everything
Creating or updating your project’s CLAUDE.md
file is the single highest-leverage action for
improving agent performance.


---
*Page 16*


Not setting up Mem0. Not implementing graph
memory. Not building elaborate context injection
pipelines.
The file. The one that documents your
architecture, conventions, and the decisions you’ve
already made.
Every token you don’t spend re-explaining
yesterday’s decisions is a token available for today’s
work. Every mistake that goes into the memory file
is a mistake that never repeats.
The agent that remembers is the agent that
compounds. Start there.
One question before you go:
What’s the one thing you find yourself explaining
to your agent over and over every session? Drop it
below — that’s exactly what should be in your
memory file.


---
*Page 17*


If this changed how you think about agent context, hit
Follow — next up is the debugging post: when AI wrote
the bug, how do you make AI find it.
Find me on LinkedIn for quick findings between posts.
Catch up on the Agentic Engineering series: → Vibe
Coding Is Dead. Here’s What Replaced It. → The
Agentic Engineering Stack — 4 Tools, One System →
Stop Writing Features. Start Designing Agent-Proof
Systems. → Your AI Agent Wrote 500 Lines. Here’s How
to Review It.
AI Agentic Ai Ai Memory Context Engineering
Claude Code
Published in Artificial Intelligence in
Follow
Plain English
41K followers · Last published 9 hours ago


---
*Page 18*


New AI, ML and Data Science articles every day.
Follow to join our 3.5M+ monthly readers.
Written by Ayesha Mughal
Following
851 followers · 3 following
Ayesha Mughal. AI developer & technical writer,
🇵🇰
Karachi Claude Code • Agentic AI • 225K+ views.
ayesha-mughals-portfolio.vercel.app
No responses yet
To respond to this story,
get the free Medium app.
More from Ayesha Mughal and Artificial
Intelligence in Plain English


---
*Page 19*


In by In by
Artificial Intelligen… Ayesh… Artificial Intelligen… Damia…
Claude Code Has Been 5 Real Ways People Are
S i AI A t U i AI t M k
You asked Claude to Most people use AI for faster
d t d l t k A ll i tl
Mar 11 Mar 9
In by In by
Artificial Intelligenc… Baba… Artificial Intelligen… Ayesh…
I Built 8 AI Micro-Tools Your AI Agent Wrote
Th t G t 500 Li f C d
How small AI automations Here’s the productivity
t d t di t k i t d b d i th ti
Feb 23 6d ago
See all from Ayesha See all from Artificial Intelligence in Plain
Mughal English


---
*Page 20*


Recommended from Medium
Vikas Sah In by
Level Up Coding Dean Blank
Build Your First Claude
A Powerful Framework
Skill i 5 Mi t
f M t i Cl d
I was few weeks into using
A two-habit system to use
Cl d ’ C k d h
Cl d ff ti l f d
Mar 7 Mar 18


---
*Page 21*


In by
Towar… Adi Insights and In…
Google Just Released a
7 C AI
Google’s new AI Professional
C tifi t j t t li
Mar 26
See more recommendations