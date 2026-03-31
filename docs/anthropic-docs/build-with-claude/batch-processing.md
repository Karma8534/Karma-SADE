---
source: https://platform.claude.com/docs/en/build-with-claude/batch-processing
scraped: 2026-03-23
section: build-with-claude
---

# Batch processing

---

Batch processing is a powerful approach for handling large volumes of requests efficiently. Instead of processing requests one at a time with immediate responses, batch processing allows you to submit multiple requests together for asynchronous processing. This pattern is particularly useful when:

- You need to process large volumes of data
- Immediate responses are not required
- You want to optimize for cost efficiency
- You're running large-scale evaluations or analyses

The Message Batches API is Anthropic's first implementation of this pattern.

> **Note**: This feature is **not** eligible for Zero Data Retention (ZDR). Data is retained according to the feature's standard retention policy.

---

# Message Batches API

The Message Batches API is a powerful, cost-effective way to asynchronously process large volumes of Messages requests. This approach is well-suited to tasks that do not require immediate responses, with most batches finishing in less than 1 hour while reducing costs by 50% and increasing throughput.

## How the Message Batches API works

When you send a request to the Message Batches API:

1. The system creates a new Message Batch with the provided Messages requests.
2. The batch is then processed asynchronously, with each request handled independently.
3. You can poll for the status of the batch and retrieve results when processing has ended for all requests.

This is especially useful for bulk operations that don't require immediate results, such as:
- Large-scale evaluations: Process thousands of test cases efficiently.
- Content moderation: Analyze large volumes of user-generated content asynchronously.
- Data analysis: Generate insights or summaries for large datasets.
- Bulk content generation: Create large amounts of text for various purposes.

### Batch limitations
- A Message Batch is limited to either 100,000 Message requests or 256 MB in size, whichever is reached first.
- The system processes each batch as fast as possible, with most batches completing within 1 hour.
- Batch results are available for 29 days after creation.
- Batches are scoped to a Workspace.

### Supported models

All active models support the Message Batches API.

### What can be batched
Any request that you can make to the Messages API can be included in a batch. This includes:

- Vision
- Tool use
- System messages
- Multi-turn conversations
- Any beta features

## Pricing

The Batches API offers significant cost savings. All usage is charged at 50% of the standard API prices.

| Model | Batch input | Batch output |
|-------|-------------|--------------|
| Claude Opus 4.6 | $2.50 / MTok | $12.50 / MTok |
| Claude Opus 4.5 | $2.50 / MTok | $12.50 / MTok |
| Claude Sonnet 4.6 | $1.50 / MTok | $7.50 / MTok |
| Claude Sonnet 4.5 | $1.50 / MTok | $7.50 / MTok |
| Claude Haiku 4.5 | $0.50 / MTok | $2.50 / MTok |

## How to use the Message Batches API

### Prepare and create your batch

A Message Batch is composed of a list of requests to create a Message. The shape of an individual request is comprised of:
- A unique `custom_id` for identifying the Messages request
- A `params` object with the standard Messages API parameters

```bash Shell
curl https://api.anthropic.com/v1/messages/batches \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "requests": [
        {
            "custom_id": "my-first-request",
            "params": {
                "model": "claude-opus-4-6",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": "Hello, world"}
                ]
            }
        },
        {
            "custom_id": "my-second-request",
            "params": {
                "model": "claude-opus-4-6",
                "max_tokens": 1024,
                "messages": [
                    {"role": "user", "content": "Hi again, friend"}
                ]
            }
        }
    ]
}'
```

```python Python
import anthropic
from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
from anthropic.types.messages.batch_create_params import Request

client = anthropic.Anthropic()

message_batch = client.messages.batches.create(
    requests=[
        Request(
            custom_id="my-first-request",
            params=MessageCreateParamsNonStreaming(
                model="claude-opus-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": "Hello, world"}],
            ),
        ),
        Request(
            custom_id="my-second-request",
            params=MessageCreateParamsNonStreaming(
                model="claude-opus-4-6",
                max_tokens=1024,
                messages=[{"role": "user", "content": "Hi again, friend"}],
            ),
        ),
    ]
)

print(message_batch)
```

### Check batch status

```python Python
import anthropic

client = anthropic.Anthropic()

message_batch = client.messages.batches.retrieve("msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d")
print(message_batch)
```

### Retrieving batch results

Once a batch has `processing_status: "ended"`, you can retrieve the results:

```python Python
import anthropic

client = anthropic.Anthropic()

for result in client.messages.batches.results("msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d"):
    match result.result.type:
        case "succeeded":
            print(f"Success! {result.custom_id}")
            print(result.result.message.content)
        case "errored":
            if result.result.error.type == "invalid_request":
                print(f"Validation error: {result.custom_id}")
            else:
                print(f"Server error: {result.custom_id}")
        case "expired":
            print(f"Expired: {result.custom_id}")
```

### Listing all batches

```python Python
import anthropic

client = anthropic.Anthropic()

all_batches = []
for batch in client.messages.batches.list():
    all_batches.append(batch)
print(all_batches)
```

### Delete a batch

```python Python
import anthropic

client = anthropic.Anthropic()

delete_result = client.messages.batches.delete("msgbatch_01HkcTjaV5uDC8jWR4ZsDV8d")
print(delete_result)
```

## Tips and best practices

**Use prompt caching**: Since batches can take longer than 5 minutes to process, consider using the 1-hour cache duration with prompt caching for better cache hit rates when processing batches with shared context.

**Unique custom_ids**: Use unique `custom_id` values within a batch to map results back to your original requests.

**Error handling**: Check individual result types (`succeeded`, `errored`, `expired`) when processing batch results.
