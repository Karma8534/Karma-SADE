---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/bash-tool
scraped: 2026-03-23
section: agents-and-tools
---

# Bash tool

The bash tool enables Claude to execute shell commands in a persistent bash session, allowing system operations, script execution, and command-line automation.

## Overview

The bash tool provides Claude with:
- Persistent bash session that maintains state
- Ability to run any shell command
- Access to environment variables and working directory
- Command chaining and scripting capabilities

## Model compatibility

| Model | Tool Version |
|-------|--------------|
| Claude 4 models and Sonnet 3.7 (deprecated) | `bash_20250124` |

> Older tool versions are not guaranteed to be backwards-compatible with newer models. Always use the tool version that corresponds to your model version.

## Use cases

- **Development workflows:** Run build commands, tests, and development tools
- **System automation:** Execute scripts, manage files, automate tasks
- **Data processing:** Process files, run analysis scripts, manage datasets
- **Environment setup:** Install packages, configure environments

## Quick start

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[{"type": "bash_20250124", "name": "bash"}],
    messages=[
        {"role": "user", "content": "List all Python files in the current directory."}
    ],
)
```

```bash Shell
curl https://api.anthropic.com/v1/messages \
  -H "content-type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "tools": [
      {
        "type": "bash_20250124",
        "name": "bash"
      }
    ],
    "messages": [
      {
        "role": "user",
        "content": "List all Python files in the current directory."
      }
    ]
  }'
```

## How it works

The bash tool maintains a persistent session:

1. Claude determines what command to run
2. You execute the command in a bash shell
3. Return the output (stdout and stderr) to Claude
4. Session state persists between commands (environment variables, working directory)

## Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `command` | Yes* | The bash command to run |
| `restart` | No | Set to `true` to restart the bash session |

*Required unless using `restart`

## Example: Multi-step automation

Claude can chain commands to complete complex tasks:

```python
# User request
"Install the requests library and create a simple Python script that fetches a joke from an API, then run it."

# Claude's tool uses:
# 1. Install package
{"command": "pip install requests"}

# 2. Create script
{
    "command": "cat > fetch_joke.py << 'EOF'\nimport requests\nresponse = requests.get('https://official-joke-api.appspot.com/random_joke')\njoke = response.json()\nprint(f\"Setup: {joke['setup']}\")\nprint(f\"Punchline: {joke['punchline']}\")\nEOF"
}

# 3. Run script
{"command": "python fetch_joke.py"}
```

The session maintains state between commands, so files created in step 2 are available in step 3.

## Implement the bash tool

The bash tool is implemented as a schema-less tool. When using this tool, you don't need to provide an input schema; the schema is built into Claude's model.

### Set up a bash environment

Create a persistent bash session that Claude can interact with:

```python
import subprocess
import threading
import queue


class BashSession:
    def __init__(self):
        self.process = subprocess.Popen(
            ["/bin/bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
        )
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        self._start_readers()
```

### Process Claude's tool calls

```python
for content in response.content:
    if content.type == "tool_use" and content.name == "bash":
        if content.input.get("restart"):
            bash_session.restart()
            result = "Bash session restarted"
        else:
            command = content.input.get("command")
            result = bash_session.execute_command(command)

        # Return result to Claude
        tool_result = {
            "type": "tool_result",
            "tool_use_id": content.id,
            "content": result,
        }
```

### Implement safety measures

```python
def validate_command(command):
    # Block dangerous commands
    dangerous_patterns = ["rm -rf /", "format", ":(){:|:&};:"]
    for pattern in dangerous_patterns:
        if pattern in command:
            return False, f"Command contains dangerous pattern: {pattern}"
    return True, None
```

### Handle errors

When implementing the bash tool, handle various error scenarios:

**Command execution timeout:**
```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "Error: Command timed out after 30 seconds",
      "is_error": true
    }
  ]
}
```

### Implementation best practices

**Use command timeouts:**
```python
def execute_with_timeout(command, timeout=30):
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout} seconds"
```

**Handle large outputs:**
```python
def truncate_output(output, max_lines=100):
    lines = output.split("\n")
    if len(lines) > max_lines:
        truncated = "\n".join(lines[:max_lines])
        return f"{truncated}\n\n... Output truncated ({len(lines)} total lines) ..."
    return output
```

**Log all commands:**
```python
import logging

def log_command(command, output, user_id):
    logging.info(f"User {user_id} executed: {command}")
    logging.info(f"Output: {output[:200]}...")
```

## Security

> **Warning**: The bash tool provides direct system access. Implement these essential safety measures:
> - Running in isolated environments (Docker/VM)
> - Implementing command filtering and allowlists
> - Setting resource limits (CPU, memory, disk)
> - Logging all executed commands

### Key recommendations
- Use `ulimit` to set resource constraints
- Filter dangerous commands (`sudo`, `rm -rf`, etc.)
- Run with minimal user permissions
- Monitor and log all command execution

## Pricing

The bash tool adds **245 input tokens** to your API calls.

Additional tokens are consumed by:
- Command outputs (stdout/stderr)
- Error messages
- Large file contents

## Common patterns

### Development workflows
- Running tests: `pytest && coverage report`
- Building projects: `npm install && npm run build`
- Git operations: `git status && git add . && git commit -m "message"`

### Git-based checkpointing

Git serves as a structured recovery mechanism in long-running agent workflows:

- **Capture a baseline:** Before any agent work begins, commit the current state.
- **Commit per feature:** Each completed feature gets its own commit.
- **Reconstruct state at session start:** Read `git log` alongside a progress file.
- **Revert on failure:** If work goes sideways, `git checkout` reverts to the last good commit.

### File operations
- Processing data: `wc -l *.csv && ls -lh *.csv`
- Searching files: `find . -name "*.py" | xargs grep "pattern"`
- Creating backups: `tar -czf backup.tar.gz ./data`

## Limitations

- **No interactive commands:** Cannot handle `vim`, `less`, or password prompts
- **No GUI applications:** Command-line only
- **Session scope:** Persists within conversation, lost between API calls
- **Output limits:** Large outputs may be truncated
- **No streaming:** Results returned after completion

## Combining with other tools

The bash tool is most powerful when combined with the text editor and other tools.

> If you're also using the [code execution tool](/docs/en/agents-and-tools/tool-use/code-execution-tool), Claude has access to two separate execution environments: your local bash session and Anthropic's sandboxed container. State is not shared between them.
