param()
$BaseDir   = 'C:\Users\raest\Documents\Karma_SADE'
$TokenFile = "$BaseDir\.hub-chat-token"
$Script    = "$BaseDir\Scripts\karma-inbox-watcher.ps1"

$argList = @(
    '-WindowStyle', 'Hidden', '-NonInteractive',
    '-File', $Script,
    '-InboxPath', "$BaseDir\Karma_PDFs\Inbox",
    '-GatedPath', "$BaseDir\Karma_PDFs\Gated",
    '-ProcessingPath', "$BaseDir\Karma_PDFs\Processing",
    '-DonePath', "$BaseDir\Karma_PDFs\Done",
    '-TokenFile', $TokenFile
)

Write-Output 'Starting karma-inbox-watcher as background process...'
$proc = Start-Process pwsh -ArgumentList $argList -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 4
if ($proc.HasExited) {
    Write-Output "ERROR: Process exited (code $($proc.ExitCode))"
} else {
    Write-Output "Running OK - PID $($proc.Id)"
}
