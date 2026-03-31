---
source: https://platform.claude.com/docs/en/build-with-claude/administration-api
scraped: 2026-03-23
section: build-with-claude
---

# Admin API overview

---

The Admin API allows you to programmatically manage your organization's resources, including organization members, workspaces, and API keys. This provides programmatic control over administrative tasks that would otherwise require manual configuration in the Claude Console.

The Admin API requires a special Admin API key (starting with `sk-ant-admin...`) that differs from standard API keys. Only organization members with the admin role can provision Admin API keys through the Claude Console.

## How the Admin API works

When you use the Admin API:

1. You make requests using your Admin API key in the `x-api-key` header
2. The API allows you to manage:
   - Organization members and their roles
   - Organization member invites
   - Workspaces and their members
   - API keys

This is useful for:
- Automating user onboarding/offboarding
- Programmatically managing workspace access
- Monitoring and managing API key usage

## Organization roles and permissions

There are five organization-level roles.

| Role | Permissions |
|------|-------------|
| user | Can use Workbench |
| claude_code_user | Can use Workbench and Claude Code |
| developer | Can use Workbench and manage API keys |
| billing | Can use Workbench and manage billing details |
| admin | Can do all of the above, plus manage users |

## Key concepts

### Organization Members

You can list organization members, update member roles, and remove members.

```bash
# List organization members
curl "https://api.anthropic.com/v1/organizations/users?limit=10" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Update member role
curl "https://api.anthropic.com/v1/organizations/users/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{"role": "developer"}'

# Remove member
curl --request DELETE "https://api.anthropic.com/v1/organizations/users/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

### Organization Invites

You can invite users to organizations and manage those invites.

```bash
# Create invite
curl --request POST "https://api.anthropic.com/v1/organizations/invites" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "email": "newuser@domain.com",
    "role": "developer"
  }'

# List invites
curl "https://api.anthropic.com/v1/organizations/invites?limit=10" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Delete invite
curl --request DELETE "https://api.anthropic.com/v1/organizations/invites/{invite_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

### Workspaces

For a comprehensive guide to workspaces, including Console and API examples, see [Workspaces](/docs/en/build-with-claude/workspaces).

### Workspace Members

Manage user access to specific workspaces:

```bash
# Add member to workspace
curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "user_id": "user_xxx",
    "workspace_role": "workspace_developer"
  }'

# List workspace members
curl "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members?limit=10" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Update member role
curl --request POST "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "workspace_role": "workspace_admin"
  }'

# Remove member from workspace
curl --request DELETE "https://api.anthropic.com/v1/organizations/workspaces/{workspace_id}/members/{user_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"
```

### API Keys

Monitor and manage API keys:

```bash
# List API keys
curl "https://api.anthropic.com/v1/organizations/api_keys?limit=10&status=active&workspace_id=wrkspc_xxx" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY"

# Update API key
curl --request POST "https://api.anthropic.com/v1/organizations/api_keys/{api_key_id}" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ANTHROPIC_ADMIN_KEY" \
  --data '{
    "status": "inactive",
    "name": "New Key Name"
  }'
```

## Accessing organization info

Get information about your organization programmatically with the `/v1/organizations/me` endpoint:

```bash
curl "https://api.anthropic.com/v1/organizations/me" \
  --header "anthropic-version: 2023-06-01" \
  --header "x-api-key: $ADMIN_API_KEY"
```

```json
{
  "id": "12345678-1234-5678-1234-567812345678",
  "type": "organization",
  "name": "Organization Name"
}
```

## Usage and cost reports

Track your organization's usage and costs with the [Usage and Cost API](/docs/en/build-with-claude/usage-cost-api).

## Claude Code analytics

Monitor developer productivity and Claude Code adoption with the [Claude Code Analytics API](/docs/en/build-with-claude/claude-code-analytics-api).

## Best practices

To effectively use the Admin API:

- Use meaningful names and descriptions for workspaces and API keys
- Implement proper error handling for failed operations
- Regularly audit member roles and permissions
- Clean up unused workspaces and expired invites
- Monitor API key usage and rotate keys periodically

## FAQ

**What permissions are needed to use the Admin API?**

Only organization members with the admin role can use the Admin API. They must also have a special Admin API key (starting with `sk-ant-admin`).

**Can I create new API keys through the Admin API?**

No, new API keys can only be created through the Claude Console for security reasons. The Admin API can only manage existing API keys.

**What happens to API keys when removing a user?**

API keys persist in their current state as they are scoped to the Organization, not to individual users.

**Can organization admins be removed via the API?**

No, organization members with the admin role cannot be removed via the API for security reasons.

**How long do organization invites last?**

Organization invites expire after 21 days. There is currently no way to modify this expiration period.
