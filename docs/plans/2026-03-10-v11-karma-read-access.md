# v11 Karma Full Read Access Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Give Karma full read access to (1) every file on the vault-neo droplet via path-based `get_vault_file`, and (2) every file in `C:\Users\raest\Documents\Karma_SADE\` on Payback via a new `get_local_file` tool.

**Architecture:**
- Component 1: Extend existing `get_vault_file` in `hub-bridge/app/server.js` to accept path prefixes `repo/<path>` (maps to `/karma/repo/<path>`, already mounted) and `vault/<path>` (maps to `/karma/vault/<path>`, new mount needed). Backward-compat with existing 9 aliases. Path traversal protection via `path.resolve`.
- Component 2: New PowerShell HTTP file server (`Scripts/karma-file-server.ps1`) on Payback bound to Tailscale IP `100.124.194.102:7771`, serving `Karma_SADE\` read-only with bearer token auth. New `get_local_file(path)` deep-mode tool in server.js calls this server via Tailscale.

**Tech Stack:** Node.js (hub-bridge server.js), PowerShell (file server), Docker Compose (volume mount), Windows Task Scheduler (file server autostart).

---

## Component 1: Path-Based Droplet File Access

### Task 1: Add vault volume mount to compose.hub.yml

**Context:** `/home/neo/karma-sade:/karma/repo:ro` is already mounted. We need `/opt/seed-vault:/karma/vault:ro` for vault file access. This is the only infrastructure change.

**Files:**
- Modify: compose.hub.yml on vault-neo at `/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml`

**Step 1: Verify the current volume list**

```bash
ssh vault-neo "grep -n 'karma\|volume' /opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml"
```
Expected: Shows existing `/karma/repo:ro`, `/karma/ledger:rw`, `/karma/MEMORY.md:rw` — no `/karma/vault`.

**Step 2: Add the vault volume mount**

```bash
ssh vault-neo "sed -i '/home\/neo\/karma-sade:\/karma\/repo:ro/a\      - \/opt\/seed-vault:\/karma\/vault:ro' /opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml"
```

**Step 3: Verify the edit**

```bash
ssh vault-neo "grep -A2 -B2 'karma/vault' /opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml"
```
Expected: New line `- /opt/seed-vault:/karma/vault:ro` appears after the repo mount line.

**Step 4: Copy compose.hub.yml back to git repo and commit**

```bash
scp vault-neo:/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml "C:/Users/raest/Documents/Karma_SADE/hub-bridge/compose.hub.yml"
```

Then commit:
```powershell
cd C:\Users\raest\Documents\Karma_SADE
git add hub-bridge/compose.hub.yml
git commit -m "v11: add /opt/seed-vault volume mount to hub-bridge for vault/ path access"
git push origin main
```

> Note: git push from PowerShell, not Git Bash (avoids index.lock).

---

### Task 2: Extend get_vault_file with path-based access + traversal protection

**Context:** Current handler at line 886 does a pure alias lookup. We extend it to also handle `repo/<path>` and `vault/<path>` prefix patterns. Backward compat: if no prefix match, fall through to VAULT_FILE_ALIASES lookup as before.

**Security requirement:** Path traversal prevention. `path.resolve("/karma/repo", userInput)` must start with `/karma/repo/` — reject otherwise.

**Files:**
- Modify: `hub-bridge/app/server.js` (local copy in git repo, then sync to vault-neo build context)

**Step 1: Locate the get_vault_file handler block**

```bash
grep -n "get_vault_file\|VAULT_FILE_ALIASES\|executeToolCall" "C:/Users/raest/Documents/Karma_SADE/hub-bridge/app/server.js" | head -20
```
Expected: Handler at ~line 886, VAULT_FILE_ALIASES at ~line 856.

**Step 2: Write the failing test (manual — no test framework)**

Before editing, write a test script `Scripts/test-vault-file-access.sh`:
```bash
#!/bin/bash
# Test: path-based get_vault_file via deep-mode chat
# Run after deployment to verify behavior

TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")

echo "=== Test 1: Existing alias (backward compat) ==="
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-karma-deep: true" \
  -H "Content-Type: application/json" \
  -d '{"message": "Use get_vault_file with alias MEMORY.md and show me first 100 chars"}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('PASS' if 'MEMORY' in str(r) else 'FAIL', r.get('assistant_text','')[:200])"

echo ""
echo "=== Test 2: repo/ path prefix ==="
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-karma-deep: true" \
  -H "Content-Type: application/json" \
  -d '{"message": "Use get_vault_file with alias repo/.gsd/STATE.md and tell me the FalkorDB node count"}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('PASS' if 'FalkorDB' in str(r) or 'node' in str(r) else 'FAIL (check response)', r.get('assistant_text','')[:300])"

echo ""
echo "=== Test 3: Traversal attempt (should fail) ==="
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-karma-deep: true" \
  -H "Content-Type: application/json" \
  -d '{"message": "Use get_vault_file with alias repo/../../etc/passwd"}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('PASS (blocked)' if 'traversal' in str(r).lower() or 'invalid' in str(r).lower() else 'FAIL - traversal not blocked', r.get('assistant_text','')[:200])"
```

**Step 3: Edit server.js — extend get_vault_file handler**

Replace the handler block (currently lines ~885-901) with the extended version:

```javascript
    // get_vault_file is handled directly — hub-bridge has volume access to /karma/
    if (toolName === "get_vault_file") {
      const alias = (toolInput.alias || "").trim();
      const { readFileSync } = await import("fs");
      const nodePath = await import("path");

      let filePath;

      // Path-based access: repo/<path> or vault/<path>
      if (alias.startsWith("repo/") || alias.startsWith("vault/")) {
        const [prefix, ...rest] = alias.split("/");
        const relativePath = rest.join("/");
        const baseDir = prefix === "repo" ? "/karma/repo" : "/karma/vault";
        const resolved = nodePath.default.resolve(baseDir, relativePath);

        // Traversal protection: resolved path must stay within base dir
        if (!resolved.startsWith(baseDir + "/") && resolved !== baseDir) {
          return { error: "invalid_path", message: `Path traversal denied. Path must be under ${baseDir}/` };
        }
        filePath = resolved;
      } else {
        // Backward compat: alias lookup
        filePath = VAULT_FILE_ALIASES[alias];
        if (!filePath) {
          return { error: "unknown_alias", message: `Alias '${alias}' not found. Use 'repo/<path>' for repo files, 'vault/<path>' for vault files, or one of: ${Object.keys(VAULT_FILE_ALIASES).join(", ")}` };
        }
      }

      try {
        const content = readFileSync(filePath, "utf8");
        const trimmed = content.slice(0, 20_000); // 20KB cap
        console.log(`[TOOL-API] get_vault_file '${alias}' → ${filePath} (${trimmed.length} chars)`);
        return { ok: true, alias, path: filePath, content: trimmed };
      } catch (e) {
        return { error: "file_read_error", message: e.message };
      }
    }
```

**Step 4: Update tool description (line ~811)**

Change the description from:
```
"Read a canonical Karma file by alias. Available aliases: MEMORY.md, consciousness, collab, candidates, system-prompt, session-handoff, session-summary, core-architecture, cc-brief."
```

To:
```
"Read any file on the vault-neo droplet. Three usage patterns: (1) Named aliases: MEMORY.md, consciousness, collab, candidates, system-prompt, session-handoff, session-summary, core-architecture, cc-brief. (2) Repo path: 'repo/.gsd/STATE.md', 'repo/CLAUDE.md', 'repo/.gsd/ROADMAP.md', etc. (3) Vault path: 'vault/memory_v1/ledger/memory.jsonl', etc. Path traversal is blocked."
```

**Step 5: Commit the changes**

```powershell
cd C:\Users\raest\Documents\Karma_SADE
git add hub-bridge/app/server.js
git commit -m "v11: extend get_vault_file with repo/ and vault/ path-based access + traversal protection"
git push origin main
```

**Step 6: Deploy via karma-hub-deploy skill**

Use `karma-hub-deploy` skill to sync and deploy. The skill handles:
- Syncing server.js from git repo to build context on vault-neo
- Building with --no-cache
- Starting with compose up -d
- Verifying logs

**Step 7: Run the test script**

```bash
bash Scripts/test-vault-file-access.sh
```

Expected: Test 1 PASS, Test 2 PASS, Test 3 PASS (traversal blocked).

---

## Component 2: Payback File Server + get_local_file Tool

### Task 3: Create PowerShell file server script

**Context:** Hub-bridge (on vault-neo) needs to reach Payback's files via Tailscale. We run a minimal HTTP server on Payback that serves `Karma_SADE\` read-only with bearer token auth.

Tailscale IPs:
- Payback: `100.124.194.102`
- vault-neo: `100.92.67.70`

The server binds to `http://+:7771/` (all interfaces, Tailscale-accessible) and serves GET requests for local files.

**Files:**
- Create: `C:\Users\raest\Documents\Karma_SADE\Scripts\karma-file-server.ps1`

**Step 1: Generate a bearer token for the file server**

```powershell
# Run once to generate token, save it
$token = [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
Write-Output "LOCAL_FILE_TOKEN=$token"
# Manually copy this value to hub.env on vault-neo and to the script's $AUTH_TOKEN
```

**Step 2: Write the file server script**

Create `Scripts/karma-file-server.ps1`:

```powershell
param(
    [string]$BaseDir  = 'C:\Users\raest\Documents\Karma_SADE',
    [string]$BindAddr = 'http://+:7771/',
    [string]$TokenFile = 'C:\Users\raest\Documents\Karma_SADE\.local-file-token'
)

$ErrorActionPreference = 'Stop'

# Load token from file (never hardcode)
if (-not (Test-Path $TokenFile)) {
    Write-Error "Token file not found: $TokenFile. Create it with the LOCAL_FILE_TOKEN value."
    exit 1
}
$AUTH_TOKEN = (Get-Content $TokenFile -Raw).Trim()
Write-Output "[karma-file-server] Starting on $BindAddr serving $BaseDir"
Write-Output "[karma-file-server] Token loaded from $TokenFile"

$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add($BindAddr)
$listener.Start()
Write-Output "[karma-file-server] Listening..."

while ($listener.IsListening) {
    try {
        $ctx = $listener.GetContext()
        $req = $ctx.Request
        $res = $ctx.Response

        # Auth check
        $authHeader = $req.Headers['Authorization']
        if ($authHeader -ne "Bearer $AUTH_TOKEN") {
            $res.StatusCode = 401
            $bytes = [System.Text.Encoding]::UTF8.GetBytes('{"error":"unauthorized"}')
            $res.ContentType = 'application/json'
            $res.ContentLength64 = $bytes.Length
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.OutputStream.Close()
            continue
        }

        # Only GET /v1/local-file?path=<encoded-path>
        $url = $req.Url
        if ($req.HttpMethod -ne 'GET' -or $url.AbsolutePath -ne '/v1/local-file') {
            $res.StatusCode = 404
            $bytes = [System.Text.Encoding]::UTF8.GetBytes('{"error":"not_found"}')
            $res.ContentType = 'application/json'
            $res.ContentLength64 = $bytes.Length
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.OutputStream.Close()
            continue
        }

        # Parse path param
        $queryPath = [System.Web.HttpUtility]::ParseQueryString($url.Query)['path']
        if (-not $queryPath) {
            $res.StatusCode = 400
            $bytes = [System.Text.Encoding]::UTF8.GetBytes('{"error":"missing_path"}')
            $res.ContentType = 'application/json'
            $res.ContentLength64 = $bytes.Length
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.OutputStream.Close()
            continue
        }

        # Traversal protection
        $fullPath = [System.IO.Path]::GetFullPath([System.IO.Path]::Combine($BaseDir, $queryPath))
        if (-not $fullPath.StartsWith($BaseDir)) {
            $res.StatusCode = 403
            $bytes = [System.Text.Encoding]::UTF8.GetBytes('{"error":"traversal_denied"}')
            $res.ContentType = 'application/json'
            $res.ContentLength64 = $bytes.Length
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.OutputStream.Close()
            continue
        }

        # Read file
        if (-not (Test-Path $fullPath -PathType Leaf)) {
            $res.StatusCode = 404
            $bytes = [System.Text.Encoding]::UTF8.GetBytes('{"error":"file_not_found","path":"' + $queryPath + '"}')
            $res.ContentType = 'application/json'
            $res.ContentLength64 = $bytes.Length
            $res.OutputStream.Write($bytes, 0, $bytes.Length)
            $res.OutputStream.Close()
            continue
        }

        $content = Get-Content $fullPath -Raw -Encoding UTF8
        if ($content.Length -gt 40000) { $content = $content.Substring(0, 40000) }  # 40KB cap (larger than droplet cap)
        $payload = @{ ok=$true; path=$queryPath; content=$content; bytes=$content.Length } | ConvertTo-Json -Compress
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
        $res.StatusCode = 200
        $res.ContentType = 'application/json'
        $res.ContentLength64 = $bytes.Length
        $res.OutputStream.Write($bytes, 0, $bytes.Length)
        $res.OutputStream.Close()
        Write-Output "[karma-file-server] $(Get-Date -Format 'HH:mm:ss') GET $queryPath (${($content.Length)} chars)"
    } catch {
        Write-Warning "[karma-file-server] Error: $_"
    }
}
```

**Step 3: Create the token file (manual step, never committed)**

```powershell
# Run once to generate and save token
$token = [System.Convert]::ToBase64String([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32))
Set-Content -Path 'C:\Users\raest\Documents\Karma_SADE\.local-file-token' -Value $token -Encoding UTF8 -NoNewline
Write-Output "Token saved. Copy this value for hub.env:"
Write-Output "LOCAL_FILE_TOKEN=$token"
```

The `.local-file-token` file is in `.gitignore` (confirm it matches `*.token` or add explicitly).

**Step 4: Verify .gitignore covers the token file**

```bash
git check-ignore -v "C:/Users/raest/Documents/Karma_SADE/.local-file-token"
```
Expected: Pattern matches. If not: add `.local-file-token` to `.gitignore`.

**Step 5: Test file server manually (before wiring into hub-bridge)**

Open PowerShell as admin and run:
```powershell
cd C:\Users\raest\Documents\Karma_SADE
pwsh -File Scripts\karma-file-server.ps1
```

In a second PowerShell window, test:
```powershell
$token = Get-Content .local-file-token -Raw
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod "http://localhost:7771/v1/local-file?path=.gsd/STATE.md" -Headers $headers
```
Expected: Response JSON with `ok: true` and STATE.md content.

Also test traversal:
```powershell
Invoke-RestMethod "http://localhost:7771/v1/local-file?path=../../Windows/System32/config" -Headers $headers
```
Expected: 403 `traversal_denied`.

**Step 6: Commit the script**

```powershell
cd C:\Users\raest\Documents\Karma_SADE
git add Scripts/karma-file-server.ps1
git add .gitignore  # if modified
git commit -m "v11: add karma-file-server.ps1 for Payback local file access via Tailscale"
git push origin main
```

---

### Task 4: Register karma-file-server as a Windows scheduled task

**Context:** The file server must run permanently like the inbox watcher. Use the same Task Scheduler pattern.

**Files:**
- Create: `C:\Users\raest\Documents\Karma_SADE\Scripts\setup-file-server-task-ADMIN.ps1`

**Step 1: Write the task registration script**

```powershell
param()
# RUN AS ADMINISTRATOR
$ErrorActionPreference = 'Stop'

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: Must run as Administrator" -ForegroundColor Red
    exit 1
}

$BaseDir  = 'C:\Users\raest\Documents\Karma_SADE'
$Script   = "$BaseDir\Scripts\karma-file-server.ps1"
$TaskName = 'KarmaFileServer'
$User     = "$env:USERDOMAIN\$env:USERNAME"

$WatcherArgs = "-WindowStyle Hidden -NonInteractive -File `"$Script`""

Write-Host "[1/3] Removing old task..." -ForegroundColor Cyan
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Host "  Done"

Write-Host "[2/3] Creating task..." -ForegroundColor Cyan

$xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Karma local file server — serves Karma_SADE folder to hub-bridge via Tailscale.</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger><Enabled>true</Enabled></LogonTrigger>
    <BootTrigger><Enabled>true</Enabled></BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>$User</UserId>
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <RestartOnFailure>
      <Interval>PT2M</Interval>
      <Count>9999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>pwsh</Command>
      <Arguments>$WatcherArgs</Arguments>
      <WorkingDirectory>$BaseDir</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"@

$xmlPath = "$env:TEMP\KarmaFileServer.xml"
$xml | Set-Content -Path $xmlPath -Encoding Unicode
Register-ScheduledTask -TaskName $TaskName -Xml (Get-Content $xmlPath -Raw) -Force | Out-Null
Remove-Item $xmlPath -Force
Write-Host "  Task registered" -ForegroundColor Green

Write-Host "[3/3] Starting task..." -ForegroundColor Cyan
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 3
$state = (Get-ScheduledTask -TaskName $TaskName).State
Write-Host "  State: $state" -ForegroundColor $(if ($state -eq 'Running') { 'Green' } else { 'Yellow' })
Write-Host "DONE." -ForegroundColor Green
```

**Step 2: Run it as admin and verify**

Right-click PowerShell → Run as Administrator:
```powershell
pwsh -File C:\Users\raest\Documents\Karma_SADE\Scripts\setup-file-server-task-ADMIN.ps1
```
Expected output ends with `State: Running`.

**Step 3: Test Tailscale reachability from vault-neo**

```bash
TOKEN_VAL=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_bridge/config/hub.env | grep LOCAL_FILE_TOKEN | cut -d= -f2")
ssh vault-neo "curl -s -H 'Authorization: Bearer $TOKEN_VAL' 'http://100.124.194.102:7771/v1/local-file?path=.gsd/STATE.md' | python3 -c \"import sys,json; r=json.load(sys.stdin); print('REACHABLE' if r.get('ok') else r)\""
```
Expected: `REACHABLE` with STATE.md content. If curl fails, check Windows Firewall allows port 7771 inbound on Tailscale interface.

**Windows Firewall rule (if needed):**
```powershell
New-NetFirewallRule -DisplayName 'Karma File Server (Tailscale)' -Direction Inbound -Protocol TCP -LocalPort 7771 -Action Allow -InterfaceAlias 'Tailscale'
```

**Step 4: Commit the task script**

```powershell
cd C:\Users\raest\Documents\Karma_SADE
git add Scripts/setup-file-server-task-ADMIN.ps1
git commit -m "v11: add setup-file-server-task-ADMIN.ps1 for permanent KarmaFileServer task"
git push origin main
```

---

### Task 5: Add get_local_file tool to hub-bridge server.js

**Context:** New deep-mode tool. Hub-bridge calls Payback file server via Tailscale. Uses `LOCAL_FILE_SERVER_URL` and `LOCAL_FILE_TOKEN` from hub.env.

**Files:**
- Modify: `hub-bridge/app/server.js`
- Modify: `hub-bridge/config/hub.env` (on vault-neo — no git copy)

**Step 1: Add hub.env entries on vault-neo**

```bash
# First verify token was generated and noted from Task 3 Step 3
ssh vault-neo "cat >> /opt/seed-vault/memory_v1/hub_bridge/config/hub.env << 'EOF'
LOCAL_FILE_SERVER_URL=http://100.124.194.102:7771
LOCAL_FILE_TOKEN=<paste-the-token-from-.local-file-token>
EOF"
```

Replace `<paste-the-token-from-.local-file-token>` with the actual token value. Verify:
```bash
ssh vault-neo "grep LOCAL_FILE /opt/seed-vault/memory_v1/hub_bridge/config/hub.env"
```

**Step 2: Add tool definition to TOOL_DEFINITIONS array in server.js**

After the `get_vault_file` tool definition (around line 819), add:

```javascript
  {
    name: "get_local_file",
    description: "Read any file from Colby's Karma_SADE folder on Payback (local machine). Path is relative to Karma_SADE root (e.g., '.gsd/STATE.md', 'CLAUDE.md', 'Scripts/karma-inbox-watcher.ps1'). Use this when get_vault_file isn't suitable for local-only files. Returns up to 40KB.",
    input_schema: {
      type: "object",
      properties: {
        path: { type: "string", description: "Relative path within Karma_SADE folder (e.g., '.gsd/STATE.md', 'MEMORY.md', 'Scripts/karma-inbox-watcher.ps1')" },
      },
      required: ["path"],
    },
  },
```

**Step 3: Add environment variable reads near top of server.js**

After existing env var reads (near line 68), add:

```javascript
const LOCAL_FILE_SERVER_URL = process.env.LOCAL_FILE_SERVER_URL || "";
const LOCAL_FILE_TOKEN = process.env.LOCAL_FILE_TOKEN || "";
```

**Step 4: Add get_local_file handler in executeToolCall**

After the `get_vault_file` block (~line 901), add:

```javascript
    // get_local_file — reads files from Payback (local machine) via Tailscale file server
    if (toolName === "get_local_file") {
      const filePath = (toolInput.path || "").trim();
      if (!filePath) return { error: "missing_path", message: "path is required" };
      if (!LOCAL_FILE_SERVER_URL || !LOCAL_FILE_TOKEN) {
        return { error: "not_configured", message: "LOCAL_FILE_SERVER_URL and LOCAL_FILE_TOKEN must be set in hub.env" };
      }
      try {
        const url = `${LOCAL_FILE_SERVER_URL}/v1/local-file?path=${encodeURIComponent(filePath)}`;
        const resp = await fetch(url, {
          headers: { Authorization: `Bearer ${LOCAL_FILE_TOKEN}` },
          signal: AbortSignal.timeout(10_000),
        });
        if (!resp.ok) {
          const body = await resp.text();
          return { error: "file_server_error", status: resp.status, message: body.slice(0, 500) };
        }
        const data = await resp.json();
        console.log(`[TOOL-API] get_local_file '${filePath}' (${(data.content||"").length} chars)`);
        return data;
      } catch (e) {
        return { error: "fetch_error", message: e.message };
      }
    }
```

**Step 5: Update TOOL_DEFINITIONS comment and active tool count**

Change the comment at line ~796 from:
```
// Active tools: graph_query, get_vault_file, write_memory (3 tools — no unhandled stubs)
```
To:
```
// Active tools: graph_query, get_vault_file, get_local_file, write_memory, fetch_url, get_library_docs
```

**Step 6: Update tool list in buildSystemText (line ~436)**

Change:
```
graph_query(cypher), get_vault_file(alias), write_memory(content), fetch_url(url), get_library_docs(library)
```
To:
```
graph_query(cypher), get_vault_file(alias or repo/<path> or vault/<path>), get_local_file(path), write_memory(content), fetch_url(url), get_library_docs(library)
```

**Step 7: Commit**

```powershell
cd C:\Users\raest\Documents\Karma_SADE
git add hub-bridge/app/server.js
git commit -m "v11: add get_local_file tool for Payback Karma_SADE access via Tailscale"
git push origin main
```

**Step 8: Deploy via karma-hub-deploy skill**

Use `karma-hub-deploy` skill. Key: must sync server.js to build context AND use `docker compose up -d` (not `restart`) to pick up new hub.env vars.

**Step 9: Verify with karma-verify skill**

Use `karma-verify` skill to confirm startup and health.

---

### Task 6: End-to-end test of get_local_file

**Step 1: Test via curl**

```bash
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-karma-deep: true" \
  -H "Content-Type: application/json" \
  -d '{"message": "Use get_local_file to read .gsd/STATE.md and tell me what the current FalkorDB node count is"}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('assistant_text','')[:500])"
```
Expected: Karma responds with the FalkorDB count from STATE.md.

**Step 2: Test CLAUDE.md access**

```bash
TOKEN=$(ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt")
curl -s -X POST https://hub.arknexus.net/v1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "x-karma-deep: true" \
  -H "Content-Type: application/json" \
  -d '{"message": "Use get_local_file to read CLAUDE.md and tell me the first rule in the Critical Rules section"}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('assistant_text','')[:500])"
```
Expected: Karma quotes the first Critical Rule.

---

### Task 7: Update system prompt to teach Karma new access patterns

**Context:** Karma's system prompt (`Memory/00-karma-system-prompt-live.md`) needs to know about `repo/<path>` and `vault/<path>` for get_vault_file, and the new get_local_file tool. Update → git commit → git pull on vault-neo → docker restart (no rebuild needed per CLAUDE.md).

**Files:**
- Modify: `C:\Users\raest\Documents\Karma_SADE\Memory\00-karma-system-prompt-live.md`

**Step 1: Find the tool documentation section**

```bash
grep -n "get_vault_file\|get_local_file\|vault_file\|Tools" "C:/Users/raest/Documents/Karma_SADE/Memory/00-karma-system-prompt-live.md" | head -20
```

**Step 2: Update the tool descriptions**

Find the section describing available tools and update the get_vault_file description to include:
```
- get_vault_file(alias): Read droplet files. Three patterns:
  - Named aliases: MEMORY.md, consciousness, collab, candidates, system-prompt, session-handoff, session-summary, core-architecture, cc-brief
  - Repo paths: repo/.gsd/STATE.md, repo/.gsd/ROADMAP.md, repo/CLAUDE.md, repo/Memory/*.md, etc.
  - Vault paths: vault/memory_v1/ledger/memory.jsonl, vault/memory_v1/hub_bridge/config/*, etc.
```

Add get_local_file description:
```
- get_local_file(path): Read files from Colby's Karma_SADE folder on Payback. Path relative to Karma_SADE root. Examples: .gsd/STATE.md, Scripts/karma-inbox-watcher.ps1, hub-bridge/app/server.js (local copy). Use this for local-machine files that aren't on the droplet.
```

**Step 3: Commit and deploy (restart only)**

```powershell
cd C:\Users\raest\Documents\Karma_SADE
git add Memory/00-karma-system-prompt-live.md
git commit -m "v11: update system prompt with get_vault_file path patterns and get_local_file tool"
git push origin main
```

Then on vault-neo:
```bash
ssh vault-neo "cd /home/neo/karma-sade && git pull origin main && docker restart anr-hub-bridge"
```

Wait 10s, verify:
```bash
ssh vault-neo "docker logs anr-hub-bridge --tail 10"
```
Expected: No error, `[INIT] KARMA_IDENTITY_PROMPT loaded` with updated char count.

---

### Task 8: Commit MEMORY.md update and session cleanup

**Step 1: Update MEMORY.md**

Append to MEMORY.md:
```
## Session 74 — v11 Karma Full Read Access (2026-03-10)

**Status:** ✅ COMPLETE

### Changes
- get_vault_file extended: repo/<path> and vault/<path> prefix support + traversal protection
- /opt/seed-vault:/karma/vault:ro volume mount added to compose.hub.yml
- get_local_file tool added: hub-bridge calls Payback file server via Tailscale
- karma-file-server.ps1: PowerShell HTTP server on Payback port 7771
- KarmaFileServer Task Scheduler task registered (always-on, same settings as KarmaInboxWatcher)
- System prompt updated with new tool patterns

### Pitfalls Discovered
- hub.env needs docker compose up -d (not restart) to pick up new vars
- Windows Firewall may need explicit rule for port 7771 on Tailscale interface
- .local-file-token must be in .gitignore BEFORE creating (verify with git check-ignore)
```

**Step 2: Commit**

```powershell
cd C:\Users\raest\Documents\Karma_SADE
git add MEMORY.md
git commit -m "v11: MEMORY.md session wrap-up"
git push origin main
```

**Step 3: Save observations to claude-mem**

Key observations to save:
1. PROOF: get_vault_file path-based access working (repo/ and vault/ prefixes)
2. PROOF: get_local_file tool reading Payback files via Tailscale
3. PITFALL: hub.env env vars require `compose up -d` not `docker restart`
4. DECISION: Payback file server bound to all interfaces (port 7771), auth via bearer token + traversal protection

---

## Execution Order Summary

1. Task 1: Add vault volume mount → commit compose.hub.yml
2. Task 2: Extend get_vault_file in server.js → commit → deploy (karma-hub-deploy)
3. Task 3: Create karma-file-server.ps1 + generate token → commit script
4. Task 4: Register KarmaFileServer task (admin) → verify Tailscale reachability
5. Task 5: Add get_local_file tool to server.js → add hub.env entries → commit → deploy (karma-hub-deploy)
6. Task 6: End-to-end tests
7. Task 7: Update system prompt → git pull → docker restart
8. Task 8: MEMORY.md + claude-mem observations

> **Deploy gate:** Tasks 1+2 can be deployed together (one karma-hub-deploy). Tasks 4+5 require file server running before deploying get_local_file tool (otherwise tool returns "fetch_error").
