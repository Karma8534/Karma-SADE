# Start-ClaudeMemWorker.ps1
# Ensures a single claude-mem worker process is running on the configured port.

$ErrorActionPreference = "Stop"

function Get-ClaudeMemSettings {
    $default = @{
        Port = "37778"
        ChromaEnabled = "false"
    }
    $settingsPath = Join-Path $env:USERPROFILE ".claude-mem\settings.json"
    if (-not (Test-Path $settingsPath)) { return $default }
    try {
        $cfg = Get-Content $settingsPath -Raw | ConvertFrom-Json
        $port = [string]($cfg.CLAUDE_MEM_WORKER_PORT)
        if ([string]::IsNullOrWhiteSpace($port)) { $port = $default.Port }
        $chroma = [string]($cfg.CLAUDE_MEM_CHROMA_ENABLED)
        if ([string]::IsNullOrWhiteSpace($chroma)) { $chroma = $default.ChromaEnabled }
        return @{ Port = $port; ChromaEnabled = $chroma }
    } catch {
        return $default
    }
}

function Get-ClaudeMemScriptsDir {
    $base = Join-Path $env:USERPROFILE ".claude\plugins\cache\thedotmack\claude-mem"
    if (-not (Test-Path $base)) { return $null }
    $dirs = Get-ChildItem -Path $base -Directory | Sort-Object Name -Descending
    foreach ($d in $dirs) {
        $scripts = Join-Path $d.FullName "scripts"
        if (Test-Path (Join-Path $scripts "worker-service.cjs")) { return $scripts }
    }
    return $null
}

function Test-Health($port) {
    try {
        $resp = Invoke-RestMethod -Uri "http://127.0.0.1:$port/health" -Method Get -TimeoutSec 3
        return $resp.status -eq "ok" -or $resp.ok -eq $true
    } catch {
        return $false
    }
}

$cfg = Get-ClaudeMemSettings
$port = $cfg.Port
$scriptsDir = Get-ClaudeMemScriptsDir
if (-not $scriptsDir) {
    Write-Host "claude-mem scripts not found"
    exit 1
}

if (Test-Health -port $port) {
    Write-Host "claude-mem already healthy on $port"
    exit 0
}

$runner = Join-Path $scriptsDir "bun-runner.js"
$worker = Join-Path $scriptsDir "worker-service.cjs"
if (-not (Test-Path $runner) -or -not (Test-Path $worker)) {
    Write-Host "missing runner or worker script"
    exit 1
}

# Avoid duplicate launch loops from old detached shells.
$existing = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq "node.exe" -and $_.CommandLine -match "worker-service\.cjs start"
}
if ($existing) {
    foreach ($p in $existing) {
        try { Stop-Process -Id $p.ProcessId -Force -ErrorAction Stop } catch {}
    }
    Start-Sleep -Seconds 1
}

$env:CLAUDE_MEM_WORKER_PORT = $port
$env:CLAUDE_MEM_CHROMA_ENABLED = [string]$cfg.ChromaEnabled

Start-Process -FilePath "node" -ArgumentList @($runner, $worker, "start") -WindowStyle Hidden -WorkingDirectory $scriptsDir
Start-Sleep -Seconds 3

if (Test-Health -port $port) {
    Write-Host "claude-mem started on $port"
    exit 0
}

Write-Host "claude-mem failed to become healthy on $port"
exit 2
