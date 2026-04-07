# BashnoMCP

*Converted from: BashnoMCP.PDF*



---
*Page 1*


Open in app
8
Search Write
AI Agents Don’t Need
Your Developer Tools
Noah Mitchem Follow 7 min read · Mar 24, 2026
136 2
Vercel built sixteen specialized tools for their AI
agent. Then they deleted 80% of them and replaced
everything with one capability: execute bash
commands. Success rate went from 80% to 100%.
Speed improved 3.5x. Token usage dropped 37%.
“Maybe the best agent architecture is almost no
architecture at all.” — Andrew Qu, Vercel’s Chief of
Software
Vercel isn’t an outlier. They’re a case study in a
pattern the developer tools industry is desperately


---
*Page 2*


trying to ignore: AI agents don’t want the tools
we’re building for them. They want bash, a file
system, and git. The developer tools industry is
literally spending billions building in the opposite
direction.
The Gold Rush Nobody Questioned
AI-native developer tools are the hottest category
in tech. Eight companies in the space (Claude
Code, Cursor, Replit, Lovable, Devin, Base44,
Emergent, and Bolt) have already crossed a
combined $5 billion in annual recurring revenue.
Investors see transformation.
“AI now creates millions of software builders,” angel
investor Jaymin Shah wrote in his post. “When the
number of builders expands, the number of products
grows exponentially.”
He’s right about the growth. But nobody in this
gold rush stopped to ask a basic question: what do


---
*Page 3*


the AI agents building all this software actually
prefer to use?
The market says the answer is AI-native platforms,
specialized frameworks, and new protocols. The
data says it’s bash.
Google and Accel recently reviewed over 4,000
startup pitches. Roughly 70% were rejected as
“wrappers”, thin UI layers on existing models with
zero underlying innovation. Of the 14,000 AI
startups launched in 2024, over 5,600 have already
shut down. Forty percent failure in under 24
months. And Gartner predicts 30% of agentic AI
projects will fail. Not from lack of tooling, but from
poor data foundations.
The industry is solving the wrong problem. It’s
building tools nobody asked for.
Agents Vote With Their Tokens


---
*Page 4*


When you look at what AI agents actually choose to
use, measured by adoption, reliability, and cost,
the picture is pretty clear.
The most popular AI coding tool in the world is
Claude Code. It earned the #1 spot in the Pragmatic
Engineer’s 2026 survey, with 46% of developers
calling it “most loved.” Four percent of all public
GitHub commits now come from it, projected to
exceed 20% by year’s end. And its architecture is,
to a first approximation, a terminal. Its tools are
bash, grep, file read, file write, and git. That’s it.
An open-source project called learn-claude-code
demonstrated that you can reproduce its core
agent loop in roughly 30 lines of Python.
Thariq, an engineer on the Claude Code team at
Anthropic, summarized the philosophy in two
threads: “Your agent should use a file system” and
“Bash is all you need.”


---
*Page 5*


GitHub reached a similar conclusion from the
opposite direction. They reduced Copilot’s tool
count from over 40 to 13 core tools. Performance
improved. Pre-expansion accuracy jumped from
19% to 72%. SWE-bench scores went up 2–5
percentage points. Fewer tools, better results.
Then there’s MCP, the Model Context Protocol, an
open standard created by Anthropic for connecting
AI agents to external tools and data sources.
Independent benchmarks show MCP server
integrations are 10–32x more expensive than
equivalent CLI commands and achieve only 72%
reliability compared to CLI’s 100%. In one test, an
MCP agent consumed 44,000 tokens for a query
that a CLI agent handled in 1,365. Perplexity’s CTO
Denis Yarats publicly announced in March 2026
that the company is moving away from MCP.
The most telling signal comes from Anthropic
itself. Their recently introduced Skills feature
converts what would have been MCP tool calls into


---
*Page 6*


filesystem-based patterns, saving 98.7% on token
usage, from 150,000 tokens down to 2,000. The
company that created MCP is routing around its
own protocol.
Pieter Levels, the indie developer with dozens of
shipped products, put it bluntly:
“Thank god MCP is dead. It’s all dumb abstractions
that AI doesn’t need because AIs are as smart as
humans so they can just use what was already there —
which is APIs.”
The Ergonomics Mismatch
If you want to understand why agents keep
reaching for bash over purpose-built tools, you
have to understand what developer tools actually
are.
We built syntax highlighting because humans can’t
parse raw text at speed. We built autocomplete
because we type slowly and forget API signatures.


---
*Page 7*


The whole industry is, at root, a set of
workarounds for the limitations of the human
brain.
AI agents don’t have those limitations. They parse
tokens, not pixels. They hold entire codebases in
context. They can generate, resolve, and maintain
dependency trees without ever seeing a visual
interface. Every “feature” we built for human
ergonomics becomes friction for a non-human
user that processes text natively.
Alain Di Chiappari articulated this in an essay:
“Bash was born in 1989. The most mediocre model
running at this time knows bash better than any
person in the world. Bash is the universal adapter. It is
not a coincidence that coding agents are shifting from
complex and expensive MCP configurations to a
simple agent loop with bash as a way to interact,
literally, with the world. The oldest tool turned out to
be the most future proof.”


---
*Page 8*


A January 2026 paper on arXiv titled “From
Everything-is-a-File to Files-Are-All-You-Need”
traced this phenomenon academically, arguing
that Unix’s uniform read/write interface, designed
in the 1970s, maps directly onto how AI agents
want to interact with the world. The agents face an
“interface proliferation problem” when forced to
juggle REST APIs, SQL databases, vector stores,
and cloud consoles. A file system collapses all of
that into something composable.
At Dust, engineers noticed something remarkable:
their AI agents were spontaneously inventing
filesystem-like syntax for searching company


---
*Page 9*


content, using patterns like `file:front/src/some-
file.tsx`, instead of the semantic search interface
they’d been given. The agents weren’t told to use
filesystem patterns. They preferred them.
We built a $50 billion industry around
compensating for the limitations of the human
brain. Then we welcomed a user that doesn’t have
a human brain and tried to sell it the same
products.
The Framework Funeral
Agent frameworks (LangChain, CrewAI, AutoGen,
and many others) were supposed to make building
AI agents easier. They offered abstractions for tool
calling, memory management, chain-of-thought
reasoning, and multi-agent orchestration. A
reasonable bet.
Here’s how that bet played out.


---
*Page 10*


Microsoft placed AutoGen into maintenance mode
in October 2025. BabyAGI was archived in
September 2024 after receiving 20K+ stars.
Octomind, a company that used LangChain in
production for over a year, ripped it out entirely
and published a detailed explanation: “When we
were spending as much time understanding and
debugging LangChain as building features, it
wasn’t a good sign.”
Meanwhile, HuggingFace’s SmolAgents fits its core
agent logic in roughly 1,000 lines of Python. It
reduces LLM calls by 30% compared to traditional
agent frameworks. The model writes standard
Python rather than navigating complex JSON
schemas or framework-specific abstractions.
Anthropic’s own guidance, published in their
“Building Effective Agents blog post, is perhaps the
most damning evidence: “The most successful
implementations weren’t using complex


---
*Page 11*


frameworks or specialized libraries. Instead, they
were building with simple, composable patterns.”
The company that builds Claude, the model
powering the most popular AI coding agent, is
telling developers not to use frameworks.
Frameworks were always a compromise: trading
flexibility for velocity because humans couldn’t
hold enough complexity in their heads. Agents can
hold the complexity. The trade-off no longer
makes sense.
What Agents Actually Need
So if agents don’t need our tools and they don’t
need our frameworks, what do they actually need?
The honest answer is mostly boring: well-
documented APIs with stable contracts, reliable
file systems, clean version control semantics,
structured I/O, and sandboxing. The kind of


---
*Page 12*


infrastructure that has existed in some form for
decades.
But there’s a catch. The old infrastructure works at
human scale. Agents operate at a different scale
entirely, and that’s where genuine gaps emerge.
Not in the application layer, but in the
infrastructure layer underneath it.
Agents shouldn’t need to clone an entire repository
to read three files. They need virtual filesystems
that provide lazy, partial access to remote code.
Agents working in parallel shouldn’t collide in
merge conflict cascades. They need version control
with native concurrent write semantics and
mutable change primitives. When an agent
introduces a subtle bug, you need to query what
model, prompt, and context produced the change.
Git’s commit metadata doesn’t carry that
provenance. And as organizations spin up
hundreds of agents per repository, they need
permission scoping at the forge level: repo-scoped


---
*Page 13*


API keys, path-restricted access, sandbox
boundaries enforced by the platform rather than
by the agent’s good behavior.
Aaron Levie, Box’s CEO, said it directly on CNBC in
March 2026:
“AI agents will be the biggest users
of software in the future. And
agents actually need a file system
to be able to do their work.”
A handful of companies have started building at
this layer. Instead of another dashboard or another
MCP integration, they’re working at the protocol
level: VCS primitives, virtual filesystems, change
semantics. The boring infrastructure that agents
actually touch.
The existing tools aren’t dying for humans.
Developers still need syntax highlighting and


---
*Page 14*


dashboards and visual debuggers, and companies
like Cursor are building $2 billion businesses
serving that need. Enterprise environments still
need the governance that protocols like MCP
provide: OAuth, audit trails, per-user permissions.
These are real requirements for human developers
working with AI.
But the growth market isn’t human developers
anymore. The next hundred million “developers”
won’t be human. And the infrastructure that earns
their usage will look nothing like the tools we built
for ourselves.
The Right Question
The developer tools industry keeps asking how to
make its products AI-native. That question already
contains the wrong assumption. Agents don’t need
tools. They need primitives. Interfaces. Protocols.
Plumbing.


---
*Page 15*


Now, there’s a version of this argument that falls
apart. Bash works great when an agent is operating
on a local codebase with a filesystem it can see. It
works less well when the agent needs to
authenticate against a cloud provider, orchestrate a
multi-step deployment, or interact with a system
that has no CLI at all. The “just use bash” thesis has
real limits, and anyone building infrastructure for
agents will hit them quickly.
But the direction is clear. The most future-proof
developer tool was built in 1989. The most future-
proof developer infrastructure hasn’t been built
yet, and when it arrives, it’ll look less like a product
and more like plumbing.
Programming Technology Artificial Intelligence
Software Engineering AI


---
*Page 16*


Written by Noah Mitchem
Follow
129 followers · 5 following
Building AI coding tools. Ex-IBM. Writing about the
agent-first development stack.
Responses (2)
To respond to this story,
get the free Medium app.
Ergon Copeland
Mar 25
Definitely agree things like langchain, or any framework for building
agents is like wix for people who don’t know software engineering. For
the rest, it’s easier to just build the agent from scratch, lean meaning
token processing machine. As for… more
8 1 reply
Kamrun Nahar she/her
1 day ago
you say what everyone is thinking but cant articulate


---
*Page 17*


More from Noah Mitchem
Noah Mitchem Noah Mitchem
GitHub Is Dying and Something Flipped in
D l D ’t E D b
In 2008, GitHub changed how In July 2025, the most rigorous
d l k d I 2018 t d d t d AI
Feb 18 Feb 27
Noah Mitchem
AI Agents Don’t Need
P ll R t Th
A few weeks ago, I published a
i i th t GitH b’
Mar 12


---
*Page 18*


See all from Noah Mitchem
Recommended from Medium
Ignacio de Gregorio In by
Data Science… Tanmay D…
Why Everyone is Doing
Datadog, Block, and
A t W
Cl dfl All
Agents aren’t magic; we
Comparing traditional, code
li t th
d d l d
Mar 24 Mar 13
The Latency Gambler In by
Level Up Coding David Lee


---
*Page 19*


Anthropic Says The Rules NASA Uses
E i W ’t E i t t W it C d Th t
The most honest job posting In 2006, a NASA engineer
i t h hi t i ht l b t t l f iti
Mar 18
Mar 11
In by Max Petrusenko
Artificial Intelligenc… Faisal…
The Book That Terrified
Vector RAG Is Dead.
th P l B ildi AI
P I d J t P
Eliezer Yudkowsky and Nate
How a reasoning-based, tree-
S th t
h f k hi d
Mar 21 Mar 24
See more recommendations