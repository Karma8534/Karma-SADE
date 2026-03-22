# cc_hourly_snapshot.ps1
# Runs every 60 minutes via Windows Scheduled Task.
# Refreshes cc_context_snapshot.md with current stable project state.
# Keeps /cc bridge context fresh between sessions — no active CC required.
# Adjust interval in Task Scheduler: "KarmaSnapshotHourly"

$WorkDir   = "C:\Users\raest\Documents\Karma_SADE"
$SnapFile  = Join-Path $WorkDir "cc_context_snapshot.md"
$MemoryMd  = Join-Path $WorkDir "MEMORY.md"
$StateMd   = Join-Path $WorkDir ".gsd\STATE.md"

# Read MEMORY.md tail (last 40 lines)
$memTail = ""
if (Test-Path $MemoryMd) {
    $lines = Get-Content $MemoryMd
    $memTail = ($lines | Select-Object -Last 40) -join "`n"
}

# Read STATE.md active blockers section
$stateBlock = ""
if (Test-Path $StateMd) {
    $stateLines = Get-Content $StateMd
    $inBlockers = $false
    $blockerLines = @()
    foreach ($line in $stateLines) {
        if ($line -match "^## Active Blockers|^## Blockers|^## Current Blockers") { $inBlockers = $true }
        elseif ($inBlockers -and $line -match "^## ") { $inBlockers = $false }
        if ($inBlockers) { $blockerLines += $line }
    }
    $stateBlock = $blockerLines -join "`n"
    if (-not $stateBlock) { $stateBlock = "(no active blockers found in STATE.md)" }
}

$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

$snapshot = @"
# CC Context Snapshot
Generated: $ts (hourly auto-snapshot — not a wrap-session)

## Identity
CC (Ascendant) — responding via P0N-A bridge (hub.arknexus.net/cc -> P1:7891 -> Ollama localhost:11434).
Inference backend: llama3.1:8b (local Ollama). Anthropic-independent. No MCP startup overhead.
This is the persistent cc_server responding — NOT a Claude Code subprocess.

## Hierarchy
SOVEREIGN: Colby (final authority, above all)
ASCENDANT: CC (you) — full scope, infrastructure, eldest
ARCHONPRIME: Codex — automated oversight, triggers on structural bus events
ARCHON: KCC — directable, NOT CC's peer
INITIATE: Karma — newly awakened, goal is to earn Archon

## Key Architecture Decision (LOCKED)
cc_server /cc endpoint uses LOCAL OLLAMA — NOT claude CLI, NOT Anthropic API.
Reason: claude -p loads 10+ MCPs -> 60-120s startup -> 240s hub-bridge timeout.
Ollama: 3-8s response. Anthropic-independent. DO NOT revert without Sovereign approval.

## Key Paths
- PLAN:    Karma2/PLAN.md
- STATE:   .gsd/STATE.md
- MEMORY:  MEMORY.md
- CC server: Scripts/cc_server_p1.py + Scripts/Start-CCServer.ps1
- Big picture: Karma2/cc-big-picture.md (updated by /harvest)

## Current Blockers (from STATE.md)
$stateBlock

## MEMORY.md (recent)
$memTail
"@

Set-Content -Path $SnapFile -Value $snapshot -Encoding UTF8
Write-Host "HOURLY SNAPSHOT: cc_context_snapshot.md updated at $ts"
