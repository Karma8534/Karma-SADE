---
source: https://platform.claude.com/docs/en/api/sdks/python
scraped: 2026-03-23
section: api
---

# Python SDK

Install and configure the Anthropic Python SDK with sync and async client support

---

The Anthropic Python SDK provides convenient access to the Anthropic REST API from Python applications. It supports both synchronous and asynchronous operations, streaming, and integrations with AWS Bedrock and Google Vertex AI.

<Info>
For API feature documentation with code examples, see the [API reference](/docs/en/api/overview). This page covers Python-specific SDK features and configuration.
</Info>

## Installation

```bash
pip install anthropic
```

For platform-specific integrations, install with extras:

```bash
# For AWS Bedrock support
pip install anthropic[bedrock]

# For Google Vertex AI support
pip install anthropic[vertex]

# For improved async performance with aiohttp
pip install anthropic[aiohttp]
```

## Requirements

Python 3.9 or later is required.

## Usage

```python
import os
from anthropic import Anthropic

client = Anthropic(
    # This is the default and can be omitted
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)

message = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-opus-4-6",
)
print(message.content)
```

## Async usage

```python
import os
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


async def main() -> None:
    message = await client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello, Claude",
            }
        ],
        model="claude-opus-4-6",
    )
    print(message.content)


asyncio.run(main())
```

### Using aiohttp for better concurrency

For improved async performance, you can use the `aiohttp` HTTP backend instead of the default `httpx`:

```python
import os
import asyncio
from anthropic import AsyncAnthropic, DefaultAioHttpClient


async def main() -> None:
    async with AsyncAnthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY"),
        http_client=DefaultAioHttpClient(),
    ) as client:
        message = await client.messages.create(
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": "Hello, Claude",
                }
            ],
            model="claude-opus-4-6",
        )
        print(message.content)


asyncio.run(main())
```

## Streaming responses

The SDK provides support for streaming responses using Server-Sent Events (SSE).

```python
from anthropic import Anthropic

client = Anthropic()

stream = client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-opus-4-6",
    stream=True,
)
for event in stream:
    print(event.type)
```

The async client uses the exact same interface:

```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic()

stream = await client.messages.create(
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": "Hello, Claude",
        }
    ],
    model="claude-opus-4-6",
    stream=True,
)
async for event in stream:
    print(event.type)
```

### Streaming helpers

The SDK also provides streaming helpers that use context managers and provide access to the accumulated text and the final message:

```python
import asyncio
from anthropic import AsyncAnthropic

client = AsyncAnthropic()


async def main() -> None:
    async with client.messages.stream(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Say hello there!",
            }
        ],
        model="claude-opus-4-6",
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
        print()

        message = await stream.get_final_message()
        print(message.to_json())


asyncio.run(main())
```

## Token counting

You can see the exact usage for a given request through the `usage` response property:

```python
message = client.messages.create(...)
print(message.usage)
# Usage(input_tokens=25, output_tokens=13)
```

You can also count tokens before making a request:

```python
count = client.messages.count_tokens(
    model="claude-opus-4-6", messages=[{"role": "user", "content": "Hello, world"}]
)
print(count.input_tokens)  # 10
```

## Tool use

This SDK provides support for tool use, also known as function calling. More details can be found in the [tool use overview](/docs/en/agents-and-tools/tool-use/overview).

### Tool helpers

The SDK provides helpers for defining and running tools as pure Python functions. You can use the `@beta_tool` decorator for more control:

```python
import json
from anthropic import Anthropic, beta_tool

client = Anthropic()


@beta_tool
def get_weather(location: str) -> str:
    """Get the weather for a given location.

    Args:
        location: The city and state, e.g. San Francisco, CA
    Returns:
        A dictionary containing the location, temperature, and weather condition.
    """
    return json.dumps(
        {
            "location": location,
            "temperature": "68°F",
            "condition": "Sunny",
        }
    )


# Use the tool_runner to automatically handle tool calls
runner = client.beta.messages.tool_runner(
    max_tokens=1024,
    model="claude-opus-4-6",
    tools=[get_weather],
    messages=[
        {"role": "user", "content": "What is the weather in SF?"},
    ],
)
for message in runner:
    print(message)
```

## Message batches

This SDK provides support for the [Message Batches API](/docs/en/build-with-claude/batch-processing) under `client.messages.batches`.

### Creating a batch

```python
client.messages.batches.create(
    requests=[
        {
            "custom_id": "my-first-request",
            "params": {
                "model": "claude-opus-4-6",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Hello, world"}],
            },
        },
        {
            "custom_id": "my-second-request",
            "params": {
                "model": "claude-opus-4-6",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": "Hi again, friend"}],
            },
        },
    ]
)
```

### Getting results from a batch

```python
import anthropic

client = anthropic.Anthropic()
batch_id = "batch_abc123"
result_stream = client.messages.batches.results(batch_id)
for entry in result_stream:
    if entry.result.type == "succeeded":
        print(entry.result.message.content)
```

## File uploads

Request parameters that correspond to file uploads can be passed in many different forms:

- A `PathLike` object (e.g., `pathlib.Path`)
- A tuple of `(filename, content, content_type)`
- A `BinaryIO` file-like object
- The return value of the `toFile` helper

```python
from pathlib import Path
from anthropic import Anthropic

client = Anthropic()

# Upload using a file path
client.beta.files.upload(
    file=Path("/path/to/file"),
    betas=["files-api-2025-04-14"],
)

# Upload using bytes
client.beta.files.upload(
    file=("file.txt", b"my bytes", "text/plain"),
    betas=["files-api-2025-04-14"],
)
```

## Handling errors

When the library is unable to connect to the API, or if the API returns a non-success status code (i.e., 4xx or 5xx response), a subclass of `APIError` is raised:

```python
import anthropic
from anthropic import Anthropic

client = Anthropic()

try:
    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello, Claude",
            }
        ],
        model="claude-opus-4-6",
    )
except anthropic.APIConnectionError as e:
    print("The server could not be reached")
    print(e.__cause__)  # an underlying Exception, likely raised within httpx
except anthropic.RateLimitError as e:
    print("A 429 status code was received; we should back off a bit.")
except anthropic.APIStatusError as e:
    print("Another non-200-range status code was received")
    print(e.status_code)
    print(e.response)
```

Error codes are as follows:

| Status Code | Error Type |
|-------------|-----------|
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 422 | `UnprocessableEntityError` |
| 429 | `RateLimitError` |
| >=500 | `InternalServerError` |
| N/A | `APIConnectionError` |

## Request IDs

All object responses in the SDK provide a `_request_id` property which is added from the `request-id` response header so that you can quickly log failing requests and report them back to Anthropic.

```python
message = client.messages.create(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
    model="claude-opus-4-6",
)
print(message._request_id)  # e.g., req_018EeWyXxfu5pfWkrYcMdjWG
```

## Retries

Certain errors are automatically retried 2 times by default, with a short exponential backoff. Connection errors (for example, due to a network connectivity problem), 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors are all retried by default.

You can use the `max_retries` option to configure or disable this:

```python
from anthropic import Anthropic

# Configure the default for all requests:
client = Anthropic(
    max_retries=0,  # default is 2
)

# Or, configure per-request:
client.with_options(max_retries=5).messages.create(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
    model="claude-opus-4-6",
)
```

## Timeouts

By default requests time out after 10 minutes. You can configure this with a `timeout` option, which accepts a float or an `httpx.Timeout` object:

```python
import httpx
from anthropic import Anthropic

# Configure the default for all requests:
client = Anthropic(
    timeout=20.0,  # 20 seconds (default is 10 minutes)
)

# More granular control:
client = Anthropic(
    timeout=httpx.Timeout(60.0, read=5.0, write=10.0, connect=2.0),
)

# Override per-request:
client.with_options(timeout=5.0).messages.create(
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
    model="claude-opus-4-6",
)
```

On timeout, an `APITimeoutError` is thrown.

Note that requests which time out will be retried twice by default.

## Auto-pagination

List methods in the Claude API are paginated. You can use the `for` syntax to iterate through items across all pages:

```python
from anthropic import Anthropic

client = Anthropic()

all_batches = []
# Automatically fetches more pages as needed.
for batch in client.messages.batches.list(limit=20):
    all_batches.append(batch)
print(all_batches)
```

## Default headers

The SDK automatically sends the `anthropic-version` header set to `2023-06-01`.

If you need to, you can override it by setting default headers on the client object or per-request.

## Type system

### Request parameters

Nested request parameters are [TypedDicts](https://docs.python.org/3/library/typing.html#typing.TypedDict). Responses are [Pydantic models](https://docs.pydantic.dev) which also have helper methods for things like serializing back into JSON.

### Response models

To convert a Pydantic model to a dictionary, use the helper methods:

```python
message = client.messages.create(...)

# Convert to JSON string
json_str = message.to_json()

# Convert to dictionary
data = message.to_dict()
```

## Beta features

You can access most beta API features through the `beta` property of the client.

```python
from anthropic import Anthropic

client = Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Please summarize this document for me."},
                {
                    "type": "document",
                    "source": {
                        "type": "file",
                        "file_id": "file_abc123",
                    },
                },
            ],
        },
    ],
    betas=["files-api-2025-04-14"],
)
```

## Platform integrations

All three client classes are included in the base `anthropic` package:

| Provider | Client | Extra dependencies |
|-----------|--------|-------------------|
| Bedrock | `from anthropic import AnthropicBedrock` | `pip install anthropic[bedrock]` |
| Vertex AI | `from anthropic import AnthropicVertex` | `pip install anthropic[vertex]` |
| Foundry | `from anthropic import AnthropicFoundry` | None |

## Additional resources

- [GitHub repository](https://github.com/anthropics/anthropic-sdk-python)
- [API reference](/docs/en/api/overview)
- [Streaming guide](/docs/en/build-with-claude/streaming)
- [Tool use guide](/docs/en/agents-and-tools/tool-use/overview)
