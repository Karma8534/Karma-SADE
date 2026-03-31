---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use
scraped: 2026-03-23
section: agents-and-tools
---

# How to implement tool use

## Choosing a model

Use the latest Claude Opus (4.6) model for complex tools and ambiguous queries; it handles multiple tools better and seeks clarification when needed.

Use Claude Haiku models for straightforward tools, but note they may infer missing parameters.

> If using Claude with tool use and extended thinking, refer to the extended thinking guide for more information.

## Specifying client tools

Client tools (both Anthropic-defined and user-defined) are specified in the `tools` top-level parameter of the API request. Each tool definition includes:

| Parameter | Description |
|-----------|-------------|
| `name` | The name of the tool. Must match the regex `^[a-zA-Z0-9_-]{1,64}$`. |
| `description` | A detailed plaintext description of what the tool does, when it should be used, and how it behaves. |
| `input_schema` | A JSON Schema object defining the expected parameters for the tool. |
| `input_examples` | (Optional) An array of example input objects to help Claude understand how to use the tool. |

### Example simple tool definition

```json
{
  "name": "get_weather",
  "description": "Get the current weather in a given location",
  "input_schema": {
    "type": "object",
    "properties": {
      "location": {
        "type": "string",
        "description": "The city and state, e.g. San Francisco, CA"
      },
      "unit": {
        "type": "string",
        "enum": ["celsius", "fahrenheit"],
        "description": "The unit of temperature, either 'celsius' or 'fahrenheit'"
      }
    },
    "required": ["location"]
  }
}
```

## Tool use system prompt

When you call the Claude API with the `tools` parameter, the API constructs a special system prompt from the tool definitions, tool configuration, and any user-specified system prompt.

## Best practices for tool definitions

- **Provide extremely detailed descriptions.** Your descriptions should explain:
  - What the tool does
  - When it should be used (and when it shouldn't)
  - What each parameter means and how it affects the tool's behavior
  - Any important caveats or limitations
  - Aim for at least 3-4 sentences per tool description

- **Consolidate related operations into fewer tools.** Rather than creating separate tools for each action, group them into a single tool with an `action` parameter.

- **Use meaningful namespacing in tool names.** Prefix names with the service when tools span multiple services (e.g., `github_list_prs`, `slack_send_message`).

- **Design tool responses to return only high-signal information.** Return semantic, stable identifiers rather than opaque internal references.

## Providing tool use examples

You can provide concrete examples of valid tool inputs via the optional `input_examples` field. This is particularly useful for complex tools with nested objects, optional parameters, or format-sensitive inputs.

### Basic usage

Add an optional `input_examples` field to your tool definition with an array of example input objects:

```python
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
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The unit of temperature",
                    },
                },
                "required": ["location"],
            },
            "input_examples": [
                {"location": "San Francisco, CA", "unit": "fahrenheit"},
                {"location": "Tokyo, Japan", "unit": "celsius"},
                {"location": "New York, NY"}  # 'unit' is optional
            ],
        }
    ],
    messages=[{"role": "user", "content": "What's the weather like in San Francisco?"}],
)
```

### Requirements and limitations

- **Schema validation** - Each example must be valid according to the tool's `input_schema`
- **Not supported for server-side tools** - Only user-defined tools can have input examples
- **Token cost** - Examples add to prompt tokens: ~20-50 tokens for simple examples, ~100-200 tokens for complex nested objects

## Tool runner (beta)

The tool runner provides an out-of-the-box solution for executing tools with Claude. It automatically:

- Executes tools when Claude calls them
- Handles the request/response cycle
- Manages conversation state
- Provides type safety and validation

The tool runner is currently in beta and available in the Python, TypeScript, and Ruby SDKs.

### Basic usage

Define tools using the SDK helpers, then use the tool runner to execute them.

**Python example:**

```python
import anthropic
import json
from anthropic import beta_tool

client = anthropic.Anthropic()

@beta_tool
def get_weather(location: str, unit: str = "fahrenheit") -> str:
    """Get the current weather in a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA
        unit: Temperature unit, either 'celsius' or 'fahrenheit'
    """
    return json.dumps({"temperature": "20°C", "condition": "Sunny"})

runner = client.beta.messages.tool_runner(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[get_weather],
    messages=[
        {
            "role": "user",
            "content": "What's the weather like in Paris?",
        }
    ],
)
for message in runner:
    print(message.content[0].text)
```

### Streaming

Enable streaming to receive events as they arrive:

```python
runner = client.beta.messages.tool_runner(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[calculate_sum],
    messages=[{"role": "user", "content": "What is 15 + 27?"}],
    stream=True,
)

for message_stream in runner:
    for event in message_stream:
        print("event:", event)
    print("message:", message_stream.get_final_message())
```

## Controlling Claude's output

### Forcing tool use

You can specify the tool in the `tool_choice` field to force Claude to use a specific tool:

```text
tool_choice = {"type": "tool", "name": "get_weather"}
```

Four possible options:

- `auto` - Claude decides whether to call any provided tools or not (default when `tools` are provided)
- `any` - Claude must use one of the provided tools, but doesn't force a particular tool
- `tool` - Forces Claude to always use a particular tool
- `none` - Prevents Claude from using any tools (default when no `tools` are provided)

> When using extended thinking with tool use, only `tool_choice: {"type": "auto"}` (the default) and `tool_choice: {"type": "none"}` are compatible.

### JSON output

Tools do not necessarily need to be client functions. You can use tools anytime you want the model to return JSON output that follows a provided schema.

### Parallel tool use

By default, Claude may use multiple tools to answer a user query. You can disable this behavior by setting `disable_parallel_tool_use=true`.

## Handling tool use and tool result content blocks

When Claude responds with a `tool_use` content block, it includes:

- `id`: A unique identifier for this tool use block
- `name`: The name of the tool being used
- `input`: An object containing the input being passed to the tool

### Handling results from client tools

When you receive a tool use response:

1. Extract the `name`, `id`, and `input` from the `tool_use` block
2. Run the actual tool in your codebase corresponding to that tool name
3. Continue the conversation by sending a new user message with a `tool_result` content block containing:
   - `tool_use_id`: The `id` of the tool use request
   - `content`: The result of the tool as a string, list of content blocks, or documents
   - `is_error` (optional): Set to `true` if tool execution resulted in an error

**Important formatting requirements:**
- Tool result blocks must immediately follow their corresponding tool use blocks
- In the user message containing tool results, `tool_result` blocks must come FIRST in the content array. Any text must come AFTER all tool results.

### Example tool result

```json
{
  "role": "user",
  "content": [
    {
      "type": "tool_result",
      "tool_use_id": "toolu_01A09q90qw90lq917835lq9",
      "content": "15 degrees"
    }
  ]
}
```
