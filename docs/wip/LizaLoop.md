# LizaLoop

*Converted from: LizaLoop.PDF*



---
*Page 1*


liza-mas/liza
Public
Code Issues
About
Disciplined Multi Coding Agent System
Readme
Apache-2.0 license
Contributing
Activity
97 stars
4 watching
20 forks
Report repository
Releases
10
v0.5.4 Latest
yesterday
+ 9 releases
Packages
No packages published
Contributors 5
Languages
Go94.1% Go Template1.9% HTML1.7% Python1.5% Other0.8%
2Branches 10Tags Go to file Go to file Code
tangi-vassandclaude docs(release): add v0.5.4 release notes
503898f · yesterday
.github/workflows test(integration): add e2e full… 3 weeks ago
cmd fix(cli): auto-fallback to headl… 5 days ago
contracts docs(readme,tools): add L4 … 3 days ago


---
*Page 2*


docs docs(release): add v0.5.4 rel… yesterday
internal fix(hooks): redirect enforce-i… yesterday
lessons docs(lessons): broaden edit-… last week
plans fix(plan): keep impact history… 2 weeks ago
skills refactor(skills): compress cl… 3 days ago
specs docs(architecture): backfill A… 3 days ago
templates refactor(roles): rename Plan… last month
.editorconfig chore: add basic python setup 3 months ago
.gitignore feat(init): write SUPPORT.md… last week
.goreleaser.yaml feat: add release infrastructu… 2 months ago
.pre-commit-config.yaml chore(jscpd): ignore tests 2 months ago
CONTRIBUTING.md docs: add CONTRIBUTING.md yesterday
GUARDRAILS.md feat(init): write SUPPORT.md… last week
INVARIANTS.md docs: add system invariants … 2 weeks ago
LICENSE Initial commit 3 months ago
Makefile feat: interactive onboarding … last week
README.md docs(readme): add ANTHRO… 2 days ago
RELEASE.md feat: add release infrastructu… 2 months ago
REPOSITORY.md feat(tui): add Bubbletea TUI f… last week
go.mod feat(tui): add Bubbletea TUI f… last week
go.sum feat: interactive onboarding … last week
install.sh feat(install): support building… last week
mypy.ini chore: add basic python setup 3 months ago
pyproject.toml chore: add basic python setup 3 months ago
uv.lock chore: add basic python setup 3 months ago
README More
Liza: Hardened Multi-Agent Coding
Because "it worked in the demo" is not what on-call engineers are looking for.
The full hardening inventory to push to production with peace of mind.


---
*Page 3*


Demo video (45min).
AAsskkDDeeeeppWWiikkii
Table of Contents
What is Liza?
How Liza Compares
Getting Started
Architecture
Status
Naming
License
What is Liza?
Liza is simultaneously a Pairing and Multi-Agent System (MAS) optimized for doing things
right on the first pass — with the auditability to prove it. Liza bets on time-to-quality and durable
codebase maintainability through automated reviews and documentation (e.g. the ADR Backfill
skill).
Soufiane Keli – VP Software Engineering, Octo Technology (Accenture) – maps AI
engineering maturity across 5 levels, from autocomplete (L1) to software factory (L5, still
theoretical). He places Liza at L4 – Collaborative Agent Networks:
"Multiple specialized agents work together on design, code, testing, and deployment. Humans
orchestrate. This is typically what's happening with BMAD, BEADS, and LIZA. Very few
organizations have genuinely reached this level in 2026."
Main characteristics:


---
*Page 4*


Behavior, Posture, Know-How — three layers that make coding agents useful:
Behavior: A behavioral contract enforces governance intrinsically — not through external
scaffolding as Harness Engineering does. Optional project guardrails extend the contract
with project-specific constraints.
Posture: Original pairing postures (User Duck, Socratic Coach, Challenger, etc.)
Know-How: 20 composable skills encode methodology
Full analysis
Autonomous Spec-driven Coding System:
From general goal to code and tests, with multi-stage decomposition into intermediate
artifacts (epics, US, implementation plans) that are AI generated but human reviewed.
Automatic task decomposition based on complexity with dependency management for
parallel execution.
Multi-sprints: agents are fully autonomous within a sprint, user steers between sprints via
Liza CLI - review of produced artifacts, continuous improvement, and steering of the next
sprint
A TUI ( ) displays live system state and lets you spawn agents, pause/resume,
liza tui
add tasks, and trigger checkpoints.
Adversarial architecture:
One Orchestrator role + 8 others. More to come (Architect, ...).
Every activity is dual — a doer and a reviewer: epic planning, epic writing, US writing, code
planning, coding - everything.
They interact like on a PR review — submission, feedback comments, verdict, revised
submission, etc. — until approval.
Hybrid hardened architecture:
LLM agents wrapped by code-enforced supervisors and working on isolated git
worktrees.
The supervisor does the deterministic code-enforced actions (worktree management,
merges, TDD enforcement, etc), leaving the judgment to the agent. Strict task state
machine with 43+ validation rules.
Agents communicate and act through Liza's MCP tools.
20k LOC of Go (+60k of tests). Liza is not a prompt collection.
Agent logs recording for automatic analysis and continuous improvements (token
optimization, MCP server usage analysis, ...)
Multi-model:
Liza wraps provider CLIs, not their APIs. This means your existing subscription (Claude
Max, ChatGPT Pro, etc.) works — no API keys or per-token billing required — and your
personal setup is used.


---
*Page 5*


BYOM: Claude Code, Codex CLI, Kimi, Mistral, Gemini. Not all are made equal though.
Structured workflow:
Defined as a composable and customizable YAML pipeline with declarative sub-pipelines
(e.g. specification, coding).
Coordination is performed via an auditable YAML blackboard that acts as both the
Kanban board of the agents with full historized state details and the support for PR-like
comments made by the reviewer agents.
Agents don't discover work — they receive pre-claimed tasks in bootstrap prompt.
Eliminates race conditions and cognitive overhead.
Resilience:
Circuit breaker: pattern detection (loops, repeated failures) triggers automatic sprint
checkpoint
Crash recovery: and commands for idempotent cleanup
recover-agent recover-task
after hard crashes
Context handoff: agents hand off with structured notes when approaching context limits
See the complete vision and genesis of Liza.
What it looks like in practice
Without the contract, an agent that hits a problem it can't solve has two options: admit failure
or fake progress. Its training overwhelmingly favors the second. Faking progress feels
collaborative — look, I'm trying things!
So it spirals. Random changes dressed up as hypotheses. Each iteration more elaborate, more
confident, more wrong. You watch the diff grow and wonder if any of this is moving toward a
solution. If you're clever, you end up reverting.
Under the contract, there's a third option: say "I'm stuck" and mean it. The contract makes that
safe — no penalty for uncertainty, no pressure to perform progress. And the Approval Request
mechanism forces agents to write down their reasoning before acting. "I'll try random things
until something works" is hard to write in a structured plan. Surface the reasoning, and the
reasoning improves — no better model required.
This won't self-correct. Sycophancy drives engagement — that's what gets optimized. Acting
fast with little thinking controls inference costs. Model providers optimize for adoption and
cost efficiency, not engineering reliability.
Ten months of pairing under this contract, and the vigilance tax dropped to near zero. I can
mostly focus on the architecture and more specifically build up a MAS upon the contract.


---
*Page 6*


Here is a demo video of an implementation of a basic Todo CLI using Liza in Multi-agent mode
- spec-driven with intermediate epic and User Story creation, fully autonomous agents within
sprints, human reviews between sprints.
How Liza Compares
MAS Architecture
The multi-agent coding space splits into four categories:
Orchestration frameworks (CrewAI, LangGraph, AutoGen) — general-purpose multi-agent
building blocks; none address behavioral trust in software engineering.
Company simulators (MetaGPT, ChatDev) — SOP-based pipelines mimicking software
teams; trust assumed through process compliance.
Scheduler/runners (Symphony, Paperclip) — work dispatch and workspace isolation above
coding agents; trust delegated to whatever happens inside each session.
Behavioral enforcement (Liza) — deterministic supervisors enforce state transitions, role
boundaries, and merge authority mechanically; agents handle judgment under a behavioral
contract addressing 55+ failure modes.
Liza CrewAI Ruflo Symphony Paperclip
Behavioral Track-
Post-hoc
Trust contract (55+ record Implementation- Budget/approva
output
approach failure based (Q- dependent governance
validation
modes) learning)
Adversarial Optional
Review loop doer/reviewer manager None None None
pairs mode
Claude
Code-
Role Prompt hooks None (single- Org chart
enforced (Go
enforcement suggestion (provider- agent) hierarchy
supervisor)
specific)
Pattern
Structural Retry on
Failure matching Implementation- Budget auto-
prevention + output
handling from past dependent pause
escalation failure
successes
Where Liza leads — no competitor offers any of these:
Failure mode catalog (55+) with mechanical countermeasures


---
*Page 7*


Adversarial doer/reviewer pairs on every task
Code-enforced role boundaries (Go supervisor, not prompt suggestions)
Provider compliance matrix tested empirically across 5 providers
Multi-sprint continuity, crash recovery, context pressure management
Where others lead:
Ecosystem: CrewAI (45k stars, production v1.9.0, enterprise product) and MetaGPT (64k
stars) have far larger communities
Cost tracking: Paperclip ships per-agent/task/project budgets today; Liza's is planned
Flexibility: CrewAI works for any domain; Liza is software-engineering-only
Spec-Driven Process
Spec-driven development is becoming the standard approach for AI coding. Most tools differ in
what altitude they expect the input at and who owns product decisions.
Liza Spec Kit OpenSpec Kiro GSD
High-level Detailed
High-level goal goal delta- Interactive 3- Detailed
→
Input level (problem, users, agent- specs on doc spec
behavior, scope) generated existing generation required
spec system
Agent
Human via pairing Human Agent drives, Human
Who decides generates,
(Coach/Challenger (spec pre- human (pre-
what to build human
modes) decided) confirms written)
approves
Agent Slash Planner
Orchestrator Agent
decomposes commands sizes to
Decomposition decomposes into decomposes
spec into structure context
adversarial tasks from spec
tasks tasks budget
Advisory
(verify None Checker +
Doer/reviewer
Review None warns, (single- verifier (n
pairs with quorum
doesn't agent) adversari
block)


---
*Page 8*


Most tools either expect the detailed spec already done (OpenSpec, GSD) or have the agent
write it (Spec Kit, Kiro, MetaGPT). Liza treats goal-setting as a synchronous human-agent
collaboration where the human makes product decisions and the agent helps surface gaps —
then enforces those decisions mechanically during execution.
Rule of thumb: agents may make implementation choices but not product decisions. The goal
document is where every product decision lives. The goal-setting phase uses pairing (Coach
mode for surfacing WHY, Challenger mode for stress-testing WHAT) because this phase has
the highest decision density — every ambiguity resolved here prevents wrong turns
downstream.
Full competitive survey
→
Getting Started
Requirements
A supported coding agent CLI: Claude Code, Codex, Kimi, Mistral, or Gemini (see Provider
Compatibility). Liza runs on top of these CLIs — your provider subscription covers usage, no
separate API billing needed.
Git 2.38+ (for full worktree support)
Go 1.25.5+ (only for building from source — pre-built binaries available via )
install.sh
Installation
Liza relies on two executables: and :
liza liza-mcp
By default they install to (created automatically, no sudo needed).
~/.local/bin
Set the environment variable to override.
INSTALL_DIR
If upgrading from a previous install in , old binaries are removed
/usr/local/bin
automatically.
Quick install (latest release, macOS/Linux):
curl -fsSL https://raw.githubusercontent.com/liza-mas/liza/main/install.sh | b
Options:
# Specific version
curl -fsSL https://raw.githubusercontent.com/liza-mas/liza/main/install.sh | V
# Build from a branch (requires Go and make)
curl -fsSL https://raw.githubusercontent.com/liza-mas/liza/main/install.sh | B


---
*Page 9*


# Custom directory
curl -fsSL https://raw.githubusercontent.com/liza-mas/liza/main/install.sh | I
From a local clone:
git clone https://github.com/liza-mas/liza.git && cd liza
make install
Verify:
liza version
liza setup # initial install or liza upgrade: installs contracts + skills to
# With: agent-specific activation (skill symlinks, contract config)
liza setup --claude --codex --gemini --mistral
⚠ Customize your tool setup:
The installed ships with a default MCP server and tool
~/.liza/AGENT_TOOLS.md
configuration. It defines which tools agents prefer (IDE integrations, search providers,
documentation sources, etc.) and is specific to each user's environment.
Context management is of paramount importance. Make sure you use tools that reduce
token usage.
Recos: RTK, filesystem MCP, MorphLLM MCP, Perplexity MCP.
Edit to match your own setup — remove tools you don't have, add
~/.liza/AGENT_TOOLS.md
ones you do, and adjust precedence rules accordingly.
Or better, provide your own file at install time: .
liza setup --agent-tools ~/my-tools.md
To init your project repo, do:
# Interactive wizard (recommended for first use):
liza init
# Or with explicit flags:
liza init --claude --codex --gemini --mistral
The interactive wizard walks through mode selection (pairing vs full MAS), agent selection, and
handles existing conflicts automatically. Claude is fully automated; for other CLIs
CLAUDE.md
see contract activation for additional manual steps.
Pairing and MAS Modes


---
*Page 10*


New to Liza? Start with Pairing mode — it's the fastest way to experience how the
behavioral contract changes agent behavior. The trust you build watching agents pause at
gates, surface assumptions, and validate before claiming done is what makes letting them
run autonomously in Multi-Agent mode a comfortable next step.
Pairing: See Pairing Guide — human-agent collaboration under contract
Multi-Agent (Liza): See USAGE, then try the DEMO
Reference: Configuration · Recipes · Troubleshooting
Pairing mode — install once, then start coding in any project ( still required per
liza init
project):
When starting your CLI session ( , , ...), pairing mode will be selected
claude codex
automatically. It should start by displaying a canary test inspired by Van Halen's M&M's trick —
Four words coming from four different contract files to show what the agent actually read
thoroughly. Reading the contract files is enforced by a hook for Claude, by instructions for other
agents.
The agent reads the contract, builds mental models, and operates as a senior peer: analyzing
before acting, presenting approval requests at every state change, validating before claiming
done. Or you may choose to make it your Socratic colleague, your rubber duck, or your
challenger.
Multi-agent mode — autonomous spec-to-code pipeline:
1. . Use the
liza init "[Goal description]" --spec vision.md --entry-point detailed-
option to skip the spec phase and go coding directly.
spec
2. — the TUI shows live system state (agents, tasks, alerts, sprint metrics). From it
liza tui
you can spawn agents with role autocompletion ( ), pause/resume the system, add tasks,
s
and trigger sprint checkpoints. Check Quick Start for required roles and options (using a CLI
other than Claude, logging).
Refer to How to Produce a Goal Document For Liza to write a good input doc to use as a
--
argument.
spec
Common Commands
liza setup # One-time global setup
liza setup --agent-tools ~/my-tools.md # Custom AGENT_TOOLS.md
liza init "Project goal" --spec specs/vision.md # Initialize blackboard
liza init "Goal" --spec s.md \
--config pipeline.yaml --entry-point epic-planning # Pipeline-configured ini
liza add-task --id t1 --desc "..." --spec "..." \
--done "..." --scope "..." # Add tasks


---
*Page 11*


liza tui # Live TUI (spawn agents,
liza agent coder # Start agent supervisor (
liza validate # Validate state
liza get tasks # Query tasks
liza status # Dashboard overview
liza proceed # Transition between pipel
liza pause / liza resume # Human intervention
liza stop / liza start # System control
liza sprint-checkpoint # Sprint checkpoint
liza recover-agent <id> # Crash recovery (agents)
liza recover-task <id> # Crash recovery (tasks)
liza analyze # Circuit breaker analysis
⚠ To use Claude Code with your Claude subscription, make sure the
ANTHROPIC_API_KEY environment variable is not set by default on a new shell start
(Claude support, not specific to Liza).
Architecture
Most spec-driven multi-agent systems are LLM-all-the-way-down: agents coordinating agents,
with compliance dependent on prompt adherence and artifact-based workflows.
Liza is a hybrid system:
The agents are the popular coding agent CLIs.
The workflow is declarative but relies on a code-enforced state machine
The supervisors that wrap every agent and the validation rules are also deterministic Go
code. This means critical invariants — state transitions, role boundaries, merge authority,
TDD gates — are enforced mechanically, not by asking a LLM to please follow rules. Liza's
mechanical layer cannot fabricate, cannot skip gates, cannot interpret rules flexibly.
The LLM side is equally differentiated. Liza agents operate under a behavioral contract: 55+
documented LLM failure modes each mapped to a specific countermeasure, an explicit
state machine with forbidden transitions, and tiered rules that define what degrades
gracefully versus what never bends.
Reliability is built into every component.


---
*Page 12*


User
commands
Go CLI · liza YAML Pipeline & Ro
spawns specializes
Roles aren't composable, Skills are: agents aren't constrained regarding their capabilities by a
rigid "Act as a..." prompt and may use any skill they consider relevant to adapt to the situation.
Liza has the built-in capability to do things right on the first pass.
Liza has 9 roles organized in two pipeline phases:
Specification phase: orchestrator, epic-planner, epic-plan-reviewer, us-writer, us-reviewer
Coding phase: orchestrator, code-planner, code-plan-reviewer, coder, code-reviewer
┌─────────────────────────────────────────────────────────────┐
│ Human │
│ (leads specs, observes terminals, reads blackboard, │
│ kills agents, pauses system) │
└─────────────────────────────────────────────────────────────┘
│
┌─────────── Specification Phase ──────────┐
│ │
│ Orchestrator (decomposes & rescopes) │
│ Epic Planner ←→ Epic Plan Reviewer │
│ US Writer ←→ US Reviewer │
│ │
└──────────────────┬───────────────────────┘
│ liza proceed
┌──────────── Coding Phase ────────────────┐
│ │
│ Orchestrator (decomposes & rescopes) │
│ Code Planner ←→ Code Plan Reviewer │
│ Coder ←→ Code Reviewer │
│ │
└──────────────────┬───────────────────────┘
│
▼
┌─────────────────┐
│ .liza/ │
│ state.yaml │ ← blackboard
│ log.yaml │ ← activity history
│ alerts.log │ ← watch daemon output
│ archive/ │ ← terminal-state tasks


---
*Page 13*


└─────────────────┘
│
▼
┌─────────────────┐
│ .worktrees/ │
│ task-1/ │ ← isolated workspaces
│ task-2/ │
└─────────────────┘
See Architecture and C4 Diagrams.
Task Lifecycle
Each role pair follows the same intra-pair flow (concrete state names are role-pair-specific, e.g.
, ):
DRAFT_CODE IMPLEMENTING_CODE
initial → executing → submitted → reviewing → approved → MERGED
│ ↑ ↓ │
│ └────── rejected ──────┘ │
│ ↓
├──> BLOCKED INTEGRATION_FAILED
│ ├──> SUPERSEDED
│ └──> ABANDONED
│
└──> initial (release claim)
Inter-pair transitions ( ) create downstream tasks between sprints:
liza proceed
Spec phase Coding phase
Epic Planner ─approved─► MERGED Code Planner ─approved─►
MERGED
│ liza proceed (epic-to-us) │ liza proceed (code-
plan-to-coding)
▼ ▼
US Writer ─approved─► MERGED Coder ─approved─► MERGED
│ liza proceed (us-to-coding)
▼
Code Planner (coding phase)
Example of a task on the blackboard:
- id: code-planning-1-code-3
type: coding
role_pair: coding-pair
description: Role infrastructure recognizes the 4 new roles with correct


---
*Page 14*


status: MERGED
priority: 1
assigned_to: coder-2
base_commit: e7625ed69318836dd495b22855df3a8b91fe32b5
iteration: 1
review_commit: 9d9254b893af477fc34f48063169634d200fa332
approved_by: code-reviewer-1
merge_commit: 2fa6399223262df6a87c6b1354dfc882b73114c5
lease_expires: 2026-03-06T01:47:22.075108537Z
spec_ref: specs/plans/sub-pipelines-phase2.md
done_when: ToWorkflow("epic-planner") returns "epic_planner" (and all 4
scope: internal/roles/roles.go, internal/roles/roles_test.go, internal/m
created: 2026-03-06T01:17:00.99638669Z
history:
- time: 2026-03-06T01:17:22.075108537Z
event: claimed
agent: coder-2
- time: 2026-03-06T01:19:30.131578505Z
event: pre_execution_checkpoint
agent: coder-2
files_to_modify:
- internal/roles/roles.go
- internal/roles/roles_test.go
- internal/models/state.go
intent: Add 4 new role constants (epic-planner, epic-plan-reviewer,
validation_plan: 'Run `go test ./internal/roles/ ./internal/models/`
- time: 2026-03-06T01:22:05.371651393Z
event: submitted_for_review
agent: coder-2
- time: 2026-03-06T01:24:30.366073081Z
event: approved
agent: code-reviewer-1
- time: 2026-03-06T03:06:35.560908548+01:00
event: merged
agent: code-reviewer-1
commit: 2fa6399223262df6a87c6b1354dfc882b73114c5
tests_ran: false
Status
See Release Notes for version history and RELEASE.md for maintainer release workflow.
Where Liza works today:
Pairing mode is battle-tested — agents write ~90% of production code under human
supervision


---
*Page 15*


Multi-agent mode produces solid specs and code through the full goal-to-merge pipeline
with 9 roles across 2 phases — starting from release v0.4.0, all major Liza changes are
implemented using this mode
Liza is a collaborative agent network (L4 AI maturity) but its architecture has been designed to
support a software factory (L5) where humans focus on strategy and product vision. Still a long
way to go.
Implemented roles:
Orchestrator (decomposes goal into planning tasks)
Epic Planner / Epic Plan Reviewer
US Writer / US Reviewer
Code Planner / Code Plan Reviewer
Coder / Code Reviewer
Planned role pairs:
Sprint Analyzer role — analyze agent logs at sprint boundaries, capitalize on patterns via
lesson-capture
Architect / Architecture Reviewer — define architecture from specs for coders to follow
Security Auditor / Security Audit Reviewer — review the security of the code
Roadmap:
Integration sub-pipeline — validate a batch of commits so it can be safely merged to main.
For now, an extra pass of LLM-assisted review before merging to main is recommended.
Context handoff as blackboard event — structured positive/negative findings on every task
completion
Deterministic pre/post hooks at role transitions — mechanical checks before spawning
agents and before their handoff
Orchestrator-routed model selection — assign tasks to models based on estimated
complexity
Provider Compatibility
The contract is a capability test. It requires meta-cognitive machinery—the ability to parse
instructions as executable specifications, observe state, pause at gates.
Provider Classification Notes
Claude Opus
Fully compatible Reference provider
4.x


---
*Page 16*


Provider Classification Notes
GPT-5.x-Codex Fully compatible Equally capable
Compatible but poor on real-world
Kimi 2.5 Responsive to tooling feedback
tasks
Mistral Requires explicit activation and
Partial
Devstral-2 supervision
Gemini 2.5 Architectural limitation—no prompt-
Incompatible
Flash level fix
See Model Capability Assessment for detailed analysis.
Naming
Liza combines two references:
Lisa Simpson—the disciplined, systematic counterpoint to Ralph Wiggum. The Ralph Wiggum
technique loops agents until they converge through persistence. Lisa makes sure the work is
actually right.
ELIZA th 1966 h tb t th t d t t d t t d di l tt Li i b t