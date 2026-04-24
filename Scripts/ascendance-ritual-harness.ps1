# HARNESS_GATE: G7
# Ascendance ritual harness -- G7_RITUAL_STEP10_FIRST_PAINT.
# Rewritten Phase 3 (S182). SESSION_ID in probe; wired to ritual-recorder; fresh browser per G6.
param(
  [string]$RunDir,
  [string]$JulianExe = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\arknexusv6.exe',
  [string]$ChromeExe,
  [string]$LocalBase = 'http://127.0.0.1:7891',
  [string]$RemoteBase = 'https://hub.arknexus.net',
  [ValidateSet('mp4', 'pngseq')] [string]$RecorderMode = 'pngseq',
  [int]$WaitSeconds = 60,
  [switch]$WhatIf
)
$ErrorActionPreference = 'Stop'

if ($WhatIf) {
  Write-Host 'HARNESS_GATE: G7'
  Write-Host 'Probe plan (12 steps):'
  Write-Host '  1. Send ASCENDANCE-RITUAL-{SESSION_ID} ritual prompt via Local'
  Write-Host '  2. Capture local ack'
  Write-Host '  3. Close Julian.exe'
  Write-Host '  4. Fresh msedge --user-data-dir=%TEMP%\ark-{SESSION_ID}-browser (G6 pattern)'
  Write-Host '  5. Hub recall prompt; verify UUID recall'
  Write-Host '  6. UUID match assertion'
  Write-Host '  7. Close browser; delete user-data-dir'
  Write-Host "  8. Wait $WaitSeconds s"
  Write-Host '  9. Reopen Julian.exe'
  Write-Host '  10. G7 predicate: first-paint history row contains ASCENDANCE-RITUAL-{SESSION_ID}'
  Write-Host '  11. Local recall prompt'
  Write-Host '  12. Local UUID match'
  Write-Host '  Recorder: ritual-recorder.ps1 start -> mark each step -> stop (G8 target)'
  exit 0
}

if (-not $RunDir) { throw 'RunDir is required.' }
if (-not (Test-Path -LiteralPath $RunDir)) { throw "RunDir not found: $RunDir" }
$sessionPath = Join-Path $RunDir 'session.json'
if (-not (Test-Path -LiteralPath $sessionPath)) { throw "session.json missing: $sessionPath" }
$session = Get-Content -LiteralPath $sessionPath -Raw | ConvertFrom-Json
$sessionId = [string]$session.session_id
if (-not $sessionId) { $sessionId = [string]$session.SESSION_ID }
if (-not $sessionId) { throw 'session_id missing in session.json' }

if (-not $ChromeExe) {
  $candidates = @(
    'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
    'C:\Program Files\Google\Chrome\Application\chrome.exe'
  )
  $ChromeExe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $ChromeExe) { throw 'Chromium/Edge executable not found' }

$token = (ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt').Trim()
if (-not $token) { throw 'Hub token empty.' }

$recorder = Join-Path $PSScriptRoot 'ritual-recorder.ps1'

# Kick off recorder
& $recorder -RunDir $RunDir -Mode $RecorderMode -Action start | Out-Null

function Mark([int]$n) { & $recorder -RunDir $RunDir -Mode $RecorderMode -Action mark -Step $n | Out-Null }

function Post-Chat {
  param([string]$Base, [string]$Message, [switch]$Auth)
  $headers = @{}
  if ($Auth) { $headers.Authorization = "Bearer $token" }
  $payload = @{ message = $Message; session_id = $sessionId } | ConvertTo-Json
  $attempt = 0
  while ($attempt -lt 12) {
    $attempt++
    try {
      return Invoke-RestMethod -Uri "$Base/v1/chat" -Method Post -Body $payload -ContentType 'application/json' -Headers $headers -TimeoutSec 180
    } catch {
      $msg = [string]$_.Exception.Message
      if ($msg -match 'Rate limited' -and $attempt -lt 12) { Start-Sleep -Seconds 4; continue }
      throw
    }
  }
}

function Get-SessionHistory {
  param([string]$Base, [switch]$Auth)
  $headers = @{}
  if ($Auth) { $headers.Authorization = "Bearer $token" }
  return Invoke-RestMethod -Uri "$Base/v1/session/$sessionId" -Headers $headers -TimeoutSec 30
}

Get-Process julian, arknexusv6, msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 700
if (Test-Path -LiteralPath $JulianExe) { Start-Process -FilePath $JulianExe | Out-Null; Start-Sleep -Seconds 3 }

$uuid = [Guid]::NewGuid().ToString()
$tag = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$ritualPrompt = "ASCENDANCE-RITUAL-$sessionId-$tag -- remember the phrase: `"$uuid`""

$log = [ordered]@{
  session_id = $sessionId
  ritual_uuid = $uuid
  ritual_tag = "ASCENDANCE-RITUAL-$sessionId"
  started_utc = (Get-Date).ToUniversalTime().ToString('o')
  steps = @()
}

# 1) local send
$resp1 = Post-Chat -Base $LocalBase -Message $ritualPrompt
Mark 1
$log.steps += [ordered]@{ step = 1; action = 'local_send_ritual'; message = $ritualPrompt; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 2) local ack
$ack1 = [string]$resp1.response
if (-not $ack1) { $ack1 = [string]$resp1.text }
Mark 2
$log.steps += [ordered]@{ step = 2; action = 'local_ack'; ok = ($ack1.Length -gt 0); utc = (Get-Date).ToUniversalTime().ToString('o') }

# 3) close julian
Get-Process julian, arknexusv6, msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
Mark 3
$log.steps += [ordered]@{ step = 3; action = 'close_julian'; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 4) fresh browser (G6 pattern)
$browserDir = Join-Path $env:TEMP "ark-$sessionId-ritual-browser"
if (Test-Path -LiteralPath $browserDir) { throw "G6 precondition FAIL: $browserDir exists" }
New-Item -ItemType Directory -Force -Path $browserDir | Out-Null
$browserArgs = @('--new-window', '--no-first-run', '--no-default-browser-check', "--user-data-dir=$browserDir", "$RemoteBase")
$browser = Start-Process -FilePath $ChromeExe -ArgumentList $browserArgs -PassThru
Start-Sleep -Seconds 3
Mark 4
$log.steps += [ordered]@{ step = 4; action = 'open_hub_fresh_browser'; user_data_dir = $browserDir; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 5) hub recall
$respHub = Post-Chat -Base $RemoteBase -Message 'What phrase did I just ask you to remember?' -Auth
$hubText = [string]$respHub.response
if (-not $hubText) { $hubText = [string]$respHub.assistant_text }
if (-not $hubText) { $hubText = [string]$respHub.text }
Mark 5
$log.steps += [ordered]@{ step = 5; action = 'hub_recall_prompt'; ok = ($hubText.Length -gt 0); utc = (Get-Date).ToUniversalTime().ToString('o') }

# 6) hub uuid match
$match6 = ($hubText -match [regex]::Escape($uuid))
Mark 6
$log.steps += [ordered]@{ step = 6; action = 'hub_uuid_match'; ok = $match6; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 7) close browser; delete fresh dir
try { $browser | Stop-Process -Force } catch {}
Start-Sleep -Seconds 2
$dirDeleted = $false
try { Remove-Item -LiteralPath $browserDir -Recurse -Force; $dirDeleted = -not (Test-Path -LiteralPath $browserDir) } catch {}
Mark 7
$log.steps += [ordered]@{ step = 7; action = 'close_browser_and_delete_dir'; dir_deleted = $dirDeleted; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 8) wait
Start-Sleep -Seconds $WaitSeconds
Mark 8
$log.steps += [ordered]@{ step = 8; action = "wait_${WaitSeconds}s"; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 9) reopen julian
if (Test-Path -LiteralPath $JulianExe) { Start-Process -FilePath $JulianExe | Out-Null; Start-Sleep -Seconds 4 }
Mark 9
$log.steps += [ordered]@{ step = 9; action = 'reopen_julian'; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 10) G7 first-paint history contains ASCENDANCE-RITUAL-{SESSION_ID}
$localHistory = Get-SessionHistory -Base $LocalBase
$histHasRitual = $false
foreach ($h in @($localHistory.history | Select-Object -Last 30)) {
  $txt = if ($h.text) { [string]$h.text } elseif ($h.body.content) { [string]$h.body.content } else { '' }
  if ($txt -match "ASCENDANCE-RITUAL-$sessionId") { $histHasRitual = $true; break }
}
Mark 10
$log.steps += [ordered]@{ step = 10; action = 'g7_first_paint_ritual_in_history'; ok = $histHasRitual; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 11) local recall
$respLocal2 = Post-Chat -Base $LocalBase -Message 'What phrase did I ask you to remember?'
$local2Text = [string]$respLocal2.response
if (-not $local2Text) { $local2Text = [string]$respLocal2.text }
Mark 11
$log.steps += [ordered]@{ step = 11; action = 'local_recall_prompt'; ok = ($local2Text.Length -gt 0); utc = (Get-Date).ToUniversalTime().ToString('o') }

# 12) local uuid match
$match12 = ($local2Text -match [regex]::Escape($uuid))
Mark 12
$log.steps += [ordered]@{ step = 12; action = 'local_uuid_match'; ok = $match12; utc = (Get-Date).ToUniversalTime().ToString('o') }

& $recorder -RunDir $RunDir -Mode $RecorderMode -Action stop | Out-Null

$log.ended_utc = (Get-Date).ToUniversalTime().ToString('o')
$log.step6_uuid_match = $match6
$log.step10_first_paint_ritual = $histHasRitual
$log.step12_uuid_match = $match12
$log.gate_g7_pass = $histHasRitual
$log.gate_g6_pass_ritual_segment = $dirDeleted

$logPath = Join-Path $RunDir 'ascendance-ritual.json'
$log | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $logPath -Encoding UTF8
Write-Host "ascendance-ritual: sid=$sessionId g7=$histHasRitual uuid6=$match6 uuid12=$match12 dir_deleted=$dirDeleted"
