function Send-RoQuery {
    param([string]$Query)
    $tcp = New-Object System.Net.Sockets.TcpClient
    $tcp.Connect('192.168.0.226', 6379)
    $stream = $tcp.GetStream()
    $stream.ReadTimeout = 5000
    $parts = @('GRAPH.RO_QUERY', 'neo_workspace', $Query)
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
}

# Check total nodes (no label filter)
$r1 = Send-RoQuery "MATCH (n) RETURN count(n) AS total"
Write-Host "Total nodes (any label): $r1"

# Check labels present
$r2 = Send-RoQuery "CALL db.labels() YIELD label RETURN label"
Write-Host "Labels: $($r2.Substring(0, [Math]::Min(300, $r2.Length)))"

# Check what vault-neo has for comparison
Write-Host "`n=== Vault-neo for comparison ==="
$vaultResult = & ssh vault-neo "docker exec falkordb redis-cli GRAPH.RO_QUERY neo_workspace 'MATCH (n) RETURN count(n) AS total'"
Write-Host "vault-neo total nodes: $vaultResult"
