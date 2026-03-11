$token = (Get-Content 'C:\Users\raest\Documents\Karma_SADE\.hub-chat-token' -Raw).Trim()
Write-Output "Token length: $($token.Length)"
Write-Output "Token prefix: $($token.Substring(0, [Math]::Min(8,$token.Length)))..."

$body = '{"file_b64":"aGVsbG8=","filename":"test.txt","hint":"test"}'
try {
    $r = Invoke-WebRequest -Uri 'https://hub.arknexus.net/v1/ingest' -Method POST `
        -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } `
        -Body $body -TimeoutSec 30
    Write-Output "Status: $($r.StatusCode)"
    Write-Output "Body: $($r.Content)"
} catch {
    $resp = $_.Exception.Response
    if ($resp) {
        $stream = $resp.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        Write-Output "HTTP $([int]$resp.StatusCode) error body: $($reader.ReadToEnd())"
    } else {
        Write-Output "No response: $($_.Exception.Message)"
    }
}
