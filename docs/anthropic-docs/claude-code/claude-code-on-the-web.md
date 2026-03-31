---
source: https://code.claude.com/docs/en/claude-code-on-the-web
scraped: 2026-03-23
section: claude-code
---

# Claude Code on the web

> Run Claude Code tasks asynchronously on secure cloud infrastructure

Claude Code on the web is currently in research preview.

## What is Claude Code on the web?

Claude Code on the web lets developers kick off Claude Code from the Claude app. This is perfect for:

- **Answering questions**: Ask about code architecture and how features are implemented
- **Bug fixes and routine tasks**: Well-defined tasks that don't require frequent steering
- **Parallel work**: Tackle multiple bug fixes in parallel
- **Repositories not on your local machine**: Work on code you don't have checked out locally
- **Backend changes**: Where Claude Code can write tests and then write code to pass those tests

Claude Code is also available on the Claude app for iOS and Android for kicking off tasks on the go and monitoring work in progress.

You can kick off new tasks on the web from your terminal with `--remote`, or teleport web sessions back to your terminal to continue locally. To use the web interface while running Claude Code on your own machine instead of cloud infrastructure, see Remote Control.

## Who can use Claude Code on the web?

Claude Code on the web is available in research preview to:

- Pro users
- Max users
- Team users
- Enterprise users with premium seats or Chat + Claude Code seats

## Getting started

1. Visit [claude.ai/code](https://claude.ai/code)
2. Connect your GitHub account
3. Install the Claude GitHub app in your repositories
4. Select your default environment
5. Submit your coding task
6. Review changes in diff view, iterate with comments, then create a pull request

## How it works

When you start a task on Claude Code on the web:

1. **Repository cloning**: Your repository is cloned to an Anthropic-managed virtual machine
2. **Environment setup**: Claude prepares a secure cloud environment with your code, then runs your setup script if configured
3. **Network configuration**: Internet access is configured based on your settings
4. **Task execution**: Claude analyzes code, makes changes, runs tests, and checks its work
5. **Completion**: You're notified when finished and can create a PR with the changes
6. **Results**: Changes are pushed to a branch, ready for pull request creation

## Review changes with diff view

When Claude makes changes to files, a diff stats indicator appears showing the number of lines added and removed (for example, `+12 -1`). Select this indicator to open the diff viewer, which displays a file list on the left and the changes for each file on the right.

From the diff view, you can:
- Review changes file by file
- Comment on specific changes to request modifications
- Continue iterating with Claude based on what you see

## Moving tasks between web and terminal

### From terminal to web

Start a web session from the command line with the `--remote` flag:

```bash
claude --remote "Fix the authentication bug in src/auth/login.ts"
```

This creates a new web session on claude.ai. Use `/tasks` to check progress.

#### Tips for remote tasks

**Plan locally, execute remotely**: For complex tasks, start Claude in plan mode, then send work to the web:

```bash
claude --permission-mode plan
# Once satisfied with the plan:
claude --remote "Execute the migration plan in docs/migration-plan.md"
```

**Run tasks in parallel**: Each `--remote` command creates its own web session:

```bash
claude --remote "Fix the flaky test in auth.spec.ts"
claude --remote "Update the API documentation"
claude --remote "Refactor the logger to use structured output"
```

### From web to terminal

Ways to pull a web session into your terminal:

- **Using `/teleport`**: From within Claude Code, run `/teleport` (or `/tp`) to see an interactive picker
- **Using `--teleport`**: From the command line, run `claude --teleport` or `claude --teleport <session-id>`
- **From `/tasks`**: Run `/tasks` to see your background sessions, then press `t` to teleport
- **From the web interface**: Click "Open in CLI" to copy a command

#### Requirements for teleporting

| Requirement | Details |
|---|---|
| Clean git state | Your working directory must have no uncommitted changes |
| Correct repository | You must run `--teleport` from a checkout of the same repository, not a fork |
| Branch available | The branch from the web session must have been pushed to the remote |
| Same account | You must be authenticated to the same Claude.ai account used in the web session |

## Managing sessions

### Archiving sessions

Hover over the session in the sidebar and click the archive icon to archive a session.

### Deleting sessions

You can delete a session in two ways:
- **From the sidebar**: Filter for archived sessions, then hover over the session and click the delete icon
- **From the session menu**: Open a session, click the dropdown next to the session title, and select **Delete**

## Cloud environment

### Default image

The universal image includes common toolchains and language ecosystems:

- **Python**: Python 3.x with pip, poetry, and common scientific libraries
- **Node.js**: Latest LTS versions with npm, yarn, pnpm, and bun
- **Ruby**: Versions 3.1.6, 3.2.6, 3.3.6 (default: 3.3.6) with gem, bundler, and rbenv
- **PHP**: Version 8.4.14
- **Java**: OpenJDK with Maven and Gradle
- **Go**: Latest stable version with module support
- **Rust**: Rust toolchain with cargo
- **C++**: GCC and Clang compilers
- **PostgreSQL**: Version 16
- **Redis**: Version 7.0

To check what's pre-installed, ask Claude Code to run `check-tools`.

### Environment configuration

**To add a new environment**: Select the current environment to open the environment selector, and then select "Add environment". You can specify the environment name, network access level, environment variables, and a setup script.

**To update an existing environment**: Select the current environment, click the settings button, and update as needed.

**To select your default environment from the terminal**: Run `/remote-env` to choose which environment to use when starting web sessions from your terminal with `--remote`.

### Setup scripts

A setup script is a Bash script that runs when a new cloud session starts, before Claude Code launches. Use setup scripts to install dependencies, configure tools, or prepare anything the cloud environment needs.

Scripts run as root on Ubuntu 24.04.

To add a setup script, open the environment settings dialog and enter your script in the **Setup script** field.

Example: install the `gh` CLI:
```bash
#!/bin/bash
apt update && apt install -y gh
```

Setup scripts run only when creating a new session. They are skipped when resuming.

#### Setup scripts vs. SessionStart hooks

| | Setup scripts | SessionStart hooks |
|---|---|---|
| Attached to | The cloud environment | Your repository |
| Configured in | Cloud environment UI | `.claude/settings.json` in your repo |
| Runs | Before Claude Code launches, on new sessions only | After Claude Code launches, on every session including resumed |
| Scope | Cloud environments only | Both local and cloud |

### Dependency management

Use setup scripts to install packages when a session starts:

```bash
#!/bin/bash
npm install
pip install -r requirements.txt
```

Or use SessionStart hooks in your repository's `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/install_pkgs.sh"
          }
        ]
      }
    ]
  }
}
```

## Network access and security

### Network policy

For security, all GitHub operations go through a dedicated proxy service. Environments run behind an HTTP/HTTPS network proxy.

### Access levels

By default, network access is limited to allowlisted domains. You can configure custom network access, including disabling network access.

### Default allowed domains

The allowlist includes common package registries and development services:

- Anthropic services (api.anthropic.com, etc.)
- GitHub, GitLab, Bitbucket
- Container registries (Docker Hub, GCR, GHCR, ECR, etc.)
- Cloud platforms (AWS, GCP, Azure, Oracle)
- Package managers: npm, PyPI, RubyGems, Cargo, Go proxy, Maven, NuGet, Pub, Hex, CPAN, CocoaPods, Haskell
- Linux distributions (Ubuntu/Debian)
- Development tools (Kubernetes, HashiCorp, Anaconda, Apache, Eclipse, Node.js)
- Cloud monitoring (Sentry, Datadog)
- MCP (*.modelcontextprotocol.io)

## Security and isolation

- **Isolated virtual machines**: Each session runs in an isolated, Anthropic-managed VM
- **Network access controls**: Network access is limited by default, and can be disabled
- **Credential protection**: Sensitive credentials are never inside the sandbox with Claude Code — authentication is handled through a secure proxy using scoped credentials

## Pricing and rate limits

Claude Code on the web shares rate limits with all other Claude and Claude Code usage within your account. Running multiple tasks in parallel will consume more rate limits proportionately.

## Limitations

- **Repository authentication**: You can only move sessions from web to local when authenticated to the same account
- **Platform restrictions**: Claude Code on the web only works with code hosted in GitHub. GitLab and other non-GitHub repositories cannot be used with cloud sessions

## Best practices

1. **Automate environment setup**: Use setup scripts to install dependencies and configure tools before Claude Code launches.
2. **Document requirements**: Clearly specify dependencies and commands in your `CLAUDE.md` file.

## Related resources

- Hooks configuration
- Settings reference
- Security
- Data usage
