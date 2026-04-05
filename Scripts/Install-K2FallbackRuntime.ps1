$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\raest\Documents\Karma_SADE"
$serviceDir = Join-Path $repoRoot "Scripts\\systemd"
$vaultHost = "vault-neo"
$k2Ssh = "ssh -p 2223 -l karma -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes localhost"

function Invoke-K2Command {
    param([Parameter(Mandatory = $true)][string]$Command)
    & ssh $vaultHost "$k2Ssh ""$Command"""
    if ($LASTEXITCODE -ne 0) {
        throw "K2 command failed: $Command"
    }
}

function Copy-ToK2 {
    param(
        [Parameter(Mandatory = $true)][string]$LocalPath,
        [Parameter(Mandatory = $true)][string]$RemotePath
    )
    if (-not (Test-Path $LocalPath)) {
        throw "Missing local file: $LocalPath"
    }
    $name = [System.IO.Path]::GetFileName($RemotePath)
    $vaultTemp = "/tmp/$name"
    $k2Temp = "/tmp/$name"
    & scp -q $LocalPath "${vaultHost}:$vaultTemp"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to copy $LocalPath to $vaultHost"
    }
    $copyCmd = "scp -q -P 2223 -o StrictHostKeyChecking=no -o ConnectTimeout=8 -o BatchMode=yes $vaultTemp karma@localhost:$k2Temp && $k2Ssh ""sudo install -o root -g root -m 0644 $k2Temp $RemotePath && rm -f $k2Temp"" && rm -f $vaultTemp"
    & ssh $vaultHost $copyCmd
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install $RemotePath on K2"
    }
}

$units = @(
    @{ Local = Join-Path $serviceDir "karma-regent.service"; Remote = "/etc/systemd/system/karma-regent.service" },
    @{ Local = Join-Path $serviceDir "aria.service"; Remote = "/etc/systemd/system/aria.service" },
    @{ Local = Join-Path $serviceDir "cc-ascendant-watchdog.service"; Remote = "/etc/systemd/system/cc-ascendant-watchdog.service" },
    @{ Local = Join-Path $serviceDir "cc-ascendant-watchdog.timer"; Remote = "/etc/systemd/system/cc-ascendant-watchdog.timer" }
)

foreach ($unit in $units) {
    Copy-ToK2 -LocalPath $unit.Local -RemotePath $unit.Remote | Out-Null
}

Invoke-K2Command "sudo systemctl daemon-reload"
Invoke-K2Command "sudo systemctl enable karma-regent aria cc-ascendant-watchdog.timer"
Invoke-K2Command "sudo systemctl restart karma-regent aria"
Invoke-K2Command "sudo systemctl start cc-ascendant-watchdog.timer"
Invoke-K2Command "systemctl is-enabled karma-regent aria cc-ascendant-watchdog.timer; echo ---; systemctl is-active karma-regent aria cc-ascendant-watchdog.timer"
