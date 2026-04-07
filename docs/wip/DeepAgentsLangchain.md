# DeepAgentsLangchain

*Converted from: DeepAgentsLangchain.PDF*



---
*Page 1*


Open in app
Search Write
Pub Crawl is happening this week! Sign up to join us!
Towards AI
Member-only story
LangChain Deep
Agents: The Open-
Source Claude Code
Alternative That Works
With Any Model
Planning, filesystem access, subagents, and
context management in a two-line install. MIT
licensed. 9.9K GitHub stars in five hours
Mandar Karhade, MD. PhD. Follow 8 min read · 1 day ago
203 3


---
*Page 2*


TLDR
LangChain released Deep Agents, an agent
harness that replicates the core architecture of
Claude Code: planning tool, filesystem access,
subagent spawning, context management.
Provider agnostic; any LangChain-compatible
model. Swap providers without rebuilding.
Two lines to start: pip install deepagents, then
create_deep_agent(). Built on LangGraph for
streaming, persistence, and checkpointing.
The CLI adds web search, remote sandboxes,
persistent memory, custom skills, and human-
in-the-loop approval.
9.9K GitHub stars in five hours.
Friends link for everyone: Follow the author,
publication, and clap. Join Medium to support
other writers too! Cheers


---
*Page 3*


9,900 GitHub stars. Five hours old.
That’s not hype. That’s a market screaming for
something it didn’t have.
LangChain just released Deep Agents, and the
pitch is direct: this is the architecture that makes
Claude Code work, extracted, generalized, open-
sourced, and decoupled from any single model
provider. MIT licensed. Free. Works with anything
that supports tool calling.
From the README.md, in their own words: “This
project was primarily inspired by Claude Code, and
initially was largely an attempt to see what made
Claude Code general purpose, and make it even
more so.”
They’re not hiding it. They’re not pretending this
came from nowhere. They studied what works,
identified why it works, and made it available to
everyone.


---
*Page 4*


Another model drops! Except this time it’s not a
model. It’s the scaffolding that turns any model
into a deep agent.
Deep Waters
Why This Matters: The “Deep” Problem
Most agent frameworks run a simple loop: receive
input, call a tool, return output, repeat. This works


---
*Page 5*


for short tasks. It falls apart the moment you need
an agent to plan across multiple steps, manage
growing context, delegate subtasks, or work on
anything that takes longer than a single
conversation turn.
LangChain calls these “shallow” agents. And
they’re right. The dominant agent pattern is also
the simplest, and simplicity has a ceiling.
Claude Code broke through that ceiling not with a
better model (though the model matters) but with
four architectural choices that most agent
frameworks don’t make:
1. A planning tool that keeps the agent on track
over long-horizon tasks
2. Filesystem access for context offloading and
shared workspace between agents
3. Subagent spawning for context isolation and
parallel work


---
*Page 6*


4. A detailed system prompt that teaches the agent
how to behave in specific situations
The fascinating detail from LangChain’s blog:
Claude Code’s planning tool is essentially a no-op.
It doesn’t execute anything. It’s a context
engineering strategy. The agent writes a todo list,
tracks progress against it, and stays focused over
longer horizons. The tool itself does nothing; the
act of planning is what matters.
That insight alone is worth the repo.


---
*Page 7*


What Ships in the Box?
Deep Agents is not a framework. LangChain is the
framework. Deep Agents is what they call an
“agent harness,” a batteries-included wrapper that
gives any LangChain-compatible model the
capabilities that make Claude Code effective.


---
*Page 8*


Planning and task decomposition. A built-in
write_todos tool enables the agent to break
complex tasks into discrete steps, track progress,
and adapt plans as new information emerges.
Same pattern as Claude Code, generalized.
Filesystem access. ls, read_file, write_file,
edit_file, glob, grep. Full codebase navigation.
The filesystem isn't just for reading and writing
code; it's the agent's working memory. When
context grows too large for the conversation
window, the agent offloads to files. When
subagents need to share state, they use the
filesystem as a collaboration surface.
Pluggable filesystem backends. This is where it
gets interesting for production use. The virtual
filesystem supports in-memory state, local disk,
LangGraph store for cross-thread persistence,
sandboxes (Modal, Daytona, Deno) for isolated
code execution, or custom backends you build


---
*Page 9*


yourself. Swap backends without changing agent
logic.
Subagent spawning. A built-in task tool lets the
agent spawn specialized subagents with their own
context windows. The main agent stays clean while
subagents go deep on specific tasks. No context
pollution. Parallel execution.
Shell execution. Run commands with sandboxing.
Build, test, deploy from the agent.
Long-term memory. Persistent memory across
threads using LangGraph’s Memory Store. The
agent remembers previous conversations and
carries context forward.
Context management. Auto-summarization when
conversations get long. Large outputs saved to
files. The context window management problem
that every long-running agent hits, solved at the
harness level.


---
*Page 10*


Two lines to start:
python
# pip install -qU deepagents
from deepagents import create_deep_agent
def get_weather(city: str) -> str:
"""Get weather for a given city."""
return f"It's always sunny in {city}!"
agent = create_deep_agent(
tools=[get_weather],
system_prompt="You are a helpful assistant",
)
# Run the agent
agent.invoke(
{"messages": [{"role": "user", "content": "what i
)
That returns a compiled LangGraph graph.
Streaming, Studio, checkpointers, persistence; all
LangGraph features work out of the box.
The Provider-Agnostic Part Is the Real
Story


---
*Page 11*


Claude Code is excellent. Genuinely. But it is
locked to Anthropic. If you want the Claude Code
experience with a different model, or if you want
to run evaluations across providers, or if your
organization has a policy that requires multi-
provider support, you’re out of luck.
Deep Agents fixes that. Any of the 100+ LangChain-
compatible model providers. The agent
architecture stays the same. The tools stay the
same. The planning, filesystem, subagent, and
context management layers stay the same.
For those who cant afford the subscription to
Claude Max or who need to run the same agent on
multiple providers for comparison or compliance,
this is the unlock.
The CLI: Where It Gets Practical
The Deep Agents SDK is the library. The CLI is the
terminal experience built on top of it.


---
*Page 12*


Install script for linux
curl -LsSf https://raw.githubusercontent.com/langchai
The CLI adds web search, remote sandboxes,
persistent memory, human-in-the-loop approval,
and custom skills. It’s the interactive coding agent
experience, but model-agnostic and extensible.
MCP is supported via langchain-mcp-adapters,
which means any MCP server you've already
configured (Google Workspace, Notion, Slack,
whatever) works with Deep Agents out of the box.
How Does It Compare to Claude Code and
Codex?
LangChain published a comparison page
themselves
(docs.langchain.com/oss/python/deepagents/comp


---
*Page 13*


arison), and it’s refreshingly straightforward.
Here’s the reality:
vs. Claude Agent SDK
Claude Agent SDK is first-class for Claude models.
It has tighter integration with Anthropic’s
infrastructure, native permission models, and
session management that Deep Agents doesn’t
replicate. If you are building exclusively on Claude,
the Agent SDK gives you things Deep Agents can’t.
But if you need model flexibility, evaluation across
providers, or independence from a single vendor,
Deep Agents is the answer.
vs. Codex SDK
Similar story. Codex SDK is optimized for OpenAI.
Deep Agents trades that optimization for
universality.
Where Deep Agents wins


---
*Page 14*


Model flexibility (swap without rebuilding),
pluggable filesystem backends (in-memory to
sandboxes), long-term memory across threads,
and the ability to deploy via LangSmith or self-
host.
Where Deep Agents doesn’t win
Maturity. Claude Code has been in production for
over a year. Deep Agents just shipped. The system
prompts, the tool behaviors, the edge case
handling; all of that is refined through millions of
real interactions in Claude Code. Deep Agents has
the architecture but not the mileage.
The “trust the LLM” philosophy is also worth
flagging. From the README: “Deep Agents follows
a ‘trust the LLM’ model. The agent can do anything
its tools allow. Enforce boundaries at the
tool/sandbox level, not by expecting the model to
self-police.” This is architecturally clean but puts
the security burden on whoever configures the
tools and sandboxes. If you deploy this with broad


---
*Page 15*


filesystem access and no sandbox, your agent can
do anything. That is a feature and a risk, and you
need to decide which it is for your use case.
Why 9,900 Stars in Five Hours? Because
the Demand Was Already There.
9,900 stars in five hours is not about LangChain’s
marketing. It’s about unmet demand. And also it
already existed on github just that it became MIT
licensed. There is no MOAT for Langchain to
maintain.
The agent ecosystem has been fractured along
provider lines. Want Claude Code? You need
Anthropic. Want Codex? You need OpenAI. Want
Antigravity? You need Google. Every vendor builds
an excellent agent experience that only works with
their models, creating lock-in at the agent layer on
top of the model layer.


---
*Page 16*


Developers have been asking for
exactly what Deep Agents
provides: the agent architecture,
decoupled from the model.
The ability to build once and swap providers. The
ability to evaluate which model actually performs
best for their specific agentic workloads without
rebuilding the entire stack.
LangChain has had a complicated reputation.
Early LangChain (the 0.x era) was notorious for
abstraction overhead, dependency bloat, and an
API that broke with every minor release. A lot of
developers swore it off.
Deep Agents is a different product. It’s built on
LangGraph, which is the production runtime that
emerged from the lessons of early LangChain. It’s a
harness, not a framework. It’s opinionated about
architecture (planning, filesystem, subagents) but


---
*Page 17*


unopinionated about model, provider, and
deployment.
The tech world buzzes with excitement every time
an open-source project threatens to commoditize a
proprietary advantage. This is one of those
moments. The core architectural patterns that
make Claude Code, Codex, and similar tools
effective are now MIT-licensed, provider-agnostic,
and two lines of Python away.
This Is What Open Source Is Supposed to
Look Like
Deep Agents is a genuine contribution to the open-
source ecosystem. LangChain studied what works,
named their inspiration explicitly, and built
something that democratizes the architecture
without pretending to replace the
implementations.


---
*Page 18*


Is it as good as Claude Code today? No. Claude
Code has a year of production refinement, a model
that was partially trained for the agentic loop, and
Anthropic’s entire engineering team behind it.
Deep Agents has the skeleton. The muscle and the
scar tissue come with time and adoption. But it is
tinkerer’s paradise. If it comes down to it, I would
rely on my own langgraph as my core go-to option
but definitely dabble into deep agents to access
filesystem framework.
But the skeleton is the hard part. Planning,
filesystem, subagents, context management,
provider abstraction, pluggable backends,
persistent memory. That’s not a weekend hack.
That’s a considered architectural choice that gives
the open-source community a foundation to build
on.
If you’re building agents professionally, install it
today. Run it with your model of choice. Compare


---
*Page 19*


it against Claude Code on the same tasks. File
issues. Contribute tools. Push the edges.
This is what open source is supposed to look like.
Someone builds something excellent and
proprietary. Someone else studies why it’s
excellent, extracts the principles, and makes them
available to everyone. The original gets credit. The
ecosystem gets options.
Everybody wins.
This is my perspective. You should do what you are
comfortable with. But if you’ve been waiting for
the Claude Code architecture to become model-
agnostic and MIT-licensed, the wait is over. Two
lines. Any model. Free*.
If you have read it until this point, Thank you! You
are a hero (and a Nerd ❤)! I try to keep my readers


---
*Page 20*


up to date with “interesting happenings in the AI
🔔 🔔
world,” so please clap | follow | Subscribe
Agentic Ai AI Agent LLM Artificial Intelligence
Open Source
Published in Towards AI
Following
114K followers · Last published just now
We build Enterprise AI. We teach what we learn. Join
100K+ AI practitioners on Towards AI Academy. Free:
6-day Agentic AI Engineering Email Guide:
https://email-course.towardsai.net/
Written by Mandar Karhade, MD.
Follow
PhD.
4.3K followers · 141 following
Life Sciences AI/ML/GenAI advisor
Responses (3)


---
*Page 21*


To respond to this story,
get the free Medium app.
Sebastian Buzdugan
20 hours ago
super curious how this behaves with smaller local models, feels like the
🤔
planning overhead might dwarf any gains for lightweight setups
9 1 reply
Ken Geis
4 hours ago
just released
four months ago
2 1 reply
Colin Griffiths
17 hours ago
Nerd or not, I've read to the end. When I programmed, Python was on the
horizon. Most of what you describe is gibberish to me. How, for example,
do I use Python? How do I use curl, when my programming experience is
limited to what I can do within… more


---
*Page 22*


More from Mandar Karhade, MD. PhD. and
Towards AI
In by In by
AI Adva… Mandar Karhade,… Towards AI Divy Yadav
Why Doc-to-LoRA is A Beginner’s Guide to
th E d f th C t t P d ti G d
We are now predicting Six Agentic RAG patterns
i ht i i l f d l i d ith l d ti
Mar 4 Feb 10
In by In by
Towards… Fabio Yáñez Ro… Level Up … Mandar Karhad…
Why LLMs Fail at GLiNER v2 60M: A
K l d G h M d l F Ed AI!
From Entity Extraction to Scaling GLiNER to 60M
G h A t ti Wh t P t ith t th H


---
*Page 23*


Jan 15 Feb 24
See all from Mandar Karhade, MD. PhD. See all from Towards AI
Recommended from Medium
In by Yusuf Baykaloğlu
Towards AI Divy Yadav
Multi-Agent Systems:
A Beginner’s Guide to
O h t ti AI
P d ti G d
A Deep Dive into Agent
Six Agentic RAG patterns
A hit t W kfl d
l i d ith l d ti
Feb 10 Jan 12


---
*Page 24*


Rost Glukhov In by
Spillwave Solu… Rick Hight…
Best LLMs for Ollama
Agent RuleZ: A
16GB VRAM GPU
D t i i ti P li
Running large language
Human-readable YAML rules
d l l ll i
th t bl k f ti
Feb 21 Feb 19
In by In by
Google Cloud - C… Pradeep… Artificial INTEL-lig… Fabio …
The Agentic Web is AI Frankenstein is alive
H H W bMCP t 4
Web development has The Modular Superbrain:
hi t i ll f d th I id IBM’ G it 4 0 d
Feb 22 Feb 23
See more recommendations