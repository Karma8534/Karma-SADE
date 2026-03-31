# Start-CortexSync.ps1 — Hidden launcher for sync_k2_to_p1.py
$scriptPath = "C:\Users\raest\Documents\Karma_SADE\Scripts\cortex\sync_k2_to_p1.py"
$logPath = "C:\Users\raest\Documents\Karma_SADE\tmp\cortex_sync.log"
$python = "C:\Python314\python.exe"

& $python $scriptPath *>> $logPath
