---
name: api-design-principles
description: "Review or design REST/API endpoints for consistency, backwards compatibility, and correctness. Use when adding endpoints to hub-bridge or vault API, reviewing API shape, or designing new integration surfaces. Invoke with /api-design-principles."
user-invocable: true
---

# API Design Principles

## What This Does

Reviews or designs API endpoints against a consistent set of principles. Catches naming inconsistencies, missing error handling, backwards-incompatible changes, and contract violations before they ship to production.

**Invocation:** `/api-design-principles [endpoint code, route file, or description]`

---

## The 7 Principles (in priority order)

### 1. Backwards Compatibility is Non-Negotiable
- Never remove or rename a response field — only add new ones
- Never change the type of an existing field (string → array breaks clients)
- Deprecate with `_deprecated: true` in response, remove only after migration
- Version breaking changes: `/v2/endpoint`, not modifying `/v1/`
- **Karma rule:** `CLAUDE.md` states additive-only schemas. Any removal = protocol violation.

### 2. Consistent Resource Naming
```
GET    /v1/resource           — list
GET    /v1/resource/:id       — get one
POST   /v1/resource           — create
PATCH  /v1/resource/:id       — partial update
DELETE /v1/resource/:id       — delete
POST   /v1/resource/:id/action — non-CRUD action
```
- Nouns not verbs: `/v1/messages` not `/v1/sendMessage`
- Plural for collections: `/v1/agents` not `/v1/agent`
- Kebab-case for multi-word: `/v1/vault-file`, not `/v1/vaultFile`

### 3. Response Shape Contract
Every response must be consistent and predictable:
```json
{
  "ok": true,
  "data": { ... },
  "error": null,
  "meta": { "request_id": "...", "timestamp": "..." }
}
```
On error:
```json
{
  "ok": false,
  "error": "human-readable message",
  "code": "MACHINE_READABLE_CODE",
  "data": null
}
```
- Never return 200 with error information in the body
- HTTP status codes must be semantically correct (401 = unauth, 403 = forbidden, 404 = not found, 422 = validation error, 500 = server error)

### 4. Auth is Always Required on State-Mutating Endpoints
- GET endpoints MAY be public if data is non-sensitive
- POST/PATCH/DELETE MUST require authentication
- Never rely on "security by obscurity" (hidden endpoints, undocumented routes)
- **Karma rule:** All `/v1/` hub-bridge endpoints require Bearer token. No exceptions.

### 5. Input Validation at the Boundary
- Validate all inputs before processing — never trust client data
- Return 422 with specific field errors, not generic 400
- Cap payload sizes (prevent DoS via large body)
- Sanitize before any downstream use (DB, shell, template)

### 6. Idempotency for Safe Operations
- GET requests must be idempotent (no side effects)
- PUT (full replace) must be idempotent
- POST creates — not idempotent unless `Idempotency-Key` header is supported
- Retries from clients must not double-create resources

### 7. Documentation is Part of the Contract
Every endpoint needs, in code or docs:
- What it accepts (method, path, auth, body schema)
- What it returns (response schema, status codes)
- What errors it can produce (error codes, meaning)

---

## Review Checklist

When reviewing an endpoint, check each:

```
[ ] Route follows resource naming convention
[ ] HTTP method matches semantics (GET=read, POST=create, PATCH=update)
[ ] Response shape is consistent with existing endpoints
[ ] Auth enforced on state-mutating operations
[ ] Input validated with specific error messages
[ ] No backwards-incompatible changes (no field removals, no type changes)
[ ] Error responses use correct HTTP status codes
[ ] No hardcoded secrets or tokens in handler code
[ ] Rate limiting considered for public-facing endpoints
[ ] Endpoint documented (inline or in API docs)
```

---

## Karma-Specific API Conventions

| Pattern | Karma Convention |
|---------|-----------------|
| Auth header | `Authorization: Bearer <token>` |
| Deep mode signal | `X-Karma-Deep: true` header |
| Aria delegation | `X-Aria-Service-Key` only — never `X-Aria-Delegated` |
| Bus message shape | `{from, to, type, urgency, content}` |
| Vault file read | `GET /v1/vault-file/:alias[?tail=N]` |
| Vault file write | `PATCH /v1/vault-file/MEMORY.md {append:"..."}` |
| Tool calls | Tool name must be in hooks.py ALLOWED_TOOLS + TOOL_DEFINITIONS in server.js |

---

## Common Issues This Catches

1. **Endpoint returns 200 on error** — should be 4xx/5xx
2. **Missing auth on write endpoint** — state mutation without auth
3. **Field removed from response** — breaks existing clients silently
4. **POST used for read operation** — should be GET
5. **Tool added to TOOL_DEFINITIONS but not ALLOWED_TOOLS** — silently rejected by hooks.py
6. **Cypher query uses f-string with user input** — injection risk
7. **No input size cap** — DoS vector

---

## When to Invoke

- Designing a new hub-bridge endpoint
- Adding a new tool to the tool registry
- Reviewing coordination bus message shape changes
- Before adding any route to vault API
- When Aria or KCC adds a new API surface
