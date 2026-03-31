---
source: https://code.claude.com/docs/en/skills
scraped: 2026-03-23
section: claude-code
---

# Extend Claude with skills

> Create, manage, and share skills to extend Claude's capabilities in Claude Code. Includes custom commands and bundled skills.

Skills extend what Claude can do. Create a `SKILL.md` file with instructions, and Claude adds it to its toolkit. Claude uses skills when relevant, or you can invoke one directly with `/skill-name`.

Claude Code skills follow the [Agent Skills](https://agentskills.io) open standard. Custom commands have been merged into skills — a file at `.claude/commands/deploy.md` and a skill at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way.

## Bundled skills

Bundled skills ship with Claude Code and are available in every session:

| Skill | Purpose |
|---|---|
| `/batch <instruction>` | Orchestrate large-scale changes across a codebase in parallel. Researches the codebase, decomposes the work into 5 to 30 independent units, and presents a plan. Once approved, spawns one background agent per unit. |
| `/claude-api` | Load Claude API reference material for your project's language. Also activates automatically when your code imports `anthropic`, `@anthropic-ai/sdk`, or `claude_agent_sdk`. |
| `/debug [description]` | Troubleshoot your current Claude Code session by reading the session debug log. |
| `/loop [interval] <prompt>` | Run a prompt repeatedly on an interval while the session stays open. |
| `/simplify [focus]` | Review your recently changed files for code reuse, quality, and efficiency issues, then fix them. Spawns three review agents in parallel. |

## Getting started

### Create your first skill

```bash
mkdir -p ~/.claude/skills/explain-code
```

Create `~/.claude/skills/explain-code/SKILL.md`:

```yaml
---
name: explain-code
description: Explains code with visual diagrams and analogies. Use when explaining how code works, teaching about a codebase, or when the user asks "how does this work?"
---

When explaining code, always include:

1. **Start with an analogy**: Compare the code to something from everyday life
2. **Draw a diagram**: Use ASCII art to show the flow, structure, or relationships
3. **Walk through the code**: Explain step-by-step what happens
4. **Highlight a gotcha**: What's a common mistake or misconception?

Keep explanations conversational. For complex concepts, use multiple analogies.
```

Test it two ways:
- Let Claude invoke it automatically by asking something that matches the description
- Or invoke it directly with `/explain-code src/auth/login.ts`

### Where skills live

| Location | Path | Applies to |
|---|---|---|
| Enterprise | See managed settings | All users in your organization |
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<skill-name>/SKILL.md` | This project only |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Where plugin is enabled |

When skills share the same name across levels, higher-priority locations win: enterprise > personal > project.

Each skill is a directory with `SKILL.md` as the entrypoint:

```text
my-skill/
├── SKILL.md           # Main instructions (required)
├── template.md        # Template for Claude to fill in
├── examples/
│   └── sample.md      # Example output showing expected format
└── scripts/
    └── validate.sh    # Script Claude can execute
```

## Configure skills

### Types of skill content

**Reference content** adds knowledge Claude applies to your current work:
```yaml
---
name: api-conventions
description: API design patterns for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

**Task content** gives Claude step-by-step instructions for a specific action:
```yaml
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

### Frontmatter reference

| Field | Required | Description |
|---|---|---|
| `name` | No | Display name for the skill. If omitted, uses the directory name. |
| `description` | Recommended | What the skill does and when to use it. |
| `argument-hint` | No | Hint shown during autocomplete to indicate expected arguments. |
| `disable-model-invocation` | No | Set to `true` to prevent Claude from automatically loading this skill. |
| `user-invocable` | No | Set to `false` to hide from the `/` menu. |
| `allowed-tools` | No | Tools Claude can use without asking permission when this skill is active. |
| `model` | No | Model to use when this skill is active. |
| `effort` | No | Effort level when this skill is active. |
| `context` | No | Set to `fork` to run in a forked subagent context. |
| `agent` | No | Which subagent type to use when `context: fork` is set. |
| `hooks` | No | Hooks scoped to this skill's lifecycle. |

#### Available string substitutions

| Variable | Description |
|---|---|
| `$ARGUMENTS` | All arguments passed when invoking the skill. |
| `$ARGUMENTS[N]` | Access a specific argument by 0-based index. |
| `$N` | Shorthand for `$ARGUMENTS[N]`. |
| `${CLAUDE_SESSION_ID}` | The current session ID. |
| `${CLAUDE_SKILL_DIR}` | The directory containing the skill's `SKILL.md` file. |

### Add supporting files

```text
my-skill/
├── SKILL.md (required - overview and navigation)
├── reference.md (detailed API docs - loaded when needed)
├── examples.md (usage examples - loaded when needed)
└── scripts/
    └── helper.py (utility script - executed, not loaded)
```

Reference supporting files from `SKILL.md`:
```markdown
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files.

### Control who invokes a skill

By default, both you and Claude can invoke any skill.

- **`disable-model-invocation: true`**: Only you can invoke the skill. Use for workflows with side effects like `/commit`, `/deploy`, or `/send-slack-message`.
- **`user-invocable: false`**: Only Claude can invoke the skill. Use for background knowledge that isn't actionable as a command.

| Frontmatter | You can invoke | Claude can invoke | When loaded into context |
|---|---|---|---|
| (default) | Yes | Yes | Description always in context, full skill loads when invoked |
| `disable-model-invocation: true` | Yes | No | Description not in context, full skill loads when you invoke |
| `user-invocable: false` | No | Yes | Description always in context, full skill loads when invoked |

### Restrict tool access

```yaml
---
name: safe-reader
description: Read files without making changes
allowed-tools: Read, Grep, Glob
---
```

### Pass arguments to skills

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

When you run `/fix-issue 123`, Claude receives "Fix GitHub issue 123 following our coding standards..."

Using positional arguments:
```yaml
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```

Running `/migrate-component SearchBar React Vue` replaces `$0` with `SearchBar`, `$1` with `React`, `$2` with `Vue`.

## Advanced patterns

### Inject dynamic context

The `` !`<command>` `` syntax runs shell commands before the skill content is sent to Claude:

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

When this skill runs:
1. Each `` !`<command>` `` executes immediately
2. The output replaces the placeholder in the skill content
3. Claude receives the fully-rendered prompt with actual data

### Run skills in a subagent

Add `context: fork` to your frontmatter when you want a skill to run in isolation:

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

### Restrict Claude's skill access

**Disable all skills** by denying the Skill tool in `/permissions`:
```text
# Add to deny rules:
Skill
```

**Allow or deny specific skills** using permission rules:
```text
# Allow only specific skills
Skill(commit)
Skill(review-pr *)

# Deny specific skills
Skill(deploy *)
```

## Troubleshooting

### Skill not triggering

1. Check the description includes keywords users would naturally say
2. Verify the skill appears in `What skills are available?`
3. Try rephrasing your request to match the description
4. Invoke it directly with `/skill-name` if the skill is user-invocable

### Skill triggers too often

1. Make the description more specific
2. Add `disable-model-invocation: true` if you only want manual invocation

### Claude doesn't see all my skills

Skill descriptions are loaded into context. If you have many skills, they may exceed the character budget. Run `/context` to check for a warning about excluded skills.

To override the limit, set the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable.

## Related resources

- **Subagents**: delegate tasks to specialized agents
- **Plugins**: package and distribute skills with other extensions
- **Hooks**: automate workflows around tool events
- **Memory**: manage CLAUDE.md files for persistent context
- **Built-in commands**: reference for built-in `/` commands
- **Permissions**: control tool and skill access
