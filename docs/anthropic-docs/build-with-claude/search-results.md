---
source: https://platform.claude.com/docs/en/build-with-claude/search-results
scraped: 2026-03-23
section: build-with-claude
---

# Search results

Enable natural citations for RAG applications by providing search results with source attribution

---

Search result content blocks enable natural citations with proper source attribution, bringing web search-quality citations to your custom applications. This feature is particularly powerful for RAG (Retrieval-Augmented Generation) applications where you need Claude to cite sources accurately.

The search results feature is available on the following models:

- Claude Opus 4.6 (`claude-opus-4-6`)
- Claude Sonnet 4.6 (`claude-sonnet-4-6`)
- Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`)
- Claude Opus 4.5 (`claude-opus-4-5-20251101`)
- Claude Opus 4.1 (`claude-opus-4-1-20250805`)
- Claude Opus 4 (`claude-opus-4-20250514`)
- Claude Sonnet 4 (`claude-sonnet-4-20250514`)
- Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)

## Key benefits

- **Natural citations** - Achieve the same citation quality as web search for any content
- **Flexible integration** - Use in tool returns for dynamic RAG or as top-level content for pre-fetched data
- **Proper source attribution** - Each result includes source and title information for clear attribution
- **No document workarounds needed** - Eliminates the need for document-based workarounds
- **Consistent citation format** - Matches the citation quality and format of Claude's web search functionality

## How it works

Search results can be provided in two ways:

1. **From tool calls** - Your custom tools return search results, enabling dynamic RAG applications
2. **As top-level content** - You provide search results directly in user messages for pre-fetched or cached content

In both cases, Claude can automatically cite information from the search results with proper source attribution.

### Search result schema

```json
{
  "type": "search_result",
  "source": "https://example.com/article",
  "title": "Article Title",
  "content": [
    {
      "type": "text",
      "text": "The actual content of the search result..."
    }
  ],
  "citations": {
    "enabled": true
  }
}
```

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Must be `"search_result"` |
| `source` | string | The source URL or identifier for the content |
| `title` | string | A descriptive title for the search result |
| `content` | array | An array of text blocks containing the actual content |

### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `citations` | object | Citation configuration with `enabled` boolean field |
| `cache_control` | object | Cache control settings (e.g., `{"type": "ephemeral"}`) |

## Method 1: Search results from tool calls

The most powerful use case is returning search results from your custom tools. This enables dynamic RAG applications where tools fetch and return relevant content with automatic citations.

```python Python
from anthropic import Anthropic
from anthropic.types import (
    MessageParam,
    TextBlockParam,
    SearchResultBlockParam,
    ToolResultBlockParam,
)

client = Anthropic()

# Define a knowledge base search tool
knowledge_base_tool = {
    "name": "search_knowledge_base",
    "description": "Search the company knowledge base for information",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "The search query"}},
        "required": ["query"],
    },
}


# Function to handle the tool call
def search_knowledge_base(query):
    return [
        SearchResultBlockParam(
            type="search_result",
            source="https://docs.company.com/product-guide",
            title="Product Configuration Guide",
            content=[
                TextBlockParam(
                    type="text",
                    text="To configure the product, navigate to Settings > Configuration. The default timeout is 30 seconds.",
                )
            ],
            citations={"enabled": True},
        ),
    ]


# Create a message with the tool
response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    tools=[knowledge_base_tool],
    messages=[
        MessageParam(role="user", content="How do I configure the timeout settings?")
    ],
)

# When Claude calls the tool, provide the search results
if response.content[0].type == "tool_use":
    tool_result = search_knowledge_base(response.content[0].input["query"])

    # Send the tool result back
    final_response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[
            MessageParam(role="user", content="How do I configure the timeout settings?"),
            MessageParam(role="assistant", content=response.content),
            MessageParam(
                role="user",
                content=[
                    ToolResultBlockParam(
                        type="tool_result",
                        tool_use_id=response.content[0].id,
                        content=tool_result,
                    )
                ],
            ),
        ],
    )
```

## Method 2: Search results as top-level content

For pre-fetched or cached content, you can include search results directly in your user messages. This is ideal for pre-processing content before sending it to Claude.

```python Python
from anthropic import Anthropic
from anthropic.types import SearchResultBlockParam, TextBlockParam

client = Anthropic()

# Pre-fetched search results
search_results = [
    SearchResultBlockParam(
        type="search_result",
        source="https://docs.example.com/api",
        title="API Documentation",
        content=[
            TextBlockParam(
                type="text",
                text="The API rate limit is 1000 requests per minute. Exceeding this limit returns a 429 status code.",
            )
        ],
        citations={"enabled": True},
    )
]

response = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                *search_results,
                {"type": "text", "text": "What is the API rate limit?"},
            ],
        }
    ],
)

print(response.content)
```

## Example response with citations

When search results are provided with citations enabled, Claude will cite the sources in its response:

```json
{
  "content": [
    {
      "type": "text",
      "text": "According to the documentation, "
    },
    {
      "type": "text",
      "text": "the API rate limit is 1000 requests per minute",
      "citations": [
        {
          "type": "search_result_location",
          "source": "https://docs.example.com/api",
          "title": "API Documentation",
          "cited_text": "The API rate limit is 1000 requests per minute."
        }
      ]
    }
  ]
}
```
