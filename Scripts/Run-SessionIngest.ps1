# Run-SessionIngest.ps1 — Nightly CC session extraction + review
# Registered as Windows Scheduled Task "KarmaSessionIngest" on P1
# Runs at 2:30 AM daily
# Uses K2 Ollama (qwen3:8b) at 100.75.109.92:11434 for review quality

$ErrorActionPreference = "Continue"
$RepoDir = "C:\Users\raest\Documents\Karma_SADE"
$LogFile = "$RepoDir\Logs\session_ingest.log"

$ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
Add-Content $LogFile "=== SESSION INGEST RUN $ts ==="

# Step 1: Extract new CC sessions from JSONL files
Write-Host "Step 1: Extracting CC sessions..."
Add-Content $LogFile "Step 1: extract_cc_sessions.py"

$env:PYTHONIOENCODING = "utf-8"
$result = & python3 "$RepoDir\Scripts\extract_cc_sessions.py" 2>&1
Add-Content $LogFile $result
Write-Host $result

# Step 2: Review new sessions with K2 Ollama (qwen3:8b)
Write-Host "Step 2: Reviewing sessions..."
Add-Content $LogFile "Step 2: session_review.py --source json (OLLAMA_URL=http://100.75.109.92:11434)"

$env:OLLAMA_URL = "http://100.75.109.92:11434"
$env:REVIEW_MODEL = "qwen3:8b"
$result2 = & python3 "$RepoDir\Scripts\session_review.py" --source json 2>&1
Add-Content $LogFile $result2
Write-Host $result2

# Step 3: Emit observation list for CC to process next session
Write-Host "Step 3: Emitting observations..."
Add-Content $LogFile "Step 3: session_obs_writer.py"

$result3 = & python3 "$RepoDir\Scripts\session_obs_writer.py" 2>&1
$ObsFile = "$RepoDir\Logs\pending_observations.txt"
$result3 | Set-Content $ObsFile -Encoding UTF8
Add-Content $LogFile "Observations written to: $ObsFile"

$ts2 = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
Add-Content $LogFile "=== COMPLETE $ts2 ==="
Write-Host "Session ingest complete. Observations at: $ObsFile"
