# PROBE_LOG - 20260422T151430Z-91cf359a

started_utc: 2026-04-22T15:14:30Z
SESSION_ID: 91cf359a-324d-4857-b97e-0caa800b58a5

## Log

2026-04-22T15:14:30Z | DIRECTION | init | obs=pending | bus=pending | run initialized | art_sha=none


## Forward-pass attempt_n=2 events (S182 debug-loop)

2026-04-22T15:50:00Z | DECISION | G1_BOOT_DOM_ATTR | obs=30294 | bus=coord_1776872875970_jkst | phase1 rebuild + remote-allow-origins + tab-filter + CDP localStorage fallback | art_sha=eac25998
2026-04-22T15:50:00Z | PROOF | G1_BOOT_DOM_ATTR | obs=30294 | bus=coord_1776872875970_jkst | data-hydration-state=ready + data-session-id=b3763079 (canonical); harness SID in trace artifacts | art_sha=eac25998+c4e5e107
2026-04-22T15:50:00Z | DECISION | G2_COLD_BOOT_RERUN | obs=30294 | bus=coord_1776872875970_jkst | auth-decouple hydrate + localStorage __bootMetrics key | art_sha=346f8f91
2026-04-22T15:50:00Z | PROOF | G2_COLD_BOOT_RERUN | obs=30294 | bus=coord_1776872875970_jkst | persona_paint=318ms + effective=792ms < 2000 budget; bootMetrics.hydration_state=ready; source=cdp_localstorage | art_sha=346f8f91
2026-04-22T15:50:00Z | DECISION | G14_TRACKER_SCHEMA_ALIGNMENT | obs=30294 | bus=coord_1776872875970_jkst | timing.json emits persona_paint_ms + effective_paint_ms; formula: effective=window_visible+persona_paint | art_sha=346f8f91
2026-04-22T15:50:00Z | PROOF | G14_TRACKER_SCHEMA_ALIGNMENT | obs=30294 | bus=coord_1776872875970_jkst | phase1-cold-boot-harness.ps1:193-195 computes both fields; 474+318=792 | art_sha=346f8f91
2026-04-23T09:42:09.0138638-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-91cf359a-324d-4857-b97e-0caa800b58a5-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-23T09:42:22.2141746-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (The WebSocket is in an invalid state ('Aborted') for this operation. Valid states are: 'Open, CloseReceived')"
2026-04-23T09:44:05.6902775-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-91cf359a-324d-4857-b97e-0caa800b58a5-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-23T09:44:25.8494788-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (The WebSocket is in an invalid state ('Aborted') for this operation. Valid states are: 'Open, CloseReceived, CloseSent')"
2026-04-23T09:45:29.0843956-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-91cf359a-324d-4857-b97e-0caa800b58a5-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-23T09:45:49.2529130-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (The WebSocket is in an invalid state ('Aborted') for this operation. Valid states are: 'Open, CloseReceived, CloseSent')"
2026-04-23T09:47:38.9442411-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-91cf359a-324d-4857-b97e-0caa800b58a5-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-23T09:47:59.0802706-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (The WebSocket is in an invalid state ('Aborted') for this operation. Valid states are: 'Open, CloseReceived, CloseSent')"
2026-04-23T09:49:38.9688506-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-91cf359a-324d-4857-b97e-0caa800b58a5-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-23T09:49:59.1216956-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (The WebSocket is in an invalid state ('Aborted') for this operation. Valid states are: 'Open, CloseReceived, CloseSent')"
2026-04-23T09:50:23.6608055-04:00 | PITFALL | G5 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (A task was canceled.)"
2026-04-23T09:52:41.8921135-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-91cf359a-324d-4857-b97e-0caa800b58a5-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-23T09:53:02.0449873-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (The WebSocket is in an invalid state ('Aborted') for this operation. Valid states are: 'Open, CloseReceived, CloseSent')"
2026-04-23T09:53:26.9326765-04:00 | PITFALL | G5 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (A task was canceled.)"
2026-04-23T09:54:35.0738823-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-91cf359a-324d-4857-b97e-0caa800b58a5-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-23T09:54:55.1915566-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (The WebSocket is in an invalid state ('Aborted') for this operation. Valid states are: 'Open, CloseReceived, CloseSent')"
2026-04-23T09:55:19.9445488-04:00 | PITFALL | G5 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (A task was canceled.)"
2026-04-23T09:56:04.5759342-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-91cf359a-324d-4857-b97e-0caa800b58a5-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-23T09:56:24.7740858-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (The WebSocket is in an invalid state ('Aborted') for this operation. Valid states are: 'Open, CloseReceived, CloseSent')"
2026-04-23T09:56:49.6743777-04:00 | PITFALL | G5 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (A task was canceled.)"
2026-04-23T09:57:50.8232266-04:00 | DECISION | G6 | obs=none | bus=none | fresh_browser_cmdline=C:\Program Files\Google\Chrome\Application\chrome.exe --remote-debugging-port=9333 --user-data-dir=C:\Users\raest\AppData\Local\Temp\ark-91cf359a-324d-4857-b97e-0caa800b58a5-browser --no-first-run --no-default-browser-check https://hub.arknexus.net | art_sha=none
2026-04-23T09:58:10.9475323-04:00 | PITFALL | G3 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (The WebSocket is in an invalid state ('Aborted') for this operation. Valid states are: 'Open, CloseReceived, CloseSent')"
2026-04-23T09:58:36.0712381-04:00 | PITFALL | G5 | cdp_error=Exception calling "Wait" with "0" argument(s): "One or more errors occurred. (A task was canceled.)"
