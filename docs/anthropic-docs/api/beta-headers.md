---
source: https://platform.claude.com/docs/en/api/beta-headers
scraped: 2026-03-23
section: api
---

# Beta headers

Beta headers allow you to access experimental features and new model capabilities before they become part of the standard API. These features are subject to change and may be modified or removed in future releases.

Beta headers are often used in conjunction with the beta namespace in the client SDKs.

## How to use beta headers

To access beta features, include the `anthropic-beta` header in your API requests:

```http
POST /v1/messages
Content-Type: application/json
X-API-Key: YOUR_API_KEY
anthropic-beta: BETA_FEATURE_NAME
```

When using the SDK, you can specify beta headers in the request options:

```python
# Python
from anthropic import Anthropic

client = Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude"}],
    betas=["files-api-2025-04-14"],
)
```

```typescript
// TypeScript
import Anthropic from "@anthropic-ai/sdk";

const anthropic = new Anthropic();

const msg = await anthropic.beta.messages.create({
  model: "claude-opus-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hello, Claude" }],
  betas: ["files-api-2025-04-14"]
});
```

```bash
# Shell
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "anthropic-beta: files-api-2025-04-14" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-opus-4-6",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Hello, Claude"}]
  }'
```

**Warning:** Beta features are experimental and may have breaking changes with notice, be deprecated or removed, have different rate limits or pricing, or not be available in all regions.

### Multiple beta features

To use multiple beta features in a single request, include all feature names in the header separated by commas:

```http
anthropic-beta: feature1,feature2,feature3
```

### Version naming conventions

Beta feature names typically follow the pattern: `feature-name-YYYY-MM-DD`, where the date indicates when the beta version was released. Always use the exact beta feature name as documented.

## Error handling

If you use an invalid or unavailable beta header, you will receive an error response:

```json
{
  "type": "error",
  "error": {
    "type": "invalid_request_error",
    "message": "Unsupported beta header: invalid-beta-name"
  }
}
```

## Getting help

For questions about beta features:

1. Check the documentation for the specific feature
2. Review the API changelog for updates
3. Contact support for assistance with production usage

Remember that beta features are provided "as-is" and may not have the same SLA guarantees as stable API features.
