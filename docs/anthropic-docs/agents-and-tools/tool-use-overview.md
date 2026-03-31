---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview
scraped: 2026-03-23
section: agents-and-tools
---

# Tool use with Claude

---

Claude is capable of interacting with tools and functions, allowing you to extend Claude's capabilities to perform a wider variety of tasks. Each tool defines a contract: you specify what operations are available and what they return; Claude decides when and how to call them. Tool access is one of the highest-leverage primitives you can give an agent. On benchmarks like [LAB-Bench FigQA](https://lab-bench.org/) (scientific figure interpretation) and [SWE-bench](https://www.swebench.com/) (real-world software engineering), adding even simple tools produces outsized capability gains, often surpassing human expert baselines.

Here's an example of how to provide tools to Claude using the Messages API:

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
        "name": "get_weather",
        "description": "Get the current weather in a given location",
        "input_schema": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "The city and state, e.g. San Francisco, CA"
            }
          },
          "required": ["location"]
        }
      }
    ],
    "messages": [
      {
        "role": "user",
        "content": "What is the weather like in San Francisco?"
      }
    ]
  }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[
        {
            "name": "get_weather",
            "description": "Get the current weather in a given location",
            "input_schema": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"],
            },
        }
    ],
    messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
)
print(response)
```

---

## How tool use works

Claude supports two types of tools:

1. **Client tools**: Tools that execute on your systems, which include:
   - User-defined custom tools that you create and implement
   - Anthropic-defined tools like [computer use](/docs/en/agents-and-tools/tool-use/computer-use-tool) and [text editor](/docs/en/agents-and-tools/tool-use/text-editor-tool) that require client implementation

2. **Server tools**: Tools that execute on Anthropic's servers, like the [web search](/docs/en/agents-and-tools/tool-use/web-search-tool) and [web fetch](/docs/en/agents-and-tools/tool-use/web-fetch-tool) tools. These tools must be specified in the API request but don't require implementation on your part.

> Anthropic-defined tools use versioned types (e.g., `web_search_20250305`, `text_editor_20250124`) to ensure compatibility across model versions.

### Client tools
Integrate client tools with Claude in these steps:

1. **Provide Claude with tools and a user prompt** — Define client tools with names, descriptions, and input schemas in your API request. Include a user prompt that might require these tools.
2. **Claude decides to use a tool** — Claude assesses if any tools can help. If yes, Claude constructs a properly formatted tool use request. The API response has a `stop_reason` of `tool_use`.
3. **Execute the tool and return results** — Extract the tool name and input from Claude's request, execute the tool, and return results in a new `user` message containing a `tool_result` content block.
4. **Claude uses tool result to formulate a response** — Claude analyzes the tool results to craft its final response.

### Server tools

Server tools follow a different workflow where Anthropic's servers handle tool execution in a loop:

1. **Provide Claude with tools and a user prompt** — Server tools like web search and web fetch have their own parameters.
2. **Claude executes the server tool** — Claude assesses if a server tool can help. If yes, Claude executes the tool, and the results are automatically incorporated into Claude's response. The server runs a sampling loop that may execute multiple tool calls before returning a response.
3. **Claude uses the server tool result to formulate a response** — In most cases, no additional user interaction is needed for server tool execution.

> **Handling `pause_turn` with server tools**: The server-side sampling loop has a default limit of 10 iterations. If Claude reaches this limit, the API returns a response with `stop_reason="pause_turn"`. Continue the conversation by sending the response back to let Claude finish processing.

## Pricing

### Client tool pricing

The tools parameter in API requests uses additional tokens. Tokens are used to describe the tools available to Claude:

| Tool | Additional input tokens |
|------|-------------------------|
| `text_editor_20250728` | 700 tokens |
| `text_editor_20250124` | 700 tokens |
| `bash_20250124` | 245 tokens |
| `computer_20251124` | 683 tokens |
| `computer_20250124` | 683 tokens |

### Server tool pricing

| Tool | Price |
|------|-------|
| Web search | $10 per 1,000 searches |
| Web fetch | Free (standard token costs only) |
| Code execution | $0.05 per session hour (free when used with web_search_20260209 or web_fetch_20260209) |

Standard input/output token costs apply to all tool interactions.
