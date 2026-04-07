# 3LayerHarness

*Converted from: 3LayerHarness.PDF*



---
*Page 1*


Open in app
Search Write
Chaotic AI-generated code on the left versus clean organized harness
engineering architecture on the right, illustrating the contrast between
uncontrolled AI code generation and structured harness engineering
Member-only story
Beyond the AI Coding
Hangover: How
Harness Engineering


---
*Page 2*


Prevents the Next
Outage
Navigating the Challenges of AI Code
Generation: Implementing Harness
Engineering to Ensure Reliability and Safety
Rick Hightower Following 23 min read · 3 days ago
43
Is your AI coding tool a double-edged sword? Discover
how the latest engineering strategies can prevent
outages and safeguard your projects from the chaos of
unchecked AI-generated code. Don’t let the AI coding
hangover catch you off guard! Read more to learn how
to build a robust harness for your software
development.
It’s 2am. Your phone starts screaming. You grab it,
see the ops alert, and your stomach drops. The
post-mortem will say “erroneous software code
deployment,” but you already know the real story:


---
*Page 3*


an AI agent did something nobody tested, nobody
caught, and now you’re in a bridge call with six
engineers trying to figure out why orders are
failing across the entire ecommerce platform. That
scenario is not hypothetical. It happened at
Amazon in March 2026. The company that builds
the AI coding tools had its own orders disrupted by
code its own engineers shipped with AI assistance.
If it happened to them, it can happen to you.
David Linthicum put a name to what many of us
have been quietly living through. His March 2026
InfoWorld piece, “The AI Coding Hangover”,
landed because it said out loud what senior
engineers have been saying in Slack DMs for
months: we moved fast with AI, we shipped a lot of
code, and now the operational debt is coming due.
The AI coding hangover is real. But “AI is bad” is
the wrong diagnosis, and “write better prompts” is
the wrong cure. Here’s what’s actually broken;


---
*Page 4*


here’s what you can do about it starting Monday
morning.
AI Coding Hangover — Table of Contents
The Promise Was Real. So Is the Hangover.
The Number That Should Keep You Up at Night
You’ve Been Optimizing the Wrong Layer
The Three Layers of a Working Harness
Engineering System
Open-Source Tools That Build the Harness
Build the Harness, Not Just the Prompt
References
AI Coding Key Takeaways
The AI coding hangover is real: 42% of
production code is now AI-generated, and defect


---
*Page 5*


rates are 1.7x higher per AI pull request than
human-written code.
The verification gap is the core problem: 96% of
developers distrust AI-generated code, yet only
48% always verify it before committing. This is
verification debt.
Context engineering alone is not enough:
Optimizing prompts and RAG pipelines
addresses single-inference quality but cannot
prevent systemic failures across time.
Harness engineering is the missing layer:
Architectural constraints and feedback loops
(above context engineering called harness
engineering) are what keep AI-generated code
production-safe.
Amazon proved the need: The world’s most
sophisticated cloud engineering org added
mandatory sign-off gates after a pattern of high-
blast-radius AI-assisted incidents.


---
*Page 6*


Three open-source tools map to the three
layers: Agent Brain (context), Agent RuleZ
(constraints), Agent Skills (feedback) — each
MIT-licensed and production-ready.
Shift, Risk and Harness Engineering for AI code development
AI Coding: The Promise Was Real. So Is
the Hangover.
Let’s be honest about the excitement before we talk
about the crash.


---
*Page 7*


AI coding tools are genuinely transformative.
Between 82% and 91% of developers now use AI
tools weekly. GitHub Copilot crossed 20 million
users. According to Sonar’s 2026 State of Code
Developer Survey, 42% of all committed
production code is now AI-generated, and
developers expect that to reach 65% by 2027. That’s
not a trend. That’s a structural shift in how
software gets built.
The AI Hangover
The productivity gains are real. Tasks that took
days genuinely take hours now. Junior engineers


---
*Page 8*


produce at senior rates for narrow, well-defined
problems. Documentation that never got written
gets written. The tools work.
The problem was not the tools. The problem was
the story executives told themselves about what
the tools could replace.
“Software will be free.” That framing was
everywhere in 2023 and 2024. The assumption
underneath it: writing code is software
engineering. If AI writes code, you can shrink
engineering teams. If AI writes code fast, you can
ship everything fast. If code is free, complexity is
free.
“Software will be free.” That framing was everywhere
in 2023 and 2024. The assumption underneath it:
writing code is software engineering.
Linthicum calls this the fundamental
misunderstanding. Code typing is a small fraction
of what software engineering actually is. The hard


---
*Page 9*


parts (requirements definition, data quality,
security modeling, performance engineering,
operational design, architecture trade-offs) do not
get solved by an LLM generating functions faster.
When you remove human engineering judgment
from those decisions, the cost does not disappear.
It defers.
And deferred cost compounds.
The promise versus the hangover
The AI coding hangover did not arrive suddenly. It
built across four years as adoption outpaced


---
*Page 10*


governance, culminating in high-profile
production incidents and an industry-wide
recognition that writing code faster is not the same
as engineering software better.
CodeRabbit’s December 2025 “State of AI vs
Human Code Generation Report” gives us the
numbers. Across 470 open-source GitHub pull
requests, AI-generated code produced 1.7 times
more issues per PR than human-written code:
10.83 issues per AI PR versus 6.45 for human PRs.
Major issues are 1.7 times higher. Readability
problems are 3.15 times higher. Security issues are
1.56 times higher.
AI doesn’t eliminate complexity. It generates
complexity faster.
Linthicum observes what many of us are seeing
firsthand: companies that bet on AI as a
replacement are quietly rehiring. Platform
engineers, specifically, are being brought back to


---
*Page 11*


untangle the sprawling systems that grew without
architecture reviews or operational planning.
What Linthicum calls “mini-enterprises” (teams
that started with small coding tasks, then
generated modules, then entire services, with no
governance and no system intent) are now
operational problems requiring human engineers
to fix.
The hangover is expensive. And it’s going to get
worse before the industry builds the right
response.
There is hope, you can escape the AI Coding Hangover by adopting
Harness Enginnering


---
*Page 12*


AI Coding: The Number That Should Keep
You Up at Night
Here is the statistic I keep coming back to.
According to Sonar’s 2026 survey, 96% of
developers distrust AI-generated code’s functional
correctness. Nearly every developer working with
AI tools today. Only 3% say they highly trust the
output. Nine out of ten people using these tools
actively doubt what the tools produce.
Now here’s the number that keeps me up at night:
only 48% of those same developers always verify
AI-generated code before committing.


---
*Page 13*


The number that should keep you up at night about AI generated code
Let that sit for a moment. We don’t trust it. And
roughly half of us ship it anyway.
💡
The Verification Paradox: 96% of developers
distrust AI-generated code. Only 48% always verify it.
We know it’s untrustworthy, and we ship it anyway.
Sonar’s 2026 survey reveals a 48-point gap
between awareness and action. Ninety-six percent
of developers distrust AI-generated code for
functional correctness, yet only 48 percent always
verify it before committing. This gap, the
Verification Debt Zone, is not a skills problem. It’s


---
*Page 14*


a structural failure in how teams have integrated
AI into their engineering workflow.
Verification Debt
Werner Vogels, AWS CTO, described this structural
gap at re:Invent 2025 with a term that has stuck:
“verification debt.” He put it precisely: “When you
write code yourself, comprehension comes with
the act of creation. When the machine writes it,
you’ll have to rebuild that comprehension during
review. That’s what’s called verification debt.”
(Note: Kevin Browne first coined the term in
December 2024; Vogels gave it industry-wide
visibility at re:Invent.)


---
*Page 15*


Bridging the AI Verification Gap
Security: Syntactically Correct Does not mean
Semantically Secure
The security dimension of this gap is where the
consequences become unavoidable. Veracode’s
2025 GenAI Code Security Report, testing code
from over 100 large language models, found that
45% of AI-generated code samples failed OWASP
Top 10 security tests. By language: Java failed at
72%, C# at 45%, JavaScript at 43%, Python at 38%.
Syntactically correct code is not the same as
semantically secure code. AI produces the former


---
*Page 16*


reliably. The latter requires something the model
cannot provide on its own.
Syntactically Correct Does not mean Semantically Secure
The Amazon incidents are the most concrete
evidence we have that verification debt has real
blast radius.
In December 2025, an approximately 13-hour
outage hit AWS’s Cost Explorer in the Mainland
China region. Reports describe engineers using
Amazon’s Kiro AI coding tool; the agent deleted
and recreated the entire environment. Amazon


---
*Page 17*


attributed the outage to a misconfigured IAM role
and disputed AI as the root cause. The safeguards
they put in place after the incident are more
revealing than the attribution.
In March 2026, a roughly 6-hour outage disrupted
Amazon’s main ecommerce platform: orders,
account details, product pages. Amazon described
it as an “erroneous software code deployment” and
acknowledged a “trend of incidents” with high
blast radius from AI-assisted changes. They
disputed direct AI causation again. But they
mandated that even senior engineers get code
signed off before deployment — a governance
control added specifically in response to the
pattern of incidents.
Here’s what I take from that: when the world’s
most sophisticated cloud engineering organization
(the company that builds the AI coding tools)
responds to an operational pattern by adding
mandatory review gates, that is not a political


---
*Page 18*


decision. That is an engineering organization
recognizing it needed a harness.
💡
The AWS Data Point: Amazon added mandatory
senior engineer sign-off for AI-assisted code
deployments after acknowledging a “trend of
incidents” with high blast radius. The company that
builds the AI tools concluded it needed harness
controls. That matters.
Move from AI Coding to AI Engineering:
You’ve Been Optimizing the Wrong Layer:
Context Engineering Is Not Enough
So what has the industry done in response to the
quality and security problems? Predictable: better
prompts, better RAG, better context. A whole field
called context engineering has grown up around
improving what the model sees at inference time.
Context engineering is real and valuable. Let me
define it precisely so I can explain why it isn’t


---
*Page 19*


enough.
Context Engineering is not enough
Context engineering is the design and
management of everything the LLM sees during a
single inference: the system prompt, the tool
definitions, the RAG results pulled from your
codebase, the message history, the output
schemas, the memory from prior sessions. The
question it answers is: “What do we show the
agent?”


---
*Page 20*


Good context engineering reduces hallucinations.
It produces better-structured output. It makes a
single inference more likely to succeed. These are
real improvements.
But context engineering has a fundamental ceiling.
Every new inference starts fresh. The model has
no memory of its own failures. If it makes a
mistake today and you fix the context tomorrow,
nothing prevents the exact same mistake next
Thursday when the context shifts again. Context
engineering optimizes the single inference, not the
system across time.
The 96/48 verification gap is proof that context
engineering has not solved the quality problem.
We have had years to refine our prompts, improve
our RAG pipelines, tune our system instructions.
And still, 96% of developers don’t trust what comes
out.
Agent Harness Engineering


---
*Page 21*


What’s missing is the layer above context: harness
engineering.
Birgitta Boeckeler, writing on Martin Fowler’s site
in February 2026, gave us the formal definition.
She describes harness engineering as having three
components:
1. Context Engineering: the continuously
enhanced knowledge base in the codebase, plus
dynamic context from observability data
2. Architectural Constraints: monitored not only
by LLM-based agents, but also by deterministic
custom linters and structural tests
3. Garbage Collection: agents that run periodically
to find inconsistencies in documentation or
violations of architectural constraints
Read that first component carefully. Context
engineering is a subset of harness engineering.
Not a parallel discipline. Not a competitor. A
subset.


---
*Page 22*


Three layers of harness engineering
Context engineering (prompts, RAG, tool
definitions, memory, and output schemas) is the
innermost layer of the harness, not the whole
thing. Boeckeler’s three-component model adds
Architectural Constraints (deterministic linters,
structural tests, security gates) and Feedback
Loops / Garbage Collection (review gates, CI/CD
hooks, drift detection) as required outer layers.
Optimizing only the inner layer while leaving the
outer layers unbuilt is why the verification gap
persists.


---
*Page 23*


Mitchell Hashimoto said it most practically. In his
essay “My AI Adoption Journey” on mitchellh.com,
he wrote:
💡
“I’m making an earnest effort whenever I see an
agent do a Bad Thing to prevent it from ever doing
that bad thing again.”
That single sentence is the philosophy of harness
engineering. Not “let me fix this prompt.” Not “let
me improve the context.” Let me engineer a
solution such that this class of failure cannot recur.
When Hashimoto built this approach into his
Ghostty project, he kept an AGENTS.md file where
each line corresponds to one specific bad behavior
he corrected. “Each line in that file is based on a
bad agent behavior, and it almost completely
resolved them all.”
Context engineering asks: “What do we show the
agent?”


---
*Page 24*


Harness engineering asks: “What do we prevent,
measure, control, and fix?”
Different questions. Different engineering work.
Right now, most teams are only doing the first one.
The model is the CPU. The harness is the OS.
You’ve been tuning the CPU without building the
OS.
The AI Harness is the aspirin to the AI Coding Headache


---
*Page 25*


The Three Layers of a Working Harness
Engineering System for AI Coding Agents
What does a working harness actually look like in
practice? Three layers, each addressing a different
failure mode. Together, they change AI coding
from “code generation I can’t fully trust” to
“engineering automation I can put in production.”
Without a harness, AI-assisted development
becomes a loop: code ships fast, incidents follow,
hotfixes get pushed, and the same failure recurs
next sprint. The harness model interrupts that
loop with gates before production and a feedback
mechanism that converts each failure into a
permanent improvement. Amazon’s mandatory
senior engineer sign-off is the review gate,
implemented by hand. The harness automates it.
Harness Engineering Layer 1: Context
Engineering Done Right — making AI
Coding into Agents AI Coding Engineers


---
*Page 26*


This is where most teams already spend their time,
and it matters. Layer 1 means the agent knows
your system. Not just “here’s a system prompt”; the
agent knows your actual architecture, your failure
history, and which services own which data.
Not just a CLAUDE.md file (though that’s a start).
The agent needs semantic indexing of your
codebase so it can retrieve relevant context at
inference time. It needs persisted architectural
decisions it can access across sessions. It needs
that context kept current as the codebase evolves.
Spec driven development is a real factor here.
Check out BSD, BMAD, SpecKit, Superpowers, and
their ilk.
When context is done right, the agent stops
reinventing what already exists, stops violating
patterns that are already established, and stops
making category errors about which services own
which data. Those three failure modes alone


---
*Page 27*


account for a huge share of the operational debt
Linthicum is describing.
Harness Engineering Layer 2:
Architectural Constraints for AI Coding
Agents
Layer 2 means the agent cannot break certain
invariants even if it tries. This is where context
engineering alone fundamentally fails.
A well-prompted agent might make a reasonable
mistake anyway. A system with architectural
constraints stops that mistake before it ships.
Deterministic constraints don’t negotiate: type
checking passes or it doesn’t. Security linters flag
specific vulnerability patterns or they don’t.
Structural tests catch architecture violations. Think
of it like a circuit breaker for your AI agent; it
doesn’t matter how good the agent is; the breaker
trips on specific conditions, period.


---
*Page 28*


This layer directly addresses the Veracode finding.
If 45% of AI-generated code fails OWASP Top 10
tests, and you run OWASP-aligned security checks
in your CI pipeline before any AI-generated code
merges, the exposure drops dramatically. The
constraint layer doesn’t trust the model to get
security right. It verifies independently.
Amazon’s mandatory sign-off policy is a manual
implementation of Layer 2. A senior engineer
reviewing AI-generated changes before
deployment is a constraint gate. Expensive, slow,
and exactly what you need when you don’t have the
automated equivalent. The harness automates
what Amazon is doing by hand.


---
*Page 29*


Move Beyond Context Engineering and towards Harness Engineering
Harness Engineering Layer 3: Feedback
Loops and Garbage Collection for AI
Coding Agents
Layer 3 is the harness’s immune system. The
system learns from failures and prevents their
recurrence. In my experience, this is the layer
most teams skip; and it’s the one that turns the
harness from a one-time investment into a
compounding asset.
This is Boeckeler’s “garbage collection”
component. Agents that run periodically to find


---
*Page 30*


drift, inconsistencies, and violations. CI/CD hooks
that capture failure patterns. Review gates that
feed information back into the context layer. Every
incident involving AI-assisted code becomes a rule
in the constraint layer, a memory in the context
layer, or a pattern in the workflow layer.
Amazon’s post-incident response is Layer 3 at the
organizational level. They had incidents, ran post-
mortems, added controls. The harness does this
systematically and continuously rather than
reactively and manually.
Mitchell Hashimoto’s AGENTS.md is Layer 3 in its
simplest form: every bad behavior becomes a
documented constraint. One line per incident.
Each line is an improvement to the system.
Together, the three layers create a system that
degrades gracefully when the model fails, learns
from those failures, and gets progressively more
reliable over time. Without the harness, each AI


---
*Page 31*


failure is an incident. With the harness, each AI
failure is an improvement.
Open-Source Tools That Build the
Harness
Frameworks are useful. Concrete tools you can
install Monday morning are better. Adopt Spec
Driven Development with GSD, BMAD, SpecKit,
OpenSpec, Superpowers, etc.
Three open-source tools from Spillwave Solutions
map directly to the harness layers. Each one is
MIT-licensed, actively maintained, and solves a
specific documented problem.
Harness engineering solution stack showing Agent
Brain for cross-project context, Claude Code AI
Agent, Agent RuleZ for policy enforcement, and
Agent Skills for validated workflow patterns with
feedback loops connecting all layers.


---
*Page 32*


Implementing the Harness in Code, Not Just Policy
The three open-source tools implement the three
harness layers in code rather than policy. Agent
Brain provides cross-project context and
architectural memory. Agent RuleZ enforces
deterministic security and policy constraints at
sub-10ms latency. Agent Skills provides repeatable,
validated workflow patterns. The feedback loop at
the bottom converts each production incident into
a permanent harness improvement; the system
learns where context engineering alone cannot.
We are also working on Agent Memory which is
more about monitoring the conversation for


---
*Page 33*


salient information and the indexing it and making
it available so you coding agent or agent does not
forget; alas Agent Memory is still in development.
Harness engineering solution stack showing Agent Brain for cross-
project context, Claude Code AI Agent, Agent RuleZ for policy
enforcement, and Agent Skills for validated workflow patterns with
feedback loops connecting all layers
Agent Brain: Harness Engineering Layer 1
at Scale
Agent Brain is a private RAG system built as a
Claude Code plugin. Its purpose is simple and
specific: give AI agents accurate, retrievable
knowledge of your actual system.


---
*Page 34*


The problem it solves: Linthicum describes “mini-
enterprises” — fragmented systems built by teams
operating without shared context, no architecture
reviews, no system intent. Agent Brain solves this
by creating a continuously updated semantic index
of your codebase that persists across sessions and
spans multiple projects. It also does this for you
documents: design, PRD, specs., governance, etc.
What it does:
Semantic indexing with multi-mode retrieval:
hybrid, semantic/vector, BM25 keyword, and
knowledge graph modes
AST-aware code chunking that understands code
structure across 10 programming languages
Cross-project context so the agent knows how
services relate to each other, not just what’s in
the current file
Architectural memory that persists decisions
from one session to the next


---
*Page 35*


When your agent knows that the order service
owns payment state, and the inventory service
should never write to the payment database, it
stops making a whole class of architectural
mistakes. That knowledge lives in the harness, not
in the prompt you happened to write today.
Repo details: MIT license, 61 stars, 435 commits as
of March 2026. Actively maintained.
Agent RuleZ: Harness Engineering Layer
2 Deterministically
Agent RuleZ is described as “a deterministic,
auditable, local-first AI policy engine for Claude
Code.” It is the architectural constraint layer made
operational.
The problem it solves: The Veracode finding is
stark — 45% of AI-generated code fails OWASP Top
10 tests. Layer 2 without a tool means relying on CI
pipelines that run after code is written, reviewed,
and ready to merge. Agent RuleZ intercepts earlier,


---
*Page 36*


at the agent event level, before bad code is
generated and committed.
What it does:
Intercepts Claude Code events at sub-10ms
latency
Evaluates policy rules expressed in YAML
configuration (not raw JSON, which matters for
maintainability)
Blocks risky operations deterministically: no
model negotiation, no prompt override
Produces an auditable policy trail so you know
exactly what rules fired and when
Built in Rust for the performance characteristics
that make sub-10ms evaluation possible at the tool-
call level. A policy that says “never delete a
production database without an explicit
confirmation step” executes in microseconds and
cannot be talked out of it by a clever prompt.


---
*Page 37*


This is the technical equivalent of Amazon’s
mandatory sign-off, automated and running at
every inference rather than at merge time.
Repo details: MIT license, agent_rulez (with
underscore) on GitHub. Rust-based.
Here is a sample Agent RuleZ YAML policy with
two rules. Read it top to bottom — each rule is a
named policy object with three required fields:
rules:
- name: prevent-production-deletion
event: tool_call # WHEN: fires on any too
condition:
tool: bash # IF: the tool being cal
pattern: "DROP TABLE|DELETE FROM|rm -rf" # AND
environment: production # AND: the current env
action: block # THEN: block the operat
message: "Destructive operations in production re
- name: require-owasp-scan
event: file_write # WHEN: fires whenever t
condition:
file_extension: [".java", ".js", ".py"] # IF:
action: require_check # THEN: gate on a passin
check: owasp_linter # SPECIFICALLY: run the


---
*Page 38*


Walk through what each field does:
name: A human-readable label. This shows up in
audit logs, so name it like a policy document.
event: The Claude Code lifecycle hook where the
rule fires. tool_call intercepts before execution.
file_write intercepts before the file lands on
disk. The rule fires early -- before the bad thing
happens.
condition: The filter criteria. All conditions must
match for the rule to fire. The pattern field uses
regex, so you can match multiple destructive
commands in one rule.
action: What happens when the condition
matches. block stops the operation entirely.
require_check gates on an external validator
passing. There is no "warn" action that the
model can acknowledge and continue -- that
path exists, but block means block.


---
*Page 39*


message: What the developer sees when the rule
fires. This is the teachable moment. Write it like
a colleague explaining why the guardrail exists.
Now here’s a second example showing something
different: encoding an architectural decision, not
just a security policy.
rules:
- name: enforce-service-ownership
event: file_write # WHEN: fires on any file writ
condition:
file_path: "services/inventory/**" # IF: writin
content_pattern: "payment_db|orders_schema" #
action: block
message: "Inventory service must not access payme
orders schemas directly.
Use the PaymentService API. See ADR-012.
- name: require-migration-on-schema-change
event: tool_call # WHEN: a tool is called
condition:
tool: bash
pattern: "ALTER TABLE|CREATE TABLE|DROP COLUMN"
action: require_check
check: migration_exists # THEN: verify a migrati
message: "Schema changes require a versioned migr


---
*Page 40*


These two rules encode decisions from
architecture reviews as machine-enforceable
constraints. The first rule encodes the service
ownership boundary: the inventory service does
not touch payment data, full stop. The second
encodes the team’s migration discipline: schema
changes without migration files do not ship.
Neither of these rules is a prompt. Neither can be
overridden by rephrasing the request. They are not
suggestions to the model; they are constraints on
the model’s actions.
Agent RuleZ can block actions and prevent problems. Unlike Markdown
rules which are strong suggestions or CLAUDE.md or AGENTS.md,
Agent RuleZ takes action.


---
*Page 41*


This is Hashimoto’s AGENTS.md philosophy
implemented at the enforcement layer, not just the
documentation layer. Each rule corresponds to one
real failure mode. The comment in the message
field is the architecture review note, made
executable.
💡
Why Rules Beat Post-Commit CI for Architecture:
A CI check runs after the code is written, reviewed, and
staged for merge. By then, the developer has context-
switched away, the PR is open, and fixing it is friction.
Agent RuleZ fires at the moment of generation — when
the agent writes the file, before the developer even sees
it. The cost of enforcement drops from “fix a PR review
comment” to “the agent gets it right on the first pass.”
Agent Skills: Harness Engineering Layer 3
Patterns
Agent Skills is the Claude Code plugin system for
repeatable, validated workflow patterns. Where
Agent Brain gives the agent knowledge and Agent


---
*Page 42*


RuleZ enforces constraints, Agent Skills ensures
the agent follows consistent execution sequences.
The problem it solves: Inconsistency across teams
and between sessions. Left to its own devices, an
AI agent invents a slightly different deployment
sequence every time. Different engineers get
different results. Lessons learned in one session
don’t carry to the next. Agent Skills packages
validated workflows into reusable patterns that
execute consistently.
What it does:
Encapsulates multi-step workflows as executable
skill sequences
Validates each step before proceeding to the
next
Carries institutional knowledge about how tasks
should be executed in your specific environment
Prevents the common failure mode of agents
“helpfully” taking shortcuts that skip important


---
*Page 43*


validation steps
This is Layer 3’s garbage collection component
made actionable: instead of cleaning up after
failures, Skills prevents the failures by providing
the right execution path in the first place.


---
*Page 45*


Together, the three tools cover the full harness:
The harness is not a single tool. It’s a layered
system. These three tools build that system.


---
*Page 46*


Build the Harness, Not Just the Prompt
The AI coding hangover is real. Linthicum named
it. The data confirms it. Amazon lived it publicly
enough that we all have a case study with
timestamps.
This is not an indictment of AI tools. It’s an
engineering diagnosis: powerful technology
deployed without the engineering infrastructure it
requires. We have been here before. Every
powerful production technology needed a harness;
databases needed transactions and connection
pools, distributed systems needed circuit breakers
and retries, cloud infrastructure needed IaC and
drift detection. AI coding tools need a harness too.
The pattern is as old as production software.
AWS’s response proves the point from the most
credible possible direction. The company that
builds the AI tools, employs some of the world’s


---
*Page 47*


best engineers, and runs the infrastructure that
half the internet depends on — that company
added mandatory sign-off requirements and
governance controls in response to a pattern of
high-blast-radius incidents involving AI-assisted
changes. Not because AI is bad. Because powerful
tools without harness controls produce
unacceptable operational risk.
Building the Harness for Production Safe Code
If AWS needed the harness, so do you.


---
*Page 48*


Here’s where to start. These four steps build on
each other — each one makes the next more
effective.
This week: Create an AGENTS.md file. Document
every bad AI behavior you have personally seen.
One line per behavior, one line per incident. Don’t
try to make it comprehensive. Write down what
actually happened in your system. This is
Hashimoto’s minimum viable harness. Not
sophisticated — and it works. This step costs
nothing and takes an hour. It also forces you to
look honestly at what has gone wrong, which is the
prerequisite for everything that follows.
This month: Add Agent RuleZ with one security
rule. Start with the class of failure most likely to
cause a production incident in your specific
environment. A rule that prevents destructive
database operations without confirmation. A rule
that blocks deployment to production without a
tagged version. One rule, enforced


---
*Page 49*


deterministically. The AGENTS.md you wrote last
week tells you exactly which rule to write first —
it’s the incident that cost the most hours. These
rules do not just inform they take action and block.
This quarter: Set up Agent Brain for cross-project
context. Index your core services. Index your
document repos. Give your agents architectural
memory. Measure the reduction in category
errors: the wrong service touching the wrong data,
the reinvented utility that duplicates an existing
one, the architectural decision that contradicts
what was decided last quarter. The rules you added
with Agent RuleZ will generate data about which
architectural boundaries get crossed most often;
that’s your indexing priority list.
Ongoing: Every production incident involving AI-
assisted code is a harness improvement
opportunity. What rule would have caught this?
What context would have prevented it? What
workflow pattern would have taken the shortcut


---
*Page 50*


off the table? Post-mortem the harness, not just the
code. Without this step, the first three steps are
static. With it, the harness compounds; each
incident makes the system more reliable.
Build the Harnesss, Not just the Prompts
The model is the CPU. The harness is the OS. You
wouldn’t run a production system on bare metal.
Don’t run your AI coding pipeline that way either.


---
*Page 51*


Move from AI Coding Hangover to Engineering Rigor
References


---
*Page 52*


The AI Coding Hangover — David Linthicum,
InfoWorld, March 13, 2026
Sonar 2026: Critical Verification Gap in AI
Coding
CodeRabbit: State of AI vs Human Code
Generation Report, December 2025
Veracode 2025 GenAI Code Security Report
Werner Vogels at re:Invent 2025 — The Register
Amazon AWS Outage December 2025 —
GeekWire
Amazon AI Coding Outages March 2026 — The
Register
Amazon Mandatory Sign-Off — TechRadar
Mitchell Hashimoto: My AI Adoption Journey
Agent Brain — GitHub
Agent RuleZ — GitHub
LangChain Deep Agents: Harness and Context
Engineering: Memory, Skills, and Security —


---
*Page 53*


Rick Hightower, Medium, March 17, 2026 A deep-
dive into how Agent Brain, Agent Skills, and Agent
RuleZ work together inside a LangChain agent
architecture to deliver memory, security, and
reusable workflows.
Harness Engineering vs Context Engineering:
The Model is the CPU, the Harness is the OS —
Rick Hightower, Medium, March 17, 2026 —
Introduces the conceptual distinction between
context engineering and harness engineering using
the CPU/OS analogy central to this article.
Introduction to LangChain Deep Agents and the
Shift to “Agent 2.0” — Rick Hightower, Medium,
March 16, 2026 — Frames the architectural shift
from simple tool-using chatbots to Agent 2.0 systems
with persistent memory, hierarchical orchestration,
and harness-controlled execution.
Under the Hood: Middleware, Sub-Agents, and
Deep Agent LangGraph Orchestration — Rick
Hightower, Medium, March 16, 2026 — Explores
how middleware, sub-agents, and LangGraph work


---
*Page 54*


together as the runtime layer the harness operates
within.
Claude Code Agent Skills 2.0: From Custom
Instructions to Programmable Agents — Rick
Hightower, Towards AI, March 9, 2026 —
Explains the evolution of agent skills from simple
slash-command instructions to fully programmable,
multi-step workflows with validation and feedback
loops.
The End of Manual Agent Skill Invocation:
Event-Driven AI Agents — Rick Hightower,
Artificial Intelligence in Plain English, February
23, 2026 — Describes how agent skills can be
triggered automatically by events rather than
manually, eliminating a major source of
inconsistency in multi-step agentic workflows.
Put Claude on Autopilot: Scheduled Tasks with
/loop and /schedule built-in Skills — Rick
Hightower, Artificial Intelligence in Plain
English, March 11, 2026 — Demonstrates built-in
Agent Skills for scheduling and looping — concrete


---
*Page 55*


examples of how harness-managed skills enable
autonomous, long-running agent operation.
Claude Code’s Automatic Memory: No More Re-
Explaining Your Project — Rick Hightower,
Spillwave Solutions, March 9, 2026 — Covers the
automatic memory capability that ships with
Claude Code /memory
Claude Code Rules: Stop Stuffing Everything into
One CLAUDE.md — Rick Hightower, Medium,
March 10, 2026 — Explains how to structure agent
rules across path-scoped files so that the right
constraints load only when relevant — the modular
architecture behind Agent RuleZ’s deterministic
policy enforcement.
Harness and Context Engineering: Agents —
Injecting the Right Rules at the Right Moment —
Rick Hightower, Spillwave Solutions, February
27, 2026 — Covers the event-driven mechanics of
how Agent RuleZ injects the right context at the
exact moment an agent needs it — solving the
“compaction cliff” problem where static


---
*Page 56*


AGENTS.md and CLAUDE.md guidance disappears
mid-session.
From Approval Hell to Just Do It: How Agent
Skills Fork Governed Sub-Agents in Claude Code
2.1 — Rick Hightower, Spillwave Solutions,
February 6, 2026 — Shows how Agent Skills
combined with policy islands (forked sub-agents
with pre-declared permissions) eliminate approval
fatigue while maintaining governance — the Layer 3
feedback and workflow pattern this article calls
harness engineering.
About the Author
Rick Hightower is a technology executive and data
engineer who led ML/AI development at a Fortune
100 financial services company. He created skilz,
the universal agent skill installer, supporting 30+
coding agents including Claude Code, Gemini,
Copilot, and Cursor, and co-founded the world’s


---
*Page 57*


largest agentic skill marketplace. Connect with
Rick Hightower on LinkedIn or Medium.
Rick has been actively developing generative AI
systems, agents, and agentic workflows for years.
He is the author of numerous agentic frameworks
and developer tools and brings deep practical
expertise to teams looking to adopt AI.
Harness Engineering Prompt Engineering AI
Enterprise Ai Adoption Agentic Ai
Written by Rick Hightower
Following
1.98K followers · 55 following
2026 Agent Reliability Playbook – Free Download DM
me 'PLAYBOOK' for the full version + personalized 15-
minute audit of your current agent setup (no pitch).


---
*Page 58*


No responses yet
To respond to this story,
get the free Medium app.
More from Rick Hightower
Rick Hightower In by
Spillwave Solu… Rick Hight…
Mastering Claude
Stop Clicking
C d ’ /bt /f k
“A ” H I Kill
Claude Code’s /btw, /fork, and
Mastering Agent Skills in
/ i d d t
Cl d C d 2 1 E
6d ago Feb 5


---
*Page 59*


In by In by
Spillwave Solu… Rick Hight… Spillwave Solu… Rick Hight…
Claude Code Skills Agent Skills: The
D Di P t 2 U i l St d d
Part 2 of 2: Deep Dive and The Promise of AI Agents, and
I l t ti th P bl
Dec 9, 2025 Jan 28
See all from Rick Hightower
Recommended from Medium


---
*Page 60*


In by Ezgi İşçioğlu
Data Scienc… Han HELOIR …
Building AI-Powered
Sub-agent vs. Agent
J A li ti it
T i Cl d C d
The Java world hasn’t stayed
A builder’s decision
idl d i th AI l ti
f k f h i
Mar 14 Mar 8
Rick Hightower Reza Rezvani
The Great Framework Karpathy’s AgentHub:
Sh d A P ti l G id t
A practitioner’s comparison of From autoresearch to agent-
th l di ti di ti i f t t
5d ago 5d ago


---
*Page 61*


Mandar Karhade, MD. PhD. In by
CodeToD… Mohammed Br…
Trusting OpenClaw:
THE DEFINITIVE
N idi J t E t d th
BLUEPRINT FOR
NemoClaw is open source,
First published by
hi ti d i d
h d
Mar 9 Feb 21
See more recommendations