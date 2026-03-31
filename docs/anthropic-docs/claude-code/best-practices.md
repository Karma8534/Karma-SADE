---
source: https://code.claude.com/docs/en/best-practices
scraped: 2026-03-23
section: claude-code
---

# Best Practices for Claude Code

> Tips and patterns for getting the most out of Claude Code, from configuring your environment to scaling across parallel sessions.

Claude Code is an agentic coding environment. Unlike a chatbot that answers questions and waits, Claude Code can read your files, run commands, make changes, and autonomously work through problems.

Most best practices are based on one constraint: **Claude's context window fills up fast, and performance degrades as it fills.**

Track context usage continuously with a custom status line, and see Reduce token usage for strategies on reducing token usage.

## Give Claude a way to verify its work

Include tests, screenshots, or expected outputs so Claude can check itself. This is the single highest-leverage thing you can do.

| Strategy | Before | After |
|---|---|---|
| **Provide verification criteria** | *"implement a function that validates email addresses"* | *"write a validateEmail function. example test cases: user@example.com is true, invalid is false, user@.com is false. run the tests after implementing"* |
| **Verify UI changes visually** | *"make the dashboard look better"* | *"\[paste screenshot] implement this design. take a screenshot of the result and compare it to the original. list differences and fix them"* |
| **Address root causes, not symptoms** | *"the build is failing"* | *"the build fails with this error: \[paste error]. fix it and verify the build succeeds. address the root cause, don't suppress the error"* |

UI changes can be verified using the Claude in Chrome extension.

## Explore first, then plan, then code

Separate research and planning from implementation to avoid solving the wrong problem. Use Plan Mode to separate exploration from execution.

### The recommended workflow

**Step 1: Explore** — Enter Plan Mode. Claude reads files and answers questions without making changes.

```text
read /src/auth and understand how we handle sessions and login.
also look at how we manage environment variables for secrets.
```

**Step 2: Plan** — Ask Claude to create a detailed implementation plan.

```text
I want to add Google OAuth. What files need to change?
What's the session flow? Create a plan.
```

Press `Ctrl+G` to open the plan in your text editor for direct editing before Claude proceeds.

**Step 3: Implement** — Switch back to Normal Mode and let Claude code.

```text
implement the OAuth flow from your plan. write tests for the
callback handler, run the test suite and fix any failures.
```

**Step 4: Commit** — Ask Claude to commit with a descriptive message and create a PR.

```text
commit with a descriptive message and open a PR
```

Planning is most useful when you're uncertain about the approach, when the change modifies multiple files, or when you're unfamiliar with the code being modified.

## Provide specific context in your prompts

| Strategy | Before | After |
|---|---|---|
| **Scope the task** | *"add tests for foo.py"* | *"write a test for foo.py covering the edge case where the user is logged out. avoid mocks."* |
| **Point to sources** | *"why does ExecutionFactory have such a weird api?"* | *"look through ExecutionFactory's git history and summarize how its api came to be"* |
| **Reference existing patterns** | *"add a calendar widget"* | *"look at how existing widgets are implemented on the home page to understand the patterns. HotDogWidget.php is a good example. follow the pattern to implement a new calendar widget..."* |
| **Describe the symptom** | *"fix the login bug"* | *"users report that login fails after session timeout. check the auth flow in src/auth/, especially token refresh. write a failing test that reproduces the issue, then fix it"* |

### Provide rich content

- **Reference files with `@`** instead of describing where code lives
- **Paste images directly** — copy/paste or drag and drop images into the prompt
- **Give URLs** for documentation and API references
- **Pipe in data** by running `cat error.log | claude`
- **Let Claude fetch what it needs** — tell Claude to pull context itself

## Configure your environment

### Write an effective CLAUDE.md

Run `/init` to generate a starter CLAUDE.md file based on your current project structure, then refine over time.

```markdown
# Code style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')

# Workflow
- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
```

CLAUDE.md is loaded every session, so only include things that apply broadly.

| Include | Exclude |
|---|---|
| Bash commands Claude can't guess | Anything Claude can figure out by reading code |
| Code style rules that differ from defaults | Standard language conventions Claude already knows |
| Testing instructions and preferred test runners | Detailed API documentation (link to docs instead) |
| Repository etiquette (branch naming, PR conventions) | Information that changes frequently |
| Architectural decisions specific to your project | Long explanations or tutorials |
| Developer environment quirks (required env vars) | File-by-file descriptions of the codebase |
| Common gotchas or non-obvious behaviors | Self-evident practices like "write clean code" |

CLAUDE.md files can import additional files:
```markdown
See @README.md for project overview and @package.json for available npm commands.

# Additional Instructions
- Git workflow: @docs/git-instructions.md
- Personal overrides: @~/.claude/my-project-instructions.md
```

CLAUDE.md can be placed in:
- **Home folder (`~/.claude/CLAUDE.md`)**: applies to all Claude sessions
- **Project root (`./CLAUDE.md`)**: check into git to share with your team
- **Parent directories**: useful for monorepos
- **Child directories**: Claude pulls in child CLAUDE.md files on demand

### Configure permissions

Use `/permissions` to allowlist safe commands or `/sandbox` for OS-level isolation. This reduces interruptions while keeping you in control.

Use `--dangerously-skip-permissions` to bypass permission prompts for contained workflows only in a sandbox without internet access.

### Use CLI tools

Tell Claude Code to use CLI tools like `gh`, `aws`, `gcloud`, and `sentry-cli` when interacting with external services. These are the most context-efficient way to interact with external services.

Claude is also effective at learning CLI tools it doesn't already know:
```text
Use 'foo-cli-tool --help' to learn about foo tool, then use it to solve A, B, C.
```

### Connect MCP servers

With MCP servers, you can ask Claude to implement features from issue trackers, query databases, analyze monitoring data, integrate designs from Figma, and automate workflows.

```bash
claude mcp add
```

### Set up hooks

Hooks run scripts automatically at specific points in Claude's workflow. Unlike CLAUDE.md instructions which are advisory, hooks are deterministic and guarantee the action happens.

Claude can write hooks for you: *"Write a hook that runs eslint after every file edit"*

### Create skills

Skills extend Claude's knowledge with information specific to your project, team, or domain:

```markdown
---
name: api-conventions
description: REST API design conventions for our services
---
# API Conventions
- Use kebab-case for URL paths
- Use camelCase for JSON properties
- Always include pagination for list endpoints
- Version APIs in the URL path (/v1/, /v2/)
```

For executable workflows:
```markdown
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---
Analyze and fix the GitHub issue: $ARGUMENTS.

1. Use `gh issue view` to get the issue details
2. Understand the problem described in the issue
3. Search the codebase for relevant files
4. Implement the necessary changes to fix the issue
5. Write and run tests to verify the fix
...
```

### Create custom subagents

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities
tools: Read, Grep, Glob, Bash
model: opus
---
You are a senior security engineer. Review code for:
- Injection vulnerabilities (SQL, XSS, command injection)
- Authentication and authorization flaws
- Secrets or credentials in code
- Insecure data handling

Provide specific line references and suggested fixes.
```

## Communicate effectively

### Ask codebase questions

Ask Claude questions you'd ask a senior engineer:
- How does logging work?
- How do I make a new API endpoint?
- What does `async move { ... }` do on line 134 of `foo.rs`?
- Why does this code call `foo()` instead of `bar()` on line 333?

### Let Claude interview you

For larger features, have Claude interview you first:

```text
I want to build [brief description]. Interview me in detail using the AskUserQuestion tool.

Ask about technical implementation, UI/UX, edge cases, concerns, and tradeoffs. Don't ask obvious questions, dig into the hard parts I might not have considered.

Keep interviewing until we've covered everything, then write a complete spec to SPEC.md.
```

## Manage your session

### Course-correct early and often

- **`Esc`**: stop Claude mid-action. Context is preserved, so you can redirect.
- **`Esc + Esc` or `/rewind`**: press `Esc` twice or run `/rewind` to open the rewind menu
- **`"Undo that"`**: have Claude revert its changes
- **`/clear`**: reset context between unrelated tasks

If you've corrected Claude more than twice on the same issue in one session, the context is cluttered with failed approaches. Run `/clear` and start fresh.

### Manage context aggressively

- Use `/clear` frequently between tasks to reset the context window entirely
- When auto compaction triggers, Claude summarizes what matters most
- For more control, run `/compact <instructions>`, like `/compact Focus on the API changes`
- To compact only part of the conversation, use `Esc + Esc` or `/rewind`, select a message checkpoint, and choose **Summarize from here**
- Customize compaction behavior in CLAUDE.md: `"When compacting, always preserve the full list of modified files and any test commands"`
- For quick questions, use `/btw` — the answer appears in a dismissible overlay and never enters conversation history

### Use subagents for investigation

```text
Use subagents to investigate how our authentication system handles token
refresh, and whether we have any existing OAuth utilities I should reuse.
```

You can also use subagents for verification:
```text
use a subagent to review this code for edge cases
```

### Rewind with checkpoints

Every action Claude makes creates a checkpoint. Double-tap `Escape` or run `/rewind` to open the rewind menu. You can restore conversation only, restore code only, restore both, or summarize from a selected message.

### Resume conversations

```bash
claude --continue    # Resume the most recent conversation
claude --resume      # Select from recent conversations
```

## Automate and scale

### Run non-interactive mode

```bash
# One-off queries
claude -p "Explain what this project does"

# Structured output for scripts
claude -p "List all API endpoints" --output-format json

# Streaming for real-time processing
claude -p "Analyze this log file" --output-format stream-json
```

### Run multiple Claude sessions

- **Claude Code desktop app**: Manage multiple local sessions visually
- **Claude Code on the web**: Run on Anthropic's secure cloud infrastructure
- **Agent teams**: Automated coordination of multiple sessions with shared tasks

Writer/Reviewer pattern:
```
Session A: Implement a rate limiter for our API endpoints
Session B: Review the rate limiter implementation in @src/middleware/rateLimiter.ts
Session A: Address the review feedback
```

### Fan out across files

```bash
for file in $(cat files.txt); do
  claude -p "Migrate $file from React to Vue. Return OK or FAIL." \
    --allowedTools "Edit,Bash(git commit *)"
done
```

## Avoid common failure patterns

- **The kitchen sink session.** `/clear` between unrelated tasks.
- **Correcting over and over.** After two failed corrections, `/clear` and write a better initial prompt.
- **The over-specified CLAUDE.md.** Ruthlessly prune. If Claude already does something correctly without the instruction, delete it.
- **The trust-then-verify gap.** Always provide verification (tests, scripts, screenshots).
- **The infinite exploration.** Scope investigations narrowly or use subagents.

## Related resources

- How Claude Code works: the agentic loop, tools, and context management
- Extend Claude Code: skills, hooks, MCP, subagents, and plugins
- Common workflows: step-by-step recipes for debugging, testing, PRs, and more
- CLAUDE.md: store project conventions and persistent context
