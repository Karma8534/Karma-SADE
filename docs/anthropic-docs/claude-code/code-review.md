---
source: https://code.claude.com/docs/en/code-review
scrape_date: 2026-03-23
section: claude-code
---

# Code Review

> Set up automated PR reviews that catch logic errors, security vulnerabilities, and regressions using multi-agent analysis of your full codebase

Note: Code Review is in research preview, available for Teams and Enterprise subscriptions. Not available for organizations with Zero Data Retention enabled.

Code Review analyzes your GitHub pull requests and posts findings as inline comments on the lines of code where it found issues. A fleet of specialized agents examine the code changes in the context of your full codebase, looking for logic errors, security vulnerabilities, broken edge cases, and subtle regressions.

Findings are tagged by severity and don't approve or block your PR, so existing review workflows stay intact. You can tune what Claude flags by adding a `CLAUDE.md` or `REVIEW.md` file to your repository.

To run Claude in your own CI infrastructure instead, see [GitHub Actions](/en/github-actions) or [GitLab CI/CD](/en/gitlab-ci-cd).

## How reviews work

Once enabled, reviews trigger when a PR opens, on every push, or when manually requested. Commenting `@claude review` starts reviews on a PR in any mode.

When a review runs, multiple agents analyze the diff and surrounding code in parallel on Anthropic infrastructure. Each agent looks for a different class of issue, then a verification step checks candidates against actual code behavior to filter out false positives. Results are deduplicated, ranked by severity, and posted as inline comments.

Reviews scale in cost with PR size and complexity, completing in 20 minutes on average.

### Severity levels

| Marker | Severity | Meaning |
| :--- | :--- | :--- |
| 🔴 | Normal | A bug that should be fixed before merging |
| 🟡 | Nit | A minor issue, worth fixing but not blocking |
| 🟣 | Pre-existing | A bug that exists in the codebase but was not introduced by this PR |

Findings include a collapsible extended reasoning section explaining why Claude flagged the issue.

### What Code Review checks

By default, Code Review focuses on correctness: bugs that would break production, not formatting preferences or missing test coverage. You can expand what it checks by adding guidance files to your repository.

## Set up Code Review

An admin enables Code Review once for the organization and selects which repositories to include.

**Step 1: Open Claude Code admin settings**

Go to [claude.ai/admin-settings/claude-code](https://claude.ai/admin-settings/claude-code) and find the Code Review section.

**Step 2: Start setup**

Click **Setup** to begin the GitHub App installation flow.

**Step 3: Install the Claude GitHub App**

The app requests these repository permissions:
- **Contents**: read and write
- **Issues**: read and write
- **Pull requests**: read and write

**Step 4: Select repositories**

Choose which repositories to enable for Code Review.

**Step 5: Set review triggers per repo**

For each repository, use the **Review Behavior** dropdown:
- **Once after PR creation**: review runs once when a PR is opened or marked ready for review
- **After every push**: review runs on every push, catching new issues and auto-resolving threads when you fix flagged issues
- **Manual**: reviews start only when someone comments `@claude review` on a PR; subsequent pushes are then reviewed automatically

To verify setup, open a test PR. If you chose an automatic trigger, a check run named **Claude Code Review** appears within a few minutes. If you chose Manual, comment `@claude review`.

## Manually trigger reviews

Comment `@claude review` on a pull request to start a review. Requirements:
- Post as a top-level PR comment (not an inline comment on a diff line)
- Put `@claude review` at the start of the comment
- You must have owner, member, or collaborator access to the repository
- The PR must be open and not a draft

## Customize reviews

Code Review reads two files to guide what it flags:

### CLAUDE.md

Code Review reads `CLAUDE.md` files and treats newly-introduced violations as nit-level findings. Claude reads `CLAUDE.md` at every level of your directory hierarchy. See [memory documentation](/en/memory) for more.

### REVIEW\.md

Add a `REVIEW.md` file to your repository root for review-specific rules:

```markdown
# Code Review Guidelines

## Always check
- New API endpoints have corresponding integration tests
- Database migrations are backward-compatible
- Error messages don't leak internal details to users

## Style
- Prefer `match` statements over chained `isinstance` checks
- Use structured logging, not f-string interpolation in log calls

## Skip
- Generated files under `src/gen/`
- Formatting-only changes in `*.lock` files
```

Claude auto-discovers `REVIEW.md` at the repository root. No configuration needed.

## View usage

Go to [claude.ai/analytics/code-review](https://claude.ai/analytics/code-review) to see Code Review activity. The dashboard shows:

| Section | What it shows |
| :--- | :--- |
| PRs reviewed | Daily count of PRs reviewed |
| Cost weekly | Weekly spend on Code Review |
| Feedback | Count of review comments that were auto-resolved |
| Repository breakdown | Per-repo counts of PRs reviewed and comments resolved |

## Pricing

Code Review is billed based on token usage. Each review averages $15-25 in cost, scaling with PR size, codebase complexity, and how many issues require verification. Code Review usage is billed separately through extra usage and does not count against your plan's included usage.

The review trigger affects total cost:
- **Once after PR creation**: runs once per PR
- **After every push**: runs on each push
- **Manual**: no reviews until someone comments `@claude review`

In any mode, commenting `@claude review` opts the PR into push-triggered reviews.

To set a monthly spend cap, go to [claude.ai/admin-settings/usage](https://claude.ai/admin-settings/usage).

## Related resources

- [Plugins](/en/discover-plugins): browse the plugin marketplace, including a `code-review` plugin for local on-demand reviews
- [GitHub Actions](/en/github-actions): run Claude in your own GitHub Actions workflows
- [GitLab CI/CD](/en/gitlab-ci-cd): self-hosted Claude integration for GitLab pipelines
- [Memory](/en/memory): how `CLAUDE.md` files work across Claude Code
- [Analytics](/en/analytics): track Claude Code usage beyond code review
