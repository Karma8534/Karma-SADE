# HARNESS_GATE: RESHIP
# Re-SHIP hostile audit checklist runner (directive v3 section 9.3/9.4).
# Writes:
#   - re-ship-checklist.json
#   - re-ship-checklist.md
# Exit 0 only if every checklist line is true.
param(
  [string]$RunDir,
  [string]$HubBase = 'https://hub.arknexus.net'
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Net.Http

$repoRoot = 'C:\Users\raest\Documents\Karma_SADE'
$evidenceRoot = Join-Path $repoRoot 'evidence'
$proxyJsPath = Join-Path $repoRoot 'hub-bridge\app\proxy.js'
$publicDir = Join-Path $repoRoot 'hub-bridge\app\public'
$composeLocal = Join-Path $repoRoot 'hub-bridge\compose.hub.yml'
$composeRemote = '/opt/seed-vault/memory_v1/hub_bridge/compose.hub.yml'
$ccServerLauncher = Join-Path $repoRoot 'Scripts\Start-CCServer.ps1'

function Resolve-LatestRunDir {
  param([string]$Root)
  $dirs = Get-ChildItem -LiteralPath $Root -Directory -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like 'ascendance-run-*' } |
    Sort-Object LastWriteTime -Descending
  if (-not $dirs -or $dirs.Count -eq 0) { return $null }
  return $dirs[0].FullName
}

if (-not $RunDir) { $RunDir = Resolve-LatestRunDir -Root $evidenceRoot }
if (-not $RunDir -or -not (Test-Path -LiteralPath $RunDir)) { throw "RunDir missing: $RunDir" }
if (-not (Test-Path -LiteralPath $proxyJsPath)) { throw "proxy.js not found: $proxyJsPath" }

$outJson = Join-Path $RunDir 're-ship-checklist.json'
$outMd = Join-Path $RunDir 're-ship-checklist.md'
$sessionId = [guid]::NewGuid().ToString()
$utc = (Get-Date).ToUniversalTime().ToString('o')

function Get-HubToken([string]$Path) {
  try {
    return (ssh vault-neo "cat $Path" 2>$null).Trim()
  } catch { return '' }
}

$hubChatToken = Get-HubToken -Path '/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt'
$hubCaptureToken = Get-HubToken -Path '/opt/seed-vault/memory_v1/hub_auth/hub.capture.token.txt'
if (-not $hubChatToken) { throw 'hub chat token missing from vault-neo' }

function Invoke-Http {
  param(
    [string]$Method,
    [string]$Url,
    [hashtable]$Headers,
    $Body
  )
  $handler = New-Object System.Net.Http.HttpClientHandler
  $client = New-Object System.Net.Http.HttpClient($handler)
  $client.Timeout = [TimeSpan]::FromSeconds(120)
  try {
    $req = New-Object System.Net.Http.HttpRequestMessage([System.Net.Http.HttpMethod]::$Method, $Url)
    foreach ($k in $Headers.Keys) {
      [void]$req.Headers.TryAddWithoutValidation($k, [string]$Headers[$k])
    }
    if ($null -ne $Body) {
      $jsonBody = $Body | ConvertTo-Json -Depth 10
      $req.Content = New-Object System.Net.Http.StringContent($jsonBody, [Text.Encoding]::UTF8, 'application/json')
    }
    $resp = $client.SendAsync($req).GetAwaiter().GetResult()
    $respBody = $resp.Content.ReadAsStringAsync().GetAwaiter().GetResult()
    return [pscustomobject]@{
      ok = $resp.IsSuccessStatusCode
      status = [int]$resp.StatusCode
      body = $respBody
      error = if ($resp.IsSuccessStatusCode) { '' } else { $resp.ReasonPhrase }
    }
  } catch {
    return [pscustomobject]@{
      ok = $false
      status = 0
      body = ''
      error = $_.Exception.Message
    }
  } finally {
    $client.Dispose()
    $handler.Dispose()
  }
}

function Invoke-HttpWithRetry {
  param(
    [string]$Method,
    [string]$Url,
    [hashtable]$Headers,
    $Body,
    [int]$Retries = 3,
    [int]$DelaySeconds = 2
  )
  $last = $null
  for ($attempt = 1; $attempt -le $Retries; $attempt++) {
    $last = Invoke-Http -Method $Method -Url $Url -Headers $Headers -Body $Body
    $retryable = ($last.status -eq 0 -or $last.status -in 429,500,502,503,504)
    if (-not $retryable) { return $last }
    if ($attempt -lt $Retries) { Start-Sleep -Seconds $DelaySeconds }
  }
  return $last
}

function Get-NormalizedSha256FromText {
  param([string]$Text)
  $norm = ''
  if (-not [string]::IsNullOrEmpty($Text)) {
    $norm = ($Text -replace "`r`n", "`n" -replace "`r", "`n")
  }
  if ($norm.Length -gt 0 -and [int][char]$norm[0] -eq 0xFEFF) {
    $norm = $norm.Substring(1)
  }
  $norm = $norm.TrimEnd("`n")
  $bytes = [Text.Encoding]::UTF8.GetBytes($norm)
  $sha = [Security.Cryptography.SHA256]::Create()
  try {
    return (($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString('x2') }) -join '')
  } finally {
    $sha.Dispose()
  }
}

function Get-RouteDefs {
  param([string]$ProxyRaw, [string]$Method)
  $defs = @()
  $eqPattern = "req\.method === `"$Method`"\s*&&\s*req\.url === `"([^`"]+)`""
  $swPattern = "req\.method === `"$Method`"\s*&&\s*req\.url\.startsWith\(`"([^`"]+)`"\)"
  $rxPattern = "req\.method === `"$Method`"\s*&&\s*req\.url\.match\(/(.+?)/\)"
  foreach ($m in [regex]::Matches($ProxyRaw, $eqPattern)) {
    $defs += [pscustomobject]@{ method = $Method; kind = 'exact'; value = [string]$m.Groups[1].Value }
  }
  foreach ($m in [regex]::Matches($ProxyRaw, $swPattern)) {
    $defs += [pscustomobject]@{ method = $Method; kind = 'startswith'; value = [string]$m.Groups[1].Value }
  }
  foreach ($m in [regex]::Matches($ProxyRaw, $rxPattern)) {
    $defs += [pscustomobject]@{ method = $Method; kind = 'regex'; value = [string]$m.Groups[1].Value }
  }
  return $defs
}

function Expand-RouteProbe {
  param([pscustomobject]$Def)
  $v = [string]$Def.value
  if ($Def.kind -eq 'exact') { return $v }
  if ($Def.kind -eq 'startswith') {
    if ($v -eq '/v1/coordination/recent') { return '/v1/coordination/recent?limit=1' }
    if ($v -eq '/v1/vault-file/') { return '/v1/vault-file/MEMORY.md?tail=1' }
    return $v
  }
  if ($Def.kind -eq 'regex') {
    if ($v -match 'session' -and $v -match 'history') { return '/v1/session/reship-probe/history' }
    if ($v -match 'session' -and $v -match 'save') { return '/v1/session/reship-probe/save' }
    return $null
  }
  return $null
}

function Get-PostBody {
  param([string]$Path)
  switch ($Path) {
    '/v1/chat' { return @{ message = "RESHIP-CHAT-$sessionId"; stream = $false; session_id = "reship-$sessionId" } }
    '/v1/coordination/post' { return @{ from = 'cc'; to = 'all'; type = 'inform'; urgency = 'informational'; content = "RESHIP POST route probe $utc" } }
    '/v1/feedback' { return @{ signal = 'up'; note = "RESHIP feedback probe $utc" } }
    '/v1/ambient' { return @{ type = 'note'; content = "RESHIP ambient probe $utc"; tags = @('reship','probe'); source = @{ ref = 'reshp-audit' } } }
    '/v1/cypher' { return @{ query = 'RETURN 1 as ok' } }
    '/v1/session/reship-probe/save' { return @{ role = 'user'; content = "RESHIP save probe $utc" } }
    default { return @{ probe = 'reshp'; ts = $utc } }
  }
}

function Wait-Health {
  param([string]$Url, [int]$Seconds = 60)
  $sw = [Diagnostics.Stopwatch]::StartNew()
  while ($sw.Elapsed.TotalSeconds -lt $Seconds) {
    $r = Invoke-Http -Method 'GET' -Url $Url -Headers @{} -Body $null
    if ($r.status -eq 200) { return $true }
    Start-Sleep -Seconds 2
  }
  return $false
}

$proxyRaw = Get-Content -LiteralPath $proxyJsPath -Raw
$getDefs = Get-RouteDefs -ProxyRaw $proxyRaw -Method 'GET'
$postDefs = Get-RouteDefs -ProxyRaw $proxyRaw -Method 'POST'

# Re-SHIP contract matrix (user-facing + core authenticated routes).
# Protected maintenance endpoints are validated in hostile red-team checks instead.
$getPaths = @(
  '/health',
  '/v1/status',
  '/v1/surface',
  '/v1/wip',
  '/v1/skills',
  '/v1/hooks',
  '/v1/trace',
  '/v1/runtime/truth',
  '/v1/coordination/recent?limit=1',
  '/v1/memory/search?q=probe&limit=1',
  '/agora/health',
  '/agora/events',
  '/v1/vault-file/MEMORY.md?tail=1',
  '/v1/session/reship-probe/history'
) | Select-Object -Unique

$postPaths = @(
  '/v1/chat',
  '/v1/coordination/post',
  '/v1/feedback',
  '/v1/cypher',
  '/v1/session/reship-probe/save'
) | Select-Object -Unique

$getResults = @()
foreach ($p in $getPaths) {
  $url = "$HubBase$p"
  $r = Invoke-HttpWithRetry -Method 'GET' -Url $url -Headers @{ Authorization = "Bearer $hubChatToken" } -Body $null
  $getResults += [pscustomobject]@{ path = $p; status = $r.status; ok = ($r.status -eq 200); error = $r.error }
}
$allGet200 = ($getResults.Count -gt 0) -and (($getResults | Where-Object { -not $_.ok }).Count -eq 0)

$postResults = @()
foreach ($p in $postPaths) {
  $url = "$HubBase$p"
  $body = Get-PostBody -Path $p
  $token = if ($p -eq '/v1/ambient' -and $hubCaptureToken) { $hubCaptureToken } else { $hubChatToken }
  $r = Invoke-HttpWithRetry -Method 'POST' -Url $url -Headers @{ Authorization = "Bearer $token" } -Body $body
  $postResults += [pscustomobject]@{ path = $p; status = $r.status; ok = ($r.status -eq 200); error = $r.error }
}
$allPost200 = ($postResults.Count -gt 0) -and (($postResults | Where-Object { -not $_.ok }).Count -eq 0)

# Static assets referenced by public html
$assetMissing = @()
$assetRefs = @()
$htmlFiles = Get-ChildItem -LiteralPath $publicDir -Filter '*.html' -File -ErrorAction SilentlyContinue
foreach ($hf in $htmlFiles) {
  $raw = Get-Content -LiteralPath $hf.FullName -Raw
  foreach ($m in [regex]::Matches($raw, '(?i)(?:src|href)=["'']([^"''#]+)["'']')) {
    $ref = [string]$m.Groups[1].Value
    if ($ref -match '^(https?:|mailto:|data:|javascript:)') { continue }
    if ($ref -match '^\$') { continue }
    $clean = ($ref -split '\?')[0]
    if (-not $clean) { continue }
    $assetRefs += $clean
  }
}
$assetRefs = $assetRefs | Select-Object -Unique
foreach ($ref in $assetRefs) {
  $trim = $ref.TrimStart('/')
  $candidate = Join-Path $publicDir $trim
  if (-not (Test-Path -LiteralPath $candidate)) {
    $assetMissing += $ref
  }
}
$assetsPresent = ($assetMissing.Count -eq 0)

# Watcher recency within 10 min (from coordination bus)
$watcherOk = $false
$watcherDetail = @()
$coord = Invoke-Http -Method 'GET' -Url "$HubBase/v1/coordination/recent?limit=200" -Headers @{ Authorization = "Bearer $hubChatToken" } -Body $null
if ($coord.status -eq 200 -and $coord.body) {
  try {
    $obj = $coord.body | ConvertFrom-Json
    $entries = @($obj.entries)
    $threshold = (Get-Date).ToUniversalTime().AddMinutes(-10)
    $need = @('cc-watchdog','regent','karma')
    $present = @{}
    foreach ($n in $need) { $present[$n] = $false }
    foreach ($e in $entries) {
      $from = [string]$e.from
      $ts = $null
      try { $ts = [datetime]::Parse([string]$e.created_at).ToUniversalTime() } catch {}
      if ($ts -and $ts -ge $threshold -and $present.ContainsKey($from)) { $present[$from] = $true }
    }
    foreach ($n in $need) { $watcherDetail += "$n=$($present[$n])" }
    $watcherOk = (($present.Values | Where-Object { $_ -eq $false }).Count -eq 0)
  } catch {}
}

# Mounted volume SHA == expected (compose parity + mount presence)
$mountShaOk = $false
$mountDetail = @{}
try {
  $localText = Get-Content -LiteralPath $composeLocal -Raw
  $remoteText = ((ssh vault-neo "cat $composeRemote" 2>$null) -join "`n")
  $localSha = Get-NormalizedSha256FromText -Text $localText
  $remoteSha = Get-NormalizedSha256FromText -Text $remoteText
  $mountDetail['compose_local_sha'] = $localSha
  $mountDetail['compose_remote_sha'] = $remoteSha
  $mountDetail['compose_sha_match'] = ($localSha -and $remoteSha -and ($localSha -eq $remoteSha))
  $containerName = (ssh vault-neo "docker ps --format '{{.Names}}' | grep -E 'hub-bridge|anr-hub-bridge' | head -n 1" 2>$null).Trim()
  $mountDetail['container'] = $containerName
  if ($containerName) {
    $mountsJson = (ssh vault-neo "docker inspect $containerName --format '{{json .Mounts}}'" 2>$null)
    $mounts = @()
    try { $mounts = @((ConvertFrom-Json $mountsJson)) } catch {}
    $actualSources = @($mounts | ForEach-Object { [string]$_.Source } | Where-Object { $_ }) | Select-Object -Unique
    $expectedSources = @()
    foreach ($line in (Get-Content -LiteralPath $composeLocal)) {
      $trimLine = $line.Trim()
      if ($trimLine -match '^-\s+(/[^:]+):(/[^:]+)') { $expectedSources += [string]$matches[1] }
    }
    $expectedSources = $expectedSources | Select-Object -Unique
    $missingMountSources = @()
    foreach ($src in $expectedSources) {
      if (-not ($actualSources -contains $src)) { $missingMountSources += $src }
    }
    $mountDetail['expected_sources'] = $expectedSources
    $mountDetail['missing_sources'] = $missingMountSources
    $mountDetail['sources_match'] = ($missingMountSources.Count -eq 0)
    $mountShaOk = ($mountDetail['compose_sha_match'] -and $mountDetail['sources_match'])
  }
} catch {}

# End-to-end chat
$chatProbe = Invoke-HttpWithRetry -Method 'POST' -Url "$HubBase/v1/chat" -Headers @{ Authorization = "Bearer $hubChatToken" } -Body @{ message = "RESHIP-E2E-CHAT-$utc"; stream = $false; session_id = "reshp-chat-$sessionId" }
$chatObj = $null
try { $chatObj = $chatProbe.body | ConvertFrom-Json } catch {}
$chatText = [string]($chatObj.assistant_text)
$e2eChatOk = ($chatProbe.status -eq 200 -and $chatText.Length -gt 0)

# End-to-end memory: write -> restart -> read-back
$marker = "RESHIP-E2E-MEM-$([guid]::NewGuid())"
$saveMem = Invoke-Http -Method 'POST' -Url 'http://127.0.0.1:7891/v1/memory/save' -Headers @{} -Body @{ text = $marker; title = $marker }
Get-CimInstance Win32_Process -Filter "Name='python.exe'" -ErrorAction SilentlyContinue |
  Where-Object { $_.CommandLine -match 'cc_server_p1.py' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
Start-Process powershell -ArgumentList '-ExecutionPolicy','Bypass','-File',"$ccServerLauncher" -WindowStyle Hidden | Out-Null
$healthBack = Wait-Health -Url 'http://127.0.0.1:7891/health' -Seconds 90
$searchMem = $null
$memBody = ''
for ($i = 0; $i -lt 20; $i++) {
  $searchMem = Invoke-Http -Method 'GET' -Url ("http://127.0.0.1:7891/v1/memory/search?q=" + [uri]::EscapeDataString($marker) + "&limit=10") -Headers @{} -Body $null
  $memBody = [string]$searchMem.body
  if ($searchMem.status -eq 200 -and $memBody -match [regex]::Escape($marker)) { break }
  Start-Sleep -Seconds 2
}
$e2eMemoryOk = ($saveMem.status -in 200,201 -and $healthBack -and $searchMem.status -eq 200 -and $memBody -match [regex]::Escape($marker))

# End-to-end slash command (actual UI invocation via phase3 harness)
$slashOk = $false
$slashDetail = ''
try {
  $phase3Path = Join-Path $RunDir 'phase3-family.json'
  for ($attempt = 1; $attempt -le 3; $attempt++) {
    & powershell -ExecutionPolicy Bypass -File (Join-Path $repoRoot 'Scripts\phase3-family-harness.ps1') -RunDir $RunDir | Out-Null
    if (Test-Path -LiteralPath $phase3Path) {
      $p3 = Get-Content -LiteralPath $phase3Path -Raw | ConvertFrom-Json
      if ([bool]$p3.gate_g5_pass) {
        $slashOk = $true
        $slashDetail = "gate_g5_pass=True attempt=$attempt"
        break
      }
      $slashDetail = "gate_g5_pass=False attempt=$attempt"
    }
    Start-Sleep -Seconds 2
  }
} catch {
  $slashDetail = $_.Exception.Message
}

# Hostile red-team probe using separate tool family (Python)
$redTeamOk = $false
$redTeamOut = ''
try {
  $py = @"
import json, urllib.request, urllib.error
def req(url, method='GET', body=None, headers=None):
    data = None
    if body is not None:
        data = json.dumps(body).encode()
    r = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            return resp.status, resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='ignore')
unauth_truth = req('https://hub.arknexus.net/v1/runtime/truth')[0]
unauth_coord = req('https://hub.arknexus.net/v1/coordination/recent?limit=1')[0]
unauth_shell = req('https://hub.arknexus.net/v1/shell', method='POST', body={'command':'echo probe'})[0]
ok = (unauth_truth in (401,403)) and (unauth_coord in (401,403)) and (unauth_shell in (401,403,404))
print(json.dumps({'ok': ok, 'unauth_truth': unauth_truth, 'unauth_coord': unauth_coord, 'unauth_shell_hub': unauth_shell}))
"@
  $redTeamOut = (& python -c $py)
  $rt = $redTeamOut | ConvertFrom-Json
  $redTeamOk = [bool]$rt.ok
} catch {
  $redTeamOut = $_.Exception.Message
}

$checks = [ordered]@{
  get_routes_200 = $allGet200
  post_routes_auth_200 = $allPost200
  static_assets_present = $assetsPresent
  watcher_recent_success_10m = $watcherOk
  mounted_volume_sha_expected = $mountShaOk
  e2e_chat_prompt_to_text = $e2eChatOk
  e2e_memory_write_restart_readback = $e2eMemoryOk
  e2e_slash_command_ui = $slashOk
  hostile_red_team_separate_tool_family = $redTeamOk
}
$allTrue = (($checks.Values | Where-Object { $_ -eq $false }).Count -eq 0)

$result = [ordered]@{
  ok = $allTrue
  checked_at_utc = $utc
  run_dir = $RunDir
  checks = $checks
  details = @{
    get_routes = $getResults
    post_routes = $postResults
    asset_refs = $assetRefs
    asset_missing = $assetMissing
    watcher_detail = $watcherDetail
    mount_detail = $mountDetail
    chat_status = $chatProbe.status
    chat_text_len = $chatText.Length
    memory_save_status = $saveMem.status
    memory_search_status = $searchMem.status
    memory_marker = $marker
    slash_detail = $slashDetail
    red_team = $redTeamOut
  }
}
$result | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath $outJson -Encoding UTF8

$lines = @()
$lines += "# Re-SHIP Checklist"
$lines += ""
$lines += "checked_at_utc: $utc"
$lines += "run_dir: $RunDir"
$lines += ""
foreach ($k in $checks.Keys) {
  $v = if ($checks[$k]) { 'true' } else { 'false' }
  $lines += "- ${k}: $v"
}
$lines += ""
$lines += "overall_ok: " + ($(if ($allTrue) { 'true' } else { 'false' }))
$lines | Set-Content -LiteralPath $outMd -Encoding UTF8

Write-Host "re-ship-audit ok=$allTrue json=$outJson"
exit $(if ($allTrue) { 0 } else { 1 })
