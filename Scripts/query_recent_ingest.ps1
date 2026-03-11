$token = "cb5617b2ce67470d389dcff1e1fe417aa2626ae699c7d5f831b133cb1f4d450e"

$body = @{
    query = "GRAPH.QUERY neo_workspace ""MATCH (e:Episodic) WHERE e.source = 'ingest' OR e.tags CONTAINS 'ingest' RETURN e.content, e.summary, e.created_at ORDER BY e.created_at DESC LIMIT 10"""
} | ConvertTo-Json

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

$response = Invoke-RestMethod -Uri "https://hub.arknexus.net/v1/cypher" -Method POST -Headers $headers -Body $body -TimeoutSec 30
$response | ConvertTo-Json -Depth 10
