# HARNESS_GATE: G4
# Phase 2 stress harness -- G4_PARITY_STRESS (40 concurrent POSTs, byte-compare)
# Rewritten Phase 3 (S182). SESSION_ID injection; STRESS-{SESSION_ID}-{n} probes.
param(
  [string]$RunDir,
  [int]$Concurrency = 40,
  [int]$SettleSeconds = 5,
  [string]$LocalBase = 'http://127.0.0.1:7891',
  [string]$RemoteBase = 'https://hub.arknexus.net',
  [switch]$WhatIf
)
$ErrorActionPreference = 'Stop'

if ($WhatIf) {
  Write-Host 'HARNESS_GATE: G4'
  Write-Host 'Probe plan:'
  Write-Host '  1. Load session.json -> SESSION_ID'
  Write-Host "  2. Fire $Concurrency parallel POSTs labelled STRESS-{SESSION_ID}-{n}"
  Write-Host "  3. Wait $SettleSeconds s settle"
  Write-Host '  4. GET both /v1/session/{id}; byte-compare last-500 history'
  Write-Host '  5. Cite cc_server_p1.py:line for atomic write-tmp+fsync+rename'
  Write-Host '  6. Emit phase2-stress.json, phase2-stress-diff.txt'
  exit 0
}

if (-not $RunDir) { throw 'RunDir is required.' }
if (-not (Test-Path -LiteralPath $RunDir)) { throw "RunDir not found: $RunDir" }
$sessionPath = Join-Path $RunDir 'session.json'
if (-not (Test-Path -LiteralPath $sessionPath)) { throw "session.json missing: $sessionPath" }
$session = Get-Content -LiteralPath $sessionPath -Raw | ConvertFrom-Json
$sessionId = [string]$session.session_id
if (-not $sessionId) { throw 'session_id missing in session.json' }

$token = (ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt').Trim()
if (-not $token) { throw 'Hub token empty.' }

$probePrefix = "STRESS-$sessionId"
$resultsPath = Join-Path $RunDir 'phase2-stress.json'
$diffPath = Join-Path $RunDir 'phase2-stress-diff.txt'

# Cite atomic-rename file:line (G4 predicate)
$ccServerPath = Join-Path (Split-Path $PSScriptRoot -Parent) 'Scripts\cc_server_p1.py'
$atomicCite = 'not_found'
if (Test-Path -LiteralPath $ccServerPath) {
  $match = Select-String -LiteralPath $ccServerPath -Pattern 'os\.replace|os\.rename|fsync' | Select-Object -First 1
  if ($match) { $atomicCite = "$($match.Filename):$($match.LineNumber)" }
}

$jobs = @()
$start = Get-Date
for ($i = 1; $i -le $Concurrency; $i++) {
  $txt = "$probePrefix-$i"
  $jobs += Start-Job -ScriptBlock {
    param($Base, $Sid, $BodyText)
    $payload = @{ turn = $BodyText; role = 'user' } | ConvertTo-Json
    $attempts = 0
    while ($attempts -lt 8) {
      $attempts++
      try {
        Invoke-RestMethod -Uri "$Base/v1/session/$Sid" -Method Post -Body $payload -ContentType 'application/json' -TimeoutSec 30 | Out-Null
        return @{ ok = $true; probe = $BodyText; attempts = $attempts }
      } catch {
        $msg = [string]$_.Exception.Message
        if ($msg -match '429' -and $attempts -lt 8) { Start-Sleep -Milliseconds (350 * $attempts); continue }
        return @{ ok = $false; probe = $BodyText; attempts = $attempts; error = $msg }
      }
    }
  } -ArgumentList $LocalBase, $sessionId, $txt
}
Wait-Job -Job $jobs | Out-Null
$jobOut = $jobs | Receive-Job
$jobs | Remove-Job -Force | Out-Null
$end = Get-Date

Start-Sleep -Seconds $SettleSeconds

$local = Invoke-RestMethod -Uri "$LocalBase/v1/session/$sessionId" -TimeoutSec 30
$remote = Invoke-RestMethod -Uri "$RemoteBase/v1/session/$sessionId" -Headers @{ Authorization = "Bearer $token" } -TimeoutSec 30

$localLines = @()
foreach ($h in @($local.history | Select-Object -Last 500)) {
  $role = if ($h.body.role) { $h.body.role } else { '' }
  $txt = if ($h.text) { $h.text } elseif ($h.body.content) { $h.body.content } else { '' }
  $localLines += "$role|$txt"
}
$remoteLines = @()
foreach ($h in @($remote.history | Select-Object -Last 500)) {
  $role = if ($h.body.role) { $h.body.role } else { '' }
  $txt = if ($h.text) { $h.text } elseif ($h.body.content) { $h.body.content } else { '' }
  $remoteLines += "$role|$txt"
}

$missingRemote = @()
$missingLocal = @()
for ($i = 1; $i -le $Concurrency; $i++) {
  $probe = "$probePrefix-$i"
  if (-not ($remoteLines | Where-Object { $_ -like "*$probe*" })) { $missingRemote += $probe }
  if (-not ($localLines | Where-Object { $_ -like "*$probe*" })) { $missingLocal += $probe }
}
$historyMatch = (($localLines -join "`n") -eq ($remoteLines -join "`n"))

$diffLines = @(
  "session_id: $sessionId",
  "probe_prefix: $probePrefix",
  "local_history_count: $($localLines.Count)",
  "remote_history_count: $($remoteLines.Count)",
  "history_match: $historyMatch",
  "missing_on_remote: $($missingRemote.Count)"
)
if ($missingRemote.Count -gt 0) { $diffLines += ($missingRemote -join ', ') }
$diffLines += "missing_on_local: $($missingLocal.Count)"
if ($missingLocal.Count -gt 0) { $diffLines += ($missingLocal -join ', ') }
$diffLines += "atomic_write_cite: $atomicCite"
$diffLines | Set-Content -LiteralPath $diffPath -Encoding UTF8

$passed = ($missingRemote.Count -eq 0 -and $missingLocal.Count -eq 0 -and $historyMatch -and $atomicCite -ne 'not_found')

[ordered]@{
  session_id = $sessionId
  started_utc = $start.ToUniversalTime().ToString('o')
  ended_utc = $end.ToUniversalTime().ToString('o')
  concurrency = $Concurrency
  probe_prefix = $probePrefix
  posted_ok_count = @($jobOut | Where-Object { $_.ok }).Count
  posted_fail_count = @($jobOut | Where-Object { -not $_.ok }).Count
  missing_remote_count = $missingRemote.Count
  missing_local_count = $missingLocal.Count
  history_match = $historyMatch
  atomic_write_cite = $atomicCite
  gate_g4_pass = $passed
  artifacts = @($resultsPath, $diffPath)
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resultsPath -Encoding UTF8
Write-Host "phase2-stress: sid=$sessionId ok=$(@($jobOut|Where-Object{$_.ok}).Count)/$Concurrency match=$historyMatch cite=$atomicCite"
