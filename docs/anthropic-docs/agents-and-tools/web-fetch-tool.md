---
source: https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-fetch-tool
scraped: 2026-03-23
section: agents-and-tools
---

# Web fetch tool

The web fetch tool allows Claude to retrieve full content from specified web pages and PDF documents.

The latest web fetch tool version (`web_fetch_20260209`) supports **dynamic filtering** with Claude Opus 4.6 and Sonnet 4.6. Claude can write and execute code to filter fetched content before it reaches the context window, keeping only relevant information and discarding the rest. The previous tool version (`web_fetch_20250910`) remains available without dynamic filtering.

> **Warning**: Enabling the web fetch tool in environments where Claude processes untrusted input alongside sensitive data poses data exfiltration risks. Only use this tool in trusted environments or when handling non-sensitive data.
>
> To minimize exfiltration risks:
> - Claude is not allowed to dynamically construct URLs. Claude can only fetch URLs explicitly provided by the user or from previous web search/web fetch results.
> - Consider disabling the web fetch tool entirely if data exfiltration is a concern
> - Use the `max_uses` parameter to limit requests
> - Use the `allowed_domains` parameter to restrict to known safe domains

## Supported models

Web fetch is available on:

- Claude Opus 4.6 (`claude-opus-4-6`)
- Claude Opus 4.5 (`claude-opus-4-5-20251101`)
- Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- Claude Opus 4 (`claude-opus-4-20250514`)
- Claude Sonnet 4.6 (`claude-sonnet-4-6`)
- Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Claude Sonnet 3.7 (deprecated) (`claude-3-7-sonnet-20250219`)
- Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- Claude Haiku 3.5 (deprecated) (`claude-3-5-haiku-latest`)

## How web fetch works

When you add the web fetch tool to your API request:

1. Claude decides when to fetch content based on the prompt and available URLs.
2. The API retrieves the full text content from the specified URL.
3. For PDFs, automatic text extraction is performed.
4. Claude analyzes the fetched content and provides a response with optional citations.

> The web fetch tool currently does not support websites dynamically rendered via JavaScript.

### Dynamic filtering with Opus 4.6 and Sonnet 4.6

With the `web_fetch_20260209` tool version, Claude can write and execute code to filter the fetched content before loading it into context. Dynamic filtering requires the code execution tool to be enabled.

## How to use web fetch

Provide the web fetch tool in your API request:

```bash Shell
curl https://api.anthropic.com/v1/messages \
    --header "x-api-key: $ANTHROPIC_API_KEY" \
    --header "anthropic-version: 2023-06-01" \
    --header "content-type: application/json" \
    --data '{
        "model": "claude-opus-4-6",
        "max_tokens": 1024,
        "messages": [
            {
                "role": "user",
                "content": "Please analyze the content at https://example.com/article"
            }
        ],
        "tools": [{
            "type": "web_fetch_20250910",
            "name": "web_fetch",
            "max_uses": 5
        }]
    }'
```

```python Python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Please analyze the content at https://example.com/article",
        }
    ],
    tools=[{"type": "web_fetch_20250910", "name": "web_fetch", "max_uses": 5}],
)
print(response)
```

### Tool definition

The web fetch tool supports the following parameters:

```json
{
  "type": "web_fetch_20250910",
  "name": "web_fetch",

  // Optional: Limit the number of fetches per request
  "max_uses": 10,

  // Optional: Only fetch from these domains
  "allowed_domains": ["example.com", "docs.example.com"],

  // Optional: Never fetch from these domains
  "blocked_domains": ["private.example.com"],

  // Optional: Enable citations for fetched content
  "citations": {
    "enabled": true
  },

  // Optional: Maximum content length in tokens
  "max_content_tokens": 100000
}
```

#### Max uses

The `max_uses` parameter limits the number of web fetches performed. There is currently no default limit.

#### Domain filtering

- Domains should not include the HTTP/HTTPS scheme
- Subdomains are automatically included (`example.com` covers `docs.example.com`)
- Subpaths are supported (`example.com/blog`)
- You can use either `allowed_domains` or `blocked_domains`, but not both

> **Warning**: Unicode characters in domain names can create security vulnerabilities through homograph attacks. Use ASCII-only domain names when possible.

#### Content limits

The `max_content_tokens` parameter limits the amount of content included in the context. If the fetched content exceeds this limit, the tool truncates it.

> The `max_content_tokens` parameter limit is approximate. The actual number of input tokens used can vary by a small amount.

#### Citations

Unlike web search where citations are always enabled, citations are optional for web fetch. Set `"citations": {"enabled": true}` to enable citations.

### Response

The response includes:

- `url`: The URL that was fetched
- `content`: A document block containing the fetched content
- `retrieved_at`: Timestamp when the content was retrieved

> The web fetch tool caches results to improve performance and reduce redundant requests. The content returned may not always reflect the latest version available at the URL.

#### Errors

Possible error codes:
- `invalid_input`: Invalid URL format
- `url_too_long`: URL exceeds maximum length (250 characters)
- `url_not_allowed`: URL blocked by domain filtering rules and model restrictions
- `url_not_accessible`: Failed to fetch content (HTTP error)
- `too_many_requests`: Rate limit exceeded
- `unsupported_content_type`: Content type not supported (only text and PDF)
- `max_uses_exceeded`: Maximum web fetch tool uses exceeded
- `unavailable`: An internal error occurred

## URL validation

For security reasons, the web fetch tool can only fetch URLs that have previously appeared in the conversation context. This includes:

- URLs in user messages
- URLs in client-side tool results
- URLs from previous web search or web fetch results

The tool cannot fetch arbitrary URLs that Claude generates or URLs from container-based server tools.

## Combined search and fetch

Web fetch works seamlessly with web search for comprehensive information gathering:

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=4096,
    messages=[
        {
            "role": "user",
            "content": "Find recent articles about quantum computing and analyze the most relevant one in detail",
        }
    ],
    tools=[
        {"type": "web_search_20250305", "name": "web_search", "max_uses": 3},
        {
            "type": "web_fetch_20250910",
            "name": "web_fetch",
            "max_uses": 5,
            "citations": {"enabled": True},
        },
    ],
)
```

## Usage and pricing

Web fetch usage has **no additional charges** beyond standard token costs:

- Average web page (10 kB): ~2,500 tokens
- Large documentation page (100 kB): ~25,000 tokens
- Research paper PDF (500 kB): ~125,000 tokens

Use the `max_content_tokens` parameter to set appropriate limits based on your use case and budget.
