@echo off
REM Karma K2 Sync Worker — Windows Task Scheduler wrapper

setlocal
cd /d "\\PAYBACK\Users\raest\OneDrive\Karma"

REM Run Python script
python karma-k2-sync.py >> "\\PAYBACK\Users\raest\OneDrive\Karma\logs\karma-k2.log" 2>&1

endlocal
