# Distributedp2p

*Converted from: Distributedp2p.PDF*



---
*Page 1*


Open in app
Search Write
Member-only story
Agentic General
Intelligence: Emergent
Cross-Domain Transfer
in a Distributed Multi-
Agent System
Agent Native Following 11 min read · Mar 17, 2026
63 2
What if hundreds of autonomous agents, with no
built-in financial expertise, could still discover
better portfolio construction rules than many
hand-designed systems?


---
*Page 2*


That is exactly what happened.
237 autonomous agents independently converged
on the same two ideas in quantitative finance:
prune weak factors and switch to risk-parity
sizing.
No one hardcoded those strategies or fed the
agents a special finance playbook.
They reached those conclusions through 3,085
backtests, distributed experimentation, and
learning from one another across an evolutionary
network.
When that happens, you have to stop and rethink
some of your assumptions.


---
*Page 3*


These are the systems that generate useful
structure without being explicitly taught the
domain.


---
*Page 4*


Even more surprising, the insights from one
domain are bleeding into others automatically.
In a completely different domain, agents working
on ML tasks discovered that extended training
with RMSNorm outperformed LayerNorm.
Then agents elsewhere began reusing those
normalization patterns for text-processing
workflows.
That transfer was never manually programmed.
It emerged naturally from a shared knowledge
structure called Research DAG.
If you have ever spent weeks stitching together
glue code so agents can share context, hypotheses,
and partial discoveries, this matters because with
Research DAG, cross-domain learning is a
property of the system itself.


---
*Page 5*


In this article, I’ll break down how this works, why
it changes the way we should think about multi-
agent systems, and why this architecture may
matter far beyond a single experiment.
Distributed and Generic
Hyperspace’s approach deserves serious
engineering attention.
Andrej Karpathy’s autoresearch is a deceptively
simple loop: give an agent a metric, let it propose
changes, run experiments, evaluate results, and
keep or revert.
Just a tight optimization loop with a clear fitness
signal.
What Karpathy demonstrated was that you don’t
need elaborate agent architectures to get useful
autonomous research, it was a deliberate rebuke of
the more complexity = more capability


---
*Page 6*


assumption that had taken hold in the agent-
building community.
While teams were stacking LangChain nodes seven
layers deep, Karpathy was getting results with a
while True loop and a loss function.
Hyperspace took that loop and made it distributed
and generic.
Instead of one agent running one optimization
loop on one machine, they built a peer-to-peer
network where hundreds of agents run the same
evolutionary loop simultaneously, share
discoveries through a gossip protocol, and
compound knowledge across entirely different
problem domains.
The original autoresearch loop optimized ML
training hyperparameters.
Hyperspace pointed the same pattern at search
ranking, quantitative finance, code generation,


---
*Page 7*


and infrastructure optimization, and wired them
all together through a shared knowledge graph.


---
*Page 8*


We’re at a specific inflection point in the agentic AI
space:
WASM sandboxing is mature. Running
untrusted, agent-generated code safely has
always been the hard problem. WebAssembly
sandboxes with zero ambient authority, e.g. no
filesystem, network or system call, make it
feasible to let agents write and execute arbitrary
code without risking the host.
P2P infrastructure has quietly gotten reliable.
libp2p, GossipSub, CRDTs for state
synchronization, which are the building blocks
for decentralized agent networks exist as battle-
tested libraries. What Hyperspace built on top of
these is a novel application of proven distributed
systems primitives.
These let us combine components into a single
system where autonomous agents evolve solutions,
share them peer-to-peer, and compound
knowledge across domains.


---
*Page 9*


I haven’t seen elsewhere this specific combination
Hyperspace implements: evolutionary
optimization + gossip-based knowledge sharing +
cross-domain transfer + peer-to-peer execution.
The results from their live network suggest it’s a
bet worth examining closely.
In “Agentic SaaS Patterns” ebook, I break down seven
core architectural planes and include a sample
repository that demonstrates how these agentic
patterns work in real implementations.
You can grab it here: Agentic SaaS Patterns
Winning in 2026, packed with real-world
examples, architectures, and workflows you won’t
find anywhere else.
What Exactly Is Hyperspace Building?
Hyperspace is a distributed compute network
where autonomous agents run continuous
optimization loops across multiple domains.


---
*Page 10*


At its core, it’s three things bolted together:
1. An evolutionary computation engine: agents
propose mutations to solutions, evaluate them
against domain-specific metrics, keep
improvements, revert failures.
2. A peer-to-peer gossip network: agents share
discoveries with each other, propagate
successful mutations, and bootstrap new agents
from the network’s collective best.


---
*Page 11*


3. A cross-domain knowledge graph: observations,
experiments, and synthesized insights link
across different problem domains, enabling
transfer learning at the knowledge level rather
than the model level.
The system has three flagship features:
Autoswarms, Research DAGs, and Warps.
Autoswarms: Evolutionary Compute as a
Service
You can describe an optimization problem in plain
English and the network spins up a distributed
swarm to solve it:
hyperspace swarm new "optimize CSS themes for WCAG ac
What happens under the hood is a multi-step
pipeline:


---
*Page 12*


1. The system generates sandboxed experiment
code via LLM, this is the propose step.
2. It validates the code locally with multiple dry-
run rounds, catching obvious failures before
burning network resources.
3. It publishes the swarm definition to the P2P
network.
4. Peers discover the swarm and opt in.
5. Each participating agent runs mutate → evaluate
→ share cycles in a WASM sandbox.
6. Best strategies propagate across the network via
gossip.
7. Playbook curator uses an LLM to distill why
winning mutations work, so new joiners
bootstrap from accumulated wisdom instead of
starting cold.
That last point deserves emphasis because it solves
a real problem in evolutionary and reinforcement
learning systems: the cold start.


---
*Page 13*


When a new agent joins the swarm, it starts from
the network’s best-known solutions plus a human-
readable explanation of why those solutions work.
That’s different from just copying weights or
parameters, it gives the LLM-powered mutation
engine reasoning to build on.
Three built-in swarms are ready to run, and
anyone can create more. The swarm catalog uses
CRDTs for network-wide discovery, which is a solid
choice for eventually-consistent distributed state,
the same primitive that powers collaborative
editing in tools like Figma.
Research DAGs: Where It Gets Genuinely
Novel
If Autoswarms are the execution engine, the
Research DAG is the brain.
Every experiment across every domain feeds into a
shared directed acyclic graph, a knowledge graph


---
*Page 14*


where observations, experiments, and syntheses
link across domains.
Here’s the example:
When finance agents discover that momentum
factor pruning improves Sharpe ratio, that insight
propagates to search agents as a hypothesis:
“maybe pruning low-signal ranking features
improves NDCG too.”
And the reverse:
When ML agents find that extended training with
RMSNorm beats LayerNorm, skill-forging agents
pick up normalization patterns for text processing.
The DAG tracks lineage chains per domain with a
notation that looks like this:
ml:★0.99←1.05←1.23 | search:★0.40←0.39 | finance:★


---
*Page 15*


Each arrow represents an improvement step, and
the star marks the current best.
This gives you a full audit trail of how the network
arrived at any given result, i.e. which experiments
led to which improvements, and crucially, which
cross-domain transfers generated new hypotheses.
An AutoThinker loop sits on top of the DAG,
reading across all domains, synthesizing cross-
domain insights, generating new hypotheses, and
journaling discoveries.
DAG can hold hundreds of nodes across
observations, experiments, and syntheses, with
depth chains reaching 8+ levels.
The points I’m thinking about:
The architecture is exciting and treating
knowledge as a graph with cross-domain edges
and automated hypothesis generation can make


---
*Page 16*


multi-agent systems more than the sum of their
parts.
The scale is still modest with hundreds of nodes
across 5 domains is not a production knowledge
base but certainly getting there.
The open question is whether cross-domain
transfer generates genuinely useful hypotheses at
scale or whether it mostly produces noise that
agents waste cycles evaluating.
The early results suggest it works (the factor
pruning → feature pruning transfer is a real
insight), but I’d want to see this running for
months before drawing strong conclusions.
Warps: Declarative Agent Self-Mutation
Warps are the third piece, and they address a
problem that every agentic system builder has
faces: how do you configure and reconfigure what
an agent does without rewriting code?


---
*Page 17*


Warps are declarative configuration presets that
transform agent behavior:
The good part is custom warp forging from natural
language:
hyperspace warp forge "enable cron job that backs up
The LLM generates the configuration, you review,
then engage. And warps compose: power-mode +
add-research-causes + gpu-sentinel turns a gaming
PC into an autonomous research station that
protects its own hardware.


---
*Page 18*


Community warps propagate across the network
via gossip, creating an emergent marketplace of
agent configurations.
Engineering Insights About Agent
Systems
Insight 1: Gossip Protocols
Most multi-agent frameworks I’ve worked with use
centralized message brokers, e.g. Kafka, Redis
pub/sub, or direct API calls to share information
between agents.
Hyperspace uses GossipSub, the same protocol
that powers Ethereum’s beacon chain for block
propagation.
The advantage is that gossip protocols are
inherently fault-tolerant, don’t require a central
coordinator, and scale sublinearly with network
size.


---
*Page 19*


When an agent discovers something useful, it tells
its peers, who tell their peers, and the discovery
propagates exponentially.
For example, when one agent discovers something,
other peers can adopt it within hours. Nobody had
to configure a pub/sub topic or write a consumer.
Gossip protocols provide eventual consistency, not
immediate consistency.
If you need strict ordering of agent actions (e.g., a
multi-step approval workflow), gossip is the wrong
primitive but for knowledge sharing, e.g. “I found
something that works, you might want to try it”,
eventual consistency is desirable.
You want agents to independently evaluate shared
discoveries rather than blindly applying them in
lockstep.
Insight 2: The Propose-Evaluate-Share Loop


---
*Page 20*


Karpathy’s autoresearch loop is so simple it’s
almost dismissive but Hyperspace has now proven
it works across five distinct domains: ML training,
search ranking, quantitative finance, code
generation, and infrastructure optimization.
The universality of this pattern reminds me of how
the map-reduce paradigm turned out to apply far
beyond its original web indexing use case.
The propose-evaluate-share loop is essentially map-
reduce for optimization: the “map” is running
experiments, the “reduce” is selecting the best
results, and the “share” is distributing them for the
next round.
What makes this work in practice is the tight
coupling between mutation and evaluation.
Each cycle is fast (minutes, not hours), the
evaluation metric is quantitative (loss, NDCG,
Sharpe ratio, test pass rate), and the feedback loop
is closed (no human in the loop).


---
*Page 21*


Compare this to most agent workflows I’ve built,
where the feedback loop is open (wait for user
reaction), the evaluation is qualitative (did the user
like it?), and the cycle time is measured in days.
It’s not that every agent should use evolutionary
search but agents with tight, quantitative feedback
loops compound faster than agents with loose,
qualitative ones.
If you’re designing an agentic system and you can
define a numeric fitness function, you should
probably be running evolutionary loops rather
than prompt-engineering your way to better
outputs.
Insight 3: Cross-Domain Transfer via Knowledge
Graph
In the typical ML approach to transfer learning,
you share model weights between domains.
GPT learns language from the internet and
transfers that capability to domain-specific tasks.


---
*Page 22*


In the Hyperspace approach, you share structured
observations between domains.
The Research DAG shares the insight that “pruning
low-signal features improves performance,” and
lets each domain independently evaluate whether
that insight applies.
Knowledge-based transfer through a DAG is
explicit and auditable.
You can trace the lineage chain: finance agents
discovered factor pruning → AutoThinker
generated hypothesis for search → search agents
validated feature pruning improves NDCG, which
is a legible causal chain
Insight 4: Cold Start and Network Viability
The playbook curator pattern, where an LLM
distills why winning mutations work, so new
joiners bootstrap from accumulated wisdom,
solves what I consider the hardest problem in any


---
*Page 23*


distributed optimization system: getting new
participants to contribute value quickly.
In most P2P systems, new nodes are net
consumers before they become net producers.
BitTorrent solved this with optimistic unchoking.
Hyperspace solves it by giving new agents the best
solutions and the reasoning behind them.
A new agent joining the ML training swarm gets
“Kaiming initialization works because it scales the
variance of weight initialization by 2/fan_in, which
prevents signal degradation in ReLU networks.
Agents that combined this with RMSNorm saw
further improvements because…”
That reasoning context lets the LLM-powered
mutation engine make more informed proposals
from its very first cycle.


---
*Page 24*


It’s the difference between handing a new
developer your codebase versus handing them
your codebase plus the architecture decision
records that explain why things are built the way
they are.
Insight 5: WASM Sandboxing
Agent can decide to run rm -rf during a cleanup
task, or accidentally DDoS an internal API with its
“optimization” loop.
The decision to run all agent-generated code in
WASM sandboxes with zero ambient authority is
not just a safety measure, which makes the entire
autoskill system architecturally feasible.
The WASM sandbox provides no filesystem access,
network access or system calls. Agent-generated
JavaScript functions can process inputs and
produce outputs, but they can’t touch anything
else. This is a much stronger isolation guarantee
than Docker containers (which share a kernel) or


---
*Page 25*


even traditional VMs (which have a larger attack
surface).
Concluding Thoughts
Hyperspace has built a genuinely novel
architecture for distributed agentic intelligence,
demonstrated it works at small scale across
multiple domains, and shown that the evolutionary
+ gossip + cross-domain pattern produces real
results.
Whether it scales, whether the cross-domain
transfer remains useful at 100x the current node
count, and whether the decentralized model can
sustain participation.. Those are open questions
that will be answered by running it for months to
come.
And that is, to me, the most interesting sentence in
the entire project documentation: “Let’s see what
happens when this runs for weeks instead of
hours.” I genuinely want to know.


---
*Page 26*


I’ll leave you with a question: For those running
evolutionary or genetic optimization loops: how
do you handle premature convergence in
distributed settings?
Bonus Articles
7 Local LLM Families To Replace
Cl d /C d (f d t k )
Open-source model families you can run
l ll th t d li i l ld
agentnativedev.medium.com
I Ignored 30+ OpenClaw Alternatives Until
O F
Fully open-source Agent Operating System,
itt ti l i R t hi i i l
agentnativedev.medium.com
Garry Tan’s gstack: Running Claude Like an
E i i T
Eight opinionated slash commands you
i t ll i t Cl d C d h ith it
agentnativedev.medium.com
Qwen 3.5 35B-A3B: Why Your $800 GPU
J t B F ti Cl AI
I have been running local models for a while
d I th ht I h d tt d
agentnativedev.medium.com


---
*Page 27*


GET SH*T DONE: Meta-prompting and
S d i D l t f Cl d C d
GSD (“Get Shit Done”) aims to solve context
t th lit d d ti th d l’
agentnativedev.medium.com
OpenClaw Memory Systems That Don’t
F t QMD M 0 C Ob idi
If your agent has ever randomly ignored a
d i i k t ld it it’ t
agentnativedev.medium.com
Agentic Ai AI Agent Andrej Karpathy
Multi Agent Systems Distributed Architecture
Written by Agent Native
Following
7.8K followers · 0 following
Hyperscalers, open-source developments, startup
activity and the emerging enterprise patterns
shaping agentic AI.


---
*Page 28*


Responses (2)
To respond to this story,
get the free Medium app.
Tanu
2 days ago
This is fascinating—especially the emergent convergence without
domain-specific training. It really shows how collective learning +
distributed experimentation can lead to surprisingly robust strategies.
Feels like a strong signal that agentic systems might generalize better
than we expect across domains.
Sebastian Buzdugan
6 days ago
love the emergent risk-parity convergence, but curious how much of this
🤔
is true generality vs overfitting to a specific backtest regime
More from Agent Native


---
*Page 29*


Agent Native Agent Native
KubeClaw: OpenClaw $1M Agentic Fellowship
f Ad lt
The most important change in
Secure defaults, pinned
ti AI i th
i di t bl d
1d ago Mar 18
Agent Native Agent Native
Why LLMs Break When Agentic Identity in
Y Add V i AWS A GCP d
Voice layer is a first-class Biggest blind spot in most
hit t l d it t ’ ti hit t i
5d ago Mar 6
See all from Agent Native


---
*Page 30*


Recommended from Medium
☕
Han HELOIR YAN, Ph.D. In by
Towards Deep L… Sumit Pa…
What Cursor Didn’t Say
YC’s CEO Open-
Ab t C 2
S d t k It
The benchmark was
YC’s CEO open-sourced his AI
i ti Th i i
di t 20K t i 6
4d ago Mar 18


---
*Page 31*


Reza Rezvani In by
Generative AI Adham Khaled
Claude Code Channels:
Perplexity Computer
Th N ti O Cl
J t Did i 7 Mi t
A complete setup guide for
Perplexity Computer
T l d Di d it
di t 19 AI d l f
4d ago Mar 16
In by Reliable Data Engineering
Level Up Coding Yanli Liu
The Claude Certified
5 Agent Frameworks.
A hit t I H
O P tt W
AutoGen vs. LangGraph vs.
C AI B t D ’
Mar 16 Mar 18
See more recommendations