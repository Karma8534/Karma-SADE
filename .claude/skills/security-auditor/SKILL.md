---
name: security-auditor
description: "Run a structured adversarial security review over code before it ships. Checks OWASP Top 10 vulnerabilities, secrets exposure, injection flaws, auth/authz issues, and Karma-specific surface areas (hub-bridge, vault API, coordination bus). Invoke with /security-auditor or before any deployment."
user-invocable: true
---

# Security Auditor

## What This Does

Runs an adversarial pass over code — thinking like an attacker, not a reviewer. The job is not to flag potential issues but to either confirm exploitation or clear the path.

**Invocation:** `/security-auditor [file or directory or feature description]`

---

## Audit Pipeline (5 phases, in order)

### Phase 1: Secrets and Credential Exposure
- Hardcoded API keys, bearer tokens, passwords, connection strings
- Secrets in git history (`git log -p | grep -E "Bearer|api_key|password"`)
- Secrets in environment files that might be committed
- Token paths logged or returned in API responses
- **Karma-specific:** hub.chat.token.txt path never logged; OPENAI_API_KEY never in committed source

### Phase 2: Injection Vulnerabilities
- **SQL injection:** parameterized queries enforced, no string concatenation in DB calls
- **Command injection:** shell=True with user input, subprocess with untrusted args
- **SSTI (Server-Side Template Injection):** template rendering with user-controlled input
- **NoSQL/Cypher injection:** FalkorDB query construction — check for parameter placeholders vs. f-strings
- **Karma-specific:** `GRAPH.QUERY` calls must use parameters, not f-strings with user data

### Phase 3: Authentication and Session Issues
- JWT none-algorithm acceptance
- Weak or predictable session tokens
- Missing CSRF protection on state-mutating endpoints
- Session fixation after privilege change
- Default credentials left in place
- **Karma-specific:** hub-bridge Bearer token validation — every `/v1/` endpoint must check auth header

### Phase 4: Authorization (IDOR and Access Control)
- Direct object references without ownership check (IDOR)
- Privilege escalation paths — can a lower-rank agent call a Sovereign-only operation?
- Path traversal in file access
- Mass assignment — does any endpoint accept and persist arbitrary fields?
- **Karma-specific:** coordination bus messages — can any agent post as `sovereign` or `cc`?

### Phase 5: Unsafe Code Patterns
- `eval()`, `exec()`, dynamic code execution with external input
- Arbitrary file read/write from user-controlled paths
- SSRF — does any endpoint fetch a user-provided URL without allowlist?
- Denial of service — unbounded loops, regex catastrophic backtracking, large payload acceptance
- Dependency audit — known CVEs in package versions

---

## Output Format

For each finding:
```
[SEVERITY: CRITICAL|HIGH|MEDIUM|LOW] [CATEGORY]
File: path/to/file.py:line_number
Finding: what the vulnerability is
Exploit path: how an attacker would use it
Fix: exact code change required
```

**No findings = explicit CLEAR confirmation:**
```
SECURITY AUDIT CLEAR — no findings in [scope].
Checked: secrets, injection, auth, IDOR, unsafe patterns.
```

---

## Karma-Specific Surface Areas

Always check these when auditing hub-bridge or karma-server changes:

| Component | Risk Area |
|-----------|-----------|
| hub-bridge `/v1/chat` | Bearer token bypass; prompt injection in user content |
| hub-bridge tool calls | `shell_run` command injection via tool input |
| vault API | Unauthenticated reads; path traversal in `vault-file` aliases |
| FalkorDB queries | Cypher injection via f-string query construction |
| coordination bus | Message spoofing — `from` field not validated server-side |
| batch_ingest | Command injection in shell calls from Python |
| K2 `/api/exec` | shell=True with user-controlled input — highest risk surface |

---

## When to Invoke

- Before any PR that touches auth, API endpoints, or shell execution
- Before any deployment to vault-neo
- After adding a new tool to hub-bridge tool registry
- When reviewing Aria/K2 code that runs shell commands
- When a new endpoint is added to hub-bridge or vault API

---

## Integration with P3-D Governance

The `quality-gate.py` hook scans for hardcoded secrets before push. This skill covers the remaining attack surface that the secret scan cannot catch (logic flaws, injection, authorization gaps).

Run the secret scan first (`quality-gate`), then this skill for full coverage.
