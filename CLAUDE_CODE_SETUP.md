# Claude Code Integration with Karma

## Overview
Configure your local Claude Code CLI to use Karma's GLM-5 model instead of Haiku API credits.

**Benefits:**
- Unlimited Claude Code usage via $30/mo GLM-5 subscription
- No consumption of Haiku API credits
- Intelligent routing: coding tasks routed to best-performing model

**Architecture:**
```
Claude Code CLI
  ↓ (HTTP POST /v1/chat/completions)
  ↓
Karma Server (localhost:8340)
  ↓ (intelligent routing)
  ↓
GLM-5 ($30/mo unlimited)
```

## Prerequisites
1. Karma server running locally on port 8340
2. GLM-5 API key configured in Karma (via GLM_API_KEY env var)
3. Claude Code CLI installed

## Step 1: Verify Karma Proxy is Running

```bash
curl -X POST http://localhost:8340/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-5-coding",
    "messages": [
      {"role": "user", "content": "Say hello"}
    ]
  }'
```

Expected response:
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1708145000,
  "model": "glm5/glm-5",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello!"
      },
      "finish_reason": "stop"
    }
  ]
}
```

## Step 2: Configure Claude Code

### Locate Claude Code Configuration File

**macOS:**
```bash
~/Library/Application\ Support/Claude/config.json
```

**Linux:**
```bash
~/.config/Claude/config.json
```

**Windows:**
```
%APPDATA%\Claude\config.json
```

### Edit Configuration

Add custom model entry (create file if it doesn't exist):

```json
{
  "models": {
    "karma-glm5": {
      "provider": "openai",
      "baseURL": "http://localhost:8340/v1",
      "apiKey": "not-needed-local",
      "model": "glm-5-coding"
    }
  },
  "defaultModel": "karma-glm5"
}
```

**Important notes:**
- `baseURL`: Must point to Karma server (localhost:8340, or adjust if on different machine)
- `apiKey`: Can be any string (not used, but required by config schema)
- `model`: Can be anything; Karma will treat it as a coding task

### Step 3: Test Claude Code

Run Claude Code with your custom model:

```bash
claude --model karma-glm5 "Write a Python function to calculate factorial"
```

Or use in interactive mode:
```bash
claude repl --model karma-glm5
```

Expected output:
```
> Write a Python function to calculate factorial
def factorial(n):
    """Calculate factorial of n recursively."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Process: glm5/glm-5 (1234ms)
```

## Step 4: Verify Usage

### Check Karma Metrics

```bash
curl http://localhost:8340/status | jq '.routing'
```

Should show GLM-5 being used for requests.

### Check Ledger

```bash
ssh vault-neo "tail -20 /opt/seed-vault/memory_v1/ledger/memory.jsonl | grep 'openai-proxy'"
```

Shows Claude Code requests logged with source="openai-proxy".

## Troubleshooting

### "Connection refused" or "Connection timeout"

**Issue:** Karma server not running or on wrong port

**Fix:**
```bash
# Check if Karma is running
ssh vault-neo "docker ps | grep karma-server"

# Start if needed
ssh vault-neo "cd /opt/seed-vault && docker-compose up -d karma-server"
```

### "All models failed" in response

**Issue:** GLM-5 API key missing or invalid

**Fix:**
```bash
# Check env vars in running container
ssh vault-neo "docker exec karma-server env | grep GLM"

# Should see:
# GLM_API_KEY=ef9e09a983ff406dab2175d9c5422b19.hfTTxvirrXdkZAMC
# GLM_MODEL=glm-5
# GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
```

### Claude Code doesn't find the model

**Issue:** Config file path incorrect or syntax error

**Fix:**
1. Verify file path matches your OS
2. Check JSON syntax (use `jq` to validate)
3. Restart Claude Code after config changes

```bash
# Validate JSON
jq . ~/Library/Application\ Support/Claude/config.json
```

## Advanced Configuration

### Use Remote Karma Server

If Karma is running on a different machine (e.g., `karma.arknexus.net`):

```json
{
  "models": {
    "karma-glm5": {
      "provider": "openai",
      "baseURL": "https://karma.arknexus.net/v1",
      "apiKey": "not-needed",
      "model": "glm-5-coding"
    }
  },
  "defaultModel": "karma-glm5"
}
```

### Multiple Models

You can configure fallbacks:

```json
{
  "models": {
    "karma-glm5": {
      "provider": "openai",
      "baseURL": "http://localhost:8340/v1",
      "apiKey": "not-needed",
      "model": "glm-5-coding"
    },
    "karma-fallback": {
      "provider": "openai",
      "baseURL": "http://localhost:8340/v1",
      "apiKey": "not-needed",
      "model": "fallback"
    }
  },
  "defaultModel": "karma-glm5"
}
```

## Monitoring & Analytics

### Daily Usage Report

```bash
curl http://localhost:8340/status | jq '.routing.stats'
```

Shows:
- Total requests from Claude Code
- Errors/retries
- Average latency per provider

### Ledger Search

Find Claude Code requests in ledger:
```bash
ssh vault-neo "grep 'openai-proxy' /opt/seed-vault/memory_v1/ledger/memory.jsonl | wc -l"
```

Count total requests made.

## Cost Analysis

**Before (using Haiku via Claude API):**
- Input tokens: ~$0.80 per 1M
- Output tokens: ~$1.00 per 1M
- Example: 100 requests × 500 tokens avg = ~$0.05/day

**After (using GLM-5 via Karma):**
- Cost: $30/month fixed (unlimited)
- Breakeven: ~600 requests/month of average complexity
- Scaling: 0 marginal cost per additional request

## Security Notes

- **Authentication:** Not implemented in current Karma server (local-only design)
- **HTTPS:** Use in production via Caddy reverse proxy (already configured at karma.arknexus.net)
- **API Key:** Claude Code sends "not-needed-local" as placeholder (Karma doesn't validate)
- **Data:** All requests logged to local ledger; never sent to external services

## Support

For issues, check:
1. Karma server health: `curl http://localhost:8340/health`
2. Router status: `curl http://localhost:8340/status | jq '.routing'`
3. GLM-5 connectivity: Traces in `ssh vault-neo "docker logs karma-server"`
