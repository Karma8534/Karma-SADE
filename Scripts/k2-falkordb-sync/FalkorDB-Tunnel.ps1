# FalkorDB-Tunnel.ps1
# Keeps SSH tunnel to vault-neo alive and maintains K2 FalkorDB in replica mode.
# Run via Task Scheduler at logon - do not run manually unless testing.

param(
    [string]$VaultNeoHost  = "64.225.13.144",
    [int]$VaultNeoPort     = 22,
    [int]$TunnelLocalPort  = 17687,
    [int]$TunnelRemotePort = 6379,
    [string]$SshKeyPath    = "$env:USERPROFILE\.ssh\id_ed25519",
    [string]$SshUser       = "neo"
)

$LogFile = "$PSScriptRoot\tunnel.log"

function Write-Log {
    param([string]$Msg)
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Msg"
    Add-Content -Path $LogFile -Value $line
    Write-Host $line
}

function Get-FalkorContainer {
    $name = docker ps --filter "ancestor=falkordb/falkordb" --format "{{.Names}}" 2>$null |
            Select-Object -First 1
    if (-not $name) { $name = "falkordb" }  # fallback to well-known name
    return $name
}

function Set-Replication {
    param([string]$Container, [int]$Port)
    $result = docker exec $Container redis-cli REPLICAOF host.docker.internal $Port 2>&1
    Write-Log "[REPLICATION] REPLICAOF host.docker.internal $Port -> $result"
    return ($result -match "OK")
}

Write-Log "[TUNNEL] FalkorDB tunnel keeper started. Key=$SshKeyPath Target=$SshUser@${VaultNeoHost}:$VaultNeoPort"

while ($true) {
    Write-Log "[TUNNEL] Opening tunnel K2:$TunnelLocalPort -> ${VaultNeoHost}:$TunnelRemotePort"

    # Build ssh argument list
    $sshArgList = @(
        "-N",
        "-o", "StrictHostKeyChecking=no",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=3",
        "-i", $SshKeyPath,
        "-p", "$VaultNeoPort",
        "-L", "0.0.0.0:${TunnelLocalPort}:localhost:${TunnelRemotePort}",
        "${SshUser}@${VaultNeoHost}"
    )

    # Start SSH as a real Windows process (not a PS job) so it stays alive
    $proc = Start-Process -FilePath "ssh" `
                          -ArgumentList $sshArgList `
                          -PassThru `
                          -NoNewWindow

    # Wait for tunnel to stabilise
    Start-Sleep -Seconds 3

    # Issue REPLICAOF
    $container = Get-FalkorContainer
    $ok = Set-Replication -Container $container -Port $TunnelLocalPort
    if (-not $ok) {
        Write-Log "[REPLICATION] WARNING: REPLICAOF did not return OK - will retry on next reconnect"
    }

    # Wait for SSH process to exit (means tunnel died or was killed)
    $proc.WaitForExit()
    $exitCode = $proc.ExitCode
    $proc.Dispose()
    Write-Log "[TUNNEL] Tunnel exited (code=$exitCode). Reconnecting in 10s..."
    Start-Sleep -Seconds 10
}
