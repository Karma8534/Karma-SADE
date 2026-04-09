# Nexus 5.6.0 Build Plan
**Date:** 2026-04-07 | **Session:** S162

## Phase 0: Core Executor
- [x] 0-1. gap_map.py (EXISTS at Scripts/gap_map.py)
- [x] 0-2. vesper_eval.py hard gate (EXISTS at Scripts/vesper_eval.py, 7 refs)
- [x] 0-3. vesper_governor.py smoke gate (EXISTS at Scripts/vesper_governor.py, 11 refs)
- [x] 0-4. karma_persistent.py gap_closure (EXISTS at Scripts/karma_persistent.py, 1 ref)

## Phase 1: Persistent Memory — MemPalace Enhanced
- [x] 1-1. 4-Layer Memory Stack — rename buildSystemText sections to L0-L3
  - <verify> grep -c 'L0\|L1\|L2\|L3' hub-bridge/app/server.js >= 4
  - <done> All 4 layers labeled in buildSystemText. Existing behavior unchanged.

- [x] 1-2. Temporal KG — valid_from/valid_to on FalkorDB Entity nodes
  - <verify> FalkorDB Entity with valid_from property exists after batch_ingest change
  - <done> invalidate_entity function in karma-core/server.py + TOOL_DEFINITIONS + ALLOWED_TOOLS

- [x] 1-3. mid-session-promote.sh hook
  - <verify> echo '{"session_id":"t","stop_hook_active":false,"transcript_path":"/dev/null"}' | bash .claude/hooks/mid-session-promote.sh returns block decision
  - <done> Hook executable, returns block at threshold, pass-through on re-entry

- [x] 1-4. pre-compact-flush.sh hook
  - <verify> echo '{"session_id":"t"}' | bash .claude/hooks/pre-compact-flush.sh returns block
  - <done> Hook executable, always blocks

- [x] 1-5. Register hooks in settings.local.json
  - <verify> python -c "import json; d=json.load(open('.claude/settings.local.json')); print('Stop' in d.get('hooks',{}) and 'PreCompact' in d.get('hooks',{}))"
  - <done> Both hooks registered, JSON valid

- [x] 1-6. General Extractor (5-type classifier)
  - <verify> python Scripts/general_extractor.py test → classifies text into 5 types
  - <done> All 5 marker sets ported. 7 test cases pass.

- [x] 1-7. Duplicate Detection
  - <verify> Same content sent to /v1/ambient twice → second returns duplicate warning
  - <done> Dedup check before ledger append, bypass header works

- [ ] 1-8. Deploy Phase 1 to vault-neo
  - <verify> hub-bridge + karma-server healthy after deploy
  - <done> git push → pull → rebuild → health check

## Phase 3: Retrieval + Planning — MemPalace Enhanced
- [x] 3-1. AAAK Compression Dialect
  - <verify> python Scripts/aaak_dialect.py "test text" → compressed output, ratio >= 10x
  - <done> Dialect class with Karma entity codes. compress_for_cortex() wrapper.

- [x] 3-2. Palace Structure vocabulary in karmaCtx
  - <verify> grep -c 'Wing\|Room\|Hall' karma-core/server.py >= 3
  - <done> karmaCtx output uses Wing/Room/Hall vocabulary

- [x] 3-3. Agent Diaries
  - <verify> python Scripts/agent_diary.py write julian "test" && python Scripts/agent_diary.py read julian 1
  - <done> Write + read round-trip. Agent isolation. AAAK format.

- [x] 3-4. Contradiction Detection
  - <verify> grep -c 'valid_to\|EXPIRED' hub-bridge/app/server.js >= 2
  - <done> Expired facts labeled. Current facts unlabeled.

- [ ] 3-5. AAAK in K2 cortex injection — DEFERRED (K2 cortex DOWN, file on K2 only)
  - <verify> K2 karma_regent.py references compress_for_cortex
  - <done> MEMORY.md compressed before injection into 32K window

- [ ] 3-6. Deploy Phase 3 to vault-neo
  - <verify> karma-server + hub-bridge healthy
  - <done> All Phase 3 changes deployed and verified
