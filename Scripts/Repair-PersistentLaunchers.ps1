$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\raest\Documents\Karma_SADE"
$wscript = Join-Path $env:SystemRoot "System32\wscript.exe"
$hiddenLauncher = Join-Path $repoRoot "Scripts\RunHiddenPowerShell.vbs"
$localFileToken = Join-Path $repoRoot ".local-file-token"

$targets = @(
    @{
        Name = "KarmaInboxWatcher"
        Pattern = "start-karma-watcher\.ps1|karma-inbox-watcher\.ps1"
        Script = "$repoRoot\Scripts\start-karma-watcher.ps1"
    },
    @{
        Name = "KarmaSessionIndexer"
        Pattern = "karma_session_indexer\.ps1"
        Script = "$repoRoot\Scripts\karma_session_indexer.ps1"
    },
    @{
        Name = "KarmaFileServer"
        Pattern = "karma-file-server\.ps1"
        Script = "$repoRoot\Scripts\karma-file-server.ps1"
    }
)

foreach ($target in $targets) {
    $procs = @(
        Get-CimInstance Win32_Process |
            Where-Object {
                $_.Name -match '^(pwsh|powershell)\.exe$' -and
                $_.CommandLine -and
                $_.CommandLine -match $target.Pattern
            }
    )

    foreach ($proc in $procs) {
        try {
            Stop-Process -Id $proc.ProcessId -Force -ErrorAction Stop
        } catch {}
    }

    Start-Sleep -Seconds 1
    Start-Process -FilePath $wscript -ArgumentList "//B", "//nologo", $hiddenLauncher, $target.Script | Out-Null
    Start-Sleep -Seconds 2

    if ($target.Name -eq "KarmaFileServer") {
        $healthy = $false
        if (Test-Path $localFileToken) {
            try {
                $token = (Get-Content $localFileToken -Raw -ErrorAction Stop).Trim()
                $headers = @{ Authorization = "Bearer $token" }
                $result = Invoke-RestMethod -UseBasicParsing -Headers $headers -Uri "http://localhost:7771/v1/local-dir?path=tmp" -TimeoutSec 5 -ErrorAction Stop
                $healthy = ($result.ok -eq $true)
            } catch {}
        }
        "{0}={1}" -f $target.Name, $(if ($healthy) { 1 } else { 0 })
        continue
    }

    $count = @(
        Get-CimInstance Win32_Process |
            Where-Object {
                $_.Name -match '^(pwsh|powershell)\.exe$' -and
                $_.CommandLine -and
                $_.CommandLine -match $target.Pattern
            }
    ).Count

    "{0}={1}" -f $target.Name, $count
}
