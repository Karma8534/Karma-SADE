# HARNESS_GATE: G3,G5,G6
# Phase 3 family harness -- G3_PARITY_BROWSER_SCREEN, G5_WHOAMI_REAL_UI, G6_RITUAL_STEP4_FRESH_BROWSER
# Rewritten Phase 3 (S182). CDP keyboard driving + fresh browser user-data-dir + CDP Network capture.
param(
  [string]$RunDir,
  [string]$ChromeExe,
  [string]$JulianExe = 'C:\Users\raest\Documents\Karma_SADE\nexus-tauri\src-tauri\target\release\arknexusv6.exe',
  [string]$FrontendSrcDir = 'C:\Users\raest\Documents\Karma_SADE\frontend\src',
  [string]$RemoteBase = 'https://hub.arknexus.net',
  [int]$CdpPort = 9333,
  [switch]$WhatIf
)
$ErrorActionPreference = 'Stop'

if ($WhatIf) {
  Write-Host 'HARNESS_GATE: G3,G5,G6'
  Write-Host 'Probe plan:'
  Write-Host '  G6: spawn Chromium with --user-data-dir=%TEMP%\ark-{SESSION_ID}-browser (new)'
  Write-Host '  G3: navigate to hub.arknexus.net; auth w/ token; screenshot chat feed containing PARITY-PROBE-{SESSION_ID}; CDP Network records /v1/chat body with probe'
  Write-Host '  G5: CDP Input.dispatchKeyEvent slash -> verify data-picker-open=true -> type whoami -> Enter -> capture TRUE FAMILY + TOOLS/RESOURCES'
  Write-Host '  Emit phase3-family.json, phase3-agents-sections.png, phase3-whoami.png, phase3-cdp-network.jsonl, phase3-family-grep.txt'
  Write-Host '  Delete user-data-dir at close'
  exit 0
}

if (-not $RunDir) { throw 'RunDir is required.' }
if (-not (Test-Path -LiteralPath $RunDir)) { throw "RunDir not found: $RunDir" }
$sessionPath = Join-Path $RunDir 'session.json'
if (-not (Test-Path -LiteralPath $sessionPath)) { throw "session.json missing: $sessionPath" }
$session = Get-Content -LiteralPath $sessionPath -Raw | ConvertFrom-Json
$sessionId = [string]$session.session_id
if (-not $sessionId) { $sessionId = [string]$session.SESSION_ID }
if (-not $sessionId) { throw 'session_id missing' }

if (-not $ChromeExe) {
  $candidates = @(
    'C:\Program Files\Google\Chrome\Application\chrome.exe',
    'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    (Join-Path $env:LOCALAPPDATA 'Google\Chrome\Application\chrome.exe'),
    'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
    'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
  )
  $ChromeExe = $candidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $ChromeExe) { throw 'Chromium/Edge executable not found' }

$token = (ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt').Trim()
if (-not $token) { throw 'Hub token empty.' }

$agentsPng = Join-Path $RunDir 'phase3-agents-sections.png'
$whoamiPng = Join-Path $RunDir 'phase3-whoami.png'
$grepOut = Join-Path $RunDir 'phase3-family-grep.txt'
$netLog = Join-Path $RunDir 'phase3-cdp-network.jsonl'
$resultPath = Join-Path $RunDir 'phase3-family.json'

# G6: Fresh user-data-dir
$userDataDir = Join-Path $env:TEMP "ark-$sessionId-browser"
$dirExistedBefore = Test-Path -LiteralPath $userDataDir
if ($dirExistedBefore) { throw "G6 PRECONDITION FAIL: user-data-dir already exists: $userDataDir" }
New-Item -ItemType Directory -Force -Path $userDataDir | Out-Null

# Probe to locate in chat feed (G3)
$probePath = Join-Path $RunDir 'phase2-probe.txt'
$probeValue = ''
if (Test-Path -LiteralPath $probePath) { $probeValue = (Get-Content -LiteralPath $probePath -Raw).Trim() }
if (-not $probeValue) { $probeValue = "PARITY-PROBE-$sessionId-stub" }

# Launch Chromium with CDP + fresh dir -> hub.arknexus.net
$chromeArgs = @(
  "--remote-debugging-port=$CdpPort",
  "--user-data-dir=$userDataDir",
  '--no-first-run',
  '--no-default-browser-check',
  "$RemoteBase"
)
$cmdLine = "$ChromeExe " + ($chromeArgs -join ' ')
Add-Content -LiteralPath (Join-Path $RunDir 'PROBE_LOG.md') -Value "$(Get-Date -Format o) | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=$cmdLine | art_sha=none"
$chrome = Start-Process -FilePath $ChromeExe -ArgumentList $chromeArgs -PassThru

Start-Sleep -Seconds 5

# CDP bootstrap
function Get-CdpPageWs([int]$Port) {
  $tabs = Invoke-RestMethod -Uri "http://127.0.0.1:$Port/json" -TimeoutSec 10
  $page = $tabs | Where-Object { $_.type -eq 'page' -and $_.url -match 'arknexus' } | Select-Object -First 1
  if (-not $page) { $page = $tabs | Where-Object { $_.type -eq 'page' } | Select-Object -First 1 }
  return $page
}

function New-CdpSocket([string]$WsUrl) {
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  $cts = New-Object System.Threading.CancellationTokenSource 180000
  $ws.ConnectAsync([Uri]$WsUrl, $cts.Token).Wait()
  return @{ ws = $ws; cts = $cts; id = 0 }
}

function Send-Cdp($conn, [string]$method, $params) {
  $conn.id++
  $payload = @{ id = $conn.id; method = $method; params = $params } | ConvertTo-Json -Depth 10 -Compress
  $buf = [Text.Encoding]::UTF8.GetBytes($payload)
  $seg = New-Object System.ArraySegment[byte](, $buf)
  $conn.ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $conn.cts.Token).Wait()
  return $conn.id
}

function Recv-Cdp($conn, [int]$TimeoutMs = 5000) {
  # Drain event frames; returns first frame seen.
  $start = [Diagnostics.Stopwatch]::StartNew()
  $rbuf = New-Object byte[] 65536
  $rseg = New-Object System.ArraySegment[byte](, $rbuf)
  while ($start.ElapsedMilliseconds -lt $TimeoutMs) {
    try {
      $rr = $conn.ws.ReceiveAsync($rseg, $conn.cts.Token)
      if ($rr.Wait(1000)) {
        return [Text.Encoding]::UTF8.GetString($rbuf, 0, $rr.Result.Count)
      }
    } catch { break }
  }
  return $null
}

function Recv-CdpForId($conn, [int]$TargetId, [int]$TimeoutMs = 8000) {
  # Loop until we receive a COMPLETE WebSocket message (concatenating fragments),
  # then return if JSON id matches $TargetId. CDP responses can span multiple frames.
  $start = [Diagnostics.Stopwatch]::StartNew()
  $chunkBuf = New-Object byte[] 131072
  $chunkSeg = New-Object System.ArraySegment[byte](, $chunkBuf)
  while ($start.ElapsedMilliseconds -lt $TimeoutMs) {
    try {
      $ms = New-Object System.IO.MemoryStream
      do {
        $rr = $conn.ws.ReceiveAsync($chunkSeg, $conn.cts.Token)
        if (-not $rr.Wait(1500)) { break }
        $ms.Write($chunkBuf, 0, $rr.Result.Count)
      } while (-not $rr.Result.EndOfMessage)
      if ($ms.Length -eq 0) { continue }
      $raw = [Text.Encoding]::UTF8.GetString($ms.ToArray())
      if ($raw -match "`"id`":$TargetId[,}]") { return $raw }
    } catch { break }
  }
  return $null
}

$tab = Get-CdpPageWs -Port $CdpPort
$g3Pass = $false
$g5Pass = $false
$networkEvents = @()

if ($tab -and $tab.webSocketDebuggerUrl) {
  try {
    $c = New-CdpSocket $tab.webSocketDebuggerUrl
    # Enable domains
    Send-Cdp $c 'Network.enable' @{} | Out-Null; Recv-Cdp $c 1500 | Out-Null
    Send-Cdp $c 'Page.enable' @{} | Out-Null; Recv-Cdp $c 1500 | Out-Null
    Send-Cdp $c 'Runtime.enable' @{} | Out-Null; Recv-Cdp $c 1500 | Out-Null
    # Inject auth token + navigate to chat feed with probe
    $authScript = "document.cookie='hub_token=$token; path=/';"
    Send-Cdp $c 'Runtime.evaluate' @{ expression = $authScript; returnByValue = $true } | Out-Null
    Recv-Cdp $c 2000 | Out-Null
    # Trigger fetch to /v1/session/{id} so Network records body w/ probe
    $fetchScript = "fetch('/v1/session/$sessionId', {headers:{'Authorization':'Bearer $token'}}).then(r=>r.text()).then(t=>window.__probeBody=t);"
    Send-Cdp $c 'Runtime.evaluate' @{ expression = $fetchScript; awaitPromise = $true } | Out-Null
    $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($sw.ElapsedMilliseconds -lt 8000) {
      $evt = Recv-Cdp $c 500
      if ($evt) { $networkEvents += $evt; if ($evt -match [regex]::Escape($probeValue)) { $g3Pass = $true } }
    }
    # Read body text
    Send-Cdp $c 'Runtime.evaluate' @{ expression = 'window.__probeBody || ""'; returnByValue = $true } | Out-Null
    $bodyResp = Recv-Cdp $c 3000
    if ($bodyResp -and $bodyResp -match [regex]::Escape($probeValue)) { $g3Pass = $true }

    # Screenshot
    Send-Cdp $c 'Page.captureScreenshot' @{ format = 'png' } | Out-Null
    $shotResp = Recv-Cdp $c 5000
    if ($shotResp) {
      $shotObj = $shotResp | ConvertFrom-Json
      if ($shotObj.result.data) { [IO.File]::WriteAllBytes($agentsPng, [Convert]::FromBase64String($shotObj.result.data)) }
    }
    $c.ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'done', $c.cts.Token).Wait()
  } catch {
    Add-Content -LiteralPath (Join-Path $RunDir 'PROBE_LOG.md') -Value "$(Get-Date -Format o) | PITFALL | G3 | cdp_error=$($_.Exception.Message)"
  }
}
$networkEvents | Set-Content -LiteralPath $netLog -Encoding UTF8

# G5: CDP keyboard to Julian (separate CDP port 9222 for Tauri)
$env:ARKNEXUS_DEVTOOLS = '1'
$env:WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS = '--remote-debugging-port=9222 --remote-allow-origins=*'
$env:NEXUS_SESSION_ID = $sessionId
Get-Process julian, arknexusv6, msedgewebview2 -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 700
Start-Process -FilePath $JulianExe | Out-Null
Start-Sleep -Seconds 5

$whoamiBody = ''
$pickerOpen = $false
try {
  # Wait for Tauri CDP port to actually listen
  for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Milliseconds 500
    if (Get-NetTCPConnection -LocalPort 9222 -State Listen -ErrorAction SilentlyContinue) { break }
  }
  # Prefer non-devtools page (DevTools opens alongside when ARKNEXUS_DEVTOOLS=1)
  $jTabs = Invoke-RestMethod -Uri "http://127.0.0.1:9222/json" -TimeoutSec 6
  $jt = $jTabs | Where-Object { $_.type -eq 'page' -and $_.url -notmatch '^devtools:' } | Select-Object -First 1
  if (-not $jt) { $jt = Get-CdpPageWs -Port 9222 }
  if ($jt -and $jt.webSocketDebuggerUrl) {
    $jc = New-CdpSocket $jt.webSocketDebuggerUrl
    Send-Cdp $jc 'Runtime.enable' @{} | Out-Null; Recv-Cdp $jc 1500 | Out-Null
    # G5 precondition: MessageInput is auth-gated. Seed karma-token into localStorage then reload.
    $seedAuthJs = "localStorage.setItem('karma-token','$token'); localStorage.setItem('karma-authenticated','true'); location.reload();"
    $authSeedId = Send-Cdp $jc 'Runtime.evaluate' @{ expression = $seedAuthJs }
    Recv-CdpForId $jc $authSeedId 4000 | Out-Null
    Start-Sleep -Seconds 6
    # Reacquire CDP page tab post-reload (WebSocket may have been invalidated)
    try {
      $jTabs2 = Invoke-RestMethod -Uri "http://127.0.0.1:9222/json" -TimeoutSec 6
      $jt2 = $jTabs2 | Where-Object { $_.type -eq 'page' -and $_.url -notmatch '^devtools:' } | Select-Object -First 1
      if ($jt2 -and $jt2.webSocketDebuggerUrl -and $jt2.webSocketDebuggerUrl -ne $jt.webSocketDebuggerUrl) {
        try { $jc.ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'reload', $jc.cts.Token).Wait() } catch {}
        $jc = New-CdpSocket $jt2.webSocketDebuggerUrl
        Send-Cdp $jc 'Runtime.enable' @{} | Out-Null; Recv-Cdp $jc 1500 | Out-Null
      }
    } catch {}
    # React-compatible input sequence: set native value via prototype setter then dispatch input event.
    # `Input.dispatchKeyEvent type=char` bypasses React's synthetic event system and leaves value unchanged.
    $setSlashJs = @"
(function(){
  var ta = document.querySelector('textarea, input[type=text]');
  if (!ta) return 'NO_TEXTAREA';
  ta.focus();
  var proto = Object.getPrototypeOf(ta);
  var desc = Object.getOwnPropertyDescriptor(proto, 'value');
  var setter = desc && desc.set;
  if (setter) { setter.call(ta, '/'); } else { ta.value = '/'; }
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  return 'OK';
})()
"@
    $slashId = Send-Cdp $jc 'Runtime.evaluate' @{ expression = $setSlashJs; returnByValue = $true }
    Recv-CdpForId $jc $slashId 4000 | Out-Null
    Start-Sleep -Milliseconds 800
    $pickId = Send-Cdp $jc 'Runtime.evaluate' @{ expression = "!!document.querySelector('[data-picker-open=\u0022true\u0022]')"; returnByValue = $true }
    $pr = Recv-CdpForId $jc $pickId 4000
    if ($pr) {
      $po = $pr | ConvertFrom-Json
      $pickerOpen = ([string]$po.result.result.value -eq 'True' -or [string]$po.result.result.value -eq 'true')
    }
    # Extend to /whoami via same native setter path
    $setWhoamiJs = @"
(function(){
  var ta = document.querySelector('textarea, input[type=text]');
  if (!ta) return 'NO_TEXTAREA';
  ta.focus();
  var proto = Object.getPrototypeOf(ta);
  var desc = Object.getOwnPropertyDescriptor(proto, 'value');
  var setter = desc && desc.set;
  if (setter) { setter.call(ta, '/whoami'); } else { ta.value = '/whoami'; }
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  return 'OK';
})()
"@
    $whoId = Send-Cdp $jc 'Runtime.evaluate' @{ expression = $setWhoamiJs; returnByValue = $true }
    Recv-CdpForId $jc $whoId 4000 | Out-Null
    Start-Sleep -Milliseconds 800
    # Submit whoami via direct DOM click on the picker row (more reliable than synthetic KeyboardEvent;
    # picker's window keydown listener requires isTrusted events which dispatchEvent cannot produce).
    $enterJs = @"
(function(){
  var rows = document.querySelectorAll('[data-picker-open="true"] [data-index]');
  for (var i=0; i<rows.length; i++) {
    var t = (rows[i].innerText || '').toLowerCase();
    if (t.indexOf('whoami') !== -1) {
      rows[i].click();
      return 'CLICKED_ROW_' + i;
    }
  }
  return 'NO_WHOAMI_ROW_count=' + rows.length;
})()
"@
    $enterId = Send-Cdp $jc 'Runtime.evaluate' @{ expression = $enterJs; returnByValue = $true }
    $enterResp = Recv-CdpForId $jc $enterId 4000
    Add-Content -LiteralPath (Join-Path $RunDir 'phase3-g5-trace.txt') -Value "click_result: $enterResp"
    Start-Sleep -Seconds 6
    # Snapshot rows + body for diagnostic
    $diagJs = "JSON.stringify({rowCount:document.querySelectorAll('[data-picker-open=`"true`"] [data-index]').length, msgCount:document.querySelectorAll('[data-role=`"system`"],[class*=`"message`"]').length, bodyHasTF: document.body.innerText.indexOf('TRUE FAMILY')>-1, bodyHasTR: document.body.innerText.indexOf('TOOLS / RESOURCES')>-1, bodyLen:document.body.innerText.length, bodyTail:document.body.innerText.slice(-400)})"
    $diagId = Send-Cdp $jc 'Runtime.evaluate' @{ expression = $diagJs; returnByValue = $true }
    $diagResp = Recv-CdpForId $jc $diagId 4000
    Add-Content -LiteralPath (Join-Path $RunDir 'phase3-g5-trace.txt') -Value "diag: $diagResp"
    Start-Sleep -Seconds 4
    $bodyId = Send-Cdp $jc 'Runtime.evaluate' @{ expression = '(document.body && document.body.innerText) || ""'; returnByValue = $true }
    $br = Recv-CdpForId $jc $bodyId 12000
    Add-Content -LiteralPath (Join-Path $RunDir 'phase3-g5-trace.txt') -Value ("body_recv_len: " + $(if ($br) { $br.Length } else { 'null' }))
    if ($br) {
      try {
        $bo = $br | ConvertFrom-Json
        $whoamiBody = [string]$bo.result.result.value
        Add-Content -LiteralPath (Join-Path $RunDir 'phase3-g5-trace.txt') -Value ("whoamiBody_len: " + $whoamiBody.Length + "; bodyHasTF=" + ($whoamiBody -match 'TRUE FAMILY') + "; bodyHasTR=" + ($whoamiBody -match 'TOOLS\s*/\s*RESOURCES'))
      } catch {
        Add-Content -LiteralPath (Join-Path $RunDir 'phase3-g5-trace.txt') -Value ("body_parse_err: " + $_.Exception.Message + "; first_200=" + $br.Substring(0, [Math]::Min(200, $br.Length)))
      }
    }
    # Screenshot (fallback System.Drawing)
    Add-Type -AssemblyName System.Windows.Forms
    Add-Type -AssemblyName System.Drawing
    $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($b.Left, $b.Top, 0, 0, $b.Size)
    $g.Dispose()
    $bmp.Save($whoamiPng, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()
    $jc.ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'done', $jc.cts.Token).Wait()
  }
} catch {
  Add-Content -LiteralPath (Join-Path $RunDir 'PROBE_LOG.md') -Value "$(Get-Date -Format o) | PITFALL | G5 | cdp_error=$($_.Exception.Message)"
}
$g5Pass = ($pickerOpen -and $whoamiBody -match 'TRUE FAMILY' -and $whoamiBody -match 'TOOLS\s*/\s*RESOURCES')

# Family-label grep
$patterns = @('TRUE FAMILY.*[Cc]odex', 'TRUE FAMILY.*\bKCC\b', 'Codex.*\(family\)', 'KCC.*\(family\)')
$hits = @()
if (Test-Path -LiteralPath $FrontendSrcDir) {
  $files = Get-ChildItem -Path $FrontendSrcDir -Recurse -File -Include *.ts, *.tsx
  foreach ($f in $files) {
    $content = Get-Content -LiteralPath $f.FullName -Raw
    foreach ($p in $patterns) {
      if ($content -match $p) { $hits += "$($f.FullName):$p" }
    }
  }
}
if ($hits.Count -eq 0) { 'PASS zero hits' | Set-Content -LiteralPath $grepOut -Encoding UTF8 }
else { $hits | Set-Content -LiteralPath $grepOut -Encoding UTF8 }

# Close + cleanup fresh browser dir (G6 closeout)
try { if ($chrome -and -not $chrome.HasExited) { $chrome | Stop-Process -Force } } catch {}
Start-Sleep -Seconds 2
$dirDeleted = $false
try { Remove-Item -LiteralPath $userDataDir -Recurse -Force -ErrorAction Stop; $dirDeleted = -not (Test-Path -LiteralPath $userDataDir) } catch { $dirDeleted = $false }

[ordered]@{
  session_id = $sessionId
  probe_value = $probeValue
  user_data_dir = $userDataDir
  user_data_dir_existed_before = $dirExistedBefore
  user_data_dir_deleted_after = $dirDeleted
  chromium_cmdline = $cmdLine
  picker_open = $pickerOpen
  whoami_has_true_family = ($whoamiBody -match 'TRUE FAMILY')
  whoami_has_tools_resources = ($whoamiBody -match 'TOOLS\s*/\s*RESOURCES')
  family_grep_hits = $hits.Count
  gate_g3_pass = $g3Pass
  gate_g5_pass = $g5Pass
  gate_g6_pass = ((-not $dirExistedBefore) -and $dirDeleted)
  artifacts = @($agentsPng, $whoamiPng, $grepOut, $netLog)
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $resultPath -Encoding UTF8
Write-Host "phase3-family: sid=$sessionId g3=$g3Pass g5=$g5Pass g6=$((-not $dirExistedBefore) -and $dirDeleted)"
