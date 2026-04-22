# HARNESS_GATE: G3
# Phase 2 parity harness -- G3_PARITY_BROWSER_SCREEN (probe injection + session equality)
# Rewritten Phase 3 (S182). SESSION_ID injection; emits probe line for phase3-family CDP capture.
param(
  [string]$RunDir,
  [string]$JulianExe = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\arknexusv6.exe',
  [string]$LocalBase = 'http://127.0.0.1:7891',
  [string]$RemoteBase = 'https://hub.arknexus.net',
  [int]$DeadlineMs = 5000,
  [switch]$WhatIf
)
$ErrorActionPreference = 'Stop'

if ($WhatIf) {
  Write-Host 'HARNESS_GATE: G3'
  Write-Host 'Probe plan:'
  Write-Host '  1. Load session.json -> SESSION_ID'
  Write-Host '  2. POST PARITY-PROBE-{SESSION_ID} to LocalBase /v1/session/{id}'
  Write-Host '  3. Poll RemoteBase for probe until DeadlineMs'
  Write-Host '  4. Reverse probe: RemoteBase -> LocalBase'
  Write-Host '  5. GET both sides; byte-compare last-20 history'
  Write-Host '  6. Screenshot + emit phase2-parity.png, phase2-roundtrip.json, phase2-session-equality.txt'
  Write-Host '  7. Write probe-value to phase2-probe.txt (phase3-family CDP capture target)'
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

$png = Join-Path $RunDir 'phase2-parity.png'
$rt = Join-Path $RunDir 'phase2-roundtrip.json'
$eq = Join-Path $RunDir 'phase2-session-equality.txt'
$probePath = Join-Path $RunDir 'phase2-probe.txt'

function Has-Probe([string]$base, [string]$probe, [bool]$auth) {
  try {
    $h = @{}
    if ($auth) { $h.Authorization = "Bearer $token" }
    $r = Invoke-RestMethod -Uri "$base/v1/session/$sessionId" -Headers $h -TimeoutSec 10
    foreach ($x in @($r.history)) {
      $txt = ''
      if ($x.text) { $txt = $x.text } elseif ($x.body.content) { $txt = $x.body.content }
      if ($txt -like "*$probe*") { return $true }
    }
  } catch {}
  return $false
}

function Post-Turn([string]$base, [string]$txt, [bool]$auth) {
  $h = @{ 'Content-Type' = 'application/json' }
  if ($auth) { $h.Authorization = "Bearer $token" }
  $b = @{ turn = $txt; role = 'user' } | ConvertTo-Json
  Invoke-RestMethod -Uri "$base/v1/session/$sessionId" -Method Post -Headers $h -Body $b -TimeoutSec 30 | Out-Null
}

$p1 = "PARITY-PROBE-$sessionId-" + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
$p1 | Set-Content -LiteralPath $probePath -Encoding UTF8
$sw1 = [Diagnostics.Stopwatch]::StartNew()
Post-Turn $LocalBase $p1 $false
$lr = -1
while ($sw1.ElapsedMilliseconds -lt 30000) {
  if (Has-Probe $RemoteBase $p1 $true) { $lr = $sw1.ElapsedMilliseconds; break }
  Start-Sleep -Milliseconds 400
}

$p2 = "PARITY-PROBE-REV-$sessionId-" + (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmssfffZ')
$sw2 = [Diagnostics.Stopwatch]::StartNew()
Post-Turn $RemoteBase $p2 $true
$rl = -1
while ($sw2.ElapsedMilliseconds -lt 30000) {
  if (Has-Probe $LocalBase $p2 $false) { $rl = $sw2.ElapsedMilliseconds; break }
  Start-Sleep -Milliseconds 400
}

$lh = Invoke-RestMethod -Uri "$LocalBase/v1/session/$sessionId" -TimeoutSec 12
$rh = Invoke-RestMethod -Uri "$RemoteBase/v1/session/$sessionId" -Headers @{ Authorization = "Bearer $token" } -TimeoutSec 12

$ll = @()
foreach ($h in @($lh.history | Select-Object -Last 20)) {
  $role = if ($h.body.role) { $h.body.role } else { '' }
  $txt = if ($h.text) { $h.text } elseif ($h.body.content) { $h.body.content } else { '' }
  $ll += "$role|$txt"
}
$rr = @()
foreach ($h in @($rh.history | Select-Object -Last 20)) {
  $role = if ($h.body.role) { $h.body.role } else { '' }
  $txt = if ($h.text) { $h.text } elseif ($h.body.content) { $h.body.content } else { '' }
  $rr += "$role|$txt"
}

Get-Process julian, arknexusv6, msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1
Start-Process -FilePath $JulianExe | Out-Null
Start-Sleep -Seconds 6
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left, $b.Top, 0, 0, $b.Size)
$g.Dispose()
$bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

$histMatch = (($ll -join "`n") -eq ($rr -join "`n"))
$sidMatch = ([string]$lh.session_id -eq [string]$rh.session_id)
$l2rOk = ($lr -ge 0 -and $lr -lt $DeadlineMs)
$r2lOk = ($rl -ge 0 -and $rl -lt $DeadlineMs)

[ordered]@{
  session_id = $sessionId
  timestamp = (Get-Date).ToUniversalTime().ToString('o')
  probe_local_to_remote = $p1
  probe_remote_to_local = $p2
  local_to_remote_ms = $lr
  remote_to_local_ms = $rl
  deadline_ms = $DeadlineMs
  local_to_remote_within_deadline = $l2rOk
  remote_to_local_within_deadline = $r2lOk
  session_id_match = $sidMatch
  history_match = $histMatch
  gate_g3_probe_emitted = $true
  gate_g3_pass = ($l2rOk -and $r2lOk -and $sidMatch)
} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $rt -Encoding UTF8

$lines = @("session_id: $sessionId", "session_id match: $sidMatch", "history match: $histMatch", '', 'local:')
$lines += $ll
$lines += ''
$lines += 'remote:'
$lines += $rr
$lines | Set-Content -LiteralPath $eq -Encoding UTF8
Write-Host "phase2-parity: sid=$sessionId l2r=$lr r2l=$rl match=$histMatch probe=$p1"
