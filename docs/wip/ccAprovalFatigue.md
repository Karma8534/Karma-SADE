# ccAprovalFatigue

*Converted from: ccAprovalFatigue.pdf*



---
*Page 1*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
Spillwave Solutions
Mastering Agent Skills in Claude Code 2.1: Escape Approval Fatigue with a Pre-Authorized Agent
Stop Clicking “Approve”: How I
Killed Approval Fatigue with Claude
Code 2.1
Rick Hightower Following 7 min read · Feb 5, 2026
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 1/18


---
*Page 2*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
94
Mastering Agent Skills in Claude Code 2.1: Escape Approval Fatigue with a Pre-
Authorized Agent
To combat approval fatigue in Python workflows, create or fork a skill locally,
create a pre-authorized agent with necessary permissions, and bind the skill to this
agent. This setup allows for seamless execution of commands without constant
approval prompts, enhancing productivity while maintaining governance and
security. The approach emphasizes defining a clear permission boundary for
trusted local development environments.
If you’ve ever tried to run a tight Python workflow inside Claude Code —
tests, lint, format, type-check, build — you’ve probably hit the same wall:
approval fatigue.
You’re not “doing engineering” anymore. You’re playing whack-a-mole with
prompts.
Claude: Running `pytest -v`...
[Approve? y/n]
Claude: Running `ruff check .`...
[Approve? y/n]
Claude: Running `poetry install`...
[Approve? y/n]
Claude is being safe. But your momentum is getting shredded.
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 2/18


---
*Page 3*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
This article shows the pattern we shipped to fix it: fork the skill locally, bind
it to a pre-authorized agent, and eliminate the “May I?” loop — without
turning off safety entirely.
The Core Idea
You want Claude Code to stop negotiating permissions one command at a
time.
Instead, you declare a governed permission boundary up front — an agent
definition that says:
“For Python work, these tools are allowed.”
Then you wire your skill to that agent, so your workflow runs smoothly.
Think of it like this:
Skill = the reusable automation + docs
Agent = the permission boundary (what’s allowed)
Binding = the glue that makes the skill run under that boundary
The “Fork + Pre-Authorized Agent” Pattern
Here’s the minimal architecture:
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 3/18


---
*Page 4*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
.claude/
├── agents/
│ └── senior-python-engineer.md
└── skills/
└── mastering-python-skill/
├── SKILL.md
├── references/
└── sample-cli/
You’re doing three things:
Fork the mastering python skill into the project (so you can customize it
safely)
Create a “senior-python-engineer” agent with comprehensive allowed
tools
Bind the skill to that agent so commands run without constant approvals
Step 1: Install a Local Copy of the Skill
Use skilz to install into the project instead of global:
skilz install \
https://github.com/SpillwaveSolutions/mastering-python-skill-plugin \
-p --agent claude
What the flags mean:
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 4/18


---
*Page 5*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
-p / — project → installs to .claude/skills/ in this repo (your fork)
— agent claude → emits the Claude Code agent format
Result: you now have a local fork at:
.claude/skills/mastering-python-skill/
That’s the whole point: you can now customize it without touching
upstream.
Step 2: Create a Pre-Authorized Python Agent
Create:
.claude/agents/senior-python-engineer.md
And give it the permission surface that kills the fatigue — especially for
Python tooling:
---
name: senior-python-engineer
description: Senior Python engineer agent with full permissions for Python workflows
allowed_tools:
# File operations
- "Read"
- "Edit"
- "Write"
- "Glob"
- "Grep"
# Python development
- "Bash(python*)"
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 5/18


---
*Page 6*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
- "Bash(pytest*)"
- "Bash(poetry*)"
- "Bash(ruff*)"
- "Bash(mypy*)"
- "Bash(black*)"
- "Bash(uv*)"
- "Bash(pip*)"
- "Bash(pipx*)"
- "Bash(conda*)"
---
In your real setup, this grows into a broader “dev workstation” profile (often
hundreds of patterns). The trick is: declare it once, then stop getting
interrupted forever.
Step 3: Bind the Skill to the Agent
 
Open your forked skill:
.claude/skills/mastering-python-skill/SKILL.md
Add the binding:
---
name: mastering-python-skill
description: Modern Python coaching...
context: fork
agent: senior-python-engineer
allowed-tools:
- Read
- Write
- Bash
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 6/18


---
*Page 7*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
- Edit
---
That agent: senior-python-engineer line is the entire unlock.
It tells Claude Code:
“When this skill runs, use the pre-approved tool permissions from that
agent.”
What Actually Happens at Runtime
When you invoke /mastering-python-skill (or Claude triggers it based on
keywords):
Claude loads the skill from .claude/skills/mastering-python-
skill/SKILL.md
It sees agent: senior-python-engineer
Claude loads .claude/agents/senior-python-engineer.md
Everything in allowed_tools becomes pre-authorized for the session
Now your workflow runs like it always should have:
Claude: Let me validate the code...
> pytest -v ✓
> mypy src/ ✓
> ruff format . ✓
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 7/18


---
*Page 8*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
> ruff check . ✓
All checks passed!
No more “Approve? y/n” every 12 seconds.
Permission Categories That Matter
In practice, the “senior python” agent tends to include:
File operations → Read/Edit/Write/Glob/Grep
Python tooling → python/pip/uv/poetry/pytest/ruff/mypy/black/coverage
Servers → uvicorn/gunicorn/fastapi
Git → status/add/commit/push
Task runners → task/make/invoke/just
Shell basics → ls/mkdir/rm/curl/jq
If you keep adding tools because Claude keeps asking, that’s normal early
on. You’re “teaching” the agent what a real workflow needs. Keep updating
your agent with the access it needs. I often have a second Claude code CLI
running and as I see or deal with prompts, I keep prompting the second one
to edit the agent so I never see that prompt again.
Referenced Skills Inside the Agent
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 8/18


---
*Page 9*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
In our setup, the agent can also reference other skills to stay “senior” across
domains:
mastering-python-skill → modern Python patterns, typing, pytest,
FastAPI, packaging
developing-llamaindex-systems → production RAG, hybrid retrieval,
graph + vector systems
taskfile → Task (Go task runner) best practices and structure
Security Reality Check
Yes — this approach is intentionally broad. That’s the point: reduce friction
for trusted local dev workflows. Try to scope it to your project directory.
Use it when:
it’s your machine
it’s your repo
you trust the codebase
If you’re in a shared environment or running risky automation, tighten the
patterns:
scope deletes to specific paths ( rm -rf ~/.cache/uv*)
narrow git commands (no force push patterns)
keep “destructive” workflows in separate agents
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 9/18


---
*Page 10*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
The goal isn’t “maximum permission.” It’s right-sized permission with zero
interruptions.
Never resort to yolo mode ` — danger-will-robinsonmode`. Strike a balance
that you are comfortable with. I know people who have done dangerously
mode and wiped out their OS. It happens. I cringe when I see people do it. I
don’t.
For CLAUDE.md/AGENTS.md: (both root and .claude/):
## Python Development Skill
When working on Python code in this repository, use the `/mastering-python-skill`
skill which provides:
- Pre-authorized bash commands (no approval fatigue)
- Modern Python best practices and patterns
- Type hints, async, pytest, FastAPI guidance
The skill is bound to the `senior-python-engineer`
agent (`.claude/agents/senior-python-engineer.md`)
which has 300+ pre-authorized tools for seamless Python development.
Invoke with: /mastering-python-skill
 
You can even put clues into AGENTS.md and CLAUDE.md into subfolders.
Here I will put them in a Python test directory to remind them how I want
the agent skill used.
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 10/18


---
*Page 11*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
% pwd
~/src/agent-brain/agent-brain-cli/tests
% ls
AGENTS.md CLAUDE.md
Since this is the test folder, I can get real specific:
# Test Directory Guidelines for Claude Code
This directory contains tests for agent-brain-cli.
Use the `/mastering-python-skill` skill for Python testing best practices.
## Required Skill
**Invoke:** `/mastering-python-skill`
This skill is bound to the `senior-python-engineer` agent
with pre-authorized tools (no approval fatigue).
## Specific References for Testing
When writing or modifying tests in this directory, refer to these skill
references:
| Reference | Use For | Path |
|-----------|---------|------|
| **pytest-essentials.md** | Fixtures, parametrize, markers, conftest patterns | `ma
| **mocking-strategies.md** | unittest.mock, pytest-mock, MagicMock, patching | `mas
| **property-testing.md** | Hypothesis, property-based testing, strategies | `master
## When to Use Each Reference
### pytest-essentials.md
- Writing new test files
- Creating fixtures in `conftest.py`
- Using `@pytest.mark.parametrize` for test variations
- Test organization and naming conventions
- Testing Click CLI commands with `CliRunner`
### mocking-strategies.md
- Mocking HTTP client calls to the server
- Patching `httpx` or `requests` responses
- Using `MagicMock` for API client testing
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 11/18


---
*Page 12*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
- Testing error handling with mocked failures
### property-testing.md
- Testing CLI argument parsing with random inputs
- Verifying command behavior across input variations
- Using Hypothesis strategies for string inputs
## Test Commands
```bash
# Run all tests
poetry run pytest
# Run with coverage
poetry run pytest --cov=agent_brain_cli --cov-report=term-missing
# Run specific test file
poetry run pytest tests/test_commands.py -v
# Run with verbose output
poetry run pytest -v --tb=short
```
## CLI Testing Pattern
from click.testing import CliRunner
from agent_brain_cli.cli import cli
def test_status_command():
runner = CliRunner()
result = runner.invoke(cli, ['status'])
assert result.exit_code == 0
Quality Standards
Before committing test changes:
[ ] All tests pass (poetry run pytest)
[ ] Coverage >= 50% for new code
[ ] HTTP calls are properly mocked
[ ] CLI commands tested with CliRunner
The Takeaway
Here’s the pattern in plain English:
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 12/18


---
*Page 13*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
Fork the skill locally so it’s yours
Define a real “Python engineer” agent with the tools you actually use
Bind the skill to the agent so Claude runs workflows without constant
approvals
Keep the manifest so you can track upstream cleanly
That’s how you go from Approval Hell to Just Do It — while keeping
governance explicit and auditable.
About the Author
Rick Hightower is a technology executive and data engineer who led ML/AI
development at a Fortune 100 financial services company. He created skilz,
the universal agent skill installer, supporting 30+ coding agents including
Claude Code, Gemini, Copilot, and Cursor, and co-founded the world’s
largest agentic skill marketplace. Connect with Rick Hightower on LinkedIn
or Medium.
The Claude Code community has developed powerful extensions that
enhance its capabilities. Here are some valuable resources from Spillwave
Solutions (Spillwave Solutions Home Page):
If you like this article, check out these other articles by this author (me):
Agent Brain: Giving AI Coding Agents a Full Understanding of Your
Entire Enterprise — Feb 5th 2026
Build Agent Skills Faster with Claude Code 2.1 Release — Feb 4th 2026
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 13/18


---
*Page 14*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
Build Your First Agent Skill in 10 Minutes Using the Context7 Wizard (and
Save Hours) — Feb 1st 2026
Supercharge Your React Performance with Vercel’s Best Practices Agent
Skill — Jan 29th
Agent Skills: The Universal Standard Transforming How AI Agents Work
— Jan 28
Agent-Browser: AI-First Browser Automation That Saves 93% of Your
Context Window — Jan 27
Claude Code: Todos to Tasks — Jan 26
LangExtract: Multi-Provider NLP Extraction with Gemini, OpenAI,
Claude, and Local Models — Jan 20
Empowering AI Coding Agents with Private Knowledge: The Doc-Serve
Agent Skill — Jan 20
Give Your Claude Code, OpenCode, and Codex Full RAG Over Docs and
Code Repos — Jan 18
Claude Code Agent Skills Agentic Ai
Published in Spillwave Solutions
Follow
221 followers · Last published Mar 12, 2026
Perspectives from technology experience. Leadership thoughts for Cxx suite.
Technology guidance for every level below that. Visit https://spillwave.com/ to
learn more.
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 14/18


---
*Page 15*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
Written by Rick Hightower
Following
2K followers · 55 following
2026 Agent Reliability Playbook – Free Download DM me 'PLAYBOOK' for the full
version + personalized 15-minute audit of your current agent setup (no pitch).
No responses yet
Open in app
Search Write
Rae Steele
What are your thoughts?
More from Rick Hightower and Spillwave Solutions
Rick Hightower InSpillwave Solutionsby Rick Hightower
Mastering Claude Code’s /btw, Claude Code Skills Deep Dive Part 1
/fork, and /rewind: The Context…
Part 1 of 2: Foundations and Concepts
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 15/18


---
*Page 16*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
Claude Code’s /btw, /fork, and /rewind
commands to eliminate context pollution
Dec 9, 2025 144 2
6d ago 120
InSpillwave Solutionsby Rick Hightower Rick Hightower
Claude Code Skills Deep Dive Part 2 The Agent Framework Landscape:
LangChain Deep Agents vs. Claud…
Part 2 of 2: Deep Dive and Implementation
Comparing Architectures and Capabilities of
Leading AI Agent Frameworks
Dec 9, 2025 146 1 4d ago 35 1
See all from Rick Hightower See all from Spillwave Solutions
Recommended from Medium
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 16/18


---
*Page 17*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
Reza Rezvani InSpillwave Solutionsby Rick Hightower
Claude Code /loop — Here Are 3 Build Your First Agent Skill in 10
Autonomous Loops For My Daily… Minutes Using the Context7 Wizar…
Context7 Skills: Generate Agent Skills From
Live Documentation
Mar 9 97 3 Feb 2 149 1
InTowards AIby Faisal haque Joe Njenga
OpenAI Just Declared War on 12 Little-Known Claude Code
Claude Code: Inside the Codex Ap… Commands That Make You a Whiz
Why the $1B elephant in the room just got a What if I told you there are some Claude Code
macOS-native competitor that treats AI agen… commands that, although not very popular,…
Feb 4 219 5 Sep 21, 2025 377 6
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 17/18


---
*Page 18*


3/23/26, 12:07 PM Stop Clicking “Approve”: How I Killed Approval Fatigue with Claude Code 2.1 | by Rick Hightower | Feb, 2026 | Spillwave Solutions
David R Oliver Reza Rezvani
ArcKit — AI Toolkit for Solution & AI Agent Skills at Scale: What
Enterprise Architects Building 170 Skills Across 9…
These AI-based Architectural tools are used The AI skills ecosystem is converging in
across the UK Government and the NHS. theory and fragmenting in practice. A practic…
Feb 23 100 2 Mar 13 32 3
See more recommendations
https://medium.com/spillwave-solutions/stop-clicking-approve-how-i-killed-approval-fatigue-with-claude-code-2-1-60962946d101 18/18