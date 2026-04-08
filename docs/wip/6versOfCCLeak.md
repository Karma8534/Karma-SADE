# 6versOfCCLeak

*Converted from: 6versOfCCLeak.pdf*



---
*Page 1*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
Open in app
4
Search Write
AI Software Engineer
Member-only story
6 Spins of Leaked Claude Code
Source (That’ll Teach You More Than
You Expect)
Joe Njenga Following 7 min read · 1 hour ago
54 1
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 1/18


---
*Page 2*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
Since the major Claude Code source code leak, there have been several spin-
offs of the original code, but only a few stand out.
It’s hard to sort out the junk, and if you went through my first Claude Code
leaked source code review, you are one step ahead.
When the Claude Code source leaked, the developer community went into
overdrive.
Within hours, repositories started popping up everywhere. Forks, rewrites,
reconstructions, visual explainers — you remember the first review that I
shared here.
Some hit 100K stars in two hours, while some were removed in DMCA
takedowns.
I spent time going through the chaos to find the ones worth your attention.
These six spins each bring something different to the table:
A Rust rewrite that became the fastest-starred repo in GitHub history
A visual walkthrough that maps 1,900+ files into something you can
actually explore
Locally runnable versions that let you plug in your own API keys
A source-map reconstruction that shows how much you can recover from
compiled code
An academic collection with a minimal 5,000-line Python
reimplementation
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 2/18


---
*Page 3*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
An enterprise-grade version with debugging, monitoring, and custom
authentication
Each one teaches you something about how Claude Code works from the
agent loop to the tool system to the hidden features waiting to ship.
Let me walk you through them.
1) Claw Code
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 3/18


---
*Page 4*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
Claw Code is a clean-room rewrite of Claude Code that broke GitHub
records; 50K stars in two hours, now at 153K.
Sigrid Jin, a Korean developer featured in the Wall Street Journal for burning
through 25 billion Claude Code tokens in a year, built this at 4 AM the night
of the leak.
It’s ideal for developers who want to understand Claude Code’s harness
architecture without wading through 500K lines of TypeScript. The Rust port is
production-ready, and the Python version mirrors the original structure close
enough to study side by side.
The project uses oh-my-codex for orchestration; the entire porting session
was AI-assisted with parallel code review and architect-level verification.
Key Features
Full Rust workspace with API client, runtime, tools, commands, and plugin
crates
Python porting workspace that mirrors the original TypeScript layout
Parity audit tool to track gaps against the original implementation
Clean-room approach — no copied source, just architectural patterns
If you want one repo to study how agentic coding tools wire their internals,
this is the best. I shared a review of Claw Code here, which is a good place to
start.
Link: Claw Code — github.com/ultraworkers/claw-code
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 4/18


---
*Page 5*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
2) Claude Code Unpacked
Claude Code Unpacked is the visual walkthrough that finally makes sense of
the leaked source. It takes 1,900+ files and 519K lines of code and organizes
them into interactive visuals you can actually explore.
It’s perfect for visual learners and anyone who wants to trace Claude Code’s
architecture without having to read source files. Click through the treemap,
watch the agent loop animate, and see which tools are locked behind feature
flags.
I covered this one in full detail in my earlier article — the creator beat me to an
idea I was already working on.
Key Features
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 5/18


---
*Page 6*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
Agent loop visualization with 11 steps mapped from input to render
Architecture explorer displaying the entire source tree as an interactive
treemap
Tool system catalog showing all 53+ tools across 8 categories
Command catalog with 95+ slash commands organized by function
If you haven’t seen it yet, start here before going into the other spins.
Link: Claude Code Unpacked — ccunpacked.dev
My Review: For the full breakdown — I Found Claude Code Unpacked The Best
Visual Walkthrough
3) CC-Haha
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 6/18


---
*Page 7*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
CC-Haha is a locally runnable version of the leaked Claude Code source. The
original leak couldn’t run out of the box; it had missing files, broken
imports, and native packages that threw exceptions.
It’s built for developers who want to run Claude Code with their own API keys.
You can plug in MiniMax, OpenRouter, or any Anthropic-compatible endpoint.
It does not require an official Anthropic account.
The repo also includes eight architecture diagrams covering the request
lifecycle, tool system, multi-agent setup, and permission flow; they are
useful reference material.
Key Features
Full Ink TUI interface matching the official Claude Code experience
Support for third-party APIs via environment variables or settings.json
Headless mode with --print flag for scripts and CI pipelines
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 7/18


---
*Page 8*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
Recovery CLI fallback when the full TUI has issues
The documentation is primarily in Chinese, but the code and setup
instructions are simple to follow and can be translated on their website to
English.
Link: CC-Haha — github.com/NanmiCoder/cc-haha
4) Claude Code Rev
Claude Code Rev is a source-map reconstruction of Claude Code. Instead of
working from the leaked source, this project reverse-engineered the compiled
npm package using source maps and backfilled missing modules.
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 8/18


---
*Page 9*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
It’s useful for understanding how much of a codebase you can recover from
production bundles. Type-only files, build-time generated content, native
bindings — all the things source maps don’t preserve had to be shimmed or
rewritten.
The project now routes through the real CLI bootstrap instead of temporary
shims, and bundled skill content has been restored to usable reference docs.
Key Features
Source tree reconstructed primarily from source maps
Compatibility shims for Chrome MCP, and Computer Use MCP
Working fallback prompts for planning and permission-classifier flows
Runs with bun run dev after bun install
Some modules still contain restoration-time fallbacks, so behavior differs
from the original in places, but it runs.
Link: Claude Code Rev — github.com/oboard/claude-code-rev
5) Collection Claude Code Source Code
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 9/18


---
*Page 10*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
Collection Claude Code Source Code is an academic archive that bundles
multiple Claude Code resources into one place.
The original leaked source, the Claw Code rewrite, analysis documents, and a
minimal Python reimplementation called nano-claude-code. It’s suited for
researchers and developers who want everything in one repo.
The nano-claude-code project inside is useful; it’s a 5,000-line Python
implementation that supports 20+ models, including Anthropic, OpenAI,
Gemini, DeepSeek, and local models via Ollama.
Key Features
Original leaked source preserved as-is (1,884 TypeScript files)
Nano-claude-code with multi-agent orchestration, persistent memory, and
skills system
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 10/18


---
*Page 11*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
18 built-in tools, including Agent, MemorySearch, and Skill execution
Bilingual documentation in English and Chinese
The collection also tracks news and analysis from the leak; Hacker News
discussions, Chinese tech breakdowns, and video reviews are all linked in
the README.
Link: Collection Claude Code — github.com/chauncygu/collection-claude-
code-source-code
6) Claude Code Best (CCB)
Claude Code Best is an enterprise-grade decompiled version of Claude Code.
Full TypeScript type fixes, Sentry monitoring, GrowthBook feature flags, and
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 11/18


---
*Page 12*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
a custom login flow that lets you connect to any Anthropic-compatible API.
It’s designed for teams that want to run Claude Code internally with their own
infrastructure. The repo is npm-installable — bun i -g claude-code-best and
you're running.
The project is actively maintained with versioned releases (currently V5) and
a roadmap that includes Voice Mode, Bridge Mode, Computer Use, and the
/dream memory consolidation feature.
Key Features
Custom /login flow supporting Anthropic-compatible endpoints
Feature flags via environment variables (FEATURE_BUDDY,
FEATURE_FORK_SUBAGENT, etc.)
VS Code debugging support with attach mode for TUI sessions
Full documentation site with feature guides and internal breakdowns
If you want Claude Code running in a corporate environment with
monitoring and auth, this is the most complete option.
Link: Claude Code Best — github.com/claude-code-best/claude-code
Final Thoughts
These six spins save you from reading 500K lines of TypeScript.
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 12/18


---
*Page 13*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
Each one uniquely approaches the leaked source: visual exploration, clean-
room rewrites, runnable forks, academic archives, and enterprise tooling.
If you’re building agentic tools, studying how Claude Code wires its
internals, these repos will make that easier.
Do you know of any other Claude Code leak source code repo that I left out that
deserves to be on this list? Let me know in the comments below
Related Reading:
I Found Claude Code Unpacked: The Best Visual Walkthrough
Claw Code — Claude Code Source Code Rewrite in Python
I Did Claude Code Source Code Leak Full Review
Let’s Connect!
If you are new to my content, my name is Joe Njenga
Join thousands of other software engineers, AI engineers, and solopreneurs who
read my content daily on Medium and on YouTube where I review the latest AI
engineering tools and trends. If you are more curious about my projects and
want to receive detailed guides and tutorials, join thousands of other AI
enthusiasts in my weekly AI Software engineer newsletter
If you would like to connect directly, you can reach out here:
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 13/18


---
*Page 14*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
AI Integration Software Engineer (10+ Years Experience )
Software Engineer specializing in AI integration and automation.
Expert in building AI agents, MCP servers, RAG…
njengah.com
Follow me on Medium | YouTube Channel | X | LinkedIn
Claude Code Anthropic Claude Code Claude Code Tips Open Source Github
Published in AI Software Engineer
Following
3.4K followers · Last published 1 hour ago
Sharing ideas about using AI for software development and integrating AI
systems into existing software workflows. We explores practical approaches for
developers and teams who want to use AI tools in their coding process.
Written by Joe Njenga
Following
21K followers · 98 following
Software & AI Automation Engineer, Tech Writer & Educator. Vision:
Enlighten, Educate, Entertain. One story at a time. Work with me:
mail.njengah@gmail.com
Responses (1)
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 14/18


---
*Page 15*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
Rae Steele
What are your thoughts?
Rae Steele You
Just now
As always, amazing find(s) - thanks so much Joe!
Are you aware of any of these (or similar) that have the claude for windows port? I recently ran across the
windows version and would like to compare. Thanks for all you do,
~Rae
Reply
More from Joe Njenga and AI Software Engineer
InAI Software Engineer by Joe Njenga Joe Njenga
Why Claude Weekly Limits Are Everything Claude Code: The Repo
Making Everyone Angry (And… That Won Anthropic Hackathon…
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 15/18


---
*Page 16*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
Yesterday, I finally hit my weekly Claude limit, If you slept through this or missed out,
and I wasn't surprised, since I see dozens of… Everything Claude Code hit 900,000 views o…
Oct 19, 2025 733 62 Jan 22 533 4
Joe Njenga Joe Njenga
Claude Code Ultraplan Launched: I Anthropic Adds (New) Claude Code
Just Tested It (And It’s Better Tha… Auto Mode (No More Permission…
Anthropic has added Claude Code ultraplan, Ok, we had YOLO mode, but now Claude Code
and I was quick to test it. You might like it or… Auto mode is here, and you can now code…
2d ago 401 11 Mar 25 425 9
See all from Joe Njenga See all from AI Software Engineer
Recommended from Medium
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 16/18


---
*Page 17*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
InUX Planetby Nick Babich Rick Hightower
Figma Skills for Claude Code Claude Code Subagents and Main-
Agent Coordination: A Complete…
How to create UI design in Figma without
leaving Claude Code Mastering AI Agent Coordination: Effective
Delegation Patterns for Claude Code…
6d ago 56 1 Mar 30 158 2
InObsidian Observer by Theo Stowell Balu Kosuri
The TL;DR of Claude Code Inside I Turned Andrej Karpathy’s
Obsidian Autoresearch Into a Universal Skill
If you’ve not been keeping up with the jumble By Balasubramanyam Kosuri
of noise…
Mar 29 178 3 Mar 21 142 3
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 17/18


---
*Page 18*


4/7/26, 1:33 PM 6 Spins of Leaked Claude Code Source (That’ll Teach You More Than You Expect) | by Joe Njenga | AI Software Engineer | Apr, 20…
InStackademic by Usman Writes unicodeveloper
You Can Now Learn Anything 100x 10 Must-have CLIs for your AI
Faster With Claude. Agents in 2026
Most people use AI to draft emails or MCP or CLIs. Your coding agent already lives
summarize articles. in the terminal, others will follow. These are 1…
6d ago 922 5 6d ago 468 4
See more recommendations
https://medium.com/ai-software-engineer/6-spins-of-leaked-claude-code-source-thatll-teach-you-more-than-you-expect-3e806ee47aea 18/18