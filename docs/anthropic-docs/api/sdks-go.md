---
source: https://platform.claude.com/docs/en/api/sdks/go
scraped: 2026-03-23
section: api
---

# Go SDK

Install and configure the Anthropic Go SDK with context-based cancellation and functional options

---

The Anthropic Go library provides convenient access to the Anthropic REST API from applications written in Go.

<Info>
For API feature documentation with code examples, see the [API reference](/docs/en/api/overview). This page covers Go-specific SDK features and configuration.
</Info>

## Installation

```go
import (
	"github.com/anthropics/anthropic-sdk-go" // imported as anthropic
)
```

Or to pin the version:

```bash
go get -u 'github.com/anthropics/anthropic-sdk-go@v1.27.1'
```

## Requirements

This library requires Go 1.23+.

## Usage

```go
package main

import (
	"context"
	"fmt"

	"github.com/anthropics/anthropic-sdk-go"
	"github.com/anthropics/anthropic-sdk-go/option"
)

func main() {
	client := anthropic.NewClient(
		option.WithAPIKey("my-anthropic-api-key"), // defaults to os.LookupEnv("ANTHROPIC_API_KEY")
	)
	message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
		MaxTokens: 1024,
		Messages: []anthropic.MessageParam{
			anthropic.NewUserMessage(anthropic.NewTextBlock("What is a quaternion?")),
		},
		Model: anthropic.ModelClaudeOpus4_6,
	})
	if err != nil {
		panic(err.Error())
	}
	fmt.Printf("%+v\n", message.Content)
}
```

## Conversations

```go
messages := []anthropic.MessageParam{
	anthropic.NewUserMessage(anthropic.NewTextBlock("What is my first name?")),
}

message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
	Model:     anthropic.ModelClaudeOpus4_6,
	Messages:  messages,
	MaxTokens: 1024,
})
if err != nil {
	panic(err)
}

messages = append(messages, message.ToParam())
messages = append(messages, anthropic.NewUserMessage(
	anthropic.NewTextBlock("My full name is John Doe"),
))

message, err = client.Messages.New(context.TODO(), anthropic.MessageNewParams{
	Model:     anthropic.ModelClaudeOpus4_6,
	Messages:  messages,
	MaxTokens: 1024,
})
```

## System prompts

```go
messages := []anthropic.MessageParam{anthropic.NewUserMessage(anthropic.NewTextBlock("Hello"))}
message, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
	Model:     anthropic.ModelClaudeOpus4_6,
	MaxTokens: 1024,
	System: []anthropic.TextBlockParam{
		{Text: "Be very serious at all times."},
	},
	Messages: messages,
})
```

## Streaming

```go
stream := client.Messages.NewStreaming(context.TODO(), anthropic.MessageNewParams{
	Model:     anthropic.ModelClaudeOpus4_6,
	MaxTokens: 1024,
	Messages: []anthropic.MessageParam{
		anthropic.NewUserMessage(anthropic.NewTextBlock("What is a quaternion?")),
	},
})

message := anthropic.Message{}
for stream.Next() {
	event := stream.Current()
	err := message.Accumulate(event)
	if err != nil {
		panic(err)
	}

	switch eventVariant := event.AsAny().(type) {
	case anthropic.ContentBlockDeltaEvent:
		switch deltaVariant := eventVariant.Delta.AsAny().(type) {
		case anthropic.TextDelta:
			print(deltaVariant.Text)
		}
	}
}

if stream.Err() != nil {
	panic(stream.Err())
}
```

## Request fields

The anthropic library uses the `omitzero` semantics from the Go 1.24+ `encoding/json` release for request fields.

Required primitive fields (`int64`, `string`, etc.) feature the tag `` `json:"...,required"` ``. These fields are always serialized, even their zero values.

Optional primitive types are wrapped in a `param.Opt[T]`. These fields can be set with the provided constructors, `anthropic.String(string)`, `anthropic.Int(int64)`, etc.

## Error handling

When the API returns a non-success status code, the SDK returns an error with type `*anthropic.Error`.

```go
_, err := client.Messages.New(context.TODO(), anthropic.MessageNewParams{
    // ...
})
if err != nil {
    var apierr *anthropic.Error
    if errors.As(err, &apierr) {
        println("Request ID:", apierr.RequestID)
        println(string(apierr.DumpRequest(true)))
        println(string(apierr.DumpResponse(true)))
    }
    panic(err.Error())
}
```

## Retries

Certain errors will be automatically retried 2 times by default, with a short exponential backoff. The SDK retries by default all connection errors, 408 Request Timeout, 409 Conflict, 429 Rate Limit, and >=500 Internal errors.

```go
// Configure the default for all requests:
client := anthropic.NewClient(
    option.WithMaxRetries(0), // default is 2
)
```

## Timeouts

Requests do not time out by default; use context to configure a timeout for a request lifecycle.

```go
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
defer cancel()

_, _ = client.Messages.New(
    ctx,
    anthropic.MessageNewParams{
        // ...
    },
    // This sets the per-retry timeout
    option.WithRequestTimeout(20*time.Second),
)
```

## File uploads

Request parameters that correspond to file uploads in multipart requests are typed as `io.Reader`.

```go
// A file from the file system
file, err := os.Open("/path/to/file.json")
anthropic.BetaFileUploadParams{
	File:  anthropic.File(file, "custom-name.json", "application/json"),
	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaFilesAPI2025_04_14},
}

// A file from a string
anthropic.BetaFileUploadParams{
	File:  anthropic.File(strings.NewReader("my file contents"), "custom-name.json", "application/json"),
	Betas: []anthropic.AnthropicBeta{anthropic.AnthropicBetaFilesAPI2025_04_14},
}
```

## Pagination

### Auto-pagination

```go
iter := client.Messages.Batches.ListAutoPaging(context.TODO(), anthropic.MessageBatchListParams{
	Limit: anthropic.Int(20),
})
// Automatically fetches more pages as needed.
for iter.Next() {
	messageBatch := iter.Current()
	fmt.Printf("%+v\n", messageBatch)
}
if err := iter.Err(); err != nil {
	panic(err.Error())
}
```

### Manual pagination

```go
page, err := client.Messages.Batches.List(context.TODO(), anthropic.MessageBatchListParams{
	Limit: anthropic.Int(20),
})
for page != nil {
	for _, batch := range page.Data {
		fmt.Printf("%+v\n", batch)
	}
	page, err = page.GetNextPage()
}
if err != nil {
	panic(err.Error())
}
```

## RequestOptions

This library uses the functional options pattern. Functions defined in the `option` package return a `RequestOption`, which is a closure that mutates a `RequestConfig`.

```go
client := anthropic.NewClient(
	// Adds a header to every request made by the client
	option.WithHeader("X-Some-Header", "custom_header_info"),
)

client.Messages.New(context.TODO(), // ...,
	// Override the header
	option.WithHeader("X-Some-Header", "some_other_custom_header_info"),
	// Add an undocumented field to the request body, using sjson syntax
	option.WithJSONSet("some.json.path", map[string]string{"my": "object"}),
)
```

## HTTP client customization

### Middleware

```go
client := anthropic.NewClient(
    option.WithMiddleware(func(req *http.Request, next option.MiddlewareNext) (res *http.Response, err error) {
        // Before the request
        start := time.Now()
        LogReq(req)

        // Forward the request to the next handler
        res, err = next(req)

        // Handle stuff after the request
        LogRes(res, err, time.Since(start))

        return res, err
    }),
)
```

## Platform integrations

The Go SDK supports Amazon Bedrock and Google Vertex AI through subpackages:

- **Bedrock:** `import "github.com/anthropics/anthropic-sdk-go/bedrock"`. Use `bedrock.WithLoadDefaultConfig(ctx)` or `bedrock.WithConfig(cfg)`.
- **Vertex AI:** `import "github.com/anthropics/anthropic-sdk-go/vertex"`. Use `vertex.WithGoogleAuth(ctx, region, projectID)` or `vertex.WithCredentials(ctx, region, projectID, creds)`.

## Additional resources

- [GitHub repository](https://github.com/anthropics/anthropic-sdk-go)
- [Go package documentation](https://pkg.go.dev/github.com/anthropics/anthropic-sdk-go)
- [API reference](/docs/en/api/overview)
- [Streaming guide](/docs/en/build-with-claude/streaming)
