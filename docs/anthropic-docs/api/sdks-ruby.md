---
source: https://platform.claude.com/docs/en/api/sdks/ruby
scraped: 2026-03-23
section: api
---

# Ruby SDK

Install and configure the Anthropic Ruby SDK with Sorbet types, streaming helpers, and connection pooling

---

The Anthropic Ruby library provides convenient access to the Anthropic REST API from any Ruby 3.2.0+ application. It ships with comprehensive types and docstrings in Yard, RBS, and RBI. The standard library's `net/http` is used as the HTTP transport, with connection pooling via the `connection_pool` gem.

## Installation

To use this gem, install via Bundler by adding the following to your application's `Gemfile`:

```ruby
gem "anthropic", "~> 1.25.0"
```

## Requirements

Ruby 3.2.0 or higher.

## Usage

```ruby
require "anthropic"

anthropic = Anthropic::Client.new(
  api_key: ENV["ANTHROPIC_API_KEY"] # This is the default and can be omitted
)

message = anthropic.messages.create(
  max_tokens: 1024,
  messages: [{role: "user", content: "Hello, Claude"}],
  model: :"claude-opus-4-6"
)

puts(message.content)
```

## Streaming

The SDK provides support for streaming responses using Server-Sent Events (SSE).

```ruby
require "anthropic"
anthropic = Anthropic::Client.new
stream = anthropic.messages.stream(
  max_tokens: 1024,
  messages: [{role: "user", content: "Hello, Claude"}],
  model: :"claude-opus-4-6"
)

stream.each do |message|
  puts(message.type)
end
```

### Streaming helpers

```ruby
require "anthropic"
anthropic = Anthropic::Client.new
stream = anthropic.messages.stream(
  max_tokens: 1024,
  messages: [{role: :user, content: "Say hello there!"}],
  model: :"claude-opus-4-6"
)

stream.text.each do |text|
  print(text)
end
```

## Tool calling

The SDK provides helper mechanisms to define structured data classes for tools:

```ruby
require "anthropic"
anthropic = Anthropic::Client.new
class CalculatorInput < Anthropic::BaseModel
  required :lhs, Float
  required :rhs, Float
  required :operator, Anthropic::InputSchema::EnumOf[:+, :-, :*, :/]
end

class Calculator < Anthropic::BaseTool
  input_schema CalculatorInput

  def call(expr)
    expr.lhs.public_send(expr.operator, expr.rhs)
  end
end

# Automatically handles tool execution loop
anthropic.beta.messages.tool_runner(
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{role: "user", content: "What's 15 * 7?"}],
  tools: [Calculator.new]
).each_message { puts _1.content }
```

## Handling errors

When the library is unable to connect to the API, or if the API returns a non-success status code (i.e., 4xx or 5xx response), a subclass of `Anthropic::Errors::APIError` will be thrown:

```ruby
require "anthropic"
anthropic = Anthropic::Client.new
begin
  message = anthropic.messages.create(
    max_tokens: 1024,
    messages: [{role: "user", content: "Hello, Claude"}],
    model: :"claude-opus-4-6"
  )
rescue Anthropic::Errors::APIConnectionError => e
  puts("The server could not be reached")
  puts(e.cause)
rescue Anthropic::Errors::RateLimitError => e
  puts("A 429 status code was received; we should back off a bit.")
rescue Anthropic::Errors::APIStatusError => e
  puts("Another non-200-range status code was received")
  puts(e.status)
end
```

Error codes are as follows:

| Cause | Error Type |
| ---------------- | -------------------------- |
| HTTP 400 | `BadRequestError` |
| HTTP 401 | `AuthenticationError` |
| HTTP 403 | `PermissionDeniedError` |
| HTTP 404 | `NotFoundError` |
| HTTP 409 | `ConflictError` |
| HTTP 422 | `UnprocessableEntityError` |
| HTTP 429 | `RateLimitError` |
| HTTP >= 500 | `InternalServerError` |
| Other HTTP error | `APIStatusError` |
| Timeout | `APITimeoutError` |
| Network error | `APIConnectionError` |

## Retries

Certain errors will be automatically retried 2 times by default, with a short exponential backoff.

```ruby
# Configure the default for all requests:
anthropic = Anthropic::Client.new(
  max_retries: 0 # default is 2
)

# Or, configure per-request:
anthropic.messages.create(
  max_tokens: 1024,
  messages: [{role: "user", content: "Hello, Claude"}],
  model: :"claude-opus-4-6",
  request_options: {max_retries: 5}
)
```

## Timeouts

By default, requests will time out after 600 seconds.

```ruby
# Configure the default for all requests:
anthropic = Anthropic::Client.new(
  timeout: nil # default is 600
)

# Or, configure per-request:
anthropic.messages.create(
  max_tokens: 1024,
  messages: [{role: "user", content: "Hello, Claude"}],
  model: :"claude-opus-4-6",
  request_options: {timeout: 5}
)
```

## Pagination

```ruby
require "anthropic"
anthropic = Anthropic::Client.new
page = anthropic.messages.batches.list(limit: 20)

# fetch items from the current page
page.data.each { |batch| puts(batch.id) }

# Automatically fetches more pages as needed.
page.auto_paging_each do |batch|
  puts(batch.id)
end
```

## File uploads

```ruby
require "anthropic"
anthropic = Anthropic::Client.new
require "pathname"

# Use `Pathname` to send the filename and/or avoid paging a large file into memory:
file_metadata = anthropic.beta.files.upload(file: Pathname("/path/to/file"))

# Alternatively, pass file contents or a `StringIO` directly:
file_metadata = anthropic.beta.files.upload(file: File.read("/path/to/file"))

puts(file_metadata.id)
```

## Sorbet

This library provides comprehensive RBI definitions. You can provide typesafe request parameters like so:

```ruby
require "anthropic"
anthropic = Anthropic::Client.new
anthropic.messages.create(
  max_tokens: 1024,
  messages: [Anthropic::MessageParam.new(role: "user", content: "Hello, Claude")],
  model: :"claude-opus-4-6"
)
```

## Concurrency and connection pooling

The `Anthropic::Client` instances are threadsafe. Each instance has its own HTTP connection pool with a default size of 99. The recommendation is to instantiate the client once per application in most settings.

## Platform integrations

The Ruby SDK supports Bedrock and Vertex AI through dedicated client classes:

- **Bedrock:** `Anthropic::BedrockClient`. Requires the `aws-sdk-bedrockruntime` gem.
- **Vertex AI:** `Anthropic::VertexClient`. Requires the `googleauth` gem.

## Additional resources

- [GitHub repository](https://github.com/anthropics/anthropic-sdk-ruby)
- [RubyDoc documentation](https://gemdocs.org/gems/anthropic)
- [API reference](/docs/en/api/overview)
- [Streaming guide](/docs/en/build-with-claude/streaming)
