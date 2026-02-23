# Get-KarmaContext.ps1
# Fetches Karma's live CC session brief at CC session start.
# Primary: SSH to vault-neo, run gen-cc-brief.py, read cc-session-brief.md.
# Writes to cc-session-brief.md and karma-context.md (both gitignored) for CC to read.
# Fallback: K2 FalkorDB at 192.168.0.226:6379.

param(
    [string]$OutputFile      = "$PSScriptRoot\..\..\karma-context.md",
    [string]$TmpFile         = "$PSScriptRoot\..\..\karma-context.md.tmp",
    [string]$BriefOutputFile = "$PSScriptRoot\..\..\cc-session-brief.md",
    [string]$VaultNeoAlias   = "vault-neo",
    [string]$K2Host          = "192.168.0.226",
    [int]$K2Port             = 6379,
    [string]$GraphName       = "neo_workspace",
    [int]$VaultTimeoutSec    = 15,
    [int]$K2TimeoutMs        = 2000
)

$OutputFile      = [System.IO.Path]::GetFullPath($OutputFile)
$TmpFile         = [System.IO.Path]::GetFullPath($TmpFile)
$BriefOutputFile = [System.IO.Path]::GetFullPath($BriefOutputFile)
$Timestamp       = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Context {
    param([string]$Content)
    [System.IO.File]::WriteAllText($TmpFile, $Content, [System.Text.Encoding]::UTF8)
    Move-Item -Path $TmpFile -Destination $OutputFile -Force
}

# --- Primary path: vault-neo SSH (gen-cc-brief.py + read result) ---
function Get-VaultNeoContext {
    try {
        # Step 1: run the brief generator on vault-neo
        $genJob = Start-Job {
            param($alias)
            ssh $alias "python3 /home/neo/karma-sade/Scripts/gen-cc-brief.py"
        } -ArgumentList $VaultNeoAlias
        $genCompleted = Wait-Job $genJob -Timeout $VaultTimeoutSec
        if (-not $genCompleted) {
            Remove-Job $genJob -Force
            return $null
        }
        $genOut = Receive-Job $genJob
        Remove-Job $genJob -Force

        # Step 2: SCP the generated brief for binary-accurate UTF-8 transfer.
        # ssh cat garbles multi-byte chars (em-dashes, checkmarks) through
        # PowerShell 5.1's ANSI console encoding — scp writes raw bytes directly.
        $tmpBrief = [System.IO.Path]::GetTempFileName()
        & scp "vault-neo:/home/neo/karma-sade/cc-session-brief.md" $tmpBrief 2>$null
        if (-not (Test-Path $tmpBrief) -or (Get-Item $tmpBrief).Length -lt 50) {
            Remove-Item $tmpBrief -ErrorAction SilentlyContinue
            return $null
        }

        $briefText = [System.IO.File]::ReadAllText($tmpBrief, [System.Text.Encoding]::UTF8)
        Remove-Item $tmpBrief -ErrorAction SilentlyContinue
        if ($briefText.Length -lt 50) { return $null }

        return $briefText
    } catch {
        return $null
    }
}

# --- Fallback path: K2 FalkorDB via RESP TCP ---
function Invoke-FalkorQuery {
    param([string]$Query)
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $ar  = $tcp.BeginConnect($K2Host, $K2Port, $null, $null)
        if (-not $ar.AsyncWaitHandle.WaitOne($K2TimeoutMs)) {
            $tcp.Close(); return $null
        }
        $tcp.EndConnect($ar)
        $stream = $tcp.GetStream()
        $stream.ReadTimeout = $K2TimeoutMs

        # Build RESP array: *3\r\n $14\r\nGRAPH.RO_QUERY\r\n $<n>\r\n<graph>\r\n $<m>\r\n<query>\r\n
        # Use GRAPH.RO_QUERY (read-only) -- required for replicas, safe on primary too
        $cmd   = "GRAPH.RO_QUERY"
        $parts = @($cmd, $GraphName, $Query)
        $sb    = New-Object System.Text.StringBuilder
        $sb.Append("*$($parts.Count)`r`n") | Out-Null
        foreach ($p in $parts) {
            $bytes = [System.Text.Encoding]::UTF8.GetByteCount($p)
            $sb.Append("`$$bytes`r`n$p`r`n") | Out-Null
        }
        $buf = [System.Text.Encoding]::UTF8.GetBytes($sb.ToString())
        $stream.Write($buf, 0, $buf.Length)
        $stream.Flush()

        $rbuf = New-Object byte[] 65536
        $n    = $stream.Read($rbuf, 0, $rbuf.Length)
        $resp = [System.Text.Encoding]::UTF8.GetString($rbuf, 0, $n)
        $tcp.Close()
        return $resp
    } catch {
        return $null
    }
}

function Parse-RespStrings {
    # Extract data values from a GRAPH.RO_QUERY RESP response.
    # Skips column headers (passed via $SkipHeaders) and FalkorDB stat lines.
    param(
        [string]$raw,
        [string[]]$SkipHeaders = @()
    )
    if (-not $raw) { return @() }
    $lines  = $raw -split "`r`n"
    $raw_values = [System.Collections.Generic.List[string]]::new()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^\$(\d+)$') {
            $len = [int]$Matches[1]
            if ($i + 1 -lt $lines.Count -and $lines[$i+1].Length -eq $len) {
                $raw_values.Add($lines[$i+1])
                $i++
            }
        } elseif ($lines[$i] -match '^:(-?\d+)$') {
            # Integer type (e.g. count result)
            $raw_values.Add($Matches[1])
        }
    }
    # Filter out column headers and FalkorDB stats lines
    return $raw_values | Where-Object {
        $_ -notin $SkipHeaders -and
        $_ -notmatch '^Cached execution:' -and
        $_ -notmatch '^Query internal execution time:'
    }
}

# --- Collab messages from vault-neo ---
function Get-CollabMessages {
    # Fetch pending/approved CC-directed collab messages from vault-neo via SSH.
    # Shows messages that haven't been read/acked yet.
    try {
        $job = Start-Job {
            param($alias)
            ssh $alias "cat /opt/seed-vault/memory_v1/hub_bridge/data/handoffs/collab.jsonl 2>/dev/null | python3 -c 'import sys,json; msgs=[json.loads(l) for l in sys.stdin if l.strip()]; byid={}; [byid.update({m[\"id\"]:m}) for m in msgs]; cc_msgs=[m for m in byid.values() if m.get(\"to\")==\"cc\"]; [print(json.dumps({\"id\":m[\"id\"],\"status\":m[\"status\"],\"type\":m[\"type\"],\"content\":m[\"content\"][:150]})) for m in cc_msgs]' 2>/dev/null"
        } -ArgumentList $args[0]
        $completed = Wait-Job $job -Timeout 3
        if (-not $completed) {
            Remove-Job $job -Force
            return @()
        }
        $raw = Receive-Job $job
        Remove-Job $job -Force
        $msgs = @()
        foreach ($line in $raw) {
            if ($line) {
                try {
                    $msgs += ($line | ConvertFrom-Json -ErrorAction Stop)
                } catch { }
            }
        }
        return $msgs
    } catch {
        return @()
    }
}

function Get-K2Context {
    # Test connectivity first
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $ar  = $tcp.BeginConnect($K2Host, $K2Port, $null, $null)
        $ok  = $ar.AsyncWaitHandle.WaitOne($K2TimeoutMs)
        if ($ok) { $tcp.EndConnect($ar) }
        $tcp.Close()
        if (-not $ok) { return $null }
    } catch { return $null }

    # Query 1: identity entities
    $idResp = Invoke-FalkorQuery "MATCH (n:Entity) WHERE toLower(n.name) IN ['colby', 'user', 'neo'] RETURN n.name, n.summary"
    $idVals = @(Parse-RespStrings $idResp -SkipHeaders @('n.name', 'n.summary'))

    # Query 2: recent canonical episodes
    $epResp = Invoke-FalkorQuery "MATCH (e:Episodic) WHERE e.lane = 'canonical' RETURN e.content ORDER BY e.created_at DESC LIMIT 5"
    $epVals = @(Parse-RespStrings $epResp -SkipHeaders @('e.content'))

    # Query 3: graph stats (uses integer result :N)
    $stResp = Invoke-FalkorQuery "MATCH (n:Entity) RETURN count(n) AS cnt"
    $stVals = @(Parse-RespStrings $stResp -SkipHeaders @('cnt'))
    $entityCount = if ($stVals.Count -gt 0) { $stVals[0] } else { "0" }

    # Format output matching /raw-context shape
    $parts = [System.Collections.Generic.List[string]]::new()

    # Identity block
    if ($idVals.Count -ge 2) {
        $parts.Add("## User Identity (CRITICAL)")
        for ($i = 0; $i -lt $idVals.Count - 1; $i += 2) {
            $name    = $idVals[$i]
            $summary = $idVals[$i+1]
            if ($name -and $summary) {
                if ($name -ieq "colby") { $parts.Add("REAL NAME: Colby") }
                $parts.Add("- **${name}**: $($summary.Substring(0, [Math]::Min(200, $summary.Length)))")
            }
        }
    }

    # Episodes block
    if ($epVals.Count -gt 0) {
        $parts.Add("")
        $parts.Add("## Recent Memories (canonical)")
        foreach ($ep in $epVals) {
            if ($ep) { $parts.Add("- $($ep.Substring(0, [Math]::Min(200, $ep.Length)))") }
        }
    }

    return @{
        context      = ($parts -join "`n")
        entity_count = $entityCount
        source       = "K2-FALLBACK"
    }
}

# --- Main ---
Write-Host "[Karma] Fetching CC session brief from vault-neo..."

$briefText = Get-VaultNeoContext
if ($briefText) {
    $charCount = $briefText.Length

    # Write primary output: karma-context.md (atomic via tmp, for backward compat)
    Write-Context $briefText
    # Write cc-session-brief.md (primary CC pickup file)
    [System.IO.File]::WriteAllText($BriefOutputFile, $briefText, [System.Text.Encoding]::UTF8)

    Write-Host "[Karma] Context written from vault-neo ($charCount chars) -> cc-session-brief.md"
    exit 0
}

Write-Host "[Karma] vault-neo brief unavailable, trying K2 fallback (${K2Host}:${K2Port})..."
$ctx = Get-K2Context
if ($ctx) {
    $output = "# Karma Graph Context -- $Timestamp [K2-FALLBACK]`n# Note: vault-neo brief unavailable. K2 replica used. Preferences section unavailable.`n`n$($ctx.context)"
    Write-Context $output
    [System.IO.File]::WriteAllText($BriefOutputFile, $output, [System.Text.Encoding]::UTF8)
    Write-Host "[Karma] Context written from K2 fallback ($($ctx.entity_count) entities)"
    exit 0
}

# Both unreachable
$stub = "# Karma Graph Context -- UNAVAILABLE`n# Fetched: $Timestamp`n# Reason: vault-neo SSH timeout (${VaultTimeoutSec}s) + K2 TCP timeout (${K2Host}:${K2Port}, ${K2TimeoutMs}ms)`n# CC: proceed with MEMORY.md context only."
Write-Context $stub
[System.IO.File]::WriteAllText($BriefOutputFile, $stub, [System.Text.Encoding]::UTF8)
Write-Host "[Karma] Both vault-neo and K2 unreachable. UNAVAILABLE stub written."
exit 1