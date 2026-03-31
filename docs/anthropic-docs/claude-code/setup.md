---
source: https://code.claude.com/docs/en/setup
scraped: 2026-03-23
section: claude-code
---

# Advanced setup

> System requirements, platform-specific installation, version management, and uninstallation for Claude Code.

This page covers system requirements, platform-specific installation details, updates, and uninstallation.

## System requirements

Claude Code runs on the following platforms and configurations:

- **Operating system**:
  - macOS 13.0+
  - Windows 10 1809+ or Windows Server 2019+
  - Ubuntu 20.04+
  - Debian 10+
  - Alpine Linux 3.19+
- **Hardware**: 4 GB+ RAM
- **Network**: internet connection required
- **Shell**: Bash, Zsh, PowerShell, or CMD. On Windows, [Git for Windows](https://git-scm.com/downloads/win) is required
- **Location**: Anthropic supported countries

### Additional dependencies

- **ripgrep**: usually included with Claude Code. If search fails, see search troubleshooting.

## Install Claude Code

To install Claude Code, use one of the following methods:

### Native Install (Recommended)

**macOS, Linux, WSL:**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows PowerShell:**
```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows CMD:**
```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

Windows requires [Git for Windows](https://git-scm.com/downloads/win). Install it first if you don't have it.

Native installations automatically update in the background.

### Homebrew

```bash
brew install --cask claude-code
```

Homebrew installations do not auto-update. Run `brew upgrade claude-code` periodically.

### WinGet

```powershell
winget install Anthropic.ClaudeCode
```

WinGet installations do not auto-update. Run `winget upgrade Anthropic.ClaudeCode` periodically.

## Set up on Windows

Claude Code on Windows requires [Git for Windows](https://git-scm.com/downloads/win) or WSL. You can launch `claude` from PowerShell, CMD, or Git Bash.

**Option 1: Native Windows with Git Bash**

Install Git for Windows, then run the install command from PowerShell or CMD.

If Claude Code can't find your Git Bash installation, set the path in your settings.json file:

```json
{
  "env": {
    "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe"
  }
}
```

**Option 2: WSL**

Both WSL 1 and WSL 2 are supported. WSL 2 supports sandboxing for enhanced security. WSL 1 does not support sandboxing.

## Alpine Linux and musl-based distributions

The native installer on Alpine and other musl/uClibc-based distributions requires `libgcc`, `libstdc++`, and `ripgrep`:

```bash
apk add libgcc libstdc++ ripgrep
```

Then set `USE_BUILTIN_RIPGREP` to `0` in your settings.json file:

```json
{
  "env": {
    "USE_BUILTIN_RIPGREP": "0"
  }
}
```

## Verify your installation

After installing, confirm Claude Code is working:

```bash
claude --version
```

For a more detailed check:
```bash
claude doctor
```

## Authenticate

Claude Code requires a Pro, Max, Teams, Enterprise, or Console account. The free Claude.ai plan does not include Claude Code access. You can also use Claude Code with Amazon Bedrock, Google Vertex AI, or Microsoft Foundry.

After installing, log in by running `claude` and following the browser prompts.

## Update Claude Code

Native installations automatically update in the background. You can configure the release channel to control whether you receive updates immediately or on a delayed stable schedule, or disable auto-updates entirely.

### Configure release channel

Control which release channel Claude Code follows with the `autoUpdatesChannel` setting:

- `"latest"`, the default: receive new features as soon as they're released
- `"stable"`: use a version that is typically about one week old, skipping releases with major regressions

Configure via `/config` → **Auto-update channel**, or add it to your settings.json file:

```json
{
  "autoUpdatesChannel": "stable"
}
```

### Disable auto-updates

Set `DISABLE_AUTOUPDATER` to `"1"` in your settings.json file:

```json
{
  "env": {
    "DISABLE_AUTOUPDATER": "1"
  }
}
```

### Update manually

To apply an update immediately:

```bash
claude update
```

## Advanced installation options

### Install a specific version

To install the latest version (default):
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

To install the stable version:
```bash
curl -fsSL https://claude.ai/install.sh | bash -s stable
```

To install a specific version number:
```bash
curl -fsSL https://claude.ai/install.sh | bash -s 1.0.58
```

Windows PowerShell equivalents:
```powershell
# stable
& ([scriptblock]::Create((irm https://claude.ai/install.ps1))) stable

# specific version
& ([scriptblock]::Create((irm https://claude.ai/install.ps1))) 1.0.58
```

### Deprecated npm installation

npm installation is deprecated. The native installer is faster, requires no dependencies, and auto-updates in the background.

To migrate from npm to native:
```bash
# Install the native binary
curl -fsSL https://claude.ai/install.sh | bash

# Remove the old npm installation
npm uninstall -g @anthropic-ai/claude-code
```

If you need npm installation for compatibility reasons, you must have Node.js 18+ installed:
```bash
npm install -g @anthropic-ai/claude-code
```

Do NOT use `sudo npm install -g` as this can lead to permission issues and security risks.

### Binary integrity and code signing

SHA256 checksums for all platforms are published in the release manifests at:
`https://storage.googleapis.com/claude-code-dist-86c565f3-f756-42ad-8dfa-d59b1c096819/claude-code-releases/{VERSION}/manifest.json`

Signed binaries:
- **macOS**: signed by "Anthropic PBC" and notarized by Apple
- **Windows**: signed by "Anthropic, PBC"

## Uninstall Claude Code

### Native installation

**macOS, Linux, WSL:**
```bash
rm -f ~/.local/bin/claude
rm -rf ~/.local/share/claude
```

**Windows PowerShell:**
```powershell
Remove-Item -Path "$env:USERPROFILE\.local\bin\claude.exe" -Force
Remove-Item -Path "$env:USERPROFILE\.local\share\claude" -Recurse -Force
```

### Homebrew installation

```bash
brew uninstall --cask claude-code
```

### WinGet installation

```powershell
winget uninstall Anthropic.ClaudeCode
```

### npm

```bash
npm uninstall -g @anthropic-ai/claude-code
```

### Remove configuration files

> **Warning**: Removing configuration files will delete all your settings, allowed tools, MCP server configurations, and session history.

**macOS, Linux, WSL:**
```bash
# Remove user settings and state
rm -rf ~/.claude
rm ~/.claude.json

# Remove project-specific settings (run from your project directory)
rm -rf .claude
rm -f .mcp.json
```

**Windows PowerShell:**
```powershell
# Remove user settings and state
Remove-Item -Path "$env:USERPROFILE\.claude" -Recurse -Force
Remove-Item -Path "$env:USERPROFILE\.claude.json" -Force

# Remove project-specific settings (run from your project directory)
Remove-Item -Path ".claude" -Recurse -Force
Remove-Item -Path ".mcp.json" -Force
```
