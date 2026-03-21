---
name: verification-gate
enabled: true
event: stop
pattern: .*
---

**VERIFICATION GATE — before stopping, confirm:**

- [ ] Did you run the actual end-to-end test (not just "I patched the file")?
- [ ] Did the test return the **expected output** (state it explicitly)?
- [ ] If this AC failed before, did it pass THIS TIME with evidence?

**"Should work now" = NOT done.**
**"[command] returned [expected output]" = done.**

If you cannot check all boxes, do not stop. Run the verification first.

Loop circuit breaker: If the same AC has failed 2+ times already, DO NOT attempt again.
Instead: post findings to coordination bus and await Sovereign direction.
