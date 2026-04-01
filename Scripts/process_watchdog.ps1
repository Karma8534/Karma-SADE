# process_watchdog.ps1 -Ensures critical Nexus processes stay alive (S155)
# Run via schtasks every 5 minutes or as a persistent loop
# Replaces nssm dependency with pure PowerShell supervision

$processes = @(
    @{
        Name = "cc_server"
        Port = 7891
        Command = "C:\Python314\python.exe"
        Args = "C:\Users\raest\Documents\Karma_SADE\Scripts\cc_server_p1.py"
        WorkDir = "C:\Users\raest\Documents\Karma_SADE"
    },
    @{
        Name = "karma_persistent"
        Port = $null  # No port -check process existence
        Command = "C:\Python314\python.exe"
        Args = "C:\Users\raest\Documents\Karma_SADE\Scripts\karma_persistent.py"
        WorkDir = "C:\Users\raest\Documents\Karma_SADE"
    }
)

$logFile = "C:\Users\raest\Documents\Karma_SADE\tmp\watchdog.log"

function Log($msg) {
    $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    "$ts $msg" | Tee-Object -Append -FilePath $logFile
}

foreach ($proc in $processes) {
    $alive = $false

    if ($proc.Port) {
        # Check by port
        $conn = Get-NetTCPConnection -LocalPort $proc.Port -State Listen -ErrorAction SilentlyContinue
        $alive = $null -ne $conn
    } else {
        # Check by process command line
        $running = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
            $_.CommandLine -like "*$($proc.Args.Split('\')[-1])*"
        }
        $alive = $null -ne $running
    }

    if ($alive) {
        Log "[OK] $($proc.Name) is alive"
    } else {
        Log "[RESTART] $($proc.Name) is DOWN -restarting"
        Start-Process -FilePath $proc.Command -ArgumentList $proc.Args -WorkingDirectory $proc.WorkDir -WindowStyle Hidden
        Start-Sleep 3
        Log "[RESTART] $($proc.Name) restart initiated"
    }
}
