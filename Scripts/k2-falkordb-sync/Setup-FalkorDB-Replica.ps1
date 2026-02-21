# Setup-FalkorDB-Replica.ps1
# Run ONCE on K2 via RDP to install the FalkorDB tunnel keeper.
# Must be run as the karma user (not Administrator) so Task Scheduler
# uses the correct SSH key at C:\Users\karma\.ssh\id_ed25519

$InstallDir   = "C:\Users\karma\FalkorDB-Sync"
$TunnelScript = Join-Path $InstallDir "FalkorDB-Tunnel.ps1"
$TaskName     = "FalkorDB-Vault-Tunnel"

Write-Host "=== FalkorDB Replica Setup ==="
Write-Host "Install dir: $InstallDir"

# 1. Create install directory
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Write-Host "[1/5] Created $InstallDir"

# 2. Copy tunnel script (this script must live next to FalkorDB-Tunnel.ps1)
$srcScript = Join-Path $PSScriptRoot "FalkorDB-Tunnel.ps1"
if (-not (Test-Path $srcScript)) {
    Write-Error "FalkorDB-Tunnel.ps1 not found next to this script at: $srcScript"
    exit 1
}
Copy-Item -Path $srcScript -Destination $TunnelScript -Force
Write-Host "[2/5] Copied FalkorDB-Tunnel.ps1 to $InstallDir"

# 3. Verify SSH key exists
$sshKey = "C:\Users\karma\.ssh\id_ed25519"
if (-not (Test-Path $sshKey)) {
    Write-Error "SSH key not found at: $sshKey - cannot proceed"
    exit 1
}
Write-Host "[3/5] SSH key verified at $sshKey"

# 4. Register Task Scheduler task
$taskArg = "-WindowStyle Hidden -ExecutionPolicy Bypass -NonInteractive -File `"$TunnelScript`""
$action   = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $taskArg
$trigger  = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -RestartCount 5 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

# Remove existing task if present
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask `
    -TaskName    $TaskName `
    -Action      $action `
    -Trigger     $trigger `
    -Settings    $settings `
    -Description "Maintains SSH tunnel to vault-neo FalkorDB and keeps K2 FalkorDB in replica mode" `
    -RunLevel    Highest | Out-Null

Write-Host "[4/5] Registered scheduled task '$TaskName' (triggers: AtLogOn)"

# 5. Start the task now
Start-ScheduledTask -TaskName $TaskName
Start-Sleep -Seconds 5
$state = (Get-ScheduledTask -TaskName $TaskName).State
Write-Host "[5/5] Task started. Current state: $state"

Write-Host ""
Write-Host "=== Setup complete ==="
Write-Host "Monitor: Get-ScheduledTask -TaskName '$TaskName'"
Write-Host "Logs:    $InstallDir\tunnel.log"
Write-Host "Stop:    Stop-ScheduledTask -TaskName '$TaskName'"
Write-Host "Test:    docker exec falkordb redis-cli INFO replication"
