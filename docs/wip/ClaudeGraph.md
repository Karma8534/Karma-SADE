# ClaudeGraph

*Converted from: ClaudeGraph.PDF*



---
*Page 1*


Open in app
Search Write
Illustration of Codegraph making connections
I Cut Claude Code
Exploration Time and
Costs by 30% With One
Tool


---
*Page 2*


CodeGraph gives Claude Code a pre-built
understanding of your code instead of making
it explore from scratch every session
Colby McHenry Following 5 min read · Jan 19, 2026
1.1K 39
The Exploration Tax
Every Claude Code user knows this feeling. You
open a fresh session, type a request, and watch the
exploration begin:
⏺
Explore(Explore /src/api/ structure)
⎿
Done (24 tool uses · 40.0k tokens · 59s)
⏺
Explore(Explore /src/components/ structure)
⎿
Done (32 tool uses · 57.0k tokens · 1m26s)
⏺
Explore(Explore /src/database/ structure)
⎿
Done (18 tool uses · 33.0k tokens · 51s)
Every. Single. Time.


---
*Page 3*


Claude has no memory of your codebase. So it
spawns Explore agents that crawl through your
files using grep, glob, and Read calls. Each tool call
burns tokens. Each file scanned eats into your
context window.
I timed it on one of my projects. 60 tool calls.
157,800 tokens. Nearly 2 minutes of exploration
before Claude even started working on my actual
request.
And here’s the frustrating part: when you close
that session, all that expensive knowledge
disappears. Next session? Start from scratch. Pay
the exploration tax again.
The Hacky Workarounds
I’m not the first person to notice this problem. The
community has come up with workarounds:


---
*Page 4*


1. Memory markdown files. People stuff
CLAUDE.md with codebase summaries,
architecture notes, file listings. It helps a little,
but Claude still doesn’t understand the
relationships. It’s just reading a document.
2. Subagents with their own markdown files.
Some folks create elaborate systems where
exploration agents update shared memory files.
Better, but still hacky. Still text-based. Still
missing the actual structure.
3. Manual context stuffing. Copy-pasting relevant
code into your prompts before asking questions.
Works, but tedious and doesn’t scale.
None of these solutions give Claude what it
actually needs: a real understanding of how your
code connects together.
What If Explore Agents Had a Map?


---
*Page 5*


That’s the idea behind CodeGraph. Instead of
scanning files blindly, Explore agents query a pre-
built semantic knowledge graph:
Which functions call which other functions
What classes inherit from what
Where interfaces are implemented
How imports connect files together
What the impact radius is when you change
something
This isn’t a text summary Claude has to interpret.
It’s a structured database that Claude can ask direct
questions to.
The Explore agents still run — but they’re
dramatically more efficient. Graph queries return
instant results. No more file-by-file scanning.
⏺
Explore(Explore /src/api/ structure)
⎿
Done (18 tool uses · 22.0k tokens · 34s)
⏺
Explore(Explore /src/components/ structure)


---
*Page 6*


⎿
Done (24 tool uses · 29.4k tokens · 56s)
⏺
Explore(Explore /src/database/ structure)
⎿
Done (14 tool uses · 18.0k tokens · 27s)
Real Benchmark Data
I ran the same complex task 3 times with and
without CodeGraph enabled:
Real Benchmark Data


---
*Page 7*


The verdict: Explore agents use ~30% fewer tokens
and ~25% fewer tool calls. The graph lookups are
simply more efficient than file scanning.
That’s real money saved on tokens and time for
every complex task.
5-Minute Setup
Requirements:
- Node.js 18+
- Claude Code
Just run one command:
npx @colbymchenry/codegraph


---
*Page 8*


5-Minute Setup
The interactive installer handles everything:
1. Configures the MCP server in ~/.claude.json
2. Sets up auto-allow permissions for CodeGraph
tools
3. Asks if you want to initialize your current project
4. Writes auto-sync hooks to settings.json (the
Claude Code hooks mentioned above)
5. Writes CLAUDE.md instructions for the project
or global you choose
Restart Claude Code, then initialize any project
you want to use it with:


---
*Page 9*


codegraph init -i
That’s it. 85 files indexed, 542 code symbols,
relationship edges mapped — all in under a half a
second.
How It Works
1. CodeGraph indexes your codebase once using
tree-sitter parsing. Every function, class,
method, and relationship goes into a local
SQLite database with vector embeddings.


---
*Page 10*


2. Claude Code connects via MCP. When it needs to
understand your code, it queries the graph
instead of exploring.
3. Claude gets exactly what it needs. Entry points,
related symbols, code snippets, caller/callee
relationships. All from a single tool call.
4. Uses Claude Code hooks to keep it fresh.
PostToolUse(Edit|Write) marks the index dirty,
and the Stop hook runs sync-if-dirty. It syncs
when Claude edits files.
The key difference from markdown-based
solutions: Claude isn’t reading a summary and
trying to interpret it. It’s querying a structured
database that already knows how your code
connects.
What You Get
🧠
Smart Context Building
The native Claude Explorer subagents will utilize


---
*Page 11*


CodeGraph to find files faster, come up with
analysis sooner, and spend far less tokens looking
for the right answers.
🔍
Semantic Search
Find code by meaning. Search “authentication”
and get login, validateToken, AuthService even
with different naming conventions.
📈
Impact Analysis
Know what breaks before you change it. Trace
callers, callees, and the full blast radius of any
symbol.
🌍
16+ Languages
TypeScript, JavaScript, Python, Go, Rust, Java, C#,
PHP, Ruby, C, C++, Swift, Kotlin, and Liquid (for
Shopify themes). All with the same API.
🔒
100% Local
No data leaves your machine. No API keys. No
external services. Just SQLite in your project.


---
*Page 12*


⚡
Always Fresh
Uses Claude Code hooks — PostToolUse(Edit|Write)
marks the index dirty, and the Stop hook runs
sync-if-dirty. It syncs when Claude edits files.
The Technical Details
CodeGraph uses tree-sitter to parse source code
into ASTs, extracting:
- Nodes: Functions, classes, methods, interfaces,
types, variables
- Edges: Calls, imports, extends, implements, type
references
Storage is a local SQLite database with:
- Full-text search via FTS5
- Vector embeddings for semantic search
(transformers.js)
- Graph traversal for impact analysis
The MCP server exposes tools Claude can call:
- codegraph_context builds comprehensive


---
*Page 13*


context for any task
- codegraph_search quick symbol search by name.
Returns locations only (no code).
- codegraph_callers/callees traces call
relationships
- codegraph_impact calculates change blast radius
Reference resolution handles the tricky parts:
matching calls to definitions across files, resolving
imports, linking inheritance, understanding
framework patterns.
NPM & GitHub
GitHub:
https://github.com/colbymchenry/codegraph
npm:
https://www.npmjs.com/package/@colbymchenry/
codegraph


---
*Page 14*


Stop wasting context on exploration. Give Claude a
map and let it get to work.
Claude Code Software Development Vibe Coding
Context Engineering Claude
Written by Colby McHenry
Following
280 followers · 56 following
Self-taught software engineer with 15+ years of
experience. Motivated to share my solutions with the
world!
Responses (39)
To respond to this story,
get the free Medium app.


---
*Page 15*


Sandeep
Jan 26
Interesting article. Thanks for sharing. Does the internal graph auto
update with new code changes/codebase changes?
29 4 replies
Chad Lewis
Jan 27
How is this different from using an LSP?
26 2 replies
Stuart Swerdloff
Jan 26
Why not use a graph db like kuzu? That's what I use in combination with a
variety of AST generators (and optional enrichment depending on the
language). Definitely cuts down on the tokens and time. Well done and
kudos for sharing
26 1 reply
See all responses


---
*Page 16*


Recommended from Medium
In by Agent Native
CodeX MayhemCode
Local LLMs That Can
Why Thousands Are
R l Cl d C d
B i M Mi i t
Small team of engineers can
Something strange happened
il b >$2K/
i l 2026 A l t
Feb 15 Jan 20
In by Reza Rezvani
Activated Thin… Shane Coll…
Your CLAUDE.md Is
Why the Smartest
P b bl W 7
P l i T h A
Boris Cherny’s file is 2.5k
The water is rising fast, and
t k Mi 15k Aft 3
f i f Ch tGPT


---
*Page 17*


Feb 13 Jan 23
In by In by
Predict Nov Tech Towards Deep L… Sumit Pa…
I’m Skeptical of AI hype Andrej Karpathy Just
b t h t h d B ilt E ti GPT i
When Anthropic, Google No PyTorch. No TensorFlow.
D Mi d d O AI ll J t P th d b i
Feb 2 Feb 15
See more recommendations