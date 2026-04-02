$topics = @(
    "persistent AI agent frameworks 2026 self-improving",
    "local LLM optimization RTX 4070 8GB Ollama vLLM",
    "AI agent self-editing code modification autonomous",
    "multi-agent coordination bus pattern decentralized",
    "voice AI local TTS STT realtime WebRTC",
    "AI memory architecture long-running agents persistence",
    "Electron AI desktop app framework local inference",
    "AI agent browser automation autonomous web navigation"
)
$logFile = "C:\Users\raest\Documents\Karma_SADE\tmp\codex_research.log"
$idx = 0
while ($true) {
    $topic = $topics[$idx % $topics.Count]
    $ts = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"
    "$ts Researching: $topic" | Out-File -Append -FilePath $logFile
    try {
        $result = codex exec --full-auto --json --ephemeral "Search the internet for: $topic. Find 3 projects or techniques. For each: name, URL, description." 2>&1
        "$ts Done" | Out-File -Append -FilePath $logFile
    } catch {
        "$ts Error: $_" | Out-File -Append -FilePath $logFile
    }
    $idx++
    Start-Sleep 600
}
