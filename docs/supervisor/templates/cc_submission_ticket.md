# CC Submission Ticket

**Ticket ID:** <!-- e.g. CC-001 -->
**Date:** <!-- YYYY-MM-DD -->
**Session:** <!-- session hash or label -->
**Task:** <!-- task name from plan -->

## Claim

<!-- One sentence: what is being claimed as complete -->

## Evidence

### Commands run (exact, reproducible)
```
<!-- paste exact commands here -->
```

### Raw output
```
<!-- paste raw output here -->
```

### Artifacts created/modified
| Path | SHA/hash | Status |
|------|----------|--------|
| <!-- path --> | <!-- hash --> | created/modified |

### Rollback command
```
<!-- git reset or revert command to undo this submission -->
```

## Scope assertion

- [ ] No writes to hard_deny_paths (secrets, auth, financial)
- [ ] No writes to critical_paths without Colby approval
- [ ] Verified: tests pass (attach output above)
- [ ] Root cause identified (not guessed) — or stated "I don't know"

## Notes

<!-- Any caveats, known gaps, or follow-up needed -->
