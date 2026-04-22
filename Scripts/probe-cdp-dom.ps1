# probe-cdp-dom.ps1 - Read DOM attrs from Julian/Arknexusv6 via CDP
param(
  [int]$CdpPort = 9222,
  [string]$TargetTitle = 'Karma'
)
$ErrorActionPreference = 'Stop'

$targets = Invoke-RestMethod "http://127.0.0.1:$CdpPort/json"
$page = $targets | Where-Object { $_.type -eq 'page' -and $_.title -eq $TargetTitle } | Select-Object -First 1
if (-not $page) { Write-Host "no_target_title=$TargetTitle"; exit 1 }

$wsUri = [Uri]$page.webSocketDebuggerUrl
$ws = New-Object System.Net.WebSockets.ClientWebSocket
$ct = New-Object System.Threading.CancellationTokenSource 10000
$ws.ConnectAsync($wsUri, $ct.Token).Wait()

function Send-Cmd {
  param([int]$id, [string]$method, [hashtable]$params = @{})
  $msg = @{ id = $id; method = $method; params = $params } | ConvertTo-Json -Compress -Depth 8
  $buf = [Text.Encoding]::UTF8.GetBytes($msg)
  $seg = [ArraySegment[byte]]::new($buf)
  $ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $ct.Token).Wait()
}
function Recv-Until {
  param([int]$targetId)
  $sb = New-Object Text.StringBuilder
  while ($true) {
    $buf = [byte[]]::new(65536)
    $seg = [ArraySegment[byte]]::new($buf)
    $r = $ws.ReceiveAsync($seg, $ct.Token)
    $r.Wait()
    [void]$sb.Append([Text.Encoding]::UTF8.GetString($buf, 0, $r.Result.Count))
    if ($r.Result.EndOfMessage) {
      $msg = $sb.ToString() | ConvertFrom-Json
      if ($msg.id -eq $targetId) { return $msg }
      $sb.Clear() | Out-Null
    }
  }
}

Send-Cmd 1 'Runtime.evaluate' @{
  expression = "JSON.stringify({ hydration: document.documentElement.getAttribute('data-hydration-state'), session: document.documentElement.getAttribute('data-session-id'), pickerInDom: !!document.querySelector('[data-picker-open]'), bootMetrics: !!(window).__bootMetrics, bootMetricsSession: (window).__bootMetrics ? (window).__bootMetrics.session_id : null })"
  returnByValue = $true
}
$resp = Recv-Until -targetId 1
$ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'done', $ct.Token).Wait()
$value = $resp.result.result.value
Write-Host "CDP_DOM_PROBE: $value"
exit 0
