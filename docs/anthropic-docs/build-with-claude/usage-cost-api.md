---
source: https://platform.claude.com/docs/en/build-with-claude/usage-cost-api
scraped: 2026-03-23
section: build-with-claude
---

# Usage and Cost API

Programmatically access your organization's API usage and cost data with the Usage & Cost Admin API.

---

The Usage & Cost Admin API provides programmatic and granular access to historical API usage and cost data for your organization. This data is similar to the information available in the Usage and Cost pages of the Claude Console.

Use cases:
* **Accurate Usage Tracking:** Get precise token counts and usage patterns
* **Cost Reconciliation:** Match internal records with Anthropic billing for finance and accounting teams
* **Product performance and improvement:** Monitor product performance and set up alerting
* **Rate limit and Priority Tier optimization:** Optimize features like prompt caching or purchase dedicated capacity
* **Advanced Analysis:** Perform deeper data analysis than what's available in Console

Admin API key required — these endpoints require an Admin API key (starting with `sk-ant-admin...`) that differs from standard API keys.

## Partner solutions

Leading observability platforms offer ready-to-use integrations:

- **CloudZero** — Cloud intelligence platform for tracking and forecasting costs
- **Datadog** — LLM Observability with automatic tracing and monitoring
- **Grafana Cloud** — Agentless integration with out-of-the-box dashboards and alerts
- **Honeycomb** — Advanced querying and visualization through OpenTelemetry
- **Vantage** — FinOps platform for LLM cost & usage observability

## Quick start

Get your organization's daily usage for the last 7 days:

```bash
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-08T00:00:00Z&\
ending_at=2025-01-15T00:00:00Z&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"
```

## Usage API

Track token consumption across your organization with detailed breakdowns by model, workspace, and service tier with the `/v1/organizations/usage_report/messages` endpoint.

### Key concepts

- **Time buckets**: Aggregate usage data in fixed intervals (`1m`, `1h`, or `1d`)
- **Token tracking**: Measure uncached input, cached input, cache creation, and output tokens
- **Filtering & grouping**: Filter by API key, workspace, model, service tier, context window, data residency, or speed, and group results by these dimensions
- **Server tool usage**: Track usage of server-side tools like web search

### Basic examples

#### Daily usage by model

```bash
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-08T00:00:00Z&\
group_by[]=model&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"
```

#### Hourly usage with filtering

```bash
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-15T00:00:00Z&\
ending_at=2025-01-15T23:59:59Z&\
models[]=claude-opus-4-6&\
service_tiers[]=batch&\
context_window[]=0-200k&\
bucket_width=1h" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"
```

#### Filter usage by API keys and workspaces

```bash
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-08T00:00:00Z&\
api_key_ids[]=apikey_01Rj2N8SVvo6BePZj99NhmiT&\
workspace_ids[]=wrkspc_01JwQvzr7rXLA5AGx3HKfFUJ&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"
```

#### Data residency

Track data residency controls by grouping and filtering with the `inference_geo` dimension:

```bash
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
group_by[]=inference_geo&\
group_by[]=model&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"
```

Filter to a specific geo (valid values: `global`, `us`, `not_available`):

```bash
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2026-02-01T00:00:00Z&\
ending_at=2026-02-08T00:00:00Z&\
inference_geos[]=us&\
group_by[]=model&\
bucket_width=1d" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"
```

Models released before February 2026 (prior to Claude Opus 4.6) don't support the `inference_geo` request parameter; their usage reports return `"not_available"` for this dimension.

### Time granularity limits

| Granularity | Default Limit | Maximum Limit | Use Case |
|-------------|---------------|---------------|----------|
| `1m` | 60 buckets | 1440 buckets | Real-time monitoring |
| `1h` | 24 buckets | 168 buckets | Daily patterns |
| `1d` | 7 buckets | 31 buckets | Weekly/monthly reports |

## Cost API

Retrieve service-level cost breakdowns in USD with the `/v1/organizations/cost_report` endpoint.

### Key concepts

- **Currency**: All costs in USD, reported as decimal strings in lowest units (cents)
- **Cost types**: Track token usage, web search, and code execution costs
- **Grouping**: Group costs by workspace or description for detailed breakdowns
- **Time buckets**: Daily granularity only (`1d`)

Priority Tier costs use a different billing model and are not included in the cost endpoint. Track Priority Tier usage through the usage endpoint instead.

### Basic example

```bash
curl "https://api.anthropic.com/v1/organizations/cost_report?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-31T00:00:00Z&\
group_by[]=workspace_id&\
group_by[]=description" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"
```

## Pagination

Both endpoints support pagination for large datasets:

1. Make your initial request
2. If `has_more` is `true`, use the `next_page` value in your next request
3. Continue until `has_more` is `false`

```bash
# First request
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-31T00:00:00Z&\
limit=7" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"

# Next request with pagination token
curl "https://api.anthropic.com/v1/organizations/usage_report/messages?\
starting_at=2025-01-01T00:00:00Z&\
ending_at=2025-01-31T00:00:00Z&\
limit=7&\
page=page_xyz..." \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"
```

## Frequently asked questions

**How fresh is the data?**
Usage and cost data typically appears within 5 minutes of API request completion.

**What's the recommended polling frequency?**
The API supports polling once per minute for sustained use. Cache results for dashboards that need frequent updates.

**How do I track code execution usage?**
Code execution costs appear in the cost endpoint grouped under `Code Execution Usage` in the description field. Code execution is not included in the usage endpoint.

**How do I track Priority Tier usage?**
Filter or group by `service_tier` in the usage endpoint and look for the `priority` value.

**What happens with Workbench usage?**
API usage from the Workbench is not associated with an API key, so `api_key_id` will be `null`.

**How is the default workspace represented?**
Usage and costs attributed to the default workspace have a `null` value for `workspace_id`.

**How do I get per-user cost breakdowns for Claude Code?**
Use the Claude Code Analytics API, which provides per-user estimated costs and productivity metrics.

## See also

- [Admin API overview](/docs/en/build-with-claude/administration-api)
- [Pricing](/docs/en/about-claude/pricing)
- [Prompt caching](/docs/en/build-with-claude/prompt-caching)
- [Batch processing](/docs/en/build-with-claude/batch-processing)
- [Rate limits](/docs/en/api/rate-limits)
- [Data residency](/docs/en/build-with-claude/data-residency)
