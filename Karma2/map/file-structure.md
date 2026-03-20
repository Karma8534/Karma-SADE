# File Structure — Ground Truth (2026-03-20)

## K2: /mnt/c/dev/Karma/k2/aria/ — Agent Code
### Core Agent Files
- karma_regent.py — main Regent agent loop (karma-regent.service entry point)
- aria.py / aria_server.py — Aria Flask service (aria.service entry point, port 7890)
- regent_inference.py — cascade inference: K2→P1→z.ai→Groq→OpenRouter→Claude
- regent_triage.py — message routing + sovereignty detection
- regent_pipeline.py — pipeline orchestration
- vesper_watchdog.py — evolution log scanner, candidate extraction
- vesper_eval.py — grades recent turns, produces quality_metrics
- vesper_governor.py — applies promotions to spine, FalkorDB write
- vesper_researcher.py — autonomous research loop (90min cadence)
- regent_governance.py — governance rules
- regent_guardrails.py — safety boundaries
- llm_client.py — multi-model LLM abstraction
- k2_tools.py — K2-specific tool implementations
- karma_kiki.py — Kiki governance agent (in-process)

### Key Docs
- CLAUDE.md — K2-specific Claude Code instructions
- AGENTS.md — agent architecture docs

### Playwright / Browser (EXISTING, dormant)
- .playwright-cli/ — logs from 2026-03-09 (last known browser use)
- Browser available: /snap/bin/chromium, /usr/bin/chromium-browser

## K2: /mnt/c/dev/Karma/k2/cache/ — Live State
- vesper_identity_spine.json — identity + evolution spine (v82)
- vesper_brief.md — auto-generated session brief (updated every cycle)
- vesper_governor_audit.jsonl — governor run history
- regent_candidates/ — candidate pattern files (all cascade_performance currently)
- regent_control/
  - session_state.json — turn state, history, quality metrics
  - vesper_pipeline_status.json — pipeline health
  - cadence_mode.json — timing config
  - candidate_fingerprints.json — dedup registry
  - file_ownership.json / file_ownership_hashes.json — governance protection

## K2: /mnt/c/dev/Karma/k2/Config/
- governance_boundary_v1.json
- critical_paths.json

## K2: /mnt/c/dev/Karma/k2/scripts/
- karma_kiki.py / karma_kiki_v4.py / karma_kiki_v5.py — Kiki versions

## vault-neo: /home/neo/karma-sade/ — Repo Root
### Active Architecture
- hub-bridge/app/server.js — hub-bridge source (sync → /opt/seed-vault/.../hub_bridge/)
- karma-core/ — karma-server source (sync → /opt/seed-vault/.../karma-core/)
- Memory/ — identity files, system prompt, session handoff
- Vesper/ — karma_regent.py, vesper_watchdog.py, regent_triage.py (copy on vault-neo)
- k2/ — setup-k2-cache.sh, sync-from-vault.sh
- .gsd/ — STATE.md, ROADMAP.md, PLAN.md
- MEMORY.md — mutable spine (CC updates this)
- cc-session-brief.md — CC session brief (auto-generated every 30min)
- cc_scratchpad.md — CC persistent notes

### Legacy / Noise (do not modify)
- ~80 SESSION-*.md, PHASE-*.md, HANDOFF-*.md files from early sessions
- Various *.py patch scripts from debugging sessions

## vault-neo: Build Contexts (NOT the git repo)
- /opt/seed-vault/memory_v1/hub_bridge/app/server.js — hub-bridge BUILD SOURCE
- /opt/seed-vault/memory_v1/karma-core/ — karma-server BUILD SOURCE
- CRITICAL: git repo and build context are separate. Always cp after git pull.

## P1 (PAYBACK): C:\Users\raest\Documents\Karma_SADE\
- Scripts/ — PowerShell scripts, resurrection, vesper patch
- Karma2/ — this map (you are here)
- .claude/ — skills, hooks, settings
- .gsd/ — GSD workflow files
