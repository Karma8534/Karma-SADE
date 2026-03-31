# Test cc_server --continue mode
$token = (Get-Content "C:\Users\raest\Documents\Karma_SADE\.hub-chat-token" -Raw).Trim()
$body = '{"message": "Reply with exactly: CONTINUE_MODE_VERIFIED"}'
Write-Host "[test] Calling cc_server /cc endpoint (120s timeout)..."
try {
    $resp = Invoke-RestMethod `
        -Uri "http://localhost:7891/cc" `
        -Method POST `
        -Headers @{Authorization="Bearer $token"; "Content-Type"="application/json"} `
        -Body $body `
        -TimeoutSec 120
    Write-Host "[test] exit_code: $($resp.exit_code)"
    Write-Host "[test] ok: $($resp.ok)"
    $preview = $resp.response.Substring(0, [Math]::Min(300, $resp.response.Length))
    Write-Host "[test] response: $preview"
} catch {
    Write-Host "[test] ERROR: $_"
}
