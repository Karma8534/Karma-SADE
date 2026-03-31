---
source: https://platform.claude.com/docs/en/api/sdks/csharp
scraped: 2026-03-23
section: api
---

# C# SDK

Install and configure the Anthropic C# SDK for .NET applications with IChatClient integration

---

The Anthropic C# SDK provides convenient access to the Anthropic REST API from applications written in C#.

> The C# SDK is currently in beta. APIs may change between versions.

> As of version 10+, the `Anthropic` package is now the official Anthropic SDK for C#. Package versions 3.X and below were previously used for the tryAGI community-built SDK, which has moved to `tryAGI.Anthropic`.

## Installation

Install the package from [NuGet](https://www.nuget.org/packages/Anthropic):

```bash
dotnet add package Anthropic
```

## Requirements

This library requires .NET Standard 2.0 or later.

## Usage

```csharp
using System;
using Anthropic;
using Anthropic.Models.Messages;

AnthropicClient client = new();

MessageCreateParams parameters = new()
{
    MaxTokens = 1024,
    Messages =
    [
        new()
        {
            Role = Role.User,
            Content = "Hello, Claude",
        },
    ],
    Model = "claude-opus-4-6",
};

var message = await client.Messages.Create(parameters);

Console.WriteLine(message);
```

## Client configuration

Configure the client using environment variables:

```csharp
using Anthropic;

// Configured using the ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN and ANTHROPIC_BASE_URL environment variables
AnthropicClient client = new();
```

Or manually:

```csharp
using Anthropic;

AnthropicClient client = new() { ApiKey = "my-anthropic-api-key" };
```

| Property | Environment variable | Required | Default value |
| ----------- | ---------------------- | -------- | ----------------------------- |
| `ApiKey` | `ANTHROPIC_API_KEY` | false | - |
| `AuthToken` | `ANTHROPIC_AUTH_TOKEN` | false | - |
| `BaseUrl` | `ANTHROPIC_BASE_URL` | true | `"https://api.anthropic.com"` |

## Streaming

```csharp
using System;
using Anthropic.Models.Messages;

MessageCreateParams parameters = new()
{
    MaxTokens = 1024,
    Messages =
    [
        new()
        {
            Role = Role.User,
            Content = "Hello, Claude",
        },
    ],
    Model = "claude-opus-4-6",
};

await foreach (var message in client.Messages.CreateStreaming(parameters))
{
    Console.WriteLine(message);
}
```

## Error handling

The SDK throws custom unchecked exception types:

| Status | Exception |
| ------ | ---------------------------------------- |
| 400 | `AnthropicBadRequestException` |
| 401 | `AnthropicUnauthorizedException` |
| 403 | `AnthropicForbiddenException` |
| 404 | `AnthropicNotFoundException` |
| 422 | `AnthropicUnprocessableEntityException` |
| 429 | `AnthropicRateLimitException` |
| 5xx | `Anthropic5xxException` |
| others | `AnthropicUnexpectedStatusCodeException` |

## Retries

The SDK automatically retries 2 times by default.

```csharp
using Anthropic;

AnthropicClient client = new() { MaxRetries = 3 };
```

## Timeouts

Requests time out after 10 minutes by default.

```csharp
using System;
using Anthropic;

AnthropicClient client = new() { Timeout = TimeSpan.FromSeconds(42) };
```

## Pagination

### Auto-pagination

```csharp
var page = await client.Messages.Batches.List(parameters);
await foreach (var item in page.Paginate())
{
    Console.WriteLine(item);
}
```

### Manual pagination

```csharp
var page = await client.Messages.Batches.List();
while (true)
{
    foreach (var item in page.Items)
    {
        Console.WriteLine(item);
    }
    if (!page.HasNext())
    {
        break;
    }
    page = await page.Next();
}
```

## IChatClient integration

The SDK provides an implementation of the `IChatClient` interface from the `Microsoft.Extensions.AI.Abstractions` library.

```csharp
using Anthropic;
using Microsoft.Extensions.AI;
using ModelContextProtocol.Client;

IChatClient chatClient = client.AsIChatClient("claude-opus-4-6")
    .AsBuilder()
    .UseFunctionInvocation()
    .Build();

McpClient learningServer = await McpClient.CreateAsync(
    new HttpClientTransport(new() { Endpoint = new("https://learn.microsoft.com/api/mcp") }));

ChatOptions options = new() { Tools = [.. await learningServer.ListToolsAsync()] };

Console.WriteLine(await chatClient.GetResponseAsync("Tell me about IChatClient", options));
```

## Platform integrations

The C# SDK supports Bedrock and Foundry through separate NuGet packages:

- **Bedrock:** `Anthropic.Bedrock`. Uses `AnthropicBedrockClient` with `AnthropicBedrockCredentialsHelper.FromEnv()` or explicit credentials.
- **Foundry:** `Anthropic.Foundry`. Uses `AnthropicFoundryClient` with `DefaultAnthropicFoundryCredentials.FromEnv()` or explicit credentials.

## Additional resources

- [GitHub repository](https://github.com/anthropics/anthropic-sdk-csharp)
- [NuGet package](https://www.nuget.org/packages/Anthropic)
- [API reference](/docs/en/api/overview)
- [Streaming guide](/docs/en/build-with-claude/streaming)
