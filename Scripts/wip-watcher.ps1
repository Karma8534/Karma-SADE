# wip-watcher.ps1
# Watches docs/wip for new files and auto-ingests them via /v1/ingest.
# Drop any PDF, MD, or TXT into docs/wip — CC and Karma will pick it up.
#
# Install as scheduled task (run at login):
#   $action = New-ScheduledTaskAction -Execute "pwsh" -Argument "-WindowStyle Hidden -File C:\Users\raest\Documents\Karma_SADE\Scripts\wip-watcher.ps1"
#   $trigger = New-ScheduledTaskTrigger -AtLogOn
#   Register-ScheduledTask -TaskName "KarmaWipWatcher" -Action $action -Trigger $trigger -RunLevel Highest

param(
    [string]$WipPath  = "C:\Users\raest\Documents\Karma_SADE\docs\wip",
    [string]$HubUrl   = "https://hub.arknexus.net/v1/ingest",
    [string]$TokenFile = "C:\Users\raest\Documents\Karma_SADE\.hub-chat-token"
)

$ErrorActionPreference = "Continue"

if (-not (Test-Path $WipPath)) { New-Item -ItemType Directory -Path $WipPath -Force | Out-Null }

function Get-Token {
    if (Test-Path $TokenFile) { return (Get-Content $TokenFile -Raw).Trim() }
    # Fallback: fetch live from vault-neo
    try {
        $t = & ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt" 2>$null
        if ($t) { Set-Content -Path $TokenFile -Value $t.Trim(); return $t.Trim() }
    } catch {}
    Write-Host "[wip-watcher] ERROR: no token available"
    return $null
}

function Send-File {
    param([string]$FilePath)
    $token = Get-Token
    if (-not $token) { Write-Host "[wip-watcher] SKIP (no token): $FilePath"; return }

    $filename = Split-Path $FilePath -Leaf
    $ext = [System.IO.Path]::GetExtension($filename).ToLower()
    $mimeType = switch ($ext) {
        ".pdf"  { "application/pdf" }
        ".md"   { "text/markdown" }
        ".txt"  { "text/plain" }
        default { "application/octet-stream" }
    }

    Write-Host "[wip-watcher] Ingesting: $filename"
    try {
        $bytes  = [System.IO.File]::ReadAllBytes($FilePath)
        $b64    = [Convert]::ToBase64String($bytes)
        $body   = @{ filename = $filename; content = $b64; mime_type = $mimeType; source = "docs/wip"; priority = $true } | ConvertTo-Json
        $resp   = Invoke-RestMethod -Uri $HubUrl -Method Post -Body $body -ContentType "application/json" `
                    -Headers @{ Authorization = "Bearer $token" } -TimeoutSec 60
        Write-Host "[wip-watcher] OK: $filename → $($resp | ConvertTo-Json -Compress)"
    } catch {
        Write-Host "[wip-watcher] ERROR ingesting $filename`: $_"
    }
}

# Process any existing files at startup
Get-ChildItem -Path $WipPath -File | Where-Object { $_.Name -ne ".gitkeep" } | ForEach-Object {
    Send-File $_.FullName
}

# Watch for new files
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path   = $WipPath
$watcher.Filter = "*.*"
$watcher.EnableRaisingEvents = $true
$watcher.IncludeSubdirectories = $false

Write-Host "[wip-watcher] Watching: $WipPath"

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $name = $Event.SourceEventArgs.Name
    if ($name -eq ".gitkeep") { return }
    Start-Sleep -Seconds 1  # let write complete
    & $using:function:Send-File -FilePath $path
}

$null = Register-ObjectEvent $watcher Created -Action {
    $path = $Event.SourceEventArgs.FullPath
    $name = $Event.SourceEventArgs.Name
    if ($name -eq ".gitkeep") { return }
    Start-Sleep -Seconds 1
    $token = & ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt" 2>$null
    if (-not $token) { Write-Host "[wip-watcher] SKIP (no token): $name"; return }
    $filename = $name
    $ext = [System.IO.Path]::GetExtension($filename).ToLower()
    $mimeType = switch ($ext) {
        ".pdf" { "application/pdf" }
        ".md"  { "text/markdown" }
        ".txt" { "text/plain" }
        default { "application/octet-stream" }
    }
    Write-Host "[wip-watcher] Ingesting: $filename"
    try {
        $bytes = [System.IO.File]::ReadAllBytes($path)
        $b64   = [Convert]::ToBase64String($bytes)
        $body  = @{ filename = $filename; content = $b64; mime_type = $mimeType; source = "docs/wip"; priority = $true } | ConvertTo-Json
        $resp  = Invoke-RestMethod -Uri "https://hub.arknexus.net/v1/ingest" -Method Post -Body $body `
                    -ContentType "application/json" -Headers @{ Authorization = "Bearer $token" } -TimeoutSec 60
        Write-Host "[wip-watcher] OK: $filename"
    } catch {
        Write-Host "[wip-watcher] ERROR: $_"
    }
}

# Keep alive
while ($true) { Start-Sleep -Seconds 30 }
