---
source: https://platform.claude.com/docs/en/agent-sdk/skills
scraped: 2026-03-23
section: agent-sdk
---

# Agent Skills in the SDK

Extend Claude with specialized capabilities using Agent Skills in the Claude Agent SDK

---

## Overview

Agent Skills extend Claude with specialized capabilities that Claude autonomously invokes when relevant. Skills are packaged as `SKILL.md` files containing instructions, descriptions, and optional supporting resources.

## How Skills Work with the SDK

When using the Claude Agent SDK, Skills are:

1. **Defined as filesystem artifacts**: Created as `SKILL.md` files in specific directories (`.claude/skills/`)
2. **Loaded from filesystem**: Skills are loaded from configured filesystem locations. You must specify `settingSources` (TypeScript) or `setting_sources` (Python) to load Skills from the filesystem
3. **Automatically discovered**: Once filesystem settings are loaded, Skill metadata is discovered at startup
4. **Model-invoked**: Claude autonomously chooses when to use them based on context
5. **Enabled via allowed_tools**: Add `"Skill"` to your `allowed_tools` to enable Skills

Unlike subagents (which can be defined programmatically), Skills must be created as filesystem artifacts. The SDK does not provide a programmatic API for registering Skills.

> **Default behavior**: By default, the SDK does not load any filesystem settings. To use Skills, you must explicitly configure `settingSources: ['user', 'project']` (TypeScript) or `setting_sources=["user", "project"]` (Python) in your options.

## Using Skills with the SDK

```python Python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    options = ClaudeAgentOptions(
        cwd="/path/to/project",
        setting_sources=["user", "project"],  # Load Skills from filesystem
        allowed_tools=["Skill", "Read", "Write", "Bash"],
    )

    async for message in query(prompt="Help me process this PDF document", options=options):
        print(message)


asyncio.run(main())
```

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Help me process this PDF document",
  options: {
    cwd: "/path/to/project",
    settingSources: ["user", "project"],
    allowedTools: ["Skill", "Read", "Write", "Bash"]
  }
})) {
  console.log(message);
}
```

## Skill Locations

- **Project Skills** (`.claude/skills/`): Shared with your team via git - loaded when `setting_sources` includes `"project"`
- **User Skills** (`~/.claude/skills/`): Personal Skills across all projects - loaded when `setting_sources` includes `"user"`
- **Plugin Skills**: Bundled with installed Claude Code plugins

## Creating Skills

Skills are defined as directories containing a `SKILL.md` file with YAML frontmatter and Markdown content.

**Example directory structure**:
```
.claude/skills/processing-pdfs/
└── SKILL.md
```

## Tool Restrictions

> **Note:** The `allowed-tools` frontmatter field in SKILL.md is only supported when using Claude Code CLI directly. It does not apply when using Skills through the SDK.

When using the SDK, control tool access through the main `allowedTools` option:

```python Python
options = ClaudeAgentOptions(
    setting_sources=["user", "project"],
    allowed_tools=["Skill", "Read", "Grep", "Glob"],
)
```

```typescript TypeScript
const options = {
  settingSources: ["user", "project"],
  allowedTools: ["Skill", "Read", "Grep", "Glob"],
  permissionMode: "dontAsk"
};
```

## Troubleshooting

### Skills Not Found

**Check settingSources configuration**: Skills are only loaded when you explicitly configure `settingSources`/`setting_sources`. This is the most common issue.

```python Python
# Wrong - Skills won't be loaded
options = ClaudeAgentOptions(allowed_tools=["Skill"])

# Correct - Skills will be loaded
options = ClaudeAgentOptions(
    setting_sources=["user", "project"],  # Required to load Skills
    allowed_tools=["Skill"],
)
```

**Check working directory**: The SDK loads Skills relative to the `cwd` option.

**Verify filesystem location**:
```bash
ls .claude/skills/*/SKILL.md
ls ~/.claude/skills/*/SKILL.md
```

## Related Documentation

- [Agent Skills in Claude Code](https://code.claude.com/docs/en/skills): Complete Skills guide
- [Agent Skills Overview](/docs/en/agents-and-tools/agent-skills/overview): Conceptual overview
- [Subagents in the SDK](/docs/en/agent-sdk/subagents): Similar filesystem-based agents with programmatic options
- [Slash Commands in the SDK](/docs/en/agent-sdk/slash-commands): User-invoked commands
