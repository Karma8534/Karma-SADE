param([int]$Port = 9222, [string]$TestPrompt = 'respond with the single word PONG')
$ErrorActionPreference = 'Continue'
$tabs = Invoke-RestMethod "http://127.0.0.1:$Port/json" -TimeoutSec 5
$page = $tabs | Where-Object { $_.type -eq 'page' -and $_.url -notmatch '^devtools:' } | Select-Object -First 1
if (-not $page) { Write-Host 'NO_PAGE_TAB'; exit 1 }
$token = (ssh vault-neo 'cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt').Trim()
$ws = New-Object System.Net.WebSockets.ClientWebSocket
$cts = New-Object System.Threading.CancellationTokenSource 180000
$ws.ConnectAsync([Uri]$page.webSocketDebuggerUrl, $cts.Token).Wait()
$id = 0
function Send-Recv([string]$expr, [int]$timeoutMs = 30000) {
  $script:id++
  $payload = @{ id = $script:id; method = 'Runtime.evaluate'; params = @{ expression = $expr; returnByValue = $true; awaitPromise = $true } } | ConvertTo-Json -Depth 5 -Compress
  $buf = [Text.Encoding]::UTF8.GetBytes($payload)
  $seg = New-Object System.ArraySegment[byte](, $buf)
  $ws.SendAsync($seg, [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $cts.Token).Wait()
  $start = [Diagnostics.Stopwatch]::StartNew()
  while ($start.ElapsedMilliseconds -lt $timeoutMs) {
    $ms = New-Object IO.MemoryStream
    $cbuf = New-Object byte[] 131072
    $cseg = New-Object System.ArraySegment[byte](, $cbuf)
    do {
      $rr = $ws.ReceiveAsync($cseg, $cts.Token)
      if (-not $rr.Wait(3000)) { break }
      $ms.Write($cbuf, 0, $rr.Result.Count)
    } while (-not $rr.Result.EndOfMessage)
    if ($ms.Length -eq 0) { continue }
    $raw = [Text.Encoding]::UTF8.GetString($ms.ToArray())
    if ($raw -match "`"id`":$($script:id)[,}]") { return $raw }
  }
  return $null
}

# Seed auth + reload
Send-Recv "localStorage.setItem('karma-token','$token'); localStorage.setItem('karma-authenticated','true'); location.reload();" | Out-Null
Start-Sleep -Seconds 8

# Reacquire WS after reload
$tabs2 = Invoke-RestMethod "http://127.0.0.1:$Port/json" -TimeoutSec 5
$page2 = $tabs2 | Where-Object { $_.type -eq 'page' -and $_.url -notmatch '^devtools:' } | Select-Object -First 1
if ($page2 -and $page2.webSocketDebuggerUrl -ne $page.webSocketDebuggerUrl) {
  try { $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'r', $cts.Token).Wait() } catch {}
  $ws = New-Object System.Net.WebSockets.ClientWebSocket
  $cts = New-Object System.Threading.CancellationTokenSource 180000
  $ws.ConnectAsync([Uri]$page2.webSocketDebuggerUrl, $cts.Token).Wait()
  $script:id = 0
  Send-Recv 'null' | Out-Null
}

# Type prompt via React-native setter + submit via Enter keydown on textarea
$setInput = @"
(function(){
  var ta = document.querySelector('textarea');
  if (!ta) return 'NO_TEXTAREA';
  ta.focus();
  var p = Object.getPrototypeOf(ta);
  var d = Object.getOwnPropertyDescriptor(p, 'value');
  (d && d.set ? d.set.call(ta, '$TestPrompt') : (ta.value = '$TestPrompt'));
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  return 'OK';
})()
"@
Send-Recv $setInput | Out-Null
Start-Sleep -Milliseconds 500

# Click Send button (find button with "SEND" text or type submit)
$clickSend = @"
(function(){
  var btns = document.querySelectorAll('button');
  for (var i = 0; i < btns.length; i++) {
    var t = (btns[i].innerText || btns[i].textContent || '').trim().toUpperCase();
    if (t === 'SEND' || t.indexOf('SEND') === 0) { btns[i].click(); return 'CLICKED_' + i; }
  }
  // Fallback: dispatch Enter on textarea
  var ta = document.querySelector('textarea');
  if (ta) {
    ta.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true, cancelable: true }));
    return 'ENTER_FALLBACK';
  }
  return 'NO_SEND';
})()
"@
Send-Recv $clickSend | Out-Null
Start-Sleep -Seconds 15

# Poll body for response + reconnecting detection
$probe = "JSON.stringify({bodyLen:document.body.innerText.length,hasReconnecting:document.body.innerText.indexOf('reconnecting')>-1,hasThinking:document.body.innerText.indexOf('thinking')>-1,bodyTail:document.body.innerText.slice(-600)})"
$r = Send-Recv $probe
Write-Host $r
$ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, 'done', $cts.Token).Wait()
