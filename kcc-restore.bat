@echo off
REM KCC Restore Script - Run as Administrator on K2
REM Restores WSL distro from backup

set BACKUP_DIR=C:\KCC-Backups
set WSL_INSTALL_DIR=C:\WSL\Ubuntu

echo ============================================
echo  KCC Restore
echo ============================================
echo.

REM List available backups
echo Available backups:
echo ------------------
dir /b /o-d "%BACKUP_DIR%\kcc-wsl-*.tar" 2>nul
echo.

set /p TARFILE=Enter backup filename (or press Enter for latest):

if "%TARFILE%"=="" (
    for /f %%f in ('dir /b /o-d "%BACKUP_DIR%\kcc-wsl-*.tar" 2^>nul') do (
        set TARFILE=%%f
        goto :found
    )
)
:found

if not exist "%BACKUP_DIR%\%TARFILE%" (
    echo ERROR: File not found: %BACKUP_DIR%\%TARFILE%
    pause
    exit /b 1
)

echo.
echo Using: %TARFILE%
echo.
echo WARNING: This will REPLACE your current Ubuntu WSL distro!
echo Press Ctrl+C to cancel, or
pause

echo.
echo [1/5] Stopping Docker Desktop...
taskkill /f /im "Docker Desktop.exe" 2>nul
taskkill /f /im com.docker.backend.exe 2>nul
timeout /t 3 /nobreak >nul

echo [2/5] Shutting down WSL...
wsl --shutdown
timeout /t 3 /nobreak >nul

echo [3/5] Unregistering current Ubuntu distro...
wsl --unregister Ubuntu

echo [4/5] Importing backup (this may take several minutes)...
if not exist "%WSL_INSTALL_DIR%" mkdir "%WSL_INSTALL_DIR%"
wsl --import Ubuntu "%WSL_INSTALL_DIR%" "%BACKUP_DIR%\%TARFILE%"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WSL import failed!
    pause
    exit /b 1
)

echo [5/5] Setting default user back to karma...
ubuntu config --default-user karma 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo NOTE: If default user is wrong, run manually:
    echo   ubuntu config --default-user karma
)

echo.
echo ============================================
echo  Restore complete!
echo  Test with: wsl -u karma -- ~/k2_boot.sh
echo  Or double-click the KCC desktop shortcut
echo ============================================
pause
