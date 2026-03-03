@echo off
REM KCC Backup Script - Run as Administrator on K2
REM Creates a full WSL distro snapshot + claude-mem DB backup

set BACKUP_DIR=C:\KCC-Backups
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%

if not exist %BACKUP_DIR% mkdir %BACKUP_DIR%

echo ============================================
echo  KCC Backup - %TIMESTAMP%
echo ============================================

echo.
echo [1/4] Stopping Docker Desktop to prevent WSL conflict...
taskkill /f /im "Docker Desktop.exe" 2>nul
taskkill /f /im com.docker.backend.exe 2>nul
taskkill /f /im com.docker.service 2>nul
timeout /t 3 /nobreak >nul

echo [2/4] Shutting down WSL for clean snapshot...
wsl --shutdown
timeout /t 5 /nobreak >nul

echo [3/4] Exporting WSL distro (this may take a few minutes)...
wsl --export Ubuntu "%BACKUP_DIR%\kcc-wsl-%TIMESTAMP%.tar"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: WSL export failed!
    pause
    exit /b 1
)

echo [4/4] Backing up Windows-side configs...
robocopy "C:\Users\karma\.claude" "%BACKUP_DIR%\claude-config-%TIMESTAMP%" /E /NFL /NDL /NJH /NJS
robocopy "C:\Users\karma\.claude-mem" "%BACKUP_DIR%\claude-mem-%TIMESTAMP%" /E /NFL /NDL /NJH /NJS
copy "C:\Users\karma\.claude.json" "%BACKUP_DIR%\claude.json.%TIMESTAMP%.bak" >nul 2>nul

echo.
echo ============================================
echo  Backup complete!
echo  Location: %BACKUP_DIR%
echo  WSL tar:  kcc-wsl-%TIMESTAMP%.tar
echo ============================================
echo.

REM Clean up old backups - keep last 3
for /f "skip=3 delims=" %%f in ('dir /b /o-d "%BACKUP_DIR%\kcc-wsl-*.tar" 2^>nul') do del "%BACKUP_DIR%\%%f"

echo Old backups cleaned (kept last 3).
echo NOTE: Restart Docker Desktop manually if needed.
pause
