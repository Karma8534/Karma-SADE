param([string]$StatePath)
$s = Get-Content -LiteralPath $StatePath -Raw | ConvertFrom-Json
$steps = @($s.steps | Sort-Object -Property @{ Expression = { [int]$_.step } })
Write-Host ('count: ' + $steps.Count)
for ($i = 0; $i -lt $steps.Count; $i++) {
  Write-Host ('idx=' + $i + ' step=' + $steps[$i].step + ' utc=' + $steps[$i].utc)
}
for ($i = 1; $i -lt $steps.Count; $i++) {
  $p = [DateTime]::Parse([string]$steps[$i - 1].utc, [cultureinfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind).Ticks
  $c = [DateTime]::Parse([string]$steps[$i].utc, [cultureinfo]::InvariantCulture, [System.Globalization.DateTimeStyles]::RoundtripKind).Ticks
  if ($c -le $p) {
    Write-Host ('VIOLATION idx ' + $i + ' prev_ticks ' + $p + ' cur_ticks ' + $c)
  }
}
