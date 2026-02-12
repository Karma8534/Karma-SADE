' Karma SADE - Hidden Launcher
' Starts the backend silently in the background without showing terminal window

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the Karma SADE directory
karmaDir = "C:\Users\raest\Documents\Karma_SADE"

' Start the backend hidden (0 = hidden window)
objShell.Run "cmd /c cd /d " & karmaDir & " && python Scripts\karma_backend.py > Logs\karma-startup.log 2>&1", 0, False

' Wait 5 seconds for backend to start
WScript.Sleep 5000

' Open browser to dashboard
objShell.Run "http://localhost:9401/unified", 1, False

' Show balloon notification (if supported)
Set objNotify = CreateObject("WScript.Shell")
objNotify.Popup "Karma SADE backend started successfully!" & vbCrLf & vbCrLf & "Dashboard: http://localhost:9401/unified", 3, "Karma SADE", 64
