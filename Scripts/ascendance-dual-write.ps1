# ascendance-dual-write.ps1 — Dual-write wrapper per plan v2 §5 + directive v3 §6
# HARNESS_GATE: dual-write
# Usage: .\ascendance-dual-write.ps1 -Type PROOF -Title "..." -Text "..." -Gate G1_BOOT_DOM_ATTR -RunDir <path>
# Emits obs_id + bus_id to stdout on success; appends queue + PROBE_LOG.
param(
  [Parameter(Mandatory=$true)][ValidateSet('DECISION','PROOF','PITFALL','DIRECTION','INSIGHT')][string]$Type,
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$true)][string]$Text,
  [string]$Gate = 'plan-level',
  [Parameter(Mandatory=$true)][string]$RunDir,
  [switch]$QueueOnly
)
$ErrorActionPreference = 'Stop'
$utc = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')
$queuePath = Join-Path $RunDir 'dual-write-queue.jsonl'
$probePath = Join-Path $RunDir 'PROBE_LOG.md'
$sessionJson = Get-Content (Join-Path $RunDir 'session.json') -Raw | ConvertFrom-Json
$sid = $sessionJson.SESSION_ID

$entry = @{
  utc = $utc
  type = $Type
  gate = $Gate
  title = $Title
  text = $Text
  session_id = $sid
  obs_id = $null
  bus_id = $null
  state = 'pending'
}
$jsonLine = $entry | ConvertTo-Json -Compress -Depth 3
Add-Content -Path $queuePath -Value $jsonLine -Encoding utf8NoBOM

# Attempt MCP claude-mem via python (requires claude-mem worker on 37782)
$obsOk = $false; $obsId = $null
if (-not $QueueOnly) {
  try {
    $body = @{ text = $Text; title = "[$Type] $Title"; project = 'Karma_SADE' } | ConvertTo-Json -Compress
    $resp = Invoke-RestMethod -Uri 'http://127.0.0.1:37782/api/save_observation' -Method POST -Body $body -ContentType 'application/json' -TimeoutSec 10
    if ($resp.success) { $obsOk = $true; $obsId = $resp.id }
  } catch { $obsOk = $false }
}

# Attempt bus POST via ssh vault-neo
$busOk = $false; $busId = $null
if (-not $QueueOnly) {
  try {
    $msg = "[$Type][$Gate] $Title — $Text"
    $pyCmd = @"
import json, urllib.request
token = open('/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt').read().strip()
payload = json.dumps({'from':'cc','to':'all','type':'inform','urgency':'informational','content': $(ConvertTo-Json $msg -Compress) }).encode()
req = urllib.request.Request('https://hub.arknexus.net/v1/coordination/post', data=payload, headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=10) as r:
    d = json.loads(r.read())
    print(d.get('id',''))
"@
    $busId = (ssh vault-neo "python3 -c `"$($pyCmd -replace '`','\\`' -replace '"','\"')`"") 2>$null
    if ($busId -and $busId -match '^coord_') { $busOk = $true }
  } catch { $busOk = $false }
}

# Update queue entry state
$lines = Get-Content $queuePath
$idx = $lines.Count - 1
$entry.obs_id = $obsId
$entry.bus_id = $busId
$entry.state = if ($obsOk -and $busOk) { 'confirmed' } else { 'pending' }
$lines[$idx] = ($entry | ConvertTo-Json -Compress -Depth 3)
Set-Content -Path $queuePath -Value $lines -Encoding utf8NoBOM

# Append PROBE_LOG
Add-Content -Path $probePath -Value "$utc | $Type | $Gate | obs=$($obsId) | bus=$($busId) | $Title | art_sha=none" -Encoding utf8NoBOM

Write-Host "obs_id=$obsId bus_id=$busId state=$($entry.state)"
exit (if ($obsOk -and $busOk) { 0 } else { 3 })
