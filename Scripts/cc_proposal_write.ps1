<#
.SYNOPSIS
    CC Self-Proposal Writer — proposes behavioral changes for Sovereign review
.DESCRIPTION
    Writes proposals to cc_proposals.jsonl on K2. Watchdog tracks stability.
    Sovereign approves/rejects via bus or direct review.

    Types: pattern (new behavioral pattern), skill (skill modification suggestion),
           rule (CLAUDE.md rule suggestion), optimization (efficiency improvement)
.NOTES
    Writes to: K2:/mnt/c/dev/Karma/k2/cache/cc_proposals.jsonl
    Sovereign approval required for all proposals.
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("pattern", "skill", "rule", "optimization")]
    [string]$Type,

    [Parameter(Mandatory=$true)]
    [string]$Description,

    [Parameter(Mandatory=$false)]
    [string]$Rationale = "",

    [Parameter(Mandatory=$false)]
    [string]$Evidence = ""
)

$ErrorActionPreference = "Stop"

$ariaKeyPath = Join-Path $env:USERPROFILE ".aria-service-key"
if (-not (Test-Path $ariaKeyPath)) {
    Write-Error "No .aria-service-key found at $ariaKeyPath"
    exit 1
}
$ariaKey = (Get-Content $ariaKeyPath -Raw).Trim()
$ts = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")

$proposal = @{
    id = "prop-" + (Get-Date).ToString("yyyyMMdd-HHmmss")
    type = $Type
    description = $Description
    rationale = $Rationale
    evidence = $Evidence
    status = "pending"
    stability_score = 0
    created = $ts
}

$json = $proposal | ConvertTo-Json -Depth 3 -Compress
$bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
$b64 = [Convert]::ToBase64String($bytes)

$pyCmd = "import base64; f=open('/mnt/c/dev/Karma/k2/cache/cc_proposals.jsonl','a'); f.write(base64.b64decode('$b64').decode() + chr(10)); f.close(); print('proposal created: $($proposal.id)')"

$body = @{ command = "python3 -c `"$pyCmd`"" } | ConvertTo-Json
$resp = Invoke-RestMethod -Uri "http://100.75.109.92:7890/api/exec" -Method POST `
    -Headers @{ "Content-Type"="application/json"; "X-Aria-Service-Key"=$ariaKey } `
    -Body $body -TimeoutSec 15

if ($resp.exit_code -eq 0) {
    Write-Host $resp.stdout.Trim() -ForegroundColor Green
} else {
    Write-Host "Error: $($resp.stderr)" -ForegroundColor Red
}
