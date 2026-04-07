# SelfEvolveHope

*Converted from: SelfEvolveHope.PDF*



---
*Page 1*


Open in app
11
Search Write
Self-Evolving Agents:
Open-Source Projects
Redefining AI in 2026
From Static Prompts to Recursive Mastery:
How the Open-Source Community is Building
AI that Teaches Itself
evoailabs Follow 9 min read · Mar 25, 2026
17
Top Most Exciting Self-Evolving Projects


---
*Page 2*


https://eu.36kr.com/en/p/3739201554399237
https://arxiv.org/pdf/2603.24517v1
Agentic Variation Operators (AVO) are a new family of
evolutionary variation operators that replace the fixed
mutation, crossover, and hand-designed heuristics of
classical evolutionary search with autonomous coding
agents. Rather than confining a language model to
candidate generation within a prescribed pipeline,
AVO instantiates variation as a self-directed agent loop


---
*Page 3*


that can consult the current lineage, a domain-specific
knowledge base, and execution feedback to propose,
repair, critique, and verify implementation edits. We
evaluate AVO on attention, among the most
aggressively optimized kernel targets in AI, on NVIDIA
Blackwell (B200) GPUs. Over 7 days of continuous
autonomous evolution on multi-head attention, AVO
discovers kernels that outperform cuDNN by up to
3.5% and FlashAttention-4 by up to 10.5% across the
evaluated configurations. The discovered
optimizations transfer readily to grouped-query
attention, requiring only 30 minutes of additional
autonomous adaptation and yielding gains of up to
7.0% over cuDNN and 9.3% over FlashAttention-4.
Together, these results show that agentic variation
operators move beyond prior LLM-in-the-loop
evolutionary pipelines by elevating the agent from
candidate generator to variation operator, and can
discover performance-critical micro-architectural
optimizations that produce kernels surpassing state-of-
the-art expert-engineered attention implementations
on today’s most advanced GPU hardware.


---
*Page 4*


https://github.com/HKUDS/OpenSpace
The Problem with Today’s AI Agents
Today’s AI agents — OpenClaw, nanobot, Claude
Code, Codex, Cursor, etc. — are powerful, but they
have a critical weakness: they never Learn, Adapt,
and Evolve from real-world experience — let alone
Share with each other.


---
*Page 5*


❌
Massive Token Waste — How to reuse successful
task patterns instead of reasoning from scratch and
burning tokens every time?
❌
Repeated Costly Failures — How to share solutions
across agents instead of repeating the same costly
exploration and mistakes?
❌
Poor and Unreliable Skills — How to maintain
skill reliability as tools and APIs evolve — while
ensuring community-contributed skills meet rigorous
quality standards?
🎯
What is OpenSpace?
🚀🚀
The self-evolving engine where every task
makes every agent smarter and more cost-efficient.


---
*Page 6*


https://www.marktechpost.com/2026/03/24/a-coding-implementation-
to-design-self-evolving-skill-engine-with-openspace-for-skill-learning-
token-efficiency-and-collective-intelligence/
This tutorial explores OpenSpace, a self-evolving
skill engine developed by HKUDS that enables AI
agents to capture and reuse patterns from
completed tasks. The framework utilizes three
evolution modes — FIX, DERIVED, and CAPTURED
— to automate skill learning, resulting in a
demonstrated 46% reduction in token usage. Users
can manage these capabilities through a local
SQLite database or share evolved intelligence via
the open-space.cloud community. By
implementing this system, developers can


---
*Page 7*


significantly improve agent cost-efficiency and
performance across professional multi-task
pipelines.
https://github.com/karpathy/autoresearch
One day, frontier AI research used to be done by
meat computers in between eating, sleeping,
having other fun, and synchronizing once in a
while using sound wave interconnect in the ritual
of “group meeting”. That era is long gone.
Research is now entirely the domain of
autonomous swarms of AI agents running across


---
*Page 8*


compute cluster megastructures in the skies. The
agents claim that we are now in the 10,205th
generation of the code base, in any case no one
could tell if that’s right or wrong as the “code” is
now a self-modifying binary that has grown
beyond human comprehension. This repo is the
story of how it all began. -@karpathy, March 2026.
The idea: give an AI agent a small but real LLM
training setup and let it experiment autonomously
overnight. It modifies the code, trains for 5 minutes,
checks if the result improved, keeps or discards, and
repeats. You wake up in the morning to a log of
experiments and (hopefully) a better model. The
training code here is a simplified single-GPU
implementation of nanochat. The core idea is that
you’re not touching any of the Python files like you
normally would as a researcher. Instead, you are
programming the program.md Markdown files that
provide context to the AI agents and set up your
autonomous research org. The default program.md in
this repo is intentionally kept as a bare bones baseline,


---
*Page 9*


though it's obvious how one would iterate on it over
time to find the "research org code" that achieves the
fastest research progress, how you'd add more agents to
the mix, etc. A bit more context on this project is here
in this tweet and this tweet.
Karpathy/AutoResearch: The “Karpathy Loop”
Implementation
Andrej Karpathy’s latest viral repository has turned
“Vibe Coding” into “Recursive Science.” It focuses
on a small, tight loop: the agent modifies its own
training code, runs a 5-minute test, evaluates the
result, and commits the change only if it improves
the metric. It operates on a program.md file — a
human-readable “operating manual” for the agent
that the agent itself refines over thousands of
generations.


---
*Page 10*


https://arxiv.org/pdf/2603.19461
Self-improving AI systems aim to reduce reliance on
human engineering by learning to improve their own
learning and problem-solving processes. Existing
approaches to recursive self-improvement typically rely
on fixed, handcrafted meta-level mechanisms, which
fundamentally limit how fast such systems can
improve. The Darwin Gödel Machine (DGM) (Zhang
et al., 2025b) demonstrates that open-ended self-
improvement is achievable in coding. Starting from a
single coding agent, the DGM repeatedly generates and
evaluates self-modified variants, forming a growing
archive of stepping stones for future improvement.
Because both evaluation and self-modification are
coding tasks, gains in coding ability can translate into
gains in self-improvement ability. However, this
alignment does not generally hold beyond coding
domains. We introduce hyperagents, self-referential
agents that integrate a task agent (which solves the
target task) and a meta agent (which modifies itself
and the task agent) into a single editable program.


---
*Page 11*


Crucially, the meta-level modification procedure is
itself editable, enabling metacognitive self-
modification, improving not only task-solving
behavior, but also the mechanism that generates future
improvements. We instantiate this framework by
extending DGM to create DGM-Hyperagents (DGM-
H). By allowing the improvement procedure to evolve,
the DGM-H eliminates the assumption of domain-
specific alignment between task performance and self-
modification skill, and can potentially support self-
accelerating progress on any computable task. Across
diverse domains (coding, paper review, robotics
reward design, and Olympiad-level math-solution
grading), the DGM-H improves performance over time
and outperforms baselines without self-improvement
or open-ended exploration, as well as prior self-
improving systems like DGM. We further show that the
DGM-H improves the process by which it generates
new agents (e.g., persistent memory, performance
tracking), and that these meta-level improvements
transfer across domains and accumulate across runs.
All experiments were conducted with safety


---
*Page 12*


precautions (e.g., sandboxing, human oversight). We
discuss what safety entails in this setting and the
broader implications of self-improving systems. DGM-
Hyperagents offer a glimpse of open-ended AI systems
that do not merely search for better solutions, but
continually improve their search for how to improve.
Hyperagents: Metacognitive Recursive LLMs
Emerging from recent arXiv breakthroughs,
Hyperagents bypass human engineering
bottlenecks by merging the Task Agent and the
Meta Agent into a single editable program. It uses
a Gödel Machine approach where the agent is
mathematically authorized to rewrite its own
source code. If the “Meta Agent” proves that a
change to its internal logic will lead to better task
performance, it self-patches in real-time.


---
*Page 13*


https://github.com/aiming-lab/AutoResearchClaw
What Is This?
You think it. AutoResearchClaw writes it.
Drop a research topic — get back a full academic paper
with real literature from OpenAlex, Semantic Scholar
& arXiv, hardware-aware sandbox experiments
(GPU/MPS/CPU auto-detected), statistical analysis,
multi-agent peer review, and conference-ready LaTeX
targeting NeurIPS/ICML/ICLR. No babysitting. No
copy-pasting. No hallucinated references.
Aiming-Lab/AutoResearchClaw: The 23-Stage
Scientist


---
*Page 14*


While most agents handle “tasks,”
AutoResearchClaw handles “careers.” It automates
the entire scientific lifecycle, from hypothesis
generation to NeurIPS-ready PDF formatting. It
doesn’t just learn facts, it learns process failures. If a
data visualization fails in Stage 14, the agent
generates a “Structured Lesson” that is
permanently injected into its global reasoning
framework to prevent that specific type of failure
in all future research runs.


---
*Page 15*


https://github.com/volcengine/OpenViking
Automatic Session Management → Context Self-
Iteration
OpenViking has a built-in memory self-iteration loop.
At the end of each session, developers can actively
trigger the memory extraction mechanism. The system
will asynchronously analyze task execution results and
user feedback, and automatically update them to the
User and Agent memory directories.


---
*Page 16*


User Memory Update: Update memories related to user
preferences, making Agent responses better fit user
needs.
Agent Experience Accumulation: Extract core content
such as operational tips and tool usage experience
from task execution experience, aiding efficient
decision-making in subsequent tasks.
This allows the Agent to get “smarter with use”
through interactions with the world, achieving self-
evolution. Learn more: Session Management
OpenViking: The Filesystem for AI Brains
Traditional RAG (Retrieval-Augmented Generation)
is “flat.” OpenViking replaces it with a hierarchical
context OS that treats an agent’s memory like a
Linux filesystem (viking://agent/skills/). It features
Recursive Retrieval. Instead of just finding a
matching text chunk, the agent “browses” its own
memory directories, evolving its knowledge
structure over time to be more navigable and
token-efficient.


---
*Page 17*


Core Principles of Self-Improvement
Modern self-evolving agents operate on four
foundational pillars:
1. Closed-Loop Feedback: The system must have a
“Judge” (often a stronger model or a hard-coded
test suite) that provides a binary or scalar reward
for every self-modification.
2. Atomic Skill Acquisition: Instead of changing
the whole model, agents evolve “Skills” — small,
reusable Python modules or optimized prompt
snippets stored in a library.
3. Experience Persistence: Information is not just
stored in a conversation history, it is distilled
into “Lessons Learned” and “Workflow
Templates” that survive the termination of the
current session.
4. Recursive Meta-Reasoning: The agent asks itself:
“How could I have solved this task with 50% fewer
steps?” and then updates its internal strategy for
the next iteration.


---
*Page 18*


The Core Architecture: The “Evolutionary
Loop” Framework
The standard architecture for a self-improving
agent in 2026 follows a Layered Recursive Stack:
graph TD
User((User Goal)) --> Orchestrator[Orchestrator:
Orchestrator --> Executor[Task Agent: Execute Cod
Executor --> Sandbox[Secure Sandbox: Test Run]
Sandbox --> Evaluator[Critic/Judge: Measure Succe
Evaluator -- Failure --> Debugger[Self-Correction
Debugger --> Executor
Evaluator -- Success --> Optimizer[Meta-Optimizer
Optimizer --> SkillLibrary[(Skill Library / Files
SkillLibrary -.-> Orchestrator
subgraph Evolution Engine
Optimizer
SkillLibrary
end
How the Framework Works:
1. The Plan: The Orchestrator receives a goal and
checks the Skill Library for any “evolved”


---
*Page 19*


patterns that match.
2. The Execution: The Task Agent runs the code in
a Sandbox (using tools like NVIDIA OpenShell) to
prevent system damage.
3. The Critique: The Evaluator checks if the code
worked and if it was efficient.
4. The Evolution: If successful, the Optimizer
strips away the trial-and-error “noise” and saves
only the perfected logic as a new SKILL.md file,
making the agent permanently smarter for the
next run.
AI Ai Agents Self Improvement
Written by evoailabs
Follow
821 followers · 37 following
Tech/biz consulting, analytics, research for founders,
startups, corps and govs.


---
*Page 20*


No responses yet
To respond to this story,
get the free Medium app.
More from evoailabs
evoailabs evoailabs
Meet Clawra: The Open The Rise of World
S Gi lf i d Wh M d l d th E d f
When your girlfriend lives on Key takeaways from the 2026
h d d i t W ld M d li W k h i
Feb 11 Feb 8


---
*Page 21*


evoailabs evoailabs
When AI Gets Physical Cybersecurity LLMs:
H d A R i f N L ll
In early 2026, the open-source By 2026, we stopped asking
AI t f k AI t it d t t
Mar 3 Feb 1
See all from evoailabs
Recommended from Medium
In by In by
Predict Tasmia Sharmin CodeX MayhemCode


---
*Page 22*


Palantir CEO Says Only Mini PC vs Desktop PC
T T Will S i f L l LLM i 2026
Alex Karp told Gen Z there are Most people buying hardware
“b i ll t t k f l l AI i 2026 k th
Mar 26 Mar 26
Mandar Karhade, MD. PhD. In by
Towards AI Ari Vance
Europe’s €800 Billion
This 196B Open-Source
B k L tt t
M d l B t Cl d
The EU isn’t just diversifying.
Every week, the same models
It’ b ildi ll l
d i t Li k dI /
Mar 27 Mar 23


---
*Page 23*


In by Ege Karaosmanoglu
Activated… Adi Insights and…
Apache Camel Was
I Ignored 40+
Al d G t AI
O F Alt ti
There’s a quiet reason Apache
Everyone is building agent
C l i b i f th
f k M t P th
Mar 21 Mar 17
See more recommendations