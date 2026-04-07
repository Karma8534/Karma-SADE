# New agent framework matches human-engineered AI systems — and adds zero inference cost to deploy _ VentureBeat

*Converted from: New agent framework matches human-engineered AI systems — and adds zero inference cost to deploy _ VentureBeat.PDF*



---
*Page 1*


All Posts
Featured
New agent framework matches human-
engineered AI systems — and adds zero
inference cost to deploy
Ben Dickson
February 18, 2026
Image credit: VentureBeat with ChatGPT


---
*Page 2*


Agents built on top of today's models often break with simple changes — a new library, a
workflow modification — and require a human engineer to fix it. That's one of the most
persistent challenges in deploying AI for the enterprise: creating agents that can adapt to
dynamic environments without constant hand-holding. While today's models are powerful,
they are largely static.
To address this, researchers at the University of California, Santa Barbara have developed
Group-Evolving Agents (GEA), a new framework that enables groups of AI agents to evolve
together, sharing experiences and reusing their innovations to autonomously improve over
time.


---
*Page 3*


In experiments on complex coding and software engineering tasks, GEA substantially
outperformed existing self-improving frameworks. Perhaps most notably for enterprise
decision-makers, the system autonomously evolved agents that matched or exceeded the
performance of frameworks painstakingly designed by human experts.
The limitations of 'lone wolf' evolution
Most existing agentic AI systems rely on fixed architectures designed by engineers. These
systems often struggle to move beyond the capability boundaries imposed by their initial
designs.
To solve this, researchers have long sought to create self-evolving agents that can
autonomously modify their own code and structure to overcome their initial limits. This
capability is essential for handling open-ended environments where the agent must
continuously explore new solutions.


---
*Page 4*


However, current approaches to self-evolution have a major structural flaw. As the
researchers note in their paper, most systems are inspired by biological evolution and are
designed around "individual-centric" processes. These methods typically use a tree-
structured approach: a single "parent" agent is selected to produce offspring, creating distinct
evolutionary branches that remain strictly isolated from one another.
Classic self-evolving agent structure (source: arXiv)


---
*Page 5*


This isolation creates a silo effect. An agent in one branch cannot access the data, tools, or
workflows discovered by an agent in a parallel branch. If a specific lineage fails to be selected
for the next generation, any valuable discovery made by that agent, such as a novel
debugging tool or a more efficient testing workflow, dies out with it.
In their paper, the researchers question the necessity of adhering to this biological metaphor.
"AI agents are not biological individuals," they argue. "Why should their evolution remain
constrained by biological paradigms?"
The collective intelligence of Group-Evolving
Agents
GEA shifts the paradigm by treating a group of agents, rather than an individual, as the
fundamental unit of evolution.
The process begins by selecting a group of parent agents from an existing archive. To ensure
a healthy mix of stability and innovation, GEA selects these agents based on a combined
score of performance (competence in solving tasks) and novelty (how distinct their
capabilities are from others).
Group-evolving agent (GEA) (source: arXiv)
Unlike traditional systems where an agent only learns from its direct parent, GEA creates a
shared pool of collective experience. This pool contains the evolutionary traces from all
members of the parent group, including code modifications, successful solutions to tasks,


---
*Page 6*


and tool invocation histories. Every agent in the group gains access to this collective history,
allowing them to learn from the breakthroughs and mistakes of their peers.
A “Reflection Module,” powered by a large language model, analyzes this collective history to
identify group-wide patterns. For instance, if one agent discovers a high-performing
debugging tool while another perfects a testing workflow, the system extracts both insights.
Based on this analysis, the system generates high-level "evolution directives" that guide the
creation of the child group. This ensures the next generation possesses the combined
strengths of all their parents, rather than just the traits of a single lineage.
How GEA chooses and shares evolution traits (source: arXiv)


---
*Page 7*


However, this hive-mind approach works best when success is objective, such as in coding
tasks. "For less deterministic domains (e.g., creative generation), evaluation signals are
weaker," Zhaotian Weng and Xin Eric Wang, co-authors of the paper, told VentureBeat in
written comments. "Blindly sharing outputs and experiences may introduce low-quality
experiences that act as noise. This suggests the need for stronger experience filtering
mechanisms" for subjective tasks.
GEA in action
The researchers tested GEA against the current state-of-the-art self-evolving baseline, the
Darwin Godel Machine (DGM), on two rigorous benchmarks. The results demonstrated a
massive leap in capability without increasing the number of agents used.
This collaborative approach also makes the system more robust against failure. In their
experiments, the researchers intentionally broke agents by manually injecting bugs into their
implementations. GEA was able to repair these critical bugs in an average of 1.4 iterations,
while the baseline took 5 iterations. The system effectively leverages the "healthy" members
of the group to diagnose and patch the compromised ones.
On SWE-bench Verified, a benchmark consisting of real GitHub issues including bugs and
feature requests, GEA achieved a 71.0% success rate, compared to the baseline's 56.7%. This
translates to a significant boost in autonomous engineering throughput, meaning the agents
are far more capable of handling real-world software maintenance. Similarly, on Polyglot,
which tests code generation across diverse programming languages, GEA achieved 88.3%
against the baseline's 68.3%, indicating high adaptability to different tech stacks.
GEA vs Darwin-Godel Machine (DGM) (source: arXiv)


---
*Page 8*


For enterprise R&D teams, the most critical finding is that GEA allows AI to design itself as
effectively as human engineers. On SWE-bench, GEA’s 71.0% success rate effectively matches
the performance of OpenHands, the top human-designed open-source framework. On
Polyglot, GEA significantly outperformed Aider, a popular coding assistant, which achieved
52.0%. This suggests that organizations may eventually reduce their reliance on large teams
of prompt engineers to tweak agent frameworks, as the agents can meta-learn these
optimizations autonomously.
This efficiency extends to cost management. "GEA is explicitly a two-stage system: (1) agent
evolution, then (2) inference/deployment," the researchers said. "After evolution, you deploy a
single evolved agent... so enterprise inference cost is essentially unchanged versus a standard
single-agent setup."
The success of GEA stems largely from its ability to consolidate improvements. The
researchers tracked specific innovations invented by the agents during the evolutionary
process. In the baseline approach, valuable tools often appeared in isolated branches but
failed to propagate because those specific lineages ended. In GEA, the shared experience
model ensured these tools were adopted by the best-performing agents. The top GEA agent
integrated traits from 17 unique ancestors (representing 28% of the population) whereas the
best baseline agent integrated traits from only 9. In effect, GEA creates a "super-employee"
that possesses the combined best practices of the entire group.
"A GEA-inspired workflow in production would allow agents to first attempt a few
independent fixes when failures occur," the researchers explained regarding this self-healing
capability. "A reflection agent (typically powered by a strong foundation model) can then
summarize the outcomes... and guide a more comprehensive system update."
Furthermore, the improvements discovered by GEA are not tied to a specific underlying
model. Agents evolved using one model, such as Claude, maintained their performance gains
even when the underlying engine was swapped to another model family, such as GPT-5.1 or
GPT-o3-mini. This transferability offers enterprises the flexibility to switch model providers
without losing the custom architectural optimizations their agents have learned.
For industries with strict compliance requirements, the idea of self-modifying code might
sound risky. To address this, the authors said: "We expect enterprise deployments to include
non-evolvable guardrails, such as sandboxed execution, policy constraints, and verification
layers."
While the researchers plan to release the official code soon, developers can already begin
implementing the GEA architecture conceptually on top of existing agent frameworks. The
system requires three key additions to a standard agent stack: an “experience archive” to
store evolutionary traces, a “reflection module” to analyze group patterns, and an “updating
module” that allows the agent to modify its own code based on those insights.


---
*Page 9*


Looking ahead, the framework could democratize advanced agent development. "One
promising direction is hybrid evolution pipelines," the researchers said, "where smaller
models explore early to accumulate diverse experiences, and stronger models later guide
evolution using those experiences."
Subscribe to get latest news!
Deep insights for enterprise AI, data, and security leaders
VB Daily AI Weekly AGI Weekly Security Weekly
Data Infrastructure Weekly VB Events All of them
Enter Your Email
By submitting your email, you agree to ourTermsandPrivacy Notice.
Get updates


---
*Page 10*


More


---
*Page 11*


Anthropic's Sonnet 4.6 matches flagship AI performance at one-
fifth the cost, accelerating enterprise adoption
The model is a full upgrade across coding, computer use, long-context reasoning, agent
planning, knowledge work, and design. It features a 1M token context window in beta. It is
now the default model in claude.ai and Claude Cowork, and pricing holds steady at $3/$15 pe…
Michael Nuñez
February 17, 2026
Qodo 2.1 solves your coding agents' 'amnesia' problem, giving
them an 11% precision boost
As AI-powered coding tools flood the market, a critical weakness has emerged: by default, as
with most LLM chat sessions, they are temporary — as soon as you close a session and start a
new one, the tool forgets everything you were just working on.
Carl Franzen
February 17, 2026


---
*Page 12*


Nvidia, Groq and the limestone race to real-time AI: Why
enterprises win or lose here
From miles away across the desert, the Great Pyramid looks like a perfect, smooth geometry
— a sleek triangle pointing to the stars. Stand at the base, however, and the illusion of
smoothness vanishes. You see massive, jagged blocks of limestone. It is not a slope; it is a…
Andrew Filev, Zencoder
February 16, 2026


---
*Page 13*


AI agents turned Super Bowl viewers into one high-IQ team — now
imagine this in the enterprise
The average Fortune 1000 company has more than 30,000 employees and engineering, sales
and marketing teams with hundreds of members. Equally large teams exist in government,
science and defense organizations. And yet, research shows that the ideal size for a…
Louis Rosenberg, Unanimous A.I.
February 13, 2026


---
*Page 14*


Nvidia’s new technique cuts LLM reasoning costs by 8x without
losing accuracy
Nvidia researchers developed dynamic memory sparsification (DMS), a technique that compresses
the KV cache in large language models by up to 8x while maintaining reasoning accuracy — and it
can be retrofitted onto existing models in hours.
Ben Dickson
February 12, 2026


---
*Page 15*


Anthropic’s Claude Cowork finally lands on Windows — and it
wants to automate your workday
The Windows launch arrives with what Anthropic calls "full feature parity" with the macOS
version: file access, multi-step task execution, plugins, and Model Context Protocol (MCP)
connectors for integrating external services. Users can now also set global and folder-speci…
Michael Nuñez
February 11, 2026


---
*Page 16*


MIT's new fine-tuning method lets LLMs learn new skills without
losing old ones
MIT researchers unveil a new fine-tuning method that lets enterprises consolidate their "model zoos"
into a single, continuously learning agent.
Ben Dickson
February 11, 2026


---
*Page 17*


NanoClaw solves one of OpenClaw's biggest security issues — and
it's already powering the creator's biz
The rapid viral adoption of Austrian developer Peter Steinberger's open source AI assistant
OpenClaw in recent weeks has sent enterprises and indie developers into a tizzy.
Carl Franzen
February 11, 2026


---
*Page 18*


PARTNER CONTENT
Why enterprise IT operations are breaking — and how AgenticOps
fixes them
Presented by Cisco
VB Staff
February 11, 2026


---
*Page 19*


OpenAI upgrades its Responses API to support agent skills and a
complete terminal shell
Until recently, the practice of building AI agents has been a bit like training a long-distance
runner with a thirty-second memory.
Carl Franzen
February 10, 2026


---
*Page 20*


What AI builders can learn from fraud models that run in 300
milliseconds
Mastercard's Decision Intelligence Pro uses recurrent neural networks to analyze 160 billion yearly
transactions in under 50 milliseconds, delivering precise fraud risk scores at 70,000 transactions per
second during peak periods.
Taryn Plumb
February 10, 2026


---
*Page 21*


PARTNER CONTENT
Is agentic AI ready to reshape Global Business Services?
Presented by EdgeVerve
N. Shashidar, EdgeVerve
February 10, 2026
Press Releases
Contact Us
Advertise
Share a News Tip


---
*Page 22*


Contribute
Privacy Policy
Terms of Service
Consent Preferences
Do not sell my personal info
© 2026 VentureBeat. All rights reserved.