# ForgetMCP

*Converted from: ForgetMCP.PDF*



---
*Page 1*


Read distraction-free on Substack
Forget MCP, Bash Is All You Need
DEAD NEURONS
FEB 17, 2026
LLMs need tools. They can reason, write prose, and generate code, but they can’t do
anything in the real world without some way to reach out and touch it. The industry
answer to this problem has been MCP, the Model Context Protocol, and it’s
everywhere: thousands of servers, every major framework, a growing ecosystem of
integrations. It’s becoming the default answer to “how do I give my model access to
things.”
There’s a contradiction hiding in plain sight, though. The most successful AI agent
aren’t built on it, and the reason goes deeper than most people realise: it’s not just t
bash is a better tool interface, it’s that the operating system itself is already the agen
runtime MCP is trying to build.
MCP keeps reinventing the operating system
MCP has had a rough year, not because it failed, but because it keeps needing to be
fixed. What’s interesting is where the fixes keep landing.
The first problem was the context window tax. MCP requires tool definitions to be
loaded into the model’s context so it knows what’s available, and a typical five-serve
setup consumes around 55,000 tokens in tool schemas before the conversation even
starts. Anthropic’s own engineering team reported seeing setups that consumed
134,000 tokens in tool metadata alone, which at Claude’s current pricing works out
roughly $0.40 in input tokens per conversation just for tool definitions, before the u
says a word. 4 1


---
*Page 2*


The fix was Tool Search Tool and deferred loading: instead of loading every tool
definition upfront, discover tools on demand when the model actually needs them.
This is sensible engineering. It’s also just... running a binary when you need it. You
don’t load grep’s man page into memory at boot; you run grep when you need to gre
and Unix figured this out decades ago. What MCP reinvented here wasn’t a shell
feature, it was process invocation: the OS’s ability to find and launch a program on
demand without preloading anything.
The second problem was that every MCP tool call requires a full model inference pa
You can’t pipe one tool’s output into another, can’t loop over results without the mo
reasoning about each iteration, can’t run a workflow in a cron job. A five-step
workflow means five inference passes, each burning tokens on both the reasoning a
the response. The fix was Programmatic Tool Calling, which lets Claude write Pyth
code that orchestrates multiple tool calls in a sandbox and returns only the final res
to context. Anthropic’s own blog post explains why: traditional tool calling was “bo
slow and error-prone.” Their solution was to let the model write code that calls tool
directly, which is what shell scripts have done since 1977, and what the kernel has
always done: manage inter-process communication so that programs can pass data
each other without a human in the loop.
Each of these fixes is good engineering, and I’m not questioning the competence of
people building them. What I’m pointing out is the trajectory: zoom out and you ca
see MCP slowly reinventing the operating system, one feature at a time. Deferred
loading is process invocation, programmatic tool calling is IPC and pipelines, tool
schemas are man pages, and MCP servers are daemons. The protocol isn’t convergi
on bash specifically; it’s converging on POSIX, the entire model of how programs
discover each other, communicate, compose, and run.
Linux is already the agent runtime


---
*Page 3*


Once you see MCP’s trajectory as OS-convergent, the deeper question becomes
obvious: what would an ideal “operating system for AI agents” actually need to
provide? You’d want process discovery and invocation so you can find a tool and run
process isolation so one tool can’t corrupt another, a universal communication
protocol between tools, composition primitives for chaining tools together, and the
the usual suspects of resource management, permissions, scheduling, and
configuration.
That’s not a wishlist for some future agent framework. That’s a description of Linux
where every one of those capabilities already exists, battle-tested for decades, in the
operating system MCP is running on top of.
Stdin, stdout, and stderr give you a universal communication protocol between any
two processes. Pipes give you composition. Permissions give you access control. Cr
gives you scheduling, signals give you lifecycle management, environment variables
give you configuration, and package managers give you discovery and installation.
These aren’t features that someone bolted onto the shell; they’re primitives provide
by the kernel and the OS layer around it, and they’ve been stable for decades becaus
the design was right the first time.
Bash is the interface to all of this, and it’s a good one, but the power isn’t in bash.
curl api.example.com/data | jq '.results[] | .name
When you pipe
you’re not using a clever shell trick; you’re using the kernel’s process model, its IPC
primitives, and its file descriptor system. Data flows between isolated processes
without entering a context window because the operating system manages the data
flow, which is exactly what operating systems are for.
tool_a | tool_b | tool_c
Composition is free because the OS provides it.
chains three tools with the output of each feeding the next, with no inference betwe
stages, no tokens burned, and no protocol overhead. At current API pricing a five-s
pipeline that costs fractions of a cent in bash can cost dollars when each step requir
a model inference pass.


---
*Page 4*


The ecosystem is already there too. Tools like jq, curl, git, docker, kubectl, aws, gh,
ffmpeg, imagemagick, and pandoc represent a tiny fraction of the hundreds of
thousands of CLI tools that exist on every machine, tested for decades, maintained
communities that aren’t going anywhere. Every one of these is immediately availabl
to an LLM with bash access, with no adapter needed, no SDK, and no server proces
because Linux already defines how applications install, register themselves, and get
invoked. That’s what a runtime does.
The real advantage, though, is scriptability without an LLM. A bash pipeline can ru
in CI, in cron, on a Raspberry Pi, and it’s deterministic, fast, and free. Once the mod
figures out the right sequence of commands, you can save it as a script and never pa
for inference again, because the OS is the runtime, not the model.
The evidence is shipping
This isn’t a theoretical argument. The three most successful agent products of the p
year all converged on the same architecture, and it’s not MCP.
Claude Code is Anthropic’s most successful product launch, a terminal-based codin
agent that gives Claude a bash tool and lets it write shell commands, compose CLI
tools, and orchestrate via code. MCP connectors are there for integrations, but they
the accessory, not the engine. Strip out MCP and you still have a great agent; strip o
bash and you have nothing. Nobody says “Claude Code is amazing because of its M
support.” They say it’s amazing because it can just do things on your machine, and
what “on your machine” really means is that it has access to the operating system.
Cowork is what happened when Anthropic noticed that developers were using Clau
Code for non-coding work: vacation research, building slide decks, cleaning up ema
recovering wedding photos from a hard drive. People were forcing a developer tool
do general-purpose work because the underlying pattern, an LLM with OS access,
turned out to be the best agent architecture anyone had shipped. So Anthropic


---
*Page 5*


wrapped the same bash-lineage architecture in a GUI for non-technical users, wher
you point it at a folder, describe what you need, and Claude reads, edits, and creates
files autonomously. A team of four engineers built it in ten days, using Claude Code
itself. The foundation is code execution and file system access, not MCP tool calls.
OpenClaw, powered by Mario Zechner’s Pi agent, went from zero to 145,000 GitHub
stars in a single week. Pi has four tools: Read, Write, Edit, Bash. That’s the entire
agent, and there is no MCP support, which isn’t a lazy omission. As Armin Ronache
wrote, it’s a deliberate philosophical choice: if the agent needs to do something new
doesn’t download an extension or install a plugin, it writes the code itself. Need
rg gh
ripgrep? Run via bash. Need to search GitHub? Use via bash. The model read
documentation and figures out CLI tools on its own, and Pi’s system prompt is roug
ten lines long, compared to the multi-thousand-token prompts needed when you ha
to describe dozens of MCP tool schemas upfront.
It’s worth pausing on Pi’s four tools for a moment, because Read, Write, Edit, and B
aren’t really “agent tools” in the way MCP thinks about them. They’re system calls.
is a thin wrapper that gives a model access to the operating system’s own primitives
and that turned out to be enough for 145,000 stars.
Three products, three teams, three independent conclusions. Claude Code has the O
as its foundation with MCP bolted on, Cowork inherits that foundation, and
OpenClaw drops MCP entirely. Each step takes the agent further from the protocol
and each one has been a major success.
The one thing MCP does well is authentication. It bakes in OAuth, handling the
browser redirect, token exchange, and credential passing transparently, which
genuinely adds value in chat UIs where connecting to Google Drive or Slack withou
touching a terminal is a real improvement. CLI tools have done OAuth for years,
gh auth login gcloud auth login aws configure
though: , , . The token en
GITHUB_TOKEN=xxx gh repo
up in an environment variable or config file, and


---
*Page 6*


list
works with pipes, scripts, Docker, and CI/CD. MCP’s auth story is good for ch
interfaces specifically, which is a narrower use case than it first appears.
The future
Agents will orchestrate the OS, not because it’s trendy, but because it’s the right
abstraction. An operating system is, by definition, the layer that manages how
programs discover, invoke, and communicate with each other, and that’s exactly the
problem MCP is trying to solve. The reason the fixes keep converging is something
like gravity: MCP is being pulled towards the actual OS because the OS already
occupies that niche.
Shell commands are the interface to this layer, and the model’s job is to decide whic
commands to run and how to chain them, not to be the runtime for every individual
tool invocation. MCP may survive as an interface layer handling authentication in c
UIs, but in the long run the value of an agent isn’t presentational; it’s in how it
executes and composes tools underneath. That layer is the operating system, and ba
is how you talk to it. The trajectory from Claude Code to Cowork to OpenClaw sho
the industry moving towards the OS as a foundation.
This is bigger than a protocol debate, though. LLMs that can write and execute she
commands have real computer use capabilities, not the constrained, tool-by-tool kin
where every action requires a pass through the model, but the kind where the mach
actually operates itself. Linux is the universal interface to everything a computer ca
do: files, processes, networks, hardware, APIs, databases. Give a model that interfac
and it doesn’t need a purpose-built integration for every service; it just uses the
computer the way a human would, except faster and without getting bored.
Every industry that runs on computers, which is every industry, will eventually run
agents that orchestrate work through bash, not because bash is a creative design
decision, but because Linux already defined the most powerful application runtime


---
*Page 7*


ever built. MCP is trying to construct a new one on top of it, whilst the winning age
just use the one that’s already there.
Subscribe to Dead Neurons
Launched a month ago
Quick reads on Tech, Econ & AI.
Type your email... Subscribe
By subscribing, you agree Substack'sTerms of Use, and acknowledge
itsInformation Collection NoticeandPrivacy Policy.
4 Likes
Discussion about this post
Comments Restacks
Write a comment...
taignobias 21h
Well said. I have been pointing out what was first taught to me by a consultant-turned-professor
ago: every few years, they just re-invent the same solutions with new names.
Most AI advancements are just the rediscovery of lessons learned decades ago during the birth
multi-threading, networking, and the like.
LIKE REPLY


---
*Page 8*


© 2026Dead Neurons · Privacy ∙ Terms ∙ Collection notice
Substackis the home for great culture