@echo off
echo ========================================
echo Starting Karma SADE Unified Backend
echo ========================================
echo.

cd /d C:\Users\raest\Documents\Karma_SADE

echo [1/3] Checking Python...
python --version
echo.

echo [2/3] Starting backend on port 9401...
start /B python Scripts\karma_backend.py

echo.
echo [3/3] Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Karma SADE Backend Started!
echo ========================================
echo.
echo Access the dashboard at:
echo   http://localhost:9401/unified
echo.
echo Backend logs:
echo   %CD%\Logs\karma-backend.log
echo.
echo Press any key to open dashboard in browser...
pause >nul

start http://localhost:9401/unified
