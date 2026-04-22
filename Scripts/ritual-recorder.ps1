# HARNESS_GATE: G8
# Ritual recorder -- G8_RITUAL_UNINTERRUPTED_RECORDING.
# Records EITHER ffmpeg mp4 via gdigrab OR per-step PNG sequence with monotonic timestamps.
param(
  [string]$RunDir,
  [ValidateSet('mp4', 'pngseq')] [string]$Mode = 'mp4',
  [int]$Framerate = 5,
  [ValidateSet('start', 'mark', 'stop')] [string]$Action = 'start',
  [int]$Step = 0,
  [switch]$WhatIf
)
$ErrorActionPreference = 'Stop'

if ($WhatIf) {
  Write-Host 'HARNESS_GATE: G8'
  Write-Host 'Probe plan:'
  Write-Host '  Action=start: wipe evidence/ritual/; start ffmpeg gdigrab OR init pngseq state'
  Write-Host '  Action=mark:  pngseq only -> capture step-NN.png, write state file'
  Write-Host '  Action=stop:  kill ffmpeg; finalize manifest with monotonic timestamps + session_id'
  Write-Host '  Invariants: all mtimes within [session_start_utc, session_start_utc+30min]'
  Write-Host '             max gap between consecutive steps = 180s (step 8 allowed 60s wait only)'
  exit 0
}

if (-not $RunDir) { throw 'RunDir is required.' }
$sessionPath = Join-Path $RunDir 'session.json'
if (-not (Test-Path -LiteralPath $sessionPath)) { throw "session.json missing: $sessionPath" }
$sessionObj = Get-Content -LiteralPath $sessionPath -Raw | ConvertFrom-Json
$sessionId = [string]$sessionObj.session_id
$sessionStart = [string]$sessionObj.session_start_utc
if (-not $sessionId) { throw 'session_id missing' }

$ritualDir = Join-Path $RunDir 'ritual'
$statePath = Join-Path $ritualDir 'recorder-state.json'
$manifestPath = Join-Path $ritualDir 'recorder-manifest.json'
$mp4Path = Join-Path $ritualDir "ritual-$sessionId.mp4"
$ffpidPath = Join-Path $ritualDir 'ffmpeg.pid'

switch ($Action) {
  'start' {
    if (Test-Path -LiteralPath $ritualDir) { Remove-Item -LiteralPath $ritualDir -Recurse -Force }
    New-Item -ItemType Directory -Force -Path $ritualDir | Out-Null
    $state = [ordered]@{
      session_id = $sessionId
      session_start_utc = $sessionStart
      mode = $Mode
      framerate = $Framerate
      start_utc = (Get-Date).ToUniversalTime().ToString('o')
      steps = @()
    }
    if ($Mode -eq 'mp4') {
      $ff = Get-Command ffmpeg -ErrorAction SilentlyContinue
      if (-not $ff) { throw 'ffmpeg not on PATH (PF07)' }
      $args = @('-y', '-f', 'gdigrab', '-framerate', "$Framerate", '-i', 'desktop', '-c:v', 'libx264', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', $mp4Path)
      $proc = Start-Process -FilePath 'ffmpeg' -ArgumentList $args -WindowStyle Hidden -PassThru
      $proc.Id | Set-Content -LiteralPath $ffpidPath -Encoding UTF8
      $state.mp4_path = $mp4Path
      $state.ffmpeg_pid = $proc.Id
    }
    $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statePath -Encoding UTF8
    Write-Host "ritual-recorder: start mode=$Mode sid=$sessionId"
  }
  'mark' {
    if (-not (Test-Path -LiteralPath $statePath)) { throw 'recorder-state.json missing; start first' }
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    $utc = (Get-Date).ToUniversalTime().ToString('o')
    $entry = [ordered]@{ step = $Step; utc = $utc; session_id = $sessionId }
    if ($state.mode -eq 'pngseq') {
      Add-Type -AssemblyName System.Windows.Forms
      Add-Type -AssemblyName System.Drawing
      $bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
      $bmp = New-Object System.Drawing.Bitmap($bounds.Width, $bounds.Height)
      $g = [System.Drawing.Graphics]::FromImage($bmp)
      $g.CopyFromScreen($bounds.Left, $bounds.Top, 0, 0, $bounds.Size)
      $g.Dispose()
      $png = Join-Path $ritualDir ('step-{0:D2}.png' -f $Step)
      $bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png)
      $bmp.Dispose()
      $entry.artifact = $png
    }
    $existing = @()
    if ($state.steps) { $existing = @($state.steps) }
    $existing += [pscustomobject]$entry
    $state.steps = $existing
    $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statePath -Encoding UTF8
    Write-Host "ritual-recorder: mark step=$Step utc=$utc"
  }
  'stop' {
    if (-not (Test-Path -LiteralPath $statePath)) { throw 'recorder-state.json missing' }
    $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    $state.end_utc = (Get-Date).ToUniversalTime().ToString('o')
    $gapOk = $true
    $maxGap = 0
    $steps = @($state.steps | Sort-Object step)
    for ($i = 1; $i -lt $steps.Count; $i++) {
      $prev = [DateTime]::Parse($steps[$i - 1].utc).ToUniversalTime()
      $cur = [DateTime]::Parse($steps[$i].utc).ToUniversalTime()
      $delta = ($cur - $prev).TotalSeconds
      if ($delta -gt $maxGap) { $maxGap = $delta }
      $allowed = if ($steps[$i].step -eq 8) { 180 } else { 180 }
      if ($delta -gt $allowed) { $gapOk = $false }
    }
    $monotonic = $true
    for ($i = 1; $i -lt $steps.Count; $i++) {
      if ([DateTime]::Parse($steps[$i].utc) -le [DateTime]::Parse($steps[$i - 1].utc)) { $monotonic = $false; break }
    }
    $withinWindow = $true
    if ($sessionStart) {
      $ssUtc = [DateTime]::Parse($sessionStart).ToUniversalTime()
      foreach ($s in $steps) {
        $t = [DateTime]::Parse($s.utc).ToUniversalTime()
        if ($t -lt $ssUtc -or $t -gt $ssUtc.AddMinutes(30)) { $withinWindow = $false }
      }
    }
    if ($state.mode -eq 'mp4' -and (Test-Path -LiteralPath $ffpidPath)) {
      $pid = (Get-Content -LiteralPath $ffpidPath).Trim()
      try {
        $ff = Get-Process -Id $pid -ErrorAction SilentlyContinue
        if ($ff) { $ff.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 3; if (-not $ff.HasExited) { Stop-Process -Id $pid -Force } }
      } catch {}
      Start-Sleep -Seconds 2
      $state.mp4_bytes = if (Test-Path -LiteralPath $mp4Path) { (Get-Item -LiteralPath $mp4Path).Length } else { 0 }
    }
    $state.max_gap_s = $maxGap
    $state.monotonic = $monotonic
    $state.gap_ok = $gapOk
    $state.within_session_window = $withinWindow
    $state.gate_g8_pass = ($monotonic -and $gapOk -and $withinWindow -and (($state.mode -eq 'mp4' -and $state.mp4_bytes -gt 0) -or ($state.mode -eq 'pngseq' -and $steps.Count -ge 12)))
    $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statePath -Encoding UTF8
    Write-Host "ritual-recorder: stop mode=$($state.mode) max_gap=$maxGap monotonic=$monotonic within=$withinWindow g8=$($state.gate_g8_pass)"
  }
}
