param(
  [string]$RunDir,
  [int]$Concurrency = 40,
  [string]$LocalBase = 'http://127.0.0.1:7891',
  [string]$RemoteBase = 'https://hub.arknexus.net'
)

$ErrorActionPreference = 'Stop'

if (-not $RunDir) {
  throw 'RunDir is required.'
}

if (-not (Test-Path -LiteralPath $RunDir)) {
  throw "RunDir not found: $RunDir"
}

$sessionPath = Join-Path $RunDir 'session.json'
if (-not (Test-Path -LiteralPath $sessionPath)) {
  throw "session.json missing: $sessionPath"
}

$session = Get-Content -LiteralPath $sessionPath -Raw | ConvertFrom-Json
$sessionId = [string]$session.session_id
if (-not $sessionId) {
  throw 'session_id missing in session.json'
}

$token = (ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt").Trim()
if (-not $token) {
  throw 'Hub token empty.'
}

$stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssZ')
$probePrefix = "STRESS-PROBE-$stamp"
$resultsPath = Join-Path $RunDir 'phase2-stress.json'
$diffPath = Join-Path $RunDir 'phase2-stress-diff.txt'

$jobs = @()
$start = Get-Date
for ($i = 1; $i -le $Concurrency; $i++) {
  $txt = "$probePrefix-$i"
  $jobs += Start-Job -ScriptBlock {
    param($Base, $Sid, $BodyText)
    $payload = @{ turn = $BodyText; role = 'user' } | ConvertTo-Json
    $attempts = 0
    $maxAttempts = 8
    while ($attempts -lt $maxAttempts) {
      $attempts++
      try {
        Invoke-RestMethod -Uri "$Base/v1/session/$Sid" -Method Post -Body $payload -ContentType 'application/json' -TimeoutSec 30 | Out-Null
        return @{ ok = $true; probe = $BodyText; attempts = $attempts }
      } catch {
        $msg = [string]$_.Exception.Message
        if ($msg -match '429' -and $attempts -lt $maxAttempts) {
          Start-Sleep -Milliseconds (350 * $attempts)
          continue
        }
        return @{ ok = $false; probe = $BodyText; attempts = $attempts; error = $msg }
      }
    }
  } -ArgumentList $LocalBase, $sessionId, $txt
}

Wait-Job -Job $jobs | Out-Null
$jobOut = $jobs | Receive-Job
$jobs | Remove-Job -Force | Out-Null
$end = Get-Date

$local = Invoke-RestMethod -Uri "$LocalBase/v1/session/$sessionId" -TimeoutSec 30
$remote = Invoke-RestMethod -Uri "$RemoteBase/v1/session/$sessionId" -Headers @{ Authorization = "Bearer $token" } -TimeoutSec 30

$localLines = @()
foreach ($h in @($local.history | Select-Object -Last 500)) {
  $role = if ($h.body.role) { [string]$h.body.role } else { '' }
  $txt = if ($h.text) { [string]$h.text } elseif ($h.body.content) { [string]$h.body.content } else { '' }
  $localLines += "$role|$txt"
}
$remoteLines = @()
foreach ($h in @($remote.history | Select-Object -Last 500)) {
  $role = if ($h.body.role) { [string]$h.body.role } else { '' }
  $txt = if ($h.text) { [string]$h.text } elseif ($h.body.content) { [string]$h.body.content } else { '' }
  $remoteLines += "$role|$txt"
}

$missingRemote = @()
for ($i = 1; $i -le $Concurrency; $i++) {
  $probe = "$probePrefix-$i"
  $has = $false
  foreach ($line in $remoteLines) {
    if ($line -like "*$probe*") { $has = $true; break }
  }
  if (-not $has) { $missingRemote += $probe }
}

$missingLocal = @()
for ($i = 1; $i -le $Concurrency; $i++) {
  $probe = "$probePrefix-$i"
  $has = $false
  foreach ($line in $localLines) {
    if ($line -like "*$probe*") { $has = $true; break }
  }
  if (-not $has) { $missingLocal += $probe }
}

$historyMatch = (($localLines -join "`n") -eq ($remoteLines -join "`n"))

$diffLines = @()
$diffLines += "session_id: $sessionId"
$diffLines += "probe_prefix: $probePrefix"
$diffLines += "local_history_count: $($localLines.Count)"
$diffLines += "remote_history_count: $($remoteLines.Count)"
$diffLines += "history_match: $historyMatch"
$diffLines += "missing_on_remote: $($missingRemote.Count)"
if ($missingRemote.Count -gt 0) { $diffLines += ($missingRemote -join ', ') }
$diffLines += "missing_on_local: $($missingLocal.Count)"
if ($missingLocal.Count -gt 0) { $diffLines += ($missingLocal -join ', ') }
$diffLines | Set-Content -LiteralPath $diffPath -Encoding UTF8

$passed = ($missingRemote.Count -eq 0 -and $missingLocal.Count -eq 0 -and $historyMatch)

@{
  ok = $true
  session_id = $sessionId
  started_utc = $start.ToUniversalTime().ToString('o')
  ended_utc = $end.ToUniversalTime().ToString('o')
  concurrency = $Concurrency
  probe_prefix = $probePrefix
  post_results = @($jobOut)
  posted_ok_count = @($jobOut | Where-Object { $_.ok }).Count
  posted_fail_count = @($jobOut | Where-Object { -not $_.ok }).Count
  missing_remote_count = $missingRemote.Count
  missing_local_count = $missingLocal.Count
  history_match = $historyMatch
  gate_pass = $passed
  artifacts = @($resultsPath, $diffPath)
} | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $resultsPath -Encoding UTF8

Get-Content -LiteralPath $resultsPath -Raw
