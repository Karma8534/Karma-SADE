$ErrorActionPreference = "Continue"
$token = (ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt" 2>$null).Trim()
if (-not $token) { Write-Host "FATAL: no token"; exit 1 }
Write-Host "Token OK"

$resp = Invoke-WebRequest -Uri "https://hub.arknexus.net/v1/coordination/recent?limit=20&status=pending" -Headers @{ Authorization = "Bearer $token" } -UseBasicParsing -TimeoutSec 15
$data = $resp.Content | ConvertFrom-Json
Write-Host ("Pending: " + $data.count)

$target = $data.entries | Where-Object { $_.to -eq "codex" } | Select-Object -First 1
if (-not $target) { Write-Host "No to=codex pending"; exit 0 }
Write-Host ("Found: " + $target.id)

$ScriptDir = "C:\Users\raest\Documents\Karma_SADE\Scripts"
$prompt = "You are ArchonPrime (Codex). Analyze this bus request in 3-5 sentences: " + $target.content
Write-Host "Calling trigger..."
$analysis = & "$ScriptDir\kcc_codex_trigger.ps1" -Prompt $prompt 2>&1
$analysisStr = [string]$analysis
Write-Host ("Analysis length: " + $analysisStr.Length)
Write-Host ("Preview: " + $analysisStr.Substring(0, [Math]::Min(200, $analysisStr.Length)))

if ($analysisStr.Length -gt 10) {
    $safe = ($analysisStr -replace '[^\x20-\x7E\r\n]','').Trim()
    if ($safe.Length -gt 2000) { $safe = $safe.Substring(0,2000) }
    $body = '{"from":"codex","to":"all","type":"inform","urgency":"informational","content":"[ARCHONPRIME] ' + ($safe -replace '"','\"') + '"}'
    $r = Invoke-WebRequest -Uri "https://hub.arknexus.net/v1/coordination/post" -Method POST -Headers @{Authorization="Bearer $token"} -Body $body -ContentType "application/json" -UseBasicParsing -TimeoutSec 15
    $posted = $r.Content | ConvertFrom-Json
    Write-Host ("ARCHONPRIME posted: " + $posted.id)
} else {
    Write-Host "WARN: analysis too short or empty"
}
