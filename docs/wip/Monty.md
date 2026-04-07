# Monty

*Converted from: Monty.PDF*



---
*Page 1*


Open in app
11
Search Write
Member-only story
Why AI Agents Are
Ditching Docker for
Interpreter-Level
Sandboxing
Suleiman Tawil Follow 7 min read · Feb 10, 2026
6
Monty: <1 microsecond startup. Docker: ~195
milliseconds. Both claim to solve AI code
execution. One is 195,000 times faster.


---
*Page 2*


On February 6, 2026, Pydantic dropped Monty — a
minimal Python interpreter written in Rust that
executes code in under one microsecond. Within
48 hours, it hit 2,600 GitHub stars and sparked
intense debate on Hacker News. The claim? Docker
containers are too slow for how AI agents actually
work.
This isn’t a “Docker is bad” story. It’s evidence that
we’ve been solving the wrong problem. Most AI
infrastructure assumes agents need full filesystem


---
*Page 3*


and network access — the kind of isolation Docker
provides. But the majority of AI code execution
today happens in “code mode”: LLMs writing tiny
Python scripts to chain tool calls, process JSON, or
perform quick calculations. For this use case,
spinning up a container is like renting a U-Haul to
deliver a letter.
The gap between Docker’s hundreds of
milliseconds and Monty’s microseconds isn’t just a
benchmark flex. It represents a fundamental shift
in how we sandbox AI-generated code — and
exposes assumptions the industry hasn’t
questioned until now.
The Latency Problem
Container startup times have been “good enough”
for years. A typical Docker container running
python:3.14-alpine starts in roughly 195
milliseconds. Modern research confirms most
containers launch in "hundreds of milliseconds,"
with optimized setups reaching tens of


---
*Page 4*


milliseconds using low-level runtimes like runc or
crun.
But “good enough” assumed the wrong workflow.
When AI agents execute code, they don’t run one
long script and exit. In code mode — the pattern
Anthropic, Cloudflare, and now Pydantic are
pushing — the LLM writes dozens of micro-scripts
per conversation turn. Each script chains tool
calls, extracts specific fields from results, and runs
small algorithms without sending entire
intermediate values back to the LLM.
Here’s what that looks like in practice:
Traditional tool calling:
1. LLM calls get_user_data(user_id="12345")
2. Tool returns entire 50KB JSON object
3. All 50KB goes back into LLM context
4. LLM calls another tool with extracted field


---
*Page 5*


5. Repeat for every dependent operation
Code mode with Monty:
1. LLM writes: user = get_user_data("12345");
send_email(user["email"], "subject")
2. Monty executes both calls, only returns
success/error
3. Context stays minimal
Every tool call that depends on a previous result
now requires a new LLM turn in traditional mode.
With code mode, you chain operations in one pass.
The catch? You’re executing code many times per
turn, not once per session.
If you’re running 20 code snippets per
conversation turn, Docker’s 195ms becomes 3.9
seconds of pure startup overhead. Monty’s sub-
microsecond execution makes this effectively zero.


---
*Page 6*


This is why Simon Willison immediately built a
WebAssembly demo of Monty hours after release
— the speed enables entirely new interaction
patterns that weren’t viable before.
Why a Minimal Interpreter Beats a Full
Sandbox
Monty isn’t trying to replace CPython. It’s solving a
different problem: secure, instant execution of
small, predictable scripts.
Here’s what Monty strips away:
No standard library (except basics: sys, typing
support coming)
No class declarations (yet — v0.0.4 as of Feb
2026)
No third-party libraries
No filesystem, network, or environment variable
access by default
What it keeps:


---
*Page 7*


Core Python syntax (functions, loops,
comprehensions, basic types)
Snapshotting: pause/resume interpreter state to
bytes
Strict resource limits: memory, allocations, stack
depth, execution time
Performance: generally 5x faster to 5x slower
than CPython
The counterintuitive insight: These limitations
don’t matter for code mode.
From the Hacker News thread, Simon Willison
noted: “It doesn’t have class support yet! But it doesn’t
matter, because LLMs that try to use a class will get an
error message and rewrite their code to not use classes
instead.”
LLMs are incredibly good at adapting to
constrained environments through error feedback.
If a feature is missing, they iterate around it. One
Hacker News user (jstanley) pushed back: “Every


---
*Page 8*


little papercut at the lower levels of abstraction
degrades performance at higher levels as the LLM
needs to spend its efforts on hacking around jank
in the Python interpreter instead of solving the
real problem.”
Fair concern. But Pydantic is betting the trade-off
is worth it.
The alternative — running full CPython with
seccomp, namespaces, and Docker isolation —
adds complexity, latency, and operational
overhead. Pre-warming container pools helps, but
now you’re managing infrastructure for something
that should be instant.
Monty’s Rust implementation with zero CPython
dependencies means it can be embedded
anywhere: Python projects, JavaScript/TypeScript
via bindings, compiled to WASM for browsers. The
attack surface is minimal by design, not by bolting
on security layers afterward.


---
*Page 9*


The Docker Counterargument: “We’re
Evolving Too”
Docker isn’t sitting still. Two major releases in the
past four months specifically target AI agent
workloads:
Docker Sandboxes (January 2026): microVM-
based isolation for coding agents like Claude Code,
Cursor, and Gemini. These are specifically
designed to let agents build and run Docker
containers while remaining isolated from the host.
As Docker’s blog states: “Most developers quickly
run into the same set of problems trying to solve
this: OS-level sandboxing interrupts workflows and
isn’t consistent across platforms.”
Docker Compose for AI Agents (November 2025):
Native support for defining agents, models, and
MCP tools in compose.yaml. One command spins up
your full agentic stack, integrated with LangGraph,
Embabel, Vercel AI SDK, Spring AI, CrewAI, and
Google's ADK.


---
*Page 10*


Google also released Kubernetes Agent Sandbox in
late 2025 — a formal subproject of Kubernetes SIG
Apps for agent workloads. It uses pre-warmed pod
pools to achieve sub-1-second latency with gVisor
or Kata Containers isolation.
These are impressive advancements. But they’re
solving a different problem.
Docker Sandboxes target autonomous coding
agents that need terminal access, filesystem
operations, and network calls. Monty targets code-
mode execution where the agent isn’t running
arbitrary commands — it’s chaining your pre-
approved tool calls with small glue scripts.
The founder of E2B (a VM-based agent sandbox
company) commented on Hacker News: “There’s no
way around VMs for secure, untrusted workloads.
Everything else, like Monty, has too many tradeoffs.”
Samuel Colvin (Pydantic creator) responded: “V8
shows that’s not true. But to be clear, we’re not even


---
*Page 11*


targeting the same ‘computer use’ use case… we’re
aiming to support programmatic tool calling with
minimal latency and complexity.”
This captures the fundamental divide: VMs and
Docker for autonomous agents with broad system
access. Minimal interpreters for constrained code
mode.
When Does This Actually Matter?
Not every AI application needs Monty. Here’s
where it makes sense:
Use Monty when:
Agents execute code 10+ times per conversation
turn
Scripts are small, predictable, and primarily
chain tool calls
Latency compounds (conversational AI, real-
time systems)


---
*Page 12*


You want zero infrastructure overhead (no
container pools to manage)
Security via minimal surface area is acceptable
Stick with Docker/VMs when:
Agents need filesystem or network access
Scripts use arbitrary third-party libraries
Long-running compute tasks (>1 second)
Regulatory compliance requires VM-level
isolation
You’re building autonomous coding agents
(Claude Code, Cursor)
Cloudflare’s code-mode implementation uses
Pyodide (CPython compiled to WASM) because
they already had robust WASM sandboxing in
Workers. Anthropic is expected to integrate Monty
into Pydantic AI for code mode soon.


---
*Page 13*


The pattern emerging: polyglot sandboxing. Use
the right isolation for the job — Monty for code
mode, Docker for terminal agents, VMs for
untrusted external code.
The Unanswered Security Questions
Monty’s security model deserves scrutiny. While it
blocks filesystem, network, and environment
access by default, it’s a brand-new codebase
(v0.0.4) implementing a complex language subset.
The README acknowledges this with refreshing
honesty: “Most of these solutions were not conceived
with the goal of providing an LLM sandbox, which is
why they’re not necessarily great at it.”
Early Hacker News concerns:
Can malicious prompts craft exploits in the
limited Python subset?
What happens when snapshot/resume state
handling has bugs?


---
*Page 14*


How does it compare to battle-tested seccomp +
namespace isolation?
Pydantic’s bet: starting with a minimal
implementation is safer than locking down a
massive one. The entire stdlib in CPython is tens
of thousands of lines of C code that interacts with
the OS. Monty sidesteps this by not implementing
most of it.
V8 (JavaScript engine) proves user-space
sandboxing can work — billions of devices run
untrusted JavaScript daily. But V8 has had constant
sandbox escapes since its inception. Monty will
need hardening over time.
For production use today, defense-in-depth makes
sense: run Monty inside a container or microVM
for an extra boundary layer. You still get most of
the speed benefit while adding insurance.
Why This Matters Beyond Speed


---
*Page 15*


The speed gap isn’t just about milliseconds. It’s a
signal that AI code execution is a distinct category
from general-purpose computing.
For decades, we’ve optimized for:
Developers writing code humans maintain
Long-running processes with rich I/O
Maximum flexibility and library ecosystem
access
AI agents have different needs:
Code nobody reads (intermediate calculations)
Thousands of tiny, throwaway scripts per day
Controlled environments with explicit tool
access
Monty’s success (2,600 stars in 48 hours) suggests
the market agrees there’s a gap. The question isn’t
whether minimal interpreters have a place — it’s


---
*Page 16*


whether the current limitations are acceptable
trade-offs.
Class support is coming. Standard library modules
are being added. But Pydantic is intentionally
moving slowly, prioritizing security and simplicity
over feature parity with CPython.
The real innovation isn’t the technology — it’s
correctly identifying the use case. Code mode
doesn’t need Docker’s 195ms startup. It needs
instant, constrained execution with no operational
overhead.
Whether Monty specifically wins or another
project takes the idea further, the pattern is clear:
the next generation of AI infrastructure will be
purpose-built, not retrofitted from cloud-native
tools designed for humans.


---
*Page 17*


What’s your take? Are minimal interpreters the
future of AI code execution, or does Docker’s
ecosystem and maturity make it the safer long-
term bet? Drop your thoughts in the comments.
For the latest on Monty’s development, check the
GitHub repo. For Pydantic AI’s code-mode
implementation (coming soon), watch PR #4153.
Written by Suleiman Tawil
Follow
222 followers · 397 following
Exploring AI and emerging tech with curiosity—
highlighting what matters most and where human
and machine intelligence intersect.
No responses yet


---
*Page 18*


To respond to this story,
get the free Medium app.
More from Suleiman Tawil
Suleiman Tawil Suleiman Tawil
Who Watches the Cosmos-Predict2.5:
W t h ? I id NVIDIA’
An Analysis of the vmfunc How a unified world model
R h T ’ R l ti t i d 200 illi t
Feb 19 Nov 5, 2025
Suleiman Tawil Suleiman Tawil
Prisma 7 Upgrade: The How Large Language
D i Ad t P th M d l W k A G id


---
*Page 19*


A real-world experience The Simple Truth
di N tJS
Nov 17, 2025
Jan 5
See all from Suleiman Tawil
Recommended from Medium
In by ⾼達 Nayan Paul
Towards … Gao Dalie ( …
Ontology-Driven
NVIDIA Nemoclaw +
A t Th Mi i
O Sh ll FASTEST
Why enterprises need this
If you don’t have a Medium
b i ti thi li k t
Mar 22 Mar 24


---
*Page 20*


Christian Dussol Purvanshi Mehta
I built a Claude Code Why SVG Generation
Skill f K b t N d N
How encoding Kubernetes Haonan Zhu, Adrienne
li i f D tti P hi M ht
Mar 21 Mar 27
💻 🚀
Piero Silvestri In by
Level Up Coding Yanli Liu
From Claude Code to a
Claude Code Just Got
l t Fi d i
Ch l I It E h?
How Claude Code can turn a
t i t d i d
Mar 24 Mar 23
See more recommendations