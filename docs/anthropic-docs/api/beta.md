---
source: https://platform.claude.com/docs/en/api/beta
scraped: 2026-03-23
section: api
---

# Beta

## Available Beta API Versions

Access beta features by including the `anthropic-beta` header in your requests. Multiple beta features can be enabled simultaneously.

### Current Beta Headers

| Beta Header | Feature |
|-------------|---------|
| `message-batches-2024-09-24` | Batch message processing |
| `prompt-caching-2024-07-31` | Prompt caching |
| `computer-use-2024-10-22` | Computer use capabilities |
| `computer-use-2025-01-24` | Updated computer use |
| `pdfs-2024-09-25` | PDF document support |
| `token-counting-2024-11-01` | Token counting |
| `token-efficient-tools-2025-02-19` | Efficient tool usage |
| `output-128k-2025-02-19` | 128K output tokens |
| `files-api-2025-04-14` | Files API |
| `mcp-client-2025-04-04` | MCP client support |
| `mcp-client-2025-11-20` | Updated MCP client |
| `dev-full-thinking-2025-05-14` | Full thinking mode |
| `interleaved-thinking-2025-05-14` | Interleaved thinking |
| `code-execution-2025-05-22` | Code execution |
| `extended-cache-ttl-2025-04-11` | Extended cache TTL |
| `context-1m-2025-08-07` | 1M context window |
| `context-management-2025-06-27` | Context management |
| `model-context-window-exceeded-2025-08-26` | Context overflow handling |
| `skills-2025-10-02` | Skills framework |
| `fast-mode-2026-02-01` | Fast mode |

## Beta Messages API

The beta namespace allows access to beta features through the Messages API.

### Create Message (Beta)

**post** `/v1/messages` with beta headers

The beta Messages API supports additional content block types and parameters not yet in general availability.

Additional content blocks available in beta:
- `BetaContainerUploadBlockParam` — Files for container upload
- Extended thinking blocks
- Additional tool types (code execution, bash, text editor, web search, web fetch, memory)

### Usage Example

```python
import anthropic

client = anthropic.Anthropic()

# Using Files API (beta)
response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Please summarize this document."},
                {
                    "type": "document",
                    "source": {"type": "file", "file_id": "file_abc123"},
                },
            ],
        }
    ],
    betas=["files-api-2025-04-14"],
)
```

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const response = await client.beta.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [
    {
      role: "user",
      content: [
        { type: "text", text: "Please summarize this document." },
        { type: "document", source: { type: "file", file_id: "file_abc123" } }
      ]
    }
  ],
  betas: ["files-api-2025-04-14"]
});
```

## Beta Files API

**post** `/v1/files` (requires `files-api-2025-04-14` beta header)

Upload and manage files for use across multiple API calls. Files can be referenced in messages without re-uploading.

## Beta Skills API

**post** `/v1/skills` (requires `skills-2025-10-02` beta header)

Create and manage custom agent skills.

## Error Types

The API returns standard error objects:

| Type | Meaning |
|------|---------|
| `invalid_request_error` | Invalid request parameters |
| `authentication_error` | Authentication failed |
| `billing_error` | Billing issue |
| `permission_error` | Insufficient permissions |
| `not_found_error` | Resource not found |
| `rate_limit_error` | Rate limit exceeded |
| `timeout_error` | Request timeout |
| `api_error` | General API error |
| `overloaded_error` | Service overloaded |

## See Also

- [Beta headers](/docs/en/api/beta-headers) — Complete list of beta feature headers
- [Files](/docs/en/build-with-claude/files) — Files API guide
- [Build with Claude overview](/docs/en/build-with-claude/overview) — Feature availability
