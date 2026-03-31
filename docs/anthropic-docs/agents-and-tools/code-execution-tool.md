---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/code-execution-tool
scraped: 2026-03-23
section: agents-and-tools
---

# Code execution tool

Claude can analyze data, create visualizations, perform complex calculations, run system commands, create and edit files, and process uploaded files directly within the API conversation. The code execution tool allows Claude to run Bash commands and manipulate files, including writing code, in a secure, sandboxed environment.

**Code execution is free when used with web search or web fetch.** When `web_search_20260209` or `web_fetch_20260209` is included in your request, there are no additional charges for code execution tool calls beyond the standard input and output token costs. Standard code execution charges apply when these tools are not included.

Code execution is a core primitive for building high-performance agents. It enables dynamic filtering in web search and web fetch tools, allowing Claude to process results before they reach the context window, improving accuracy while reducing token consumption.

> This feature is **not** eligible for Zero Data Retention (ZDR). Data is retained according to the feature's standard retention policy.

## Model compatibility

The code execution tool is available on the following models:

| Model | Tool Version |
|-------|--------------|
| Claude Opus 4.6 (`claude-opus-4-6`) | `code_execution_20250825` |
| Claude Sonnet 4.6 (`claude-sonnet-4-6`) | `code_execution_20250825` |
| Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) | `code_execution_20250825` |
| Claude Opus 4.5 (`claude-opus-4-5-20251101`) | `code_execution_20250825` |
| Claude Opus 4.1 (`claude-opus-4-1-20250805`) | `code_execution_20250825` |
| Claude Opus 4 (`claude-opus-4-20250514`) | `code_execution_20250825` |
| Claude Sonnet 4 (`claude-sonnet-4-20250514`) | `code_execution_20250825` |
| Claude Sonnet 3.7 (`claude-3-7-sonnet-20250219`) (deprecated) | `code_execution_20250825` |
| Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) | `code_execution_20250825` |
| Claude Haiku 3.5 (`claude-3-5-haiku-latest`) (deprecated) | `code_execution_20250825` |

> The current version `code_execution_20250825` supports Bash commands and file operations. A legacy version `code_execution_20250522` (Python only) is also available.

> Older tool versions are not guaranteed to be backwards-compatible with newer models.

## Platform availability

Code execution is available on:
- **Claude API** (Anthropic)
- **Microsoft Azure AI Foundry**

Code execution is not currently available on Amazon Bedrock or Google Vertex AI.

## Quick start

Here's a simple example that asks Claude to perform a calculation:

```bash Shell
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-opus-4-6",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": "Calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]"
            }
        ],
        "tools": [{
            "type": "code_execution_20250825",
            "name": "code_execution"
        }]
    }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Calculate the mean and standard deviation of [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)

print(response)
```

## How code execution works

When you add the code execution tool to your API request:

1. Claude evaluates whether code execution would help answer your question
2. The tool automatically provides Claude with the following capabilities:
   - **Bash commands**: Execute shell commands for system operations and package management
   - **File operations**: Create, view, and edit files directly, including writing code
3. Claude can use any combination of these capabilities in a single request
4. All operations run in a secure sandbox environment
5. Claude provides results with any generated charts, calculations, or analysis

## Using code execution with other execution tools

When you provide code execution alongside client-provided tools that also run code (such as a bash tool or custom REPL), Claude is operating in a multi-computer environment. The code execution tool runs in Anthropic's sandboxed container, while your client-provided tools run in a separate environment that you control. Claude can sometimes confuse these environments.

To avoid this, add instructions to your system prompt that clarify the distinction:

```text
When multiple code execution environments are available, be aware that:
- Variables, files, and state do NOT persist between different execution environments
- Use the code_execution tool for general-purpose computation in Anthropic's sandboxed environment
- Use client-provided execution tools (e.g., bash) when you need access to the user's local system, files, or data
- If you need to pass results between environments, explicitly include outputs in subsequent tool calls rather than assuming shared state
```

## How to use the tool

### Execute Bash commands

Ask Claude to check system information and install packages:

```python Python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Check the Python version and list installed packages",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
```

### Analyze data and create visualizations

```python Python
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Create a visualization of the following sales data: Q1: $100k, Q2: $120k, Q3: $90k, Q4: $150k",
        }
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
)
```

## Retrieve generated files

When Claude creates files during code execution, the response includes file references. These files can be retrieved using the Files API.

Each file reference in the response contains a `file_id` that you can use to download the file:

```python Python
# Extract file IDs from the response
for block in response.content:
    if block.type == "tool_result":
        for result in block.content:
            if hasattr(result, "file_id"):
                file_id = result.file_id
                # Download using Files API
                file_content = client.beta.files.download(
                    file_id=file_id,
                    betas=["files-api-2025-04-14"]
                )
```

## Upgrade to latest tool version

To migrate from `code_execution_20250522` (Python only) to `code_execution_20250825` (Bash + files):

1. Update the tool type in your request from `code_execution_20250522` to `code_execution_20250825`
2. Update any response parsing to handle the new content block types
3. Note that the new version supports Bash commands in addition to Python execution

## Pricing

Code execution is priced at **$0.05 per session hour**. Code execution is free when used alongside `web_search_20260209` or `web_fetch_20260209`.

Token costs for code execution tool:
- Input: standard input token pricing
- Output: standard output token pricing
- File content included in context counts as input tokens

See [tool use pricing](/docs/en/agents-and-tools/tool-use/overview#pricing) for complete pricing details.
