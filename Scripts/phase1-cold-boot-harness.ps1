# HARNESS_GATE: G1,G2,G14
# Phase 1 cold-boot harness -- G1_BOOT_DOM_ATTR, G2_COLD_BOOT_RERUN, G14_TRACKER_SCHEMA_ALIGNMENT
# Rewritten Phase 3 (S182). SESSION_ID injection, leveldb_latest scraper, CDP DOM readback.
param(
  [string]$RunDir,
  [string]$JulianExe = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\arknexusv6.exe',
  [string]$EvidenceDir = 'C:\Users\raest\Documents\Karma_SADE\evidence',
  [string]$LocalBase = 'http://127.0.0.1:7891',
  [int]$CdpPort = 9222,
  [switch]$WhatIf
)
$ErrorActionPreference = 'Stop'

if ($WhatIf) {
  Write-Host 'HARNESS_GATE: G1,G2,G14'
  Write-Host 'Probe plan:'
  Write-Host '  1. Kill arknexusv6,julian,msedgewebview2'
  Write-Host '  2. Launch arknexusv6.exe with ARKNEXUS_DEVTOOLS=1 + CDP port'
  Write-Host '  3. Measure window_visible_ms (MainWindowHandle poll)'
  Write-Host '  4. CDP Runtime.evaluate <html> data-hydration-state + data-session-id'
  Write-Host '  5. Scrape LevelDB __bootMetrics via Scripts/leveldb_latest.ps1'
  Write-Host '  6. Emit phase1-first-frame.png, phase1-timing.json (persona+effective_paint), phase1-history-diff.txt, phase1-canonical-trace.txt'
  Write-Host '  7. SESSION_ID written into every artifact'
  exit 0
}

if (-not $RunDir) { $RunDir = $EvidenceDir }
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$sessionPath = Join-Path $RunDir 'session.json'
$sessionId = ''
if (Test-Path -LiteralPath $sessionPath) {
  $sessionId = [string]((Get-Content -LiteralPath $sessionPath -Raw | ConvertFrom-Json).session_id)
}
if (-not $sessionId) {
  try { $sessionId = [string]((Invoke-RestMethod -Uri "$LocalBase/memory/session" -TimeoutSec 8).session_id) } catch {}
}
if (-not $sessionId) { $sessionId = 'unknown-session' }

$png = Join-Path $RunDir 'phase1-first-frame.png'
$tim = Join-Path $RunDir 'phase1-timing.json'
$hist = Join-Path $RunDir 'phase1-history-diff.txt'
$trace = Join-Path $RunDir 'phase1-canonical-trace.txt'
$cdpLog = Join-Path $RunDir 'phase1-cdp-dom.json'

Get-Process julian, arknexusv6, msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 700

$env:ARKNEXUS_DEVTOOLS = '1'
$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = "--remote-debugging-port=$CdpPort --remote-allow-origins=*"
$env:NEXUS_SESSION_ID = $sessionId

$sw = [Diagnostics.Stopwatch]::StartNew()
$p = Start-Process -FilePath $JulianExe -PassThru
$visible = -1
for ($i = 0; $i -lt 120; $i++) {
  Start-Sleep -Milliseconds 50
  $p.Refresh()
  if ($p.MainWindowHandle -ne 0) { $visible = $sw.ElapsedMilliseconds; break }
}

# Wait for CDP port to actually listen (up to 15s)
$cdpReady = $false
for ($i = 0; $i -lt 30; $i++) {
  Start-Sleep -Milliseconds 500
  $conn = Get-NetTCPConnection -LocalPort $CdpPort -State Listen -ErrorAction SilentlyContinue
  if ($conn) { $cdpReady = $true; break }
}
# Poll CDP for page tab + wait for hydration attr to become 'ready' (up to 10s after port open)
$hydrationReady = $false
if ($cdpReady) {
  for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    try {
      $pollTabs = Invoke-RestMethod -Uri "http://127.0.0.1:$CdpPort/json" -TimeoutSec 3 -ErrorAction SilentlyContinue
      $pollPage = $pollTabs | Where-Object { $_.type -eq 'page' -and $_.url -notmatch '^devtools:' } | Select-Object -First 1
      if (-not $pollPage) { $pollPage = $pollTabs | Where-Object { $_.type -eq 'page' } | Select-Object -First 1 }
      if ($pollPage -and $pollPage.webSocketDebuggerUrl) {
        $pollWs = New-Object System.Net.WebSockets.ClientWebSocket
        $pollCt = New-Object System.Threading.CancellationTokenSource 3000
        $pollWs.ConnectAsync([Uri]$pollPage.webSocketDebuggerUrl, $pollCt.Token).Wait()
        $pollMsg = '{"id":999,"method":"Runtime.evaluate","params":{"expression":"document.documentElement.dataset.hydrationState || \"\""}}'
        $pBuf = [Text.Encoding]::UTF8.GetBytes($pollMsg)
        $pSeg = New-Object System.ArraySegment[byte](,$pBuf)
        $pollWs.SendAsync($pSeg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $pollCt.Token).Wait()
        $prBuf = New-Object byte[] 8192
        $prSeg = New-Object System.ArraySegment[byte](,$prBuf)
        $prResult = $pollWs.ReceiveAsync($prSeg, $pollCt.Token)
        $prResult.Wait()
        $prRaw = [Text.Encoding]::UTF8.GetString($prBuf, 0, $prResult.Result.Count)
        $pollWs.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'poll', $pollCt.Token).Wait()
        if ($prRaw -match '"ready"') { $hydrationReady = $true; break }
      }
    } catch {}
  }
}
Start-Sleep -Seconds 1
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left, $b.Top, 0, 0, $b.Size)
$g.Dispose()
$bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

# CDP DOM readback -- G1 predicate
$cdpDom = [ordered]@{ session_id = $sessionId; cdp_port = $CdpPort; data_hydration_state = ''; data_session_id = ''; error = $null }
try {
  $tabs = Invoke-RestMethod -Uri "http://127.0.0.1:$CdpPort/json" -TimeoutSec 6
  $pageTab = $tabs | Where-Object { $_.type -eq 'page' -and $_.url -notmatch '^devtools:' } | Select-Object -First 1
  if (-not $pageTab) { $pageTab = $tabs | Where-Object { $_.type -eq 'page' } | Select-Object -First 1 }
  if ($pageTab -and $pageTab.webSocketDebuggerUrl) {
    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $ct = New-Object System.Threading.CancellationTokenSource 10000
    $uri = [Uri]$pageTab.webSocketDebuggerUrl
    $ws.ConnectAsync($uri, $ct.Token).Wait()
    $msg = '{"id":1,"method":"Runtime.evaluate","params":{"expression":"JSON.stringify({h:document.documentElement.dataset.hydrationState,s:document.documentElement.dataset.sessionId})","returnByValue":true}}'
    $buf = [Text.Encoding]::UTF8.GetBytes($msg)
    $seg = New-Object System.ArraySegment[byte](,$buf)
    $ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct.Token).Wait()
    $rbuf = New-Object byte[] 16384
    $rseg = New-Object System.ArraySegment[byte](,$rbuf)
    $rr = $ws.ReceiveAsync($rseg, $ct.Token)
    $rr.Wait()
    $raw = [Text.Encoding]::UTF8.GetString($rbuf, 0, $rr.Result.Count)
    $parsed = $raw | ConvertFrom-Json
    $inner = $parsed.result.result.value | ConvertFrom-Json
    $cdpDom.data_hydration_state = [string]$inner.h
    $cdpDom.data_session_id = [string]$inner.s
    $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'done', $ct.Token).Wait()
  } else {
    $cdpDom.error = 'no_page_tab'
  }
} catch {
  $cdpDom.error = [string]$_.Exception.Message
}
$cdpDom | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $cdpLog -Encoding UTF8

# LevelDB __bootMetrics scrape
$bootMetrics = $null
$personaPaint = -1
try {
  $raw = & (Join-Path $PSScriptRoot 'leveldb_latest.ps1') -Key '__bootMetrics' 2>&1
  if ($LASTEXITCODE -eq 0) {
    $bootEntry = $raw | ConvertFrom-Json
    $valStr = [string]$bootEntry.value
    try { $bootMetrics = $valStr | ConvertFrom-Json } catch { $bootMetrics = $null }
    if ($bootMetrics -and $bootMetrics.persona_paint_ms) { $personaPaint = [int]$bootMetrics.persona_paint_ms }
  }
} catch {}

# Canonical endpoint trace
function ProbeUrl([string]$u) {
  try {
    $r = Invoke-WebRequest -Uri $u -UseBasicParsing -TimeoutSec 8
    [pscustomobject]@{ url = $u; status = $r.StatusCode; session_id = $sessionId }
  } catch {
    [pscustomobject]@{ url = $u; status = 0; session_id = $sessionId; error = $_.Exception.Message }
  }
}
$w = ProbeUrl "$LocalBase/memory/wakeup"
$s = ProbeUrl "$LocalBase/memory/session"
$ss = ProbeUrl "$LocalBase/v1/session/$sessionId"
@($w, $s, $ss) | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $trace -Encoding UTF8

# History (last 3)
$history = @()
try {
  $sj = Invoke-RestMethod -Uri "$LocalBase/v1/session/$sessionId" -TimeoutSec 8
  $history = @($sj.history | Select-Object -Last 3)
} catch {}
$lines = @("session_id: $sessionId", 'last 3 turns:')
if ($history.Count -eq 0) { $lines += '(none)' }
else {
  foreach ($h in $history) {
    $role = if ($h.body.role) { $h.body.role } else { '?' }
    $txt = if ($h.text) { $h.text } elseif ($h.body.content) { $h.body.content } else { '' }
    $lines += "$role | $($txt -replace '[\r\n]', ' ')"
  }
}
$lines | Set-Content -LiteralPath $hist -Encoding UTF8

# Timing -- G14 requires both persona_paint_ms AND effective_paint_ms
$effectivePaint = if ($personaPaint -ge 0 -and $visible -ge 0) { $visible + $personaPaint } else { -1 }
$tm = [ordered]@{
  session_id               = $sessionId
  timestamp                = (Get-Date).ToUniversalTime().ToString('o')
  window_visible_ms        = $visible
  persona_paint_ms         = $personaPaint
  effective_paint_ms       = $effectivePaint
  wall_clock_ms            = $sw.ElapsedMilliseconds
  paint_deadline_ms        = 2000
  paint_within_deadline    = ($effectivePaint -ge 0 -and $effectivePaint -lt 2000)
  boot_metrics             = $bootMetrics
  cdp_data_hydration_state = $cdpDom.data_hydration_state
  cdp_data_session_id      = $cdpDom.data_session_id
  gate_g1_pass             = ($cdpDom.data_hydration_state -eq 'ready' -and $cdpDom.data_session_id -eq $sessionId)
  gate_g2_pass             = ($bootMetrics -and [string]$bootMetrics.session_id -eq $sessionId -and $effectivePaint -ge 0 -and $effectivePaint -lt 2000)
  gate_g14_pass            = ($personaPaint -ge 0 -and $effectivePaint -ge 0)
}
$tm | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $tim -Encoding UTF8
Write-Host "phase1-cold-boot-harness: session_id=$sessionId visible=$visible persona_paint=$personaPaint effective=$effectivePaint g1=$($tm.gate_g1_pass) g2=$($tm.gate_g2_pass) g14=$($tm.gate_g14_pass)"
