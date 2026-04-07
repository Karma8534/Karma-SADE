# ComposioHQ_agent-orchestrator_ Agentic orchestrator for parallel coding agents — plans tasks, spawns agents, and autonomousl

*Converted from: ComposioHQ_agent-orchestrator_ Agentic orchestrator for parallel coding agents — plans tasks, spawns agents, and autonomousl.PDF*



---
*Page 1*


agent-orchestrator
Code Issues 27 More
Watch 4
Agentic orchestrator for parallel coding agents — plans tasks, spawns agents, and autonomously handles CI fixes,
merge conflicts, and code reviews.
composio.dev
MIT license
Security policy
504 stars 70 forks 4 watching 96Branches 3Tags Activity Custom properties
Public repository
96Branches 3Tags Go to file t Go to file Add file Code
AgentWrapperandclaude docs: redesign README based on competitive research (#132)
ade1322 · yesterday
.changeset feat: seamless onboarding with enh… 5 days ago
.cursor feat: publish to npm under@compo… last week
.github/workflows fix: dashboard config discovery + C… 3 days ago
.husky feat: implement comprehensive sec… last week
artifacts feat: publish to npm under@compo… last week
changelog fix: migrate to hash-based project is… 4 days ago
docs feat(web): redesign dashboard, ses… yesterday
examples docs: update port references to refl… 3 days ago
packages feat(web): redesign dashboard, ses… yesterday
scripts fix: migrate to hash-based project is… 4 days ago
tests/integration feat: configurable terminal server p… 3 days ago
.gitignore fix: dashboard config discovery + C… 3 days ago
.gitleaks.toml feat: implement comprehensive sec… last week
.npmrc feat: publish to npm under@compo… last week
chore: add ESLint, Prettier, CI workfl… last week
.prettierignore


---
*Page 2*


.prettierrc chore: add ESLint, Prettier, CI workfl… last week
ARCHITECTURE.md fix: migrate to hash-based project is… 4 days ago
CLAUDE.md feat(web): redesign dashboard, ses… yesterday
CLAUDE.orchestrator.md fix: dashboard config discovery + C… 3 days ago
DASHBOARD_FIXES_SUMM… feat: seamless onboarding with enh… 5 days ago
LICENSE feat: publish to npm under@compo… last week
README.md docs: redesign README based on c… yesterday
SECURITY.md fix: migrate to hash-based project is… 4 days ago
SETUP.md docs: update port references to refl… 3 days ago
TROUBLESHOOTING.md fix: migrate to hash-based project is… 4 days ago
agent-orchestrator.yaml fix: dashboard config discovery + C… 3 days ago
agent-orchestrator.yaml.exa… feat: configurable terminal server p… 3 days ago
eslint.config.js feat: seamless onboarding with enh… 5 days ago
package.json feat: seamless onboarding with enh… 5 days ago
pnpm-lock.yaml fix: three spawn regressions from P… 3 days ago
pnpm-workspace.yaml feat: scaffold TypeScript monorepo … last week
test-ao-config.yaml feat: seamless onboarding with enh… 5 days ago
test-ao-config2.yaml feat: seamless onboarding with enh… 5 days ago
tsconfig.base.json feat: scaffold TypeScript monorepo … last week
README More
Agent Orchestrator
Spawn parallel AI coding agents. Monitor from one dashboard. Merge their PRs.
stars 501 license MIT PRsmerged 61 testcases 3,288


---
*Page 3*


Agent Orchestrator manages fleets of AI coding agents working in parallel on your codebase. Each agent
gets its own git worktree, its own branch, and its own PR. When CI fails, the agent fixes it. When reviewers
leave comments, the agent addresses them. You only get pulled in when human judgment is needed.
Agent-agnostic (Claude Code, Codex, Aider) · Runtime-agnostic (tmux, Docker) · Tracker-agnostic (GitHub,
Linear)
Quick Start
# Install
git clone https://github.com/ComposioHQ/agent-orchestrator.git
cd agent-orchestrator && bash scripts/setup.sh
# Configure your project
cd ~/your-project && ao init --auto
# Launch and spawn an agent
ao start
ao spawn my-project 123 # GitHub issue, Linear ticket, or ad-hoc
Dashboard opens at . Run for the CLI view.
http://localhost:3000 ao status
How It Works
ao spawn my-project 123
1. Workspace creates an isolated git worktree with a feature branch
2. Runtime starts a tmux session (or Docker container)
3. Agent launches Claude Code (or Codex, or Aider) with issue context
4. Agent works autonomously — reads code, writes tests, creates PR
5. Reactions auto-handle CI failures and review comments
6. Notifier pings you only when judgment is needed
Plugin Architecture
Eight slots. Every abstraction is swappable.
Slot Default Alternatives
Runtime tmux docker, k8s, process
Agent claude-code codex, aider, opencode
Workspace worktree clone
Tracker github linear
SCM github —


---
*Page 4*


Slot Default Alternatives
Notifier desktop slack, composio, webhook
Terminal iterm2 web
Lifecycle core —
All interfaces defined in . A plugin implements one interface and exports a
packages/core/src/types.ts
. That's it.
PluginModule
Configuration
# agent-orchestrator.yaml
port: 3000
defaults:
runtime: tmux
agent: claude-code
workspace: worktree
notifiers: [desktop]
projects:
my-app:
repo: owner/my-app
path: ~/my-app
defaultBranch: main
sessionPrefix: app
reactions:
ci-failed:
auto: true
action: send-to-agent
retries: 2
changes-requested:
auto: true
action: send-to-agent
escalateAfter: 30m
approved-and-green:
auto: false # flip to true for auto-merge
action: notify
CI fails → agent gets the logs and fixes it. Reviewer requests changes → agent addresses them. PR
approved with green CI → you get a notification to merge.
See for the full reference.
agent-orchestrator.yaml.example
CLI
ao status # Overview of all sessions
ao spawn <project> [issue] # Spawn an agent
ao send <session> "Fix the tests" # Send instructions
ao session ls # List sessions


---
*Page 5*


ao session kill <session> # Kill a session
ao session restore <session> # Revive a crashed agent
ao dashboard # Open web dashboard
Why Agent Orchestrator?
Running one AI agent in a terminal is easy. Running 30 across different issues, branches, and PRs is a
coordination problem.
Without orchestration, you manually: create branches, start agents, check if they're stuck, read CI failures,
forward review comments, track which PRs are ready to merge, clean up when done.
With Agent Orchestrator, you: and walk away. The system handles isolation, feedback routing,
ao spawn
and status tracking. You review PRs and make decisions — the rest is automated.
Prerequisites
Node.js 20+
Git 2.25+
tmux (for default runtime)
CLI (for GitHub integration)
gh
Development
pnpm install && pnpm build # Install and build all packages
pnpm test # Run tests (3,288 test cases)
pnpm dev # Start web dashboard dev server
See CLAUDE.md for code conventions and architecture details.
Documentation
Doc What it covers
Setup Guide Detailed installation and configuration
Examples Config templates (GitHub, Linear, multi-project, auto-merge)
CLAUDE.md Architecture, conventions, plugin pattern
Troubleshooting Common issues and fixes
Contributing
Contributions welcome. The plugin system makes it straightforward to add support for new agents,
runtimes, trackers, and notification channels. Every plugin is an implementation of a TypeScript interface —
see CLAUDE.md for the pattern.


---
*Page 6*


Releases 3
Project Metrics & Evolution Report — Feb 20, 2026 Latest
yesterday
+ 2 releases
Packages
No packages published
Contributors 2
AgentWrapperprateek
claudeClaude
Languages
TypeScript89.1% Shell10.0% Other0.9%