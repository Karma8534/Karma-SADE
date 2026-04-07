# CCintoanOS

*Converted from: CCintoanOS.PDF*



---
*Page 1*


Open in app
Search Write
AI Advances
Member-only story
I Turned Claude Code
Into an Operating
System. Here’s the
Blueprint.
How to configure Claude Code with hooks,
skills, agents, and zero-trust permissions. A
field-tested architecture that eliminates
hallucinations and unsafe commands by
design.
Delanoe Pirard Follow 23 min read · 3 days ago
366 7


---
*Page 2*


Claude generated three perfectly confident, completely fictional FastAPI
parameters. I lost 40 minutes. This article is about what I built to make
sure it never happens again.
TL;DR
Claude Code is not a chatbot with a terminal. It’s a
programmable platform. This blueprint turns it
into a 6-layer operating system with skills, hooks,
agents, and MCP servers working under zero-trust
security. Here’s what the system contains:
1. 78 permission rules (40 allow + 38 deny): a zero-
trust model where every command, every write,


---
*Page 3*


every MCP access is explicitly permitted or
blocked. Anthropic Documentation
2. 17 hooks covering 17 lifecycle events: bash
scripts (or HTTP endpoints, or LLM prompts)
that intercept every action before and after
execution. Secret detection, destructive
command blocking, auto-formatting, automatic
failure logging. Pure determinism.
3. 32 skills organized into 10 categories: from anti-
hallucination to generative AI, each skill follows
a common 5-phase architectural pattern
(ASSESS, ANALYZE, PLAN, EXECUTE,
VALIDATE). Including 6 dedicated AI/ML skills
(NLP, vision, MLOps, RL, generative, agents).
4. 10 specialized agents across 5 domains: not
generic assistants, but autonomous departments
with dedicated tools, models, and colors. Code
agents were replaced by more modular plugins.
5. 6 MCP servers as an integration layer: real-time
documentation, git operations, web reading,


---
*Page 4*


Jupyter notebooks. The nervous system
connecting Claude to the outside world.
6. Persistent memory: the memory/ directory allows
Claude to retain learnings between sessions.
Confirmed patterns, architectural decisions,
workflow preferences.
7. Everything is open-source: the claude-code-
blueprint contains the CLAUDE.md, skills,
agents, hooks, rules, commands and settings
described in this article. Clone, adapt, iterate.
8. The central question: Claude Code is not a
chatbot with a terminal. It’s a programmable
platform. Most users exploit only the terminal.
Open-source repository of a claude
code configuration example: HERE.


---
*Page 5*


Three months ago, Claude lied to my face without
a trace of hesitation.
I was working on a FastAPI application. I needed to
inject a conditional dependency into an endpoint. I
asked Claude Code for the exact signature of
Depends(). The answer arrived in under two
seconds, delivered with the confidence of a
surgeon explaining a procedure:
Depends(dependency, use_cache=True,
allow_override=False). Three parameters. Detailed
descriptions. Usage examples. Everything was
clear, structured, convincing.
I refactored my code around those three
parameters. I spent forty minutes integrating
allow_override into my dependency logic. Then I
ran the tests.
Everything broke.


---
*Page 6*


Depends() takes one argument. The dependency
itself. Full stop. The other two parameters don't
exist. They never existed. Claude had fabricated
them from nothing, with the same conviction it
would use to cite the Pythagorean theorem.
This is the fundamental problem with LLMs: they
don’t know what they don’t know. A student
cheating at an oral exam will show some
discomfort when questioned. An LLM that
hallucinates looks you in the eye with absolute
certainty. No warning signal. No drop in tone. No
“I think”. Just a wrong answer, delivered with the
confidence of a verified fact.
Forty minutes of work. Lost to an invented
function signature.
That day, I decided it wouldn’t happen again. Not
by relying on my memory, nor on the model’s. By
building a system that makes hallucination
structurally difficult.


---
*Page 7*


That system is what I’ll describe here. Not a
tutorial. Not a list of tips. The complete
architecture of a Claude Code environment where
every layer has a function, where errors are
intercepted before they reach the code, and where
the model is never the last line of defense.
Claude Code Architecture: The 6-Layer
System
Before getting into the details, here’s the full
picture. The system breaks down into 6 layers,
each with a distinct responsibility:
+---------------------------------------------------+
| LAYER 6: MCP |
| 6 servers (context7, fetch, git, |
| huggingface, jupyter, ide) |
+---------------------------------------------------+
| LAYER 5: SECURITY |
| 40 allow + 38 deny + 17 lifecycle hooks |
| + regex secrets + fail-closed trap |
+---------------------------------------------------+
| LAYER 4: AGENTS |
| 10 specialized agents (5 domains) |


---
*Page 8*


| multi-agent brainstorm (4 in parallel) |
+---------------------------------------------------+
| LAYER 3: SKILLS |
| 32 skills (10 categories) auto-loaded |
| Common pattern: 5 AAPEV phases |
+---------------------------------------------------+
| LAYER 2: MEMORY |
| persistent memory/ + project-level rules/ |
| Cross-session learnings |
+---------------------------------------------------+
| LAYER 1: CLAUDE.md (KERNEL) |
| Anti-hallucination + Confidence levels + |
| Toolchain + Code standards + /compact rules |
+---------------------------------------------------+
The 6-layer architecture starts with CLAUDE.md as
the kernel (layer 1), adds persistent memory (layer
2), context-aware skills (layer 3), specialized agents
(layer 4), zero-trust security with hooks (layer 5),
and MCP server integrations (layer 6). Each layer
builds on the previous one. Removing any layer
degrades the system but doesn’t break it.
The analogy to an operating system is not
decorative. The CLAUDE.md is the kernel: it defines
fundamental behaviors. Persistent memory is the
filesystem: it retains learnings between sessions.


---
*Page 9*


Skills are shared libraries: loaded on demand
when context requires them. Agents are processes:
autonomous entities with dedicated resources.
Security is the permission layer: who can do what,
where, and under which conditions. And MCP
servers are the peripheral drivers: the interface
with the outside world.
This is not a forced analogy. It’s how the system
actually works.
The six-layer architecture: CLAUDE.md as kernel, persistent memory,
lazy-loaded skills, specialized agents, zero-trust security, and MCP


---
*Page 10*


integrations. Each layer has a single responsibility.
CLAUDE.md as the Kernel
Most guides tell you to put your “preferences” in
CLAUDE.md. Your code style. Your favorite
framework. Maybe a reminder to use TypeScript.
That’s not enough.
CLAUDE.md is not a preferences file. It's the system
kernel. It defines the default behavior of every
session, every tool, every response. Everything not
in CLAUDE.md is optional. Everything in it is
mandatory.


---
*Page 11*


CLAUDE.md is the kernel: it boots before any conversation, enforces the
anti-hallucination protocol, defines confidence levels, and sets the tone
for every interaction. Change the kernel, change the system.
Here’s what mine contains:
The Anti-Hallucination Protocol
This is the first rule. Written the day of the FastAPI
incident. A decision tree that Claude must follow
before responding to any technical question:


---
*Page 12*


BEFORE answering:
+-- API/Library question --> Context7 FIRST
+-- Recent facts/news --> WebSearch FIRST
+-- File content --> Read FIRST
+-- Uncertain --> "I need to verify" + use
NEVER:
+-- Invent function signatures
+-- Guess library versions
+-- Assume API behavior without verification
+-- Fabricate citations or sources
Each branch is a direct order. Not a suggestion.
Not a “preferably.” If Claude needs to answer a
question about an API, it must first query Context7
(an MCP server that provides real-time
documentation). If it can’t verify, it must say so.
Mandatory Confidence Levels
Every technical claim must be accompanied by a
confidence level:


---
*Page 13*


Table 1: Confidence Levels (Source: personal CLAUDE.md)
This is not a gadget. It’s an operational constraint.
When Claude answers “the function takes 3
parameters” with a MEDIUM confidence level, I
know I need to verify. When it answers with HIGH
and a Context7 link, I can trust it. The difference
between the two is forty minutes of lost
refactoring.
Preservation During /compact
Claude Code has a context limit. When a
conversation grows too long, the /compact
command compresses the context. The problem:
without explicit instructions, compaction loses
critical information. My CLAUDE.md specifies what
must survive:


---
*Page 14*


When context is compacted, ALWAYS preserve:
- List of modified files with paths
- Current git branch and uncommitted changes
- Pending tasks and TODO items
- Test results and failures
- Key architectural decisions made during session
Without this rule, every compaction is a partial
lobotomy. With it, it’s a structured summary.
Persistent Memory
Claude Code has a fundamental problem: every
session starts from scratch. You spend an hour
explaining your architecture, your preferences,
your conventions. The next day, it’s all forgotten.
The context window is volatile.


---
*Page 16*


Between every session, context dies. The memory layer writes structured
Markdown files that survive restarts. The session ends; the knowledge
doesn’t.
The solution: the memory/ directory. Claude Code
can write and read files in
~/.claude/projects/<project>/memory/. These files
persist between sessions. The MEMORY.md is
automatically loaded into every conversation. It's
the permanent working memory. Memory
documentation
memory/
├── MEMORY.md <-- Auto-loaded (max 200 line
├── patterns.md <-- Confirmed patterns on the
├── debugging.md <-- Solutions to recurring pr
└── architecture.md <-- Structural decisions
The MEMORY.md is the index. It must stay concise
(lines after 200 are truncated). Satellite files
contain the details. Claude updates these files over
sessions. Not ephemeral notes, but confirmed
learnings validated across multiple interactions.


---
*Page 17*


What I store there:
Architectural patterns validated on the project
(not hypotheses)
Confirmed workflow preferences (“always use
uv”, “never auto-commit”)
Critical paths and project structure
Solutions to recurring problems
What I do not store: current session context,
unverified information, speculative conclusions.
Memory is a ledger of facts, not a scratch pad.
The difference with /compact: compact preserves
context within a session. Memory preserves
learnings between sessions. One is RAM, the other
is persistent storage.
Path-Based Rules
CLAUDE.md is global. It applies to everything. But a
project with Python and TypeScript doesn't have
the same conventions for both. Putting "use ruff"


---
*Page 18*


and "use prettier" in the same file forces Claude
to sort out what applies to what. That's
probabilistic work where determinism is possible.
The ~/.claude/rules/ directory solves this. Each
file has a paths: frontmatter that defines when it
loads:
~/.claude/rules/
├── python.md <-- *.py, pyproject.toml (40 l
└── typescript.md <-- *.ts, *.tsx, package.json
The python.md contains uv, ruff, pytest, type hints
and async patterns. The typescript.md contains
prettier, vitest, strict mode, satisfies over as, no
enums. The paths: frontmatter works like a glob:
when the file being edited matches the pattern, the
rule loads.
Honesty note: at the time of writing, path-scoping
has a known bug. All rules/ files load at session
start regardless of paths:. In practice, my 78 lines


---
*Page 19*


of conventions load systematically. It's not
catastrophic: 78 lines is roughly 100 tokens on a
200K context window. And when the bug is fixed,
scoping will work automatically without changing
anything in my files.
The advantage over centralizing everything in
CLAUDE.md: my kernel stays at 109 lines. Language-
specific conventions live alongside it and don't
pollute the main file's readability.
32 Claude Code Skills and How They Load
Skills are the mechanism most people skip in
Claude Code. A skill is a Markdown file in
~/.claude/skills/ with YAML frontmatter and
structured content. Claude loads them
automatically when the conversation matches the
skill's description. No API. No SDK. No build step.
Plain text that the model follows like instructions.
Official documentation


---
*Page 20*


Thirty-two skills, none loaded at startup. Each YAML file sits dormant
until Claude detects its trigger keyword. The lazy-loading pattern keeps
context lean and response time fast.
Anatomy of a Skill
What is a Claude Code skill? A Claude Code skill is
a Markdown file in ~/.claude/skills/ with YAML
frontmatter that Claude loads automatically when
the conversation context matches the skill's
description. No API, no SDK, no build step. Plain
text that the model follows like instructions.


---
*Page 21*


Every skill follows the same structure. Here’s the
frontmatter of the anti-hallucination skill:
---
name: anti-hallucination
description: |-
Verify API signatures, library methods, and factual
before answering using Context7 and WebSearch.
MUST BE USED when user asks about: function paramet
method signatures, library versions, API behavior.
allowed-tools:
- mcp__context7__resolve-library-id
- mcp__context7__get-library-docs
- WebSearch
- Read
- Grep
---
The description is the key. That's what Claude uses
to decide whether to load the skill. The allowed-
tools field is a whitelist: the skill can only use the
listed tools. The content after the frontmatter
defines the behavior, including a complete
decision tree:


---
*Page 22*


Question type?
+-- API/Library signature --> Context7 FIRST, THEN a
+-- Recent event/fact --> WebSearch FIRST
+-- File content --> Read tool FIRST
+-- Code behavior --> Read + trace FIRST
+-- Historical fact --> Can use training data
+-- Cannot verify --> State "I don't know"
The Common Architectural Pattern
All 32 skills follow a 5-phase pattern:
Phase 1: ASSESS / CLARIFY --> Understand the probl
Phase 2: ANALYZE / RESEARCH --> Research before acti
Phase 3: PLAN / DESIGN --> Propose a plan
Phase 4: EXECUTE / IMPLEMENT --> Apply the changes
Phase 5: VALIDATE / VERIFY --> Test the result
This pattern imposes a cognitive discipline on the
model. Instead of jumping straight to
implementation (Phase 4), Claude must first
understand (Phase 1), then research (Phase 2),
then plan (Phase 3). Phase 5 closes the loop with
verification. The same reasoning you’d expect from a
senior engineer.


---
*Page 23*


Taxonomy of the 32 Skills
Table 2: Skills by Category (Source: )
~/.claude/skills/
The AI/ML category is the densest in the system.
The 6 most recently added skills cover the entire
machine learning pipeline: nlp-transformers for
fine-tuning and embeddings, computer-vision for
YOLO and SAM, mlops-training for distributed
training and quantization, agentic-ai for agents
and tool use, generative-models for Stable Diffusion
and LoRA, reinforcement-learning for PPO and
Gymnasium environments. Each follows the same
AAPEV pattern and defines its own tool whitelist.


---
*Page 24*


Loading is lazy: only skills whose description
matches the conversation context are injected.
Asking for help on a FastAPI endpoint does not
load the visual-prompts skill. Requesting a
brainstorm loads the brainstorm skill and
potentially research-protocol. The system is
selective by design.
The Agents Layer: Departments, Not
Assistants
A Claude Code agent is a Markdown file in
~/.claude/agents/ that defines a specialized sub-
agent. The difference from a skill: an agent has its
own model, its own tools, and can be spawned as
an independent process. A skill teaches a method.
An agent is a specialist. Official documentation
One important note: the system has evolved. My
first iteration had 18 agents. Today there are 15 (10


---
*Page 25*


primary ones described here). Not through
reduction, but through maturation.
Ten specialized agents, not ten instances of the same chatbot. Each has a
fixed model, a tool whitelist, and a routing trigger. Departments, not
assistants.
Anatomy of an Agent: the
research-synthesizer
Case
---
name: research-synthesizer
model: opus
description: |-
Multi-source academic research: literature reviews,
cross-domain synthesis, DOI/arXiv/PMID citations.
MUST BE USED when user asks for: "literature review
"research synthesis", "SOTA", "state of the art",


---
*Page 26*


"find papers", "compare studies".
tools: [Read, Grep, Glob, WebSearch, WebFetch,
mcp__fetch__fetch, mcp__arxiv-mcp-server__sea
mcp__arxiv-mcp-server__read_paper,
mcp__huggingface__get-paper-info,
mcp__huggingface__get-daily-papers]
color: "#8B5CF6"
---
Each agent defines:
model: sonnet for routine tasks, opus for
complex analysis
tools: a whitelist of accessible tools (not every
tool in the system)
description: the automatic routing trigger
color: visual identification in the terminal
From 18 to 10 Agents: the Plugin Lesson
The first version of the system had 18 agents.
Three were removed: python-expert, typescript-
expert, and frontend-developer. Not because they
didn't work. Because plugins do it better.


---
*Page 27*


Claude Code plugins (feature-dev, pr-review-
toolkit, frontend-design) package entire systems
(agents, skills, workflows) into distributable
modules. My python-expert was a 200-line
Markdown file. The python-development:python-pro
plugin is a complete system with code review, test
runner, and integrated patterns. Maintaining both
is redundant. The custom agent gave way.
In parallel, the most verbose agents (seo-expert,
fitness-coach, claude-expert, prompt-engineer, ui-
ux-designer) were trimmed by -70% on average.
Less text, same capabilities. The lesson: an agent
doesn’t need a novel to be effective. It needs a precise
description and the right tools.


---
*Page 28*


Table 3: The 10 Primary Agents by Domain (Source: )
~/.claude/agents/
The Multi-Agent Brainstorm
The brainstorm skill is probably the most
interesting piece in the system. It orchestrates
multiple agents in parallel to attack a problem
from different angles:
Phase 1: CLARIFY --> Understand the topic (2-3 que
Phase 2: MAP --> Select the expert agents
Phase 3: EXPLORE --> Spawn the agents in parallel
Phase 4: SYNTHESIZE --> Combine: consensus, divergenc
recommendation
Each agent receiving the brainstorm prompt must:
1. Propose 2–3 approaches from its domain of
expertise
2. Give the trade-offs and risks of each approach
3. Justify each recommendation with sources
4. Declare a confidence level
5. Flag what it cannot verify


---
*Page 29*


The synthesis identifies points of consensus
(strong signal), divergences (decision points), and
produces an argued recommendation. This is not a
vote. It’s a structured deliberation.
The multi-agent brainstorm: one orchestrator spawns specialized
subagents in parallel, each attacks the problem from a different angle,
the results are synthesized into a single structured output.
Zero-Trust Permissions and Hooks
This is where the system gets serious.


---
*Page 30*


Claude Code can execute shell commands. It can
write files. It can modify production code. Default
trust is a strategy that works until the day it
doesn’t. My system starts from the opposite
principle: everything is forbidden unless
explicitly authorized.
Level 1: Static Permissions
The settings.json file defines 78 permission rules.
40 authorizations. 38 denials. Permissions
documentation Here's an extract:
Allowed:
"Bash(git:*)", "Bash(uv:*)", "Bash(npm run:*)",
"Bash(python:*)", "Bash(cargo:*)", "Bash(docker:*)",
"Bash(ruff:*)", "Bash(gh:*)",
"mcp__context7__*", "mcp__fetch__*", "mcp__git__*"
Denied:
"Bash(chmod 777:*)", "Bash(sudo:*)", "Bash(:|:*)",
"Bash(dd if:*)", "Bash(eval :*)", "Bash(nc :*)",


---
*Page 31*


"Write(~/.ssh/*)", "Write(*.pem)", "Write(*secret*)",
"Edit(.env.production)", "Edit(*credentials*)"
The logic is straightforward: Claude can run git,
python, cargo, docker. It cannot run sudo, chmod
777, eval, nor write to ~/.ssh/ or any file
containing "secret" in its name. Each permission is
an explicit decision.
Seventy-eight explicit permissions. Hooks that fail closed. A bash-guard
that pattern-matches dangerous commands before they execute. Zero
trust means the system earns the right to act.


---
*Page 32*


Level 2: PreToolUse Hooks
Static permissions are not enough. A permitted
Bash(rm:*) would be dangerous if the full
command is rm -rf /. PreToolUse hooks inspect
the content of every command before execution.
The bash-guard intercepts destructive patterns:
#!/usr/bin/env bash
set -euo pipefail
# Fail-closed: on error, block by default
trap 'echo "{\"hookSpecificOutput\":{...\"deny\"...}}
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command
# Sudo/Su: blocked, not just warned
if echo "$command" | grep -qE \
'(^|;|&&)\s*(sudo|su |doas |pkexec)'; then
# --> DENY: privilege escalation blocked
exit 0
fi
# Destructive patterns
# Detects: rm -rf /, fork bombs, chmod -R 777,
# curl pipe bash, mkfs, dd to device
if echo "$command" | grep -qE "$dangerous_patterns";
# --> DENY: dangerous command detected
exit 0
fi
# Obfuscation: eval $var, base64 decode pipe shell
if echo "$command" | grep -qE "$obfuscation_patterns"


---
*Page 33*


# --> DENY: indirect execution detected
exit 0
fi
Three protections in one script: privilege escalation
The write-guard protects sensitive files and scans co
# === Sensitive file protection ===
# Blocks writes to: .env, credentials, id_rsa,
# .pem, .key, .ssh/, .npmrc, .pypirc, .aws/, kubeconf
protected='\.env($|\.)|credentials|id_rsa|\.pem$|\.ke
if echo "$file_path" | grep -qiE "$protected"; then
# --> DENY: protected file
fi
# === Secret detection in written content ===
# Regex covering 15+ key and token formats:
# - OpenAI keys (sk-...)
# - AWS keys (AKIA...)
# - GitHub tokens (ghp_..., gho_..., github_pat_...
# - GitLab, Slack, Google, Stripe, SendGrid tokens
# - SSH/TLS private keys (BEGIN ... KEY)
# - DB connection URLs (with inline password)
# - JWT (eyJ...eyJ...sig format)
#
if echo "$content" | grep -qE "$secret_patterns"; the
# --> DENY: potential secret detected
fi
This regex covers the most common accidental
leaks: API keys from major cloud and SaaS
providers, certificates, authentication tokens, and
database connections containing plaintext


---
*Page 34*


passwords. Not an exhaustive list, but sufficient for
the most frequent cases.
Level 3: The Fail-Closed Pattern
The single most important line across all hooks is
probably this one:
trap 'echo "{\"hookSpecificOutput\":{
\"permissionDecision\":\"deny\",
\"permissionDecisionReason\":\"Hook error - fail-cl
If the hook itself crashes, if jq fails to parse the
input, if a variable is empty, if anything goes
wrong: the default response is deny. Not allow. Not
"we'll see." Deny. This is the fail-closed principle:
when in doubt, block.
Beyond Bash: HTTP and Prompt Hooks
All my hooks are bash scripts. But that’s no longer
the only option. Claude Code now supports three
hook types:
"type": "command": a shell script (what I use)


---
*Page 35*


"type": "http": POST JSON to a URL, receive
JSON in return
"type": "prompt": an LLM sub-agent that
interprets the event
HTTP hooks open interesting possibilities: send
every tool failure to a Slack webhook, push
security metrics to a dashboard, or delegate
allow/deny decisions to a centralized service.
Prompt hooks allow more nuanced decisions than
a regex, at the cost of tokens and latency. I stay on
bash for determinism and speed, but the
architecture supports all three. Hooks
documentation
The Pre-Send Scan
One last hook intercepts user prompts before
they’re sent to the API:
# Detects mentions of secrets in the user prompt
# (but not questions about secrets)
if echo "$prompt" | grep -qiE \
'(password|api.?key|token|credential)'; then


---
*Page 36*


if ! echo "$prompt" | grep -qiE \
'(how|help|explain|what is)'; then
echo '{"systemMessage":"Warning: your prompt
mentions sensitive information."}'
fi
fi
If you type a password directly into the prompt
(without asking a question about passwords), the
hook warns you before the text leaves for
Anthropic’s servers.
The Protection Matrix
Table 4: Multi-Layer Security Matrix (Source: +
settings.json
)
hooks/scripts/
Each threat is covered by at least two layers. This
is the principle of defense in depth: if one layer
fails, the next intercepts.


---
*Page 37*


The Safety Net: PostToolUseFailure
PostToolUseFailure intercepts tool failures: a Read
that fails, a Bash that times out, an MCP that
doesn't respond. Instead of letting these errors
disappear, the hook logs them:
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // "unk
ERROR=$(echo "$INPUT" | jq -r '.error // .stderr // "
| head -c 500)
LOG_FILE="$HOME/.claude/logs/tool-failures.log"
# Automatic rotation at 1MB
if [ -f "$LOG_FILE" ] && \
[ "$(stat -f%z "$LOG_FILE")" -gt 1048576 ]; then
mv "$LOG_FILE" "$LOG_FILE.old"
fi
echo "[$(date '+%Y-%m-%d %H:%M:%S')] FAIL tool=$TOOL_
error=$(echo "$ERROR" | tr '\n' ' ' | head -c 200)"
>> "$LOG_FILE"
This is not strictly security. It’s observability. When
a hook blocks an action, I know immediately. But
when a tool fails silently (MCP timeout, file not
found, unexpected format), without logging, these
errors are invisible. PostToolUseFailure closes this


---
*Page 38*


gap. Automatic rotation at 1MB keeps the disk
clean.
PostToolUseFailure fires on every tool error. The process exits non-zero,
the action is blocked, and the failure is logged with automatic 1MB
rotation. The safety net doesn’t warn. It catches.
MCP Servers: The 6 Integration Points
MCP (Model Context Protocol) is the open protocol
that allows Claude Code to connect to external
services. Each MCP server exposes tools that
Claude can call directly, as if they were part of its
native repertoire.


---
*Page 39*


Table 5: MCP Servers (Source: )
~/.claude/settings.json
The context7 server is the cornerstone of the anti-
hallucination protocol. When Claude needs to
answer a question about FastAPI, it calls
mcp__context7__resolve-library-id to find the
library, then mcp__context7__get-library-docs to get
the current documentation. Not its training
memory. The real, up-to-date documentation,
with the correct signatures.


---
*Page 40*


Six MCP servers: Context7 for verified documentation, Fetch for live web
content, Git for repository operations, HuggingFace for model access,
Jupyter for computation, and IDE for real-time editor feedback. The
nervous system connecting Claude to the outside world.
If context7 had been in the system the day of the
Depends() incident, the hallucination wouldn't have
survived Phase 2 of the protocol.
Loading is lazy. Servers are only initialized when
an MCP tool is actually called. A
MAX_MCP_OUTPUT_TOKENS of 25,000 prevents large
responses from saturating the context window.


---
*Page 41*


Why Hooks Beat LLMs for Formatting and
Security
There’s a simple rule I apply to every decision in
this system: never ask an LLM to do what a linter
does better.
Code formatting is the perfect example. Claude
can format Python. It does it rather well, actually.
But “rather well” is not deterministic. An LLM will
format dict[str, Any] differently depending on
context, the probabilistic mood of token sampling,
the phase of the moon.
A linter formats dict[str, Any] the same way.
Always. Without exception.


---
*Page 42*


A hook is a deterministic function: same input, same output, every time.
An LLM is a probability distribution: same input, different output, every
time. For formatting and security, you want the function.
The PostToolUse hook for Write/Edit applies this
principle:
if [ -n "$file_path" ] && [ -f "$file_path" ]; then
case "$file_path" in
*.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs)
npx prettier --write "$file_path" 2>/dev/
;;
*.py)
ruff format --quiet "$file_path" 2>/dev/n
;;
*.json)


---
*Page 43*


npx prettier --write "$file_path" 2>/dev/
;;
esac
fi
Every file written by Claude is automatically
reformatted by the corresponding deterministic
tool: prettier for TypeScript/JavaScript/JSON, ruff
for Python. Claude never even sees the final
formatting. It writes, the hook reformats, the
result is guaranteed compliant.
The same principle applies to vulnerability
detection. After every npm install, the
posttooluse-bash-vuln.sh hook scans the output for
CVE mentions:
if echo "$command" | grep -qE \
'^(npm|pnpm|yarn) (install|add|remove)'; then
if echo "$stdout" | grep -qiE '(vulnerabilit|CVE-
echo '{"systemMessage":"Vulnerabilities detec
Run npm audit for details."}'
fi
fi


---
*Page 44*


Deterministic. Reproducible. Zero tokens
consumed.
The Complete Claude Code Lifecycle: 17
Events Mapped
To see how everything fits together, here’s what
happens when I type a command in Claude Code:
User types: "Refactor this FastAPI endpoint"
|
v
[SessionStart] --> session-start.sh
Detects: Python project, main branch, 3 modified fi
|
v
[UserPromptSubmit] --> user-prompt-secrets.sh
Scan: no secret in prompt --> OK
|
v
Claude loads skill "code-patterns" + "anti-hallucinat
Claude queries Context7 for FastAPI docs (Phase 2: AN
Claude proposes a refactoring plan (Phase 3: PLAN)
|
v
[PreToolUse: Write] --> write-guard.sh
File: src/api/endpoints.py --> not protected --> OK
Content: no secret detected --> OK


---
*Page 45*


|
v
Claude writes the file
|
v
[PostToolUse: Write] --> write-format.sh
Extension .py --> ruff format --> auto-formatted
|
v
[PreToolUse: Bash] --> bash-guard.sh
Command: pytest tests/ --> not dangerous --> OK
|
v
Claude runs the tests (Phase 5: VALIDATE)
|
v
[Stop] --> stop.sh
Git summary: main branch, 1 modified file, 0 staged
Claude Code supports 17 lifecycle hook events.
Here is the complete list, with the hooks active in
my setup:


---
*Page 46*


Table 6: The 17 Lifecycle Events and Their Hooks (Source:
+ official docs)
~/.claude/settings.json
Why Claude Code Is a Platform, Not a
Chatbot
Claude Code is not a tool. It’s a platform.


---
*Page 47*


The difference is structural. A tool, you use. A
platform, you program. The settings.json is a
system configuration file. Hooks are event
listeners. Skills are on-demand modules. Agents
are processes with isolated resources. MCP servers
are peripheral drivers.
Most articles about Claude Code show isolated
gears: “here’s how to write a hook”, “here’s a useful
skill”, “here are 5 MCP servers to install.” Those are
components. They don’t show how those
components form a system where each layer
reinforces the others.
The anti-hallucination protocol works because
Context7 is an accessible MCP server. Security
hooks work because static permissions define a
perimeter. Multi-agent brainstorming works
because agents have dedicated tools and models.
Remove one layer and the others lose
effectiveness.


---
*Page 48*


My position: the value of Claude Code does not
reside in the model. It resides in the
infrastructure around the model. The model is the
engine. The CLAUDE.md, skills, agents, hooks,
permissions and MCP servers are the chassis, the
transmission, the brakes, and the dashboard.
One final point. This system is not a showcase. It’s
my daily work environment. Every skill, every
hook, every permission was written to solve a real
problem I encountered. The anti-hallucination
protocol was born from an invented function
signature. The write-guard was born from an API
key accidentally written to a file. The bash-guard
was born from a misdirected rm -rf. This is not
preventive engineering. It's reactive engineering,
crystallized into deterministic code.
The Limits of This Analysis


---
*Page 49*


1. Survivorship bias. I’m showing a system that
works for me. My workflow (technical articles,
Python/TypeScript APIs, ML research) is not
representative of every use case. A mobile
developer or a data engineer would have a
different setup.
2. Token cost. 32 skills, even with lazy loading,
consume context. I haven’t precisely measured
the token overhead compared to a minimal
setup. The intuition: it’s significant.
3. Bash hook fragility. Hooks depend on jq, grep,
and a stable JSON format from Claude Code. An
update to the input format could break the
system. I don't have automated tests for the
hooks themselves.
4. Regex is not security. Secret scanning by regex
is a heuristic, not a guarantee. A base64-encoded
or multi-line secret would pass through. This is
not a substitute for a secrets manager.


---
*Page 50*


5. Maintenance. 32 skills, 10 agents, 17 hooks. This
is a system to maintain. APIs evolve, models
change, patterns age. The upfront investment is
significant. The good news: plugins let you
delegate maintenance of the most generic agents
(code review, testing, frontend) to community
packages.
What This Changes for You
I published a companion repo with a curated,
ready-to-use selection: claude-code-blueprint. It
contains the CLAUDE.md, 8 skills, 4 agents, 11
hooks (2 sanitized), rules, commands, and a
permissions template. Not a mirror of my setup. A
starting point, adapted for use.
If you’re new to Claude Code: start with the
blueprint’s CLAUDE.md. Add the anti-hallucination
protocol and confidence levels. That's the change


---
*Page 51*


with the best effort-to-impact ratio. Budget 30
minutes.
If you already have an intermediate setup: add the
security hooks. The write-guard and bash-guard
from the blueprint contain the structure and threat
categories. Add your own regex. An afternoon to
adapt and test. Add 3-5 skills for your main use
cases.
If you’re ready for the full system: design your
agents by domain, configure your MCP servers,
write your zero-trust permissions. The blueprint
provides the skeleton; budget a week to adapt and
iterate. The system pays upfront, not downstream.
Claude Code Setup FAQ
Why Markdown files instead of an SDK or API?
It’s an architectural choice by Anthropic. Skills and
agents are plain text that the model interprets as


---
*Page 52*


instructions. The advantage: zero build step, zero
dependency, total portability. The disadvantage:
the “runtime” is the model itself, with its share of
non-deterministic interpretation.
Do Claude Code hooks slow down execution?
Each hook has a timeout (2 to 15 seconds
depending on type). In practice, my hooks execute
in under 100ms. The write-format.sh is the slowest
(calling prettier/ruff), but with a 15-second
timeout, it's transparent. Anthropic documentation
Does this work with models other than Claude?
No. Skills, agents, hooks and CLAUDE.md are specific
to Claude Code. The architectural concept (layers,
zero-trust, determinism) is transposable, but the
implementation is tied to the Anthropic
ecosystem.
Don’t 32 skills saturate the context window?
Loading is lazy. Claude only loads a skill if its
description matches the conversation context. In
practice, 2 to 4 skills are loaded simultaneously,


---
*Page 53*


rarely more. The MAX_MCP_OUTPUT_TOKENS of 25,000
and maximum output of 64,000 tokens provide a
comfortable margin.
How do you debug a hook that isn’t working?
Hooks write to stderr for debugging (invisible to
Claude but visible in logs). The set -euo pipefail +
trap ERR pattern guarantees that a broken hook
blocks rather than failing silently. I add echo
"DEBUG: ..." >&2 during development. And since
adding the PostToolUseFailure hook, every tool
failure is automatically logged to
~/.claude/logs/tool-failures.log.
Won’t persistent memory become stale?
It’s a real risk. The MEMORY.md is not an automatic
dump. It's a curated ledger. I only store patterns
confirmed across multiple sessions, never
hypotheses. And when information becomes
outdated, Claude updates or removes it. The rule:
never write to memory what hasn't been verified
against the project.


---
*Page 54*


Conclusion: From the Confident Liar to the
System That Verifies
Back to
Depends()
Three months ago, Claude invented three
parameters for Depends() without blinking. Forty
minutes lost, a pointless refactor, and the
realization that trusting an LLM is a strategy with
an expiration date.
Today, the same question would pass through a
verification chain: the anti-hallucination protocol
would trigger Context7, which would query the
Starlette/FastAPI documentation in real time,
which would return the real signature
(Depends(dependency), one argument) with a HIGH
confidence level and a link to the source. The lie
would be intercepted before reaching my code.
There’s a contradiction worth stating. The system
that prevents Claude from lying was built with Claude.


---
*Page 55*


The hooks that block dangerous commands were
written in a terminal where Claude could execute
dangerous commands. The trust needed to build
the zero-trust system is the same trust the system
is designed to eliminate.
The system doesn’t make Claude smarter. It makes Claude accountable.
Every claim has a confidence level. Every tool call has a guard. Every
session has a memory. That’s the difference between a confident liar and
a reliable system.
My Position
Claude Code is a programmable development
platform that almost nobody uses as one in 2026.
Not because of the model. Because of the


---
*Page 56*


infrastructure. Hooks, skills, agents, permissions
and MCP form a minimalist operating system
where the LLM is the processor and everything
else is deterministic code.
Users who treat Claude Code as a chatbot with a
terminal are using a fraction of what it can do.
Those who treat it as a programmable platform
ship faster and break less.
What’s Next
Most articles about Claude Code show gears. This one
shows the clockwork.
But the clockwork isn’t finished. HTTP and prompt
hooks (documented above) allow replacing bash
scripts with endpoints or specialized sub-agents.
Plugins package entire systems for distribution.
The MCP protocol gains new servers every week.
And then there are Agent Teams, the most
significant experimental feature right now. Instead
of a single Claude Code instance orchestrating


---
*Page 57*


silent sub-agents, multiple instances collaborate in
parallel with direct communication between
teammates. A lead assigns tasks, teammates work
in their own contexts, and they coordinate without
going through an intermediary. It’s the natural
evolution of my system: moving from a single-core
OS to a multi-core OS. The feature is still behind
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1, but the
direction is clear.
The question is no longer “can Claude Code replace
my IDE”. It’s: how far can you push the
programmability of an agent before it becomes an
operating system itself?
I don’t have the answer. But I know the question is
worth forty minutes of refactoring.
✦ DELANOE PIRARD ✦
Artificial Intelligence Researcher & Engineer


---
*Page 58*


🌐
delanoe-pirard.com
💻
github.com/Aedelon
💼
linkedin.com/in/delanoe-pirard
𝕏
x.com/0xAedelon
👉
This article did help you ? Clap + Follow for the
next one.
Sources
Tier 1: Official Documentation
Anthropic (2026). “Hooks reference.” Claude
Code Docs. Link
Anthropic (2026). “Automate workflows with
hooks.” Claude Code Docs. Link
Anthropic (2026). “Extend Claude with skills.”
Claude Code Docs. Link
Anthropic (2026). “Create custom subagents.”
Claude Code Docs. Link


---
*Page 59*


Anthropic (2026). “Orchestrate teams of Claude
Code sessions.” Claude Code Docs. Link
Anthropic (2026). “Configure MCP servers.”
Claude Code Docs. Link
Anthropic (2026). “Memory and CLAUDE.md.”
Claude Code Docs. Link
Anthropic (2026). “Permissions.” Claude Code
Docs. Link
Anthropic (2026). “Extend Claude Code —
Features overview.” Claude Code Docs. Link
Tier 2: Technical Articles
Julian B (2026). “The OS Hiding In Claude Code.”
Medium. Link
David Haberlah (2026). “Configure Claude Code
to Power Your Agent Team.” Medium. Link
alexop.dev (2026). “Understanding Claude Code’s
Full Stack: MCP, Skills, Subagents, and Hooks.”
Link
Tier 3: Community Resources


---
*Page 60*


ChrisWiles (2026). “claude-code-showcase.”
GitHub. Link
hesreallyhim (2026). “awesome-claude-code.”
GitHub. Link
Okhlopkov (2026). “My Claude Code Setup: MCP,
Hooks, Skills.” Link
Artificial Intelligence Software Engineering LLM
Software Development Machine Learning
Published in AI Advances
Following
63K followers · Last published 1 hour ago
Democratizing access to artificial intelligence
Written by Delanoe Pirard
Follow
6.2K followers · 61 following
AI Researcher, AI Engineer. Building autonomous
systems. Reinforcement Learning, Computer Vision.
🇧🇪
Brussels https://www.delanoe-pirard.com/


---
*Page 61*


Responses (7)
To respond to this story,
get the free Medium app.
Steve Henty
3 days ago
Simply by showing examples of the [skill | hook | agent, etc] text itself
puts this article in its own, superior class. The fact that they form a
coherent systematic whole makes it other-worldly.
You have demonstrated a practical advancement of the… more
26 2 replies
Shafaq Naeem
2 days ago
Claude Code is so much in discussions right now.
I am also trying to learn it.
11
nderground
2 days ago


---
*Page 62*


Depends() takes one argument. The dependency
itself. Full stop. The other two parameters don't exist.
They never existed.
I am a big fan of your writing and your carefully thought out posts. But
perhaps this is why you should use Java and not Python. With Java you
would have known immediately that the call did not exist.
I use Gemini, not Claude. The only reason is that… more
10 1 reply
See all responses
More from Delanoe Pirard and AI Advances
In by In by
AI Advances Delanoe Pirard AI Advanc… Jose Crespo, P…
A 1967 Math Paper Just Everyone’s Wrong
S l d AI’ $100 Milli Ab t AI P i


---
*Page 63*


December 31st, 2025. While The lens that makes AI coding
Sili V ll d b i ibl d
Jan 28 Jan 28
In by In by
AI Adv… Han HELOIR YAN,… AI Advances Delanoe Pirard
The 89% Ceiling: Why AI Is Eating Itself to
V t RAG i F ili D th d N b d I
How PageIndex uses 526 citations. Zero solutions
hi hi l t t t d l d t l I id th
Feb 10 Feb 11
See all from Delanoe Pirard See all from AI Advances
Recommended from Medium


---
*Page 64*


In by In by
Level Up Co… Gaurav Shriv… Data Scienc… Han HELOIR …
Build Multi Agent AI The February Reset:
D R h Th L b F
How I designed a planning- How Gemini 3.1 Pro, Claude
fi t lti t h O 4 6 d GPT 5 3 C d
Feb 20 Feb 21
In by Will Lockett
Predict srgg6701
Musk Has Totally Lost
Amazon Just
Hi Mi d
C fi d M W t
He is a literal lunatic.
Big Tech is now officially held
h t b th AI b bbl
Feb 19 Feb 21


---
*Page 65*


In by In by
Artificial Intelligenc… Faisal… Realworld AI Use… Chris Du…
Amazon’s AI But but but, can’t I just
Ulti t Wh 80% d thi i Ch tGPT?
The $200 billion bet that’s Your client just compared your
h i Bi T h’ i th b ild t f
Feb 17 Feb 17
See more recommendations