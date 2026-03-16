<#
.SYNOPSIS
    CC Reasoning Arc Writer — manages multi-session hypothesis tracking on K2
.DESCRIPTION
    Appends, updates, or resolves reasoning arcs in cc_reasoning_arcs.jsonl.
    Each arc tracks a hypothesis across sessions with linked evidence.

    Actions: new, evidence, resolve, abandon
.NOTES
    Writes to: K2:/mnt/c/dev/Karma/k2/cache/cc_reasoning_arcs.jsonl
    Read by: cc_sentinel.py -> build_brief() -> resurrection context
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("new", "evidence", "resolve", "abandon")]
    [string]$Action,

    [Parameter(Mandatory=$false)]
    [string]$ArcId = "",

    [Parameter(Mandatory=$false)]
    [string]$Hypothesis = "",

    [Parameter(Mandatory=$false)]
    [string]$Summary = "",

    [Parameter(Mandatory=$false)]
    [int]$ObsId = 0
)

$ErrorActionPreference = "Stop"

$ariaKeyPath = Join-Path $env:USERPROFILE ".aria-service-key"
if (-not (Test-Path $ariaKeyPath)) {
    Write-Error "No .aria-service-key found at $ariaKeyPath"
    exit 1
}
$ariaKey = (Get-Content $ariaKeyPath -Raw).Trim()
$ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

switch ($Action) {
    "new" {
        if (-not $Hypothesis) { Write-Error "-Hypothesis required for new arc"; exit 1 }
        $id = "arc-" + (Get-Date).ToString("yyyyMMdd-HHmmss")
        $arc = @{
            id = $id
            hypothesis = $Hypothesis
            status = "active"
            evidence = @()
            created = $ts
            updated = $ts
        }
        $json = ($arc | ConvertTo-Json -Depth 5 -Compress)
        $ArcId = $id
    }
    "evidence" {
        if (-not $ArcId -or -not $Summary) { Write-Error "-ArcId and -Summary required"; exit 1 }
        $entry = @{
            obs_id = $ObsId
            summary = $Summary
            ts = $ts
        }
        $json = $null  # handled by python update logic
    }
    "resolve" {
        if (-not $ArcId) { Write-Error "-ArcId required"; exit 1 }
        $json = $null
    }
    "abandon" {
        if (-not $ArcId) { Write-Error "-ArcId required"; exit 1 }
        $json = $null
    }
}

# Build python command based on action
if ($Action -eq "new") {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $b64 = [Convert]::ToBase64String($bytes)
    $pyCmd = "import base64; f=open('/mnt/c/dev/Karma/k2/cache/cc_reasoning_arcs.jsonl','a'); f.write(base64.b64decode('$b64').decode() + chr(10)); f.close(); print('arc created: $ArcId')"
} elseif ($Action -eq "evidence") {
    $evidenceJson = (@{ obs_id=$ObsId; summary=$Summary; ts=$ts } | ConvertTo-Json -Compress)
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($evidenceJson)
    $b64 = [Convert]::ToBase64String($bytes)
    $pyCmd = @"
import json, base64
path = '/mnt/c/dev/Karma/k2/cache/cc_reasoning_arcs.jsonl'
lines = open(path).readlines()
new_evidence = json.loads(base64.b64decode('$b64').decode())
updated = False
with open(path, 'w') as f:
    for line in lines:
        if line.strip():
            arc = json.loads(line)
            if arc.get('id') == '$ArcId':
                arc.setdefault('evidence', []).append(new_evidence)
                arc['updated'] = '$ts'
                updated = True
            f.write(json.dumps(arc) + chr(10))
print('evidence added' if updated else 'arc not found: $ArcId')
"@
} else {
    # resolve or abandon
    $newStatus = if ($Action -eq "resolve") { "resolved" } else { "abandoned" }
    $pyCmd = @"
import json
path = '/mnt/c/dev/Karma/k2/cache/cc_reasoning_arcs.jsonl'
lines = open(path).readlines()
updated = False
with open(path, 'w') as f:
    for line in lines:
        if line.strip():
            arc = json.loads(line)
            if arc.get('id') == '$ArcId':
                arc['status'] = '$newStatus'
                arc['updated'] = '$ts'
                updated = True
            f.write(json.dumps(arc) + chr(10))
print('$Action' + ': $ArcId' if updated else 'arc not found: $ArcId')
"@
}

$body = @{ command = "python3 -c `"$pyCmd`"" } | ConvertTo-Json
$resp = Invoke-RestMethod -Uri "http://100.75.109.92:7890/api/exec" -Method POST `
    -Headers @{ "Content-Type"="application/json"; "X-Aria-Service-Key"=$ariaKey } `
    -Body $body -TimeoutSec 15

if ($resp.exit_code -eq 0) {
    Write-Host $resp.stdout.Trim() -ForegroundColor Green
} else {
    Write-Host "Error: $($resp.stderr)" -ForegroundColor Red
}
