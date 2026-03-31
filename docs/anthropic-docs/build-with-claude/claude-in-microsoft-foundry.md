---
source: https://platform.claude.com/docs/en/build-with-claude/claude-in-microsoft-foundry
scraped: 2026-03-23
section: build-with-claude
---

# Claude in Microsoft Foundry

Access Claude models through Microsoft Foundry with Azure-native endpoints and authentication.

---

This guide walks you through the process of setting up and making API calls to Claude in Foundry in Python, TypeScript, or using direct HTTP requests. When you access Claude in Foundry, you are billed for Claude usage in the Microsoft Marketplace with your Azure subscription.

Regional availability: At launch, Claude is available as a Global Standard deployment type in Foundry resources. Pricing uses Anthropic's standard API pricing.

> Foundry is supported by the C#, Java, PHP, Python, and TypeScript SDKs. The Go and Ruby SDKs do not currently support Microsoft Foundry.

## Prerequisites

- An active Azure subscription
- Access to Foundry (ai.azure.com)
- The Azure CLI installed (optional)

## Install an SDK

```bash Python
pip install -U "anthropic"
```

```bash TypeScript
npm install @anthropic-ai/foundry-sdk
```

```bash C#
dotnet add package Anthropic.Foundry
```

## Provisioning

Foundry uses a two-level hierarchy: **resources** contain your security and billing configuration, while **deployments** are the model instances you call via API.

### Provisioning Foundry resources

1. Navigate to the Foundry portal (ai.azure.com)
2. Create a new Foundry resource or select an existing one
3. Configure access management using Azure-issued API keys or Entra ID
4. Note your resource name — used as `{resource}` in API endpoints

### Creating Foundry deployments

1. In the Foundry portal, navigate to your resource
2. Go to **Models + endpoints** and select **+ Deploy model** > **Deploy base model**
3. Search for and select a Claude model (e.g., `claude-sonnet-4-6`)
4. Configure deployment settings including **Deployment name** and **Deployment type** (Global Standard recommended)
5. Select **Deploy** and wait for provisioning to complete

> The deployment name you choose becomes the value you pass in the `model` parameter of your API requests.

## Authentication

### API key authentication

```python Python
import os
from anthropic import AnthropicFoundry

client = AnthropicFoundry(
    api_key=os.environ.get("ANTHROPIC_FOUNDRY_API_KEY"),
    resource="example-resource",
)

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
print(message.content)
```

```typescript TypeScript
import AnthropicFoundry from "@anthropic-ai/foundry-sdk";

const client = new AnthropicFoundry({
  apiKey: process.env.ANTHROPIC_FOUNDRY_API_KEY,
  resource: "example-resource"
});

const message = await client.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello!" }]
});
console.log(message.content);
```

```bash Shell
curl https://{resource}.services.ai.azure.com/anthropic/v1/messages \
  -H "content-type: application/json" \
  -H "api-key: YOUR_AZURE_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'
```

### Microsoft Entra authentication

```python Python
import os
from anthropic import AnthropicFoundry
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

token_provider = get_bearer_token_provider(
    DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
)

client = AnthropicFoundry(
    resource="example-resource",
    azure_ad_token_provider=token_provider,
)

message = client.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
print(message.content)
```

## API model IDs and deployments

| Model             | Default Deployment Name     |
| :---------------- | :-------------------------- |
| Claude Opus 4.6   | `claude-opus-4-6`           |
| Claude Opus 4.5   | `claude-opus-4-5`           |
| Claude Sonnet 4.6 | `claude-sonnet-4-6`         |
| Claude Sonnet 4.5 | `claude-sonnet-4-5`         |
| Claude Opus 4.1   | `claude-opus-4-1`           |
| Claude Haiku 4.5  | `claude-haiku-4-5`          |

## Context window

Claude Opus 4.6, Sonnet 4.6, and Sonnet 4.5 have a 1M-token context window on Microsoft Foundry.

## Features not supported

- Admin API (`/v1/organizations/*` endpoints)
- Models API (`/v1/models`)
- Message Batch API (`/v1/messages/batches`)

## Correlation request IDs

Foundry includes request identifiers in HTTP response headers for debugging. When contacting support, provide both the `request-id` and `apim-request-id` values.

> Foundry does not include Anthropic's standard rate limit headers. Manage rate limiting through Azure's monitoring tools instead.

## Additional resources

- **Foundry documentation:** [ai.azure.com/catalog](https://ai.azure.com/catalog/publishers/anthropic)
- **Azure pricing:** [azure.microsoft.com/en-us/pricing](https://azure.microsoft.com/en-us/pricing/)
