#!/usr/bin/env pwsh
# PROOF-B: AC1 + AC3 regression smoke test
$TokenFile = "C:\Users\raest\Documents\Karma_SADE\.hub-chat-token"
$token = (Get-Content $TokenFile -Raw).Trim()
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

# AC1: Rank check
$body1 = '{"message": "State your rank in the Family hierarchy. One sentence.", "session_id": "proof-b-ac1-smoke"}'
try {
    $r1 = Invoke-RestMethod -Uri "https://hub.arknexus.net/v1/chat" -Method POST -Headers $headers -Body $body1 -TimeoutSec 30
    $resp1 = $r1.response
    Write-Host "=== AC1 response ==="
    Write-Host $resp1
    if ($resp1 -match "initiate|Initiate") {
        Write-Host "AC1 PASS: Karma identifies as Initiate"
    } else {
        Write-Host "AC1 WARN: 'Initiate' not in response"
    }
} catch {
    Write-Host "AC1 ERROR: $_"
}

Start-Sleep -Seconds 3

# AC3: PITFALL pattern visible in karmaCtx
$body3 = '{"message": "List any PITFALL patterns you know about from your behavioral awareness. Brief list.", "session_id": "proof-b-ac3-smoke"}'
try {
    $r3 = Invoke-RestMethod -Uri "https://hub.arknexus.net/v1/chat" -Method POST -Headers $headers -Body $body3 -TimeoutSec 30
    $resp3 = $r3.response
    Write-Host "`n=== AC3 response ==="
    Write-Host $resp3
    if ($resp3 -match "PITFALL|pitfall|P00[0-9]|Architecture|divergence|resurrect") {
        Write-Host "AC3 PASS: PITFALL patterns visible in response"
    } else {
        Write-Host "AC3 WARN: No PITFALL content detected in response"
    }
} catch {
    Write-Host "AC3 ERROR: $_"
}
