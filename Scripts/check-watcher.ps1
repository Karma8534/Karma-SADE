#NoProfile
$procs = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'"
$found = $false
foreach ($p in $procs) {
    if ($p.CommandLine -like '*watcher*') {
        Write-Output "RUNNING: PID $($p.ProcessId)"
        Write-Output "CMD: $($p.CommandLine.Substring(0, [Math]::Min(160, $p.CommandLine.Length)))"
        $found = $true
    }
}
if (-not $found) { Write-Output "NOT RUNNING" }

$inbox = (Get-ChildItem 'Karma_PDFs/Inbox' -ErrorAction SilentlyContinue | Measure-Object).Count
$gated = (Get-ChildItem 'Karma_PDFs/Gated' -ErrorAction SilentlyContinue | Measure-Object).Count
$proc  = (Get-ChildItem 'Karma_PDFs/Processing' -ErrorAction SilentlyContinue | Measure-Object).Count
$jammed = (Get-ChildItem 'Karma_PDFs/Processing' -Filter '*.jammed.txt' -ErrorAction SilentlyContinue | Measure-Object).Count
$done  = (Get-ChildItem 'Karma_PDFs/Done' -ErrorAction SilentlyContinue | Measure-Object).Count
Write-Output "Inbox=$inbox Gated=$gated Processing=$proc Jammed=$jammed Done=$done"
