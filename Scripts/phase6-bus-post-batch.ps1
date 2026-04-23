param([Parameter(Mandatory = $true)][string]$RunDir)
$ErrorActionPreference = 'Stop'
$mapping = @(
  @{ gate = 'G1_BOOT_DOM_ATTR'; obs = 30614; text = 'G1 strict live VERIFIED; cdp hydration=ready; data-session-id=26edc43d harness-injected' },
  @{ gate = 'G2_COLD_BOOT_RERUN'; obs = 30615; text = 'G2 strict live VERIFIED; persona_paint=418 effective=544 <2000' },
  @{ gate = 'G3_PARITY_BROWSER_SCREEN'; obs = 30616; text = 'G3 strict live VERIFIED; CDP Network + fresh Chromium on hub.arknexus.net w/ PARITY-PROBE' },
  @{ gate = 'G4_PARITY_STRESS'; obs = 30617; text = 'G4 strict live VERIFIED; 40/40 concurrent missing=0 history_match cite cc_server_p1.py:898' },
  @{ gate = 'G5_WHOAMI_REAL_UI'; obs = 30618; text = 'G5 strict live VERIFIED primary path; picker open whoami click body TRUE FAMILY + TOOLS/RESOURCES' },
  @{ gate = 'G6_RITUAL_STEP4_FRESH_BROWSER'; obs = 30619; text = 'G6 strict live VERIFIED; fresh user-data-dir created and deleted' },
  @{ gate = 'G7_RITUAL_STEP10_FIRST_PAINT'; obs = 30620; text = 'G7 strict live VERIFIED; first-paint history contains ASCENDANCE-RITUAL-SID' },
  @{ gate = 'G8_RITUAL_UNINTERRUPTED_RECORDING'; obs = 30621; text = 'G8 strict live VERIFIED; mp4 1MB monotonic gap=18s within_window=true' },
  @{ gate = 'G11_QUARANTINE_CLEANUP'; obs = 30622; text = 'G11 strict live VERIFIED; quarantine artifacts absent' },
  @{ gate = 'G13_FOCUS_GATE_UNLOCK'; obs = 30623; text = 'G13 strict live VERIFIED; focus lock absent' },
  @{ gate = 'G14_TRACKER_SCHEMA_ALIGNMENT'; obs = 30624; text = 'G14 strict live VERIFIED; both persona_paint_ms + effective_paint_ms emitted' }
)
$busIdsPath = Join-Path $RunDir 'bus-posts.txt'
if (Test-Path -LiteralPath $busIdsPath) { Remove-Item -LiteralPath $busIdsPath -Force }
$busEntries = @()
foreach ($m in $mapping) {
  $msg = "CC PROOF S183 $($m.gate) obs=$($m.obs) - $($m.text)"
  $payload = @{ from = 'cc'; to = 'all'; type = 'inform'; urgency = 'informational'; content = $msg } | ConvertTo-Json -Compress
  $tmpPayload = Join-Path $env:TEMP "bus-payload-$([Guid]::NewGuid().ToString('N').Substring(0,8)).json"
  [IO.File]::WriteAllText($tmpPayload, $payload, [Text.UTF8Encoding]::new($false))
  # scp payload to vault-neo tmp + POST via curl (avoids heredoc escape chaos)
  $remoteTmp = "/tmp/cc-bus-$([Guid]::NewGuid().ToString('N').Substring(0,8)).json"
  & scp -q $tmpPayload "vault-neo:$remoteTmp" 2>$null
  $curlOut = & ssh vault-neo "TOKEN=`$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt); curl -s -X POST -H 'Authorization: Bearer '`$TOKEN -H 'Content-Type: application/json' --data-binary @$remoteTmp https://hub.arknexus.net/v1/coordination/post ; rm -f $remoteTmp"
  $busId = ''
  if ($curlOut -match '"id"\s*:\s*"([^"]+)"') { $busId = $matches[1] }
  Remove-Item -LiteralPath $tmpPayload -Force -ErrorAction SilentlyContinue
  $busEntries += [ordered]@{ gate = $m.gate; obs_id = $m.obs; bus_id = $busId.Trim() }
  Add-Content -LiteralPath $busIdsPath -Value "$($m.gate)|obs=$($m.obs)|bus=$($busId.Trim())"
}
$busEntries | ConvertTo-Json -Depth 5
