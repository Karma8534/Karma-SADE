---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool
scraped: 2026-03-23
section: agents-and-tools
---

# Tool search tool

The tool search tool enables Claude to work with hundreds or thousands of tools by dynamically discovering and loading them on-demand. Instead of loading all tool definitions into the context window upfront, Claude searches your tool catalog (including tool names, descriptions, argument names, and argument descriptions) and loads only the tools it needs.

This approach solves two problems that compound quickly as tool libraries scale:

- **Context bloat:** Tool definitions eat into your context budget fast. A typical multi-server setup (GitHub, Slack, Sentry, Grafana, Splunk) can consume ~55k tokens in definitions before Claude does any actual work. Tool search typically reduces this by over 85%, loading only the 3–5 tools Claude actually needs for a given request.
- **Tool selection accuracy:** Claude's ability to correctly pick the right tool degrades significantly once you exceed 30–50 available tools. By surfacing a focused set of relevant tools on demand, tool search keeps selection accuracy high even across thousands of tools.

Although this is provided as a server-side tool, you can also implement your own client-side tool search functionality.

> Server-side tool search is **not** covered by Zero Data Retention (ZDR) arrangements. Data is retained according to the feature's standard retention policy. Custom client-side tool search implementations use the standard Messages API and are ZDR-eligible.

> On Amazon Bedrock, server-side tool search is available only via the invoke API, not the converse API.

## How tool search works

There are two tool search variants:

- **Regex** (`tool_search_tool_regex_20251119`): Claude constructs regex patterns to search for tools
- **BM25** (`tool_search_tool_bm25_20251119`): Claude uses natural language queries to search for tools

When you enable the tool search tool:

1. You include a tool search tool (e.g., `tool_search_tool_regex_20251119` or `tool_search_tool_bm25_20251119`) in your tools list
2. You provide all tool definitions with `defer_loading: true` for tools that shouldn't be loaded immediately
3. Claude sees only the tool search tool and any non-deferred tools initially
4. When Claude needs additional tools, it searches using a tool search tool
5. The API returns 3-5 most relevant `tool_reference` blocks
6. These references are automatically expanded into full tool definitions
7. Claude selects from the discovered tools and invokes them

This keeps your context window efficient while maintaining high tool selection accuracy.

## Quick start

Here's a simple example with deferred tools:

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
                "content": "What is the weather in San Francisco?"
            }
        ],
        "tools": [
            {
                "type": "tool_search_tool_regex_20251119",
                "name": "tool_search_tool_regex"
            },
            {
                "name": "get_weather",
                "description": "Get the weather at a specific location",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"]
                        }
                    },
                    "required": ["location"]
                },
                "defer_loading": true
            },
            {
                "name": "search_files",
                "description": "Search through files in the workspace",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "file_types": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["query"]
                },
                "defer_loading": true
            }
        ]
    }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=2048,
    messages=[{"role": "user", "content": "What is the weather in San Francisco?"}],
    tools=[
        {"type": "tool_search_tool_regex_20251119", "name": "tool_search_tool_regex"},
        {
            "name": "get_weather",
            "description": "Get the weather at a specific location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
            "defer_loading": True,
        },
        {
            "name": "search_files",
            "description": "Search through files in the workspace",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "file_types": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["query"],
            },
            "defer_loading": True,
        },
    ],
)

print(response)
```

## The `defer_loading` parameter

Set `defer_loading: true` on tools that shouldn't be loaded into context immediately. When `defer_loading` is true:
- The tool's full definition is not sent to the model initially
- The tool can be discovered via tool search
- Only the tool's name and description are used during search
- The full definition is loaded only when Claude decides to use it

## Tool search result format

When Claude uses the tool search tool, the API returns `tool_reference` blocks that are automatically expanded into full tool definitions:

```json
{
  "type": "tool_reference",
  "tool_name": "get_weather",
  "tool_search_result_id": "tsr_01ABC123"
}
```

## Custom tool search implementation

You can also implement client-side tool search by returning `tool_reference` blocks from your own search implementation. This approach is ZDR-eligible and gives you full control over the search algorithm and tool catalog.

When implementing client-side tool search:
1. Handle the tool search tool call on your end
2. Search your tool catalog using whatever method you prefer
3. Return `tool_reference` blocks for the 3-5 most relevant tools
4. Include the full tool definitions alongside these references in the tool results

## Pricing

The tool search tool adds tokens to your API calls based on the tool definitions that are loaded. Because only relevant tools are loaded, you typically see significant token savings compared to loading all tool definitions upfront.

The tool search tool itself (regex or BM25 variant) follows standard tool pricing. See tool use pricing documentation for complete pricing details.
