# Get-KarmaContext.ps1
# Fetches Karma's live canonical graph context at CC session start.
# Writes to karma-context.md (gitignored) for CC to read.
# Primary: vault-neo /raw-context via SSH. Fallback: K2 FalkorDB at 192.168.0.226:6379.

param(
    [string]$OutputFile    = "$PSScriptRoot\..\..\karma-context.md",
    [string]$TmpFile       = "$PSScriptRoot\..\..\karma-context.md.tmp",
    [string]$VaultNeoAlias = "vault-neo",
    [string]$K2Host        = "192.168.0.226",
    [int]$K2Port           = 6379,
    [string]$GraphName     = "neo_workspace",
    [int]$VaultTimeoutSec  = 3,
    [int]$K2TimeoutMs      = 2000
)

$OutputFile = [System.IO.Path]::GetFullPath($OutputFile)
$TmpFile    = [System.IO.Path]::GetFullPath($TmpFile)
$Timestamp  = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

function Write-Context {
    param([string]$Content)
    [System.IO.File]::WriteAllText($TmpFile, $Content, [System.Text.Encoding]::UTF8)
    Move-Item -Path $TmpFile -Destination $OutputFile -Force
}

# --- Primary path: vault-neo SSH ---
function Get-VaultNeoContext {
    try {
        $job = Start-Job {
            param($alias)
            ssh $alias "curl -s 'http://localhost:8340/raw-context?q=session_start&lane=canonical'"
        } -ArgumentList $VaultNeoAlias
        $completed = Wait-Job $job -Timeout $VaultTimeoutSec
        if (-not $completed) {
            Remove-Job $job -Force
            return $null
        }
        $raw = Receive-Job $job
        Remove-Job $job -Force
        if (-not $raw) { return $null }
        $json = $raw | ConvertFrom-Json -ErrorAction Stop
        if (-not $json.ok -or -not $json.context) { return $null }
        return $json
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

        # Build RESP array: *3\r\n $11\r\nGRAPH.QUERY\r\n $<n>\r\n<graph>\r\n $<m>\r\n<query>\r\n
        $cmd   = "GRAPH.QUERY"
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
    param([string]$raw)
    if (-not $raw) { return @() }
    $lines  = $raw -split "\r\n"
    $values = [System.Collections.Generic.List[string]]::new()
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match '^\$(\d+)$') {
            $len = [int]$Matches[1]
            if ($i + 1 -lt $lines.Count -and $lines[$i+1].Length -eq $len) {
                $values.Add($lines[$i+1])
                $i++
            }
        }
    }
    return $values.ToArray()
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
    $idVals = Parse-RespStrings $idResp

    # Query 2: recent canonical episodes
    $epResp = Invoke-FalkorQuery "MATCH (e:Episodic) WHERE e.lane = 'canonical' RETURN e.content ORDER BY e.created_at DESC LIMIT 5"
    $epVals = Parse-RespStrings $epResp

    # Query 3: graph stats
    $stResp = Invoke-FalkorQuery "MATCH (n:Entity) RETURN count(n) AS cnt"
    $stVals = Parse-RespStrings $stResp
    $entityCount = if ($stVals.Count -gt 0) { $stVals[-1] } else { "?" }

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
Write-Host "[Karma] Fetching graph context..."

$ctx = Get-VaultNeoContext
if ($ctx) {
    $output = "# Karma Graph Context -- $Timestamp (vault-neo)`n# Query: session_start | Lane: canonical`n`n$($ctx.context)"
    Write-Context $output
    Write-Host "[Karma] Context written from vault-neo ($($ctx.context.Length) chars)"
    exit 0
}

Write-Host "[Karma] vault-neo unreachable, trying K2 fallback (${K2Host}:${K2Port})..."
$ctx = Get-K2Context
if ($ctx) {
    $output = "# Karma Graph Context -- $Timestamp [K2-FALLBACK]`n# Note: vault-neo unreachable. K2 replica used. Preferences section unavailable.`n`n$($ctx.context)"
    Write-Context $output
    Write-Host "[Karma] Context written from K2 fallback ($($ctx.entity_count) entities)"
    exit 0
}

# Both unreachable
$stub = "# Karma Graph Context -- UNAVAILABLE`n# Fetched: $Timestamp`n# Reason: vault-neo SSH timeout (${VaultTimeoutSec}s) + K2 TCP timeout (${K2Host}:${K2Port}, ${K2TimeoutMs}ms)`n# CC: proceed with MEMORY.md context only."
Write-Context $stub
Write-Host "[Karma] Both vault-neo and K2 unreachable. UNAVAILABLE stub written."
exit 1
