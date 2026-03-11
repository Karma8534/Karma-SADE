$token = (Get-Content 'C:\Users\raest\Documents\Karma_SADE\.hub-chat-token' -Raw).Trim()

function Send-Ingest($filePath, $hint) {
    $name = Split-Path $filePath -Leaf
    $bytes = [System.IO.File]::ReadAllBytes($filePath)
    $b64 = [Convert]::ToBase64String($bytes)
    $body = @{ file_b64 = $b64; filename = $name; hint = $hint } | ConvertTo-Json -Depth 3
    try {
        $r = Invoke-WebRequest -Uri 'https://hub.arknexus.net/v1/ingest' -Method POST `
            -Headers @{ Authorization = "Bearer $token"; 'Content-Type' = 'application/json' } `
            -Body $body -TimeoutSec 120
        Write-Output "$name -> $($r.StatusCode)"
    } catch {
        Write-Output "$name -> ERROR: $($_.Exception.Message)"
    }
}

# LocalAIFortress + PiMonoCoder: send as PDF directly
Send-Ingest 'C:\Users\raest\Documents\Karma_SADE\Karma_PDFs\Inbox\LocalAIFortress.PDF' 'Local RAG stack with Ollama ChromaDB LangChain — sovereign intelligence architecture'
Start-Sleep -Seconds 8

# CCintoanOS: too large as PDF (~49MB b64 > 30MB limit) — extract text first
Write-Output "Extracting CCintoanOS text..."
$txt = & C:\Python314\python.exe -c @'
import pdfplumber, sys
sys.stdout.reconfigure(encoding='utf-8')
with pdfplumber.open(r'C:\Users\raest\Documents\Karma_SADE\Karma_PDFs\Inbox\CCintoanOS.PDF') as pdf:
    for p in pdf.pages:
        t = p.extract_text()
        if t: print(t)
'@
$txtPath = 'C:\Users\raest\Documents\Karma_SADE\Karma_PDFs\Inbox\CCintoanOS.txt'
$txt | Out-File -FilePath $txtPath -Encoding utf8
Write-Output "CCintoanOS.txt written: $((Get-Item $txtPath).Length) bytes"
Start-Sleep -Seconds 2
Send-Ingest $txtPath 'Claude Code as 6-layer OS: CLAUDE.md kernel, hooks, skills, agents, zero-trust permissions, MCP servers — anti-hallucination, confidence levels, PostToolUseFailure logging'
Start-Sleep -Seconds 8

Send-Ingest 'C:\Users\raest\Documents\Karma_SADE\Karma_PDFs\Inbox\PiMonoCoder.PDF' 'Pi-mono minimalist coding agent: 4 tools only (read/write/edit/bash), minimal system prompt, no MCP bloat, self-as-subagent via bash — for Karma coding use'
