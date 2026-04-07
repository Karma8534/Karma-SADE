# Caching

*Converted from: Caching.PDF*



---
*Page 1*


Open in app
Search Write
AI Software Engi…
Member-only story
Anthropic Just Fixed
the Biggest Hidden
Cost in AI Agents
(Automatic Prompt
Caching)
Joe Njenga Following 9 min read · 2 hours ago
63


---
*Page 2*


With just one change, you can cut Claude API costs
to 10 cents on the dollar and stop bleeding cash on
every single API call.
Yes.
Do you know that every time your agent calls
Claude, you’re paying for the same system prompt,
tool definitions, and instructions — over and over
again?
Not because Claude needs them repeated.
But,


---
*Page 3*


Because the API is stateless — it remembers nothing
between turns, which means your harness has to
resend everything from scratch on every single
request.
If you are not a paid Medium
member, you can read the article
here for FREE, but consider joining
Medium to support my work —
thank you!
Run a coding agent for 50 turns with a 10,000-token
system prompt, and you’ve silently paid for 500,000
tokens of the same instructions you already sent
on turn one.
Most developers don’t catch this until they see the
bill. Anthropic just made this new fix.


---
*Page 4*


The Claude API now automatically
caches the static parts of your
prompts — system instructions,
tool definitions, context — and
reuses them across turns.
Cache hits cost just 10% of standard input token
pricing, which means that 500,000-token overhead
drops to 50,000 tokens billed.
I’ve been covering Anthropic’s infrastructure
releases closely — from how they solved the AI
agent bloat problem by cutting token usage from
150,000 down to 2,000 with code execution and
MCP, to the prompt caching mechanics that sit at
the core of how Claude Code works.
Auto-caching is the piece that makes all of it
accessible to every developer building on the API,
without any manual overhead.


---
*Page 5*


In this article, I’ll break down how prompt caching
works and the lessons the Claude Code team
learned from running this in production.
How Prompt Caching Works
Before we get into how to use it, you need to
understand what’s happening.
Two Things Happen Every Time You Call Claude
When you send a request to the Claude API, the
model runs two distinct phases.
First, the prefill phase — this is where Claude
processes your entire prompt. Every token in
your system instructions, tool definitions, and
conversation history gets read and computed
before a single word of the response is
generated.
Second, the decode phase — this is where
Claude generates the actual response, token by
token.


---
*Page 6*


The prefill phase is the expensive one.
If your prompt shares a prefix with a previous
request, that prefill computation doesn’t need to
happen again since it’s already been done.
The result can be saved, hashed, and reused. That’s
the entire premise of prompt caching.
Prefix Match
Claude’s caching works through exact prefix
matching.
When you mark a block withcache_control, the API
creates a cryptographic hash of everything from
the start of your request up to that point.
On the next request, if that prefix is identical, it
finds the hash, skips the prefill for those tokens, and
charges you 10% of the standard rate.


---
*Page 7*


One character difference anywhere in that prefix
— a different timestamp, a reshuffled tool, an extra
space — produces a completely different hash.
This is why ordering matters so much, and why
some changes that seem harmless will cost you
without any warning — more on that later.
Token Math in Real Terms
Let’s make this easy to understand with a real
scenario.
Say you’re building a code review agent.
Your setup looks like this:
System prompt with instructions and persona: 8,000
tokens
Tool definitions (read file, search, run tests): 4,000
tokens


---
*Page 8*


Project context (CLAUDE.md, coding standards):
3,000 tokens
That’s 15,000 tokens of static context before a
single user message.
Now your agent runs a review session — 40 turns of
back-and-forth as it reads files, runs checks, and
reports findings.
Without caching:
15,000 tokens × 40 turns = 600,000 input tokens bille
With caching:
Turn 1: 15,000 tokens at full price (cache write)
Turns 2–40: 15,000 tokens × 39 turns at 10% = 58,500
Total static token cost: 15,000 + 58,500 = 73,500 tok
That’s a reduction from 600,000 tokens down to
73,500 — for the static parts alone, on a single


---
*Page 9*


session.
At scale, across hundreds of concurrent users
running similar sessions, that difference stops
being a nice-to-have and starts being the reason
your product is financially viable.
How the Cache Breakpoint Works
Before auto-caching, you had to tell Claude exactly
where to cache by placing a cache_control
breakpoint manually in your request:
{
"messages": [
{ "role": "user", "content": "Review this file" }
{ "role": "assistant", "content": "Here are my fi
{
"role": "user",
"content": "Now check the tests",
"cache_control": { "type": "ephemeral" }
}
]
}


---
*Page 10*


The breakpoint does two things.
It tells Claude to cache everything up to and
including that block.
And on the next request, it tells Claude to search
backward up to 20 blocks for a matching hash.
The problem with this manual approach is that as
the conversation grows, you have to keep moving
the breakpoint to the latest block.
If you miss a turn, you lose the cache hit or get the
ordering wrong, and you pay full price for tokens
you already paid for.
This is where auto-caching provides the solution.
Auto-Caching: What Changed
Manual caching worked, but it put the entire
burden on the developer.


---
*Page 11*


You had to track the conversation yourself, decide
where the breakpoint should sit, and move it forward
on every single turn as new messages accumulated.
For simple apps, that is manageable, but for long-
running agents with dozens of turns, it creates a
real problem.
One Parameter
With auto-caching, you add a single cache_control
field at the top level of your API request:
{
"cache_control": { "type": "ephemeral" },
"messages": [
{ "role": "user", "content": "Review this file" }
{ "role": "assistant", "content": "Here are my fi
{ "role": "user", "content": "Now check the tests
]
}
The API automatically identifies the longest
matching prefix in your request, moves the cache
breakpoint to the last cacheable block, and reuses


---
*Page 12*


it on every subsequent turn as the conversation
grows.
Session Example Breakdown
Turn 1 comes in — the API writes the cache for
your system prompt, tools, and context.
Turn 2 arrives — the API finds the matching
prefix from Turn 1, hits the cache, and you only
pay full price for the new message.
Turn 10, Turn 20, Turn 40 — same thing, the
cached prefix grows with the conversation, and
only the new tokens cost full price.
This is what makes long-running coding agents and
document analysis pipelines financially viable at
scale. The static parts of your prompt — which can
easily be 60–70% of your total token count.
Works with Manual Caching


---
*Page 13*


Auto-caching doesn’t replace block-level
cache_control if you need more granular control.
Say you want to cache your system prompt
independently from your project context, because
the system prompt is globally shared across all
users, but the project context changes per user.
You can still place explicit breakpoints on those
specific blocks, and auto-caching handles everything
else on top.
The caching rules haven’t changed, only the
implementation overhead. Auto-caching removes
the manual work of managing breakpoints.
But,
It doesn’t protect you from the ways developers break
their own cache mid-session, and those mistakes are
more common than you’d think.


---
*Page 14*


Rules That Keep Your Cache Alive
The Claude Code team built their entire agent
harness around prompt caching and monitors
cache hit rate the same way most teams monitor
uptime, with alerts, and incidents when it drops.
These lessons are drawn from Thariq's article shared
on X :
Here’s what they learned.
1. Order Your Prompt Static to Dynamic


---
*Page 15*


Caching works through prefix matching, so the
order of your request determines everything. The
Claude Code team structures every request like
this:
Base system instructions — globally cached
across all sessions
Tool definitions — globally cached across all
sessions
CLAUDE.md and project memory — cached per
project
Session state — cached per session
Conversation messages — grow each turn
Static content first means every session starts with a
cache hit. Dynamic content last means only new
tokens cost full price.
What breaks this ordering:
A timestamp embedded in your system prompt


---
*Page 16*


Tool definitions loading in a non-deterministic order
A parameter that changes slightly between sessions
Any of these shifts your prefix, produces a
different hash, and hands you a full-price bill on
every turn, with no warning.
2. Never Change Tools Mid-Session
The moment you add or remove a tool mid-
conversation, you’ve changed the cached prefix.
The entire cache is gone, and you’re paying full
price to rebuild it from scratch.
The fix the Claude Code team uses: instead of
swapping tools when a mode changes, they added
EnterPlanMode and ExitPlanMode as tools themselves.
The tool definitions never change. The model gets
a system message explaining the current mode,
but the prefix stays identical.


---
*Page 17*


3. Use System Messages, Not Prompt Edits
When something changes mid-session: a file
update, a time change, a user preference, the
instinct is to edit the system prompt.
But,
Every edit breaks the hash and triggers a full cache
rebuild. Instead, pass updated information as a
<system-reminder> tag inside the next user message
or tool result.
The model reads it, understands the update, and
your cached prefix stays untouched.
4. Don’t Switch Models Mid-Conversation
This one catches people off guard.
You’re 100,000 tokens deep with Opus. A simple
question comes up — the kind Haiku handles


---
*Page 18*


easily at a fraction of the cost. Switching feels like
the smart move.
But,
Prompt caches are unique to each model. Haiku has
no cache for your conversation. You’d pay full price
to rebuild 100,000 tokens of context from scratch,
which means switching to the cheaper model costs
more.
If you need a different model for a subtask, use a
subagent.
Opus prepares a focused handoff message with
only the relevant context, passes it to Haiku, and
the main session cache stays intact.
5. Compaction: The Edge Case Nobody Talks
About
Every long-running agent eventually hits the
context window limit, which means you need to


---
*Page 19*


summarize the conversation and continue in a
fresh session — this is compaction.
The naive implementation kills your cache.
Most developers run compaction as a separate API
call with a different system prompt and no tools.
From the API’s perspective, this looks nothing like
the parent conversation.
The Claude Code team’s solution is cache-safe
forking:
Use the exact same system prompt, tools, and
context as the parent conversation
Prepend the full conversation history
Append the compaction prompt as the final user
message
The API sees a request that looks nearly identical
to the last turn of the parent session. The cache


---
*Page 20*


hits, and the only tokens billed at full price are the
compaction prompt itself.
Final Thoughts
Not every use case benefits equally from prompt
caching, and it’s worth being honest about that
before you go restructuring your entire prompt
architecture.
It's useful when two conditions are met: your static
context is large, and your sessions run long. The
more turns, the more that the cached prefix pays for
itself. It makes the biggest difference in these
scenarios:
Coding agents — large system prompts, many tool
definitions, long multi-turn sessions.
Document analysis pipelines — agents that ingest
the same instructions and context repeatedly across
many documents or users


---
*Page 21*


Customer support bots — big system prompts with
company knowledge, product details, and policy
instructions that never change between
conversations
Research assistants — long sessions where the agent
reads, synthesizes, and iterates across many turns
If your static context is under 1,000 tokens and
sessions rarely exceed 5 turns, auto-caching won’t
move the needle much.
Prompt caching has always been available in the
Claude API, but manual management puts the
complexity on the developer. Auto-caching makes
the optimization accessible to everyone building
on the Claude API.
If you’re building anything that runs more than a
handful of turns, you cannot afford to ignore this!
Let’s Connect!


---
*Page 22*


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
Follow me on Medium | YouTube Channel | X |
LinkedIn


---
*Page 23*


Anthropic Claude Anthropic Ai Claude Claude Code
Claude Ai
Published in AI Software Engineer
Follow
2.1K followers · Last published 2 hours ago
Sharing ideas about using AI for software
development and integrating AI systems into existing
software workflows. We explores practical
approaches for developers and teams who want to
use AI tools in their coding process.
Written by Joe Njenga
Following
16.5K followers · 99 following
Software & AI Automation Engineer, Tech Writer
& Educator. Vision: Enlighten, Educate, Entertain.
One story at a time. Work with me:
mail.njengah@gmail.com
No responses yet


---
*Page 24*


To respond to this story,
get the free Medium app.
More from Joe Njenga and AI Software
Engineer
Joe Njenga Joe Njenga
I Tried New Claude Everything Claude
C d Oll W kfl C d Th R Th t
Claude Code now works with If you slept through this or
Oll hi h t k th i d t E thi Cl d
Jan 19 Jan 22
Joe Njenga In by
AI Software Engi… Joe Nje…


---
*Page 25*


I Tested Kimi K2.5 with I Tested Clawdbot: The
Cl d C d (1 T illi M t P f l AI
Moonshot AI never stops I thought Clawdbot was
i i Ki i K2 5 i th AI h til I
Jan 25
Jan 28
See all from Joe Njenga See all from AI Software Engineer
Recommended from Medium
In by Joe Njenga
Activated Thin… Shane Coll…
How I Use Claude Code
Why the Smartest
SSH t C t t A
P l i T h A
Recently, Claude Code added
The water is rising fast, and
SSH t th Cl d
f i f Ch tGPT
6d ago 4d ago


---
*Page 26*


In by Steve Yegge
Coding Nexus Civil Learning
The Anthropic Hive
Claude Code Hooks: 5
Mi d
A t ti Th t
As you’ve probably noticed,
Claude Code hooks explained
thi i h i
ith l l Eli i t
Jan 16 Feb 6
Phil | Rentier Digital Automation In by
Towards AI Felix Pappe
21 OpenClaw
From Notes to
A t ti N b d
K l d Th Cl
After I published “33
How to combine human
O Cl A t ti ”
i i ht ith AI i f
5d ago Feb 7
See more recommendations