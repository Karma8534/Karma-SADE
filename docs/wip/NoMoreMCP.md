# NoMoreMCP

*Converted from: NoMoreMCP.pdf*



---
*Page 1*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
Tech and AI Guild
Member-only story
Bye-Bye MCP: Says Perplexity and
Cloudflare
Shashwat Follow 4 min read · Mar 13, 2026
275 13
Open in app
Search Write
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 1/12


---
*Page 2*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
Photo by Luiz Rogério Nunes on Unsplash
After months of hype, Perplexity’s CTO just announced they are moving
away from the Model Context Protocol (MCP) internally.
Well, the agentic AI community is experiencing a massive reality check.
If you have been following the developer narrative for some time, the Model
Context Protocol (MCP) was supposed to be the universal standard.
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 2/12


---
*Page 3*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
And I won’t say it wasn’t helpful. I built the Splitwise MCP because paying for
pro wasn’t a great idea.
Free to read for non members
It was the magic glue that securely connected Claude or Gemini to our local
databases, APIs, and file systems.
But I guess that phase is officially over.
Over the last 24 hours, the communities have been on fire.
The CTO of Perplexity confirmed they are stepping back from MCP
internally in favor of traditional REST APIs and CLIs, especially for their
enterprise clients.
Simultaneously, Cloudflare dropped a massive technical teardown
explaining exactly why traditional MCP tool-calling architectures are
fundamentally flawed for complex AI agents.
Why Perplexity is Pulling the Plug
The premise of MCP is brilliant: standardize the way LLMs interact with
external data. But according to the leaked internal consensus at Perplexity,
the execution in a high-scale enterprise environment is currently a
nightmare.
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 3/12


---
*Page 4*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
The Security Gap: For a startup that’s small, local MCPs are great. But for
a massive enterprise client, the auth story in MCP is practically
nonexistent. When dealing with strict compliance requirements, rate
limiting, and audit logs, developers are realizing that traditional
REST/GraphQL APIs already solved these problems a decade ago.
The Stdio Transport Flaw: Developers have reported that using stdio
transport, the default way local MCP servers communicate with the IDE
becomes incredibly brittle under serious load.
Protocol Immaturity: The spec feels outdated to many infrastructure
engineers, making it feel more like a great local dev tool than an
enterprise-ready pipeline.
Note: Perplexity isn’t deleting MCP entirely, they still maintain it so tools like
Claude Desktop can connect to their search.
But for their core, cross-org enterprise routing? They are going back to the
boring, battle-tested reality of REST APIs.
The Cloudflare Teardown: Token Waste and Tool Overload
While Perplexity cited infrastructure and security, Cloudflare attacked the
actual mechanism of how LLMs use tools via MCP.
In a highly circulated article, they pointed out three fatal flaws in standard
tool calling:
1. Lack of Training Data: LLMs have ingested millions of lines of code, but
very few examples of raw JSON tool calling. As Cloudflare put it: “Asking
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 4/12


---
*Page 5*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
an LLM to use tool calling is like putting Shakespeare through a one-month
Mandarin course and then asking him to write a play in it.”
2. Tool Overload (The Cardinality Problem): When you dump 30+ MCP
tools into the context window, the model starts hallucinating because the
descriptions blur together. It struggles to pick the right tool.
3. The “Token Waste” Loop: This is the biggest architectural flaw. In a multi-
step task (e.g., A → B → C), every intermediate result has to pass back
through the LLM.
Call API A → Result goes to LLM → LLM reads it → Calls API B → Result
goes to LLM → LLM reads it → Calls API C.
Every round-trip adds 1–5 seconds of latency and wastes thousands of
tokens just copying data.
The Code Mode Solution
The alternative being pushed by Cloudflare, Pydantic (with Monty), and new
open-source runtimes like Zapcode, is a radical shift:
Stop letting the LLM call tools one by one.
Let the LLM write a script that calls them all.
This is what Cloudflare calls “Code Mode.”
Instead of three separate LLM round-trips to compare the weather in two
cities, the LLM generates a single block of TypeScript.
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 5/12


---
*Page 6*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
The LLM fires off the code, and a sandboxed runtime (like a V8 isolate on
Cloudflare Workers) executes the entire chain.
The intermediate values stay in the code, they never pass back through the
neural network.
What used to be four expensive LLM round-trips becomes one single
generation step followed by native code execution :)
What This Means for the Local Stack?
If you are running an M3 Max and relying on the Claude Code CLI to manage
your backend, this debate is critical.
MCP is not dead. It is just being demoted.
Cloudflare explicitly stated that MCP remains the absolute best “tool
discovery protocol.”
What is changing is the last mile of execution.
Instead of letting Claude call my database 15 times to generate a report, the
future of the stack involves Claude reading the MCP schema, writing a 50-
line TypeScript or Python script, and handing that script to a sandboxed
local runtime (like Zapcode) to execute in one shot.
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 6/12


---
*Page 7*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
So, If you are building an agentic workflow this week, don’t throw away your
MCP servers.
Just stop treating them like a magic wand.
Treat them like an API schema, and let your LLM do what it actually does
best: write the code to consume it.
Btw, I recently built a medium-no-bait-reader
In case we are meeting for the first time, come over here, it’ll be worth the roller
coaster of articles that are gonna come up in the next few weeks.
Mcp Server Model Context Protocol Perplexity Ai Cloudflare AI
Published in Tech and AI Guild
Follow
44 followers · Last published 9 hours ago
Every new updates and thoughts about tech and AI
Written by Shashwat
Follow
414 followers · 26 following
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 7/12


---
*Page 8*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
Sharing lessons on everything I learn (mostly tech). I love reading more than I
love writing. Scaling https://boutpredict.aibucket.org to 150 monthly users.
Responses (13)
Rae Steele
What are your thoughts?
FinTech with Aniket he/him
Mar 17
This feels less like “MCP failed” and more like a reality check on how AI actually works in production.
Standardizing everything sounds good in theory… but once you deal with real tools, APIs, and edge cases,
abstraction starts adding more friction than it removes.
Feels like we’re moving from “ideal architectures” back to what actually works, simpler, more direct
integrations.
68 Reply
Michael
4 days ago
What comes after MCP?
One for sure: Going back to the Rest API cann't be the answer.
15 Reply
Sylva Moth
Mar 13
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 8/12


---
*Page 9*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
This sounds like it solves a few problems. I'll have to get AI to study, this is above my understanding.
12 1 reply Reply
See all responses
More from Shashwat and Tech and AI Guild
InActivated Thinker by Shashwat InTech and AI Guild by Shashwat
Gemini 3.1 Pro: Google Antigravity My 90-Day “Life Changing”
just got a massive brain transplant. Roadmap
77% reasoning scores, 1M context, and the Balancing a Full-Time Job, DSA, System
end of tool-hallucination? Design, health and my sanity
Feb 20 176 3 Nov 30, 2025 318 6
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 9/12


---
*Page 10*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
InTech and AI Guild by Shashwat Shashwat
Day 6: Topological Sort (DFS vs Why Google (Mostly) Won’t Let Its
Kahn’s Algo) Own Devs Use Antigravity?
The Strategic Half-Day The world’s biggest AI company launches an
“agent-first” IDE that its own engineers can’t…
Dec 5, 2025 15 Dec 18, 2025 147 4
See all from Shashwat See all from Tech and AI Guild
Recommended from Medium
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 10/12


---
*Page 11*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
The Latency Gambler Han HELOIR YAN, Ph.D. ☕
Anthropic Says Engineers Won’t What Cursor Didn’t Say About
Exist in a Year. It’s Also Paying… Composer 2 (And What a Develop…
The most honest job posting in tech history The benchmark was innovative. The
might also be the most revealing thing about… engineering was real. The model ID told a…
Mar 11 463 15 4d ago 1.4K 9
Reliable Data Engineering InTowards Deep Learning by Sumit Pandey
The Claude Certified Architect Is YC’s CEO Open-Sourced gstack. It
Here — And It’s Unlike Any AI… Changed My Mind About Claude…
YC’s CEO open-sourced his AI coding setup.
20K stars in 6 days. Here’s how to use it and…
Mar 18 471 9 Mar 18 459 15
InLevel Up Coding by Yanli Liu InGenerative AIby Adham Khaled
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 11/12


---
*Page 12*


3/25/26, 3:13 PM Perplexity Drops MCP: Why Cloudflare Says AI Tool Calling is Broken | Tech and AI Guild
5 Agent Frameworks. One Pattern Perplexity Computer Just Did in 7
Won. Minutes What Took Me Hours
AutoGen vs. LangGraph vs. CrewAI vs. Perplexity Computer coordinates 19 AI
ByteDance’s DeerFlow vs. Anthropic — and a… models for real research tasks. Here’s what it…
Mar 16 725 8 Mar 16 1.3K 21
See more recommendations
https://medium.com/tech-and-ai-guild/bye-bye-mcp-says-perplexity-and-cloudflare-2c0f10a44b29 12/12