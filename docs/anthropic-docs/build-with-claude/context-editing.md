---
source: https://platform.claude.com/docs/en/build-with-claude/context-editing
scraped: 2026-03-23
section: build-with-claude
---

# Context editing

Automatically manage conversation context as it grows with context editing.

---

## Overview

> For most use cases, server-side compaction is the primary strategy for managing context in long-running conversations. The strategies on this page are useful for specific scenarios where you need more fine-grained control over what content is cleared.

Context editing allows you to selectively clear specific content from conversation history as it grows. Beyond optimizing costs and staying within limits, this is about actively curating what Claude sees: context is a finite resource with diminishing returns, and irrelevant content degrades model focus. Context editing gives you fine-grained runtime control over that curation. This page covers:

- **Tool result clearing** - Best for agentic workflows with heavy tool use where old tool results are no longer needed
- **Thinking block clearing** - For managing thinking blocks when using extended thinking, with options to preserve recent thinking for context continuity
- **Client-side SDK compaction** - An SDK-based alternative for summary-based context management (server-side compaction is generally preferred)

| Approach | Where it runs | Strategies | How it works |
|----------|---------------|------------|--------------|
| **Server-side** | API | Tool result clearing (`clear_tool_uses_20250919`)<br/>Thinking block clearing (`clear_thinking_20251015`) | Applied before the prompt reaches Claude. Clears specific content from conversation history. Each strategy can be configured independently. |
| **Client-side** | SDK | Compaction | Available in Python, TypeScript, and Ruby SDKs when using `tool_runner`. Generates a summary and replaces full conversation history. |

## Server-side strategies

> Context editing is in beta with support for tool result clearing and thinking block clearing. To enable it, use the beta header `context-management-2025-06-27` in your API requests.

> This feature is in beta and is **not** eligible for Zero Data Retention (ZDR). Beta features are excluded from ZDR.

### Tool result clearing

The `clear_tool_uses_20250919` strategy clears tool results when conversation context grows beyond your configured threshold. This is particularly useful for agentic workflows with heavy tool use. Older tool results (like file contents or search results) are no longer needed once Claude has processed them.

When activated, the API automatically clears the oldest tool results in chronological order. Each cleared result is replaced with placeholder text so Claude knows it was removed. By default, only tool results are cleared. You can optionally clear both tool results and tool calls (the tool use parameters) by setting `clear_tool_inputs` to true.

### Thinking block clearing

The `clear_thinking_20251015` strategy manages `thinking` blocks in conversations when extended thinking is enabled. This strategy gives you control over thinking preservation: you can choose to keep more thinking blocks to maintain reasoning continuity, or clear them more aggressively to save context space.

> **Default behavior:** When extended thinking is enabled without configuring the `clear_thinking_20251015` strategy, the API automatically keeps only the thinking blocks from the last assistant turn (equivalent to `keep: {type: "thinking_turns", value: 1}`).
>
> To maximize cache hits, preserve all thinking blocks by setting `keep: "all"`.

An assistant conversation turn may include multiple content blocks (e.g. when using tools) and multiple thinking blocks (e.g. with interleaved thinking).

### Context editing happens server-side

Context editing is applied server-side before the prompt reaches Claude. Your client application maintains the full, unmodified conversation history. You do not need to sync your client state with the edited version. Continue managing your full conversation history locally as you normally would.

### Context editing and prompt caching

Context editing's interaction with prompt caching varies by strategy:

- **Tool result clearing**: Invalidates cached prompt prefixes when content is cleared. To account for this, clear enough tokens to make the cache invalidation worthwhile. Use the `clear_at_least` parameter to ensure a minimum number of tokens is cleared each time. You'll incur cache write costs each time content is cleared, but subsequent requests can reuse the newly cached prefix.

- **Thinking block clearing**: When thinking blocks are **kept** in context (not cleared), the prompt cache is preserved, enabling cache hits and reducing input token costs. When thinking blocks are **cleared**, the cache is invalidated at the point where clearing occurs.

## Supported models

Context editing is available on:

- Claude Opus 4.6 (`claude-opus-4-6`)
- Claude Opus 4.5 (`claude-opus-4-5-20251101`)
- Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- Claude Opus 4 (`claude-opus-4-20250514`)
- Claude Sonnet 4.6 (`claude-sonnet-4-6`)
- Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)

## Tool result clearing usage

The simplest way to enable tool result clearing is to specify only the strategy type:

```bash Shell
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --header "anthropic-beta: context-management-2025-06-27" \
    --data '{
        "model": "claude-opus-4-6",
        "max_tokens": 4096,
        "messages": [
            {
                "role": "user",
                "content": "Search for recent developments in AI"
            }
        ],
        "tools": [
            {
                "type": "web_search_20250305",
                "name": "web_search"
            }
        ],
        "context_management": {
            "edits": [
                {"type": "clear_tool_uses_20250919"}
            ]
        }
    }'
```

```python Python
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Search for recent developments in AI"}],
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    betas=["context-management-2025-06-27"],
    context_management={"edits": [{"type": "clear_tool_uses_20250919"}]},
)
```

## Configuration options for tool result clearing

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `trigger_token_count` | integer | 95% of context window | Token threshold that triggers clearing |
| `clear_at_least` | integer | 0 | Minimum tokens to clear per activation |
| `clear_tool_inputs` | boolean | false | Also clear tool call inputs (not just results) |

## Configuration options for thinking block clearing

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keep` | string or object | `{"type": "thinking_turns", "value": 1}` | Controls which thinking blocks to preserve |

### `keep` values

- `"all"` — Keep all thinking blocks (maximizes cache hits)
- `{"type": "thinking_turns", "value": N}` — Keep thinking from last N assistant turns
- `{"type": "thinking_blocks", "value": N}` — Keep last N individual thinking blocks

## Combining strategies

You can use both strategies together:

```python Python
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=messages,
    tools=tools,
    thinking={"type": "enabled", "budget_tokens": 10000},
    betas=["context-management-2025-06-27"],
    context_management={
        "edits": [
            {
                "type": "clear_tool_uses_20250919",
                "trigger_token_count": 150000,
                "clear_at_least": 10000,
            },
            {
                "type": "clear_thinking_20251015",
                "keep": {"type": "thinking_turns", "value": 2},
            },
        ]
    },
)
```

## Client-side compaction (SDK)

The Python, TypeScript, and Ruby SDKs provide a `tool_runner` helper that supports client-side compaction. When the conversation approaches the context window limit, the SDK generates a summary of the conversation and replaces the full history with the summary.

Server-side compaction (via the `compact_20260112` strategy) is generally preferred as it requires less integration work. Client-side compaction is useful when you need more control over the summarization process.

```python Python
from anthropic import Anthropic
from anthropic.lib.tool_runner import ToolRunner

client = Anthropic()

runner = ToolRunner(
    client=client,
    model="claude-opus-4-6",
    tools=[...],
    compaction={"type": "enabled"},
)

result = runner.run(messages=[...])
```
