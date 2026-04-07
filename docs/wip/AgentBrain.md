# AgentBrain

*Converted from: AgentBrain.PDF*



---
*Page 1*


Open in app
8
Search Write
Member-only story
Getting Started with
Agent Brain: From Zero
to Semantic Search in
15 Minutes
Mastering Local Semantic Search with Agent
Brain: A Step-by-Step Guide
Rick Hightower Following 24 min read · Mar 22, 2026


---
*Page 2*


272 1
Ready to supercharge your AI projects? Discover
how to set up Agent Brain in just 15 minutes for
powerful local semantic search! Say goodbye to
context loss and hello to instant, intelligent
codebase indexing. Dive into our step-by-step
guide and transform your development
experience!
This guide provides a step-by-step process for
installing and configuring Agent Brain 9.3.0 for
local semantic search using Ollama. It addresses
common challenges faced by AI developers, such
as the limitations of large language models in
retaining context. Agent Brain allows for local
indexing of codebases and documentation,
enabling efficient semantic and document
searches without requiring API keys. Key steps
include installation, configuration via a guided
wizard, project initialization, starting the server,
and indexing folders, with emphasis on avoiding


---
*Page 3*


common mistakes and optimizing search quality
through dual GraphRAG setups.
Check out the Agent Brain latest releases. If you
need help installing, reach out.
The Problem Every AI Agent Developer
Hits
You spend forty-five minutes explaining your
project layout to Claude Code. You describe which
modules handle authentication, where the retry
logic lives, and how the plugin system connects to
the core. The session ends. Next morning, you
open a new conversation and the agent is blank
again: no memory of anything you covered.
This is not a bug in Claude Code. It is a
fundamental architectural constraint. Large
language models work within a context window:
they see what you paste in and nothing else. When
the session resets, so does the context.


---
*Page 4*


Agent Brain solves this with a different approach:
instead of asking the model to remember things,
you give it a local search engine it can query on
demand. Agent Brain is a local RAG (Retrieval-
Augmented Generation) server that indexes your
codebase, documentation, and notes. When an AI
agent needs to find something, such as the
authentication retry logic, the relationship
between two modules, or the configuration option
you documented last month, it queries Agent Brain
and gets back ranked results in milliseconds.
I actually use it to index other code bases (other
microservices, event buses and IaC code). I also
download governance documents, PRDS,
requirements from confluence and tickets,
milestones, stories and related tasks from JIRA.
Then I index them all.
No API keys. No per-query cloud costs. Everything
can run locally via Ollama. Or, you can use Gemini,
GPT or Anthropic Claude models.


---
*Page 5*


This guide walks through a real first-time
installation for local semantic search. You will see
the actual commands, the actual terminal output,
and the actual errors, including the startup
timeout that catches most new users on their first
run.
By the end, you will have a running Agent Brain
instance with:
Semantic search over your codebase with AST-
aware chunking
Document search with LangExtract semantic
entity extraction
A dual GraphRAG setup that understands code
relationships and prose concepts
Zero API keys needed (all local via Ollama)
Here is the full system you are building:


---
*Page 6*


Every component in that diagram runs on your
machine. The AI agent sends a natural-language
query to Agent Brain, Agent Brain searches two
indexes in parallel (semantic and keyword),
merges the results, re-ranks them with a cross-
encoder model, and returns the top results with
file paths and line numbers. The whole round-trip
typically takes under a second.


---
*Page 7*


Agent Brain Wizards: You don’t have to do
anything but answer questions
/agent-brain-install
/agent-brain-setup
We have plugins and skills for Claude, OpenCode,
Codex and the Gemini CLI. You literally just have
to run the above two commands and they walk you
through the complete AgentBrain setup.
After you are set up, you just run
/agent-brain-start
/agent-brain-index <use natural language to tell codi
We make it really easy to setup
Ollama or Anthropic or OpenAI or Gemini


---
*Page 8*


ChromaDB or Postgres
Cache layers
Chunking strategies
Index code folders
Index document folders
Wizard checks Prerequisites
Before you start, the install wizard will confirm
you have the following installed and running. You
need at least 16 GB of RAM to run nomic-embed-
text alongside a full reasoning model like mistral-
small3.2 simultaneously.
Python 3.10 or higher (3.12 is the practical
recommendation for AI projects in 2026):
Python 3.10 or higher (3.12 is the practical
recommendation for AI projects in 2026):
python --version
# Python 3.12.9


---
*Page 9*


uv (the fast Python package manager, with the uv
binary in your PATH):
# Install uv if you don't have it
curl -LsSf <https://astral.sh/uv/install.sh> | sh
Ollama running locally with at least two models
pulled:
# Pull the required models
ollama pull nomic-embed-text
ollama pull mistral-small3.2
Verify Ollama is up and your models are available:
ollama list
# NAME ID SIZE
# nomic-embed-text:latest ... 274 MB
# mistral-small3.2:latest ... 15 GB
If ollama list returns an error, start the Ollama
service first: ollama serve.


---
*Page 10*


Step 1: Install Agent Brain
The recommended method is uv tool install.
This installs Agent Brain as a global CLI tool you
can invoke from any directory, in an isolated
virtual environment that cannot conflict with your
project dependencies.
# Check the latest published version before pinning
curl -sf <https://pypi.org/pypi/agent-brain-rag/json>
python3 -c "import sys,json; print(json.load(sys.st
# Latest available: 9.3.0
# Install as a global uv tool (isolated from your pro
uv tool install agent-brain-cli==9.3.0
# Confirm the installation succeeded
agent-brain --version
# agent-brain, version 9.3.0
If you prefer pip and do not mind managing the
environment yourself:
pip install agent-brain-cli==9.3.0


---
*Page 11*


Why pin to a specific version? Agent Brain 9.3.x is
the current stable series. Pinning prevents a future
breaking change from affecting your existing
index data when you upgrade other tools.
Why uv over pip? uv tool install creates an
isolated environment automatically, installs
roughly 10x faster than pip, and makes the agent-
brain command available globally. Most users have
Agent Brain installed and ready in under 10
seconds.
Step 2: Configure Agent Brain for Local
Semantic Search
Agent Brain uses a guided configuration wizard.
Run it once before your first init:
agent-brain config setup


---
*Page 12*


The wizard asks 8 questions. Here is what each one
means, what the right choice is for a local-first
Ollama RAG setup, and why.
Q1: Provider Setup
The wizard probes your environment for available
AI providers before asking you to choose. With
Ollama running locally, you will see something
like:
Pre-flight detection:
✅
Ollama: Running
✅
Models: nomic-embed-text, mistral-small3.2:lates
❌
OpenAI API key: not set
❌
Anthropic API key: not set
Choose: Ollama + Mistral.
This selects nomic-embed-text as the embedding
model (for turning text into searchable vectors)
and mistral-small3.2:latest as the summarization
model (used by GraphRAG to extract concepts
from your documents, and to create semantically


---
*Page 13*


related block). Everything runs locally: no API
keys, no per-query costs.
Understanding Your Embedding Model Options:
The embedding model converts text into a high-
dimensional vector, which is a list of numbers that
captures semantic meaning. Two texts with similar
meaning produce vectors that are close together in
this space; that is what makes semantic search
work.
Agent Brain supports several embedding models
through Ollama. Here is how the main options
compare:
Agent Brain supports several embedding models
through Ollama. Here is how the main options
compare:
nomic-embed-text
Context Window: 8192 tokens


---
*Page 14*


Size on Disk: 274 MB
Retrieval Quality: ~57% (MTEB)
Best For: Speed-sensitive local use
BGE-M3
Context Window: 8192 tokens
Size on Disk: 1.2 GB
Retrieval Quality: ~72% (MTEB)
Best For: Highest accuracy, more RAM
mxbai-embed-large
Context Window: 512 tokens
Size on Disk: 670 MB
Retrieval Quality: ~65% (MTEB)
Best For: Balanced performance, shorter
documents
The practical recommendation is nomic-embed-text
for a first install. It fits in RAM alongside a full-size


---
*Page 15*


reasoning model, starts fast, and handles 8192-
token context, meaning even large source files
rarely get truncated mid-function.
When to consider BGE-M3 instead: If retrieval
accuracy matters more than speed and memory
footprint, BGE-M3 scores significantly higher on
retrieval benchmarks. A codebase with highly
similar function names or where small semantic
differences matter is a good candidate. The trade-
off is 4x the disk footprint and slower embedding
generation.
Important caveat about Ollama context limits:
Ollama’s default serving configuration may cap
nomic-embed-text at 2048 tokens rather than its full
8192-token capability. If you index large files and
see embeddings that miss content from later in
long functions, add num_ctx: 8192 to your Ollama
model configuration. Agent Brain's
troubleshooting guide covers this in detail.


---
*Page 16*


Q2: Storage Backend
Choose: ChromaDB (the default).
ChromaDB is Agent Brain’s recommended vector
store. It runs embedded in the same process, so
there is no separate database server to install,
manage, or keep running. Vectors persist to disk in
your .agent-brain/data/ directory and survive
server restarts.
Why not Postgres with pgvector or Pinecone?
Those are excellent choices for production multi-
user deployments where you need concurrent
writes and cloud durability. For a single-developer
local setup, they add operational overhead with no
practical benefit. ChromaDB is the right default;
you can migrate later if your needs change. We do
support Postgres with vectordb.
Q3: GraphRAG Mode for Code and
Documents


---
*Page 17*


This is the most consequential configuration
decision. Take a moment to understand it.
What Is RAG, and What Does GraphRAG Add?:
Standard RAG (Retrieval-Augmented Generation)
works by converting your documents into vectors
and storing them in a vector database. When you
search, your query also converts to a vector, and
the database finds the stored vectors most similar
to it. This handles point lookups well: “show me
the retry function” finds the retry function.
Where standard RAG struggles is multi-hop
questions: “what calls the retry function, and what
does the calling function return to its caller?”
Standard RAG has no concept of relationships
between chunks; each chunk is an independent
island. We do add context aware headers to each
chunk and provenance meta-data. Following the
guidelines of Anthropic Vector RAG.


---
*Page 18*


GraphRAG adds a knowledge graph layer on top of
the vector index. It analyzes your code and
documents to extract entities (functions, classes,
concepts) and the relationships between them
(calls, imports, inherits-from, mentions). When
you search, Agent Brain traverses this graph to
follow relationships, not just find similar text.
Research shows GraphRAG achieves roughly 86%
accuracy on complex multi-hop questions,
compared to 32–76% for standard RAG. For
codebase navigation such as “show me everything
involved in the authentication flow,” this difference
is significant.
The Dual-Mode Setup: AST for Code, LangExtract
for Docs:
Agent Brain uses two different extraction
strategies depending on content type, and you
should enable both:


---
*Page 19*


AST extraction for source code: AST stands for
Abstract Syntax Tree (the structured
representation a programming language’s parser
produces from source code). Agent Brain’s AST
extractor reads this tree directly to extract import
relationships, function call graphs, and class
hierarchies. It requires no LLM calls. It is fast,
deterministic, and works with Python, JavaScript,
TypeScript, Go, and other supported languages.
BM25 is always added.
BM25: Precision Search for Identifiers and Exact
Matches:
While vector similarity search excels at finding
semantically related content and GraphRAG helps
traverse relationships between code entities, there
is a third retrieval dimension that is often the
missing link in production RAG systems: exact-
match keyword search.
This is where BM25 becomes critical.


---
*Page 20*


What is BM25? BM25 (Best Match 25) is a
probabilistic ranking function used in information
retrieval. Unlike semantic embeddings that
capture meaning, BM25 is a term-frequency
algorithm that scores documents based on how
often your exact query terms appear, weighted by
how rare those terms are across the entire corpus.
Think of it this way: if you search for “TICKET-
4729” in your codebase, semantic similarity is
useless — the embedding model sees random
digits and produces a generic vector. BM25,
however, recognizes this as a rare exact sequence
and returns every location where “TICKET-4729”
appears, ranked by frequency.
Why Agent Brain Includes BM25 Alongside Vector
Search:
Real-world development involves precise
identifiers that have no semantic meaning:
Ticket IDs: JIRA-8452, TICKET-4729


---
*Page 21*


Job or transaction IDs: job_3a8f2b91, txn-
20260312-4821
Function or variable names:
parse_legacy_format_v2
Error codes: ERR_CONNECTION_TIMEOUT, E404
Vector similarity struggles with these because
embeddings smooth over exact characters into
distributional semantics. BM25 treats them as
literal strings and finds exact or near-exact
matches.
Fusion Search: Combining All Three Retrieval
Modes:
Agent Brain uses fusion search to combine results
from BM25, vector similarity, and GraphRAG into a
single ranked result set. Here is how it works:
1. Your query runs against the BM25 index (fast
keyword match)


---
*Page 22*


2. The same query converts to a vector and
searches the vector index (semantic similarity)
3. If GraphRAG is enabled, the system also
traverses the knowledge graph (relationship-
aware retrieval)
4. Results from all three sources merge using
Reciprocal Rank Fusion (RRF), which
normalizes scores across different ranking
systems and promotes candidates that appear
highly ranked in multiple result sets
5. The reranker cross-encoder reads each fused
candidate with your query and produces a final
relevance score
The practical effect: if you search for
“authentication flow for TICKET-8291,” Agent Brain
returns:
Files mentioning TICKET-8291 literally (BM25)
Functions semantically related to
“authentication flow” (vector similarity)


---
*Page 23*


The call graph of functions involved in
authentication (GraphRAG)
Fusion search is what makes Agent Brain effective
for both conceptual exploration (“show me retry
logic”) and forensic debugging (“where is
job_3a8f2b91 referenced”). It is the missing link
that closes the gap between semantic
understanding and precise recall.
LangExtract for documents: Markdown files, text
notes, and documentation do not have syntax
trees. LangExtract uses your summarization model
(mistral-small3.2) to read each document and
extract semantic entities: concepts, named things,
and relationships expressed in prose. This is
slower than AST extraction (it requires LLM
inference for each document) but far more
effective than treating documentation as
unstructured text.


---
*Page 24*


When the wizard asks whether to enable
GraphRAG, choose the option for both: AST for
code and LangExtract for documents.
The combination gives you graph-aware search
across your entire project without paying LLM
inference costs for code files.
Q4: LangExtract Installation
If LangExtract is not yet installed, the wizard offers
to install it for you. Choose “Install now.”
If the wizard’s installation fails, or if you want to
install manually:
# This fails without an active virtual environment ac
uv pip install langextract
# error: No virtual environment found
# Use --system to install into the system Python inst
uv pip install --system langextract
# Installed 4 packages in 3ms


---
*Page 25*


The --system flag tells uv to install into the system-
level Python rather than a project virtual
environment. The wizard handles this
automatically, but knowing the flag matters if you
need to reinstall later.
Q5-Q8: Cache, File Watcher, Reranking,
Deployment
Accept the defaults for all four of these on your
first install. Here is what each setting does and
why the default is correct:
Cache (accept: Enabled): Agent Brain uses a two-
tier cache: an in-memory LRU cache for the most
recent queries and a SQLite cache on disk for
longer-term storage. Files that have not changed
since the last index do not get re-embedded. On a
codebase of 50,000 lines, this reduces re-index
time from minutes to seconds for incremental
changes.


---
*Page 26*


File Watcher (accept: 30-second debounce): When
enabled, Agent Brain monitors your indexed
folders for changes and queues re-index jobs
automatically. The 30-second debounce prevents it
from re-indexing while you are still actively editing
a file. For most development workflows, this
means your index stays current without you
thinking about it.
Reranking (accept: sentence-transformers
enabled): This downloads a ~90 MB cross-encoder
model (cross-encoder/ms-marco-MiniLM-L-6-v2) on
first use. A cross-encoder re-ranks search
candidates by reading the query and each
candidate together; this is a slower but
significantly more accurate scoring method than
the initial vector similarity. This is what turns
"okay results" into "the right result at position 1."
Accept this unless you are extremely memory-
constrained.


---
*Page 27*


Deployment (accept: Local): Self-explanatory for a
local setup.
The Resulting Configuration File
The wizard writes ~/.agent-brain/config.yaml with
everything you selected:
embedding:
provider: "ollama"
model: "nomic-embed-text"
base_url: "<http://localhost:11434/v1>" # Ollama's
summarization:
provider: "ollama"
model: "mistral-small3.2:latest" # Used by La
base_url: "<http://localhost:11434/v1>"
storage:
backend: "chromadb" # Embedded v
graph_rag:
use_code_metadata: true # Enable AST
doc_extractor: "langextract" # Enable LLM
reranking:
enabled: true
provider: "sentence-transformers"
model: "cross-encoder/ms-marco-MiniLM-L-6-v2" # ~9
cache:
enabled: true
max_size: 1000 # Entries in
ttl_seconds: 3600 # Cache entr
file_watcher:


---
*Page 28*


enabled: true
debounce_seconds: 30 # Wait 30s o
The wizard also adds an environment variable to
your shell profile:
export AGENT_BRAIN_WATCH_DEBOUNCE_SECONDS=30
Reload your shell profile (source ~/.zshrc or open
a new terminal) before continuing.
Step 3: Initialize the Project
Agent Brain keeps a separate index for each
project. Run init from your project's root
directory:
cd /path/to/your/project
agent-brain init


---
*Page 29*


Expected output:
╭────────────────────── Agent Brain Initialized ─
│ Project initialized successfully!
│ State dir: .agent-brain/
│ Config: .agent-brain/config.json
╰────────────────────────────────────────────
This creates a .agent-brain/ directory in your
project root:
.agent-brain/
├── config.json # Project-specific settings (chun
├── data/ # Vector and BM25 indexes (popula
└── logs/ # Server logs, including startup
The project configuration file:
{
"chunk_size": 512, // Maximum tokens per inde
"auto_port": true, // Scan ports 8000-8100 an
"exclude_patterns": [ // Folders and file patter
".git/",
"node_modules/",
"__pycache__/",


---
*Page 30*


"*.pyc",
".env"
],
"data_dir": ".agent-brain/data",
"log_dir": ".agent-brain/logs"
}
Understanding the Two-Level
Configuration Hierarchy
Agent Brain separates global settings (which
models to use, how to connect to Ollama) from
project settings (how to chunk code, which files to
skip). This lets you share one Ollama setup across
all your projects while tuning index behavior per
project.
The diagram below shows how these two files
combine at runtime:


---
*Page 31*


Agent Brain Config locations for user and project
FileScopeWhat It Controls~/.agent-
brain/config.yamlAll projects on this
machineEmbedding provider, models, storage
backend, reranking.agent-brain/config.jsonThis
project onlyChunk size, port scanning, file
exclusion patterns
You can also create .agent-brain/config.yaml inside
a project directory to override the global provider
settings for that project. This is useful when one
project needs higher-accuracy embeddings (BGE-
M3) while others use the faster nomic model.


---
*Page 32*


About auto_port: true: When multiple projects
run simultaneously, each Agent Brain instance
needs its own port. With auto_port enabled, the
server scans ports 8000 through 8100 and binds to
the first available one. You can run Agent Brain in
three different project directories at the same
time, and each will find a free port automatically.
Step 4: Start the Agent Brain Server
Agent Brain server startup in terminal showing
health status, cross-encoder model loading,


---
*Page 33*


ChromaDB initialization, and HEALTHY status
confirmation on dark terminal background
agent-brain start
On the first run of a fresh install, you may see this
immediately after the startup message:
Starting server on <http://127.0.0.1:8000>...
Error: Server failed to start
Check logs: .agent-brain/logs/server.err
Do not panic. This is not a crash. It is a startup
timeout issue, and it has a simple fix. This may not
be a problem in the next version or depending on
which options you choose.
Why This Happens
When Agent Brain starts for the first time after you
enable reranking, it needs to download and load
the cross-encoder model (cross-encoder/ms-marco-


---
*Page 34*


MiniLM-L-6-v2, ~90 MB). Depending on your
connection speed and machine, this takes 30 to 90
seconds.
The default agent-brain start command checks
whether the server became ready within 30
seconds. When model loading takes longer than
that threshold, the timeout check fails and reports
an error, even though the server itself continues
starting correctly in the background.
To confirm this is the issue and not an actual
crash, check the log:
cat .agent-brain/logs/server.err
# If you see lines about "downloading model" or "load
# the server is still initializing. Wait 60 seconds a
agent-brain status
The Fix: Use — foreground Mode
The most reliable solution is to start the server in
foreground mode, which has no startup timeout:


---
*Page 35*


# Foreground mode: the server runs in your terminal,
agent-brain start --foreground
In foreground mode you see the startup logs
directly in your terminal, including the model
download progress. Once you see “Server ready on
http://127.0.0.1:8000", the server has fully loaded.
After the model caches on disk, agent-brain start
works fine for subsequent launches; the model
loads from disk in a few seconds, well within the
timeout.
If your CLI version supports a timeout flag, you
can also extend the startup check:
# Verify whether --timeout is supported in your versi
agent-brain start --help | grep timeout
# If present, extend the startup check to 90 seconds
agent-brain start --timeout 90


---
*Page 36*


Which approach should you use? --foreground is
the confirmed workaround and works on all 9.3.x
versions. --timeout is present in some versions;
check your CLI help output before relying on it.
We should have this patched in 9.4.x.
Confirming the Server Is Ready
Once started, verify health:
agent-brain status
╭─────────────────────────────── Server Status
│ HEALTHY
│ Server is running and ready for queries
│ URL: <http://127.0.0.1:8000>
│ Version: 9.3.0
│ Documents: 0 (nothing indexed yet)
│ File Watcher: Running (0 folders watched)
╰────────────────────────────────────────────
A “Documents: 0” count is expected; you have not
indexed anything yet.


---
*Page 37*


About the ChromaDB telemetry error in logs:
After startup you may see lines like:
capture() takes 1 positional argument but 3 were give
This is a known bug in ChromaDB’s analytics
integration caused by a breaking API change in
PostHog v6.0.0. It does not affect search, indexing,
or any Agent Brain functionality. The fix ships in
ChromaDB 1.0.15 and later:
uv pip install --system "chromadb>=1.0.15"
You can also ignore it entirely; the error is
cosmetic.
This should be patched in 9.4.x.
Step 5: Index Your First Folders


---
*Page 38*


With the server running, you can start building the
index. The key concept: not all content should be
indexed the same way.
Code vs. Documents: Two Indexing
Strategies
Understanding the distinction between code
indexing and document indexing explains why
Agent Brain’s search quality exceeds full-text
search tools.
Source code with --include-code: Python,
JavaScript, Go, TypeScript, and other supported
languages have formal syntax. Agent Brain's AST
(Abstract Syntax Tree) extractor parses this syntax
to understand structure. Instead of splitting at
arbitrary token count boundaries (which might cut
a function in half), AST chunking respects the
code's natural units: a function stays in one chunk,
a class definition stays together, and imports group
with the code that uses them.


---
*Page 39*


The practical result: when you search for “the retry
handler,” you get the complete function back, not a
512-token fragment that starts midway through the
docstring.
Documents without --include-code: Markdown
files, plain text, and RST documentation do not
have syntax trees. For these, Agent Brain uses
LangExtract with your summarization model to
extract semantic entities: the concepts, named
things, and relationships the document discusses.
It then uses standard paragraph-aware chunking.
The graph layer for documents captures prose
relationships rather than code call graphs.
Here is how each content type flows through the
indexing pipeline:


---
*Page 40*


Both paths feed into the same ChromaDB vector
store and BM25 keyword index, which is why
hybrid search works across both code and
documentation in a single query.
The — allow-external Flag
By default, Agent Brain only indexes paths inside
your current project root (the directory where you
ran agent-brain init). This safety boundary
prevents accidental indexing of unrelated
directories.
To index folders outside your project root (other
projects, shared libraries, a documents folder), add
--allow-external:
# Code folder inside the project (no extra flags need
agent-brain index ./src --include-code
# Code folder outside the project root
agent-brain index /path/to/your/source-code --include
# Documents folder outside the project root
agent-brain index /path/to/your/documents --allow-ext


---
*Page 41*


When you run /agent-brain-index command in
Claude Code or OpenCode or Gemini, etc. it will
automate most of this for you. You will never have
to remember all of these command line
arguments, it might ask you if the directory is code
(or autodetect it). It will know when something is
external and pass the correct flags.
Queue Index Requests, Never Parallelize
This is the most common first-use mistake:
running multiple index commands at the same
time.
# DO NOT do this (parallel requests overload the requ
agent-brain index ./folder-a --include-code &
agent-brain index ./folder-b --include-code & # lik
agent-brain index ./folder-c --include-code & # lik
Agent Brain processes index jobs through a
sequential queue. The server handles one active
indexing operation at a time. When you send three
simultaneous HTTP requests, the server accepts


---
*Page 42*


the first and may timeout or reject the others
before they reach the queue.
The correct approach is to issue the commands
one at a time:
# DO this (each command queues a job, the server work
agent-brain index ./folder-a --include-code
agent-brain index ./folder-b --include-code
agent-brain index ./folder-c --include-code
# All three are now in the queue. The server processe
This is not slower overall. The server processes all
three jobs in the same sequence either way.
Sequential submission just ensures all three get
queued successfully.
Monitoring Index Progress
You do not need to wait for one folder to finish
before submitting the next. Once a job is in the
queue, submit more and watch the queue from a
separate terminal:


---
*Page 43*


# List all queued and active jobs
agent-brain jobs
# Stream job status updates in real time
agent-brain jobs --watch
# Inspect a specific job by ID
agent-brain jobs job_6d8b9de3e9dd
Example output from agent-brain jobs:
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━
┃ ID ┃ Status ┃ Source ┃ Folder ┃ P
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━
│ job_6d… │ running │ manual │ .../agent-brain │
│ job_91… │ pending │ manual │ .../rulez_plugin │
│ job_23… │ pending │ manual │ .../agent-memory │
│ job_e7… │ pending │ manual │ .../articles │
└─────────┴─────────┴────────┴───────────────
The first job actively indexes. The other three
queue and run in order when it completes.
You do not typically have to do this. Agent Brain
will do all this work for you using the commands,


---
*Page 44*


agents and skills that ship with the AgentBrain
plugin. We make it super easy to use.
Step 6: Verify Semantic Search Is Working
Once at least one index job completes, check the
document count in status:
agent-brain status
# Documents: 2847 (or however many were indexed)
Then run a search. Here is what happens behind
the scenes:
The two-stage process is what makes results
accurate. Stage 1 (parallel BM25 + vector search)


---
*Page 45*


casts a wide net, retrieving up to 40 raw
candidates. Stage 2 (cross-encoder reranking)
reads the query and each candidate together and
scores them as a pair, which is significantly more
accurate than vector similarity alone. The cross-
encoder is slower but only needs to evaluate 30–40
candidates, so the total latency stays low.
Run your first search:
agent-brain search "RAG retrieval implementation"
Results include:
Relevant code chunks or document excerpts
Relevance scores from the hybrid BM25 +
semantic search pass
File paths and line numbers for each result
Final ranking from the cross-encoder reranker


---
*Page 46*


For code files indexed with AST chunking, results
include structural context: the result identifies that
a matched method belongs to class
RetrieverPipeline, even when the search term only
appears in an inner method body.
Explore the two available search modes:
# Default: hybrid BM25 + semantic vector search
agent-brain search "retry logic with exponential back
# Graph-aware mode: follows code
relationships and concept connections
agent-brain search --mode graph "all
functions that call the retry handler"
The graph mode is particularly useful for impact
analysis (“what would break if I change this
function?”) and for understanding unfamiliar
codebases where you do not yet know the function
names to search for.


---
*Page 47*


Real-World Example: Researching a Live
Project with Agent Brain
The best way to understand Agent Brain’s value is
to see it in action. Right after completing the setup
in this article, the indexed folders were used to
research an entirely separate project: agent-
memory, a Rust-based episodic memory system
for AI agents.
I asked Agent Brain inside Claude to use the
research agent, then asked it to write about
another project we’re working on — agent-
memory, an episodic conversation search system. I
wanted to understand the architecture, purpose,
and design. This was entirely a natural language
search. Then it issued a series of queries to Agent
Brain.
The research agent ran 46 hybrid BM25+vector
queries against the indexed codebase:


---
*Page 48*


agent-brain query "agent memory salience detection im
agent-brain query "memory eviction expiration older c
agent-brain query "agent memory architecture design c
agent-brain query "append-only event log design decis
agent-brain query "RocksDB HNSW BM25 vector index sto
# ... 41 more targeted queries
In under 4 minutes, without opening a single file
manually, the research agent returned:
A complete architecture overview of the 6-layer
cognitive stack
All 8 Architecture Decision Records (ADRs) with
their trade-offs
The salience detection formula and
MemoryKind classification system
The retention policy matrices for vector and
BM25 indexes
The multi-agent storage strategies
The full milestone history from v1.0 MVP to v2.7


---
*Page 49*


This is the practical payoff of the installation you
just completed. The session transcript that
contained all those agent-brain index commands?
That indexed data is now searchable by meaning,
not just by filename or grep pattern.
💡
Key Distinction: agent-brain is “library
memory” for documents and code. agent-memory
(the project we researched) is “episodic memory”
for conversations. They solve complementary
problems: agent-brain answers “what does the
codebase in project A, B, C say about X?”, while
agent-memory answers “what were we discussing
last week about X?” See the companion article
agent-memory: Giving AI Agents Episodic Memory for
the full deep-dive.
What’s Next
You now have a fully operational Agent Brain
instance. Here are the natural next steps, roughly


---
*Page 50*


in order of immediate usefulness.
Add folders with automatic file watching:
# Index a folder and configure auto-reindex on file c
agent-brain folders add ./src --watch auto
Once you register a folder with --watch auto, Agent
Brain monitors it for changes and queues re-index
jobs as you edit files. With the 30-second
debounce, your index stays current throughout a
working session without manual intervention.
Connect Agent Brain to Claude Code: The agent-
brain Claude Code plugin provides /agent-
brain:agent-brain-search and related commands.
Once connected, AI agents in your project query
Agent Brain directly during development
conversations, finding relevant code and
documentation without you pasting it into context.


---
*Page 51*


Tune chunk size for your content: The default
chunk_size: 512 tokens works well for most Python
and JavaScript codebases. For projects with very
large files (long configuration files, extensive
documentation), increasing to 1024 reduces the
number of chunks and can improve result
coherence. Edit .agent-brain/config.json and re-
run the index commands for affected folders.
Experiment with BGE-M3 for higher retrieval
accuracy: If searches return results that are close
but not quite right, and you have the RAM budget
(1.2 GB for the model), switching to BGE-M3 as
your embedding model may noticeably improve
precision. Update model: "bge-m3" in ~/.agent-
brain/config.yaml and re-index your folders to
rebuild the vector store with the new embeddings.
Troubleshooting Common Issues


---
*Page 52*


Error: Server failed to start on first launch (some
of these should be fixed with the current release).
Cause: Reranker model download (~90 MB)
exceeds the 30-second startup timeout
Fix: Use agent-brain start --foreground for first
start; subsequent starts are fine
uv pip install langextract fails with "No virtual
environment found"
Cause: uv requires an active virtual environment
by default
Fix: Use uv pip install --system langextract
capture() takes 1 positional argument but 3 were
given in logs
Cause: ChromaDB PostHog telemetry bug;
cosmetic only, no impact on functionality
Fix: Upgrade with uv pip install --system
"chromadb>=1.0.15" or ignore it


---
*Page 53*


Index request times out or returns error
Cause: Too many simultaneous index requests
overloaded the request handler
Fix: Submit index commands one at a time; do
not use & to background them
Error: path outside project root
Cause: Attempting to index a folder outside the
project directory
Fix: Add --allow-external flag to the index
command
Embeddings seem to miss content from the end of
large files
Cause: Ollama default context cap is 2048
tokens, below nomic’s 8192 maximum
Fix: Add num_ctx: 8192 to your Ollama model
configuration


---
*Page 54*


agent-brain status shows HEALTHY but document
count stays at 0
Cause: Index job is still running or queued
Fix: Run agent-brain jobs --watch to see active
and pending jobs
Server binds to unexpected port (not 8000)
Cause: Another process is using port 8000 and
auto_port: true selected the next available port
Fix: Run agent-brain status to see the actual
bound URL
Re-indexing takes as long as the first index
Cause: Cache is disabled or the cache TTL
expired
Fix: Verify cache.enabled: true in ~/.agent-
brain/config.yaml; increase ttl_seconds if
needed


---
*Page 55*


Graph search returns no results
Cause: GraphRAG index not yet built or content
type mismatch
Fix: Ensure folders were indexed with --include-
code for source files; allow time for graph
extraction to complete
You installed Agent Brain 9.3.0 for local semantic
search in five steps:
1. Install: uv tool install agent-brain-cli==9.3.0
2. Configure: The 8-question wizard generates
~/.agent-brain/config.yaml with Ollama +
ChromaDB + dual GraphRAG (AST for code,
LangExtract for docs)
3. Initialize: agent-brain init from your project
root creates .agent-brain/ with project-specific
settings


---
*Page 56*


4. Start: agent-brain start --foreground avoids the
reranker model-download timeout on first
launch
5. Index: Queue folders sequentially with --
include-code for source code, without it for
documents
The two most common first-time mistakes:
Starting in background mode before the
reranker model caches (use --foreground the
first time)
Submitting multiple index commands in parallel
(always queue them one at a time)
The two configuration decisions that most affect
search quality:
nomic-embed-text with 8192-token context is the
right default; consider BGE-M3 if you need
higher accuracy and have the memory


---
*Page 57*


Dual GraphRAG (AST for code + LangExtract for
docs) gives you relationship-aware search across
your entire project at minimal LLM inference
cost
Agent Brain now listens on http://127.0.0.1:8000,
indexed and ready. Your AI agents have the
semantic memory they needed.
Have questions about your specific codebase setup
or embedding model choice? Drop them in the
comments below.
#AgentBrain #LocalLLM #RAG #AIAgents
#GenerativeAI #SoftwareEngineering #Ollama
#GraphRAG #DevTools #SemanticSearch
About the Author
Rick Hightower is a technology executive and data
engineer who led ML/AI development at a Fortune
100 financial services company. He created skilz,
the universal agent skill installer, supporting 30+


---
*Page 58*


coding agents including Claude Code, Gemini,
Copilot, and Cursor, and co-founded the world’s
largest agentic skill marketplace. Connect with
Rick Hightower on LinkedIn or Medium. Rick has
been doing active agent development, GenAI,
agents, and agentic workflows for quite a while. He
is the author of many agentic frameworks and
tools. He brings core deep knowledge to teams
who want to adopt AI.
AI Agent Claude Code Llamaindex Context Engineering
Harness Engineering
Written by Rick Hightower
Following
2.3K followers · 75 following
2026 Agent Reliability Playbook – Free Download DM
me 'PLAYBOOK' for the full version + personalized 15-
minute audit of your current agent setup (no pitch).


---
*Page 59*


Responses (1)
To respond to this story,
get the free Medium app.
Matt Hosner he/him
Mar 24
Very interesting article and project. The dual GraphRAG setup with AST
for code and LangExtract for docs is the architecture I've had an eye out
for.
Recently forked Deep Agents and building an open-source SDLC pipeline
(Superagents) that brainstorms… more
More from Rick Hightower


---
*Page 60*


Rick Hightower In by
Towards AI Rick Hightower
LangChain Deep
From “Vibe Coding” to
A t H d
Vi bl C di H
How LangChain Deep Agents
The open-source plugin that
H dl W ki M
dd b i t i TDD
Mar 17 Mar 14
Rick Hightower Rick Hightower
Save Hours: Stop Claude Code: How to
R ti Y lf t B ild E l t d
Mastering Claude Code: Mastering Claude Code Agent
St li Y D l Skill Eff ti St t i f
Mar 23 Mar 22
See all from Rick Hightower
Recommended from Medium


---
*Page 61*


Rick Hightower Reza Rezvani
Save Hours: Stop Claude Code Auto
R ti Y lf t M d Wh t
Mastering Claude Code: My day-one configuration
St li Y D l id d f lt l l
Mar 23 Mar 26
Ewan Mak In by
Google Cloud - Co… Esther …
Everything Claude
Why I Stopped
C d I id th 82K
I t lli A t Skill
Everything Claude Code (ECC)
Agent Skills are a brilliantly
h l t d 82 00
i l t th i ht
Mar 17 Mar 12


---
*Page 62*


In by In by
Level Up Coding Yanli Liu Graph P… Alexander Shere…
Claude Code Just Got Building Knowledge
Ch l I It E h? G h ith L l
For the production GraphRAG
i li th t ti t i
Mar 23 Mar 23
See more recommendations