# ascendance-drain-queue.ps1 — Drain pending dual-write queue entries
# HARNESS_GATE: queue-drain
param(
  [Parameter(Mandatory=$true)][string]$RunDir
)
$ErrorActionPreference = 'Stop'
$queuePath = Join-Path $RunDir 'dual-write-queue.jsonl'
if (-not (Test-Path $queuePath)) { Write-Host 'no-queue'; exit 0 }

$lines = Get-Content $queuePath | Where-Object { $_.Trim().Length -gt 0 }
if (-not $lines) { Write-Host 'queue-empty'; exit 0 }

$updated = @()
$pendingBefore = 0
$confirmedAfter = 0
foreach ($line in $lines) {
  try {
    $e = $line | ConvertFrom-Json
    if ($e.state -eq 'confirmed') { $updated += $line; $confirmedAfter += 1; continue }
    $pendingBefore += 1
    # Retry via dual-write
    & (Join-Path $PSScriptRoot 'ascendance-dual-write.ps1') -Type $e.type -Title $e.title -Text $e.text -Gate $e.gate -RunDir $RunDir | Out-Null
    # re-read last line
    $newLines = Get-Content $queuePath
    $updated += $newLines[-1]
    $confirmedAfter += 1
  } catch {
    $updated += $line
  }
}
Set-Content -Path $queuePath -Value $updated -Encoding utf8NoBOM
Write-Host "pending_before=$pendingBefore confirmed_after=$confirmedAfter"
exit 0
