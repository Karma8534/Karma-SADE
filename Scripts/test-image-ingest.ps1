$token = (Get-Content "$env:USERPROFILE\Documents\Karma_SADE\.hub-chat-token" -Raw).Trim()
$bytes = [System.IO.File]::ReadAllBytes("$env:USERPROFILE\OneDrive\Karma\Inbox\HowIseeKarma.jpg")
$b64   = [Convert]::ToBase64String($bytes)
$body  = @{
    file_b64 = $b64
    filename = "HowIseeKarma.jpg"
    hint     = "how Colby sees Karma - visual representation of our peer relationship"
} | ConvertTo-Json -Depth 2 -Compress

$response = Invoke-RestMethod `
    -Uri "https://hub.arknexus.net/v1/ingest" `
    -Method POST `
    -Headers @{
        Authorization  = "Bearer $token"
        'Content-Type' = 'application/json'
    } `
    -Body $body `
    -TimeoutSec 120

$response | ConvertTo-Json -Depth 5
