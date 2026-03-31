---
source: https://platform.claude.com/docs/en/api/admin
scraped: 2026-03-23
section: api
---

# Admin

The Admin API provides endpoints for managing organizations, users, workspaces, API keys, and invitations.

## Organizations

### Me

**get** `/v1/organizations/me`

Retrieve information about the organization associated with the authenticated API key.

**Returns:**

```typescript
{
  id: string,           // ID of the Organization
  name: string,         // Name of the Organization
  type: "organization"  // Always "organization"
}
```

## Invites

### Create

**post** `/v1/organizations/invites`

Create an invitation to join the organization.

**Body Parameters:**

- `email: string` — Email of the User.
- `role: string` — Role for the invited User. Cannot be "admin". Options: `"user"`, `"developer"`, `"billing"`, `"claude_code_user"`, `"managed"`.

**Returns:** `Invite` object with `id`, `email`, `expires_at`, `invited_at`, `role`, `status`, `type`.

### Retrieve

**get** `/v1/organizations/invites/{invite_id}`

Get a specific invite.

### List

**get** `/v1/organizations/invites`

List all invites.

### Delete

**delete** `/v1/organizations/invites/{invite_id}`

Delete an invite.

## Members

### List

**get** `/v1/organizations/members`

List all members in the organization.

### Retrieve

**get** `/v1/organizations/members/{user_id}`

Get a specific member.

### Update

**patch** `/v1/organizations/members/{user_id}`

Update a member's role.

**Body Parameters:**

- `role: string` — New role. Options: `"user"`, `"developer"`, `"billing"`, `"claude_code_user"`, `"managed"`.

### Delete/Remove

**delete** `/v1/organizations/members/{user_id}`

Remove a member from the organization.

## Workspaces

### Create

**post** `/v1/organizations/workspaces`

Create a new workspace.

**Body Parameters:**

- `name: string` — Name of the workspace.

### Retrieve

**get** `/v1/organizations/workspaces/{workspace_id}`

Get a specific workspace.

### Update

**patch** `/v1/organizations/workspaces/{workspace_id}`

Update a workspace.

### List

**get** `/v1/organizations/workspaces`

List all workspaces.

### Archive

**post** `/v1/organizations/workspaces/{workspace_id}/archive`

Archive a workspace.

## Workspace Members

### Add

**post** `/v1/organizations/workspaces/{workspace_id}/members`

Add a member to a workspace.

### Retrieve

**get** `/v1/organizations/workspaces/{workspace_id}/members/{user_id}`

Get a workspace member.

### Update

**patch** `/v1/organizations/workspaces/{workspace_id}/members/{user_id}`

Update a workspace member's role.

### Remove

**delete** `/v1/organizations/workspaces/{workspace_id}/members/{user_id}`

Remove a member from a workspace.

### List

**get** `/v1/organizations/workspaces/{workspace_id}/members`

List all workspace members.

## API Keys

### Retrieve

**get** `/v1/organizations/api_keys/{api_key_id}`

Get a specific API key.

### Update

**patch** `/v1/organizations/api_keys/{api_key_id}`

Update an API key (e.g., name or status).

### List

**get** `/v1/organizations/api_keys`

List all API keys in the organization.

**Query Parameters:**

- `workspace_id: optional string` — Filter by workspace.
- `created_by_user_id: optional string` — Filter by creator.
- `status: optional string` — Filter by status (`"active"` or `"disabled"`).

## Domain Types

### Organization

```typescript
{
  id: string,
  name: string,
  type: "organization"
}
```

### Invite

```typescript
{
  id: string,
  email: string,
  expires_at: string,    // RFC 3339 datetime
  invited_at: string,    // RFC 3339 datetime
  role: string,          // "user" | "developer" | "billing" | "admin" | "claude_code_user" | "managed"
  status: string,        // "accepted" | "expired" | "deleted" | "pending"
  type: "invite"
}
```

### Member

```typescript
{
  user_id: string,
  email: string,
  name: string,
  role: string,
  type: "user"
}
```

### Workspace

```typescript
{
  id: string,
  name: string,
  created_at: string,
  archived_at: string | null,
  display_color: string,
  type: "workspace"
}
```

### API Key

```typescript
{
  id: string,
  name: string,
  hint: string,
  status: "active" | "disabled",
  created_at: string,
  workspace_id: string | null,
  created_by: { id: string, type: string },
  type: "api_key"
}
```
