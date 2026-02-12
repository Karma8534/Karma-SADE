@echo off
title Karma Cockpit
if "%1"=="" (
    start "" /min cmd /c "\"%~f0\" hidden"
    exit /b
)

:: Check if port 9400 is already in use
netstat -ano | findstr :9400 >nul 2>&1
if %errorlevel%==0 (
    exit /b 1
)

python "%~dp0karma_cockpit_service.py"
