---
source: https://platform.claude.com/docs/en/agent-sdk/python
scraped: 2026-03-23
section: agent-sdk
---

# Agent SDK Reference - Python

Complete API reference for the Python Agent SDK, including all functions, types, and classes.

## Installation

```bash
pip install claude-agent-sdk
```

## Choosing between `query()` and `ClaudeSDKClient`

The Python SDK provides two ways to interact with Claude Code:

| Feature             | `query()`                     | `ClaudeSDKClient`                  |
| :------------------ | :---------------------------- | :--------------------------------- |
| **Session**         | Creates new session each time | Reuses same session                |
| **Conversation**    | Single exchange               | Multiple exchanges in same context |
| **Connection**      | Managed automatically         | Manual control                     |
| **Streaming Input** | ✅ Supported                  | ✅ Supported                       |
| **Interrupts**      | ❌ Not supported              | ✅ Supported                       |
| **Hooks**           | ✅ Supported                  | ✅ Supported                       |
| **Custom Tools**    | ✅ Supported                  | ✅ Supported                       |
| **Continue Chat**   | ❌ New session each time      | ✅ Maintains conversation          |
| **Use Case**        | One-off tasks                 | Continuous conversations           |

### When to use `query()` (new session each time)

**Best for:**
- One-off questions where you don't need conversation history
- Independent tasks that don't require context from previous exchanges
- Simple automation scripts
- When you want a fresh start each time

### When to use `ClaudeSDKClient` (continuous conversation)

**Best for:**
- **Continuing conversations** - When you need Claude to remember context
- **Follow-up questions** - Building on previous responses
- **Interactive applications** - Chat interfaces, REPLs
- **Response-driven logic** - When next action depends on Claude's response
- **Session control** - Managing conversation lifecycle explicitly

## Functions

### `query()`

Creates a new session for each interaction with Claude Code. Returns an async iterator that yields messages as they arrive. Each call to `query()` starts fresh with no memory of previous interactions.

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None
) -> AsyncIterator[Message]
```

#### Parameters

| Parameter | Type                         | Description                                                                |
| :-------- | :--------------------------- | :------------------------------------------------------------------------- |
| `prompt`  | `str \| AsyncIterable[dict]` | The input prompt as a string or async iterable for streaming mode          |
| `options` | `ClaudeAgentOptions \| None` | Optional configuration object (defaults to `ClaudeAgentOptions()` if None) |
| `transport` | `Transport \| None` | Optional custom transport for communicating with the CLI process |

#### Returns

Returns an `AsyncIterator[Message]` that yields messages from the conversation.

#### Example - With options

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer",
        permission_mode="acceptEdits",
        cwd="/home/user/project",
    )

    async for message in query(prompt="Create a Python web server", options=options):
        print(message)


asyncio.run(main())
```

### `tool()`

Decorator for defining MCP tools with type safety.

```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any],
    annotations: ToolAnnotations | None = None
) -> Callable[[Callable[[Any], Awaitable[dict[str, Any]]]], SdkMcpTool[Any]]
```

#### Parameters

| Parameter      | Type                         | Description                                                                                                                      |
| :------------- | :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| `name`         | `str`                        | Unique identifier for the tool                                                                                                   |
| `description`  | `str`                        | Human-readable description of what the tool does                                                                                 |
| `input_schema` | `type \| dict[str, Any]`     | Schema defining the tool's input parameters (see below)                                                                          |
| `annotations`  | `ToolAnnotations \| None`    | Optional MCP tool annotations (e.g., `readOnlyHint`, `destructiveHint`, `openWorldHint`). Imported from `mcp.types`              |

#### Input schema options

1. **Simple type mapping** (recommended):
   ```python
   {"text": str, "count": int, "enabled": bool}
   ```

2. **JSON Schema format** (for complex validation):
   ```python
   {
       "type": "object",
       "properties": {
           "text": {"type": "string"},
           "count": {"type": "integer", "minimum": 0},
       },
       "required": ["text"],
   }
   ```

#### Returns

A decorator function that wraps the tool implementation and returns an `SdkMcpTool` instance.

#### Example

```python
from claude_agent_sdk import tool
from typing import Any


@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}
```

### `create_sdk_mcp_server()`

Create an in-process MCP server that runs within your Python application.

```python
def create_sdk_mcp_server(
    name: str,
    version: str = "1.0.0",
    tools: list[SdkMcpTool[Any]] | None = None
) -> McpSdkServerConfig
```

#### Parameters

| Parameter | Type                            | Default   | Description                                           |
| :-------- | :------------------------------ | :-------- | :---------------------------------------------------- |
| `name`    | `str`                           | -         | Unique identifier for the server                      |
| `version` | `str`                           | `"1.0.0"` | Server version string                                 |
| `tools`   | `list[SdkMcpTool[Any]] \| None` | `None`    | List of tool functions created with `@tool` decorator |

#### Returns

Returns an `McpSdkServerConfig` object that can be passed to `ClaudeAgentOptions.mcp_servers`.

#### Example

```python
from claude_agent_sdk import tool, create_sdk_mcp_server


@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args):
    return {"content": [{"type": "text", "text": f"Sum: {args['a'] + args['b']}"}]}


@tool("multiply", "Multiply two numbers", {"a": float, "b": float})
async def multiply(args):
    return {"content": [{"type": "text", "text": f"Product: {args['a'] * args['b']}"}]}


calculator = create_sdk_mcp_server(
    name="calculator",
    version="2.0.0",
    tools=[add, multiply],  # Pass decorated functions
)

# Use with Claude
options = ClaudeAgentOptions(
    mcp_servers={"calc": calculator},
    allowed_tools=["mcp__calc__add", "mcp__calc__multiply"],
)
```

### `list_sessions()`

Lists past sessions with metadata. Filter by project directory or list sessions across all projects. Synchronous; returns immediately.

```python
def list_sessions(
    directory: str | None = None,
    limit: int | None = None,
    include_worktrees: bool = True
) -> list[SDKSessionInfo]
```

#### Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `directory` | `str \| None` | `None` | Directory to list sessions for. When omitted, returns sessions across all projects |
| `limit` | `int \| None` | `None` | Maximum number of sessions to return |
| `include_worktrees` | `bool` | `True` | When `directory` is inside a git repository, include sessions from all worktree paths |

#### Return type: `SDKSessionInfo`

| Property | Type | Description |
| :------- | :--- | :---------- |
| `session_id` | `str` | Unique session identifier |
| `summary` | `str` | Display title: custom title, auto-generated summary, or first prompt |
| `last_modified` | `int` | Last modified time in milliseconds since epoch |
| `file_size` | `int` | Session file size in bytes |
| `custom_title` | `str \| None` | User-set session title |
| `first_prompt` | `str \| None` | First meaningful user prompt in the session |
| `git_branch` | `str \| None` | Git branch at the end of the session |
| `cwd` | `str \| None` | Working directory for the session |

#### Example

```python
from claude_agent_sdk import list_sessions

for session in list_sessions(directory="/path/to/project", limit=10):
    print(f"{session.summary} ({session.session_id})")
```

### `get_session_messages()`

Retrieves messages from a past session. Synchronous; returns immediately.

```python
def get_session_messages(
    session_id: str,
    directory: str | None = None,
    limit: int | None = None,
    offset: int = 0
) -> list[SessionMessage]
```

#### Parameters

| Parameter | Type | Default | Description |
| :-------- | :--- | :------ | :---------- |
| `session_id` | `str` | required | The session ID to retrieve messages for |
| `directory` | `str \| None` | `None` | Project directory to look in. When omitted, searches all projects |
| `limit` | `int \| None` | `None` | Maximum number of messages to return |
| `offset` | `int` | `0` | Number of messages to skip from the start |

#### Return type: `SessionMessage`

| Property | Type | Description |
| :------- | :--- | :---------- |
| `type` | `Literal["user", "assistant"]` | Message role |
| `uuid` | `str` | Unique message identifier |
| `session_id` | `str` | Session identifier |
| `message` | `Any` | Raw message content |
| `parent_tool_use_id` | `None` | Reserved for future use |

#### Example

```python
from claude_agent_sdk import list_sessions, get_session_messages

sessions = list_sessions(limit=1)
if sessions:
    messages = get_session_messages(sessions[0].session_id)
    for msg in messages:
        print(f"[{msg.type}] {msg.uuid}")
```

## Classes

### `ClaudeSDKClient`

**Maintains a conversation session across multiple exchanges.** This is the Python equivalent of how the TypeScript SDK's `query()` function works internally - it creates a client object that can continue conversations.

#### Key Features

- **Session continuity**: Maintains conversation context across multiple `query()` calls
- **Same conversation**: The session retains previous messages
- **Interrupt support**: Can stop execution mid-task
- **Explicit lifecycle**: You control when the session starts and ends
- **Response-driven flow**: Can react to responses and send follow-ups
- **Custom tools and hooks**: Supports custom tools (created with `@tool` decorator) and hooks

```python
class ClaudeSDKClient:
    def __init__(self, options: ClaudeAgentOptions | None = None, transport: Transport | None = None)
    async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
    async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
    async def receive_messages(self) -> AsyncIterator[Message]
    async def receive_response(self) -> AsyncIterator[Message]
    async def interrupt(self) -> None
    async def set_permission_mode(self, mode: str) -> None
    async def set_model(self, model: str | None = None) -> None
    async def rewind_files(self, user_message_id: str) -> None
    async def get_mcp_status(self) -> list[McpServerStatus]
    async def add_mcp_server(self, name: str, config: McpServerConfig) -> None
    async def remove_mcp_server(self, name: str) -> None
    async def get_server_info(self) -> dict[str, Any] | None
    async def disconnect(self) -> None
```

#### Methods

| Method                      | Description                                                         |
| :-------------------------- | :------------------------------------------------------------------ |
| `__init__(options)`         | Initialize the client with optional configuration                   |
| `connect(prompt)`           | Connect to Claude with an optional initial prompt or message stream |
| `query(prompt, session_id)` | Send a new request in streaming mode                                |
| `receive_messages()`        | Receive all messages from Claude as an async iterator               |
| `receive_response()`        | Receive messages until and including a ResultMessage                |
| `interrupt()`               | Send interrupt signal (only works in streaming mode)                |
| `set_permission_mode(mode)` | Change the permission mode for the current session                  |
| `set_model(model)`          | Change the model for the current session. Pass `None` to reset to default |
| `rewind_files(user_message_id)` | Restore files to their state at the specified user message. Requires `enable_file_checkpointing=True`. |
| `get_mcp_status()`          | Get the status of all configured MCP servers                        |
| `add_mcp_server(name, config)` | Add an MCP server to the running session                         |
| `remove_mcp_server(name)`   | Remove an MCP server from the running session                       |
| `get_server_info()`         | Get server information including session ID and capabilities        |
| `disconnect()`              | Disconnect from Claude                                              |

#### Context Manager Support

```python
async with ClaudeSDKClient() as client:
    await client.query("Hello Claude")
    async for message in client.receive_response():
        print(message)
```

> **Important:** When iterating over messages, avoid using `break` to exit early as this can cause asyncio cleanup issues. Instead, let the iteration complete naturally or use flags to track when you've found what you need.

#### Example - Continuing a conversation

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, AssistantMessage, TextBlock, ResultMessage


async def main():
    async with ClaudeSDKClient() as client:
        # First question
        await client.query("What's the capital of France?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")

        # Follow-up question - the session retains the previous context
        await client.query("What's the population of that city?")

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"Claude: {block.text}")


asyncio.run(main())
```

#### Example - Using interrupts

```python
import asyncio
from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


async def interruptible_task():
    options = ClaudeAgentOptions(allowed_tools=["Bash"], permission_mode="acceptEdits")

    async with ClaudeSDKClient(options=options) as client:
        await client.query("Count from 1 to 100 slowly")
        await asyncio.sleep(2)
        await client.interrupt()
        print("Task interrupted!")
        await client.query("Just say hello instead")

        async for message in client.receive_response():
            pass


asyncio.run(interruptible_task())
```

## Types

### `ClaudeAgentOptions`

Configuration dataclass for Claude Code queries.

```python
@dataclass
class ClaudeAgentOptions:
    tools: list[str] | ToolsPreset | None = None
    allowed_tools: list[str] = field(default_factory=list)
    system_prompt: str | SystemPromptPreset | None = None
    mcp_servers: dict[str, McpServerConfig] | str | Path = field(default_factory=dict)
    permission_mode: PermissionMode | None = None
    continue_conversation: bool = False
    resume: str | None = None
    max_turns: int | None = None
    max_budget_usd: float | None = None
    disallowed_tools: list[str] = field(default_factory=list)
    model: str | None = None
    fallback_model: str | None = None
    betas: list[SdkBeta] = field(default_factory=list)
    output_format: dict[str, Any] | None = None
    permission_prompt_tool_name: str | None = None
    cwd: str | Path | None = None
    cli_path: str | Path | None = None
    settings: str | None = None
    add_dirs: list[str | Path] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    extra_args: dict[str, str | None] = field(default_factory=dict)
    max_buffer_size: int | None = None
    stderr: Callable[[str], None] | None = None
    can_use_tool: CanUseTool | None = None
    hooks: dict[HookEvent, list[HookMatcher]] | None = None
    user: str | None = None
    include_partial_messages: bool = False
    fork_session: bool = False
    agents: dict[str, AgentDefinition] | None = None
    setting_sources: list[SettingSource] | None = None
    sandbox: SandboxSettings | None = None
    plugins: list[SdkPluginConfig] = field(default_factory=list)
    thinking: ThinkingConfig | None = None
    effort: Literal["low", "medium", "high", "max"] | None = None
    enable_file_checkpointing: bool = False
```

Key properties:

| Property                      | Type                                         | Default              | Description                                                                                                                                                                             |
| :---------------------------- | :------------------------------------------- | :------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tools`                       | `list[str] \| ToolsPreset \| None`           | `None`               | Tools configuration. Use `{"type": "preset", "preset": "claude_code"}` for Claude Code's default tools                                                                                  |
| `allowed_tools`               | `list[str]`                                  | `[]`                 | Tools to auto-approve without prompting                                                                                                                                |
| `system_prompt`               | `str \| SystemPromptPreset \| None`          | `None`               | System prompt configuration                                                                                                                                          |
| `mcp_servers`                 | `dict[str, McpServerConfig] \| str \| Path`  | `{}`                 | MCP server configurations or path to config file                                                                                                                                        |
| `permission_mode`             | `PermissionMode \| None`                     | `None`               | Permission mode for tool usage                                                                                                                                                          |
| `cwd`                         | `str \| Path \| None`                        | `None`               | Current working directory                                                                                                                                                               |
| `model`                       | `str \| None`                                | `None`               | Claude model to use                                                                                                                                                                     |
| `sandbox`                     | `SandboxSettings \| None`                    | `None`               | Configure sandbox behavior programmatically                                                                        |
| `thinking`                    | `ThinkingConfig \| None`                     | `None`               | Controls extended thinking behavior                                                                                                        |
| `enable_file_checkpointing`   | `bool`                                       | `False`              | Enable file change tracking for rewinding                                                                                                                                              |

### `PermissionMode`

```python
PermissionMode = Literal[
    "default",          # Standard permission behavior
    "acceptEdits",      # Auto-accept file edits
    "plan",             # Planning mode - no execution
    "bypassPermissions",# Bypass all permission checks (use with caution)
]
```

### `Message` Types

```python
Message = UserMessage | AssistantMessage | SystemMessage | ResultMessage | StreamEvent
```

#### `AssistantMessage`

```python
@dataclass
class AssistantMessage:
    content: list[ContentBlock]
    model: str
    parent_tool_use_id: str | None = None
    error: AssistantMessageError | None = None
```

#### `ResultMessage`

```python
@dataclass
class ResultMessage:
    subtype: str
    duration_ms: int
    duration_api_ms: int
    is_error: bool
    num_turns: int
    session_id: str
    total_cost_usd: float | None = None
    usage: dict[str, Any] | None = None
    result: str | None = None
    stop_reason: str | None = None
    structured_output: Any = None
```

### Content Blocks

```python
ContentBlock = TextBlock | ThinkingBlock | ToolUseBlock | ToolResultBlock

@dataclass
class TextBlock:
    text: str

@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict[str, Any]

@dataclass
class ToolResultBlock:
    tool_use_id: str
    content: str | list[dict[str, Any]] | None = None
    is_error: bool | None = None
```

### `SandboxSettings`

```python
class SandboxSettings(TypedDict, total=False):
    enabled: bool
    autoAllowBashIfSandboxed: bool
    excludedCommands: list[str]
    allowUnsandboxedCommands: bool
    network: SandboxNetworkConfig
    ignoreViolations: SandboxIgnoreViolations
    enableWeakerNestedSandbox: bool
```

### `ThinkingConfig`

```python
class ThinkingConfigAdaptive(TypedDict):
    type: Literal["adaptive"]

class ThinkingConfigEnabled(TypedDict):
    type: Literal["enabled"]
    budget_tokens: int

class ThinkingConfigDisabled(TypedDict):
    type: Literal["disabled"]

ThinkingConfig = ThinkingConfigAdaptive | ThinkingConfigEnabled | ThinkingConfigDisabled
```

## Error Types

### `ClaudeSDKError`

Base exception class for all SDK errors.

### `CLINotFoundError`

Raised when Claude Code CLI is not installed or not found.

```python
class CLINotFoundError(CLIConnectionError):
    def __init__(
        self, message: str = "Claude Code not found", cli_path: str | None = None
    ): ...
```

### `ProcessError`

```python
class ProcessError(ClaudeSDKError):
    def __init__(
        self, message: str, exit_code: int | None = None, stderr: str | None = None
    ):
        self.exit_code = exit_code
        self.stderr = stderr
```

## Example Usage

### Basic file operations

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock
import asyncio


async def create_project():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Write", "Bash"],
        permission_mode="acceptEdits",
        cwd="/home/user/project",
    )

    async for message in query(
        prompt="Create a Python project structure with setup.py", options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"Using tool: {block.name}")


asyncio.run(create_project())
```

### Error handling

```python
from claude_agent_sdk import query, CLINotFoundError, ProcessError, CLIJSONDecodeError

try:
    async for message in query(prompt="Hello"):
        print(message)
except CLINotFoundError:
    print("Claude Code CLI not found. Try reinstalling: pip install --force-reinstall claude-agent-sdk")
except ProcessError as e:
    print(f"Process failed with exit code: {e.exit_code}")
except CLIJSONDecodeError as e:
    print(f"Failed to parse response: {e}")
```

### Interactive session with ClaudeSDKClient

```python
from claude_agent_sdk import ClaudeSDKClient
import asyncio


async def interactive_session():
    async with ClaudeSDKClient() as client:
        await client.query("What's the weather like?")
        async for msg in client.receive_response():
            print(msg)

        await client.query("Tell me more about that")
        async for msg in client.receive_response():
            print(msg)


asyncio.run(interactive_session())
```
