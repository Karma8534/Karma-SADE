---
name: karma-pitfall-aria-delegated-header
description: Use when implementing or modifying aria_local_call in hub-bridge. X-Aria-Delegated header silently blocks ALL Aria memory writes.
type: feedback
---

## Rule

`aria_local_call` must ONLY send `X-Aria-Service-Key` header. NEVER add `X-Aria-Delegated: karma` or any delegated header.

**Why:** Session 81 (Decision #30): Adding `X-Aria-Delegated: karma` triggers Aria's `delegated_read_only` policy — all memory writes to Aria's SQLite are silently dropped. Observations stay at 0. No error is returned. The call appears to succeed. This wasted significant debugging time as there was no indication anything was wrong.

**How to apply:**
```python
# CORRECT: service key only
headers = {
    'X-Aria-Service-Key': ARIA_SERVICE_KEY,
    'Content-Type': 'application/json'
}

# WRONG: adds delegated mode, silently kills writes
headers = {
    'X-Aria-Service-Key': ARIA_SERVICE_KEY,
    'X-Aria-Delegated': 'karma',  # DO NOT ADD
    'Content-Type': 'application/json'
}
```

Also: after each `aria_local_call`, hub-bridge must POST observation to `/v1/ambient` explicitly. Aria's local SQLite backfill endpoint does NOT sync to vault-neo.

## Evidence

- Session 81: Aria observation count stayed at 0 across multiple calls. Traced to delegated_read_only policy.
- Decision #30 in architecture.md
