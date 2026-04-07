# ClawCode1

*Converted from: ClawCode1.PDF*



---
*Page 1*


Open in app
11
Search Write
AI Software Engi…
Member-only story
Claw Code: Why This
Claude Code Agent
Harness Clone is
Blowing Up (114k+
Stars)
Joe Njenga Following 6 min read · 2 days ago
256 6


---
*Page 2*


It’s weird, the fastest repo in history to blow past
100K+ stars in a few hours, not days.
Forget OpenClaw, Claw-Code surpassed 50k stars in
2 hours of publication, but there is an interesting
twist.
On March 31, 2026, Anthropic accidentally shipped
a .map file inside their Claude Code npm package.
If you are not a premium Medium
member, you can read the article
here for FREE, but please consider


---
*Page 3*


joining Medium to support my work
— thank you!
That single file exposed 512,000 lines of TypeScript
across 1,906 source files — the entire internal
architecture of their flagship AI coding agent.
I already covered it here in the Claude Code source
code leak full code review.
Within hours, developer Sigrid Jin ported the core
architecture to Python from scratch.
The project, now called Claw Code,
captured the architectural patterns
without copying a single line of
proprietary source.
They have a website up already :


---
*Page 4*


In the midst of confusion with other projects or
products with a similar name — Claw Code.
So, don’t get confused, this is the GitHub link for
this project :
GitHub - instructkr/claw-code: The fastest
⭐
i hi t t 50K t
The fastest repo in history to surpass 50K
⭐
t hi th il t i j t 2
github.com
This project blew past the 100k stars in just a few
hours, and the community is now building what


---
*Page 5*


could become the open-source standard.
In this article, I break down what Claw Code is, how
it works, and why you should pay attention to this
project.
What is Claw Code?
Claw Code is an open-source AI coding agent
framework.
They describe it as a clean-room rewrite of Claude
Code’s internal architecture; built in Python and
Rust, from scratch.
Key points:
There was no proprietary code copied; the
architecture is different and legally independent
It’s provider-agnostic, works with Claude,
OpenAI, or local models
It’s fully auditable and extensible


---
*Page 6*


Free to use, self-hostable
Who Built It
Sigrid Jin, the developer :
Featured in the Wall Street Journal (March 21,
2026)
Consumed 25 billion Claude Code tokens in one year
Flew to San Francisco for Claude Code’s first
birthday party
One of the most active Claude Code power users in
the world
When the leak happened, Jin woke up at 4 AM to
notifications blowing up. Instead of hosting the
leaked source (legal risk), he ported the architecture
to Python overnight.
How It Was Built


---
*Page 7*


Jin used oh-my-codex (OmX) — a workflow layer
built on OpenAI’s Codex.
Two modes drove the build:
$team mode — parallel code review and
architectural feedback
$ralph mode — persistent execution loops with
verification
He collaborated with OmX creator Yeachan Heo
(@bellman_ych) to push the project further.
Current State
Be clear on what Claw Code is today:
Python foundation in place and functional
Rust port is actively in development (dev/rust branch
— 89.6% Rust now)


---
*Page 8*


27 CLI subcommands for inspection, manifests, and
verification
Not yet a full runtime replacement for Claude Code
You can inspect the architecture, but agentic
execution is still in progress
The Rust migration is expected to merge soon, which
will make it a fully functional agent runtime.
Architecture & Core Components
Claw Code uses a dual-layer design:
Rust (72.9%) — performance-critical runtime paths
Python (27.1%) — agent orchestration and LLM
integration
Repository Structure
claw-code/
├── src/ # Python workspace
│ ├── commands.py # CLI command registry
│ ├── tools.py # Plugin-based tool syst


---
*Page 9*


│ ├── query_engine.py # LLM calls, streaming,
│ ├── task.py # Task management
│ └── main.py # Entry point
├── rust/ # Rust core (6 crates)
│ ├── crates/api/ # API client + streaming
│ ├── crates/runtime/ # Session, tools, MCP, c
│ ├── crates/claw-cli/ # Interactive CLI binary
│ ├── crates/plugins/ # Plugin system
│ ├── crates/commands/ # Slash commands
│ ├── crates/server/ # HTTP/SSE server
│ └── crates/tools/ # Tool specs
└── tests/ # Verification suite
Core Components
1. Tool System
19 built-in, permission-gated tools
Covers: file I/O, bash execution, Git operations, web
scraping, agent spawning
Each tool is sandboxed with configurable access
controls
2. Query Engine
Handles all LLM API calls
Manages response streaming and caching


---
*Page 10*


Supports multi-step orchestration
Provider-agnostic design (not locked to Claude)
3. Multi-Agent Orchestration
Spawn sub-agents (called “swarms”)
Parallelize complex tasks
Each sub-agent runs in an isolated context with
shared memory access
4. MCP Integration
Full Model Context Protocol support
6 transport types: Stdio, SSE, HTTP, WebSocket,
SDK, ClaudeAiProxy
Connect to external tool servers with OAuth
authentication
5. Session & Memory
Multi-layer memory system
Session persistence and transcript compaction


---
*Page 11*


CLAUDE.md instruction file system for context
discovery
7-Stage Bootstrap Sequence
Every time Claw Code starts, it follows this
sequence:
1. Prefetch — gather workspace metadata and config
2. Warning Handler — install error handlers
3. CLI Parser + Trust Gate — parse args, verify
permissions
4. Setup + Parallel Load — run workspace setup, load
commands/agents
5. Deferred Init — execute deferred steps after trust
gate clears
6. Mode Routing — route to runtime mode (standard,
remote, SSH, teleport, direct-connect, deep-link)
7. Query Engine Submit Loop — enter main
conversation loop, process tool calls


---
*Page 12*


This mirrors what Claude Code does internally but
now documented and open.
Claw Code vs Claude Code
Claw Code Offers
Transparency — read every line of code
Multi-provider support — not locked to one LLM
vendor


---
*Page 13*


Customization — modify tools, commands, and
orchestration
Self-hosting — run it on your own infrastructure
Community-driven —open issues, active
development, and such
Claude Code Still Has
Production-ready, battle-tested runtime
Official Anthropic support and updates
IDE integrations (VS Code, JetBrains)
Claude also has upcoming features not yet
replicated: KAIROS — proactive background agent
mode, ULTRAPLAN — remote Opus-level planning
(up to 30 min sessions), and autoDream —
background memory consolidation
Final Thoughts


---
*Page 14*


Claw Code survives DMCA takedowns because it’s a
clean-room implementation. Direct mirrors of the
leaked source are quickly taken down.
But a Python/Rust rewrite that captures
architectural patterns without copying code is a new
creative work — but I think it's still a grey area.
Gergely Orosz (The Pragmatic Engineer) put it:
Anthropic can’t DMCA a project
that rewrote their code in a
different language from scratch.
If you want to study how agent harnesses work,
build your own tools on top, or understand what’s
in Claude Code's engine,’ Claw Code is a good place
to start.
Do you think this is a justifiable clone? Let me know
your thoughts in the comments below.


---
*Page 15*


Let’s Connect!
If you are new to my content, my name is Joe
Njenga
Join thousands of other software engineers, AI
engineers, and solopreneurs who read my content
daily on Medium and on YouTube where I review the
latest AI engineering tools and trends. If you are
more curious about my projects and want to receive
detailed guides and tutorials, join thousands of other
AI enthusiasts in my weekly AI Software engineer
newsletter
If you would like to connect directly, you can reach
out here:
AI Integration Software Engineer (10+
Y E i )
Software Engineer specializing in AI
i t ti d t ti E t i
njengah.com


---
*Page 16*


Follow me on Medium | YouTube Channel | X |
LinkedIn
Claw Code Claude Code Anthropic Claude Claude
Open Source
Published in AI Software Engineer
Follow
3.3K followers · Last published 6 hours ago
Sharing ideas about using AI for software
development and integrating AI systems into existing
software workflows. We explores practical
approaches for developers and teams who want to
use AI tools in their coding process.
Written by Joe Njenga
Following
20K followers · 98 following
Software & AI Automation Engineer, Tech Writer
& Educator. Vision: Enlighten, Educate, Entertain.
One story at a time. Work with me:
mail.njengah@gmail.com


---
*Page 17*


Responses (6)
To respond to this story,
get the free Medium app.
Cédric M
2 days ago
"But a Python/Rust rewrite that captures architectural patterns without
copying code is a new creative work — though I think it remains a grey
area."
Well, just look at how things turned out for Google with the Java API, and
😉
you'll have your answer… (besides, it's not exactly "new")
8
Ola
2 days ago (edited)
This is amazing.. Hey Joe, check out my work on GitHub.. SessionFS..
sessionfs.dev. It was all built with Claude code
7
Edinho
2 days ago
Technically, the original code is still present in the Git history, so it could
still be subject to a copyright takedown.


---
*Page 18*


3 1 reply
See all responses
More from Joe Njenga and AI Software
Engineer
Joe Njenga In by
AI Software Engi… Joe Nje…
I Finally Tested Claude
I Tested Cursor vs
C d / i It’
A ti it (I D ’t
Anthropic has now rolled out
After a week of rigorous
Cl d C d / i t ll
t ti G l A ti it i
Mar 13 Dec 9, 2025


---
*Page 19*


In by In by
AI Software Engi… Joe Nje… AI Software Engi… Joe Nje…
Gemini CLI Skills Are I Tested The New
H W k With Y G l Stit h (A d
Yes, Gemini CLI now supports Not so long ago, I discovered
Skill b t d ’t k th G l Stit h d th
Jan 12 Mar 26
See all from Joe Njenga See all from AI Software Engineer
Recommended from Medium


---
*Page 20*


Rick Hightower Reza Rezvani
Claude Code Top 10 Claude Code
S b t d M i Q ti B i
Mastering AI Agent The same three clusters keep
C di ti Eff ti f i t ti
4d ago 4d ago
Madhuranga Rathnayaka In by
Towar… Mandar Karhade, …
Massive Upgrade by
Anthropic Leaked Its
Cl d C d
O N l O ti
It upgraded your computer
The company that warns
l C b t ll d
b t “ d t d
Mar 26 6d ago


---
*Page 21*


In by ZIRU
Data Science … Gao Dalie…
Why 90% of Claude
Hermes Agent +
C d U A
Oll FASTEST W
The secret isn’t better
If you don’t have a Medium
t t d l
b i ti thi li k t
5d ago 6d ago
See more recommendations