$ErrorActionPreference = "Stop"

$repoRoot = "C:\Users\raest\Documents\Karma_SADE"
$runKeyPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$wscript = Join-Path $env:SystemRoot "System32\wscript.exe"
$hiddenLauncher = Join-Path $repoRoot "Scripts\RunHiddenPowerShell.vbs"

$expectedRun = @{
    KarmaSovereignHarness = "$wscript //B //nologo `"$hiddenLauncher`" `"$repoRoot\Scripts\Start-CCServer.ps1`""
    KarmaChannelsBridge   = "$wscript //B //nologo `"$hiddenLauncher`" `"$repoRoot\Scripts\Start-ChannelsBridge.ps1`""
    KarmaCortexSync       = "$wscript //B //nologo `"$hiddenLauncher`" `"$repoRoot\Scripts\Start-CortexSync.ps1`""
    KarmaRegentWatchdog   = "$wscript //B //nologo `"$hiddenLauncher`" `"$repoRoot\Scripts\Start-RegentWatchdog.ps1`""
    KarmaArchonPrime      = "$wscript //B //nologo `"$hiddenLauncher`" `"$repoRoot\Scripts\Start-ArchonPrime.ps1`""
    KarmaLauncherSentinel = "$wscript //B //nologo `"$hiddenLauncher`" `"$repoRoot\Scripts\Start-LauncherSentinel.ps1`""
    KarmaInboxWatcher     = "$wscript //B //nologo `"$hiddenLauncher`" `"$repoRoot\Scripts\start-karma-watcher.ps1`""
    KarmaFileServer       = "$wscript //B //nologo `"$hiddenLauncher`" `"$repoRoot\Scripts\karma-file-server.ps1`""
    KarmaSessionIndexer   = "$wscript //B //nologo `"$hiddenLauncher`" `"$repoRoot\Scripts\karma_session_indexer.ps1`""
}

$taskNames = @(
    "KarmaSovereignHarness",
    "KarmaChannelsBridge",
    "KarmaCortexSync",
    "KarmaRegentWatchdog",
    "KarmaArchonPrime",
    "KarmaLauncherSentinel",
    "KarmaInboxWatcher",
    "KarmaFileServer",
    "KarmaSessionIndexer"
)

$issues = New-Object System.Collections.Generic.List[string]

function Add-Issue {
    param([string]$Message)
    $issues.Add($Message) | Out-Null
}

function Normalize-Command {
    param([string]$Value)
    if (-not $Value) { return "" }
    return (($Value -replace '"', '') -replace '\s+', ' ').Trim().ToLowerInvariant()
}

function Get-TaskScriptPath {
    param([string]$TaskXml)
    if (-not $TaskXml) { return $null }
    $match = [regex]::Match($TaskXml, '(?i)-File\s+["'']?([^"'']+?\.ps1)\b')
    if ($match.Success) {
        return $match.Groups[1].Value
    }
    return $null
}

function Test-SelfWrappingScript {
    param([string]$ScriptPath)
    if (-not $ScriptPath -or -not (Test-Path $ScriptPath)) {
        return $false
    }
    try {
        $content = Get-Content $ScriptPath -Raw -ErrorAction Stop
        return ($content -match 'Invoke-HiddenRelaunchIfNeeded' -or $content -match 'KARMA_REPO_FORWARDER')
    } catch {
        return $false
    }
}

function Test-FileServerHealth {
    $tokenFile = Join-Path $repoRoot ".local-file-token"
    if (-not (Test-Path $tokenFile)) {
        return $false
    }
    try {
        $token = (Get-Content $tokenFile -Raw -ErrorAction Stop).Trim()
        $headers = @{ Authorization = "Bearer $token" }
        $result = Invoke-RestMethod -UseBasicParsing -Headers $headers -Uri "http://localhost:7771/v1/local-dir?path=tmp" -TimeoutSec 5 -ErrorAction Stop
        return ($result.ok -eq $true)
    } catch {
        return $false
    }
}

foreach ($entry in $expectedRun.GetEnumerator()) {
    $actual = (Get-ItemProperty -Path $runKeyPath -Name $entry.Key -ErrorAction SilentlyContinue).$($entry.Key)
    if (-not $actual) {
        Add-Issue "RUN_MISSING $($entry.Key)"
        continue
    }
    if ((Normalize-Command $actual) -ne (Normalize-Command $entry.Value)) {
        Add-Issue "RUN_MISMATCH $($entry.Key) => $actual"
    }
}

foreach ($taskName in $taskNames) {
    $xml = $null
    try {
        $xml = & schtasks /query /tn $taskName /xml 2>$null
    } catch {
        $xml = $null
    }
    if (-not $xml) {
        continue
    }
    $scriptPath = Get-TaskScriptPath -TaskXml $xml
    $isSelfWrapping = Test-SelfWrappingScript -ScriptPath $scriptPath
    if ($xml -match "worktrees\\" -and -not $isSelfWrapping) {
        Add-Issue "TASK_STALE_WORKTREE $taskName"
    }
    if (($xml -match "<Command>powershell(?:\.exe)?</Command>" -or $xml -match "<Command>pwsh</Command>") -and -not $isSelfWrapping) {
        Add-Issue "TASK_DIRECT_POWERSHELL $taskName"
    }
}

$processChecks = @(
    @{ Name = "KarmaInboxWatcher"; Pattern = "start-karma-watcher\.ps1|karma-inbox-watcher\.ps1"; Min = 1; Max = 1 },
    @{ Name = "KarmaSessionIndexer"; Pattern = "karma_session_indexer\.ps1"; Min = 1; Max = 1 }
)

foreach ($check in $processChecks) {
    $count = @(
        Get-CimInstance Win32_Process |
            Where-Object {
                $_.ProcessId -ne $PID -and
                $_.Name -match '^(pwsh|powershell)\.exe$' -and
                $_.CommandLine -and
                $_.CommandLine -match $check.Pattern
            }
    ).Count
    if ($count -lt $check.Min) {
        Add-Issue "MISSING_PROCESS $($check.Name) count=$count"
    }
    if ($count -gt $check.Max) {
        Add-Issue "DUPLICATE_PROCESS $($check.Name) count=$count"
    }
}

if (-not (Test-FileServerHealth)) {
    Add-Issue "MISSING_ENDPOINT KarmaFileServer"
}

if ($issues.Count -eq 0) {
    "AUDIT_OK"
    exit 0
}

$issues | ForEach-Object { $_ }
exit 1
