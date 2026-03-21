---
name: plan-before-patch
enabled: true
event: file
conditions:
  - field: file_path
    operator: regex_match
    pattern: server\.js$|server\.py$|karma_regent\.py$|karma_contract|batch_ingest\.py$
---

**PLAN PHASE REQUIRED before editing production files.**

Before this edit, have you written your PLAN? State it now:

1. **Source of truth** for the value/behavior being changed: `[file/endpoint/log]`
2. **Evidence** I have for the root cause: `[specific file read, log line, API response]`
3. **Fix location**: `[exact file + line]`
4. **Verify command**: `[command to run]`
5. **Expected output**: `[exact output that means it worked]`

If you cannot state all 5, stop and investigate first. No patch without a PLAN.
