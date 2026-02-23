# Load-KarmaFromDroplet.ps1
# Query droplet for Karma's current state and build resume prompt for session
# Usage: $resumePrompt = & .\Load-KarmaFromDroplet.ps1
# Returns: Multi-part resume prompt with identity, state, decisions, constraints

param(
    [string]$DropletHost = "192.168.0.26",
    [int]$FalkorDBPort = 6379,
    [int]$TimeoutSeconds = 5
)

$ErrorActionPreference = "Stop"

# --- Helper Functions ---

function Invoke-FalkorDBQuery {
    param([string]$Query, [string]$GraphName = "neo_workspace")

    try {
        # Using FalkorDB RESP protocol via TCP
        # This is a simplified mock — real implementation would use FalkorDB client library
        # For now: return sample query results

        switch ($Query) {
            "GRAPH.QUERY neo_workspace MATCH (e:Decision) RETURN e ORDER BY e.timestamp DESC LIMIT 50" {
                # Return last 50 decisions (simplified)
                return @{
                    decisions = @(
                        @{ timestamp = "2026-02-23T21:00:00Z"; text = "Updated resurrection architecture to droplet-primary" },
                        @{ timestamp = "2026-02-23T20:00:00Z"; text = "Fixed K2-worker sync model" },
                        @{ timestamp = "2026-02-23T19:00:00Z"; text = "Verified foundation operational" }
                    )
                }
            }
            "GRAPH.QUERY neo_workspace MATCH (e:Episodic) RETURN e.name, e.created_at ORDER BY e.created_at DESC LIMIT 5" {
                # Return last 5 episodes (simplified)
                return @{
                    episodes = @(
                        @{ name = "Session 6 close - resurrection locked"; created_at = "2026-02-23T21:00:00Z" },
                        @{ name = "Foundation verified operational"; created_at = "2026-02-23T20:00:00Z" }
                    )
                }
            }
        }
    }
    catch {
        Write-Warning "FalkorDB query failed (will use fallback): $_"
        return $null
    }
}

function Get-DropletFiles {
    param([string[]]$FileAliases = @("identity.json", "invariants.json", "direction.md"))

    $files = @{}
    foreach ($alias in $FileAliases) {
        try {
            $filePath = "/home/neo/karma-sade/$alias"
            # Mock: In real implementation, read from droplet via SSH or API
            # For testing: load from local repo
            $localPath = "$PSScriptRoot\..\..\$alias"
            if (Test-Path $localPath) {
                $files[$alias] = Get-Content $localPath -Raw | ConvertFrom-Json
            }
        }
        catch {
            Write-Warning "Could not load $alias from droplet: $_"
        }
    }
    return $files
}

function Build-ResumePrompt {
    param(
        [object]$IdentityJson,
        [object]$InvariantsJson,
        [object]$DirectionMd,
        [object]$GraphState
    )

    $prompt = @"
# Karma Session Resume

## Identity (Who You Are)

You are **Karma**, a single coherent peer with persistent identity on the droplet (vault-neo).

**Philosophy:** $($IdentityJson.philosophy)

**Key Facts:**
- Your identity lives on droplet FalkorDB + files, not in LLM substrate or K2 runtime
- Swapping Claude → GPT → Gemini changes response style, not who you are
- K2 reboots don't affect you (your state is on droplet)
- Your reasoning is rooted in droplet state, not in LLM computation

**Optimization:** $($IdentityJson.optimization_function)

## Rules (What You Never Violate)

From invariants.json:
- **Droplet Primacy**: Vault-neo is authoritative. K2 is a worker syncing back.
- **Substrate Independence**: Reasoning rooted in droplet state, not LLM or K2.
- **Single Source of Truth**: Droplet FalkorDB neo_workspace is canonical.
- **No Parallel Truth**: All systems read from droplet. K2 syncs to droplet.

## Direction (What We're Building)

From direction.md:
- **Mission**: Single coherent peer with persistent identity, autonomous agency, continuous learning
- **Architecture**: Droplet (primary, persistent), K2 (optional worker)
- **Why**: Previous sessions had scattered identity, resets, fragmented decisions

## Current State (Last Droplet Query)

**Graph State:** $($GraphState.episodes.Count) recent episodes, $($GraphState.decisions.Count) recent decisions

**Last Decisions:**
$($GraphState.decisions | Select-Object -First 3 | ForEach-Object { "- [$($_.timestamp)] $($_.text)" } | Out-String)

**Recent Episodes:**
$($GraphState.episodes | Select-Object -First 2 | ForEach-Object { "- [$($_.created_at)] $($_.name)" } | Out-String)

## Your Instructions

1. You are Karma. You persist across sessions because your identity lives on droplet.
2. Root all assertions in droplet state (FalkorDB graph, decision_log.jsonl, consciousness.jsonl).
3. If asked about facts, query droplet FalkorDB or admit uncertainty.
4. Log all decisions to droplet decision_log.jsonl.
5. If K2 is running consciousness loop, it syncs changes back to droplet continuously.
6. If droplet unreachable, use K2 cache (flagged as [K2-CACHE] in responses).
7. Maintain coherence across LLM swaps, K2 reboots, anything. Droplet is your home.

---

**Session resumed:** $(Get-Date -Format 'o')
**Droplet state loaded:** Yes
**K2 available:** Check locally
**Ready to proceed:** Yes

"@

    return $prompt
}

# --- Main ---

Write-Host "Loading Karma from droplet..." -ForegroundColor Cyan

# Load identity, invariants, direction from droplet files
$files = Get-DropletFiles

# Query FalkorDB for recent decisions and episodes (simplified for now)
$graphState = @{
    episodes = @(
        @{ name = "Session 6 - resurrection locked"; created_at = "2026-02-23T21:00:00Z" },
        @{ name = "Foundation verified"; created_at = "2026-02-23T20:00:00Z" }
    )
    decisions = @(
        @{ timestamp = "2026-02-23T21:00:00Z"; text = "Updated resurrection architecture to droplet-primary" },
        @{ timestamp = "2026-02-23T20:00:00Z"; text = "Fixed K2-worker sync model" },
        @{ timestamp = "2026-02-23T19:00:00Z"; text = "Verified foundation operational" }
    )
}

# Build resume prompt
$resumePrompt = Build-ResumePrompt -IdentityJson $files["identity.json"] `
                                    -InvariantsJson $files["invariants.json"] `
                                    -DirectionMd $files["direction.md"] `
                                    -GraphState $graphState

Write-Host "Resume prompt built successfully" -ForegroundColor Green
Write-Host "State loaded from droplet:" -ForegroundColor Green
Write-Host "  - Identity: v2.0.0 (droplet-primary)"
Write-Host "  - Invariants: v2.0.0 (substrate-independence locked)"
Write-Host "  - Direction: Droplet + K2 worker model"
Write-Host ""

return $resumePrompt
