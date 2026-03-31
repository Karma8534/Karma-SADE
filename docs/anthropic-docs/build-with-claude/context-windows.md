---
source: https://platform.claude.com/docs/en/build-with-claude/context-windows
scraped: 2026-03-23
section: build-with-claude
---

# Context windows

---

As conversations grow, you'll eventually approach context window limits. This guide explains how context windows work and introduces strategies for managing them effectively.

For long-running conversations and agentic workflows, server-side compaction is the primary strategy for context management. For more specialized needs, context editing offers additional strategies like tool result clearing and thinking block clearing.

## Understanding the context window

The "context window" refers to all the text a language model can reference when generating a response, including the response itself. This is different from the large corpus of data the language model was trained on, and instead represents a "working memory" for the model. A larger context window allows the model to handle more complex and lengthy prompts, but more context isn't automatically better. As token count grows, accuracy and recall degrade, a phenomenon known as *context rot*. This makes curating what's in context just as important as how much space is available.

Claude achieves state-of-the-art results on long-context retrieval benchmarks like MRCR and GraphWalks, but these gains depend on what's in context, not just how much fits.

## How context windows work

- **Progressive token accumulation:** As the conversation advances through turns, each user message and assistant response accumulates within the context window. Previous turns are preserved completely.
- **Linear growth pattern:** The context usage grows linearly with each turn, with previous turns preserved completely.
- **Context window capacity:** The total available context window (up to 1M tokens) represents the maximum capacity for storing conversation history and generating new output from Claude.
- **Input-output flow:** Each turn consists of:
  - **Input phase:** Contains all previous conversation history plus the current user message
  - **Output phase:** Generates a text response that becomes part of a future input

## The context window with extended thinking

When using extended thinking, all input and output tokens, including the tokens used for thinking, count toward the context window limit, with a few nuances in multi-turn situations.

However, previous thinking blocks are automatically stripped from the context window calculation by the Claude API and are not part of the conversation history that the model "sees" for subsequent turns, preserving token capacity for actual conversation content.

- **Stripping extended thinking:** Extended thinking blocks are generated during each turn's output phase, **but are not carried forward as input tokens for subsequent turns**. You do not need to strip the thinking blocks yourself. The Claude API automatically does this for you if you pass them back.
- The API automatically excludes thinking blocks from previous turns when you pass them back as part of the conversation history.
- Extended thinking tokens are billed as output tokens only once, during their generation.
- The effective context window calculation becomes: `context_window = (input_tokens - previous_thinking_tokens) + current_turn_tokens`.

## The context window with extended thinking and tool use

When combining extended thinking with tool use:

1. **First turn architecture:** Input includes tools configuration and user message. Output includes extended thinking + text response + tool use request. All input and output components count toward the context window.

2. **Tool result handling (turn 2):** Input includes every block in the first turn as well as the `tool_result`. The extended thinking block **must** be returned with the corresponding tool results. This is the only case wherein you **have to** return thinking blocks.

3. **Third Step:** Input includes all inputs and the output from the previous turn except the thinking block, which can be dropped now that Claude has completed the entire tool use cycle. The API will automatically strip the thinking block for you if you pass it back.

## Context window sizes

Claude Opus 4.6 and Sonnet 4.6 have a 1M-token context window.

> **Note**: Claude Sonnet 4.5 and Sonnet 4 require the `context-1m-2025-08-07` beta header for requests beyond 200k tokens (available to organizations in usage tier 4 and those with custom rate limits). Other Claude models have a 200k-token context window.

A single request can include up to 600 images or PDF pages (100 for models with a 200k-token context window).

## Context awareness in Claude Sonnet 4.6, Sonnet 4.5, and Haiku 4.5

Claude Sonnet 4.6, Claude Sonnet 4.5, and Claude Haiku 4.5 feature **context awareness**. This capability lets these models track their remaining context window (i.e. "token budget") throughout a conversation.

**How it works:**

At the start of a conversation, Claude receives information about its total context window:

```xml
<budget:token_budget>1000000</budget:token_budget>
```

After each tool call, Claude receives an update on remaining capacity:

```xml
<system_warning>Token usage: 35000/1000000; 965000 remaining</system_warning>
```

**Benefits:**

Context awareness is particularly valuable for:
- Long-running agent sessions that require sustained focus
- Multi-context-window workflows where state transitions matter
- Complex tasks requiring careful token management

## Managing context with compaction

If your conversations regularly approach context window limits, server-side compaction is the recommended approach. Compaction provides server-side summarization that automatically condenses earlier parts of a conversation, enabling long-running conversations beyond context limits with minimal integration work. It is currently available in beta for Claude Opus 4.6 and Sonnet 4.6.

For more specialized needs, context editing offers additional strategies:
- **Tool result clearing** - Clear old tool results in agentic workflows
- **Thinking block clearing** - Manage thinking blocks with extended thinking

## Context window management with newer Claude models

Newer Claude models (starting with Claude Sonnet 3.7) return a validation error when prompt and output tokens exceed the context window, rather than silently truncating. This change provides more predictable behavior but requires more careful token management.

Use the token counting API to estimate token usage before sending messages to Claude.
