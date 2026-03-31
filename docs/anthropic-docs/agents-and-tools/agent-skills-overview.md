---
source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
scraped: 2026-03-23
section: agents-and-tools
---

# Agent Skills

Agent Skills are modular capabilities that extend Claude's functionality. Each Skill packages instructions, metadata, and optional resources (scripts, templates) that Claude uses automatically when relevant.

## Why use Skills

Skills are reusable, filesystem-based resources that provide Claude with domain-specific expertise: workflows, context, and best practices that transform general-purpose agents into specialists. Unlike prompts (conversation-level instructions for one-off tasks), Skills load on-demand and eliminate the need to repeatedly provide the same guidance across multiple conversations.

**Key benefits**:
- **Specialize Claude**: Tailor capabilities for domain-specific tasks
- **Reduce repetition**: Create once, use automatically
- **Compose capabilities**: Combine Skills to build complex workflows

## Using Skills

Anthropic provides pre-built Agent Skills for common document tasks (PowerPoint, Excel, Word, PDF), and you can create your own custom Skills. Both work the same way. Claude automatically uses them when relevant to your request.

**Pre-built Agent Skills** are available to all users on claude.ai and via the Claude API.

**Custom Skills** let you package domain expertise and organizational knowledge. They're available across Claude's products: create them in Claude Code, upload them via the API, or add them in claude.ai settings.

## How Skills work

Skills leverage Claude's VM environment to provide capabilities beyond what's possible with prompts alone. Claude operates in a virtual machine with filesystem access, allowing Skills to exist as directories containing instructions, executable code, and reference materials.

This filesystem-based architecture enables **progressive disclosure**: Claude loads information in stages as needed, rather than consuming context upfront.

### Three types of Skill content, three levels of loading

#### Level 1: Metadata (always loaded)

The Skill's YAML frontmatter provides discovery information:

```yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---
```

Claude loads this metadata at startup. This lightweight approach means you can install many Skills without context penalty.

#### Level 2: Instructions (loaded when triggered)

The main body of SKILL.md contains procedural knowledge: workflows, best practices, and guidance. When you request something that matches a Skill's description, Claude reads SKILL.md from the filesystem.

#### Level 3: Resources and code (loaded as needed)

Skills can bundle additional materials:

```text
pdf-skill/
├── SKILL.md (main instructions)
├── FORMS.md (form-filling guide)
├── REFERENCE.md (detailed API reference)
└── scripts/
    └── fill_form.py (utility script)
```

Claude accesses these files only when referenced.

| Level | When Loaded | Token Cost | Content |
|-------|------------|------------|---------|
| **Level 1: Metadata** | Always (at startup) | ~100 tokens per Skill | `name` and `description` from YAML frontmatter |
| **Level 2: Instructions** | When Skill is triggered | Under 5k tokens | SKILL.md body with instructions and guidance |
| **Level 3+: Resources** | As needed | Effectively unlimited | Bundled files executed via bash without loading contents into context |

## Where Skills work

### Claude API

The Claude API supports both pre-built Agent Skills and custom Skills. Specify the relevant `skill_id` in the `container` parameter along with the code execution tool.

**Prerequisites**: Using Skills via the API requires three beta headers:
- `code-execution-2025-08-25` - Skills run in the code execution container
- `skills-2025-10-02` - Enables Skills functionality
- `files-api-2025-04-14` - Required for uploading/downloading files to/from the container

### Claude Code

Claude Code supports only Custom Skills. Create Skills as directories with SKILL.md files. Claude discovers and uses them automatically.

### Claude Agent SDK

The Claude Agent SDK supports custom Skills through filesystem-based configuration. Create Skills as directories with SKILL.md files in `.claude/skills/`.

### Claude.ai

Claude.ai supports both pre-built Agent Skills and custom Skills. Custom Skills are individual to each user and are not shared organization-wide.

## Skill structure

Every Skill requires a `SKILL.md` file with YAML frontmatter:

```yaml
---
name: your-skill-name
description: Brief description of what this Skill does and when to use it
---

# Your Skill Name

## Instructions
[Clear, step-by-step guidance for Claude to follow]

## Examples
[Concrete examples of using this Skill]
```

**Required fields**: `name` and `description`

**Field requirements**:

`name`:
- Maximum 64 characters
- Must contain only lowercase letters, numbers, and hyphens
- Cannot contain XML tags
- Cannot contain reserved words: "anthropic", "claude"

`description`:
- Must be non-empty
- Maximum 1024 characters
- Cannot contain XML tags

## Security considerations

We strongly recommend using Skills only from trusted sources: those you created yourself or obtained from Anthropic. Skills provide Claude with new capabilities through instructions and code, and while this makes them powerful, it also means a malicious Skill can direct Claude to invoke tools or execute code in ways that don't match the Skill's stated purpose.

> **Warning**: If you must use a Skill from an untrusted or unknown source, exercise extreme caution and thoroughly audit it before use.

**Key security considerations**:
- **Audit thoroughly**: Review all files bundled in the Skill
- **External sources are risky**: Skills that fetch data from external URLs pose particular risk
- **Tool misuse**: Malicious Skills can invoke tools in harmful ways
- **Data exposure**: Skills with access to sensitive data could be designed to leak information
- **Treat like installing software**: Only use Skills from trusted sources

## Available Skills

### Pre-built Agent Skills

- **PowerPoint (pptx)**: Create presentations, edit slides, analyze presentation content
- **Excel (xlsx)**: Create spreadsheets, analyze data, generate reports with charts
- **Word (docx)**: Create documents, edit content, format text
- **PDF (pdf)**: Generate formatted PDF documents and reports

## Limitations and constraints

### Cross-surface availability

**Custom Skills do not sync across surfaces**:
- Skills uploaded to Claude.ai must be separately uploaded to the API
- Skills uploaded via the API are not available on Claude.ai
- Claude Code Skills are filesystem-based and separate from both

### Sharing scope

- **Claude.ai**: Individual user only
- **Claude API**: Workspace-wide; all workspace members can access uploaded Skills
- **Claude Code**: Personal or project-based

### Runtime environment constraints

- **Claude.ai**: Varying network access depending on user/admin settings
- **Claude API**: No network access, no runtime package installation, pre-configured dependencies only
- **Claude Code**: Full network access, global package installation discouraged
