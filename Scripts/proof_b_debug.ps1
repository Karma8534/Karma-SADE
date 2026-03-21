$token = (Get-Content 'C:\Users\raest\Documents\Karma_SADE\.hub-chat-token' -Raw).Trim()
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }
$body = '{"message": "Hi. State your rank.", "session_id": "proof-b-debug2"}'
$r = Invoke-WebRequest -Uri "https://hub.arknexus.net/v1/chat" -Method POST -Headers $headers -Body $body -TimeoutSec 30
$d = $r.Content | ConvertFrom-Json
Write-Host "response: '$($d.response)'"
Write-Host "debug_stop_reason: $($d.debug_stop_reason)"
Write-Host "debug_max_output_tokens_used: $($d.debug_max_output_tokens_used)"
Write-Host "model: $($d.model)"
Write-Host "error: $($d.error)"
Write-Host "full json snippet:"
$r.Content.Substring(0, [Math]::Min(500, $r.Content.Length))
