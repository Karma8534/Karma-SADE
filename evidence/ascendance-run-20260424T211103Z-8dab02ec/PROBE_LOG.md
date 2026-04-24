# PROBE_LOG - 20260424T211103Z-8dab02ec

started_utc: 2026-04-24T21:11:03Z
SESSION_ID: 8dab02ec-7282-4da4-9c9f-f1a967e244f1

## Log

2026-04-24T21:11:03Z | DIRECTION | init | obs=pending | bus=pending | run initialized | art_sha=none

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_ENV | 2026-04-24T21:11:42.7878674Z | command=Get-Date -Format o; hostname; whoami; Get-Location; git branch --show-current; git remote -v; git rev-parse HEAD; git rev-parse "@{u}" | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\environment.txt | sha256=B451537D4443D2A9569A76AF4D3EFCE4536CD5D8B524B248F8FC7E6689E1F961

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_GIT_STATUS | 2026-04-24T21:11:43.3891328Z | command=git status --short --untracked-files=all | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\git_status_short_untracked_all.txt | sha256=53B7F32CF7E9D57B589EDF0FF36E8C365EDF5F4C99D428D143C2B45D84CA7B8C

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_IGNORED | 2026-04-24T21:11:43.9558742Z | command=git status --ignored --short --untracked-files=all -- res1 runtime tmp evidence Scripts frontend hub-bridge nexus-tauri | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\ignored_relevant_inventory.txt | sha256=8CE3B72E1ED116DE9CE612FFA227BC7FFC305A07D83408A4BDF5A006C5C420DC

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_PROCESSES | 2026-04-24T21:11:44.7016925Z | command=Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "cc_server|Arknexus|Nexus|watchdog|claude-mem|karma|regent|launcher" } | Select-Object ProcessId,Name,CommandLine | ConvertTo-Json -Depth 4 | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\process_list_relevant.txt | sha256=5398F954FED8C88986AACF1E9BB938457B2C743189024AB8FB1E19A5909DF608

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_VERIFIER_HASHES | 2026-04-24T21:11:46.8533556Z | command=Get-ChildItem Scripts -File -Include *ascendance*.ps1,*harness*.ps1,ascendance-pre-commit.sh,cc_server_p1.py,Start-CCServer.ps1,auto_memory_bridge.py | ForEach-Object { $h=Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName; "$($h.Hash)  $($_.FullName)" } | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\verifier_harness_hashes.txt | sha256=5EDC8FFC5E3B37097C48F119F646DA0F09DAF3F227A9C6D97C28F1A7EC8B34BA

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_DESKTOP_HASHES | 2026-04-24T21:11:47.1930231Z | command=Get-ChildItem -Path nexus-tauri\src-tauri\target\release -Filter *.exe -ErrorAction SilentlyContinue | ForEach-Object { $h=Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName; "$($h.Hash)  $($_.FullName)" } | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\desktop_exe_hashes.txt | sha256=40F2DEE8DEFE6FF215933473628F0DAFD67A203CA4ADC0038B32152976D7BAFF

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_FRONTEND_HASHES | 2026-04-24T21:11:47.8542257Z | command=Get-ChildItem -Path frontend\out -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 200 | ForEach-Object { $h=Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName; "$($h.Hash)  $($_.FullName)" } | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\frontend_build_hashes.txt | sha256=A2EB9AC641F9100E1608C3CF662B523D077AC19722C397C65571E53811BAF750

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_7891_HEALTH | 2026-04-24T21:11:48.2780585Z | command=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:7891/health -TimeoutSec 10 | Select-Object StatusCode,Content | ConvertTo-Json -Depth 5 | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\port_7891_health.txt | sha256=6C360A8AC3BEC3425F831FCFB5F2E7F7A2FD8419C34B51305217C890BBB89128

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_37782_HEALTH | 2026-04-24T21:11:48.6482571Z | command=Invoke-WebRequest -UseBasicParsing http://127.0.0.1:37782/health -TimeoutSec 10 | Select-Object StatusCode,Content | ConvertTo-Json -Depth 5 | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\port_37782_health.txt | sha256=E3586600CC55367E3C26A9A12C8A62AEBBD26239A82DA8BA0ACE0832EA02AF83

- RUN_ID=ascendance-run-20260424T211103Z-8dab02ec | BASE_HUB_HEALTH | 2026-04-24T21:11:49.4493651Z | command=Invoke-WebRequest -UseBasicParsing https://hub.arknexus.net/health -TimeoutSec 20 | Select-Object StatusCode,Content | ConvertTo-Json -Depth 5 | exit=0 | evidence=C:\Users\raest\Documents\Karma_SADE\evidence\ascendance-run-20260424T211103Z-8dab02ec\baseline\hub_health.txt | sha256=13CB3E65F8876B7A88AB55E868E744B542F6FE463C5CAF3731A97F4D7C5B3C32
2026-04-24T17:21:32.0355745-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-8dab02ec-7282-4da4-9c9f-f1a967e244f1-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-24T17:21:45.1926271-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred."
2026-04-24T21:26:39Z | PROOF | G2_COLD_BOOT_RERUN | obs=31372 | bus=coord_1777066000730_hsn1 | G2 live verified | art_sha=none
2026-04-24T21:26:40Z | PROOF | G3_PARITY_BROWSER_SCREEN | obs=31373 | bus=coord_1777066001975_uku0 | G3 live verified | art_sha=none
2026-04-24T21:26:41Z | PROOF | G4_PARITY_STRESS | obs=31374 | bus=coord_1777066003179_sak1 | G4 live verified | art_sha=none
2026-04-24T21:26:42Z | PROOF | G5_WHOAMI_REAL_UI | obs=31375 | bus=coord_1777066004353_ea58 | G5 live verified | art_sha=none
2026-04-24T21:26:44Z | PROOF | G6_RITUAL_STEP4_FRESH_BROWSER | obs=31376 | bus=coord_1777066005657_5uba | G6 live verified | art_sha=none
2026-04-24T21:26:45Z | PROOF | G7_RITUAL_STEP10_FIRST_PAINT | obs=31377 | bus=coord_1777066006918_uua0 | G7 live verified | art_sha=none
2026-04-24T21:26:46Z | PROOF | G8_RITUAL_UNINTERRUPTED_RECORDING | obs=31378 | bus=coord_1777066008102_zxtg | G8 live verified | art_sha=none
2026-04-24T21:26:47Z | PROOF | G9_DUAL_WRITE_DISCIPLINE | obs=31379 | bus=coord_1777066009280_dcg8 | G9 live verified | art_sha=none
2026-04-24T21:26:49Z | PROOF | G10_GIT_AND_MEMORY | obs=31380 | bus=coord_1777066010455_u9mn | G10 pending ship metadata | art_sha=none
2026-04-24T21:26:50Z | PROOF | G11_QUARANTINE_CLEANUP | obs=31381 | bus=coord_1777066011630_z3z4 | G11 live verified | art_sha=none
2026-04-24T21:26:51Z | PROOF | G12_VAULT_PARITY | obs=31382 | bus=coord_1777066012845_xbe4 | G12 pending parity | art_sha=none
2026-04-24T21:26:52Z | PROOF | G13_FOCUS_GATE_UNLOCK | obs=31383 | bus=coord_1777066014001_yhl4 | G13 live verified | art_sha=none
2026-04-24T21:26:53Z | PROOF | G14_TRACKER_SCHEMA_ALIGNMENT | obs=31384 | bus=coord_1777066015229_iiq4 | G14 live verified | art_sha=none
2026-04-24T21:27:02Z | PROOF | G1_BOOT_DOM_ATTR | obs=31385 | bus=coord_1777066023697_7q7x | G1 live verified rerun | art_sha=none
2026-04-24T17:32:21.5044247-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-8dab02ec-7282-4da4-9c9f-f1a967e244f1-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-24T17:32:34.7023794-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred."
2026-04-24T17:36:20.3791345-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-8dab02ec-7282-4da4-9c9f-f1a967e244f1-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-24T17:36:33.5245077-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred."
2026-04-24T17:39:13.8156362-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-8dab02ec-7282-4da4-9c9f-f1a967e244f1-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-24T17:39:27.0093213-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred."
2026-04-24T17:42:27.8545836-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-8dab02ec-7282-4da4-9c9f-f1a967e244f1-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-24T17:42:41.0386889-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred."
