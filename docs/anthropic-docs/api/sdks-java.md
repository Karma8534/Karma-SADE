---
source: https://platform.claude.com/docs/en/api/sdks/java
scraped: 2026-03-23
section: api
---

# Java SDK

Install and configure the Anthropic Java SDK with builder patterns and async support

---

The Anthropic Java SDK provides convenient access to the Anthropic REST API from applications written in Java. It uses the builder pattern for creating requests and supports both synchronous and asynchronous operations.

<Info>
For API feature documentation with code examples, see the [API reference](/docs/en/api/overview). This page covers Java-specific SDK features and configuration.
</Info>

## Installation

### Gradle
```kotlin
implementation("com.anthropic:anthropic-java:2.18.0")
```

### Maven
```xml
<dependency>
    <groupId>com.anthropic</groupId>
    <artifactId>anthropic-java</artifactId>
    <version>2.18.0</version>
</dependency>
```

## Requirements

This library requires Java 8 or later.

## Quick start

```java
import com.anthropic.client.AnthropicClient;
import com.anthropic.client.okhttp.AnthropicOkHttpClient;
import com.anthropic.models.messages.Message;
import com.anthropic.models.messages.MessageCreateParams;
import com.anthropic.models.messages.Model;

// Configures using the `anthropic.apiKey`, `anthropic.authToken` and `anthropic.baseUrl` system properties
// Or configures using the `ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL` environment variables
AnthropicClient client = AnthropicOkHttpClient.fromEnv();

MessageCreateParams params = MessageCreateParams.builder()
  .maxTokens(1024L)
  .addUserMessage("Hello, Claude")
  .model(Model.CLAUDE_OPUS_4_6)
  .build();

Message message = client.messages().create(params);
```

## Client configuration

### API key setup

Configure the client using system properties or environment variables:

```java
AnthropicClient client = AnthropicOkHttpClient.fromEnv();
```

Or configure manually:

```java
AnthropicClient client = AnthropicOkHttpClient.builder()
  .apiKey("my-anthropic-api-key")
  .build();
```

### Configuration options

| Setter | System property | Environment variable | Required | Default value |
| ----------- | --------------------- | ---------------------- | -------- | ----------------------------- |
| `apiKey` | `anthropic.apiKey` | `ANTHROPIC_API_KEY` | false | - |
| `authToken` | `anthropic.authToken` | `ANTHROPIC_AUTH_TOKEN` | false | - |
| `baseUrl` | `anthropic.baseUrl` | `ANTHROPIC_BASE_URL` | true | `"https://api.anthropic.com"` |

## Async usage

The default client is synchronous. To switch to asynchronous execution, call the `async()` method:

```java
import java.util.concurrent.CompletableFuture;

CompletableFuture<Message> message = client.async().messages().create(params);
```

Or create an asynchronous client from the beginning:

```java
import com.anthropic.client.AnthropicClientAsync;
import com.anthropic.client.okhttp.AnthropicOkHttpClientAsync;

AnthropicClientAsync client = AnthropicOkHttpClientAsync.fromEnv();
```

## Streaming

### Synchronous streaming

```java
import com.anthropic.core.http.StreamResponse;
import com.anthropic.models.messages.RawMessageStreamEvent;

try (StreamResponse<RawMessageStreamEvent> streamResponse = client.messages().createStreaming(params)) {
    streamResponse.stream().forEach(chunk -> {
        System.out.println(chunk);
    });
    System.out.println("No more chunks!");
}
```

### Asynchronous streaming

```java
import com.anthropic.core.http.AsyncStreamResponse;
import com.anthropic.models.messages.RawMessageStreamEvent;

client.async().messages().createStreaming(params).subscribe(chunk -> {
    System.out.println(chunk);
});
```

### Streaming with message accumulator

```java
import com.anthropic.helpers.MessageAccumulator;
import com.anthropic.models.messages.Message;

MessageAccumulator messageAccumulator = MessageAccumulator.create();

try (StreamResponse<RawMessageStreamEvent> streamResponse =
         client.messages().createStreaming(createParams)) {
    streamResponse.stream()
            .peek(messageAccumulator::accumulate)
            .flatMap(event -> event.contentBlockDelta().stream())
            .flatMap(deltaEvent -> deltaEvent.delta().text().stream())
            .forEach(textDelta -> System.out.print(textDelta.text()));
}

Message message = messageAccumulator.message();
```

## Tool use

The SDK can derive a tool and its parameters automatically from the structure of an arbitrary Java class.

### Defining tools with annotations

```java
import com.fasterxml.jackson.annotation.JsonClassDescription;
import com.fasterxml.jackson.annotation.JsonPropertyDescription;

@JsonClassDescription("Get the weather in a given location")
static class GetWeather {

  @JsonPropertyDescription("The city and state, e.g. San Francisco, CA")
  public String location;

  @JsonPropertyDescription("The unit of temperature")
  public Unit unit;

  public Weather execute() {
    // implementation
    return new Weather("72°F");
  }
}
```

### Calling tools

```java
MessageCreateParams.Builder createParamsBuilder = MessageCreateParams.builder()
        .model(Model.CLAUDE_OPUS_4_6)
        .maxTokens(2048)
        .addTool(GetWeather.class)
        .addUserMessage("What's the temperature in New York?");
```

## Error handling

The SDK throws custom unchecked exception types:

| Status | Exception |
| ------ | --------- |
| 400 | `BadRequestException` |
| 401 | `UnauthorizedException` |
| 403 | `PermissionDeniedException` |
| 404 | `NotFoundException` |
| 422 | `UnprocessableEntityException` |
| 429 | `RateLimitException` |
| 5xx | `InternalServerException` |
| others | `UnexpectedStatusCodeException` |

```java
import com.anthropic.errors.*;

try {
    Message message = client.messages().create(params);
} catch (RateLimitException e) {
    System.out.println("Rate limited, retry after: " + e.headers());
} catch (UnauthorizedException e) {
    System.out.println("Invalid API key");
} catch (AnthropicServiceException e) {
    System.out.println("API error: " + e.statusCode());
} catch (AnthropicIoException e) {
    System.out.println("Network error: " + e.getMessage());
}
```

## Retries

The SDK automatically retries 2 times by default, with a short exponential backoff between requests.

```java
AnthropicClient client = AnthropicOkHttpClient.builder().fromEnv().maxRetries(4).build();
```

## Timeouts

Requests time out after 10 minutes by default.

```java
AnthropicClient client = AnthropicOkHttpClient.builder()
  .fromEnv()
  .timeout(Duration.ofSeconds(30))
  .build();
```

## Pagination

### Auto-pagination

```java
import com.anthropic.models.messages.batches.MessageBatch;

BatchListPage page = client.messages().batches().list();

// Process as an Iterable
for (MessageBatch batch : page.autoPager()) {
    System.out.println(batch);
}
```

### Manual pagination

```java
BatchListPage page = client.messages().batches().list();
while (true) {
    for (MessageBatch batch : page.items()) {
        System.out.println(batch);
    }

    if (!page.hasNextPage()) {
        break;
    }

    page = page.nextPage();
}
```

## Platform integrations

The Java SDK supports Bedrock, Vertex AI, and Foundry through separate dependencies:

- **Bedrock:** `com.anthropic:anthropic-java-bedrock`: Uses `BedrockBackend.fromEnv()` or `BedrockBackend.builder()`
- **Vertex AI:** `com.anthropic:anthropic-java-vertex`: Uses `VertexBackend.fromEnv()` or `VertexBackend.builder()`
- **Foundry:** `com.anthropic:anthropic-java-foundry`: Uses `FoundryBackend.fromEnv()` or `FoundryBackend.builder()`

## Logging

Enable logging by setting the `ANTHROPIC_LOG` environment variable to `info` or `debug`:

```bash
export ANTHROPIC_LOG=debug
```

## Additional resources

- [GitHub repository](https://github.com/anthropics/anthropic-sdk-java)
- [Javadocs](https://javadoc.io/doc/com.anthropic/anthropic-java)
- [API reference](/docs/en/api/overview)
- [Streaming guide](/docs/en/build-with-claude/streaming)
- [Tool use guide](/docs/en/agents-and-tools/tool-use/overview)
