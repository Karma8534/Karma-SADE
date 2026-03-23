param(
    [string]$DocsPath = "C:\Users\raest\Documents\Karma_SADE\docs\anthropic-docs",
    [int]$DelayMs = 500,
    [switch]$DryRun
)

$HubUrl = "https://hub.arknexus.net/v1/ingest"
$TokenPath = "/opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt"

Write-Host "Fetching hub token from vault-neo..." -ForegroundColor Cyan
$Token = (ssh vault-neo "cat $TokenPath").Trim()
if (-not $Token) {
    Write-Error "Failed to fetch hub token"
    exit 1
}
Write-Host "Token fetched ($($Token.Length) chars)" -ForegroundColor Green

$Files = Get-ChildItem -Path $DocsPath -Recurse -Filter "*.md" | Sort-Object FullName
Write-Host "Found $($Files.Count) .md files to ingest" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "DRY RUN - no files will be posted" -ForegroundColor Yellow
    $Files | ForEach-Object { Write-Host "  $($_.FullName)" }
    exit 0
}

$Success = 0
$Failures = 0
$i = 0

foreach ($File in $Files) {
    $i++
    $Rel = $File.FullName.Replace($DocsPath, "").TrimStart("\")

    try {
        $Content = Get-Content -Path $File.FullName -Raw -Encoding UTF8
        $Bytes = [System.Text.Encoding]::UTF8.GetBytes($Content)
        $B64 = [Convert]::ToBase64String($Bytes)

        $Section = "anthropic-docs"
        if ($Content -match 'section:\s*(.+)') {
            $Section = $Matches[1].Trim()
        }

        $Hint = [System.IO.Path]::GetFileNameWithoutExtension($File.Name) -replace '[-_]', ' '
        if ($Section -ne "anthropic-docs") {
            $Hint = "$Section $Hint"
        }

        $BodyObj = @{
            file_b64 = $B64
            filename = $File.Name
            hint     = $Hint
        }
        $Body = $BodyObj | ConvertTo-Json -Depth 2 -Compress

        $Headers = @{
            "Authorization" = "Bearer $Token"
            "Content-Type"  = "application/json"
        }

        $null = Invoke-RestMethod -Uri $HubUrl -Method Post -Headers $Headers -Body $Body -TimeoutSec 30
        $Success++

        if (($i % 10 -eq 0) -or ($i -le 5)) {
            Write-Host "[$i/$($Files.Count)] OK: $Rel" -ForegroundColor Green
        }
    }
    catch {
        $Failures++
        $Msg = $_.Exception.Message
        Write-Host "[$i/$($Files.Count)] FAIL: $Rel - $Msg" -ForegroundColor Red
    }

    if ($DelayMs -gt 0) {
        Start-Sleep -Milliseconds $DelayMs
    }
}

Write-Host ""
Write-Host "=== BATCH INGEST COMPLETE ===" -ForegroundColor Cyan
Write-Host "  Total:    $($Files.Count)"
Write-Host "  Success:  $Success"
Write-Host "  Failures: $Failures"
