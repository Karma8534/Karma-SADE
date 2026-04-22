param(
  [int]$CdpPort = 9222,
  [string]$TargetTitle = 'Karma',
  [string]$Token,
  [string]$Nonce = "smoke-nonce-$(Get-Date -Format 'HHmmss')"
)
$ErrorActionPreference = 'Stop'

$targets = Invoke-RestMethod "http://127.0.0.1:$CdpPort/json"
$page = $targets | Where-Object { $_.type -eq 'page' -and $_.title -eq $TargetTitle } | Select-Object -First 1
if (-not $page) { Write-Host "no_target"; exit 1 }
$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ct = New-Object System.Threading.CancellationTokenSource 20000
$ws.ConnectAsync([Uri]$page.webSocketDebuggerUrl, $ct.Token).Wait()

function Send-Eval {
  param([int]$id, [string]$expr, [bool]$awaitP = $false)
  $msg = @{ id = $id; method = 'Runtime.evaluate'; params = @{ expression = $expr; returnByValue = $true; awaitPromise = $awaitP } } | ConvertTo-Json -Compress -Depth 10
  $buf = [Text.Encoding]::UTF8.GetBytes($msg)
  $ws.SendAsync([ArraySegment[byte]]::new($buf), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct.Token).Wait()
}
function Recv-Until {
  param([int]$targetId)
  $sb = New-Object Text.StringBuilder
  while ($true) {
    $buf = [byte[]]::new(131072)
    $r = $ws.ReceiveAsync([ArraySegment[byte]]::new($buf), $ct.Token); $r.Wait()
    [void]$sb.Append([Text.Encoding]::UTF8.GetString($buf, 0, $r.Result.Count))
    if ($r.Result.EndOfMessage) {
      $m = $sb.ToString() | ConvertFrom-Json
      if ($m.id -eq $targetId) { return $m }
      $sb.Clear() | Out-Null
    }
  }
}

$seedExpr = "localStorage.setItem('karma-token','$Token'); localStorage.setItem('karma-ark-session-nonce','$Nonce'); location.reload(); 'seeded'"
Send-Eval 1 $seedExpr
$r1 = Recv-Until 1
Write-Host ("seed: " + $r1.result.result.value)
Start-Sleep -Seconds 6

# Reconnect WS after reload (page context destroyed)
$ws.Abort()
Start-Sleep -Seconds 2
$targets2 = Invoke-RestMethod "http://127.0.0.1:$CdpPort/json"
$page2 = $targets2 | Where-Object { $_.type -eq 'page' -and $_.title -eq $TargetTitle } | Select-Object -First 1
$ws2 = New-Object System.Net.WebSockets.ClientWebSocket
$ct2 = New-Object System.Threading.CancellationTokenSource 20000
$ws2.ConnectAsync([Uri]$page2.webSocketDebuggerUrl, $ct2.Token).Wait()

$probeExpr = "JSON.stringify({hydration: document.documentElement.getAttribute('data-hydration-state'), session: document.documentElement.getAttribute('data-session-id'), pickerAttr: (function(){var e=document.querySelector('[data-picker-open]');return e?e.getAttribute('data-picker-open'):null;})(), bootMetrics: !!window.__bootMetrics, bootMetricsSession: window.__bootMetrics ? window.__bootMetrics.session_id : null, bootMetricsTimestamp: window.__bootMetrics ? window.__bootMetrics.timestamp : null, conversationId: localStorage.getItem('karma-conversation-id'), nonce: localStorage.getItem('karma-ark-session-nonce')})"
$msg = @{ id = 2; method = 'Runtime.evaluate'; params = @{ expression = $probeExpr; returnByValue = $true } } | ConvertTo-Json -Compress -Depth 10
$buf = [Text.Encoding]::UTF8.GetBytes($msg)
$ws2.SendAsync([ArraySegment[byte]]::new($buf), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct2.Token).Wait()
$sb = New-Object Text.StringBuilder
while ($true) {
  $buf2 = [byte[]]::new(131072)
  $rr = $ws2.ReceiveAsync([ArraySegment[byte]]::new($buf2), $ct2.Token); $rr.Wait()
  [void]$sb.Append([Text.Encoding]::UTF8.GetString($buf2, 0, $rr.Result.Count))
  if ($rr.Result.EndOfMessage) {
    $m2 = $sb.ToString() | ConvertFrom-Json
    if ($m2.id -eq 2) { Write-Host ("PROBE: " + $m2.result.result.value); break }
    $sb.Clear() | Out-Null
  }
}
$ws2.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'done', $ct2.Token).Wait()
