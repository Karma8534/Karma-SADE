---
source: https://platform.claude.com/docs/en/build-with-claude/deployments/claude-on-vertex-ai
scraped: 2026-03-23
section: build-with-claude
---

# Claude on Google Cloud Vertex AI

Anthropic's Claude models are available on Google Cloud Vertex AI. This guide walks you through making API calls to Claude on Vertex AI using Anthropic's client SDKs.

## Install an SDK for accessing Vertex AI

```bash
pip install -U "anthropic[vertex]"
```

```bash
npm install @anthropic-ai/vertex-sdk
```

## Authentication

Configure Google Cloud authentication using Application Default Credentials (ADC):

```bash
gcloud auth application-default login
```

## Making requests

```python
from anthropic import AnthropicVertex

client = AnthropicVertex(
    project_id="your-project-id",
    region="us-east5",
)

message = client.messages.create(
    model="claude-opus-4-6@20250514",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
)
print(message.content)
```

```typescript
import { AnthropicVertex } from "@anthropic-ai/vertex-sdk";

const client = new AnthropicVertex({
  projectId: "your-project-id",
  region: "us-east5",
});

const message = await client.messages.create({
  model: "claude-opus-4-6@20250514",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello, Claude" }],
});
console.log(message);
```

## Available regions

Claude models are available in specific Vertex AI regions. Check the Google Cloud documentation for current regional availability.

## Model IDs

Vertex AI model IDs use the format `model-name@version`, for example:
- `claude-opus-4-6@20250514`
- `claude-sonnet-4-6@20250514`
- `claude-haiku-4-5@20251001`

## Feature support

For all currently supported features on Vertex AI, see the API features overview. Some features like the Files API are not available on third-party platforms.

## Pricing

Vertex AI uses Google Cloud consumption pricing. See the Vertex AI pricing page for current Claude rates.
