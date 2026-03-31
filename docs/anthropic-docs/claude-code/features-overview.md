---
source: https://code.claude.com/docs/en/features-overview
scraped: 2026-03-23
section: claude-code
---

# Extend Claude Code

> Understand when to use CLAUDE.md, Skills, subagents, hooks, MCP, and plugins.

Claude Code combines a model that reasons about your code with built-in tools for file operations, search, execution, and web access. The built-in tools cover most coding tasks. This guide covers the extension layer: features you add to customize what Claude knows, connect it to external services, and automate workflows.

**New to Claude Code?** Start with CLAUDE.md for project conventions. Add other extensions as you need them.

## Overview

Extensions plug into different parts of the agentic loop:

- **CLAUDE.md** adds persistent context Claude sees every session
- **Skills** add reusable knowledge and invocable workflows
- **MCP** connects Claude to external services and tools
- **Subagents** run their own loops in isolated context, returning summaries
- **Agent teams** coordinate multiple independent sessions with shared tasks and peer-to-peer messaging
- **Hooks** run outside the loop entirely as deterministic scripts
- **Plugins** and **marketplaces** package and distribute these features

Skills are the most flexible extension. A skill is a markdown file containing knowledge, workflows, or instructions. You can invoke skills with a command like `/deploy`, or Claude can load them automatically when relevant.

## Match features to your goal

| Feature | What it does | When to use it | Example |
|---|---|---|---|
| **CLAUDE.md** | Persistent context loaded every conversation | Project conventions, "always do X" rules | "Use pnpm, not npm. Run tests before committing." |
| **Skill** | Instructions, knowledge, and workflows Claude can use | Reusable content, reference docs, repeatable tasks | `/deploy` runs your deployment checklist |
| **Subagent** | Isolated execution context that returns summarized results | Context isolation, parallel tasks, specialized workers | Research task that reads many files but returns only key findings |
| **Agent teams** | Coordinate multiple independent Claude Code sessions | Parallel research, new feature development, debugging with competing hypotheses | Spawn reviewers to check security, performance, and tests simultaneously |
| **MCP** | Connect to external services | External data or actions | Query your database, post to Slack, control a browser |
| **Hook** | Deterministic script that runs on events | Predictable automation, no LLM involved | Run ESLint after every file edit |

**Plugins** are the packaging layer. A plugin bundles skills, hooks, subagents, and MCP servers into a single installable unit.

### Compare similar features

#### Skill vs Subagent

- **Skills** are reusable content you can load into any context
- **Subagents** are isolated workers that run separately from your main conversation

| Aspect | Skill | Subagent |
|---|---|---|
| **What it is** | Reusable instructions, knowledge, or workflows | Isolated worker with its own context |
| **Key benefit** | Share content across contexts | Context isolation. Work happens separately, only summary returns |
| **Best for** | Reference material, invocable workflows | Tasks that read many files, parallel work, specialized workers |

#### CLAUDE.md vs Skill

| Aspect | CLAUDE.md | Skill |
|---|---|---|
| **Loads** | Every session, automatically | On demand |
| **Can include files** | Yes, with `@path` imports | Yes, with `@path` imports |
| **Can trigger workflows** | No | Yes, with `/<name>` |
| **Best for** | "Always do X" rules | Reference material, invocable workflows |

**Put it in CLAUDE.md** if Claude should always know it: coding conventions, build commands, project structure.

**Put it in a skill** if it's reference material Claude needs sometimes or a workflow you trigger with `/<name>`.

**Rule of thumb:** Keep CLAUDE.md under 200 lines. If it's growing, move reference content to skills or split into `.claude/rules/` files.

#### CLAUDE.md vs Rules vs Skills

| Aspect | CLAUDE.md | `.claude/rules/` | Skill |
|---|---|---|---|
| **Loads** | Every session | Every session, or when matching files are opened | On demand, when invoked or relevant |
| **Scope** | Whole project | Can be scoped to file paths | Task-specific |
| **Best for** | Core conventions and build commands | Language-specific or directory-specific guidelines | Reference material, repeatable workflows |

#### Subagent vs Agent team

| Aspect | Subagent | Agent team |
|---|---|---|
| **Context** | Own context window; results return to the caller | Own context window; fully independent |
| **Communication** | Reports results back to the main agent only | Teammates message each other directly |
| **Coordination** | Main agent manages all work | Shared task list with self-coordination |
| **Best for** | Focused tasks where only the result matters | Complex work requiring discussion and collaboration |
| **Token cost** | Lower: results summarized back to main context | Higher: each teammate is a separate Claude instance |

#### MCP vs Skill

| Aspect | MCP | Skill |
|---|---|---|
| **What it is** | Protocol for connecting to external services | Knowledge, workflows, and reference material |
| **Provides** | Tools and data access | Knowledge, workflows, reference material |

MCP gives Claude the ability to interact with external systems. Skills give Claude knowledge about how to use those tools effectively.

## Understand how features layer

- **CLAUDE.md files** are additive: all levels contribute content simultaneously
- **Skills and subagents** override by name when the same name exists at multiple levels
- **MCP servers** override by name: local > project > user
- **Hooks** merge: all registered hooks fire for their matching events regardless of source

## Combine features

| Pattern | How it works | Example |
|---|---|---|
| **Skill + MCP** | MCP provides the connection; a skill teaches Claude how to use it well | MCP connects to your database, a skill documents your schema and query patterns |
| **Skill + Subagent** | A skill spawns subagents for parallel work | `/audit` skill kicks off security, performance, and style subagents |
| **CLAUDE.md + Skills** | CLAUDE.md holds always-on rules; skills hold reference material loaded on demand | CLAUDE.md says "follow our API conventions," a skill contains the full API style guide |
| **Hook + MCP** | A hook triggers external actions through MCP | Post-edit hook sends a Slack notification when Claude modifies critical files |

## Understand context costs

| Feature | When it loads | What loads | Context cost |
|---|---|---|---|
| **CLAUDE.md** | Session start | Full content | Every request |
| **Skills** | Session start + when used | Descriptions at start, full content when used | Low (descriptions every request) |
| **MCP servers** | Session start | All tool definitions and schemas | Every request |
| **Subagents** | When spawned | Fresh context with specified skills | Isolated from main session |
| **Hooks** | On trigger | Nothing (runs externally) | Zero, unless hook returns additional context |

Set `disable-model-invocation: true` in a skill's frontmatter to hide it from Claude entirely until you invoke it manually. This reduces context cost to zero for skills you only trigger yourself.

### CLAUDE.md loading

**When:** Session start

**What loads:** Full content of all CLAUDE.md files (managed, user, and project levels).

Keep CLAUDE.md under ~500 lines. Move reference material to skills, which load on-demand.

### Skills loading

Skills load descriptions at session start so Claude can decide when to use them. When you invoke a skill with `/<name>` or Claude loads it automatically, the full content loads into your conversation.

Use `disable-model-invocation: true` for skills with side effects. This saves context and ensures only you trigger them.

### MCP servers loading

Tool search (enabled by default) loads MCP tools up to 10% of context and defers the rest until needed.

Run `/mcp` to see token costs per server. Disconnect servers you're not actively using.

### Subagents loading

Fresh, isolated context containing:
- The system prompt
- Full content of skills listed in the agent's `skills:` field
- CLAUDE.md and git status
- Whatever context the lead agent passes in the prompt

Subagents don't inherit your conversation history or invoked skills.

### Hooks loading

Hooks run as external scripts. Context cost is zero unless the hook returns output that gets added as messages to your conversation.

## Learn more

- **CLAUDE.md**: Store project context, conventions, and instructions
- **Skills**: Give Claude domain expertise and reusable workflows
- **Subagents**: Offload work to isolated context
- **Agent teams**: Coordinate multiple sessions working in parallel
- **MCP**: Connect Claude to external services
- **Hooks**: Automate workflows with hooks
- **Plugins**: Bundle and share feature sets
- **Marketplaces**: Host and distribute plugin collections
