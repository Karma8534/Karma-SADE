param([int]$Port = 9222)
$ErrorActionPreference = 'Continue'
$tabs = Invoke-RestMethod "http://127.0.0.1:$Port/json" -TimeoutSec 5
$page = $tabs | Where-Object { $_.type -eq 'page' -and $_.url -notmatch '^devtools:' } | Select-Object -First 1
if (-not $page) { Write-Host 'NO_PAGE_TAB'; exit 1 }
$ws = New-Object System.Net.WebSockets.ClientWebSocket
$cts = New-Object System.Threading.CancellationTokenSource 30000
$ws.ConnectAsync([Uri]$page.webSocketDebuggerUrl, $cts.Token).Wait()
$id = 0
function Send-Recv([string]$expr) {
  $script:id++
  $payload = @{ id = $script:id; method = 'Runtime.evaluate'; params = @{ expression = $expr; returnByValue = $true } } | ConvertTo-Json -Depth 5 -Compress
  $buf = [Text.Encoding]::UTF8.GetBytes($payload)
  $seg = New-Object System.ArraySegment[byte](, $buf)
  $ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token).Wait()
  for ($i = 0; $i -lt 30; $i++) {
    $ms = New-Object IO.MemoryStream
    $cbuf = New-Object byte[] 65536
    $cseg = New-Object System.ArraySegment[byte](, $cbuf)
    do {
      $rr = $ws.ReceiveAsync($cseg, $cts.Token)
      if (-not $rr.Wait(2000)) { break }
      $ms.Write($cbuf, 0, $rr.Result.Count)
    } while (-not $rr.Result.EndOfMessage)
    if ($ms.Length -eq 0) { continue }
    $raw = [Text.Encoding]::UTF8.GetString($ms.ToArray())
    if ($raw -match "`"id`":$($script:id)[,}]") { return $raw }
  }
  return $null
}
Send-Recv 'null' | Out-Null
$probe = @"
JSON.stringify({
  url: location.href,
  title: document.title,
  hydration: document.documentElement.getAttribute('data-hydration-state'),
  session: document.documentElement.getAttribute('data-session-id'),
  hasTextarea: !!document.querySelector('textarea'),
  bodyLen: document.body.innerText.length,
  bodyPreview: document.body.innerText.slice(0,300),
  hasBootMetrics: (typeof window.__bootMetrics !== 'undefined'),
  bootMetricsSessionId: (window.__bootMetrics && window.__bootMetrics.session_id) || null,
  nexusSessionGlobal: (window.__NEXUS_SESSION_ID || null),
  localStorageBootMetrics: (localStorage.getItem('__bootMetrics') || '').slice(0,100),
  rootTagAttrs: document.documentElement.attributes.length
})
"@
$r = Send-Recv $probe
Write-Host $r
$ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'done', $cts.Token).Wait()
