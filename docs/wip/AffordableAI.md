# AffordableAI

*Converted from: AffordableAI.PDF*



---
*Page 1*


Open in app
2
Search Write
Member-only story
The Engineering Trick
That Makes AI Agents
Affordable
Learn about the difference between a 0.50c
response and a $5.00 response
Marco Kotrotsos Follow 9 min read · 2 days ago
49
Thariq Shafi, a Claude Code engineer at Anthropic,
dropped a thread this week that should be required
reading for anyone building with AI APIs. The gist:
Claude Code, the AI coding agent used by millions,
treats prompt cache misses the same way most
companies treat server outages. They run alerts.


---
*Page 2*


They declare incidents. A few percentage points of
cache miss rate triggers an emergency response.
That sounds dramatic until you understand the
economics. Without prompt caching, every
message in a long AI conversation reprocesses the
entire conversation history from scratch. A
100,000-token conversation where you send 50
messages means the API processes 5 million
tokens of input. With caching, it processes the new
tokens and reads the rest from cache at a 90%
discount.
The difference between a cached and uncached
agentic session is the difference between a product
that costs $0.50 and one that costs $5. At scale, that
is the difference between a viable business and a
bankrupt one.
Peak Ji, the founder of Manus (another AI agent),
published parallel findings. His team found a 100:1
ratio of input tokens to output tokens in their agent


---
*Page 3*


sessions. When your input volume is that lopsided,
cache efficiency is not an optimization. It is the
entire cost structure.
This matters for you even if you are not building an
agent. If you use the Claude API for anything with
multi-turn conversations, long system prompts, or
repeated context, prompt caching can cut your
costs dramatically. And Anthropic just shipped
auto-caching, which makes the basic version
trivially easy to implement.
Here is how it works, what the Claude Code team
learned the hard way, and how to apply their
lessons without building a product as complex as
theirs.
What prompt caching actually is
Every time you send a message to the Claude API,
the model needs to process all the input tokens:
your system prompt, tools, conversation history,


---
*Page 4*


everything. Processing tokens is the expensive
part. It takes compute and time.
Prompt caching lets the API remember the
processed result of tokens it has seen before. On
the next request, if the beginning of your input
matches what was cached, the API skips
reprocessing those tokens and reads the cached
result instead. The read costs 10% of normal input
pricing.
The key mechanic: it works by prefix matching.
The API caches everything from the start of your
request up to a cache breakpoint. If the next
request has an identical prefix, those tokens are
read from cache. If anything in that prefix
changes, even one character, the cache is
invalidated and everything after it needs to be
reprocessed.
Think of it like a shared commute. If you and your
colleague both drive from the same neighborhood


---
*Page 5*


to the same office, you can carpool for the shared
portion of the route. But if one of you takes a
detour three blocks from home, you are driving
separately the rest of the way. The “shared prefix”
of the route is what makes carpooling work.
Prompt caching is the same idea applied to
computation.
The numbers
The cost savings are significant.
For Claude Sonnet 4.6, that means cached reads
cost $0.30 per million tokens versus $3.00 per
million for uncached input. For Opus 4.6, cached
reads are $1.50 versus $15.00. The first time tokens
are cached, you pay a small premium (25% extra
for a 5-minute cache). After that, every read is at
the 90% discount.
There is also a 1-hour cache tier that costs 2x base
rate but keeps the cache alive longer, useful for
sessions that might have gaps between messages.


---
*Page 6*


The latency improvement matters too. Cached
tokens process much faster than uncached ones,
which means your agent or chatbot responds
noticeably quicker as conversations get longer.
Two ways to implement it
Anthropic offers two approaches, and the simpler
one is new.
Auto-caching (the easy way)
Add a single field to your API request:
{
"model": "claude-sonnet-4-6",
"max_tokens": 1024,
"cache_control": {"type": "ephemeral"},
"system": "Your system prompt here...",
"messages": [...]
}
That is it. The API automatically places the cache
breakpoint at the end of the last cacheable block
and moves it forward as the conversation grows.


---
*Page 7*


For most multi-turn conversation use cases, this is
all you need.
Explicit breakpoints (for control)
If you need precise control over what gets cached,
you can place cache_control on specific content
blocks:
{
"system": [
{
"type": "text",
"text": "Your long system prompt...",
"cache_control": {"type": "ephemeral"}
}
]
}
This lets you set multiple cache breakpoints at
specific positions. Useful when you have distinct
sections of context (system prompt, reference
documents, conversation history) and want to
ensure each one is cached independently.


---
*Page 8*


What the Claude Code team learned
The auto-caching feature handles the basics. But if
you are building anything with long-running
sessions, lots of tools, or complex state
management, the Claude Code team’s lessons are
worth understanding. They shaped every design
decision in the product.
Lesson 1: Order your prompt like a cache
hierarchy


---
*Page 9*


Prompt caching matches from the beginning of the
request forward. That means the order of content
in your prompt determines how much gets cached
across requests.
The rule: static content first, dynamic content
last.
Claude Code structures every request like this:
1. Static system prompt and tool definitions (same
for every user, every session)
2. Project-level context like CLAUDE.md (same
within a project)
3. Session-level context (same within a session)
4. Conversation messages (changes every turn)
This way, even requests from different sessions
share cache hits on the system prompt and tools.
Requests within the same project share hits on the


---
*Page 10*


project context too. The only uncached tokens are
the newest messages.
If you flip this ordering, putting the dynamic stuff
first, you invalidate the cache on every single
request. The shared prefix is zero, and you are
paying full price for everything.
Lesson 2: The prefix is fragile
The Claude Code team broke their own caching
multiple times with changes that seemed
harmless. Some examples:


---
*Page 11*


Putting a detailed timestamp in the system
prompt (changes every second, invalidates the
entire prefix)
Shuffling tool definitions in a non-deterministic
order (the tools are the same, but the ordering
changed, so the prefix does not match)
Updating a tool’s parameters dynamically (e.g.,
changing which sub-agents are available)
Each of these caused the cache hit rate to drop,
costs to spike, and the team to scramble. This is
why they monitor cache hit rates like uptime and
treat drops as incidents.
The takeaway: anything in your static prefix needs
to be truly static. If it changes, move it out of the
prefix and into the conversation messages instead.
Lesson 3: Use messages for updates, not
prompt changes


---
*Page 12*


When information changes mid-session (the time,
a file the user edited, a new configuration), the
tempting approach is to update the system prompt.
Do not do this. It breaks the cache.
Instead, pass the update as a message in the next
conversation turn. Claude Code uses a <system-
reminder> tag inside user messages or tool results
to communicate updates to the model. "It is now
Wednesday." "The user changed file X." "New
context available."


---
*Page 13*


The model reads the update from the message. The
system prompt stays identical. The cache stays
intact.
Lesson 4: Never change tools mid-session
This one is counterintuitive. You would think that
giving the model only the tools it needs right now
would be efficient. But because tool definitions are
part of the cached prefix, adding or removing a
tool invalidates the cache for the entire
conversation.


---
*Page 14*


Claude Code’s solution: keep all tools in every
request, always. For tools that are only sometimes
needed (like dozens of MCP server tools), they use
a “defer loading” approach: send lightweight stubs
with just the tool name and a defer_loading: true
flag. The model can discover the full tool schemas
through a ToolSearch tool when it actually needs
them. The stubs stay stable in the prefix. The
cache stays intact.
Lesson 5: Do not switch models mid-
session


---
*Page 15*


Prompt caches are unique to each model. If you
are 100,000 tokens into a conversation with Opus
and want to ask a quick question that Haiku could
handle, switching to Haiku is actually more
expensive because you need to rebuild the entire
cache for Haiku from scratch.
The better pattern: use sub-agents. The main
model prepares a concise handoff message with
the relevant context, and a sub-agent running on a
cheaper model handles the task in its own session.
Claude Code does this with its Explore agents,
which run on Haiku with a focused context rather
than the full conversation history.
Lesson 6: Design features around the
cache, not the other way around


---
*Page 16*


Plan mode in Claude Code is a perfect example.
The obvious implementation: when the user enters
plan mode, swap out the tools for read-only tools.
But swapping tools breaks the cache.
Instead, Claude Code keeps all tools in every
request and implements plan mode as a tool itself.
When the user toggles plan mode, the model calls
EnterPlanMode, receives a message explaining the
constraints (explore the codebase, do not edit


---
*Page 17*


files), and calls ExitPlanMode when done. The tool
definitions never change. The cache never breaks.
A bonus of this design: because EnterPlanMode is a
tool the model can call on its own, it can
autonomously enter plan mode when it detects a
hard problem. A feature designed around a
caching constraint ended up producing better
behavior.
Lesson 7: Compaction needs to share the
parent’s prefix


---
*Page 18*


When a conversation hits the context window
limit, Claude Code summarizes the conversation so
far and continues with the summary. This is called
compaction.
The naive implementation: make a separate API
call with a different system prompt that says
“summarize this conversation.” This destroys the
cache, because the prefix of the compaction
request does not match the parent conversation.
You pay full price for all those tokens.
Claude Code’s approach: the compaction request
uses the exact same system prompt, tools, and
context as the parent conversation. The parent’s
messages are included, and the compaction
instruction is appended as a new user message at
the end. From the API’s perspective, the request
looks almost identical to the parent’s last request,
so the cache hit rate stays high.


---
*Page 19*


Anthropic built this directly into the API as a
compaction feature, so you do not need to
engineer it yourself.
What this means for you
If you are using the Claude API for multi-turn
conversations, enable auto-caching. It is one field
in your request body and it can cut your costs by
80–90% on long conversations. There is no reason
not to do this.
If you are building an agent or any product with
long-running sessions, the design lessons matter
more than the implementation:
1. Put static content at the top of your prompts.
Dynamic content at the bottom.
2. Do not modify your system prompt mid-session.
Use messages instead.
3. Do not add, remove, or reorder tools mid-
session.


---
*Page 20*


4. Do not switch models mid-session without using
sub-agents.
5. Monitor your cache hit rate. A drop means
something changed in your prefix.
The Claude Code team built their entire product
around these constraints from day one. They did
not optimize for caching later. They designed
around it from the start. Every architectural
decision, from how plan mode works to how tools
are loaded to how compaction runs, was shaped by
one question: does this break the cache?
If you are building on the API and ignoring prompt
caching, you are leaving money and speed on the
table.
Probably a lot of both.


---
*Page 21*


Marco Kotrotsos, specializing in practical AI
implementation for organizations ready to close the
gap between AI hype and AI value. With 30 years of IT
experience now focused purely on AI deployment, he
works hands-on with companies to turn AI potential
into measurable business outcomes.
My free substack about practical AI called
Autocomplete can be found here:
https://acdigest.substack.com.
I have another Medium publication where I write
about life, personal relationships, parenthood and
health from my own perspective.
https://medium.com/@strongerafter
AI LLM Programming Software Development


---
*Page 22*


Written by Marco Kotrotsos
Follow
1.4K followers · 410 following
Tech person. I write about technology, Generative AI,
the cloud, design and development. Deeper AND
broader at acdigest.substack.com
No responses yet
To respond to this story,
get the free Medium app.
More from Marco Kotrotsos
Marco Kotrotsos Marco Kotrotsos
GPT-5.3 Codex Isn’t a Claude Cowork is a
C d G t G Ch
One developer said they built What Claude Code’s
i f h th th C Sibli M f


---
*Page 23*


Feb 8 Jan 16
Marco Kotrotsos Marco Kotrotsos
Anthropic Is Running a The AI Agent Race is
Diff t R O Th Wi i
OpenAI needs to do more than Or; Agent Skills for the
i t d d
Feb 18 Dec 12, 2025
See all from Marco Kotrotsos
Recommended from Medium


---
*Page 24*


Marco Kotrotsos In by
Artificial Corn… The PyCoa…
Coding Is Solved.
You’re Using AI Wrong!
This Is How Programming Will H ’ H t B
The 3 levels of using AI in
Ch
2026
Feb 21 Feb 23
In by In by
Investor’s Handb… Sanjeev… Towards AI Divy Yadav
A New Financial Era AI Agent Guardrails:
H B 5 Y St Y A t F
The Strategic Moves Smart Building AI agents without
E M ki N d il i lik i i
Feb 17 Feb 20


---
*Page 25*


Reza Rezvani In by
Artificial Intelligenc… Faisal…
30 OpenClaw
The End of “Software
A t ti P t
E i ” Wh
SOUL.md templates, cron
Boris Cherny’s bold prediction
h d l it d il
i l i i hift i h
5d ago Feb 19
See more recommendations