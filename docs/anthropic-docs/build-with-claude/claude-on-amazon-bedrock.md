---
source: https://platform.claude.com/docs/en/build-with-claude/claude-on-amazon-bedrock
scraped: 2026-03-23
section: build-with-claude
---

# Claude on Amazon Bedrock

Anthropic's Claude models are now generally available through Amazon Bedrock.

---

Calling Claude through Bedrock slightly differs from how you would call Claude when using Anthropic's client SDKs. This guide walks you through completing an API call to Claude on Bedrock using one of Anthropic's client SDKs.

Note that this guide assumes you have already signed up for an AWS account and configured programmatic access.

## Install and configure the AWS CLI

1. Install a version of the AWS CLI at or newer than version `2.13.23`
2. Configure your AWS credentials using the AWS configure command or find your credentials by navigating to "Command line or programmatic access" within your AWS dashboard
3. Verify that your credentials are working:

```bash Shell
aws sts get-caller-identity
```

## Install an SDK for accessing Bedrock

```bash Python
pip install -U "anthropic[bedrock]"
```

```bash TypeScript
npm install @anthropic-ai/bedrock-sdk
```

## Accessing Bedrock

### Subscribe to Anthropic models

Go to the AWS Console > Bedrock > Model Access and request access to Anthropic models. Note that Anthropic model availability varies by region.

#### API model IDs

| Model | Base Bedrock model ID | `global` | `us` | `eu` | `jp` | `apac` |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Claude Opus 4.6 | anthropic.claude-opus-4-6-v1 | Yes | Yes | Yes | Yes | Yes |
| Claude Sonnet 4.6 | anthropic.claude-sonnet-4-6 | Yes | Yes | Yes | Yes | No |
| Claude Sonnet 4.5 | anthropic.claude-sonnet-4-5-20250929-v1:0 | Yes | Yes | Yes | Yes | No |
| Claude Sonnet 4 | anthropic.claude-sonnet-4-20250514-v1:0 | Yes | Yes | Yes | No | Yes |
| Claude Opus 4.5 | anthropic.claude-opus-4-5-20251101-v1:0 | Yes | Yes | Yes | No | No |
| Claude Opus 4.1 | anthropic.claude-opus-4-1-20250805-v1:0 | No | Yes | No | No | No |
| Claude Opus 4 | anthropic.claude-opus-4-20250514-v1:0 | No | Yes | No | No | No |
| Claude Haiku 4.5 | anthropic.claude-haiku-4-5-20251001-v1:0 | Yes | Yes | Yes | No | No |

### Making requests

```python Python
from anthropic import AnthropicBedrock

client = AnthropicBedrock(
    aws_access_key="<access key>",
    aws_secret_key="<secret key>",
    aws_session_token="<session_token>",
    aws_region="us-west-2",
)

message = client.messages.create(
    model="global.anthropic.claude-opus-4-6-v1",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello, world"}],
)
print(message.content)
```

```typescript TypeScript
import AnthropicBedrock from "@anthropic-ai/bedrock-sdk";

const client = new AnthropicBedrock({
  awsAccessKey: "<access key>",
  awsSecretKey: "<secret key>",
  awsSessionToken: "<session_token>",
  awsRegion: "us-west-2"
});

const message = await client.messages.create({
  model: "global.anthropic.claude-opus-4-6-v1",
  max_tokens: 256,
  messages: [{ role: "user", content: "Hello, world" }]
});
console.log(message);
```

### Bearer token authentication

You can authenticate with Bedrock using bearer tokens instead of AWS credentials. Set the `AWS_BEARER_TOKEN_BEDROCK` environment variable, which is automatically detected by `fromEnv()` credential resolution.

## Activity logging

Bedrock provides an invocation logging service that allows customers to log the prompts and completions associated with your usage.

Anthropic recommends that you log your activity on at least a 30-day rolling basis in order to understand your activity and investigate any potential misuse.

> Turning on this service does not give AWS or Anthropic any access to your content.

## Feature support

For all currently supported features on Bedrock, see the API features overview documentation.

### Context window

Claude Opus 4.6, Sonnet 4.6, Sonnet 4.5, and Sonnet 4 have a 1M-token context window on Amazon Bedrock.

> For Claude Sonnet 4.5 and Sonnet 4, the 1M-token context window is in beta. Include the `context-1m-2025-08-07` beta header in your Bedrock API requests.

Amazon Bedrock limits request payloads to 20 MB. When sending large documents or many images, you may reach this limit before the token limit.

## Global vs regional endpoints

Starting with **Claude Sonnet 4.5 and all future models**, Amazon Bedrock offers two endpoint types:

- **Global endpoints:** Dynamic routing for maximum availability
- **Regional endpoints:** Guaranteed data routing through specific geographic regions

Regional endpoints include a 10% pricing premium over global endpoints.

### Implementation

**Using global endpoints:**

```python Python
from anthropic import AnthropicBedrock

client = AnthropicBedrock(aws_region="us-west-2")

message = client.messages.create(
    model="global.anthropic.claude-opus-4-6-v1",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello, world"}],
)
```

**Using regional endpoints:**

Remove the `global.` prefix from the model ID:

```python Python
from anthropic import AnthropicBedrock

client = AnthropicBedrock(aws_region="us-west-2")

# Using US regional endpoint (CRIS)
message = client.messages.create(
    model="anthropic.claude-opus-4-6-v1",  # No global. prefix
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello, world"}],
)
```

### Additional resources

- **AWS Bedrock pricing:** [aws.amazon.com/bedrock/pricing](https://aws.amazon.com/bedrock/pricing/)
- **Anthropic pricing details:** See Pricing documentation for third-party platform pricing
