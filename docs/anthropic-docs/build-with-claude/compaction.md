---
source: https://platform.claude.com/docs/en/build-with-claude/compaction
scraped: 2026-03-23
section: build-with-claude
---

# Compaction

Server-side context compaction for managing long conversations that approach context window limits.

---

> **Tip**: Server-side compaction is the recommended strategy for managing context in long-running conversations and agentic workflows. It handles context management automatically with minimal integration work.

Compaction extends the effective context length for long-running conversations and tasks by automatically summarizing older context when approaching the context window limit. This isn't just about staying under a token cap. As conversations get longer, models struggle to maintain focus across the full history. Compaction keeps the active context focused and performant by replacing stale content with concise summaries.

This is ideal for:

- Chat-based, multi-turn conversations where you want users to use one chat for a long period of time
- Task-oriented prompts that require a lot of follow-up work (often tool use) that may exceed the context window

> **Note**: Compaction is in beta. Include the beta header `compact-2026-01-12` in your API requests to use this feature.

> **Note**: Compaction is eligible for Zero Data Retention (ZDR) arrangements.

## Supported models

Compaction is supported on the following models:

- Claude Opus 4.6 (`claude-opus-4-6`)
- Claude Sonnet 4.6 (`claude-sonnet-4-6`)

## How compaction works

When compaction is enabled, Claude automatically summarizes your conversation when it approaches the configured token threshold. The API:

1. Detects when input tokens exceed your specified trigger threshold.
2. Generates a summary of the current conversation.
3. Creates a `compaction` block containing the summary.
4. Continues the response with the compacted context.

On subsequent requests, append the response to your messages. The API automatically drops all message blocks prior to the `compaction` block, continuing the conversation from the summary.

## Basic usage

Enable compaction by adding the `compact_20260112` strategy to `context_management.edits` in your Messages API request.

```bash Shell
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "anthropic-beta: compact-2026-01-12" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-opus-4-6",
    "max_tokens": 4096,
    "messages": [
        {
            "role": "user",
            "content": "Help me build a website"
        }
    ],
    "context_management": {
        "edits": [
            {
                "type": "compact_20260112"
            }
        ]
    }
}'
```

```python Python
import anthropic

client = anthropic.Anthropic()

messages = [{"role": "user", "content": "Help me build a website"}]

response = client.beta.messages.create(
    betas=["compact-2026-01-12"],
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=messages,
    context_management={"edits": [{"type": "compact_20260112"}]},
)

# Append the response (including any compaction block) to continue the conversation
messages.append({"role": "assistant", "content": response.content})
```

```typescript TypeScript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const messages: Anthropic.Beta.Messages.BetaMessageParam[] = [
  { role: "user", content: "Help me build a website" }
];

const response = await client.beta.messages.create({
  betas: ["compact-2026-01-12"],
  model: "claude-opus-4-6",
  max_tokens: 4096,
  messages,
  context_management: {
    edits: [{ type: "compact_20260112" }]
  }
} as unknown as Anthropic.Beta.Messages.MessageCreateParamsNonStreaming);

// Append the response (including any compaction block) to continue the conversation
messages.push({
  role: "assistant",
  content: response.content as unknown as Anthropic.Beta.Messages.BetaContentBlockParam[]
});
```

## Configuring the trigger threshold

By default, compaction triggers when input tokens exceed 95% of the context window. You can customize this threshold using the `trigger_token_count` parameter. The value must be between 1 and the model's context window size.

```python Python
response = client.beta.messages.create(
    betas=["compact-2026-01-12"],
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=messages,
    context_management={
        "edits": [
            {
                "type": "compact_20260112",
                "trigger_token_count": 80000  # Trigger compaction at 80k tokens
            }
        ]
    },
)
```

## Streaming with compaction

Compaction is supported with streaming responses. When compaction occurs during a stream, a `compaction` block appears in the streamed response:

```python Python
import anthropic

client = anthropic.Anthropic()

messages = [{"role": "user", "content": "Help me write a very long novel..."}]

with client.beta.messages.stream(
    betas=["compact-2026-01-12"],
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=messages,
    context_management={"edits": [{"type": "compact_20260112"}]},
) as stream:
    response = stream.get_final_message()

# Always append the full response to maintain conversation state
messages.append({"role": "assistant", "content": response.content})
```

## Handling the compaction block

When compaction occurs, the response includes a `compaction` block before any text content:

```json
{
  "content": [
    {
      "type": "compaction",
      "summary": "We've been discussing building a website. So far we've covered: HTML structure, CSS styling basics, and started working on JavaScript interactivity. The user wants a contact form with email validation.",
      "tokens_removed": 15000,
      "tokens_added": 350
    },
    {
      "type": "text",
      "text": "Let me continue helping you with the JavaScript validation..."
    }
  ]
}
```

You don't need to process the `compaction` block specially — just append the full response content to your messages array and continue the conversation normally.

## Important considerations

**Compaction and tool use**: When using compaction with tools, the `compaction` block will appear before any tool use or text blocks in the response.

**Cost**: Compaction generates additional tokens for the summary, which are billed at standard output rates. The overall cost savings come from reduced input tokens in subsequent requests.

**Accuracy**: Compaction summarizes older context. Some fine-grained details from earlier in the conversation may be condensed. For tasks requiring exact recall of all previous content, consider alternative context management strategies.

**When compaction doesn't trigger**: If input tokens don't exceed the trigger threshold, compaction won't occur and the response is a standard text response.
