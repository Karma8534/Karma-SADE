# Git Workflow & GitHub Backup Protocol

## Repository
- **Remote:** https://github.com/Karma8534/Karma-SADE.git (PRIVATE)
- **Branch:** claude/elegant-solomon
- **Visibility:** Private — must remain private (secrets exist in git history)

## .gitignore Requirements
These patterns MUST be in .gitignore before any commit:
```
.vault-token
*.env
.env.*
*secret*
*credentials*
*.pem
*.key
id_rsa*
*.sqlite
*.db
node_modules/
__pycache__/
.DS_Store
Thumbs.db
```

## Pre-Commit Verification (Mandatory)
Run this before EVERY commit:
```bash
grep -rn "Bearer\|token\|secret\|password\|api_key" --include="*.js" --include="*.py" --include="*.json" --include="*.md" . | grep -v node_modules | grep -v .git
```
If any real secrets appear in output, do NOT commit. Remove them first.

## Commit & Push Workflow
1. Verify no secrets in staged files (pre-commit check above)
2. `git add -A`
3. `git commit -m "phase-N: descriptive message"`
4. `git push origin claude/elegant-solomon`
5. Verify: `git log --oneline -1` matches remote

## If Secrets Are Accidentally Committed
1. STOP — do not push if not yet pushed
2. `git rm --cached [file-with-secret]`
3. Add file to .gitignore
4. `git commit --amend` to remove from last commit
5. If already pushed: the secret is compromised. Rotate it immediately.
6. To scrub history: `git filter-repo --path [file] --invert-paths` (destructive, requires force push)

## Backup Frequency
- After every significant code change
- After completing any phase milestone
- At the end of every session (part of Session End Protocol in CLAUDE.md)
- Minimum: once per session, no exceptions
