param(
  [Parameter(Mandatory=$true)][string]$RunDir,
  [Parameter(Mandatory=$true)][string]$GateId,
  [Parameter(Mandatory=$true)][string]$EventType,
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$true)][string]$Text,
  [string]$Project = 'Karma_SADE'
)
$ErrorActionPreference = 'Stop'
$utc = (Get-Date).ToUniversalTime().ToString('o')

# claude-mem save_observation via MCP-bridge approach: write observation content to a temp file,
# invoke the process via existing save_observation pattern. Since we're invoked from PS we
# cannot call MCP directly; queue line with state=pending until verified by caller layer that
# does have MCP access. Caller (CC) should invoke save_observation + bus post inline.
# This script's job: append canonical queue line + PROBE_LOG line for this event.

$queuePath = Join-Path $RunDir 'dual-write-queue.jsonl'
$probePath = Join-Path $RunDir 'PROBE_LOG.md'

$entry = [ordered]@{
  utc     = $utc
  type    = $EventType
  gate    = $GateId
  title   = $Title
  text    = $Text
  state   = 'pending'
  obs_id  = $null
  bus_id  = $null
  session_id = ((Get-Content -LiteralPath (Join-Path $RunDir 'session.json') -Raw | ConvertFrom-Json).SESSION_ID)
}
$line = $entry | ConvertTo-Json -Compress
Add-Content -LiteralPath $queuePath -Value $line

# PROBE_LOG line
$probeLine = "$utc | $EventType | $GateId | obs=pending | bus=pending | $Title | art=RT"
Add-Content -LiteralPath $probePath -Value $probeLine

Write-Host ("queued: $GateId $EventType utc=$utc")
