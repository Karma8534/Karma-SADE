# MiniMax4CC

*Converted from: MiniMax4CC.PDF*



---
*Page 1*


Open in app
8
Search Write
Towards AI
Member-only story
MiniMax M2.7 Built
Itself! Here’s How to
Use It Like a Pro
Setup guides and the official prompting guide
from MiniMax’s own docs and the exact
workflow that replaced GLM-5 in my coding
stack.
Adham Khaled Follow 11 min read · Mar 21, 2026
350 1
In 10 minutes you’ll
know exactly what MiniMax M2.7 is,
why the benchmarks matter,


---
*Page 2*


how to set it up in OpenCode, OpenClaw, Claude Code,
and Ollama,
the 5 prompting patterns from MiniMax’s own docs
that most people skip,
and which tasks to give it versus which to keep on
Opus.
MiniMax just released M2.7 days ago and if you’ve
been following my Claude subscription saga, you
already know why I’m writing this at 1 a.m.
I cancelled my Opus API subscription month ago.
Since then, my workflow has been Opus for high-
level planning through only the pro sub. and GLM-
5 for the actual coding grunt work. It’s been solid.
But M2.7 just walked into the room with a 56.22%
SWE-Bench Pro score — nearly matching Opus 4.6
— at roughly 1/20th the price.
This isn’t a review. This is the setup-and-prompting
guide based on their docs.


---
*Page 3*


Source: MiniMax
Table of Contents
1. What MiniMax M2.7 Actually Is
2. The Cost Math: 17x Cheaper Than Opus
3. Step 1: Set It Up (Five Paths, Two Minutes Each)
4. Step 2: The Prompting Playbook That Most
People Miss
5. Step 3: Give It the Right Jobs
6. Why I’m Swapping GLM-5 Out of My Stack
7. The Caveats
What MiniMax M2.7 Actually Is
M2.7 is MiniMax’s new flagship text model — the
latest in their M2 series, built specifically for


---
*Page 4*


software engineering, agentic workflows, and
professional office tasks.
Here’s the spec sheet that matters. It has a 200,000-
token context window — enough to feed it an
entire repository. It’s text-only — no image or audio
input, which keeps it focused and fast. It ships in
two variants: standard and highspeed, where the
highspeed version delivers identical outputs with
significantly faster inference. And here’s the part
that made me sit up — it exposes an Anthropic-
compatible API endpoint, which means any tool
built for Claude can talk to M2.7 by changing two
lines of config.


---
*Page 5*


Source: MiniMax
MiniMax calls this model the beginning of their
“recursive self-improvement” journey. In plain
English, M2.7 doesn’t just write code — it can
iteratively optimize the scaffolding and workflows
around itself.
In internal tests, it ran over 100 autonomous
optimization rounds and improved its own evaluation
scores by 30%. That’s not marketing fluff — that’s a
documented self-evolution loop.
The Cost Math: 17x Cheaper Than Opus
Let’s get to the numbers that actually matter.


---
*Page 6*


MiniMax M2.7 charges $0.30 per million input
tokens and $1.20 per million output tokens. Claude
Opus 4.6 charges $5.00 per million input tokens
and $25.00 per million output tokens.
That’s 17x cheaper on input. 21x cheaper on
output.
Put it in monthly terms. If you’re burning through
30 million input tokens and 10 million output
tokens per month on coding tasks — a realistic
number for an active developer using an AI coding
agent — that’s $400 with Opus. With M2.7, it’s $21.
Same month. Same work volume.
It’s The Best! Source: Artificial Analysis


---
*Page 7*


And the performance gap? On SWE-Bench Pro —
the benchmark that tests real, long-horizon, multi-
file software engineering tasks — M2.7 scores
56.22%. Opus 4.6 is in the same neighborhood. On
VIBE-Pro, which measures end-to-end project
delivery across web, Android, iOS, and simulation
targets, M2.7 hits 55.6%. On GDPval-AA, a
professional knowledge evaluation, M2.7 scores an
ELO of 1,495 — the highest among open-source
models and competitive with Opus 4.6 and GPT-
5.4.
Source: MiniMax


---
*Page 8*


The math is simple. You’re paying 95% less for
90%+ of the capability on coding tasks.
Step 1: Set It Up (Five Paths, Two Minutes
Each)
You can visit MiniMax for a normal chat (free tier)
or you can choose one path from these:
OpenCode (the Best Claude Code Alternative)
If you haven’t switched to OpenCode yet, here’s the
short version: it’s open-source, has 125,000+
GitHub stars, supports 75+ models, and isn’t locked
to any single provider. Claude Code charges you
$20+/month and ties you to Anthropic’s pricing.
OpenCode lets you route to any model — including
M2.7 — through its API, or through two first-party
gateways that most people don’t know about.
OpenCode Go is a $10/month subscription ($5 for
the first month) that gives you generous, rate-
limited access to the best open-source models
including the new M2.7.


---
*Page 9*


Source: OpenCode
OpenCode Zen is the pay-as-you-go alternative — a
curated, benchmarked gateway of 30+ verified
model configurations.
Free-tier models rotate through periodically,
including MiniMax offerings. Both Go and Zen are
currently in beta.
Want faster responses for quick diagnostic
queries? Swap the model to MiniMax-M2.7-
highspeed. Same outputs, higher throughput —
perfect for inner-loop tasks where you're making
rapid tool calls.
OpenClaw (the agentic platform)
This one’s even easier with OAuth:


---
*Page 10*


1. Run the OpenClaw setup and select QuickStart
mode
2. Choose MiniMax as your model provider
3. Select MiniMax Global — OAuth (minimax.io)
for authentication
4. A browser window opens — sign in to your
MiniMax API Platform account and hit
Authorize
5. Back in the terminal, M2.7 is pre-selected. Press
Enter.
Done. OpenClaw automatically configures
MiniMax’s VLM API endpoint too, which gives your
agent image understanding out of the box — no
extra setup. You can connect it to Telegram,
WhatsApp, Discord, or iMessage as a messaging
channel from the same setup flow.
Ollama (cloud-hosted preset)
The simplest path:


---
*Page 11*


ollama run minimax-m2.7:cloud
This proxies to MiniMax’s cloud infrastructure. You
get the full 200k context window, same model, no
local hardware requirements. The :cloud tag is
important — M2.7 doesn't have open weights, so
this is a cloud-only model accessed through
Ollama's preset system.
Claude Code via Ollama (free, limited)
If you’re still on Claude Code and not ready to
switch, Ollama has you covered with zero config.
Ollama’s launch command sets up Claude Code
directly against a cloud model — no API keys, no
environment variables:
ollama launch claude --model minimax-m2.7:cloud
That’s it. Ollama handles the proxy, Claude Code
sees a compatible endpoint, and you’re running


---
*Page 12*


M2.7 as your Claude Code backend for free within
Ollama’s usage limits. No subscription required to
test it. It’s the fastest possible way to try M2.7 in a
real workflow before committing to an API key or
paid plan.
Claude Code via MiniMax API (full power, pay-as-
you-go)
If you want the full 200k context, no rate limits,
and direct API access inside Claude Code — skip
Ollama and connect straight to MiniMax’s
Anthropic-compatible endpoint.
Set these environment variables before launching
Claude Code:
export ANTHROPIC_BASE_URL="https://api.minimax.io/ant
export ANTHROPIC_AUTH_TOKEN="YOUR_MINIMAX_API_KEY"
export API_TIMEOUT_MS="3000000"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"
Or, if you prefer a persistent config, add this to
~/.claude/settings.json:


---
*Page 13*


{
"env": {
"ANTHROPIC_BASE_URL": "https://api.minimax.io/ant
"ANTHROPIC_AUTH_TOKEN": "YOUR_MINIMAX_API_KEY",
"API_TIMEOUT_MS": "3000000",
"CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1"
}
}
Two things to note. First, environment variables
take priority over settings.json — so if you've
previously set ANTHROPIC_AUTH_TOKEN in your shell
profile, that will override whatever's in the config
file. Clear them if you're going the settings.json
route. Second, the API_TIMEOUT_MS is set to
3,000,000 milliseconds (50 minutes) because M2.7's
long-context tasks can run significantly longer
than Claude's default timeout expects.
Now launch claude as normal. Every request
routes through MiniMax at $0.30/$1.20 per million
tokens instead of Anthropic's $5/$25. Same Claude
Code interface, same commands, same workflows
— 17x cheaper backend.


---
*Page 14*


Step 2: The Prompting Playbook That
Most People Miss
Here’s where most developers fumble. They throw
the same prompts they use for ChatGPT or Claude
at M2.7 and get mediocre results. MiniMax’s own
documentation reveals five prompting patterns
that unlock the model’s real capability — and
almost nobody reads vendor docs.
Tell it WHY, not just WHAT
M2.7 performs measurably better when it
understands your intent. This is the single biggest
lever.
Less effective:
Do not use document symbols
More effective:


---
*Page 15*


Your response will be read aloud by a text-to-speech
so present it in plain text format and avoid using do
symbol formatting
The second prompt gives M2.7 the reasoning
behind the constraint. It can then generalize — it
won’t just avoid headers, it’ll also skip bullet
points, code blocks, and other formatting that
would sound wrong when spoken aloud.
This applies to every instruction. Don’t say “write
clean code.” Say “this code will be reviewed by a
junior developer who joined the team last week, so
prioritize readability and add inline comments
explaining non-obvious decisions.”
Show a good example AND a bad example
M2.7 generalizes well from templates. Give it both
sides of the quality spectrum.
Less effective:


---
*Page 16*


Write an engaging product description for a smart the
More effective:
Please write a product description following this exa
[Good: This desk lamp uses full-spectrum LED technolo
simulates natural morning light. It features 6 bright
levels for reading, working, and resting.]
Please avoid vague descriptions like this:
[Bad: This desk lamp is great, the light is comfortab
and the design is nice.]
Now, write a description for a 'smart thermos'.
This works for code too. Show it a function that
follows your team’s conventions, then show one
that violates them. M2.7 will internalize the
pattern.
Manage the 200k context window
deliberately
This is where M2.7 gets tricky. It has a massive
200,000-token context window — enough for an
entire codebase. But MiniMax’s own docs warn


---
*Page 17*


that the model may terminate tasks early when
approaching capacity thresholds.
The fix: keep your system prompts lean. If you’re
using tools that support context compression like
OpenCode, control the token count of your
instructions. Don’t dump your entire project
documentation into the system prompt just
because you can.
Use multi-window workflows for big tasks
For complex, multi-step projects, MiniMax
recommends a phased approach:
First window: Set up the framework —
architecture, tests, initialization scripts
Second window: Iterate through the actual
implementation tasks
Create a tests.py or tests.json file to track
progress across windows


---
*Page 18*


Create an init.sh script that starts servers and
runs tests — this eliminates repetitive setup
when opening fresh windows
Use compression for continuing a single task;
restart with a fresh window for new tasks
This is not how most people use AI coding tools.
They dump everything into one marathon session
and wonder why quality degrades at the 80% mark.
The system prompt trick for long tasks
When you need M2.7 to handle a lengthy task
without cutting corners, add this to your system
prompt:
This is a very lengthy task. Make full use of the com
output context — keep total input and output tokens w
200k tokens. Use the full context window length to co
the task thoroughly and avoid exhausting tokens prema
This explicitly tells the model to pace itself rather
than rushing to a premature conclusion. It sounds


---
*Page 19*


simple, but it measurably improves output
completeness on long-horizon tasks.
Step 3: Give It the Right Jobs
M2.7 isn’t a universal replacement for every model
in your stack. It’s a specialist — and knowing where
to deploy it is the difference between “meh” and
“this thing is incredible.”
Where M2.7 dominates:
Long-horizon software engineering. Multi-file bug
fixes, repository-level refactors, end-to-end project
scaffolding. Its 56.22% SWE-Bench Pro score isn’t
just a number — SWE-Bench Pro tests real
enterprise-style issues where a single task touches
multiple files and requires significant edits. Most
models score below 50% on Pro, even if they crush
easier benchmarks.
Tool-calling and agentic workflows. On MiniMax’s
Toolathon benchmark, M2.7 hits 46.3% accuracy


---
*Page 20*


on multi-tool reasoning tasks. More impressively, it
maintains a 97% skill adherence rate when
operating with 40 complex skills, each exceeding
2,000 tokens. That’s the stat that matters for anyone
building agent systems — it follows long, detailed
instructions without drifting.
Bulk coding tasks. The highspeed variant is built
for this. Quick diagnostic queries, rapid tool calls,
small code generation tasks — all at the same
quality level as the standard model but with
significantly faster throughput.
Production debugging. MiniMax demonstrates
M2.7 correlating monitoring metrics with
deployment timelines, performing statistical
analysis on traces, and proactively connecting to
databases to verify root causes. They claim
recovery times under three minutes for some
production incidents.
Where to keep Opus (or another frontier model):


---
*Page 21*


Strategic planning and architectural decisions.
When I’m designing a system architecture or
making high-stakes technical decisions, I still want
Opus-level reasoning. M2.7 is an executor, not a
philosopher.
Creative and nuanced writing. M2.7 is a text-first
coding model. It’s not optimized for the kind of
nuanced creative work that Opus handles well.
Multimodal tasks. M2.7 is text-only. If you need
image understanding, audio processing, or visual
reasoning, you need a different model.
Why I’m Swapping GLM-5 Out of My Stack
My workflow for the past month has been
straightforward — Opus for planning, GLM-5 for
execution. GLM-5 has been excellent for its price
tier, and I’ve recommended it publicly multiple
times.


---
*Page 22*


But M2.7 shifts the equation in three ways. First,
the Anthropic-compatible API is a genuine game-
changer for tool integration. GLM-5 requires
custom configuration for every tool. M2.7 slots
into any Anthropic-compatible tool by swapping a
base URL and API key. That alone saves hours of
setup across my workflows.
Second, the benchmarks favor M2.7 for software
engineering specifically. SWE-Bench Pro 56.22%
puts it in a different tier than most models for the
kind of multi-file, long-horizon coding tasks I
actually do.
Third, the 200k context window with 128k max
output gives M2.7 breathing room that matters for
repository-scale work. Feed it an entire module,
get back a complete implementation — not a
truncated one with “// … rest of implementation”
comments.


---
*Page 23*


GLM-5 isn’t going anywhere in the broader
ecosystem. But for my coding stack specifically,
M2.7 just earned the spot.
The Caveats (Because I’m Not a Hype
Writer)
Full transparency — because I’ve called out hype
before and I’m not stopping now.
M2.7 has no open weights. It’s cloud-only. You can’t
self-host it or inspect the architecture. MiniMax
hasn’t disclosed the parameter count, training data
composition, or detailed RL methodology. If model
transparency matters to your organization, that’s a
real limitation.
There are no independent third-party evaluations
yet. The benchmarks I cited come from MiniMax’s
own blog and derivative sources. The model
dropped yesterday — give it a few weeks for the
community to run standardized evaluations with
open scripts.


---
*Page 24*


And because this is a brand-new release, expect
rough edges. Every model has them at launch. I’ll
update this article as the community digs in and as
I put it through my own daily workflow.
Your Move
M2.7 is live right now. The setup takes five
minutes. The prompting playbook above is what
separates “another AI model” from “the thing that
cut my coding costs by 95%.”
I’m integrating it into my workflow starting today
— Opus for planning, M2.7 for execution. If the
benchmarks hold up in real-world usage, this
might be the article where I tell you I cancelled
something again.
What’s your current AI coding stack? And more
importantly — what would it take for you to switch?
Artificial Intelligence Software Development Programming


---
*Page 25*


Writing Prompts Technology
Published in Towards AI
Following
119K followers · Last published just now
We build Enterprise AI. We teach what we learn. Join
100K+ AI practitioners on Towards AI Academy. Free:
6-day Agentic AI Engineering Email Guide:
https://email-course.towardsai.net/
Written by Adham Khaled
Follow
15.1K followers · 122 following
10x Boosted Writer || Embedded Systems Engineer ||
Technical Writer || https://adhamkhaled.vercel.app/
Responses (1)
To respond to this story,
get the free Medium app.
Andy Eadie
Mar 23


---
*Page 26*


I use ChatGPT as architect/ thinking partner and Codex as code builder.
All for 20 bucks without ever having hit the limit that I hit daily on Claude
Code. Is minimax m2.7 comparable to codex 5.4 in coding?
2
More from Adham Khaled and Towards AI
In by In by
Generative AI Adham Khaled Towards AI Rohan Mistry
Stop Saying “It’s Just The 10 Claude Plugins
N t T k P di ti Y A t ll N d i
Why GRPO, RLVR, and the How to transform Claude from
“R i E ” h fi ll h tb t i t AI th t
Jan 27 Mar 17


---
*Page 27*


In by In by
Towards AI Divy Yadav Level Up Cod… Adham Kha…
LLM Observability: The I’ve Never Opened
Mi i L i M t Bl d I B ilt 3D
For developers who shipped A complete beginner’s
LLM li ti d t t f i f 3
Mar 14 Mar 6
See all from Adham Khaled See all from Towards AI
Recommended from Medium


---
*Page 28*


Ignacio de Gregorio In by
Data Science Co… Paolo Pe…
Why Everyone is Doing
The Complete Claude
A t W
A hit t St d G id
Agents aren’t magic; we
Everything you need to build,
li t th
fi d hi d ti
Mar 24 6d ago
In by In by
Let’s Code Fut… Deep conc… Level Up Coding David Lee
20 Most Important AI The Rules NASA Uses
C t E l i d i t W it C d Th t
Beginner-Friendly Guide In 2006, a NASA engineer
t t l f iti
5d ago Mar 18


---
*Page 29*


In by In by
Write A C… The Curious Fin… Artificial Intelligenc… Faisal…
The Last Time This Vector RAG Is Dead.
H d L t f P I d J t P
How a historic wave of money How a reasoning-based, tree-
i b t t h thi h f k hi d
Mar 14 Mar 21
See more recommendations