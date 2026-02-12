@echo off
title Open WebUI
if "%1"=="" (
    start "" /min cmd /c "\"%~f0\" hidden"
    exit /b
)
"C:\openwebui\venv\Scripts\open-webui.exe" serve
