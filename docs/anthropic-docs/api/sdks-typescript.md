---
source: https://platform.claude.com/docs/en/api/sdks/typescript
scraped: 2026-03-23
section: api
---

# TypeScript SDK

Install and configure the Anthropic TypeScript SDK for Node.js, Deno, Bun, and browser environments

---

This library provides convenient access to the Anthropic REST API from server-side TypeScript or JavaScript.

<Info>
For API feature documentation with code examples, see the [API reference](/docs/en/api/overview). This page covers TypeScript-specific SDK features and configuration.
</Info>

## Installation

```bash
npm install @anthropic-ai/sdk
```

## Requirements

TypeScript >= 4.9 is supported.

The following runtimes are supported:

- Node.js 20 LTS or later ([non-EOL](https://endoflife.date/nodejs)) versions.
- Deno v1.28.0 or higher.
- Bun 1.0 or later.
- Cloudflare Workers.
- Vercel Edge Runtime.
- Jest 28 or greater with the `"node"` environment (`"jsdom"` is not supported at this time).
- Nitro v2.6 or greater.
- Web browsers: disabled by default to avoid exposing your secret API credentials. Enable browser support by explicitly setting `dangerouslyAllowBrowser` to `true`.

Note that React Native is not supported at this time.

## Usage

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env["ANTHROPIC_API_KEY"] // This is the default and can be omitted
});

const message = await client.messages.create({
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello, Claude" }],
  model: "claude-opus-4-6"
});

console.log(message.content);
```

## Request and response types

This library includes TypeScript definitions for all request params and response fields. You may import and use them like so:

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env["ANTHROPIC_API_KEY"] // This is the default and can be omitted
});

const params: Anthropic.MessageCreateParams = {
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello, Claude" }],
  model: "claude-opus-4-6"
};
const message: Anthropic.Message = await client.messages.create(params);
```

## Counting tokens

You can see the exact usage for a given request through the `usage` response property, e.g.

```typescript
const message = await client.messages.create(/* ... */);
console.log(message.usage);
// { input_tokens: 25, output_tokens: 13 }
```

## Streaming responses

The SDK provides support for streaming responses using Server Sent Events (SSE).

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const stream = await client.messages.create({
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello, Claude" }],
  model: "claude-opus-4-6",
  stream: true
});
for await (const messageStreamEvent of stream) {
  console.log(messageStreamEvent.type);
}
```

If you need to cancel a stream, you can `break` from the loop or call `stream.controller.abort()`.

## Streaming helpers

This library provides several conveniences for streaming messages, for example:

```typescript
import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic();

async function main() {
  const stream = anthropic.messages
    .stream({
      model: "claude-opus-4-6",
      max_tokens: 1024,
      messages: [
        {
          role: "user",
          content: "Say hello there!"
        }
      ]
    })
    .on("text", (text) => {
      console.log(text);
    });

  const message = await stream.finalMessage();
  console.log(message);
}

main();
```

## Tool helpers

This SDK provides helpers for making it easy to create and run tools in the Messages API. You can use Zod schemas or JSON Schemas to describe the input to a tool.

```typescript
import Anthropic from "@anthropic-ai/sdk";

import { betaZodTool } from "@anthropic-ai/sdk/helpers/beta/zod";
import { z } from "zod";

const anthropic = new Anthropic();

const weatherTool = betaZodTool({
  name: "get_weather",
  inputSchema: z.object({
    location: z.string()
  }),
  description: "Get the current weather in a given location",
  run: (input) => {
    return `The weather in ${input.location} is foggy and 60°F`;
  }
});

const finalMessage = await anthropic.beta.messages.toolRunner({
  model: "claude-opus-4-6",
  max_tokens: 1000,
  messages: [{ role: "user", content: "What is the weather in San Francisco?" }],
  tools: [weatherTool]
});
```

### Tool errors

To report an error from a tool back to the model, throw a `ToolError` from the `run` function:

```typescript
import { ToolError } from "@anthropic-ai/sdk/lib/tools/BetaRunnableTool";

const screenshotTool = betaZodTool({
  name: "take_screenshot",
  inputSchema: z.object({ url: z.string() }),
  run: async (input) => {
    if (!isValidUrl(input.url)) {
      throw new ToolError(`Invalid URL: ${input.url}`);
    }
    // ...
  }
});
```

## MCP helpers

This SDK provides helpers for integrating with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers.

```typescript
import Anthropic from "@anthropic-ai/sdk";
import {
  mcpTools,
  mcpMessages,
  mcpResourceToContent,
  mcpResourceToFile
} from "@anthropic-ai/sdk/helpers/beta/mcp";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const anthropic = new Anthropic();

// Connect to an MCP server
const transport = new StdioClientTransport({ command: "mcp-server", args: [] });
const mcpClient = new Client({ name: "my-client", version: "1.0.0" });
await mcpClient.connect(transport);

// Use MCP tools with toolRunner
const { tools } = await mcpClient.listTools();
const runner = await anthropic.beta.messages.toolRunner({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Use the available tools" }],
  tools: mcpTools(tools, mcpClient)
});
```

## Message batches

### Creating a batch

```typescript
await client.messages.batches.create({
  requests: [
    {
      custom_id: "my-first-request",
      params: {
        model: "claude-opus-4-6",
        max_tokens: 1024,
        messages: [{ role: "user", content: "Hello, world" }]
      }
    },
    {
      custom_id: "my-second-request",
      params: {
        model: "claude-opus-4-6",
        max_tokens: 1024,
        messages: [{ role: "user", content: "Hi again, friend" }]
      }
    }
  ]
});
```

### Getting results from a batch

```typescript
const results = await client.messages.batches.results(batch_id);
for await (const entry of results) {
  if (entry.result.type === "succeeded") {
    console.log(entry.result.message.content);
  }
}
```

## File uploads

```typescript
import fs from "fs";
import Anthropic, { toFile } from "@anthropic-ai/sdk";

const client = new Anthropic();

// If you have access to Node `fs` we recommend using `fs.createReadStream()`:
await client.beta.files.upload({
  file: await toFile(fs.createReadStream("/path/to/file"), undefined, {
    type: "application/json"
  }),
  betas: ["files-api-2025-04-14"]
});

// Or if you have the web `File` API you can pass a `File` instance:
await client.beta.files.upload({
  file: new File(["my bytes"], "file.txt", { type: "text/plain" }),
  betas: ["files-api-2025-04-14"]
});
```

## Handling errors

When the library is unable to connect to the API, or if the API returns a non-success status code (i.e., 4xx or 5xx response), a subclass of `APIError` will be thrown:

```typescript
const message = await client.messages
  .create({
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    model: "claude-opus-4-6"
  })
  .catch(async (err) => {
    if (err instanceof Anthropic.APIError) {
      console.log(err.status); // 400
      console.log(err.name); // BadRequestError
      console.log(err.headers); // {server: 'nginx', ...}
    } else {
      throw err;
    }
  });
```

Error codes are as follows:

| Status Code | Error Type |
| ----------- | -------------------------- |
| 400 | `BadRequestError` |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` |
| 404 | `NotFoundError` |
| 422 | `UnprocessableEntityError` |
| 429 | `RateLimitError` |
| >=500 | `InternalServerError` |
| N/A | `APIConnectionError` |

## Request IDs

All object responses in the SDK provide a `_request_id` property:

```typescript
const message = await client.messages.create({
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello, Claude" }],
  model: "claude-opus-4-6"
});
console.log(message._request_id); // req_018EeWyXxfu5pfWkrYcMdjWG
```

## Retries

Certain errors will be automatically retried 2 times by default, with a short exponential backoff. Connection errors, 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors will all be retried by default.

```typescript
// Configure the default for all requests:
const client = new Anthropic({
  maxRetries: 0 // default is 2
});

// Or, configure per-request:
await client.messages.create(
  {
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    model: "claude-opus-4-6"
  },
  { maxRetries: 5 }
);
```

## Timeouts

By default requests time out after 10 minutes. You can configure this with a `timeout` option:

```typescript
// Configure the default for all requests:
const client = new Anthropic({
  timeout: 20 * 1000 // 20 seconds (default is 10 minutes)
});

// Override per-request:
await client.messages.create(
  {
    max_tokens: 1024,
    messages: [{ role: "user", content: "Hello, Claude" }],
    model: "claude-opus-4-6"
  },
  { timeout: 5 * 1000 }
);
```

## Auto-pagination

List methods in the Claude API are paginated.

```typescript
async function fetchAllMessageBatches(params: Record<string, unknown>) {
  const allMessageBatches = [];
  // Automatically fetches more pages as needed.
  for await (const messageBatch of client.messages.batches.list({ limit: 20 })) {
    allMessageBatches.push(messageBatch);
  }
  return allMessageBatches;
}
```

## Logging

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  logLevel: "debug" // Show all log messages
});
```

Available log levels: `'debug'`, `'info'`, `'warn'`, `'error'`, `'off'`

## Platform integrations

The TypeScript SDK supports Bedrock, Vertex AI, and Foundry through separate npm packages:

- **Bedrock:** `npm install @anthropic-ai/bedrock-sdk`: Provides `AnthropicBedrock` client
- **Vertex AI:** `npm install @anthropic-ai/vertex-sdk`: Provides `AnthropicVertex` client
- **Foundry:** `npm install @anthropic-ai/foundry-sdk`: Provides `AnthropicFoundry` client

## Additional resources

- [GitHub repository](https://github.com/anthropics/anthropic-sdk-typescript)
- [API reference](/docs/en/api/overview)
- [Streaming guide](/docs/en/build-with-claude/streaming)
- [Tool use guide](/docs/en/agents-and-tools/tool-use/overview)
