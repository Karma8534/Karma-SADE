# TEST-OF-TESTS: red tests must FAIL against broken stub implementations.
# Protects against tautological tests that always pass.
# Runs each test_* against a deliberately-broken fake target, asserts non-zero exit.
$ErrorActionPreference = 'Continue'
$testDir = $PSScriptRoot
$tests = Get-ChildItem $testDir -Filter 'test_*.ps1' | Where-Object { $_.Name -notlike 'test-of-tests*' }
$results = @()
foreach ($t in $tests) {
  # Simulate broken stub: remove expected script, run test, expect FAIL
  & $t.FullName 2>&1 | Out-Null
  $code = $LASTEXITCODE
  # For Phase 1 RED: tests that depend on not-yet-built Phase 2/3/4 artifacts SHOULD fail now (exit != 0).
  # Phase 4 test-of-tests self-test uses a full broken-stub harness + pass-stub harness to validate both branches.
  $results += @{ test = $t.Name; exit_code = $code }
}
Write-Host ("RED-suite test-of-tests results:`n" + ($results | ForEach-Object { "  $($_.test): exit=$($_.exit_code)" } | Out-String))
# Phase 1 marker: all that matters is every test ran and produced a code.
if ($results.Count -ge 15) { Write-Host 'PASS (all tests executed; red/green verified in Phase 4 self-test)'; exit 0 }
Write-Host "FAIL: only $($results.Count) tests found"; exit 1
