---
source: https://platform.claude.com/docs/en/build-with-claude/extended-thinking
scraped: 2026-03-23
section: build-with-claude
---

# Building with extended thinking

Extended thinking gives Claude enhanced reasoning capabilities for complex tasks, while providing varying levels of transparency into its step-by-step thought process before it delivers its final answer.

> **Note**: For Claude Opus 4.6, use adaptive thinking (`thinking: {type: "adaptive"}`) with the effort parameter instead of the manual thinking mode described on this page. The manual `thinking: {type: "enabled", budget_tokens: N}` configuration is deprecated on Opus 4.6 and will be removed in a future model release.

## Supported models

Extended thinking is supported in the following models:

- Claude Opus 4.6 (`claude-opus-4-6`), adaptive thinking only; manual mode is deprecated
- Claude Opus 4.5 (`claude-opus-4-5-20251101`)
- Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- Claude Opus 4 (`claude-opus-4-20250514`)
- Claude Sonnet 4.6 (`claude-sonnet-4-6`), supports both manual extended thinking with interleaved mode and adaptive thinking
- Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Claude Sonnet 3.7 (`claude-3-7-sonnet-20250219`) (deprecated)
- Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)

## How extended thinking works

When extended thinking is turned on, Claude creates `thinking` content blocks where it outputs its internal reasoning. Claude incorporates insights from this reasoning before crafting a final response.

The API response includes `thinking` content blocks, followed by `text` content blocks:

```json
{
  "content": [
    {
      "type": "thinking",
      "thinking": "Let me analyze this step by step...",
      "signature": "WaUjzkypQ2mUEVM36O2TxuC06KN8xyfbJwyem2dw3URve/op91XWHOEBLLqIOMfFG/UvLEczmEsUjavL...."
    },
    {
      "type": "text",
      "text": "Based on my analysis..."
    }
  ]
}
```

## How to use extended thinking

To enable extended thinking, add a `thinking` object with `type: "enabled"` and set `budget_tokens` to specify the maximum tokens for reasoning:

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[
        {
            "role": "user",
            "content": "Are there an infinite number of prime numbers such that n mod 4 == 3?",
        }
    ],
)

for block in response.content:
    if block.type == "thinking":
        print(f"\nThinking summary: {block.thinking}")
    elif block.type == "text":
        print(f"\nResponse: {block.text}")
```

The `budget_tokens` parameter determines the maximum tokens allowed for Claude's internal reasoning. Larger budgets can improve response quality by enabling more thorough analysis, though Claude may not use the entire allocation.

> **Important**: `budget_tokens` must be less than `max_tokens`. With interleaved thinking and tools, you can exceed this limit as the token limit becomes your entire context window.

## Summarized thinking

With extended thinking enabled on Claude 4 models, the Messages API returns a **summary** of Claude's full thinking process (default behavior). This provides full intelligence benefits while preventing misuse.

Key considerations:
- You're charged for the full thinking tokens generated, not the summary tokens
- The billed output token count will **not match** the count of tokens in the response
- Summarization preserves key ideas with minimal added latency
- Claude Sonnet 3.7 continues to return full thinking output

> **Note**: Claude Opus 4.6 supports up to 128k output tokens. Earlier models support up to 64k output tokens.

## Controlling thinking display

The `display` field controls how thinking content is returned:

- `"summarized"` (default): Thinking blocks contain summarized thinking text
- `"omitted"`: Thinking blocks return with an empty `thinking` field, with signature for multi-turn continuity

Setting `display: "omitted"` is useful when your application doesn't surface thinking to users. The primary benefit is **faster time-to-first-text-token when streaming**, since the server skips streaming thinking tokens and delivers only the signature.

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000,
        "display": "omitted",
    },
    messages=[
        {"role": "user", "content": "What is 27 * 453?"},
    ],
)
```

## Streaming thinking

You can stream extended thinking responses using server-sent events (SSE). When streaming is enabled, you receive thinking content via `thinking_delta` events.

```python
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    thinking={"type": "enabled", "budget_tokens": 10000},
    messages=[
        {
            "role": "user",
            "content": "What is the greatest common divisor of 1071 and 462?",
        }
    ],
) as stream:
    thinking_started = False
    response_started = False

    for event in stream:
        if event.type == "content_block_start":
            print(f"\nStarting {event.content_block.type} block...")
            thinking_started = False
            response_started = False
        elif event.type == "content_block_delta":
            if event.delta.type == "thinking_delta":
                if not thinking_started:
                    print("Thinking: ", end="", flush=True)
                    thinking_started = True
                print(event.delta.thinking, end="", flush=True)
            elif event.delta.type == "text_delta":
                if not response_started:
                    print("Response: ", end="", flush=True)
                    response_started = True
                print(event.delta.text, end="", flush=True)
        elif event.type == "content_block_stop":
            print("\nBlock complete.")
```

## Extended thinking with tool use

Extended thinking can be used alongside tool use, allowing Claude to reason through tool selection and results processing.

**Limitations:**
- Only supports `tool_choice: {"type": "auto"}` (default) or `{"type": "none"}`
- Using `tool_choice: {"type": "any"}` or specifying a specific tool will result in an error

**Important**: During tool use, you must pass `thinking` blocks back to the API unmodified to maintain reasoning continuity.

### Toggling thinking modes in conversations

You cannot toggle thinking in the middle of an assistant turn, including during tool use loops. The entire assistant turn must operate in a single thinking mode.

**Graceful degradation**: When a mid-turn thinking conflict occurs, the API automatically disables thinking for that request. To confirm thinking was active, check for the presence of `thinking` blocks in the response.

**Best practice**: Plan your thinking strategy at the start of each turn rather than trying to toggle mid-turn.

### Interleaved thinking

Extended thinking with tool use in Claude 4 models supports **interleaved thinking**, enabling Claude to think between tool calls and make more sophisticated reasoning after receiving tool results.

**Model support:**
- **Claude Opus 4.6**: Automatically enabled with adaptive thinking
- **Claude Sonnet 4.6**: Add beta header `interleaved-thinking-2025-05-14` with manual thinking
- **Other Claude 4 models**: Add beta header `interleaved-thinking-2025-05-14`

**Important considerations:**
- With interleaved thinking, `budget_tokens` can exceed `max_tokens` (represents total budget across all thinking blocks)
- Only supported for tool use via Messages API
- The beta header is automatically handled or safely ignored on models where it doesn't apply

## Extended thinking with prompt caching

When using extended thinking with prompt caching, consider:

**Thinking block context removal:**
- Thinking blocks from previous turns are removed from context, affecting cache breakpoints
- When continuing conversations with tool use, thinking blocks are cached and count as input tokens when read from cache
- Toggling thinking parameters invalidates message cache breakpoints

**Cache invalidation patterns:**
- Changes to thinking parameters (enabled/disabled or budget allocation) invalidate message cache
- Interleaved thinking amplifies cache invalidation due to thinking blocks between tool calls
- System prompts and tools remain cached despite thinking parameter changes

**Key point**: While thinking blocks don't consume context window space visually, they count toward input token usage when cached. For longer thinking sessions, consider using the 1-hour cache duration.

### System prompt caching behavior

System prompts with cache markers remain cached even when thinking parameters change. This allows you to maintain cached system prompts across multiple requests with different thinking configurations.

### Messages caching behavior

Messages cache is invalidated when thinking parameters change. For example, changing `budget_tokens` from 4000 to 8000 will break message cache, but system prompt cache remains valid.
