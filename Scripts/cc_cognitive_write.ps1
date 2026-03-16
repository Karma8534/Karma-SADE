<#
.SYNOPSIS
    CC Cognitive Checkpoint Writer — captures active reasoning state to K2
.DESCRIPTION
    Called at session-end (by wrap-session or manually) to write CC's active
    cognitive state to K2 cache. This is what closes the 30% continuity gap:
    captures not just WHAT was decided but HOW and WHY, plus open hypotheses.

    Writes to: K2:/mnt/c/dev/Karma/k2/cache/cc_cognitive_checkpoint.json
    Read by: cc_sentinel.py → build_brief() → resurrection context
.NOTES
    Requires: Aria service on K2 (100.75.109.92:7890/api/exec)
    Auth: .hub-chat-token in user home directory
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$ActiveReasoning,

    [Parameter(Mandatory=$false)]
    [string[]]$HypothesisTrees = @(),

    [Parameter(Mandatory=$false)]
    [string[]]$ReasoningChains = @(),

    [Parameter(Mandatory=$false)]
    [string[]]$NextMoves = @(),

    [Parameter(Mandatory=$false)]
    [string]$AgentContext = "",

    [Parameter(Mandatory=$false)]
    [string[]]$OpenQuestions = @()
)

$ErrorActionPreference = "Stop"

# Build checkpoint JSON
$checkpoint = @{
    timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
    session_id = [guid]::NewGuid().ToString().Substring(0, 8)
    active_reasoning = $ActiveReasoning
    hypothesis_trees = $HypothesisTrees
    reasoning_chains = $ReasoningChains
    next_moves = $NextMoves
    agent_context = $AgentContext
    open_questions = $OpenQuestions
}

$jsonPayload = $checkpoint | ConvertTo-Json -Depth 5 -Compress

# Read Aria service key (separate from hub token)
$ariaKeyPath = Join-Path $env:USERPROFILE ".aria-service-key"
if (-not (Test-Path $ariaKeyPath)) {
    Write-Error "No .aria-service-key found at $ariaKeyPath. Get it from K2: /etc/aria.env"
    exit 1
}
$token = (Get-Content $ariaKeyPath -Raw).Trim()

# Escape JSON for python command (double-escape for nested JSON in string)
$escapedJson = $jsonPayload.Replace('\', '\\').Replace("'", "\'").Replace('"', '\"')

# Write to K2 via Aria /api/exec
$command = "python3 -c `"import json; f=open('/mnt/c/dev/Karma/k2/cache/cc_cognitive_checkpoint.json','w'); json.dump(json.loads('$escapedJson'), f, indent=2); f.close(); print('OK')`""

$body = @{
    command = $command
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "http://100.75.109.92:7890/api/exec" `
        -Method POST `
        -Headers @{
            "Content-Type" = "application/json"
            "X-Aria-Service-Key" = $token
        } `
        -Body $body `
        -TimeoutSec 15

    if ($response.exit_code -eq 0) {
        Write-Host "Cognitive checkpoint written to K2 successfully" -ForegroundColor Green
    } else {
        Write-Host "K2 exec returned non-zero: $($response.stderr)" -ForegroundColor Red
    }
} catch {
    Write-Host "Failed to write cognitive checkpoint to K2: $_" -ForegroundColor Red
    exit 1
}
