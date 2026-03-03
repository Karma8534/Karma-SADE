@echo off
REM DEPRECATED 2026-03-03: K2 is continuity substrate only. This script is not used.
REM Karma K2 Sync Worker — Windows Task Scheduler wrapper

setlocal
cd /d "\\PAYBACK\Users\raest\OneDrive\Karma"

REM Run Python script
python karma-k2-sync.py >> "\\PAYBACK\Users\raest\OneDrive\Karma\logs\karma-k2.log" 2>&1

endlocal
