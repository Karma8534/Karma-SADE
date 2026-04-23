# P-FU6 Nexus V3.0 merge: Port Isolation Firewall
# Blocks LAN exposure of Ollama/FalkorDB/cortex/harness ports; only Tailscale subnet 100.0.0.0/8 allowed.
# Idempotent. Run on K2 (as Admin) + P1 (as Admin). vault-neo firewall via iptables (see bottom of this file).

param([switch]$Uninstall, [switch]$WhatIf)

$ErrorActionPreference = 'Stop'
$rules = @(
  @{ Name = 'NexusV3-Block-Ollama-11434-LAN';      Port = 11434; Proto = 'TCP' },
  @{ Name = 'NexusV3-Block-FalkorDB-6379-LAN';     Port = 6379;  Proto = 'TCP' },
  @{ Name = 'NexusV3-Block-K2Cortex-7892-LAN';     Port = 7892;  Proto = 'TCP' },
  @{ Name = 'NexusV3-Block-Harness-7891-LAN';      Port = 7891;  Proto = 'TCP' },
  @{ Name = 'NexusV3-Block-Aria-7890-LAN';         Port = 7890;  Proto = 'TCP' }
)
# Tailscale subnet allowed; everything else on these ports BLOCKED inbound.
$tailscaleSubnet = '100.0.0.0/8'
$localSubnet = '127.0.0.0/8'

if ($Uninstall) {
  foreach ($r in $rules) {
    Remove-NetFirewallRule -DisplayName $r.Name -ErrorAction SilentlyContinue
    Write-Host "removed: $($r.Name)"
  }
  exit 0
}

foreach ($r in $rules) {
  if ($WhatIf) {
    Write-Host "WhatIf: would create inbound BLOCK rule $($r.Name) port $($r.Port)/$($r.Proto) RemoteAddress=Any except ($tailscaleSubnet, $localSubnet)"
    continue
  }
  # Remove if exists to ensure idempotent re-apply
  Remove-NetFirewallRule -DisplayName $r.Name -ErrorAction SilentlyContinue
  # Allow Tailscale + localhost explicitly
  New-NetFirewallRule `
    -DisplayName ($r.Name + '-ALLOW-TAILSCALE') `
    -Direction Inbound `
    -Action Allow `
    -Protocol $r.Proto `
    -LocalPort $r.Port `
    -RemoteAddress $tailscaleSubnet, $localSubnet `
    -Profile Any | Out-Null
  # Block everything else on that port
  New-NetFirewallRule `
    -DisplayName $r.Name `
    -Direction Inbound `
    -Action Block `
    -Protocol $r.Proto `
    -LocalPort $r.Port `
    -RemoteAddress Any `
    -Profile Any | Out-Null
  Write-Host "installed: $($r.Name) (Tailscale + localhost ALLOW; all else BLOCK)"
}

# --- vault-neo (Linux droplet) reference iptables rules ---
# Run these manually on vault-neo if not already in place:
<#
# Allow Tailscale ingress on cortex/harness ports; block public by default
sudo iptables -A INPUT -i tailscale0 -p tcp --dport 7890 -j ACCEPT
sudo iptables -A INPUT -i tailscale0 -p tcp --dport 7891 -j ACCEPT
sudo iptables -A INPUT -i tailscale0 -p tcp --dport 7892 -j ACCEPT
sudo iptables -A INPUT -i tailscale0 -p tcp --dport 6379 -j ACCEPT
sudo iptables -A INPUT -i tailscale0 -p tcp --dport 11434 -j ACCEPT
# Drop public on same ports (Caddy on 443 unaffected)
sudo iptables -A INPUT -p tcp --dport 7890:7892 -j DROP
sudo iptables -A INPUT -p tcp --dport 6379 -j DROP
sudo iptables -A INPUT -p tcp --dport 11434 -j DROP
#>
