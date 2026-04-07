# OCMem4CC

*Converted from: OCMem4CC.PDF*



---
*Page 1*


Open in app
11
Search Write
Generative AI
Member-only story
I Studied OpenClaw
Memory System —
Here’s What I Found
⾼達烈
Gao Dalie ( ) Follow 10 min read · Mar 16, 2026
303 1


---
*Page 2*


Over the past year, almost all AI products have
been talking about one word: memory.
ChatGPT is adding “long-term memory,” Claude is
starting to “understand context better,” and various
agent frameworks are emphasising “continuous
dialogue.” But the question remains: to whom do
these memories belong?
The recently viral open-source project OpenClaw
offers a completely different, even somewhat
dangerous, answer.


---
*Page 3*


It doesn’t entrust memories to the cloud, to
companies, or hide them in a black box. It stores
all memories, intact, on your own hard drive.
This open-source personal AI assistant, licensed by
MIT, was created by Peter Steinberger. After a
week of explosive growth, Clawdbot quickly
garnered over 100,000 stars on GitHub.
What it can do is nothing special; it’s all things that
large models excel at: managing emails,
scheduling trips, flight check-in, and running
scheduled background tasks…
But the most significant difference is that after it is
integrated with popular chat tools such as Discord,
WhatsApp, Telegram, and Slack, a wonderful
chemical reaction occurs: it doesn’t forget.
Even if you don’t use it for three days or three
months, even if you restart your computer, change
the model, or clear the context, it will still


---
*Page 4*


remember the decisions, preferences, and history
you made.
This quickly drew the attention of industry
developers. How exactly did Clawdbot manage to
do this?
Just now, an AI research engineer named Manthan
Gupta conducted a special study on this issue. He
dissected the memory system behind OpenClaw
and found that it is very different from ChatGPT
and Claude.
But what truly caught Manthan Gupta’s eye was its
persistent memory system: it could maintain
contextual memory around the clock, remember
previous conversations, and could infinitely build
upon past interactions.
Compared to ChatGPT and Claude, Clawdbot took a
completely different path:


---
*Page 5*


It doesn’t rely on cloud-based, company-controlled
memory; instead, it keeps everything local, giving
users complete control over their context and
skills.
󰬾
Before we start!
If you like this topic and you want to support me:
1. Clap my article 50 times; that will really help me
👏
out.
2. Follow me on Medium and subscribe to get my
🫶
latest article for Free
3. Join the family — Subscribe to the YouTube
channel
≠
Context Memory
To clarify this issue, Manthan Gupta stated that it is
necessary to understand a concept that is easily
confused in the industry: context ≠ memory.
“To understand Clawdbot, you must first separate
two things that many products deliberately


---
*Page 6*


confuse.”
What is context? Context is essentially all the
information the model can see in this round of
requests, including:
System Prompt, conversation history, tool return
results, current message, etc.
The reason people get headaches when it comes to
context, whether they are developing large models
or agents, is that context has three inherent
drawbacks: it is short, expensive, and limited.
Short: This round is all that’s left.
Expensive: The cost and latency increase with
each additional token.
Limited: Subject to context window limitations
(200,000, 1,000,000 tokens)
So what exactly is memory? In Clawdbot, memory
is something else that everyone is already familiar


---
*Page 7*


with:
Memory = Files stored on the disk
After all, the prompt and the tool's results are
intended for AI. But the Markdown files on disk
are human-readable, editable, and searchable.
This Markdown file better reflects people’s
understanding of the phenomenon of “memory”.
Durable: Remains after restart, the next day, and
the next month.
Unbounded: Theoretically, it can grow
indefinitely.
Cheap: No API fees are required
Searchable: A semantic index has been built
Manthan stated that it is based on this concept that
Clawdbot has transformed AI from a
“conversational tool” back into a “long-term
collaborator.”


---
*Page 8*


Anti-industry design: Markdown files are enough,
no need for “context windows”.
Clawdbot’s core memory design can be
summarised in one sentence:
Memory is just Markdown.
It has no proprietary database, no private cloud
format, and no internal state that you can’t
understand. Its default directory structure looks
like this:
~/clawd/
├── MEMORY.md - Layer 2: Long-term cura
└── memory/
├── 2026-01-26.md - Layer 1: Today's notes
├── 2026-01-25.md - Yesterday's notes
├── 2026-01-24.md - ...and so on
└── ...
There are no “AI privileges”.
Two-layer memory design


---
*Page 9*


One noteworthy key design feature is that
Clawdbot divides memory into two layers.
First layer: Daily log (short-term, raw). This is
similar to a person’s work notebook.
It records everything you talked about today, the
decisions you made, and the preferences you
casually mentioned:
## 10:30 AM - API Discussion
Decided to use REST over GraphQL.
## 4:00 PM - User Preference
User prefers TypeScript over JavaScript
The second layer: long-term memory (organisation
and sedimentation). This can be understood as the
human brain’s “knowledge base”.
When certain information is repeatedly
mentioned, confirmed, or cited, the agent will
organise it into… MEMORY.md ，


---
*Page 10*


Two-layer memory design
This step is equivalent to upgrading from a
notepad to common sense.
# Long-term Memory
## User Preferences
- Prefers TypeScript over JavaScript
- Likes concise explanations
- Working on project "Acme Dashboard"
## Important Decisions
- 2026-01-15: Chose PostgreSQL for database
- 2026-01-20: Adopted REST over GraphQL
- 2026-01-26: Using Tailwind CSS for styling
## Key Contacts
- Alice (alice@acme.com) - Design lead
- Bob (bob@acme.com) - Backend engineer
The AGENT.md file, which is automatically loaded
at session runtime, specifies some principles for
reading these memories:
SOUL.md ( Note: The “soul” here is also what
creator Peter calls the only secret that hasn’t been


---
*Page 11*


fully open-sourced. ) tells you who it is.
USER.md tells the agent who it is serving.
The file memory/YYYY-MM-DD.md stores the
current context.
If in a session, you also need to read MEMORY.md.
## Every Session
Before doing anything else:
1. Read SOUL.md — this is who you are
2. Read USER.md — this is who you are helping
3. Read memory/YYYY-MM-DD.md (today and
yesterday) for recent context
4. If in MAIN SESSION (direct chat with your
human), also read MEMORY.md
Don’t ask permission, just do it.


---
*Page 12*


Interestingly, Peter also set a special rule: Don’t ask
for permissions, just do it!
How are memory files indexed?
Once the memory files are saved, the background
process will slice these memories and create a
vector semantic index.
┌────────────────────────────────────────────
│ 1. File Saved
│ ~/clawd/memory/2026-01-26.md
└────────────────────────────────────────────
│
▼
┌────────────────────────────────────────────
│ 2. File Watcher Detects Change
│ Chokidar monitors MEMORY.md + memory/**/*.md
│ Debounced 1.5 seconds to batch rapid writes
└────────────────────────────────────────────
│
▼
┌────────────────────────────────────────────
│ 3. Chunking
│ Split into ~400 token chunks with 80 token over
│
│ ┌────────────────┐
│ │ Chunk 1 │
│ │ Lines 1-15 │──────┐
│ └────────────────┘ │
│ ┌────────────────┐ │ (80 token overlap


---
*Page 13*


│ │ Chunk 2 │◄─────┘
│ │ Lines 12-28 │──────┐
│ └────────────────┘ │
│ ┌────────────────┐ │
│ │ Chunk 3 │◄─────┘
│ │ Lines 25-40 │
│ └────────────────┘
│
│ Why 400/80? Balances semantic coherence vs gran
│ Overlap ensures facts spanning chunk boundaries
│ captured in both. Both values are configurable.
└────────────────────────────────────────────
│
▼
┌────────────────────────────────────────────
│ 4. Embedding
│ Each chunk -> embedding provider -> vector
│
│ "Discussed REST vs GraphQL" ->
│ OpenAI/Gemini/Local ->
│ [0.12, -0.34, 0.56, ...] (1536 dimensions)
└────────────────────────────────────────────
│
▼
┌────────────────────────────────────────────
│ 5. Storage
│ ~/.clawdbot/memory/<agentId>.sqlite
│
│ Tables:
│ - chunks (id, path, start_line, end_line, text,
│ - chunks_vec (id, embedding) -> sqlite-vec
│ - chunks_fts (text) -> FTS5 full-
│ - embedding_cache (hash, vector) -> avoid re-e
└────────────────────────────────────────────


---
*Page 14*


Note the following:
sqlite-vec is an SQLite extension that enables
vector similarity searches to be performed directly
in SQLite, without an external vector database.
FTS5 is the full-text search engine built into SQLite,
supporting BM25 keyword matching.
Together, they enable OpenCLAW to run hybrid
searches (semantic search + keyword search) from
a single lightweight database file.
Trick: How does it “remember” these
memories?
Here comes the important part.
OpenClaw never dumps all its memories into the
context at once. Its approach is simple: search
first, then inject.
How do I perform a search?


---
*Page 15*


Whenever “past events” are involved, the agent
must first go through a memory search process:
Vector semantic search (understanding what you
are saying)
Search for the keyword BM25 (make sure no
proper nouns are missed).
Weighted fusion of the two:
finalScore = 0.7 * semantic + 0.3 * keyword
The result is not relevant enough, so it is
discarded.
What does this mean? It means the context should
contain only the memories that are truly needed
at the moment, rather than “I’m afraid of
forgetting, so I fit everything in.”
One detail: No external database was used.
Many people overlook this point.


---
*Page 16*


As mentioned above, all the indexes are in a single
local .sqlite file.
Clawdbot’s vector search does not use external
vector databases, but rather SQLite, sqlite-vec, and
FTS5. It has no SaaS dependencies.
This also reveals Peter’s design philosophy for
“personal agents”: a personal AI assistant should
be a single file, portable, and backable.
How to handle long conversations? Context
window.
The reality is harsh: even the largest context
window will eventually run out of space.
Opeenclaw solution is straightforward:
compression. ( Editor’s note: This is similar to the
approach taken by Codex, which OpenAI revealed
last weekend; it also involves compression.)
Summarise the early conversations into a
structured summary.


---
*Page 17*


Retain the most recent original message
Write the summary to disk instead of just storing
it in the prompt.
There’s a special step here: before compression,
the memory is forcibly refreshed. In other words,
before the model “forgets,” it writes the important
information into the Markdown file.
This step is very clever, as it compresses the
context while avoiding the classic mistake of
“inadvertently erasing key decisions when
summarising”.
┌────────────────────────────────────────────
│ Context Approaching Limit
│
│ ████████████████████████████░░░░░░░░ 75% o
│ ↑
│ Soft threshold crossed
│ (contextWindow - reserve - softT
└────────────────────────────────────────────
│
▼
┌────────────────────────────────────────────
│ Silent Memory Flush Turn


---
*Page 18*


│
│ System: "Pre-compaction memory flush. Store durabl
│ memories now (use memory/YYYY-MM-DD.md).
│ If nothing to store, reply with NO_REPLY.
│
│ Agent: reviews conversation for important info
│ writes key decisions/facts to memory files
│ -> NO_REPLY (user sees nothing)
└────────────────────────────────────────────
│
▼
┌────────────────────────────────────────────
│ Compaction Proceeds Safely
│
│ Important information is now on disk
│ Compaction can proceed without losing knowledge
└────────────────────────────────────────────
Multiple agents, multiple personalities, but their
memories are isolated from each other.
OpenCLAW supports multiple agents:
Personal, work, experimental, automation scripts
Each Agent has an independent workspace,
memory, and index, and, by default, they do not
read each other’s data.


---
*Page 19*


You can make your “life assistant” on WhatsApp
completely unaware of the work you do on Slack.
This is almost a luxury feature in today’s AI
products.
~/.clawdbot/memory/ # State directory (i
├── main.sqlite # Vector index for
└── work.sqlite # Vector index for
~/clawd/ # "main" agent works
├── MEMORY.md
└── memory/
└── 2026-01-26.md
~/clawd-work/ # "work" agent works
├── MEMORY.md
└── memory/
└── 2026-01-26.md
Summary: Four principles of the Clawdbot
memory system
Clawdbot’s memory system succeeded because it
followed several key principles:
1. Transparency is better than a black box.


---
*Page 20*


Memory uses a plain Markdown format. Users can
read, edit, and version control it. It does not use
any obscure databases or proprietary formats.
2. Search over injection
Instead of stuffing all information into the context,
the agent searches for relevant information. This
maintains the context's focus while reducing costs.
3. Persistence is superior to session-based.
Important information is stored not only in the
chat history but also in files on the disk.
Compression cannot delete already saved content.
4. Hybrid search is superior to single search.
A vector search alone cannot provide an exact
match, and a keyword search alone cannot capture
semantic information. Hybrid search, however,
can achieve both.


---
*Page 21*


What really matters: Users take control of their
own data
Looking back, if we focus just on the
implementation, OpenClaw isn’t mysterious. But as
Peter originally intended when he created it:
“This year will be the year of personal agents, and
big companies like OpenAI and Anthropic will
likely dominate this field. But I want to make a
different choice: you can control your own data
instead of handing over more data to these giants.”
Therefore, it sends a signal:
AI’s memories are beginning to return to users'
hands.
It can be stored on a local disk, and users can
operate it like their own chat history — readable,
controllable, deletable, and transferable.
Clearly, this route is more popular with users. This
explains why it was all over social media at the


---
*Page 22*


beginning of 2026.
After all, when agents begin to accompany users
for extended periods, and when AI no longer just
answers questions but participates in decision-
making, execution, and collaboration, memory
transforms from a “function” into a “power.”
Whoever possesses this memory determines
which side the AI will ultimately take.
Reference :
https://manthanguptaa.in/posts/clawdbot_memo
ry/
󰩃
I am an AI Generative expert! If you want to
collaborate on a project, drop an inquiry here or
book a 1-on-1 Consulting Call With Me.
OpenClaw + Ollama + Security Guide: The
ULTIMATE LOCAL AI A i t t A t h
At the end of 2025, an open source project
dd l d th i t t th
pub.towardsai.net


---
*Page 23*


The New Nano Banana 2 + OCR + Claude
C d P f l AI OCR PDF Edit
Yesterday, when I was trying to draw an
ill t ti th t I ll i t i t t
pub.towardsai.net
How to build Claude Skills 2.0 Better than
99% f P l
“It’s a pain to give the same instructions to
th AI ti ” “Th AI b
pub.towardsai.net
This story is published on Generative AI. Connect
with us on LinkedIn and follow Zeniteq to stay in
the loop with the latest AI stories.
Subscribe to our newsletter and YouTube channel
to stay updated with the latest news and updates
on generative AI. Let’s shape the future of AI
together!


---
*Page 24*


Data Science Machine Learning Programming
Technology Artificial Intelligence
Published in Generative AI
Follow
82K followers · Last published 17 hours ago
Stay updated with the latest news, research, and
developments in the world of generative AI. We cover
everything from AI model updates, comprehensive
tutorials, and real-world applications to the broader
impact of AI on society. Work with us:
jimclydegm@gmail.com
⾼達烈
Written by Gao Dalie ( )
Follow
9.3K followers · 1 following
NC State Uni (Research Assistant), Learn AI Agent,
LLMs, RAG & Generative AI. See everything I have to
offer at the link below: https://linktr.ee/GaoDalie_AI
Responses (1)


---
*Page 25*


To respond to this story,
get the free Medium app.
BOOKS THAT MADE ME THINK ?
Mar 16
The most interesting part here isn’t the tech — it’s the philosophy.
If AI memory lives on company servers, the assistant ultimately serves
the company.
If memory lives on your disk, the assistant serves you.
1
⾼達烈
More from Gao Dalie ( ) and
Generative AI
In by ⾼達 In by
Towards … Gao Dalie ( … Generati… MohamedAbdel…
PaddleOCR + hybrid Atlassian Just Fired Its
t i l + R k CTO f AI Y


---
*Page 26*


In 2026, Generative AI will 1,600 people lost their jobs.
h d it “ i ” t Th CTO l t hi Th l
Jan 3 Mar 19
In by In by ⾼達
Generativ… Jim Clyde Mo… Towards … Gao Dalie ( …
The Best AI Diagram RLM: The Ultimate
T l t B t Y E l ti f AI?
Diagrimo is an AI tool that lets During the weekend, I scrolled
t t t i t di th h T itt t h t
Jan 23 Jan 10
⾼達烈
See all from Gao Dalie ( ) See all from Generative AI
Recommended from Medium


---
*Page 27*


In by In by
AI Advanc… Marco Rodrigu… Towards AI Moun R.
10 Tips to Make Your I Built My Own Local AI
Lif E i With A t ith O Cl
Learn the most useful A real field report on a VM
d h t i t ll Ub t t D k
Mar 7 Mar 10
In by Przemek Chojecki
Activated… Adi Insights and…
How I turned a
I Ignored 40+
R b Pi 4 i t
O F Alt ti
From Blank SD Card to AI
Everyone is building agent
A t S tti U O Cl
f k M t P th
Mar 21 Mar 12


---
*Page 28*


In by In by
AI Advances Jing Hu Activated … Mandar Karhad…
Raising Lobsters: 200,000 Devices. One
I id Chi ’ N ti Ad i P d H
Why are retirees, students, Stryker Corporation’s
d h i li i t b it
Mar 17 Mar 16
See more recommendations