$tok = [System.IO.File]::ReadAllText('C:\Users\raest\Documents\Karma_SADE\.hub-chat-token').Trim()
$authHdr = "Authorization: Bearer $tok"

# Write body to temp file to avoid shell quoting issues
$bodyFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($bodyFile, '{"message":"State your rank. One sentence.","session_id":"proof-b-curl2"}')

$result = & curl.exe -s -X POST https://hub.arknexus.net/v1/chat `
    -H $authHdr `
    -H "Content-Type: application/json" `
    --data-binary "@$bodyFile" `
    --max-time 30

Remove-Item $bodyFile -Force
Write-Host "response: $result"
