---
source: https://code.claude.com/docs/en/github-actions
scraped: 2026-03-23
section: claude-code
---

# Claude Code GitHub Actions

> Learn about integrating Claude Code into your development workflow with Claude Code GitHub Actions

Claude Code GitHub Actions brings AI-powered automation to your GitHub workflow. With a simple `@claude` mention in any PR or issue, Claude can analyze your code, create pull requests, implement features, and fix bugs - all while following your project's standards. For automatic reviews posted on every PR without a trigger, see GitHub Code Review.

Claude Code GitHub Actions is built on top of the Claude Agent SDK, which enables programmatic integration of Claude Code into your applications.

**Claude Opus 4.6 is now available.** Claude Code GitHub Actions default to Sonnet. To use Opus 4.6, configure the `claude_args` parameter to use `--model claude-opus-4-6`.

## Why use Claude Code GitHub Actions?

- **Instant PR creation**: Describe what you need, and Claude creates a complete PR with all necessary changes
- **Automated code implementation**: Turn issues into working code with a single command
- **Follows your standards**: Claude respects your `CLAUDE.md` guidelines and existing code patterns
- **Simple setup**: Get started in minutes with our installer and API key
- **Secure by default**: Your code stays on GitHub's runners

## Setup

### Quick setup

The easiest way to set up this action is through Claude Code in the terminal. Just open claude and run `/install-github-app`.

This command guides you through setting up the GitHub app and required secrets.

- You must be a repository admin to install the GitHub app and add secrets
- The GitHub app requests read & write permissions for Contents, Issues, and Pull requests
- This quickstart method is only available for direct Claude API users. If you're using AWS Bedrock or Google Vertex AI, see the Using with AWS Bedrock & Google Vertex AI section.

### Manual setup

1. **Install the Claude GitHub app** to your repository: [https://github.com/apps/claude](https://github.com/apps/claude)

   Required permissions:
   - **Contents**: Read & write
   - **Issues**: Read & write
   - **Pull requests**: Read & write

2. **Add ANTHROPIC_API_KEY** to your repository secrets

3. **Copy the workflow file** from [examples/claude.yml](https://github.com/anthropics/claude-code-action/blob/main/examples/claude.yml) into your repository's `.github/workflows/`

After completing setup, test the action by tagging `@claude` in an issue or PR comment.

## Upgrading from Beta

Claude Code GitHub Actions v1.0 introduces breaking changes from the beta version.

### Breaking Changes Reference

| Old Beta Input | New v1.0 Input |
|---|---|
| `mode` | *(Removed - auto-detected)* |
| `direct_prompt` | `prompt` |
| `override_prompt` | `prompt` with GitHub variables |
| `custom_instructions` | `claude_args: --append-system-prompt` |
| `max_turns` | `claude_args: --max-turns` |
| `model` | `claude_args: --model` |
| `allowed_tools` | `claude_args: --allowedTools` |
| `disallowed_tools` | `claude_args: --disallowedTools` |
| `claude_env` | `settings` JSON format |

### Before and After Example

**Beta version:**
```yaml
- uses: anthropics/claude-code-action@beta
  with:
    mode: "tag"
    direct_prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    custom_instructions: "Follow our coding standards"
    max_turns: "10"
    model: "claude-sonnet-4-6"
```

**GA version (v1.0):**
```yaml
- uses: anthropics/claude-code-action@v1
  with:
    prompt: "Review this PR for security issues"
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    claude_args: |
      --append-system-prompt "Follow our coding standards"
      --max-turns 10
      --model claude-sonnet-4-6
```

## Example use cases

### Basic workflow

```yaml
name: Claude Code
on:
  issue_comment:
    types: [created]
  pull_request_review_comment:
    types: [created]
jobs:
  claude:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          # Responds to @claude mentions in comments
```

### Code review automation

```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Review this pull request for code quality, correctness, and security."
          claude_args: "--max-turns 5"
```

### Custom automation with prompts

```yaml
name: Daily Report
on:
  schedule:
    - cron: "0 9 * * *"
jobs:
  report:
    runs-on: ubuntu-latest
    steps:
      - uses: anthropics/claude-code-action@v1
        with:
          anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
          prompt: "Generate a summary of yesterday's commits and open issues"
          claude_args: "--model opus"
```

### Common @claude mention commands

```text
@claude implement this feature based on the issue description
@claude how should I implement user authentication for this endpoint?
@claude fix the TypeError in the user dashboard component
```

## Best practices

### CLAUDE.md configuration

Create a `CLAUDE.md` file in your repository root to define code style guidelines, review criteria, project-specific rules, and preferred patterns.

### Security considerations

Never commit API keys directly to your repository. Always use GitHub Secrets:
- Add your API key as `ANTHROPIC_API_KEY`
- Reference it in workflows: `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
- Limit action permissions to only what's necessary
- Review Claude's suggestions before merging

### CI costs

**GitHub Actions costs**: Claude Code runs on GitHub-hosted runners, which consume your GitHub Actions minutes.

**API costs**: Each Claude interaction consumes API tokens based on the length of prompts and responses.

**Cost optimization tips:**
- Use specific `@claude` commands to reduce unnecessary API calls
- Configure appropriate `--max-turns` in `claude_args`
- Set workflow-level timeouts
- Consider using GitHub's concurrency controls

## Using with AWS Bedrock & Google Vertex AI

### For Google Cloud Vertex AI

Prerequisites:
1. A Google Cloud Project with Vertex AI enabled
2. Workload Identity Federation configured for GitHub Actions
3. A service account with the required permissions

**Example Vertex AI workflow:**
```yaml
- uses: anthropics/claude-code-action@v1
  with:
    github_token: ${{ steps.app-token.outputs.token }}
    trigger_phrase: "@claude"
    use_vertex: "true"
    claude_args: '--model claude-sonnet-4@20250514 --max-turns 10'
  env:
    ANTHROPIC_VERTEX_PROJECT_ID: ${{ steps.auth.outputs.project_id }}
    CLOUD_ML_REGION: us-east5
```

### For AWS Bedrock

Prerequisites:
1. An AWS account with Amazon Bedrock enabled
2. GitHub OIDC Identity Provider configured in AWS
3. An IAM role with Bedrock permissions

**Example Bedrock workflow:**
```yaml
- uses: anthropics/claude-code-action@v1
  with:
    github_token: ${{ steps.app-token.outputs.token }}
    use_bedrock: "true"
    claude_args: '--model us.anthropic.claude-sonnet-4-6 --max-turns 10'
```

## Advanced configuration

### Action parameters

| Parameter | Description | Required |
|---|---|---|
| `prompt` | Instructions for Claude | No* |
| `claude_args` | CLI arguments passed to Claude Code | No |
| `anthropic_api_key` | Claude API key | Yes** |
| `github_token` | GitHub token for API access | No |
| `trigger_phrase` | Custom trigger phrase (default: "@claude") | No |
| `use_bedrock` | Use AWS Bedrock instead of Claude API | No |
| `use_vertex` | Use Google Vertex AI instead of Claude API | No |

*Prompt is optional — when omitted for issue/PR comments, Claude responds to trigger phrase
**Required for direct Claude API, not for Bedrock/Vertex

### Pass CLI arguments

```yaml
claude_args: "--max-turns 5 --model claude-sonnet-4-6 --mcp-config /path/to/config.json"
```

Common arguments:
- `--max-turns`: Maximum conversation turns (default: 10)
- `--model`: Model to use (for example, `claude-sonnet-4-6`)
- `--mcp-config`: Path to MCP configuration
- `--allowedTools`: Comma-separated list of allowed tools
- `--debug`: Enable debug output

## Troubleshooting

### Claude not responding to @claude commands

Verify the GitHub App is installed correctly, check that workflows are enabled, ensure API key is set in repository secrets, and confirm the comment contains `@claude` (not `/claude`).

### CI not running on Claude's commits

Ensure you're using the GitHub App or custom app (not Actions user), check workflow triggers include the necessary events, and verify app permissions include CI triggers.

### Authentication errors

Confirm API key is valid and has sufficient permissions. For Bedrock/Vertex, check credentials configuration and ensure secrets are named correctly in workflows.
