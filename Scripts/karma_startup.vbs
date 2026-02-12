' Karma SADE — Startup Launcher
' Place this in the Windows Startup folder (replaces start_openwebui.vbs + start_cockpit.vbs)
' Startup folder: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
'
' This VBS wrapper runs the PowerShell orchestrator hidden (no console flash).
' The orchestrator handles dependency ordering: Ollama → Open WebUI → Cockpit.

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File ""C:\Users\raest\Documents\Karma_SADE\Scripts\karma_startup.ps1""", 0, False
