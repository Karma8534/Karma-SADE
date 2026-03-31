---
source: https://code.claude.com/docs/en/troubleshooting
scraped: 2026-03-23
section: claude-code
---

# Troubleshooting

> Discover solutions to common issues with Claude Code installation and usage.

## Troubleshoot installation issues

Find the error message or symptom you're seeing:

| What you see | Solution |
|---|---|
| `command not found: claude` or `'claude' is not recognized` | Fix your PATH |
| `syntax error near unexpected token '<'` | Install script returns HTML |
| `curl: (56) Failure writing output to destination` | Download script first, then run it |
| `Killed` during install on Linux | Add swap space for low-memory servers |
| `TLS connect error` or `SSL/TLS secure channel` | Update CA certificates |
| `Failed to fetch version` or can't reach download server | Check network and proxy settings |
| `irm is not recognized` or `&& is not valid` | Use the right command for your shell |
| `Claude Code on Windows requires git-bash` | Install or configure Git Bash |
| `Error loading shared library` | Wrong binary variant for your system |
| `Illegal instruction` on Linux | Architecture mismatch |
| `dyld: cannot load` or `Abort trap` on macOS | Binary incompatibility |
| `App unavailable in region` | Claude Code is not available in your country |
| `unable to get local issuer certificate` | Configure corporate CA certificates |
| `OAuth error` or `403 Forbidden` | Fix authentication |

## Debug installation problems

### Check network connectivity

The installer downloads from `storage.googleapis.com`. Verify you can reach it:

```bash
curl -sI https://storage.googleapis.com
```

If behind a corporate proxy, set `HTTPS_PROXY` and `HTTP_PROXY`:

```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
curl -fsSL https://claude.ai/install.sh | bash
```

### Verify your PATH

If installation succeeded but you get `command not found`, the install directory isn't in your PATH. Claude Code installs to `~/.local/bin/claude` on macOS/Linux or `%USERPROFILE%\.local\bin\claude.exe` on Windows.

**macOS/Linux:**
```bash
echo $PATH | tr ':' '\n' | grep local/bin
# If missing:
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Windows PowerShell:**
```powershell
$env:PATH -split ';' | Select-String 'local\\bin'
# If missing:
$currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
[Environment]::SetEnvironmentVariable('PATH', "$currentPath;$env:USERPROFILE\.local\bin", 'User')
```

### Check for conflicting installations

```bash
which -a claude
ls -la ~/.local/bin/claude
npm -g ls @anthropic-ai/claude-code 2>/dev/null
```

Uninstall npm global install: `npm uninstall -g @anthropic-ai/claude-code`

Remove Homebrew install: `brew uninstall --cask claude-code`

### Check directory permissions

```bash
test -w ~/.local/bin && echo "writable" || echo "not writable"
test -w ~/.claude && echo "writable" || echo "not writable"
# Fix:
sudo mkdir -p ~/.local/bin
sudo chown -R $(whoami) ~/.local
```

## Common installation issues

### Install script returns HTML

Error: `syntax error near unexpected token '<'` or `<!DOCTYPE html>` — the install URL returned HTML instead of the script.

**Solutions:**
1. Install via Homebrew: `brew install --cask claude-code`
2. Install via WinGet: `winget install Anthropic.ClaudeCode`
3. Retry after a few minutes

### `command not found: claude` after installation

The install directory isn't in your shell's search path. See Verify your PATH above.

### `curl: (56) Failure writing output to destination`

Connection broke mid-download. Try:
```bash
brew install --cask claude-code
# or
winget install Anthropic.ClaudeCode
```

### TLS or SSL connection errors

Update CA certificates:
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get install ca-certificates
# macOS
brew install ca-certificates
# Windows: enable TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
```

For corporate CA certificates: `export NODE_EXTRA_CA_CERTS=/path/to/corporate-ca.pem`

### Install killed on low-memory Linux servers

Add swap space:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Windows: "Claude Code on Windows requires git-bash"

Install [Git for Windows](https://git-scm.com/downloads/win). If installed but not found, set in settings.json:

```json
{
  "env": {
    "CLAUDE_CODE_GIT_BASH_PATH": "C:\\Program Files\\Git\\bin\\bash.exe"
  }
}
```

### Linux: wrong binary variant (musl/glibc mismatch)

Check which libc: `ldd /bin/ls | head -1`

For musl systems (Alpine Linux): `apk add libgcc libstdc++ ripgrep`

### `Illegal instruction` on Linux

Verify architecture: `uname -m`

Try: `brew install --cask claude-code`

### `dyld: cannot load` on macOS

Requires macOS 13.0 or later. Update macOS or use: `brew install --cask claude-code`

## Permissions and authentication

### Repeated permission prompts

Use the `/permissions` command to allow specific tools to run without approval.

### Authentication issues

1. Run `/logout` to sign out completely
2. Close Claude Code
3. Restart with `claude` and complete authentication again

If browser doesn't open, press `c` to copy the OAuth URL.

### OAuth error: Invalid code

Press Enter to retry and complete login quickly. If on remote/SSH, copy the URL shown in terminal and open in local browser.

### 403 Forbidden after login

- **Claude Pro/Max users**: verify subscription is active at [claude.ai/settings](https://claude.ai/settings)
- **Console users**: confirm account has the "Claude Code" or "Developer" role
- **Behind a proxy**: see network configuration for proxy setup

### "This organization has been disabled" with active subscription

An `ANTHROPIC_API_KEY` environment variable is overriding your subscription. Unset it:

```bash
unset ANTHROPIC_API_KEY
claude
```

Remove from `~/.zshrc`, `~/.bashrc`, or `~/.profile` to make permanent.

### "Not logged in" or token expired

Run `/login` to re-authenticate. Check that your system clock is accurate.

## Configuration file locations

| File | Purpose |
|---|---|
| `~/.claude/settings.json` | User settings (permissions, hooks, model overrides) |
| `.claude/settings.json` | Project settings (checked into source control) |
| `.claude/settings.local.json` | Local project settings (not committed) |
| `~/.claude.json` | Global state (theme, OAuth, MCP servers) |
| `.mcp.json` | Project MCP servers (checked into source control) |

### Resetting configuration

```bash
# Reset all user settings and state
rm ~/.claude.json
rm -rf ~/.claude/

# Reset project-specific settings
rm -rf .claude/
rm .mcp.json
```

## Performance and stability

### High CPU or memory usage

1. Use `/compact` regularly to reduce context size
2. Close and restart Claude Code between major tasks
3. Add large build directories to your `.gitignore` file

### Command hangs or freezes

Press Ctrl+C to cancel. If unresponsive, close the terminal and restart.

### Search and discovery issues

Install system `ripgrep`:
```bash
# macOS
brew install ripgrep
# Windows
winget install BurntSushi.ripgrep.MSVC
# Ubuntu/Debian
sudo apt install ripgrep
# Alpine
apk add ripgrep
```

Then set `USE_BUILTIN_RIPGREP=0` in your environment.

## IDE integration issues

### JetBrains IDE not detected on WSL2

**Option 1: Configure Windows Firewall**

Find WSL2 IP: `wsl hostname -I`

In PowerShell as Administrator:
```powershell
New-NetFirewallRule -DisplayName "Allow WSL2 Internal Traffic" -Direction Inbound -Protocol TCP -Action Allow -RemoteAddress 172.21.0.0/16 -LocalAddress 172.21.0.0/16
```

**Option 2: Switch to mirrored networking**

Add to `.wslconfig` in your Windows user directory:
```ini
[wsl2]
networkingMode=mirrored
```

Then restart WSL with `wsl --shutdown`.

### Escape key not working in JetBrains terminals

1. Go to Settings → Tools → Terminal
2. Uncheck "Move focus to the editor with Escape", or delete the "Switch focus to Editor" shortcut

## Markdown formatting issues

### Missing language tags in code blocks

Ask Claude: "Add appropriate language tags to all code blocks in this markdown file."

Or set up PostToolUse formatting hooks to detect and add missing language tags automatically.

## Get more help

1. Use the `/feedback` command within Claude Code to report problems to Anthropic
2. Check the [GitHub repository](https://github.com/anthropics/claude-code) for known issues
3. Run `/doctor` to diagnose issues — checks installation, search functionality, auto-update status, invalid settings files, MCP server configuration errors, and more
4. Ask Claude directly about its capabilities and features
