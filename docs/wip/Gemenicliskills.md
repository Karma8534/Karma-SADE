# Gemenicliskills

*Converted from: Gemenicliskills.PDF*



---
*Page 1*


Open in app
6
Search Write
Member-only story
Gemini CLI + Agent
Skills: Supercharge
Your Developer
Workflow | Part-8
Simranjeet Singh Following 18 min read · 4 days ago
1
The Pain Every Developer Knows
You’re 45 minutes into a coding session. Your AI
assistant has been helpful, mostly. Then it suggests
gemini-1.5-pro your new project. You correct it.
Ten minutes later, it scaffolds a Python file with no


---
*Page 2*


linting setup. You remind it you use ruff. It
apologises and fixes it. Then it writes a commit
message in a style you hate.
You’ve had this exact conversation before. Last
Tuesday. And the Tuesday before that.
This is not an AI problem. It is a memory problem.


---
*Page 3*


Gemini CLI + Agent Skills: Supercharge Your Developer Workflow
Every session starts at zero. Your preferences, your
workflows, your team standards, your go-to
package versions — gone. You are not working with
an assistant that knows you. You are working with
a very smart stranger who forgets everything
overnight.


---
*Page 4*


According to Google’s ADK team, this context
overhead is one of the primary reasons developer
productivity gains from AI assistants plateau after
the first few weeks. The novelty wears off when
you realise 20% of your prompts are just
reteaching the same rules.
What if your AI coding assistant could remember
how you work forever?
That is exactly what agent skills are designed to
solve. Not a feature. Not a plugin. Institutional
memory for your AI, written once, reused
infinitely, across every session, every project, and
every teammate who joins your repo.
You define how you work. The agent learns it
permanently.
Google ADK In-Depth Series of Learning Agentic
AI


---
*Page 5*


1. Google ADK in 2026: The Complete Beginner’s
Guide to Building AI Agents | Part-1
2. Your First Google ADK Agent with Skills: Build a
Weather and News Agent in 30 Minutes | Part-2
3. Mastering ADK Tools: Function Tools, MCP
Tools, OpenAPI Tools & When to Use Each | Part-
3
4. ADK Skill Tool That Write Skills: Building Self-
Extending AI Agents with Google ADK | Part-4
5. Google Agent Skills Explained: The Open
Standard Changing How AI Agents Work | Part-5
6. ADK Memory, Sessions & State: Building Agents
That Remember | Part-6
7. Multi-Agent Systems with ADK: Build Your Own
AI Research Team | Part-7
8. Gemini CLI + Agent Skills: Supercharge Your
Developer Workflow | Part-8
9. Firebase + Agent Skills: Add AI Superpowers to
Your Firebase App | Part-9


---
*Page 6*


10. Grounding ADK Agents: Google Search, Vertex
AI Search & RAG Patterns | Part-10
11. ADK + MCP: Connecting Your Agent to Any Tool
in the World | Part-11
12. Build a Full-Stack AI SaaS App with Google ADK:
From Idea to Live Product | Part-12
What Are Agent Skills?
If you’re new here, I covered Agent Skills in depth
in Part 2 of this series, go read that first if you
want the full picture. Here’s the short version.
A skill is a self-contained instruction package. It
lives in a folder with a SKILL.md file at its core, and
it gets loaded into your agent's context only when
it's needed — not upfront, not always, only when
triggered. This pattern is called Progressive
Disclosure, and it's the reason skills don't bloat
your context window the way a stuffed system
prompt does.


---
*Page 7*


Every skill follows this structure:
my-skill/
├── SKILL.md ← L1 metadata + L2 core instru
├── references/ ← L3 deep docs, loaded on dema
├── assets/ ← templates, schemas, data fil
└── scripts/ ← executable automations (expe
The SKILL.md file carries two things: a short
frontmatter block that tells the agent when to use
this skill and the actual instructions it follows when
it does. The references/ folder holds the heavy
stuff — API schemas, detailed guides, and
extended workflows, that only gets pulled in when
the task actually needs it.
Why does this matter? Because you’re paying per
token, and context space is finite. A well-designed
skill might be 2,000 tokens deep, but your agent
only pays that cost when the skill fires. Compare
that to dumping everything into a system prompt
on every single request.


---
*Page 8*


💡
Think of Skills like .cursorrules for Gemini
CLI, except they're standardized, installable,
shareable across your whole team, and
composable with each other.
That’s all you need to follow the rest of this article.
Let’s build something.
Setting Up Gemini CLI
Five minutes and you’re running. Here’s
everything you need:
# Install Gemini CLI
npm install -g @google/gemini-cli
# Verify installation
gemini --version
# Authenticate with your Google account
gemini auth login
# Check your global skills directory
ls ~/.gemini/skills/


---
*Page 9*


Skills live in one of two places depending on their
scope:
~/.gemini/skills/ — global skills, available in
every project on your machine
.gemini/skills/ — project-local skills, only active
inside that folder
⚠
Project skills always override global skills with
the same name. This is useful when you need a
project-specific version of a shared skill — just
drop it in .gemini/skills/ and it takes precedence
automatically.
To pull skills from a public repository, use npx
skills:
# See everything available in a skills repo
npx skills add google-gemini/gemini-skills --list
# Install a specific skill globally
npx skills add google-gemini/gemini-skills --skill ge


---
*Page 10*


You can install from any GitHub repo that follows
the Agent Skills spec, not just Google’s official one.
We’ll use this in Section 5 when we pull real
community skills.
That’s it. You’re set up. Now let’s talk about the
feature that makes skill creation feel like magic.
The Meta-Skill: Your AI
skill-creator
Writes Its Own Instructions
There is a project I created in Part 4 that shows this
project live and that creates its own skills using
web search as well.
Check this Project : ADK Skill Tool That Write Skills:
Building Self-Extending AI Agents with Google ADK


---
*Page 11*


An agent that can write its Own Skills
Gemini CLI ships with a built-in skill called skill-
creator,a meta-skill whose entire job is to help you
build other skills. Instead of staring at a blank
SKILL.md and wondering how to structure your
instructions, you just describe what you want and
let Gemini interview you.
You trigger it naturally. Any of these work:
"I want to create a new skill to [describe your need]
"Use the skill-creator to build a skill that [does X]
"Refactor my existing [process] into a reusable skill


---
*Page 12*


What happens next is where it gets interesting. The
user skill-creator uses the ask_user tool to gather
requirements before writing a single line. Here's a
real example of building a git-commit-writer skill:
You: "Use the skill-creator to build a skill that wri
conventional commits for my changes"
Gemini: [Triggers skill-creator]
→ "What commit format do you prefer? (conventional /
→ "Should it auto-stage modified files before commit
→ "Any specific scopes for your project? (feat, fix,
→ "Should it generate a commit body, or subject line
[Gemini generates the full skill directory]
After answering four questions, you get a
complete, ready-to-use skill. Here’s what the auto-
generated output looks like, annotated so you can
see what each part does:
---
name: git-commit-writer # ← s
description: >
Writes conventional commits based on staged # ← T
changes. Use when committing code changes. # Ke
---


---
*Page 13*


## Commit Format
Always use the Conventional Commits spec:
<type>(<scope>): <subject>
Allowed types: feat, fix, docs, style, refactor, test
Project scopes: api, auth, ui, db
## Workflow
### Step 1: Inspect changes
Run `git diff --staged` to understand what changed.
If nothing is staged, run `git diff` and ask the user
which files they want to include.
### Step 2: Write the commit
- Subject line: 72 chars max, imperative mood ("add"
- Body: include only if the WHY is non-obvious
- Never mention "refactor" or "cleanup" without speci
### Step 3: Confirm before committing
Show the full commit message and ask:
"Commit with this message? (yes / edit / cancel)"
Never run `git commit` without explicit confirmation.
Notice the structure: the frontmatter description is
what the model reads to decide whether to use this
skill. The instruction body is what it reads after
deciding. Keeping them separate means the agent
makes a cheap decision first, then loads the
expensive instructions only when needed.
A skill is never done on the first try. The best
workflow: use it in a real session, notice where it


---
*Page 14*


breaks or gets confused, then say “use skill-creator
to improve my git-commit-writer skill based on what
just went wrong.” Skills get sharper every time you
refine them — treat them like living
documentation, not set-and-forget config.
The real power here isn’t just automating a task.
It’s encoding your standards — your team’s commit
style, your project’s scopes, your confirmation
preferences — so every session starts from the
same baseline without you having to re-explain
anything.
Real Skills Deep Dive: Recreating 3
Community Skills
This is where the article earns its bookmark. Three
real, battle-tested skills, full SKILL.md files, design
decisions explained, and ready to install and use
today.
Skill 1: Kill Hallucinated Package Versions


---
*Page 15*


The problem: You ask Gemini to add a
dependency, and it confidently suggests gemini-
1.5-pro, numpy==1.21, or a framework API that was
deprecated 18 months ago. It's not lying — it just
genuinely doesn't know what "latest" means
anymore. Its training data has a cutoff. Yours
doesn't.
This skill fixes that by making version verification
mandatory, not optional.
---
name: latest-version
description: >
The definitive real-time source of truth for softwa
model versions. Use this skill to bypass internal k
and verify current versions before any install or d
---
## Core Mandate
**NEVER GUESS.** When asked to install a package or a
you MUST verify the latest version using available to
registries. Do not rely on internal training data for
## How to Verify Versions
### For Python packages (PyPI):
Query: https://pypi.org/pypi/{package_name}/json
Extract: response.info.version
### For Node.js packages (npm):


---
*Page 16*


Command: npm view {package} version
Or: https://registry.npmjs.org/{package}/latest
### For Gemini/Google AI Models:
Always check: https://ai.google.dev/gemini-api/docs/m
Current flagship: Refer to documentation, never assum
## Response Format
Always state the verified version explicitly:
"The latest version of {package} is {version} (verifi
Never say "I believe" or "should be" for version numb
Why it’s written this way:
The mandate is in bold and all caps because LLMs
respond to emphasis, **NEVER GUESS.** is a hard
stop, not a suggestion. Multiple registries are listed
because no single source covers everything: PyPI
for Python, npm for Node, and a direct docs link
for Google models specifically (because no registry
tracks model names the way package managers
do). The response format demands the word
"verified" explicitly — that one word forces the
model to have actually checked, not paraphrased
from memory.
Skill 2: Python Development with Enforced
Quality


---
*Page 17*


The problem: AI-generated Python tends to skip
type hints, ignore your project’s existing style, and
never run the linter. You end up doing a cleanup
pass after every AI edit, which defeats half the
point of having an AI.
This skill enforces a non-negotiable edit cycle on
every single file change.
---
name: pyhd
description: >
Python development workflow enforcing ruff linting,
and pythonic best practices. Triggers on any Python
---
## Core Workflow
When editing any Python file, follow this exact cycle
### Step 1: Read & Understand
Before editing, read the full file. Understand the ex
imports, and code style already in use.
### Step 2: Apply Changes
Use smart_edit or replace to make your modifications.
### Step 3: Sanitize with Ruff (MANDATORY)
Immediately after every edit, run:
```bash
uv run ruff check --fix {filename}
uv run ruff format {filename}
```


---
*Page 18*


Never skip this step. Never make multiple edits befor
### Step 4: Verify
Run relevant tests if a test file exists:
```bash
uv run pytest {test_file} -v
```
## Python Standards
- Type hints: Always add for function signatures
- Docstrings: Google style for public functions
- Imports: isort-compatible ordering
- Line length: 88 characters (ruff default)
- f-strings: Prefer over .format() or % formatting
## When Creating New Files
Always start with: module docstring, imports, then co
Never create a .py file without running the sanitize
Why it’s written this way:
The numbered steps aren’t just for readability,
they’re a forcing function. When instructions are
sequential and numbered, models follow them
sequentially. The word MANDATORY on Step 3 exists
because that's the step models are most likely to
skip when they're in a hurry to show you the result.
Never make multiple edits before sanitizing closes
the loophole where a model batches three changes
and then "forgets" to lint. Every standard in the


---
*Page 19*


Python Standards section is a specific, measurable
rule — not a vibe.
Skill 3: AI Writing Quality Checker
de-sloppify:
The problem: AI-generated writing is littered with
tells. “Delve into”, “leverage”, “comprehensive
solution”, “it is worth noting” — the prose is
technically correct and completely lifeless. Worse,
most models won’t catch their own patterns unless
you give them a specific checklist to check against.
This skill turns your AI into its own editor.
---
name: de-sloppify
description: >
Checks text for AI writing patterns and calculates
Use when reviewing or generating written content fo
---
## When to Trigger
- After drafting any documentation, README, or blog p
- When asked to "review", "improve", or "polish" writ
- Before any content is marked as final
## What to Check
### High-Risk Words (eliminate entirely):
delve, leverage, comprehensive, robust, seamless, cut


---
*Page 20*


innovative, utilize (use "use"), facilitate, paradigm
### Structural Patterns to Fix:
- Passive voice > 20% of sentences: rewrite to active
- Sentences starting with "It is" or "There are": rep
- Consecutive sentences of similar length: vary rhyth
- Lists of 3+ items that could be prose: convert
## Scoring Guide
Count violations and report:
✅
- 0-2: Clean
⚠
- 3-5: Needs work
🚨
- 6+: Major revision needed
## Fix Protocol
For each violation found:
1. Quote the original offending phrase
2. Explain why it's problematic
3. Provide the rewritten version
Why it’s written this way:
The banned word list is exhaustive and
opinionated on purpose. "Utilise" has a specific
replacement in parentheses — (use "use") —
because without it, a model will just find a
different formal synonym. The scoring guide gives
the output a consistent, scannable shape so you get
the same format every time, not a different
structure each run. The Fix Protocol forces the


---
*Page 21*


model to quote, then explain, then rewrite, which
produces actually useful feedback instead of a
vague "this sentence could be clearer".
Three skills, three different problems, one consistent
pattern: specific language beats general guidance
every time. The more precisely you write a skill, the
less you have to babysit the model.
Install all three from the companion repo and start
using them today.
Building Your Own Workflow Skill From
Scratch
The three skills in Section 5 are useful out of the
box. But the real leverage comes when you start
encoding your workflows — your team’s standards,
your project’s quirks, your personal preferences.
Here’s the full process, start to finish, using a pr-
reviewer skill as the example.
Step 1: Identify the Repetitive Conversation


---
*Page 22*


Before you open a file, ask yourself one question:
when do I keep re-explaining the same thing to
Gemini?
That friction is your signal. Maybe you’ve typed
“check for hardcoded secrets” in five different
sessions. Maybe you always have to remind it to
look at edge cases before suggesting a fix. Maybe
every code review it produces is a wall of text with
no structure you can actually act on.
Any time you find yourself prefacing a request
with the same paragraph of context — that’s a skill
waiting to be written.
For this example: PR reviews. Left to its own
devices, Gemini produces inconsistent feedback.
Sometimes thorough, sometimes shallow, always
in a different format. A skill fixes all three
problems at once.
Step 2: Use to Get Your First Draft
skill-creator


---
*Page 23*


Don’t start from a blank file. Trigger skill-creator
and let it interview you:
You: "Use the skill-creator to build a pr-reviewer sk
Gemini: [Triggers skill-creator]
→ "What should the review prioritize - security, log
→ "Should it run git commands to fetch the diff, or
→ "What output format does your team prefer for revi
→ "Any languages or frameworks the reviewer should b
Answer honestly and specifically. The quality of
your answers directly determines the quality of the
first draft. You’ll refine it — but a good first draft
saves you 20 minutes of staring at an empty
SKILL.md.
Step 3: Refine the SKILL.md Manually
The skill-creator output is a solid starting point,
rarely a finished product. The most important edit
you'll make is replacing vague instructions with
specific ones.
Here’s what that difference looks like in practice:


---
*Page 24*


❌
# Vague - won't work reliably
Review the PR and give feedback.
✅
# Specific — reliable and consistent every time
## PR Review Protocol
When asked to review a PR or diff, follow these steps
### 1. Summary (2-3 sentences)
What does this PR do? What's the business reason?
### 2. Security Scan
Check for: hardcoded secrets, SQL injection points,
unvalidated user input, auth bypasses
### 3. Logic Review
Identify: edge cases not handled, missing error state
incorrect assumptions about data types
### 4. Code Quality
Check: duplicate code, naming clarity, unnecessary co
missing tests for new logic
### 5. Output Format
Use this exact structure every time:
**Summary:** [2-3 sentences]
🔴
** Blockers:** [list or "None"]
🟡
** Suggestions:** [list or "None"]
✅
** Looks Good:** [what's done well]
The vague version puts all the decision-making on
the model. The specific version tells it exactly what
to check, in what order, and what the output
should look like. The model’s job becomes


---
*Page 25*


execution, not interpretation — which is where
consistency comes from.
Step 4: Test, Break It, Refine
Run the skill on a real PR. Not a clean one — find a
messy one with a missing error handler and an
overly clever variable name. See what the skill
catches and what it misses.
When it misses something obvious, don’t just fix it
manually. Say this instead:
"Use the skill-creator to improve my pr-reviewer skil
it missed the missing null check in the last review.
Add a rule for checking nullable return values."
Gemini will read your existing SKILL.md, identify
where the gap is, and patch it. After two or three
real sessions, your skill stops missing things. That's
the refinement loop — and it's faster than you'd
expect.
💡
Pro tips before you publish your first skill:


---
*Page 26*


The frontmatter description is everything. It's
the one sentence the model reads to decide
whether to use this skill at all. Make it specific —
"use when reviewing PRs or git diffs" beats "code
review helper" every time.
Write instructions in imperative language.
“Check for hardcoded secrets” not “you should
look for hardcoded secrets.” Commands work
better than suggestions.
Put your most important constraint first.
Models read top-to-bottom. If “never commit
without confirmation” matters most, it goes on
line one — not buried in Step 4.
Add a bad example when precision matters.
Showing the model what not to do is often more
effective than describing what to do. A single ❌
example can eliminate an entire class of wrong
outputs.
The methodology is always the same: find the
repetition, draft with skill-creator, sharpen the


---
*Page 27*


instructions, test on real work, refine. After a few
cycles you'll have a skill that handles the task
better than any one-off prompt ever could — and it
works that way every single time, for everyone on
your team.
Advanced Pattern
Skills with references/ for Deep Context
Your SKILL.md should be lean. It carries the
instructions the agent needs to decide what to do
and start doing it — nothing more. The moment
you find yourself writing "refer to the full API docs
for parameter details" inside a SKILL.md, stop. That
detail belongs in references/.
The rule of thumb is simple: if it’s context the
agent needs sometimes but not always, it’s a
reference file.
Here’s what that looks like for a skill that wraps a
custom internal API:


---
*Page 28*


my-api-skill/
├── SKILL.md ← core instructions + poin
└── references/
├── api-schema.yaml ← full OpenAPI spec, loade
└── auth-guide.md ← OAuth flow, token refres
The SKILL.md stays short and tells the agent exactly
when to reach for the heavy files:
---
name: my-api-skill
description: >
Use when making calls to the internal data API. Han
endpoint selection, and parameter validation.
---
## Using the API
When making any API call, follow this order:
### Step 1: Load the schema
FIRST read `references/api-schema.yaml` in full.
Do not guess endpoint paths or parameter names - veri
### Step 2: Check auth
If the request requires authentication, read `referen
before constructing the request. Token format and ref
documented there.
### Step 3: Make the call
Use only endpoints and parameters confirmed in the sc
If an endpoint you need isn't in the schema, say so -


---
*Page 29*


The agent loads api-schema.yaml only when it's
actually making an API call — not on every single
request. If your schema is 3,000 tokens, that's 3,000
tokens you're not paying for until the moment
they're useful.
This pattern scales well beyond API schemas.
Anything bulky and occasionally needed belongs
in references/:
Database table definitions for a SQL-writing skill
Brand voice guidelines for a content-writing skill
Architecture decision records for a code-review
skill
Environment setup docs for an onboarding skill
The references/ folder is your skill's long-term
memory on disk. Keep SKILL.md as the sharp edge
— fast, focused, always loaded. Let references/
carry the weight that only gets pulled when the job
actually needs it.


---
*Page 30*


The result is a skill that feels lightweight to run but
has genuine depth when the situation calls for it.
That balance — lean by default, deep on demand —
is what separates a professional skill from a
bloated system prompt.
Skills Repository Structure: Organize Like
a Pro
Once you have more than three skills, a flat folder
stops working. The structure that scales best for
teams is a single shared repository organized by
category — one source of truth, version-controlled,
installable by anyone in one command.
team-skills/
├── README.md
├── code-quality/
│ ├── pyhd/
│ ├── eslint-enforcer/
│ └── pr-reviewer/
├── documentation/
│ ├── readme-writer/
│ └── de-sloppify/
├── workflow/
│ ├── git-commit-writer/
│ └── release-notes/


---
*Page 31*


└── domain/
├── our-api-v2/
└── internal-data-schemas/
The category folders aren’t enforced by the spec —
they’re just good hygiene. code-quality/ for
anything that enforces standards on code,
documentation/ for writing and review skills,
workflow/ for repeatable processes, and domain/
for anything specific to your product or internal
systems.
Pin releases to a git tag so your team always installs
a known-good version, not whatever landed on
main this morning:
# Install a specific skill globally across your machi
npx skills add your-org/team-skills --skill pr-review
# Install a project-local skill (no --global flag)
npx skills add your-org/team-skills --skill pyhd


---
*Page 32*


Treat your skills repo like any other internal
library. PRs to add skills, changelog entries when
instructions change, and a short README.md per
skill explaining what triggers it and what it
produces. New team members get up to speed on
your AI workflow the same day they clone the
repo.
Conclusion: Skills Are Living
Documentation
You started this article re-explaining your
standards to an AI on every session. If you’ve
followed along, you now have a latest-version
skill that never hallucinates a package version, a
pyhd skill that enforces your Python quality bar
without reminders, a de-sloppify skill that catches
AI writing patterns before they ship, and a pr-
reviewer skill that produces consistent, structured
feedback every single time.
That’s not a collection of prompts. That’s
institutional knowledge — encoded once, reused


---
*Page 33*


forever, and sharpened every time you refine it.
The key insight to take away: a skill gets better
every time you use it. Every session where it
misses something is raw material for the next
iteration. Run it, notice the gaps, fire up skill-
creator, and patch them. Within a few real-world
uses, your skills will outperform any one-off
prompt you've ever written.
Missed the multi-agent architecture that powers the
systems these skills plug into? Catch up with Blog 6:
Multi-Agent Systems with ADK. Next up in the series:
Blog 8: Firebase + Agent Skills — where we wire these
skills into a live Firebase application and deploy the
whole thing.
What’s the first workflow skill you’d build? Drop it
in the comments — the best idea gets a full
SKILL.md template written up in the next post.


---
*Page 34*


Resources and Further Reading
Everything referenced in this blog, ready to open:
📘
ADK Skills documentation — how
SkillToolset, load_skill_from_dir, and the Skills
experimental feature work inside ADK:
google.github.io/adk-docs/skills
📘
agentskills.io specification — the complete
open standard for Skill structure, naming rules,
frontmatter fields, and the Progressive
Disclosure model: agentskills.io/specification
💻
Full project repository — every file from this
blog, ready to clone and run:
github.com/simranjeet97/SelfExtendingAgent_ADKGo
ogle
🐍
ADK skills_agent sample — Google’s official
Skills example including both file-based and
inline Skill definitions: github.com/google/adk-
python/tree/main/contributing/samples/skills_a
gent


---
*Page 35*


If this guide helped you…
If you learned something new or found this
breakdown useful:
Drop a comment — share which metrics you’ve
found most reliable in your projects.
Clap (or double-clap!) to help more AI builders
discover this guide.
Share it with your teammates or community, every
conversation brings us closer to better, fairer AI
evaluation.
GenAI Full Roadmap [ Learning LLM — RAG -
Agentic AI with Resources] :
https://youtu.be/4yZ7mp6cIIg
󰞵
Agentic AI 14+ Projects-
https://www.youtube.com/playlist?


---
*Page 36*


list=PLYIE4hvbWhsAkn8VzMWbMOxetpaGp-p4k
󰞵
Learn RAG from Scratch —
https://www.youtube.com/playlist?
list=PLYIE4hvbWhsAKSZVAn5oX1k0oGQ6Mnf1d
󰞵
Complete Source Code of all 75 Day Hard
🌀
GitHub —
https://github.com/simranjeet97/75DayHard_GenA
I_LLM_Challenge
🔀
Kaggle Notebook —
https://www.kaggle.com/simranjeetsingh1430
󰞵
Exclusive End to End Projects on GenAI or
Deep Learning or Machine Learning in a Domain
Specific way —
https://www.youtube.com/@freebirdscrew2023
If you like the article and would like to support me
make sure to:


---
*Page 37*


👏 󰗔
Clap for the story (100 Claps) and follow me
Simranjeet Singh
📑
View more content on my Medium Profile
🔔
Follow Me: Medium | GitHub | Linkedin |
Community
🚀
Help me in reaching to a wider audience by
sharing my content with your friends and
colleagues.
Press enter or click to view image in full size
What do you choose?


---
*Page 38*


Agentic Ai Artificial Intelligence Google Gemini Google
Technology
Written by Simranjeet Singh
Following
3.6K followers · 40 following
ML Engineer at Google l Ex-Aditya Birla Capital,
Ex-EXL, Ex-TCS | 7 Years of in
GenAI/LLMs/RAG/AgenticAI and ML Experience
| Open for Collaborations
No responses yet
To respond to this story,
get the free Medium app.
More from Simranjeet Singh


---
*Page 39*


In by In by
Artificial Intellige… Simranj… Artificial Intellige… Simranj…
TurboQuant: Google’s Agentic AI Projects:
“Pi d Pi ” M t B ild 14 H d O AI
How Google Squeezed 6x Explore 14 real-world Agentic
M AI I t th S AI j t d 2 k t t i l
3d ago Jul 6, 2025
Simranjeet Singh Simranjeet Singh
Uber Architecture — Don’t Build a
P t 5 Th Di t h Di t ib t d S t
Understand Uber Architecture Before building microservices,
i D th L b t Ub d t d th 5
2d ago Mar 11
See all from Simranjeet Singh


---
*Page 40*


Recommended from Medium
In by In by
Towards AI Rick Hightower Data Science Co… Paolo Pe…
Claude Certified The Complete Claude
A hit t Th A hit t St d G id
Everything You Need to Know Everything you need to build,
t A th CCA F d ti fi d hi d ti
Mar 24 5d ago


---
*Page 41*


In by Michal Malewicz
UX Planet Nick Babich
Vibe Coding is OVER.
Claude Code Memory
2 0 Here’s What Comes Next.
Exploring the Claude Code
A t d
Mar 25 Mar 24
In by Sourav Banerjee
AWS in Plain E… Rohith Lya…
The Evolution of
What Is Prompt
R t i l A
E i i ? Th
Large Language Models
Section 7: Prompt Engineering
(LLM ) i dibl
Dec 30, 2025 Mar 3
See more recommendations