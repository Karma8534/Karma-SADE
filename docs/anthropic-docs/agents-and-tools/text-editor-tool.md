---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/text-editor-tool
scraped: 2026-03-23
section: agents-and-tools
---

# Text editor tool

Claude can use an Anthropic-defined text editor tool to view and modify text files, helping you debug, fix, and improve your code or other text documents.

## Model compatibility

| Model | Tool Version |
|-------|--------------|
| Claude 4.x models | `text_editor_20250728` |
| Claude Sonnet 3.7 (deprecated) | `text_editor_20250124` |

The `text_editor_20250728` tool for Claude 4 models does not include the `undo_edit` command. Older tool versions are not guaranteed to be backwards-compatible with newer models.

## When to use the text editor tool

- **Code debugging:** Identify and fix bugs
- **Code refactoring:** Improve code structure, readability, and performance
- **Documentation generation:** Add docstrings, comments, or README files
- **Test creation:** Create unit tests based on implementation

## Text editor tool commands

### view
Parameters: `command` ("view"), `path`, optional `view_range` ([start, end] line numbers)

### str_replace
Parameters: `command` ("str_replace"), `path`, `old_str` (must match exactly), `new_str`

### create
Parameters: `command` ("create"), `path`, `file_text`

### insert
Parameters: `command` ("insert"), `path`, `insert_line` (0 for beginning), `insert_text`

### undo_edit
Only available in Claude Sonnet 3.7 (deprecated). Not supported in Claude 4.
Parameters: `command` ("undo_edit"), `path`

## Usage example (Claude 4)

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[
        {
            "type": "text_editor_20250728",
            "name": "str_replace_based_edit_tool",
            "max_characters": 10000,
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "There's a syntax error in my primes.py file. Can you help me fix it?",
        }
    ],
)
```

The `max_characters` parameter (optional) controls truncation when viewing large files. Only compatible with `text_editor_20250728` and later.

## Implementation best practices

- **Security**: The tool has access to your local filesystem. Implement proper security measures.
- **Backup**: Always create backups before allowing edits to important files.
- **Validation**: Validate all inputs to prevent unintended changes.
- **Unique matching**: Make sure str_replace replacements match exactly one location.

## Pricing and token usage

| Tool | Additional input tokens |
|------|------------------------|
| `text_editor_20250728` (Claude 4.x) | 700 tokens |
| `text_editor_20250124` (Claude Sonnet 3.7) | 700 tokens |

## Change log

| Date | Version | Changes |
|------|---------|---------|
| July 28, 2025 | `text_editor_20250728` | Updated tool with optional `max_characters` parameter |
| April 29, 2025 | `text_editor_20250429` | Claude 4 release; removes `undo_edit` |
| March 13, 2025 | `text_editor_20250124` | Standalone docs for Claude Sonnet 3.7 |
| October 22, 2024 | `text_editor_20241022` | Initial release with Claude Sonnet 3.5 (retired) |
