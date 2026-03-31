---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
scraped: 2026-03-23
section: agents-and-tools
---

# Memory tool

The memory tool enables Claude to store and retrieve information across conversations through a memory file directory. Claude can create, read, update, and delete files that persist between sessions, allowing it to build knowledge over time without keeping everything in the context window.

This is the key primitive for just-in-time context retrieval: rather than loading all relevant information upfront, agents store what they learn in memory and pull it back on demand. This keeps the active context focused on what's currently relevant, critical for long-running workflows where loading everything at once would overwhelm the context window.

The memory tool operates client-side: you control where and how the data is stored through your own infrastructure.

> This feature is eligible for Zero Data Retention (ZDR).

## Use cases

- Maintain project context across multiple agent executions
- Learn from past interactions, decisions, and feedback
- Build knowledge bases over time
- Enable cross-conversation learning where Claude improves at recurring workflows

## How it works

When enabled, Claude automatically checks its memory directory before starting tasks. Claude can create, read, update, and delete files in the `/memories` directory to store what it learns while working, then reference those memories in future conversations to handle similar tasks more effectively or pick up where it left off.

Since this is a client-side tool, Claude makes tool calls to perform memory operations, and your application executes those operations locally. This gives you complete control over where and how the memory is stored. For security, you should restrict all memory operations to the `/memories` directory.

### Example: How memory tool calls work

**1. User request:**
```text
"Help me respond to this customer service ticket."
```

**2. Claude checks the memory directory:**

Claude calls the memory tool:
```json
{
  "type": "tool_use",
  "id": "toolu_01C4D5E6F7G8H9I0J1K2L3M4",
  "name": "memory",
  "input": {
    "command": "view",
    "path": "/memories"
  }
}
```

**3. Your application returns the directory contents:**
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01C4D5E6F7G8H9I0J1K2L3M4",
  "content": "Here're the files and directories up to 2 levels deep in /memories, excluding hidden items and node_modules:\n4.0K\t/memories\n1.5K\t/memories/customer_service_guidelines.xml\n2.0K\t/memories/refund_policies.xml"
}
```

**4. Claude reads relevant files and uses them to help.**

## Supported models

The memory tool is available on:

- Claude Opus 4.6 (`claude-opus-4-6`)
- Claude Opus 4.5 (`claude-opus-4-5-20251101`)
- Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- Claude Opus 4 (`claude-opus-4-20250514`)
- Claude Sonnet 4.6 (`claude-sonnet-4-6`)
- Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)

## Basic usage

```bash Shell
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-opus-4-6",
        "max_tokens": 2048,
        "messages": [
            {
                "role": "user",
                "content": "Help me debug this timeout error in my web scraper."
            }
        ],
        "tools": [{
            "type": "memory_20250818",
            "name": "memory"
        }]
    }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=2048,
    messages=[
        {
            "role": "user",
            "content": "I'm working on a Python web scraper that keeps crashing with a timeout error.",
        }
    ],
    tools=[{"type": "memory_20250818", "name": "memory"}],
)
```

## Tool commands

Your client-side implementation needs to handle these memory tool commands:

### view
Shows directory contents or file contents with optional line ranges:

```json
{
  "command": "view",
  "path": "/memories",
  "view_range": [1, 10]
}
```

**For directories:** Return a listing with files, directories, and sizes (2 levels deep, excluding hidden items).

**For files:** Return file contents with line numbers. Format:
```text
Here's the content of {path} with line numbers:
     1	First line content
     2	Second line content
```

**Errors:**
- File/directory does not exist: `"The path {path} does not exist. Please provide a valid path."`

### create
Create a new file:

```json
{
  "command": "create",
  "path": "/memories/notes.txt",
  "file_text": "Meeting notes:\n- Discussed project timeline\n"
}
```

**Return values:**
- Success: `"File created successfully at: {path}"`
- File already exists: `"Error: File {path} already exists"`

### str_replace
Replace text in a file:

```json
{
  "command": "str_replace",
  "path": "/memories/preferences.txt",
  "old_str": "Favorite color: blue",
  "new_str": "Favorite color: green"
}
```

**Return values:**
- Success: `"The memory file has been edited."` followed by a snippet of the edited file
- File does not exist: `"Error: The path {path} does not exist. Please provide a valid path."`
- Text not found: `"No replacement was performed, old_str \`{old_str}\` did not appear verbatim in {path}."`
- Duplicate text: `"No replacement was performed. Multiple occurrences of old_str \`{old_str}\` in lines: {line_numbers}. Please ensure it is unique"`

### insert
Insert text at a specific line:

```json
{
  "command": "insert",
  "path": "/memories/todo.txt",
  "insert_line": 2,
  "insert_text": "- Review memory tool documentation\n"
}
```

**Return values:**
- Success: `"The file {path} has been edited."`
- File does not exist: `"Error: The path {path} does not exist"`
- Invalid line number: `"Error: Invalid \`insert_line\` parameter: {insert_line}. It should be within the range of lines of the file: [0, {n_lines}]"`

### delete
Delete a file or directory:

```json
{
  "command": "delete",
  "path": "/memories/old_file.txt"
}
```

**Return values:**
- Success: `"Successfully deleted {path}"`
- File/directory does not exist: `"Error: The path {path} does not exist"`

### rename
Rename or move a file/directory:

```json
{
  "command": "rename",
  "old_path": "/memories/draft.txt",
  "new_path": "/memories/final.txt"
}
```

**Return values:**
- Success: `"Successfully renamed {old_path} to {new_path}"`
- Source does not exist: `"Error: The path {old_path} does not exist"`
- Destination already exists: `"Error: The destination {new_path} already exists"`

## Prompting guidance

This instruction is automatically included in the system prompt when the memory tool is enabled:

```text
IMPORTANT: ALWAYS VIEW YOUR MEMORY DIRECTORY BEFORE DOING ANYTHING ELSE.
MEMORY PROTOCOL:
1. Use the `view` command of your `memory` tool to check for earlier progress.
2. ... (work on the task) ...
     - As you make progress, record status / progress / thoughts etc in your memory.
ASSUME INTERRUPTION: Your context window might be reset at any moment, so you risk losing any progress that is not recorded in your memory directory.
```

## Security considerations

### Path traversal protection

> **Warning**: Malicious path inputs could attempt to access files outside the `/memories` directory. Your implementation **MUST** validate all paths to prevent directory traversal attacks.

Consider these safeguards:

- Validate that all paths start with `/memories`
- Resolve paths to their canonical form and verify they remain within the memory directory
- Reject paths containing sequences like `../`, `..\\`, or other traversal patterns
- Watch for URL-encoded traversal sequences (`%2e%2e%2f`)
- Use your language's built-in path security utilities

### Other considerations

- **Sensitive information**: Claude will usually refuse to write down sensitive information in memory files. You may want to implement stricter validation.
- **File storage size**: Consider tracking memory file sizes and preventing files from growing too large.
- **Memory expiration**: Consider clearing out memory files periodically that haven't been accessed in an extended time.

## Using with Context Editing

The memory tool can be combined with context editing, which automatically clears old tool results when conversation context grows beyond a configured threshold. This combination enables long-running agentic workflows that would otherwise exceed context limits.

When context editing is enabled and your conversation approaches the clearing threshold, Claude automatically receives a warning notification. This prompts Claude to preserve any important information from tool results into memory files before those results are cleared from the context window.

## Using with Compaction

The memory tool can also be paired with compaction, which provides server-side summarization of older conversation context. For long-running agentic workflows, consider using both: compaction keeps the active context manageable without client-side bookkeeping, and memory persists important information across compaction boundaries so that nothing critical is lost in the summary.

## Multi-session software development pattern

For long-running software projects that span multiple agent sessions, memory files need to be bootstrapped deliberately:

1. **Initializer session:** The first session sets up the memory artifacts before any substantive work begins. This includes a progress log, a feature checklist, and a reference to any startup or initialization script the project needs.

2. **Subsequent sessions:** Each new session opens by reading those memory artifacts. This recovers the full state of the project in seconds.

3. **End-of-session update:** Before a session ends, it updates the progress log with what was completed and what remains.

**Key principle:** Work on one feature at a time. Only mark a feature complete after end-to-end verification confirms it works, not just after the code is written.
