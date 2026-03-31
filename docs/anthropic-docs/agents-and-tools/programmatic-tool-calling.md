---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/programmatic-tool-calling
scraped: 2026-03-23
section: agents-and-tools
---

# Programmatic tool calling

Programmatic tool calling allows Claude to write code that calls your tools programmatically within a code execution container, rather than requiring round trips through the model for each tool invocation. This reduces latency for multi-tool workflows and decreases token consumption by allowing Claude to filter or process data before it reaches the model's context window.

The difference compounds fast in real workflows. Consider checking budget compliance across 20 employees: the traditional approach requires 20 separate model round-trips, pulling thousands of expense line items into the context along the way. With programmatic tool calling, a single script runs all 20 lookups, filters the results, and returns only the employees who exceeded their limits.

> This feature requires the code execution tool to be enabled.

> This feature is **not** eligible for Zero Data Retention (ZDR). Data is retained according to the feature's standard retention policy.

## Model compatibility

Programmatic tool calling is available on the following models:

| Model | Tool Version |
|-------|--------------|
| Claude Opus 4.6 (`claude-opus-4-6`) | `code_execution_20260120` |
| Claude Sonnet 4.6 (`claude-sonnet-4-6`) | `code_execution_20260120` |
| Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) | `code_execution_20260120` |
| Claude Opus 4.5 (`claude-opus-4-5-20251101`) | `code_execution_20260120` |

> Programmatic tool calling is available via the Claude API and Microsoft Foundry.

## Quick start

Here's a simple example where Claude programmatically queries a database multiple times and aggregates results:

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
                "content": "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue"
            }
        ],
        "tools": [
            {
                "type": "code_execution_20260120",
                "name": "code_execution"
            },
            {
                "name": "query_database",
                "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "sql": {
                            "type": "string",
                            "description": "SQL query to execute"
                        }
                    },
                    "required": ["sql"]
                },
                "allowed_callers": ["code_execution_20260120"]
            }
        ]
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
            "content": "Query sales data for the West, East, and Central regions, then tell me which region had the highest revenue",
        }
    ],
    tools=[
        {"type": "code_execution_20260120", "name": "code_execution"},
        {
            "name": "query_database",
            "description": "Execute a SQL query against the sales database. Returns a list of rows as JSON objects.",
            "input_schema": {
                "type": "object",
                "properties": {
                    "sql": {"type": "string", "description": "SQL query to execute"}
                },
                "required": ["sql"],
            },
            "allowed_callers": ["code_execution_20260120"],
        },
    ],
)

print(response)
```

## How programmatic tool calling works

When you configure a tool to be callable from code execution and Claude decides to use that tool:

1. Claude writes Python code that invokes the tool as a function, potentially including multiple tool calls and pre/post-processing logic
2. Claude runs this code in a sandboxed container via code execution
3. When a tool function is called, code execution pauses and the API returns a `tool_use` block
4. You provide the tool result, and code execution continues (intermediate results are not loaded into Claude's context window)
5. Once all code execution completes, Claude receives the final output and continues working on the task

This approach is particularly useful for:
- **Large data processing:** Filter or aggregate tool results before they reach Claude's context
- **Multi-step workflows:** Save tokens and latency by calling tools serially or in a loop without sampling Claude in-between tool calls
- **Conditional logic:** Make decisions based on intermediate tool results

> Custom tools are converted to async Python functions to support parallel tool calling. When Claude writes code that calls your tools, it uses `await` (e.g., `result = await query_database("<sql>")`).

## Core concepts

### The `allowed_callers` field

The `allowed_callers` field on a tool definition controls which callers can invoke that tool. To enable a tool to be called from code execution:

```json
{
  "name": "my_tool",
  "description": "...",
  "input_schema": { ... },
  "allowed_callers": ["code_execution_20260120"]
}
```

Setting `allowed_callers` to `["code_execution_20260120"]` means:
- The tool can only be invoked from within code execution (not directly by the model)
- When Claude writes code that calls `my_tool(...)`, it routes through the code execution environment
- The tool appears as a Python function to Claude's code

### Tool version for programmatic calling

Use `code_execution_20260120` (not `code_execution_20250825`) when using programmatic tool calling. This newer version enables the `allowed_callers` capability.

## Handling tool results

When code execution calls a tool, the API pauses and returns a `tool_use` block. You respond with the result the same way as standard tool use:

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01ABC123",
      "content": "[{\"region\": \"West\", \"revenue\": 150000}]"
    }
  ]
}
```

Code execution then resumes with the result injected as the function return value. This continues until all code execution completes.

## Pricing

Programmatic tool calling uses the code execution tool, which is priced at **$0.05 per session hour**. Code execution is free when used alongside `web_search_20260209` or `web_fetch_20260209`.

Token costs for programmatic tool calling:
- Input: standard input token pricing
- Output: standard output token pricing
- Intermediate tool results are not loaded into Claude's context window, significantly reducing token consumption for multi-step workflows
