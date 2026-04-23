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
    $stateFileText = Get-Content -LiteralPath $statePath -Raw
    $stateRaw = $stateFileText | ConvertFrom-Json
    # Rebuild as ordered hashtable so new keys can be added (PSCustomObject is fixed-shape)
    $state = [ordered]@{}
    foreach ($p in $stateRaw.PSObject.Properties) { $state[$p.Name] = $p.Value }
    $state['end_utc'] = (Get-Date).ToUniversalTime().ToString('o')
    $gapOk = $true
    $maxGap = 0
    # Raw regex extract to preserve sub-second precision (ConvertFrom-Json auto-casts ISO-8601 to DateTime, strips sub-second).
    # Each step object has "step": N and "utc": "ISO8601Z". Extract as string-pairs ordered by numeric step.
    $stepMatches = [regex]::Matches($stateFileText, '"step"\s*:\s*(\d+)[^}]*?"utc"\s*:\s*"([^"]+)"', [System.Text.RegularExpressions.RegexOptions]::Singleline)
    $rawSteps = @()
    foreach ($m in $stepMatches) {
      $rawSteps += [pscustomobject]@{ step = [int]$m.Groups[1].Value; utc = $m.Groups[2].Value }
    }
    $steps = @($rawSteps | Sort-Object -Property step)
    for ($i = 1; $i -lt $steps.Count; $i++) {
      # DateTimeOffset preserves sub-second across PS5.1 parsing.
      $prevDto = [System.DateTimeOffset]::Parse([string]$steps[$i - 1].utc, [cultureinfo]::InvariantCulture)
      $curDto  = [System.DateTimeOffset]::Parse([string]$steps[$i].utc, [cultureinfo]::InvariantCulture)
      $delta = ($curDto - $prevDto).TotalSeconds
      if ($delta -gt $maxGap) { $maxGap = $delta }
      if ($delta -gt 180) { $gapOk = $false }
    }
    $monotonic = $true
    # PS5.1 DateTime.Parse truncates sub-second precision; ISO-8601 Z strings compare
    # lexicographically correctly (2026-04-23T14:59:34.7842423Z < 2026-04-23T14:59:34.8021761Z by [string]::Compare).
    for ($i = 1; $i -lt $steps.Count; $i++) {
      $prevStr = [string]$steps[$i - 1].utc
      $curStr  = [string]$steps[$i].utc
      if ([string]::Compare($curStr, $prevStr, [System.StringComparison]::Ordinal) -le 0) { $monotonic = $false; break }
    }
    $withinWindow = $true
    if ($sessionStart) {
      # DateTimeOffset handles Z suffix without Local-TZ shift.
      $ssDto = [System.DateTimeOffset]::Parse([string]$sessionStart, [cultureinfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::AssumeUniversal)
      $ssEnd = $ssDto.AddMinutes(30)
      foreach ($s in $steps) {
        $t = [System.DateTimeOffset]::Parse([string]$s.utc, [cultureinfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::AssumeUniversal)
        if ($t -lt $ssDto -or $t -gt $ssEnd) { $withinWindow = $false }
      }
    }
    if ($state.mode -eq 'mp4' -and (Test-Path -LiteralPath $ffpidPath)) {
      $ffPidVal = (Get-Content -LiteralPath $ffpidPath).Trim()
      try {
        $ff = Get-Process -Id $ffPidVal -ErrorAction SilentlyContinue
        if ($ff) { $ff.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 3; if (-not $ff.HasExited) { Stop-Process -Id $ffPidVal -Force } }
      } catch {}
      Start-Sleep -Seconds 2
      $state['mp4_bytes'] = if (Test-Path -LiteralPath $mp4Path) { (Get-Item -LiteralPath $mp4Path).Length } else { 0 }
    }
    $state['max_gap_s'] = $maxGap
    $state['monotonic'] = $monotonic
    $state['gap_ok'] = $gapOk
    $state['within_session_window'] = $withinWindow
    $state['gate_g8_pass'] = ($monotonic -and $gapOk -and $withinWindow -and (($state.mode -eq 'mp4' -and $state.mp4_bytes -gt 0) -or ($state.mode -eq 'pngseq' -and $steps.Count -ge 12)))
    $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $manifestPath -Encoding UTF8
    $state | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $statePath -Encoding UTF8
    Write-Host "ritual-recorder: stop mode=$($state.mode) max_gap=$maxGap monotonic=$monotonic within=$withinWindow g8=$($state.gate_g8_pass)"
  }
}
