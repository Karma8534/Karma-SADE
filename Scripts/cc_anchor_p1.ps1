# CC Anchor Agent — P1/Payback (Critic node)
# Runs every 3 hours via Windows Task Scheduler
# Verifies CC identity rails, posts heartbeat or DRIFT ALERT to bus
# This IS a Hyperrail: lays the identity track before CC wakes up

$ErrorActionPreference = "SilentlyContinue"
$LogFile = "C:\Users\raest\Documents\Karma_SADE\Scripts\cc_anchor_p1.log"
$Now = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")

function Write-Log($msg) {
    $line = "[$Now] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

Write-Log "CC Anchor P1 starting..."

# Get hub token via vault-neo SSH
try {
    $Token = (ssh vault-neo "cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt" 2>$null).Trim()
    if (-not $Token) { throw "empty token" }
    Write-Log "Token acquired"
} catch {
    Write-Log "ERROR: could not get hub token: $_"
    exit 1
}

# Read cc_scratchpad from K2
try {
    $Scratchpad = ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'cat /mnt/c/dev/Karma/k2/cache/cc_scratchpad.md'" 2>$null
} catch {
    $Scratchpad = ""
}

# Check required identity markers
$RequiredMarkers = @("Ascendant", "Sovereign: Colby", "ArchonPrime: Codex", "Archon: KCC", "Initiate: Karma", "SADE")
$MissingMarkers = @()
foreach ($marker in $RequiredMarkers) {
    if ($Scratchpad -notmatch [regex]::Escape($marker)) {
        $MissingMarkers += $marker
    }
}

# Check kiki alive via K2
try {
    $KikiCheck = ssh vault-neo "ssh -p 2223 -l karma -o StrictHostKeyChecking=no localhost 'python3 -c ""import json,datetime; s=json.load(open(\"/mnt/c/dev/Karma/k2/cache/kiki_state.json\")); ts=s.get(\"last_cycle_ts\",\"\"); age=int((datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.strptime(ts,\"%Y-%m-%dT%H:%M:%SZ\").replace(tzinfo=datetime.timezone.utc)).total_seconds()) if ts else 9999; print(\"alive\" if age<600 else \"stale:\"+str(age)+\"s\")""'" 2>$null
} catch {
    $KikiCheck = "error"
}

$AllOk = ($MissingMarkers.Count -eq 0) -and ($KikiCheck -eq "alive")

if ($AllOk) {
    $Msg = "[CC ANCHOR P1 $Now] Identity rails INTACT. Baseline #6620 active. Scratchpad verified. Kiki: $KikiCheck. Hyperrails extending. SADE Aegis active."
    $Urgency = "informational"
    $To = "all"
    Write-Log "ANCHOR OK"
} else {
    $Drifts = @()
    if ($MissingMarkers.Count -gt 0) { $Drifts += "SCRATCHPAD missing: $($MissingMarkers -join ', ')" }
    if ($KikiCheck -ne "alive") { $Drifts += "KIKI: $KikiCheck" }
    $Msg = "[CC ANCHOR DRIFT P1 $Now] ALERT: identity rails degraded. $($Drifts -join ' | ') CC must invoke /anchor."
    $Urgency = "blocking"
    $To = "cc"
    Write-Log "ANCHOR DRIFT: $($Drifts -join ' | ')"
}

# Post to bus via vault-neo python3
$PostScript = @"
import json, urllib.request
token = '$Token'
payload = json.dumps({'from':'cc','to':'$To','type':'inform','urgency':'$Urgency','content':'''$Msg'''}).encode()
req = urllib.request.Request('https://hub.arknexus.net/v1/coordination/post', data=payload, headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}, method='POST')
import urllib.error
with urllib.request.urlopen(req, timeout=10) as r:
    d=json.loads(r.read())
    print('ok:', d.get('ok'), 'id:', d.get('id','')[:30])
"@

try {
    $Result = ssh vault-neo "python3 -c `"$PostScript`"" 2>&1
    Write-Log "Bus post: $Result"
} catch {
    Write-Log "ERROR posting to bus: $_"
}

Write-Log "CC Anchor P1 complete."
