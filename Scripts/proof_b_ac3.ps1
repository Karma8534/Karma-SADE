$tok = [System.IO.File]::ReadAllText('C:\Users\raest\Documents\Karma_SADE\.hub-chat-token').Trim()
$authHdr = "Authorization: Bearer $tok"

$bodyFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($bodyFile, '{"message":"List any PITFALL patterns from your behavioral awareness. Brief.","session_id":"proof-b-ac3-curl"}')

$result = & curl.exe -s -X POST https://hub.arknexus.net/v1/chat `
    -H $authHdr `
    -H "Content-Type: application/json" `
    --data-binary "@$bodyFile" `
    --max-time 30

Remove-Item $bodyFile -Force

$d = $result | ConvertFrom-Json
$resp = $d.assistant_text
Write-Host "=== AC3 response ==="
Write-Host $resp
Write-Host ""
if ($resp -match "PITFALL|pitfall|P00[0-9]|resurrect|Architecture|divergence|K2|watchdog") {
    Write-Host "AC3 PASS: PITFALL patterns visible in Karma response"
} else {
    Write-Host "AC3 WARN: PITFALL content not detected"
}
Write-Host "debug_karma_ctx: $($d.debug_karma_ctx)"
