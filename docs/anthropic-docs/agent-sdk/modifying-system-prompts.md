---
source: https://platform.claude.com/docs/en/agent-sdk/modifying-system-prompts
scraped: 2026-03-23
section: agent-sdk
---

# Modifying system prompts

Learn how to customize Claude's behavior by modifying system prompts using three approaches - output styles, systemPrompt with append, and custom system prompts.

---

System prompts define Claude's behavior, capabilities, and response style. The Claude Agent SDK provides three ways to customize system prompts: using output styles (persistent, file-based configurations), appending to Claude Code's prompt, or using a fully custom prompt.

> **Note:** The Agent SDK uses a **minimal system prompt** by default. It contains only essential tool instructions but omits Claude Code's coding guidelines, response style, and project context. To include the full Claude Code system prompt, specify `systemPrompt: { preset: "claude_code" }` in TypeScript or `system_prompt={"type": "preset", "preset": "claude_code"}` in Python.

## Methods of modification

### Method 1: CLAUDE.md files (project-level instructions)

CLAUDE.md files provide project-specific context and instructions that are automatically read by the Agent SDK when it runs in a directory.

**IMPORTANT:** The SDK only reads CLAUDE.md files when you explicitly configure `settingSources` (TypeScript) or `setting_sources` (Python):

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Add a new React component for user profiles",
  options: {
    systemPrompt: { type: "preset", preset: "claude_code" },
    settingSources: ["project"]  // Required to load CLAUDE.md from project
  }
})) {
  // ...
}
```

```python Python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Add a new React component for user profiles",
    options=ClaudeAgentOptions(
        system_prompt={"type": "preset", "preset": "claude_code"},
        setting_sources=["project"],  # Required to load CLAUDE.md from project
    ),
):
    pass
```

### Method 2: Output styles (persistent configurations)

Output styles are saved configurations stored as markdown files and can be reused across sessions and projects. Activate via CLI: `/output-style [style-name]`

Output styles are loaded when you include `settingSources: ['user']` or `settingSources: ['project']` in your options.

### Method 3: Using `systemPrompt` with append

Use the Claude Code preset with an `append` property to add custom instructions while preserving all built-in functionality.

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

for await (const message of query({
  prompt: "Help me write a Python function to calculate fibonacci numbers",
  options: {
    systemPrompt: {
      type: "preset",
      preset: "claude_code",
      append: "Always include detailed docstrings and type hints in Python code."
    }
  }
})) {
  // ...
}
```

```python Python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Help me write a Python function to calculate fibonacci numbers",
    options=ClaudeAgentOptions(
        system_prompt={
            "type": "preset",
            "preset": "claude_code",
            "append": "Always include detailed docstrings and type hints in Python code.",
        }
    ),
):
    pass
```

### Method 4: Custom system prompts

Provide a custom string as `systemPrompt` to replace the default entirely.

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

const customPrompt = `You are a Python coding specialist.
Follow these guidelines:
- Write clean, well-documented code
- Use type hints for all functions
- Include comprehensive docstrings`;

for await (const message of query({
  prompt: "Create a data processing pipeline",
  options: { systemPrompt: customPrompt }
})) {
  // ...
}
```

## Comparison of all four approaches

| Feature | CLAUDE.md | Output Styles | `systemPrompt` with append | Custom `systemPrompt` |
| ----------------------- | ------------------- | ------------------ | -------------------------- | ------------------------- |
| **Persistence** | Per-project file | Saved as files | Session only | Session only |
| **Default tools** | Preserved | Preserved | Preserved | Lost (unless included) |
| **Built-in safety** | Maintained | Maintained | Maintained | Must be added |
| **Customization level** | Additions only | Replace default | Additions only | Complete control |

## See also

- [Output styles](https://code.claude.com/docs/en/output-styles) - Complete output styles documentation
- [TypeScript SDK guide](/docs/en/agent-sdk/typescript) - Complete SDK usage guide
- [Configuration guide](https://code.claude.com/docs/en/settings) - General configuration options
