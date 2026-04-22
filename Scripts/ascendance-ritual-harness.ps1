param(
  [string]$RunDir,
  [string]$JulianExe = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\julian.exe',
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

$ritualDir = Join-Path $RunDir 'ritual'
New-Item -ItemType Directory -Path $ritualDir -Force | Out-Null

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

function Save-StepShot {
  param([int]$Step)
  $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
  $bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
  $g = [System.Drawing.Graphics]::FromImage($bmp)
  $g.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bounds.Size)
  $g.Dispose()
  $path = Join-Path $ritualDir ("step-{0:D2}.png" -f $Step)
  $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $bmp.Dispose()
  return $path
}

function Post-Chat {
  param([string]$Base, [string]$Message, [switch]$Auth)
  $headers = @{}
  if ($Auth) { $headers.Authorization = "Bearer $token" }
  $payload = @{
    message = $Message
    session_id = $sessionId
  } | ConvertTo-Json
  $attempt = 0
  while ($attempt -lt 12) {
    $attempt++
    try {
      return Invoke-RestMethod -Uri "$Base/v1/chat" -Method Post -Body $payload -ContentType 'application/json' -Headers $headers -TimeoutSec 180
    } catch {
      $msg = [string]$_.Exception.Message
      if ($msg -match 'Rate limited' -and $attempt -lt 12) {
        Start-Sleep -Seconds 4
        continue
      }
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

Get-Process julian, msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 700
if (Test-Path -LiteralPath $JulianExe) {
  Start-Process -FilePath $JulianExe | Out-Null
  Start-Sleep -Seconds 3
}

$uuid = [Guid]::NewGuid().ToString()
$tag = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$ritualPrompt = "ASCENDANCE-RITUAL-$tag - remember the phrase: ""$uuid"""

$stepArtifacts = @()
$log = [ordered]@{
  session_id = $sessionId
  ritual_uuid = $uuid
  started_utc = (Get-Date).ToUniversalTime().ToString('o')
  steps = @()
}

# 1) send ritual message from local surface
$resp1 = Post-Chat -Base $LocalBase -Message $ritualPrompt
$stepArtifacts += Save-StepShot -Step 1
$log.steps += [ordered]@{ step = 1; action = 'local_send_ritual'; message = $ritualPrompt; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 2) capture local acknowledgement
$ack1 = [string]($resp1.response)
if (-not $ack1) { $ack1 = [string]($resp1.text) }
$stepArtifacts += Save-StepShot -Step 2
$log.steps += [ordered]@{ step = 2; action = 'local_ack'; response = $ack1; ok = ($ack1.Length -gt 0); utc = (Get-Date).ToUniversalTime().ToString('o') }

# 3) close Julian
Get-Process julian, msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
$stepArtifacts += Save-StepShot -Step 3
$log.steps += [ordered]@{ step = 3; action = 'close_julian'; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 4) fresh browser session on hub
Start-Process msedge.exe "--new-window --inprivate $RemoteBase" | Out-Null
Start-Sleep -Seconds 3
$stepArtifacts += Save-StepShot -Step 4
$log.steps += [ordered]@{ step = 4; action = 'open_hub_fresh_browser'; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 5) ask recall on hub
$q1 = 'What phrase did I just ask you to remember?'
$respHub = Post-Chat -Base $RemoteBase -Message $q1 -Auth
$stepArtifacts += Save-StepShot -Step 5
$hubText = [string]$respHub.response
if (-not $hubText) { $hubText = [string]$respHub.assistant_text }
if (-not $hubText) { $hubText = [string]$respHub.text }
$log.steps += [ordered]@{ step = 5; action = 'hub_recall_prompt'; response = $hubText; ok = ($hubText.Length -gt 0); utc = (Get-Date).ToUniversalTime().ToString('o') }

# 6) verify hub recall exact uuid
$match6 = ($hubText -match [regex]::Escape($uuid))
$stepArtifacts += Save-StepShot -Step 6
$log.steps += [ordered]@{ step = 6; action = 'hub_uuid_match'; expected = $uuid; ok = $match6; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 7) close browser
Get-Process msedge -ErrorAction SilentlyContinue | Stop-Process -Force
$stepArtifacts += Save-StepShot -Step 7
$log.steps += [ordered]@{ step = 7; action = 'close_browser'; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 8) wait 60s
Start-Sleep -Seconds 60
$stepArtifacts += Save-StepShot -Step 8
$log.steps += [ordered]@{ step = 8; action = 'wait_60s'; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 9) reopen Julian
if (Test-Path -LiteralPath $JulianExe) {
  Start-Process -FilePath $JulianExe | Out-Null
  Start-Sleep -Seconds 3
}
$stepArtifacts += Save-StepShot -Step 9
$log.steps += [ordered]@{ step = 9; action = 'reopen_julian'; ok = $true; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 10) first-frame history check from local session payload
$localHistory = Get-SessionHistory -Base $LocalBase
$histHasUuid = $false
foreach ($h in @($localHistory.history | Select-Object -Last 20)) {
  $txt = if ($h.text) { [string]$h.text } elseif ($h.body.content) { [string]$h.body.content } else { '' }
  if ($txt -match [regex]::Escape($uuid)) { $histHasUuid = $true; break }
}
$stepArtifacts += Save-StepShot -Step 10
$log.steps += [ordered]@{ step = 10; action = 'first_frame_history_uuid_check'; ok = $histHasUuid; utc = (Get-Date).ToUniversalTime().ToString('o') }

# 11) ask local recall again
$q2 = 'What phrase did I ask you to remember?'
$respLocal2 = Post-Chat -Base $LocalBase -Message $q2
$local2Text = [string]$respLocal2.response
if (-not $local2Text) { $local2Text = [string]$respLocal2.text }
$stepArtifacts += Save-StepShot -Step 11
$log.steps += [ordered]@{ step = 11; action = 'local_recall_prompt'; response = $local2Text; ok = ($local2Text.Length -gt 0); utc = (Get-Date).ToUniversalTime().ToString('o') }

# 12) verify local recall exact uuid
$match12 = ($local2Text -match [regex]::Escape($uuid))
$stepArtifacts += Save-StepShot -Step 12
$log.steps += [ordered]@{ step = 12; action = 'local_uuid_match'; expected = $uuid; ok = $match12; utc = (Get-Date).ToUniversalTime().ToString('o') }

$log.ended_utc = (Get-Date).ToUniversalTime().ToString('o')
$log.step6_uuid_match = $match6
$log.step12_uuid_match = $match12
$log.gate_pass = ($match6 -and $match12 -and $histHasUuid)
$log.artifacts = @($stepArtifacts)

$logPath = Join-Path $RunDir 'ascendance-ritual.json'
$log | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $logPath -Encoding UTF8

Get-Content -LiteralPath $logPath -Raw
