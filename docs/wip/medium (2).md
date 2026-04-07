# medium (2)

*Converted from: medium (2).PDF*



---
*Page 1*


Open in app
2
Search Write
AI Software Engi…
Member-only story
Anthropic Adds 1
Million Context Window
to Opus 4.6 & Sonnet
4.6
Joe Njenga Following 4 min read · 1 hour ago
12 1


---
*Page 2*


The 1 million context window is now generally
available for Claude Opus 4.6 and Claude Sonnet
4.6 users.
Anthropic made this announcement today, and what
caught my attention immediately was the pricing
structure. There’s no long-context premium. A 900K-
token request costs the same per-token rate as a 9K
one.
For Opus 4.6, you’re looking at $5 input and $25
output per million tokens.


---
*Page 3*


Sonnet 4.6 comes in at $3 input and $15 output per
million tokens. Standard pricing across the full
window.
This changes a few things for developers who work
with large codebases, lengthy documents, or long-
running agent sessions.
Previously, you’d need workarounds;
summarization, context clearing, or engineering
tricks to manage what fits in the window.
With 1M tokens at standard rates, you can load an
entire codebase, thousands of contract pages, or the
full trace of a long-running agent without
compromise.
The release also brings full rate limits at every
context length.
Your standard account throughput applies whether
you’re at 50K tokens or 950K tokens.


---
*Page 4*


I wanted to dig into what this means and test how
well Claude performs at these extended context
lengths.
Understanding Context Windows
Before getting into the 1M release, let’s clarify what
a context window means.
It’s everything the model can
reference when generating a
response — your prompt, previous
messages, uploaded files, and the
response itself.
This is different from Claude’s training data.
Training is what Claude learned. Context is what
Claude can see right now in your conversation.


---
*Page 5*


How It Works
Each conversation turn adds to the context
window:
Input phase: All previous conversation history
plus your current message
Output phase: Claude’s response, which
becomes part of the next input
The context grows linearly. Turn 1 feeds into Turn 2.
Turn 2 feeds into Turn 3. Previous turns stay intact.


---
*Page 6*


With a 1M token context window, you have roughly
750,000 words of working memory. That’s enough
for entire codebases, lengthy documents, or
extended agent sessions.
Context Rot
More context isn’t automatically better. As the
token count grows, accuracy and recall can
degrade.
This is called context rot.
The challenge isn’t fitting information into the
window. It’s whether the model can still find and
use the right details when they’re buried among
hundreds of thousands of tokens.
This is where benchmark performance is important
and why Anthropic’s results at 1M tokens are
significant.
Extended Thinking and Context


---
*Page 7*


When Claude uses extended thinking, the thinking
tokens count toward the context window during
that turn.
But here’s the efficiency gain: previous thinking
blocks get automatically stripped from future
turns.
You don’t pay for thinking tokens twice. If you pass
thinking blocks back in your conversation history,
they’re excluded from the context calculation.
The formula looks like this:


---
*Page 8*


context_window = (input_tokens - previous_thinking_to
This keeps your context budget focused on actual
conversation content rather than reasoning traces
from earlier turns.
Now that you understand how the context window
works, let’s look at the new changes.
What’s New?
Anthropic rolled out several improvements
alongside the 1M context window.
Here’s what changed:
1. One Price, Full Context Window
The per-token rate stays flat whether you’re
sending 10K tokens or 900K tokens.
2. Full Rate Limits Across the Entire Window


---
*Page 9*


Your standard account throughput now applies at
every context length.
Previously, longer contexts could mean reduced
throughput.
3. 6x More Media Per Request
You can now include up to 600 images or PDF
pages in a single request, up from 100.
This applies to the Claude Platform natively,
Microsoft Azure Foundry, and Google Cloud’s Vertex
AI.
4. No Beta Header Required
If you were using the beta header for requests over
200K tokens, you can remove it.
Requests over 200K now work; if you forget to
remove the header, it’s simply ignored.
5. Claude Code Gets 1M Context


---
*Page 10*


For Max, Team, and Enterprise users, Opus 4.6
sessions in Claude Code now use the full 1M
context window. This means fewer compactions
and more of your conversation stays intact.
Previously, the 1M context required extra usage
allocation.
Final Thoughts
With 1M tokens at standard pricing, these are
some of the best use cases:
Entire Codebases in One Context
You can load a full codebase — files, dependencies,
documentation — and ask Claude to reason across
all of it.
For large projects, this changes how you approach
code reviews, refactoring, and debugging. Claude
can see the full picture instead of fragments.


---
*Page 11*


Document Analysis at Scale
Legal contracts, research papers, and financial
reports. With 600 images or PDF pages per request,
you can process substantial documents in a single
pass.
Previously, you’d split documents and manage
context manually.
Long-Running Agents
Agent workflows accumulate context quickly. Tool
calls, observations, intermediate reasoning — it all
stacks up.
With 1M tokens, the full trace stays intact with fewer
compactions, meaning less information loss between
steps.
Anthropic Claude Claude Claude Ai Claude Opus


---
*Page 12*


Claude Sonnet
Published in AI Software Engineer
Follow
2.7K followers · Last published 1 hour ago
Sharing ideas about using AI for software
development and integrating AI systems into existing
software workflows. We explores practical
approaches for developers and teams who want to
use AI tools in their coding process.
Written by Joe Njenga
Following
18.2K followers · 98 following
Software & AI Automation Engineer, Tech Writer
& Educator. Vision: Enlighten, Educate, Entertain.
One story at a time. Work with me:
mail.njengah@gmail.com
Responses (1)
To respond to this story,
get the free Medium app.


---
*Page 13*


AI 404
1 hour ago (edited)
while this can be a great help, I'm wondering if this isn't going to cost us a
lot more, since a lot more conversation will now have to be sent to
Anthropic servers for each of our request (4x more than before if we don't
compact early)... that's a lot more tokens to be exchanged at every press
of Enter
1 reply
More from Joe Njenga and AI Software
Engineer


---
*Page 14*


In by In by
AI Software Engi… Joe Nje… AI Software Engi… Joe Nje…
I Tested Antigravity Why Claude Weekly
Cl d O 4 6 Li it A M ki
I thought this was just a Yesterday, I finally hit my
k ti i i k B t kl Cl d li it d I
Feb 10 Oct 19, 2025
Joe Njenga Joe Njenga
I Tried (New) Claude How I’m Using (New)
C d A t T Cl d C d F t M
Forget single-agent When I get my coding flow,
kfl Cl d C d A d i h t I d Cl d
Feb 7 Feb 8
See all from Joe Njenga See all from AI Software Engineer


---
*Page 15*


Recommended from Medium
Reza Rezvani In by
Data Science Co… Paolo Pe…
Claude Code /simplify
Cursor vs Claude Code
C d Th
I Stopped Reviewing My Own The AI coding tool decision
C d / i lif D It i 90 ’t id
Mar 3 Mar 5