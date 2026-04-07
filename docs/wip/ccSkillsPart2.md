# ccSkillsPart2

*Converted from: ccSkillsPart2.pdf*



---
*Page 1*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Member-only story
Google Agent Skills Explained: The
Open Standard Changing How AI
Agents Work | Part-5
Simranjeet Singh Following 27 min read · Just now
1
You’ve been here before.
You’re building an agent. It needs to handle a dozen different tasks —
reviewing pull requests, summarising documents, querying a database,
writing release notes, formatting reports, processing PDFs, and answering
questions about your internal API. Each task has its own rules, its own
workflow, and its own specialist knowledge.
So you do what every developer does the first time: you put it all in the
system prompt.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 1/40


---
*Page 2*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
It starts small. A few hundred tokens. Manageable. Then you add the code
review guidelines. Then the document formatting rules. Then the database
schema. Then the API reference. Before you know it, your system prompt is
12,000 tokens long and growing. You run a test. The agent is slower. It’s more
expensive. It confidently ignores the formatting rules you spent an hour
writing because they’re buried 9,000 tokens deep and the model has quietly
stopped paying attention to anything past the halfway mark.
Google Agent Skills Explained
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 2/40


---
*Page 3*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
The agent that was supposed to be a sharp specialist has become an
overwhelmed generalist, technically capable of everything, reliably good at
nothing.
This is the context window problem, and it is the single most
underestimated bottleneck in production AI agent development. It’s not a
hardware limitation you can throw money at. It’s a fundamental tension: the
more you teach your agent, the worse it performs, because you’re teaching it
everything at once, whether it needs it right now or not.
Here’s the question that changes everything: what if your agent could have
access to hundreds of specialised capabilities but only ever load the one it
needs, at the exact moment it needs it?
Load the code review instructions when someone asks for a code review.
Load the PDF processing workflow when someone uploads a PDF. Load
nothing, absolutely nothing, when none of it is relevant. Keep the always-on
context razor-thin. Pull in-depth on demand.
That is the idea behind Agent Skills, and it’s not just a Google feature or an
ADK trick. It’s an emerging open standard, published at agentskills.io, that
is quietly beginning to change how serious agent developers think about
knowledge management.
By the end of this blog, you’ll understand exactly how it works, why the
architecture matters, and how to write your first skill from scratch. If you
read Blog 1 in this series and built your first ADK agent, this is the concept
that takes you from “I can build agents” to “I can build agents that scale.”
Let’s get into it.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 3/40


---
*Page 4*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Google ADK In-Depth Series of Learning Agentic AI
1. Google ADK in 2026: The Complete Beginner’s Guide to Building AI
Agents | Part-1
2. Your First Google ADK Agent with Skills: Build a Weather and News Agent
in 30 Minutes | Part-2
3. Mastering ADK Tools: Function Tools, MCP Tools, OpenAPI Tools &
When to Use Each | Part-3
4. ADK Skill Tool That Write Skills: Building Self-Extending AI Agents with
Google ADK | Part-4
5. Google Agent Skills Explained: The Open Standard Changing How AI
Agents Work | Part-5
6. ADK Memory, Sessions & State: Building Agents That Remember | Part-6
7. Multi-Agent Systems with ADK: Build Your Own AI Research Team | Part-7
8. Gemini CLI + Agent Skills: Supercharge Your Developer Workflow | Part-8
9. Firebase + Agent Skills: Add AI Superpowers to Your Firebase App | Part-9
10. Grounding ADK Agents: Google Search, Vertex AI Search & RAG Patterns |
Part-10
11. ADK + MCP: Connecting Your Agent to Any Tool in the World | Part-11
12. Build a Full-Stack AI SaaS App with Google ADK: From Idea to Live
Product | Part-12
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 4/40


---
*Page 5*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
What Are Agent Skills?
An agent skill is a lightweight, open format for extending AI agent
capabilities with specialised knowledge and workflows. At its core, a skill is
a folder containing a SKILL.md file with metadata and instructions that tell an
agent how to perform a specific task. Skills can also bundle scripts,
templates, and reference materials. That folder, that file, and that simple
structure are all it takes to give an agent a new capability it can reach for
intelligently, on demand, without bloating its always-on context.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 5/40


---
*Page 6*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
ADK Agent Skills
If that definition still feels abstract, here are three concrete statements that
make it tangible:
First: a skill is a folder. Not a class. Not a function. Not a config file, a plugin,
or a package. A folder on your filesystem, with a specific internal structure.
If you can create a folder and write a Markdown file, you can build a skill.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 6/40


---
*Page 7*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Second: the centrepiece of that folder is a SKILL.md file. It is a standard
Markdown file with a YAML frontmatter block at the top, followed by the
skill's instructions in the body. If you have ever written a Jekyll blog post, a
Hugo page, or a GitHub README with front matter, you already know the
format. The learning curve is measured in minutes, not hours.
Third: Skills give agents just-in-time specialist knowledge. The key word is
'just-in-time'. A skill's instructions are loaded into the agent’s context only
when the current task matches the skill’s description, and they are absent
from context when they are not needed. The agent is never carrying
knowledge it is not currently using.
That third point is what separates Skills from everything that came before. It
is not just a new file format. It is a fundamentally different approach to how
agents hold and access knowledge.
The mental model that makes this click: Think of Skills as the difference
between a doctor who has memorised every medical textbook (bloated
context, slowing down every consultation) and a doctor who knows exactly
which textbook to pull off the shelf for each patient (progressive disclosure,
sharp and efficient every time). The knowledge is the same. The architecture
is completely different. One scales. The other does not.
Why This is a Big Deal: The Progressive Disclosure Principle
To understand why Agent Skills matter architecturally, you need to borrow a
concept from UX design.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 7/40


---
*Page 8*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Progressive Disclosure Principle
Progressive disclosure is a design principle that says, 'Show users only what
they need at the moment they need it, rather than presenting every possible
option at once.' Good software interfaces use it constantly. A settings panel
that hides advanced options behind an “Advanced” toggle. A form that
reveals the next field only after the current one is filled. A menu that shows
submenus only when you hover over a parent item. The full capability is
always there. It just does not arrive all at once.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 8/40


---
*Page 9*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Agent skills apply this exact principle to LLM context windows.
Instead of loading every capability your agent has into context on every
single turn, skills structure that knowledge into three disclosure levels, each
loaded at a different moment:
Stage 1: Discovery. At startup, agents load only the name and description of
each available skill. Just enough to know when a skill might be relevant.
Nothing more.
Stage 2: Activation. When a task matches a skill’s description, the agent reads
the full SKILL.md instructions in context.
Stage 3: Execution. The agent follows the instructions, optionally loading
referenced files or executing bundled scripts as needed.
Each stage loads more context. Each stage is only reached when the task
genuinely requires it.
Now let’s make that concrete with real token numbers from the official
specification:
Level 1 (Metadata): The name fields are loaded at startup for all skills, costing
approximately 100 tokens per skill.
Level 2 (Instructions): The full SKILL.md body is loaded when the skill is
activated. The specification recommends keeping this under 5,000 tokens.
Level 3 (Resources): Files are in scripts/, references/, or assets/ are
loaded only when required during execution.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 9/40


---
*Page 10*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Here is what that looks like visually across an agent with 20 skills:
ALWAYS IN CONTEXT (every turn, all 20 skills):
┌─────────────────────────────────────────────────────┐
│ Skill 1 metadata ████ ~100 tokens │
│ Skill 2 metadata ████ ~100 tokens │
│ Skill 3 metadata ████ ~100 tokens │
│ ... ████ ~100 tokens │
│ Skill 20 metadata ████ ~100 tokens │
│ TOTAL: ~2,000 tokens │
└─────────────────────────────────────────────────────┘
ONLY WHEN ONE SKILL IS ACTIVATED:
┌─────────────────────────────────────────────────────┐
│ Full SKILL.md body ████████████████ ~2,000 tokens │
└─────────────────────────────────────────────────────┘
ONLY WHEN THAT SKILL EXPLICITLY NEEDS THEM:
┌─────────────────────────────────────────────────────┐
│ Reference file ████████████████████ ~1,000 tokens│
│ Script ██████ ~500 tokens │
└─────────────────────────────────────────────────────┘
Total context cost for an agent with 20 skills, on a turn where one skill is
active and needs one reference file: roughly 5,500 tokens.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 10/40


---
*Page 11*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Progressive Disclosure
Now contrast that with the naive approach. Twenty capabilities, all fully
spelt out in the system prompt. Each one averaging 2,000 tokens of detailed
instructions. That is 40,000 tokens loaded on every single turn — regardless
of which capability the agent actually needs. On a turn where the user asks a
simple question that requires zero specialist knowledge, you are still paying
for all 40,000 tokens. Every time. All day.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 11/40


---
*Page 12*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
The difference is not small.
Naive system prompt (20 capabilities):
████████████████████████████████████████ ~40,000 tokens
every single turn
Progressive Disclosure (20 skills):
████ ~2,000 tokens baseline
████████████████ +~3,500 tokens when activated
~5,500 tokens maximum
The architectural insight worth writing down: With Progressive Disclosure,
20 skills cost roughly the same context as a single fully-loaded skill. That is
not a marginal efficiency gain. That is a completely different approach to
how agents hold knowledge. One approach hits a ceiling. The other scales
horizontally as far as you need it to.
This is why skills are not just a convenience feature. They are the
architectural foundation that makes capable, multi-domain agents viable in
production without the cost and performance penalties that kill most agent
projects before they ship.
The Open Standard: Why It Matters Beyond ADK
agentskills.io
Here is the detail that most ADK tutorials skip entirely, and it is the one that
changes how you should think about investing time in skills.
Agent Skills are not a Google product feature. They are not locked to ADK.
They are not going to be deprecated the next time Google rebrands a
developer tool.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 12/40


---
*Page 13*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Agent skills are defined by an open specification published at
agentskills.io. The spec is implementation-agnostic, meaning any agent
framework, any company, and any developer can adopt it, build for it, and
publish. Skills that work across every compatible runtime. Google
contributed the standard. Google does not own it.
This matters because of what it means in practice.
A skill you write today for your ADK agent will work in Gemini CLI without
modification. A skill someone publishes to a public GitHub repository can
be installed into your agent with a single terminal command. The
community repository github.com/google-gemini/gemini-skills already
contains skills you can pull directly into your own projects. The gemini-api-
dev skill, which encodes best practices for building Gemini-powered
applications, installs globally in one line:
npx skills add google-gemini/gemini-skills --skill gemini-api-dev --global
One command. Someone else wrote the specialist knowledge. Your agent
now has it.
That is the network effect of an open standard. The Skills ecosystem grows
every time any developer anywhere publishes a skill to a public repository,
and every compatible agent runtime benefits immediately.
The parallel to existing standards developers already trust is exact. Skills are
to AI agents what OpenAPI specs are to REST APIs: a shared, framework-
agnostic format that makes the ecosystem interoperable rather than a
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 13/40


---
*Page 14*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
collection of incompatible silos. Or think of it like package.json for Node.js.
The format is not the product. The format is what makes the product
ecosystem possible.
Without a shared standard, every agent framework invents its own
knowledge format. Skills written for LangChain do not work in CrewAI.
Prompts tuned for AutoGen do not transfer to ADK. Every team reinvents the
same patterns in isolation, and none of the work compounds.
With a shared standard, a skills library published by a fintech company can
be used by a healthcare startup. A developer workflow skill written by an
open-source contributor can be installed by an enterprise team. The
knowledge compounds across the entire ecosystem rather than being
trapped inside a single framework’s walled garden.
Why this changes your calculus as a developer: Every Skill you write
carefully and publish is a contribution to an ecosystem, not just a local
configuration file. And every Skill the ecosystem produces is available to
your agents. The open standard is what makes Skills an investment rather
than just a feature.
The Complete Skill Structure: L1/L2/L3 Deep Dive
This is the section to bookmark. Everything you need to understand the full
Agent Skills specification, with real annotated examples you can copy as
templates.
A Skill has one required file and three optional directories. Here is the
complete picture:
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 14/40


---
*Page 15*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
my-skill/ ← The folder name must match the skill name exactly
├── SKILL.md ← Required. Frontmatter = L1 metadata.
│ Body = L2 instructions.
├── scripts/ ← L3: Executable code the agent can run
│ └── process_data.py
├── references/ ← L3: Documentation loaded on demand
│ ├── REFERENCE.md
│ └── API_GUIDE.md
└── assets/ ← L3: Templates, schemas, static resources
└── report_template.md
 
Three layers. One required file. Let’s go through each one.
The L1 Layer: Metadata (Frontmatter)
The frontmatter block sits at the very top of SKILL.md, wrapped in triple-dash
fences. It is what the agent reads at startup for every skill, every turn,
regardless of whether the skill is ever activated. This is your most expensive
real estate in terms of always-on context cost, so every character counts.
Here is a fully annotated frontmatter block with every available field:
---
name: pdf-processing # Required. Max 64 characters.
# Lowercase letters, numbers, and hyphens only.
# Must match the parent folder name exactly.
# Valid: pdf-processing
# Invalid: PDF-Processing, pdf_processing
description: > # Required. Max 1024 characters.
Extract text and tables # This is what the agent reads to decide
from PDF files, fill PDF # whether to activate. Write it as
forms, and merge documents. # "Use this skill when..." - imperative voice.
Use when the user needs # Include specific keywords. Name the task
to work with PDF files. # even if the user might not.
license: Apache-2.0 # Optional. License name or path to LICENSE file.
compatibility: > # Optional. Only include if your skill has
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 15/40


---
*Page 16*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Requires pdfplumber and # specific environment requirements.
pdfminer. Python 3.10+. # Most skills do not need this field.
metadata: # Optional. Arbitrary key-value pairs.
author: your-org # Use for versioning, authorship, internal tags.
version: "1.0"
allowed-tools: Bash Read # Optional (Experimental).
# Space-delimited list of pre-approved tools.
# Support varies by agent implementation.
---
The single most important field in that entire block is description. The
description carries the entire burden of triggering. If it does not convey when
the skill is useful, the agent will not know to reach for it. Google
This is worth stopping on. The agent never reads your SKILL.md body until
after it has already decided to activate the skill. The only information it uses
to make that decision is the name and description. If your description is
vague, the skill simply does not activate, no matter how good the instructions
inside are.
 
Here is the difference between a description that works and one that does
not, taken directly from the specification:
# Bad: vague, no keywords, no "when to use" signal.
# The agent has no idea when this is relevant.
description: Helps with PDFs.
# Good: specific capabilities, explicit trigger conditions,
# covers cases where the user does not say "PDF" directly.
description: >
Extracts text and tables from PDF files, fills PDF forms,
and merges multiple PDFs. Use when working with PDF documents
or when the user mentions PDFs, forms, or document extraction,
even if they do not use the word 'PDF' explicitly.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 16/40


---
*Page 17*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
The improved version does three things the weak version does not. It lists
specific capabilities so the agent knows exactly what this skill can do. It
includes an explicit “Use when” trigger. And it covers the case where the user
describes the need without naming the technology, which is how real users
actually talk.
Write every description as if you are leaving instructions for a new colleague
who needs to know exactly when to pull this skill off the shelf and exactly
when to leave it there.
The L2 Layer: Instructions (Markdown Body)
The body of SKILL.md, everything below the closing --- of the frontmatter, is
the L2 layer. This is what gets loaded into context when the skill activates. It
is your skill's actual instructions.
The Markdown body contains the skill instructions and has no format
restrictions. Write whatever helps agents perform the task effectively.
Recommended sections include step-by-step instructions, examples of
inputs and outputs, and common edge cases.
Here is a real L2 body for the pdf-processing skill, with design annotations:
# PDF Processing
## When to use this skill
Use when the user needs to extract text, fill forms, or merge PDFs.
Include this section as an explicit confirmation - it helps the agent
verify it activated the right skill before proceeding.
## Step-by-step: Extracting text
1. Import pdfplumber - see references/REFERENCE.md for the full API
2. Open the file: `with pdfplumber.open(path) as pdf:`
3. Iterate page by page: `for page in pdf.pages:`
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 17/40


---
*Page 18*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
4. Extract text: `text = page.extract_text()`
## Step-by-step: Filling forms
See references/FORMS.md for the complete field mapping guide.
## Common edge cases
- Scanned PDFs with no text layer: warn the user and suggest OCR tools
- Password-protected files: ask for the password before attempting to open
- Files larger than 50MB: process in chunks to avoid memory issues
Notice the design pattern at work. The step-by-step instructions for
extracting text are short enough to live in the body. The complete API
reference for pdfplumber is long, detailed, and only needed mid-task, so it
lives in references/REFERENCE.md and is linked by relative path. The form
field mapping guide is similarly deferred. Keep the main SKILL.md under 500
lines and move detailed reference material to separate files. Google
The L2 body is the briefing. Not the encyclopedia.
The L3 Layer: Resources (Optional Directories)
The three optional directories are where your skill stores everything too
detailed, too long, or too specialised to live in SKILL.md directly. Each is
loaded only when the agent explicitly needs it during execution.
references/ contains additional documentation that agents read when
needed: detailed technical references, form templates, or domain-specific
files. Keep individual reference files focused. Agents load these on demand,
so smaller files mean less context usage per load.
scripts/ contains executable code that agents can run. Scripts should be
self-contained, include helpful error messages, and handle edge cases
gracefully.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 18/40


---
*Page 19*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
assets/ contains static resources: templates, images, data files, lookup
tables, and schemas.
When your SKILL.md body needs to reference these files, use relative paths
from the skill root:
For the complete API reference, see [references/REFERENCE.md](references/REFERENCE.m
To extract text from a PDF, run the extraction script:
scripts/extract.py
 
The agent reads those references and knows to load the linked file when it
reaches that step. Progressive Disclosure operating at the file level, inside a
single skill.
A Real Skill Walkthrough: Annotated End to End
Now let’s put every layer together in a complete, realistic skill you can use as
a template for your own projects.
We are going to build a code-review skill. Every developer can relate to it
immediately, and the design decisions it requires illustrate every concept
from the specification in a way that a toy example cannot.
The folder structure:
code-review/
├── SKILL.md
├── references/
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 19/40


---
*Page 20*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
│ ├── CHECKLIST.md
│ └── STYLE_GUIDE.md
└── assets/
└── review_template.md
The complete SKILL.md:
---
name: code-review
description: >
Perform thorough, structured code reviews on any language or
framework. Use this skill when asked to review code, check a
pull request, audit a function, or give feedback on implementation
quality. Use even if the user says "take a look at this" or
"what do you think of this code" rather than "review this code."
license: Apache-2.0
metadata:
author: your-github-username
version: "1.0"
---
# Code Review
## Your role
You are a senior engineer performing a structured code review.
Be specific, constructive, and direct. Prioritise correctness
and security over style. Every comment should be actionable.
## Review process
1. **Read the full diff or file** before commenting on any part of it
2. **Open references/CHECKLIST.md** for the complete review criteria
3. **Categorise every comment** as one of: [Critical] [Suggestion] [Nit]
4. **Use assets/review_template.md** to structure your final output
## Critical checks (run these on every review, no exceptions)
- [ ] No hardcoded secrets, API keys, or credentials
- [ ] No SQL queries built via string concatenation
- [ ] Error handling is present and meaningful, not just `except: pass`
- [ ] No obvious N+1 query patterns in database-touching code
## Output format
Structure your review using assets/review_template.md.
End every review with a summary verdict on its own line:
Approve / Request Changes / Needs Discussion
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 20/40


---
*Page 21*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Now let’s walk through every design decision in that file, because each one
was deliberate.
The description covers informal trigger language. The phrase “even if the
user says ‘take a look at this’” is not padding. Real user prompts contain
context that generic test queries lack. Google Users rarely say “please
perform a structured code review.” They say “can you look at this function”
or “what do you think of this PR.” The description covers those phrasings
explicitly so the skill activates reliably on real usage, not just ideally-phrased
requests.
The critical checks live in the L2 body. They are short, always relevant to
every review, and need to be in context from the moment the skill activates.
There is no reason to defer them to a reference file.
The full checklist lives in references/CHECKLIST.md. A complete code review
checklist might run to 80 items covering security, performance, naming,
documentation, test coverage, and framework-specific patterns. That is too
long for the body and only needed once the review is underway. Progressive
Disclosure at the file level: load it when the agent reaches Step 2 of the
review process, not before.
The style guide lives in references/STYLE_GUIDE.md. Style is the lowest-priority
concern in a code review. Loading it on every activation would waste context
that is better spent on the instructions the agent needs first.
The output template lives in assets/. It is a static resource, not an
instruction. It does not tell the agent how to think. It tells the agent how to
format what it already decided to write. That distinction is what separates
assets/ from references/.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 21/40


---
*Page 22*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
The discipline that makes Skills work: Notice what is not in SKILL.md. There
is no 200-line style guide. No complete API reference. No history of linting
rule changes. No exhaustive taxonomy of code smells. All of that lives in
references/, loaded only when the agent needs it. Your SKILL.md stays lean
because lean is fast, lean is cheap, and lean means the agent actually reads
everything you wrote.
Skills vs. Everything Else: Know Which Tool to Reach For
Skills do not replace the other mechanisms in your agent toolkit. They sit
alongside them, each with a specific job. The mistake most developers make
when they first encounter Skills is trying to figure out whether to use them
instead of something they already know. The right question is not “instead of”
but “in addition to, and when.”
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 22/40


---
*Page 23*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Skills vs. Everything
Here is exactly how each mechanism differs, written as a comparison you
can internalise and apply:
The System Prompt is static text that lives inside your Agent() definition and
is loaded into context on every single turn, every single time, without
exception. It costs 100% of its token weight on every interaction whether it is
relevant or not. It cannot include executable code. It cannot include
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 23/40


---
*Page 24*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
reference documentation without wasting expensive always-on context. It
has no open standard and does not transfer between frameworks. It is best
used for things that are permanently true about your agent: its name, its
tone, its hard rules, its non-negotiable constraints. If a piece of knowledge
applies to every conversation your agent will ever have, the system prompt is
the right home for it. If it applies to only some conversations, putting it in
the system prompt is waste.
A Function Tool is a Python function in your agent.py that the agent can call
to take a deterministic, programmatic action. Its context cost is minimal:
ADK only loads the schema (roughly 50 tokens per tool) until the tool is
called. The function itself is not a language model instruction; it is
executable code that does exactly what you write, every time, predictably.
Function tools are the right choice when you need to call an external API,
run a calculation, write to a database, send an email, or perform any action
where correctness and predictability matter more than flexibility. They
cannot carry reference documentation or multi-step instructional
workflows. They are hands, not knowledge.
An MCP Server is an external service running as a separate process that
exposes tools to agents via the Model Context Protocol, an open standard for
agent-to-tool communication. Like function tools, MCP servers appear in
agent context only as schemas until their tools are called. Unlike function
tools, MCP servers are persistent external integrations designed to be shared
across multiple agents and multiple applications simultaneously. They are
the right choice for integrations that need to live outside your agent’s
codebase entirely: a GitHub integration used by five different agents, a Slack
connector shared across a team’s tooling, a database layer consumed by both
an internal agent and a customer-facing one. MCP servers are interoperable
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 24/40


---
*Page 25*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
across frameworks and can include executable logic, but they are not
designed to carry instructional knowledge or domain workflows.
An Agent Skill is a folder containing a SKILL.md file with metadata,
instructions, and optional resources. Its always-on context cost is
Open in app
approximately 100 tokens per skill for the metadata layer, regardless of how
many skills are available.S eTahrceh full instructions only load when Wthritee skill
activates. Reference files load only when the agent needs them during
execution. Skills can carry executable scripts, reference documentation,
templates, and schemas alongside their instructions. They are defined by an
open standard at agentskills.io and are reusable across any compatible
framework. They are the right choice when you have specialist knowledge, a
multi-step domain workflow, or instructional context that only applies to
some tasks and should not occupy always-on context when it is not needed.
The decision in plain language, one rule per mechanism:
Use a system prompt for everything that is permanently true about your
agent regardless of what it is doing. Use a function tool when you need a
deterministic programmatic action that executes the same way every time.
Use an MCP server when you need a persistent external integration that
multiple agents or applications share. Use a Skill when you have domain
knowledge or a multi-step workflow that applies to some tasks but not all,
and you want it loaded efficiently only when it is relevant.
Four mechanisms. Four distinct jobs. None of them replaces the others.
The production stack that scales: A lean system prompt that carries only
permanent agent identity. Focused function tools for every deterministic
action. Skills for every domain and workflow that is task-specific rather than
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 25/40


---
*Page 26*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
always-on. Each layer doing exactly one job, costing exactly what it needs to
cost, and nothing more. This is the architecture that lets an agent handle
twenty domains without the context bill of a twenty-domain system prompt.
How ADK Loads Skills in Code
If you built the weather agent in Blog 1, you are three lines of code away
from adding your first Skill to it. This section is a preview of the mechanics.
Blog 3 covers both methods in full depth with a complete working project.
For now, here is enough to understand exactly how Skills slot into the ADK
agent you already know.
ADK gives you two ways to load Skills into an agent. The right choice
depends on whether your Skill lives on the filesystem or needs to be
constructed programmatically at runtime.
Method 1: File-based loading (the standard approach)
This is the method you will use for the vast majority of Skills. Your Skill
folder follows the agentskills.io spec, lives on disk, and is loaded by
pointing ADK at the directory:
import pathlib
from google.adk import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset
# Point ADK at your skill folder - it reads SKILL.md and all resources
code_review_skill = load_skill_from_dir(
pathlib.Path(__file__).parent / "skills" / "code-review"
)
# Wrap one or more skills in a SkillToolset
my_toolset = skill_toolset.SkillToolset(
skills=[code_review_skill] # pass a list - you can include multiple skills
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 26/40


---
*Page 27*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
)
root_agent = Agent(
model="gemini-2.0-flash",
name="dev_assistant",
instruction="You are a helpful software engineering assistant.",
tools=[my_toolset], # Skills drop in exactly like any other tool
)
Three things worth noting in that code. First, load_skill_from_dir takes a
pathlib.Path — use pathlib.Path(__file__).parent to build paths relative to
your agent.py file rather than relying on the working directory. Second,
SkillToolset accepts a list, so you can pass ten Skills in a single toolset.
Third, the toolset goes into the tools list exactly the same way a function
tool does — from ADK's perspective, a SkillToolset is just another tool, which
means everything you already know about the tools parameter applies.
 
Method 2: Inline definition (for dynamic or programmatic skills)
When you need to construct a Skill in Python rather than from a file —
because you are generating instructions dynamically, reading them from a
database, or building a system that creates Skills at runtime — ADK exposes
the models.Skill class for inline definition:
from google.adk.skills import models
# Build a skill entirely in Python, no files required
greeting_skill = models.Skill(
frontmatter=models.Frontmatter(
name="greeting-skill",
description=(
"Greets the user warmly by name. "
"Use when the conversation is just starting."
),
),
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 27/40


---
*Page 28*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
instructions=(
"Always address the user by name if you know it. "
"Be warm, brief, and genuine. Do not use generic openers."
),
)
```
The `Frontmatter` object maps directly to the YAML frontmatter you learned in Sectio
> 💡 **Which method to use:** File-based Skills are the right default for almost eve
Blog 3 puts both methods to work in a complete project. You will build two Skills fr
---
## Your First Skill: A 5-Minute Quick Start
Enough theory. Here is something you can build right now, today, using the `weather_
The challenge: add a Skill to your existing agent in under 5 minutes, without touchi
The Skill we are building is `city-facts` - a specialist knowledge package that give
**Step 1: Create the Skills folder structure**
Inside your existing `weather_time_agent` project, create two new folders:
```
weather_time_agent/
├── __init__.py
├── agent.py
├── .env
└── skills/
└── city-facts/
└── SKILL.md ← this is the only file you need to create
Step 2: Write the SKILL.md
Create SKILL.md inside city-facts/ and paste in the following:
---
name: city-facts
 
description: >
Provides interesting facts, local tips, hidden gems, and
neighbourhood knowledge about major cities. Use when the user
asks about a city beyond weather and time — including local
culture, food recommendations, things to do, history, or
travel tips. Use even if the user just asks "what else can
you tell me about New York?"
---
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 28/40


---
*Page 29*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
# City Facts
## New York City
- Best pizza: Di Fara in Brooklyn - cash only, arrive before noon
- Hidden gem: The High Line on a Tuesday morning before 9am
- Local tip: The subway is always faster than a cab below 96th Street
- Neighbourhood to explore: Astoria, Queens for the best food per dollar
## London
- Best pub: The Prospect of Whitby in Wapping, oldest riverside pub in the city
- Hidden gem: Postman's Park near St Paul's, a Victorian memorial garden
almost nobody knows about
- Local tip: Tap your contactless card on the yellow reader, not the green one
- Neighbourhood to explore: Maltby Street Market on a Saturday morning
This Skill took five minutes to write. It contains zero Python. It will never be
loaded unless someone asks about city culture, food, or local tips — at which
point the full content drops into context precisely when it is needed, and
disappears when it is not.
Step 3: Connect it to your agent
Open agent.py and add four lines. The first two are new imports at the top,
the third loads the Skill, and the fourth passes it to the agent:
import pathlib
from google.adk import Agent
from google.adk.skills import load_skill_from_dir # new
from google.adk.tools import skill_toolset # new
city_facts_skill = load_skill_from_dir( # new
pathlib.Path(__file__).parent / "skills" / "city-facts"
)
root_agent = Agent(
model="gemini-2.0-flash",
name="weather_time_agent",
instruction="You are a helpful assistant for city information.",
tools=[
get_weather,
get_current_time,
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 29/40


---
*Page 30*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
skill_toolset.SkillToolset(skills=[city_facts_skill]), # new
],
)
Step 4: Test it
Run adk web from the parent folder and try this prompt:
“What should I do in New York beyond just checking the weather?”
Your agent now has specialist local knowledge it did not have five minutes
ago. Open the Events tab in adk web and you will see the city-facts skill
activate in the event stream, the SKILL.md content load into context, and the
agent use it to answer. Then ask about the weather, and notice the Skill is
absent from the event stream entirely. It loaded when it was needed and cost
nothing when it was not.
That is Progressive Disclosure working exactly as designed, in your own
project, on your own machine.
The principle this quick start demonstrates: Domain knowledge does not
have to be code. The most underused capability in agent development is
plain Markdown. A well-written SKILL.md can give an agent capabilities that
would take hours to implement as function tools, with zero Python, in
minutes. Start with a Skill. Reach for code only when deterministic
execution is genuinely required.
Production Tips: Writing Skills That Actually Work
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 30/40


---
*Page 31*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
The quick start in the previous section gets you to a working Skill in five
minutes. These five tips are what get you to a Skill that works reliably in
production, on real user queries, across thousands of conversations. This is
the section senior developers bookmark and share with their teams.
Tip 1: Write descriptions as trigger instructions, not feature lists.
The most common mistake in Skill authoring is writing the description as a
summary of what the Skill does rather than as an instruction to the agent
about when to use it. Frame the description as an instruction to the agent:
“Use this skill when…” rather than “This skill does…” The agent is deciding
whether to act, so tell it when to act. A description that reads “Use this skill
when the user asks about PDFs, forms, or document extraction, even if they
do not say PDF explicitly” will activate on the queries you need it to. A
description that reads “PDF processing skill” will not activate reliably on
anything, because it gives the agent no signal about when reaching for this
Skill is the right decision. Every description you write should answer one
question from the agent’s perspective: when is it my job to use this?
Tip 2: Keep SKILL.md under 500 lines.
Move detailed reference material to separate files in references/. The
SKILL.md body is the briefing your agent reads the moment a Skill activates.
It is not the place for a complete API reference, an exhaustive taxonomy of
edge cases, or a historical record of every decision made while building the
Skill. If your instructions are running longer than a single page, you are
loading too much context on every activation and almost certainly burying
the instructions the agent needs most under material it does not need yet.
Split aggressively. Put the overview in the body. Put the depth in references/.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 31/40


---
*Page 32*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
The agent will load the references when it needs them and leave them alone
when it does not.
Tip 3: Test your description triggers deliberately.
A description that triggers correctly on your hand-crafted test query may fail
on the phrasing a real user actually sends. Model behaviour is
nondeterministic — the same query might trigger the skill on one run but not
the next. Run each test query multiple times and compute a trigger rate: the
fraction of runs where the skill was invoked. A trigger rate above 0.5 on
should-trigger queries is a reasonable passing bar. Build a small set of 15 to
20 test queries, split evenly between queries that should trigger your Skill
and queries that should not, and run each one at least three times before you
consider the description production-ready. The skill-creator tool in the
Gemini CLI automates this entire evaluation loop if you want a faster
iteration cycle.
Tip 4: Use near-miss negative test cases.
Weak negative tests are useless. Testing that your PDF skill does not trigger
on “write me a haiku” tells you nothing. The most valuable negative test
cases are near-misses: queries that share keywords or concepts with your
skill but actually need something different. For a data analysis Skill, the
telling negative test is not “tell me a joke” but “write a Python script that
reads a CSV and uploads each row to our database.” That query mentions
CSV, which is a keyword in your description, but the task is ETL pipeline
work, not data analysis. If your description is too broad, it will false-trigger
on that query and load unnecessary context. Writing near-miss negatives
forces you to sharpen the boundaries of your description until it is precise
about both what the Skill does and what it deliberately does not do.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 32/40


---
*Page 33*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Tip 5: Refine through real use, not upfront design.
No Skill is production-ready on the first draft, and trying to make it perfect
before shipping it wastes time that real usage would spend more efficiently.
Skills are rarely perfect on the first try. An effective way to refine them is
through real usage — when you notice the agent struggling with a step or
fetching the wrong context, update the skill. medium Version your Skills in
Git from the first commit, treat the description field with the same care you
give to production code, and build a habit of updating the Skill the moment
you notice it behaving unexpectedly rather than leaving a mental note to fix
it later. The description and the instructions are both live artifacts. They have
bugs. They need patches. The developers who build the best Skills are the
ones who treat them as software, not as configuration.
Resources and Further Reading
Everything referenced in this blog, ready to open:
📘
Agent Skills Specification — the complete format reference for every
field, every directory, and every constraint: agentskills.io/specification
📘
What Are Skills? — the official introduction to the Progressive
Disclosure model and the SKILL.md format: agentskills.io/what-are-skills
🐍
ADK Skills Docs — how SkillToolset, load_skill_from_dir, and inline
Skills work inside ADK: google.github.io/adk-docs/skills
🌐
Gemini Skills Repository — community Skills you can install with npx
skills add, including gemini-api-dev: github.com/google-gemini/gemini-
skills
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 33/40


---
*Page 34*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
📖
Optimising Skill Descriptions — the systematic approach to testing
and improving trigger accuracy: agentskills.io/skill-creation/optimizing-
descriptions
If this guide helped you…
If you learned something new or found this breakdown useful:
Drop a comment — share which metrics you’ve found most reliable in your
projects.
Clap (or double-clap!) to help more AI builders discover this guide.
Share it with your teammates or community, every conversation brings us
closer to better, fairer AI evaluation.
GenAI Full Roadmap [ Learning LLM — RAG -Agentic AI with Resources] :
https://youtu.be/4yZ7mp6cIIg
👨‍💻
Agentic AI 14+ Projects- https://www.youtube.com/playlist?
list=PLYIE4hvbWhsAkn8VzMWbMOxetpaGp-p4k
👨‍💻
Learn RAG from Scratch — https://www.youtube.com/playlist?
list=PLYIE4hvbWhsAKSZVAn5oX1k0oGQ6Mnf1d
👨‍💻
Complete Source Code of all 75 Day Hard
🌀
GitHub —
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 34/40


---
*Page 35*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
https://github.com/simranjeet97/75DayHard_GenAI_LLM_Challenge
🔀
Kaggle Notebook — https://www.kaggle.com/simranjeetsingh1430
👨‍💻
Exclusive End to End Projects on GenAI or Deep Learning or Machine
Learning in a Domain Specific way —
https://www.youtube.com/@freebirdscrew2023
If you like the article and would like to support me make sure to:
👏 👉🏻
Clap for the story (100 Claps) and follow me Simranjeet Singh
📑
View more content on my Medium Profile
🔔
Follow Me: Medium | GitHub | Linkedin | Community
🚀
Help me in reaching to a wider audience by sharing my content with
your friends and colleagues.
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 35/40


---
*Page 36*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
What do you choose?
Agent Skills Agentic Ai AI Agent Artificial Intelligence Technology
Written by Simranjeet Singh
Following
3.6K followers · 40 following
AI/ML Engineer l | GenAI Expert | Finance and Banking | 3K Medium + 14K
YouTube | Machine Learning | Deep Learning | NLP
No responses yet
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 36/40


---
*Page 37*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Rae Steele
What are your thoughts?
More from Simranjeet Singh
Simranjeet Singh Simranjeet Singh
Google ADK in 2026: The Complete Mastering ADK Tools: Function
Beginner’s Guide to Building AI… Tools, MCP Tools, OpenAPI Tools …
The way we build software is changing and You’ve built an agent. Now what?
most developers haven’t noticed yet.
6d ago 33 2d ago 56
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 37/40


---
*Page 38*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
InArtificial Intelligence in Plain … by Simranjeet Si… InArtificial Intelligence in Plain … by Simranjeet Si…
Your First Google ADK Agent with ADK Skill Tool That Write Skills:
Skills: Build a Weather and News… Building Self-Extending AI Agent…
I’ve read three tutorials. Installed five Most developers build AI agents the same
frameworks. Watched two YouTube videos… way they assemble IKEA furniture.
3d ago 34 1d ago 50
See all from Simranjeet Singh
Recommended from Medium
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 38/40


---
*Page 39*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Yusuf Baykaloğlu Vishal Mysore
Multi-Agent Systems: What Is PageIndex? How to Build a
Orchestrating AI Agents with A2… Vectorless RAG System (No…
A Deep Dive into Agent Architecture, PageIndex is a vectorless, reasoning-based
Workflows, and Real-World Implementation Retrieval-Augmented Generation (RAG)…
Jan 12 261 1 Mar 1 133 5
InData And Beyond by TONI RAMCHANDANI Bibek Poudel
Claude Cowork: The complete The SKILL.md Pattern: How to
guide to Anthropic’s AI desktop… Write AI Agent Skills That Actuall…
How the “digital coworker” model changes If your skill does not trigger, it is almost never
daily work plus where it still breaks. the instructions. It is the description.
Feb 12 687 4 Feb 25 66 1
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 39/40


---
*Page 40*


3/23/26, 11:54 AM Google Agent Skills Explained: The Open Standard Changing How AI Agents Work | Part-5 | by Simranjeet Singh | Mar, 2026 | Med…
Dewasheesh Rana E. Huizenga
🔥
The Ultimate Guide to AI I Interviewed Hundreds of AI
Observability in Production Engineers at Google. Here’s Why…
OpenTelemetry, Prometheus, Tempo, Grafana I spent 8.5 years at Google.
— and When to Use Langfuse & LangSmith
Feb 21 3 1 Feb 10 166 3
See more recommendations
https://medium.com/@simranjeetsingh1497/google-agent-skills-explained-the-open-standard-changing-how-ai-agents-work-part-5-0004b031a2b3 40/40