---
source: https://platform.claude.com/docs/en/agent-sdk/sessions
scraped: 2026-03-23
section: agent-sdk
---

# Work with sessions

How sessions persist agent conversation history, and when to use continue, resume, and fork to return to a prior run.

---

A session is the conversation history the SDK accumulates while your agent works. It contains your prompt, every tool call the agent made, every tool result, and every response. The SDK writes it to disk automatically so you can return to it later.

Returning to a session means the agent has full context from before: files it already read, analysis it already performed, decisions it already made. You can ask a follow-up question, recover from an interruption, or branch off to try a different approach.

> **Note:** Sessions persist the **conversation**, not the filesystem. To snapshot and revert file changes the agent made, use [file checkpointing](/docs/en/agent-sdk/file-checkpointing).

This guide covers how to pick the right approach for your app, the SDK interfaces that track sessions automatically, how to capture session IDs and use `resume` and `fork` manually, and what to know about resuming sessions across hosts.

## Choose an approach

How much session handling you need depends on your application's shape. Session management comes into play when you send multiple prompts that should share context. Within a single `query()` call, the agent already takes as many turns as it needs, and permission prompts and `AskUserQuestion` are handled in-loop (they don't end the call).

| What you're building | What to use |
|:---|:---|
| One-shot task: single prompt, no follow-up | Nothing extra. One `query()` call handles it. |
| Multi-turn chat in one process | `ClaudeSDKClient` (Python) or `continue: true` (TypeScript). The SDK tracks the session for you with no ID handling. |
| Pick up where you left off after a process restart | `continue_conversation=True` (Python) / `continue: true` (TypeScript). Resumes the most recent session in the directory, no ID needed. |
| Resume a specific past session (not the most recent) | Capture the session ID and pass it to `resume`. |
| Try an alternative approach without losing the original | Fork the session. |
| Stateless task, don't want anything written to disk (TypeScript only) | Set `persistSession: false`. The session exists only in memory for the duration of the call. Python always persists to disk. |

### Continue, resume, and fork

**Continue** and **resume** both pick up an existing session and add to it. The difference is how they find that session:

- **Continue** finds the most recent session in the current directory. You don't track anything. Works well when your app runs one conversation at a time.
- **Resume** takes a specific session ID. You track the ID. Required when you have multiple sessions or want to return to one that isn't the most recent.

**Fork** is different: it creates a new session that starts with a copy of the original's history. The original stays unchanged. Use fork to try a different direction while keeping the option to go back.

## Automatic session management

### Python: `ClaudeSDKClient`

`ClaudeSDKClient` handles session IDs internally. Each call to `client.query()` automatically continues the same session. The client must be used as an async context manager.

```python Python
import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Glob", "Grep"],
    )

    async with ClaudeSDKClient(options=options) as client:
        # First query: client captures the session ID internally
        await client.query("Analyze the auth module")
        async for message in client.receive_response():
            pass

        # Second query: automatically continues the same session
        await client.query("Now refactor it to use JWT")
        async for message in client.receive_response():
            pass


asyncio.run(main())
```

### TypeScript: `continue: true`

Pass `continue: true` on each subsequent `query()` call and the SDK picks up the most recent session on disk.

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

// First query: creates a new session
for await (const message of query({
  prompt: "Analyze the auth module",
  options: { allowedTools: ["Read", "Glob", "Grep"] }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}

// Second query: continue: true resumes the most recent session
for await (const message of query({
  prompt: "Now refactor it to use JWT",
  options: {
    continue: true,
    allowedTools: ["Read", "Edit", "Write", "Glob", "Grep"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

## Use session options with `query()`

### Capture the session ID

Read the session ID from the `session_id` field on the result message.

```python Python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


async def main():
    session_id = None

    async for message in query(
        prompt="Analyze the auth module and suggest improvements",
        options=ClaudeAgentOptions(allowed_tools=["Read", "Glob", "Grep"]),
    ):
        if isinstance(message, ResultMessage):
            session_id = message.session_id

    return session_id


session_id = asyncio.run(main())
```

```typescript TypeScript
import { query } from "@anthropic-ai/claude-agent-sdk";

let sessionId: string | undefined;

for await (const message of query({
  prompt: "Analyze the auth module and suggest improvements",
  options: { allowedTools: ["Read", "Glob", "Grep"] }
})) {
  if (message.type === "result") {
    sessionId = message.session_id;
  }
}
```

### Resume by ID

```python Python
async for message in query(
    prompt="Now implement the refactoring you suggested",
    options=ClaudeAgentOptions(
        resume=session_id,
        allowed_tools=["Read", "Edit", "Write", "Glob", "Grep"],
    ),
):
    if isinstance(message, ResultMessage) and message.subtype == "success":
        print(message.result)
```

```typescript TypeScript
for await (const message of query({
  prompt: "Now implement the refactoring you suggested",
  options: {
    resume: sessionId,
    allowedTools: ["Read", "Edit", "Write", "Glob", "Grep"]
  }
})) {
  if (message.type === "result" && message.subtype === "success") {
    console.log(message.result);
  }
}
```

### Fork to explore alternatives

Forking creates a new session that starts with a copy of the original's history but diverges from that point.

> **Note:** Forking branches the conversation history, not the filesystem. If a forked agent edits files, those changes are real and visible to any session working in the same directory.

```python Python
forked_id = None
async for message in query(
    prompt="Instead of JWT, implement OAuth2 for the auth module",
    options=ClaudeAgentOptions(resume=session_id, fork_session=True),
):
    if isinstance(message, ResultMessage):
        forked_id = message.session_id
```

```typescript TypeScript
let forkedId: string | undefined;

for await (const message of query({
  prompt: "Instead of JWT, implement OAuth2 for the auth module",
  options: { resume: sessionId, forkSession: true }
})) {
  if (message.type === "system" && message.subtype === "init") {
    forkedId = message.session_id;
  }
}
```

## Resume across hosts

Session files are local to the machine that created them. To resume a session on a different host, either move the session file (`~/.claude/projects/<encoded-cwd>/<session-id>.jsonl`) or capture results as application state and pass them into a fresh session's prompt.

Both SDKs expose `listSessions()` and `getSessionMessages()` for enumerating and reading sessions on disk.

## Related resources

- [How the agent loop works](/docs/en/agent-sdk/agent-loop): Understand turns, messages, and context accumulation within a session
- [File checkpointing](/docs/en/agent-sdk/file-checkpointing): Track and revert file changes across sessions
- [Python `ClaudeAgentOptions`](/docs/en/agent-sdk/python#claude-agent-options): Full session option reference for Python
- [TypeScript `Options`](/docs/en/agent-sdk/typescript#options): Full session option reference for TypeScript
