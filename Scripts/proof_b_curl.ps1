$tok = [System.IO.File]::ReadAllText('C:\Users\raest\Documents\Karma_SADE\.hub-chat-token').Trim()
Write-Host "token length: $($tok.Length)"
$authHdr = "Authorization: Bearer $tok"
$result = & curl.exe -s -X POST https://hub.arknexus.net/v1/chat `
    -H $authHdr `
    -H "Content-Type: application/json" `
    -d '{"message": "State your rank. One sentence.", "session_id": "proof-b-curl"}' `
    --max-time 30
Write-Host "raw: $result"
