# GitHub - maxritter_claude-pilot_ Claude Code is powerful. Pilot makes it reliable. Start a task, grab a coffee, come back to

*Converted from: GitHub - maxritter_claude-pilot_ Claude Code is powerful. Pilot makes it reliable. Start a task, grab a coffee, come back to.PDF*



---
*Page 1*


maxritter/claude-pilot Public
Claude Code is powerful. Pilot makes it reliable. Start a task, grab a coffee, come back to production-grade code. Tests enforced. Context preserved.
Quality automated.
claude-pilot.com
View license
651 stars 56 forks Branches Tags Activity
Star Notifications
Code Issues 2
main 2Branches 34Tags Go to file Go to file Code
semantic-release-bot chore(release): 6.5.3 [skip ci] 89bd00e · 14 hours ago
.claude/skills/update-refs chore: remove hardcoded counts and improve qu… last week
.devcontainer fix: split spec command into phases, add design … last week
.githooks fix: Add pre-commit hook for console build artifa… 14 hours ago
.github feat: Add Usage tab with cost/token tracking (#50) 15 hours ago
.vscode fix: split spec command into phases, add design … last week
console chore(release): 6.5.3 [skip ci] 14 hours ago
docs feat: Add Usage tab with cost/token tracking (#50) 15 hours ago
installer chore(release): 6.5.3 [skip ci] 14 hours ago
launcher chore(release): 6.5.3 [skip ci] 14 hours ago
pilot chore(release): 6.5.3 [skip ci] 14 hours ago
.coderabbit.yaml feat: Add Usage tab with cost/token tracking (#50) 15 hours ago
.gitattributes feat: Add Usage tab with cost/token tracking (#50) 15 hours ago
.gitignore fix: Add .cursor/ to .gitignore and update vault do… 14 hours ago
.python-version fix: Python 3.12 ABI compatibility for CCP binary 3 weeks ago
.releaserc.json fix: stale session cleanup, context hook, install d… last week
CHANGELOG.md chore(release): 6.5.3 [skip ci] 14 hours ago
LICENSE fix: Improve installer reliability, console UX, and v… 2 days ago
README.md chore(release): 6.5.3 [skip ci] 14 hours ago
cliff.toml fix: prevent changelog duplication from squash … 2 days ago
install.sh fix: split spec command into phases, add design … last week
mcp_servers.json feat: add mcp-cli integration for custom MCP ser… last month
pyproject.toml Replace seats with activations, refactor hooks an… 2 days ago
uv.lock fix: migrate to playwright-cli, backport console st… 5 days ago
README License


---
*Page 2*


Claude Code is powerful. Pilot makes it reliable.
Start a task, grab a coffee, come back to production-grade code.
Tests enforced. Context preserved. Quality automated.
ssttaarrss 664422 SSttaarrHHiissttoorryy cchhaarrtt ddoowwnnllooaaddss 882266 PPRRss wweellccoommee
⭐ Star this repo · 🌐 Website · 🔔 Follow for updates · 📋 Changelog · 📄 License
curl -fsSL https://raw.githubusercontent.com/maxritter/claude-pilot/main/install.sh | bash
Works on macOS, Linux, and Windows (WSL2).
Why I Built This
I'm a senior IT freelancer from Germany. My clients hire me to ship production-quality code — tested, typed, formatted, and reviewed. When
something goes into production under my name, quality isn't optional.
Claude Code writes code fast. But without structure, it skips tests, loses context, and produces inconsistent results. I tried other frameworks —
they burned tokens on bloated prompts without adding real value. Some added process without enforcement. Others were prompt templates
that Claude ignored when context got tight. None made Claude reliably produce production-grade code.
So I built Pilot. Instead of adding process on top, it bakes quality into every interaction. Linting, formatting, and type checking run as enforced
hooks on every edit. TDD is mandatory, not suggested. Context is monitored and preserved across sessions. Every piece of work goes through
verification before it's marked done.


---
*Page 3*


Before & After
Without Pilot With Pilot
Writes code, skips tests TDD enforced — RED, GREEN, REFACTOR on every feature
No quality checks Hooks auto-lint, format, type-check on every file edit
Context degrades mid-task Endless Mode with automatic session handoff
Every session starts fresh Persistent memory across sessions via Pilot Console
Hope it works Verifier sub-agents perform code review before marking complete
No codebase knowledge Production-tested rules loaded into every session
Generic suggestions Coding standards activated conditionally by file type
Changes mixed into branch Isolated worktrees — review and squash merge when verified
Manual tool setup MCP servers + language servers pre-configured and ready
Requires constant oversight Start a task, grab a coffee, come back to verified results
Why This Approach Works
There are other AI coding frameworks out there. I tried them. They add complexity — dozens of agents, elaborate scaffolding, thousands of
lines of instruction files — but the output doesn't improve proportionally. More machinery burns more tokens, increases latency, and creates
more failure modes. Complexity is not a feature.
Pilot optimizes for output quality, not system complexity. The rules are minimal and focused. There's no big learning curve, no project
scaffolding to set up, no state files to manage. You install it, run , and the quality guardrails are just there — hooks, TDD, type checking,
pilot
formatting — enforced automatically on every edit, in every session.
This isn't a vibe coding tool. It's built for developers who ship to production and need code that actually works. Every rule in the system comes
from daily professional use: real bugs caught, real regressions prevented, real sessions where the AI cut corners and the hooks stopped it. The
rules are continuously refined based on what measurably improves output.
The result: you can actually walk away. Start a task, approve the plan, then go grab a coffee. When you come back, the work is done —
/spec
tested, verified, formatted, and ready to ship. Endless Mode handles session continuity automatically, quality hooks catch every mistake along
the way, and verifier agents review the code before marking it complete. No babysitting required.
The system stays fast because it stays simple. Quick mode is direct execution with zero overhead — no sub-agents, no plan files, no directory
scaffolding. You describe the task and it gets done. adds structure only when you need it: plan verification, TDD enforcement,
/spec
independent code review, automated quality checks. Both modes share the same quality hooks. Both modes hand off cleanly across sessions
with Endless Mode.
Getting Started
Prerequisites
Claude Subscription: Solo developers should choose Max 5x for moderate usage or Max 20x for heavy usage. Teams and companies should
use Team Premium which provides 6.25x usage per member plus SSO, admin tools, and billing management. Using the API instead may lead
to much higher costs.
Installation
cd into your project folder, then run:
curl -fsSL https://raw.githubusercontent.com/maxritter/claude-pilot/main/install.sh | bash


---
*Page 4*


Choose your environment:
Local Installation — Install directly on your system using Homebrew. Works on macOS, Linux, and Windows (WSL2).
Dev Container — Pre-configured, isolated environment with all tools ready. No system conflicts and works on any OS.
After installation, run pilot or ccp in your project folder to start Claude Pilot.
What the installer does
Installing a Specific Version
If the current version has issues, you can install a specific stable version (see releases):
export VERSION=6.5.3
curl -fsSL https://raw.githubusercontent.com/maxritter/claude-pilot/main/install.sh | bash
How It Works
/sync — Sync Rules & Standards
Run /sync to sync rules and standards with your codebase. Explores your codebase, builds a semantic search index, discovers
undocumented patterns, updates project documentation, and creates new custom skills. Run it once initially, then anytime again:
pilot
> /sync
What /sync does in detail
/spec — Spec-Driven Development
Best for complex features, refactoring, or when you want to review a plan before implementation:
pilot
> /spec "Add user authentication with OAuth and JWT tokens"
Discuss → Plan → Approve → Implement → Verify → Done
│ ↑ ↓
│ └─ Loop─┘
▼
Task 1 (TDD)
▼
Task 2 (TDD)
▼
Task 3 (TDD)
Plan Phase
Implement Phase
Verify Phase
Smart Model Routing
Pilot uses the right model for each phase — Opus where reasoning quality matters most, Sonnet where speed and cost matter:
Phase Model Why
Exploring your codebase, designing architecture, and writing the spec requires deep reasoning. A good plan
Planning Opus
is the foundation of everything.


---
*Page 5*


Phase Model Why
Catching gaps, missing edge cases, and requirement mismatches before implementation saves expensive
Plan Verification Opus
rework.
With a solid plan, writing code is straightforward. Sonnet is fast, cost-effective, and produces high-quality
Implementation Sonnet
code when guided by a clear spec.
Code Independent code review against the plan requires the same reasoning depth as planning — catching
Opus
Verification subtle bugs, logic errors, and spec deviations.
The insight: Implementation is the easy part when the plan is good and verification is thorough. Pilot invests reasoning power where it has the
highest impact — planning and verification — and uses fast execution where a clear spec makes quality predictable.
Quick Mode
Just chat. No plan file, no approval gate. All quality hooks and TDD enforcement still apply.
pilot
> Fix the null pointer bug in user.py
/learn — Online Learning
Capture non-obvious discoveries as reusable skills. Triggered automatically after 10+ minute investigations, or manually:
pilot
> /learn "Extract the debugging workflow we used for the race condition"
/vault — Team Vault
Share rules, commands, and skills across your team via a private Git repository:
pilot
> /vault
Private — Use any Git repo (GitHub, GitLab, Bitbucket — public or private)
Pull — Install shared assets from your team's vault
Push — Share your custom rules and skills with teammates
Version — Assets are versioned automatically (v1, v2, v3...)
Pilot CLI
The binary ( ) manages sessions, worktrees, licensing, and context. Run or with no arguments to
pilot ~/.pilot/bin/pilot pilot ccp
start Claude with Endless Mode.
Session & Context
Worktree Isolation
License & Auth
All commands support for structured output. Multiple Pilot sessions can run in parallel on the same project — each session tracks its
--json
own worktree and context state independently.
Rules, Commands & Skills
Create your own in your project's folder:
.claude/
Type Loaded Best for
Rules Every session, or conditionally by file type Guidelines Claude should always follow
Commands On demand via Specific workflows or multi-step tasks
/command


---
*Page 6*


Type Loaded Best for
Skills On demand, created via /learn Reusable knowledge from past sessions
Claude Pilot automatically installs best-practice rules, commands, and coding standards. Standards rules use paths frontmatter to activate
only when you're working with matching file types (e.g., Python standards load only when editing .py files). Custom skills are created by
/learn when it detects non-obvious discoveries, workarounds, or reusable workflows — and can be shared across your team via /vault.
Custom MCP Servers
Add your own MCP servers in two locations:
Config File How It Works Best For
.mcp.json Instructions load into context when triggered Lightweight servers (few tools)
mcp_servers.json Called via mcp-cli; instructions never enter context Heavy servers (many tools)
Run /sync after adding servers to generate documentation.
Under the Hood
The Hooks Pipeline
Hooks fire automatically at every stage of development:
SessionStart (on startup, clear, or compact)
Hook Type What it does
Memory loader Blocking Loads persistent context from Pilot Console memory
Session tracker Async Initializes user message tracking for the session
PostToolUse (after every Write / Edit / MultiEdit)
After every single file edit, these hooks fire:
Hook Type What it does
Dispatches to language-specific checkers: Python (ruff + basedpyright), TypeScript (Prettier +
file_checker.py Blocking
ESLint + tsc), Go (gofmt + golangci-lint). Auto-fixes formatting.
Non- Checks if implementation files were modified without failing tests first. Shows reminder to write
tdd_enforcer.py
blocking tests. Excludes test files, docs, config, TSX, and infrastructure.
Memory observer Async Captures development observations to persistent memory.
Non- Monitors context window usage. Warns as usage grows, forces handoff before hitting limits.
context_monitor.py
blocking Caches for 15 seconds to avoid spam.
PreToolUse (before search, web, or task tools)
Hook Type What it does
Routes WebSearch, WebFetch, Grep, Task, and plan mode tools to appropriate contexts. Prevents tools
tool_redirect.py Blocking
from being accidentally lost during plan/implement phases.
Stop (when Claude tries to finish)
Hook Type What it does
If an active spec exists with PENDING or COMPLETE status, blocks stopping. Forces verification to
spec_stop_guard.py Blocking
complete before the session can end.


---
*Page 7*


Hook Type What it does
Session summarizer Async Saves session observations to persistent memory for future sessions.
Endless Mode
The context monitor tracks usage in real-time and manages multi-session continuity:
As context grows, Pilot warns, then forces a handoff before hitting limits
Session state is saved to ~/.pilot/sessions/ with continuation files — picks up seamlessly in the next session
During /spec, Pilot won't start a new phase when context is high — it hands off instead
Multiple Pilot sessions can run in parallel on the same project without interference
Status line shows live context usage, memory status, active plan, and license info
Built-in Rules
Production-tested best practices loaded into every session. These aren't suggestions — they're enforced standards.
Quality Enforcement (4 rules)
Context Management (3 rules)
Language Standards (3 rules)
Tool Integration (6 rules)
Development Workflow (6 rules)
Built-in Coding Standards
Conditional rules activated by file type — loaded only when working with matching files:
Standard Activates On Coverage
Python *.py uv, pytest, ruff, basedpyright, type hints, docstrings
TypeScript *.ts, *.tsx, *.js, *.jsx npm/pnpm, Jest, ESLint, Prettier, React patterns
Go *.go Modules, testing, formatting, error handling
Testing Strategies *test*, *spec* Unit vs integration vs E2E, mocking, coverage goals
API Design *route*, *endpoint*, *api* RESTful patterns, response envelopes, error handling, versioning
Data Models *model*, *schema*, *entity* Database schemas, type safety, migrations, relationships
Components *component*, *.tsx, *.vue Reusable patterns, props design, documentation, testing
CSS / Styling *.css, *.scss, *.tailwind* Naming conventions, organization, responsive design, performance
Responsive Design *.css, *.scss, *.tsx Mobile-first, breakpoints, Flexbox/Grid, touch interactions
Design System *.css, *.tsx, *.vue Color palette, typography, spacing, component consistency
Accessibility *.tsx, *.jsx, *.vue, *.html WCAG compliance, ARIA attributes, keyboard nav, screen readers
DB Migrations *migration*, *alembic* Schema changes, data transformation, rollback strategy
Query Optimization *query*, *repository*, *dao* Indexing, N+1 problems, query patterns, performance
MCP Servers
External context always available to every session:
Server Purpose
Context7 Library documentation lookup — get API docs for any dependency
mem-search Persistent memory search — recall context from past sessions


---
*Page 8*


Server Purpose
web-search Web search via DuckDuckGo, Bing, and Exa
grep-mcp GitHub code search — find real-world usage patterns across repos
web-fetch Web page fetching — read documentation, APIs, references
Language Servers (LSP)
Real-time diagnostics and go-to-definition, auto-installed and configured:
Language Server Capabilities
Python basedpyright Strict type checking, diagnostics, go-to-definition. Auto-restarts on crash (max 3).
TypeScript vtsls Full TypeScript support with Vue compatibility. Auto-restarts on crash (max 3).
Go gopls Official Go language server. Auto-restarts on crash (max 3).
All configured via .lsp.json with stdio transport.
Claude Pilot Console
Access the web-based Claude Pilot Console at http://localhost:41777 to visualize your development workflow:
What Users Say
"I stopped reviewing every line Claude writes. The hooks catch formatting and type errors automatically, TDD catches logic errors, and the
spec verifier catches everything else. I review the plan, approve it, and the output is production-grade."
"Other frameworks I tried added so much overhead that half my tokens went to the system itself. Pilot is lean — quick mode has zero
scaffolding, and even /spec only adds structure where it matters. More of my context goes to actual work."
"Endless Mode solved the problem I didn't know how to fix. Complex refactors used to stall at 60% because Claude lost track of what it
was doing. Now it hands off cleanly and the next session picks up exactly where the last one stopped."


---
*Page 9*


License
Claude Pilot is source-available under a commercial license. See the LICENSE file for full terms.
Tier Seats Includes
Solo 1 All features, continuous updates, GitHub support
Team Multi Solo + multiple seats, dedicated email support, priority feature requests
Details and licensing at claude-pilot.com.
FAQ
Does Pilot send my code or data to external services?
No code, files, prompts, project data, or personal information ever leaves your machine through Pilot. All development tools — vector search
(Vexor), persistent memory (Pilot Console), session state, and quality hooks — run entirely locally.
Pilot makes external calls only for licensing. Here is the complete list:
When Where What is sent
License validation (once per 24h) License key, organization ID
api.polar.sh
License activation (once) License key, machine fingerprint, OS, architecture, Python version
api.polar.sh
Tier, Pilot version, OS, architecture, Python version, machine
Activation analytics (once) claude-
fingerprint
pilot.com
Trial start (once) claude- Hashed hardware fingerprint, OS, Pilot version, locale
pilot.com
Trial heartbeat (each session during
claude- Hashed hardware fingerprint, OS, Pilot version
trial)
pilot.com
That's it. No code, no filenames, no prompts, no project content, no personal data. The validation result is cached locally, and Pilot works fully
offline for up to 7 days between checks. Beyond these licensing calls, the only external communication is between Claude Code and
Anthropic's API — using your own subscription or API key.
Is Pilot enterprise-compliant for data privacy?
Yes. Your source code, project files, and development context never leave your machine through Pilot. The only external calls Pilot makes are
for license management — validation (daily to ), activation and analytics (one-time), and trial heartbeats. None of these transmit
api.polar.sh
any code, project data, or personal information. Enterprises using Claude Code with their own API key or Anthropic Enterprise subscription can
add Pilot without changing their data compliance posture.
What are the licenses of Pilot's dependencies?
All external tools and dependencies that Pilot installs and uses are open source with permissive licenses (MIT, Apache 2.0, BSD). This includes
ruff, basedpyright, Prettier, ESLint, gofmt, uv, Vexor, playwright-cli, and all MCP servers. No copyleft or restrictive-licensed dependencies are
introduced into your environment.
Do I need a separate Anthropic subscription?
Yes. Pilot enhances Claude Code — it doesn't replace it. You need an active Claude subscription — Max 5x or 20x for solo developers, or Team
Premium for teams and companies. Using the Anthropic API directly is also possible but may lead to much higher costs. Pilot adds quality
automation on top of whatever Claude Code access you already have.
Does Pilot work with any programming language?
Can I use Pilot on multiple projects?
Can I customize the rules and hooks?
Yes. All rules in are markdown files you can edit, extend, or replace. Hooks are Python scripts you can modify. Built-in coding
.claude/rules/
standards are conditional rules that activate by file type and can be customized. You can also create custom skills via . Project-
/learn
specific rules override global defaults. Use to share customizations across your team.
/vault


---
*Page 10*


Changelog
See the full changelog at pilot.openchangelog.com.
Contributing
Releases 34
v6.5.3 Latest
14 hours ago
+ 33 releases
Contributors 8
Languages
TypeScript81.6% Python10.3% JavaScript7.6% Shell0.3% CSS0.2% HTML0.0%