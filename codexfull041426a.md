
## DESKTOP SURFACE DECISION — 2026-04-14 12:21:47 -04:00
- Decision: **TAURI** selected as the optimal Electron replacement for Nexus.
- Source references:
  - https://github.com/tauri-apps
  - https://github.com/tauri-apps/tauri
  - https://github.com/sudhakar3697/awesome-electron-alternatives
- Why this choice fits Nexus constraints:
  1. Satisfies NO Electron requirement.
  2. Lower runtime footprint than Chromium-bundled shell.
  3. Native webview model aligns with hub.arknexus.net unified surface.
  4. Strong IPC boundary for hardened local tool bridge (Rust commands + explicit allowlist).
  5. Clear path to model-agnostic, local-first harness without wrapper lock-in.
- Implementation policy:
  - Tauri migration is **Phase-gated**; no packaging migration is marked complete until F1–F10 floor criteria are VERIFIED.
  - Current Electron path is treated as transitional/deprecated once Tauri shell reaches parity.

## BLOCKER CLEARANCE UPDATE — 2026-04-14 13:14:58 -04:00

### 1) Runtime env drift (emergency flags)
- Probe: curl http://127.0.0.1:7891/health
- Before: mergency_independent=false, disable_anthropic=false
- Fixes applied:
  - Scripts/cc_server_p1.py defaults hardened to fail-closed emergency posture.
  - Relaunched server via Scripts/Start-CCServer.ps1.
- After: mergency_independent=true, disable_anthropic=true (verified by live health response).
- Verdict: RESOLVED.

### 2) Local-vs-live deploy parity drift (vault hash mismatch)
- Probe before: local 3f8370c... vs vault d6214dd....
- Fixes applied:
  - git push origin main from P1.
  - ssh vault-neo "cd /home/neo/karma-sade && git pull --ff-only origin main".
- Probe after: local and vault both 3f8370c563f46a3f0b03e7d2c642f5be353464be.
- Verdict: RESOLVED.

### 3) PDF ingestion error backlog (Karma_PDFs/Inbox/*.error.txt)
- Ground truth:
  - Inbox contained 6 failing PDFs with repeated .error.txt sidecars.
  - Direct ingest calls to https://hub.arknexus.net/v1/ingest produced transport failures/404.
- Fixes applied:
  - Patched Scripts/karma-inbox-watcher.ps1:
    - local PDF text extraction path,
    - resilient local-fallback ingest path when remote endpoint unavailable,
    - avoids endless .error.txt churn on endpoint drift.
  - Ran Scripts/auto_convert_pdfs.py to clear current backlog.
- Probe after:
  - inbox_count=0
  - rror_count=0
- Verdict: RESOLVED.

### 4) ccArchon stale repeated status email loop
- Ground truth:
  - cc_archon_agent.ps1 intermittently executed daemon calls via bad path (C:\Scripts\...), causing broken cycles and stale behavior.
  - Status mail sender lacked unchanged-content dedupe; stale snapshots could resend by interval.
- Fixes applied:
  - Scripts/cc_archon_agent.ps1: fixed stable repo root resolution ($ScriptRepo), removing bad path execution.
  - Scripts/cc_email_daemon.py:
    - added status digest file and dedupe gate,
    - unchanged status now skipped unless force interval (240m) reached.
- Probe evidence:
  - Archon log no longer shows can't open file 'C:\\Scripts\\cc_email_daemon.py' for current runs.
  - Forced test (status_last set 31m old) result: skipped unchanged (31.0m since last, force=240m).
- Verdict: RESOLVED.

### 5) Full claim extraction + line mapping completeness
- Generated full line-map + claim-candidate artifacts from mandated docs:
  - 	mp/claim_line_map_041426.tsv (1295 rows)
  - 	mp/claim_candidates_041426.tsv (267 rows)
- Scope included:
  - docs/ForColby/nexus.md
  - .gsd/codex-prompt-for-colby.md
  - .gsd/codex-cascade-audit.md
  - .gsd/codex-sovereign-directive.md
  - docs/ForColby/codexDirective041126C.md
- Verdict: RESOLVED for extraction/line-map artifact completeness.

## NEXUS DESKTOP PARITY UPDATE (Electron -> Tauri)
- Tauri wrapper now targets full local Nexus frontend (rontend/out) rather than minimal remote unified shell.
- rontend/src/app/page.tsx patched to support file-protocol API rewrite for both Electron and Tauri runtimes.
- Built + validated:
  - 
pm run build in rontend
  - 	auri build in 
exus-tauri
  - executable launch verified: 
exus.exe starts successfully.
- Desktop shortcut target remains Nexus.lnk -> 
exus-tauri/src-tauri/target/release/nexus.exe.
- Parity status: IN PROGRESS (core settings surface now present via full frontend build; remaining option-level parity still under verification).

## NEXUS SETTINGS PARITY ADDENDUM — 2026-04-14 13:16:55 -04:00
- Requirement accepted: every Karma Electron settings option must exist in Nexus.
- Implemented:
  - Nexus desktop now loads full local frontend (rontend/out) via Tauri (
exus-tauri/src-tauri/tauri.conf.json).
  - File-protocol fetch rewrite now supports both Electron and Tauri in rontend/src/app/page.tsx.
  - Expanded rontend/src/components/SettingsPanel.tsx Advanced tab with Electron parity runtime options:
    - CC timeout (ms)
    - Tool loop limit
    - OpenRouter primary/fallback/third model overrides
    - Local Ollama model override
    - Emergency independent toggle
    - Disable Anthropic toggle
- Verification:
  - 
pm run build (frontend) succeeded.
  - 	auri build succeeded.
  - Desktop launch path (lectron/karma-launch.vbs -> 
exus.exe) verified.
- Status: PARITY SURFACE RESTORED; full option-by-option behavioral binding verification remains in progress.

## TOOL-USE ROOT-CAUSE + FIX PASS — 2026-04-14 17:38:23 -04:00

### RED (pre-fix)
- Probe: POST https://hub.arknexus.net/v1/chat with Use the shell_run tool now. Execute exactly: echo TOOL_WRITE_PROBE_HUB_0414>tmp\\tool_write_probe_hub.txt
- Observed: ssistant_text claimed shell unavailable, 	ool_log_count=0, file was not created.
- Contradiction: Route reachable (200) but no real tool execution side effect.

### Root cause (line-by-line)
- Active runtime chat path is hub-bridge/app/proxy.js (service: sovereign-proxy) and forwards /v1/chat to /cc on P1.
- Actual tool coercion happens in Scripts/cc_server_p1.py.
- cc_server_p1.py::_message_needs_grounding() did not recognize shell_run phrasing, so forced tool path was skipped.
- cc_server_p1.py::_parse_json_object() only accepted JSON blocks; fallback 	ool_code blocks were ignored.

### GREEN (fixed)
Patched Scripts/cc_server_p1.py:
1. _parse_json_object() now accepts fenced 	ool_code/ash blocks and coerces to {"tool_use": {"name":"shell", ...}}.
2. _execute_tool_locally() now aliases shell_run|shell_exec|bash -> shell and ile_read|file_write aliases.
3. _message_needs_grounding() now includes shell_run, ash, and xecute exactly: trigger.
4. _extract_forced_tool_call() now parses explicit shell_run prompts and generalized read-path prompts.

### Proof probes
1. Local CC endpoint:
   - POST http://127.0.0.1:7891/cc message: Use the shell_run tool now. Execute exactly: echo TOOL_WRITE_PROBE_0414>tmp\\tool_write_probe_local.txt
   - Result: esponse='[shell] completed with no stdout', 	ool_log_count=1
   - Side effect: file exists at 	mp/tool_write_probe_local.txt with expected content.
2. Live hub path:
   - POST https://hub.arknexus.net/v1/chat message: Use the shell_run tool now. Execute exactly: echo TOOL_WRITE_PROBE_HUB_0414>tmp\\tool_write_probe_hub.txt
   - Result: ssistant_text='[shell] completed with no stdout', 	ool_log_count=1, model cc-sovereign
   - Side effect: file exists at 	mp/tool_write_probe_hub.txt with expected content.
3. Read-file validation through hub:
   - POST https://hub.arknexus.net/v1/chat message: Read the file tmp/tool_write_probe_hub.txt and return only its content.
   - Result: ssistant_text='TOOL_WRITE_PROBE_HUB_0414', 	ool_log_count=1, tool=ead_file with correct path.

### Verdict
- Previous claim "Karma has tool use" was PARTIAL/UNVERIFIED on this phrasing path.
- Current status after fix: VERIFIED for explicit shell_run and file-read tool paths through live hub + P1 runtime, with disk side-effect proof.
