---
source: https://platform.claude.com/docs/en/api/skills/create-skill
scraped: 2026-03-23
section: api
---

# Create Skill

**post** `/v1/skills`

Create a new Skill.

## Header Parameters

- `"anthropic-beta": optional array of AnthropicBeta`

  The Skills API requires `skills-2025-10-02`. Other supported beta values include:
  - `"message-batches-2024-09-24"`
  - `"prompt-caching-2024-07-31"`
  - `"computer-use-2024-10-22"`
  - `"computer-use-2025-01-24"`
  - `"pdfs-2024-09-25"`
  - `"token-counting-2024-11-01"`
  - `"token-efficient-tools-2025-02-19"`
  - `"output-128k-2025-02-19"`
  - `"files-api-2025-04-14"`
  - `"mcp-client-2025-04-04"`
  - `"mcp-client-2025-11-20"`
  - `"dev-full-thinking-2025-05-14"`
  - `"interleaved-thinking-2025-05-14"`
  - `"code-execution-2025-05-22"`
  - `"extended-cache-ttl-2025-04-11"`
  - `"context-1m-2025-08-07"`
  - `"context-management-2025-06-27"`
  - `"model-context-window-exceeded-2025-08-26"`
  - `"skills-2025-10-02"`
  - `"fast-mode-2026-02-01"`

## Returns

- `id: string` — Unique identifier for the skill.
- `created_at: string` — ISO 8601 timestamp of when the skill was created.
- `display_title: string` — Display title for the skill. This is a human-readable label that is not included in the prompt sent to the model.
- `latest_version: string` — The latest version identifier for the skill.
- `source: string` — Source of the skill. Either `"custom"` (created by a user) or `"anthropic"` (created by Anthropic).
- `type: string` — Object type. For Skills, this is always `"skill"`.
- `updated_at: string` — ISO 8601 timestamp of when the skill was last updated.

## Example

```bash
curl https://api.anthropic.com/v1/skills?beta=true \
    -X POST \
    -H 'anthropic-version: 2023-06-01' \
    -H 'anthropic-beta: skills-2025-10-02' \
    -H "X-Api-Key: $ANTHROPIC_API_KEY"
```
