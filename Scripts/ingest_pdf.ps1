param(
    [string]$FilePath,
    [string]$Hint = ""
)

$token = "cb5617b2ce67470d389dcff1e1fe417aa2626ae699c7d5f831b133cb1f4d450e"
$filename = Split-Path $FilePath -Leaf

$bytes = [System.IO.File]::ReadAllBytes($FilePath)
$b64 = [Convert]::ToBase64String($bytes)
Write-Host "File: $filename | Size: $($bytes.Length) bytes | b64: $($b64.Length) chars"

$body = @{
    file_b64 = $b64
    filename = $filename
    hint = $Hint
} | ConvertTo-Json -Depth 2

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

Write-Host "Sending to /v1/ingest ..."
$response = Invoke-RestMethod -Uri "https://hub.arknexus.net/v1/ingest" -Method POST -Headers $headers -Body $body -TimeoutSec 300
$response | ConvertTo-Json -Depth 5
