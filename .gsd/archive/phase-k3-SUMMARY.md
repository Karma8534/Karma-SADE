# K-3: Echo Integration — Ambient Observer Summary
**Completed:** 2026-03-22 (Sessions 120-121)
**Author:** CC (Ascendant)

## What Was Built
Full ambient observation pipeline: consciousness loop → coordination bus signals → Ollama insight → vesper evolution pipeline → spine promotion → proactive outreach to Colby.

### Components
1. **`Scripts/ambient_observer.py`** (new) — K2 module polling coordination bus via `https://hub.arknexus.net`, extracting signal batch (senders/top_words/count), calling `nemotron-mini:optimized` via `host.docker.internal:11434`, writing to `regent_evolution.jsonl`, 6h dedup.
2. **`Scripts/aria_consciousness.py`** — Phase 7 AMBIENT block after Echo step; catches exceptions cleanly.
3. **`Scripts/vesper_watchdog.py`** — `extract_ambient_candidates()` function emitting `cand_ambient_*.json` candidates (required `cand_` prefix for `pipeline.list_candidate_files()` to pick up).
4. **`Scripts/vesper_eval.py`** — `"ambient_observation"` added to `AWARENESS_TYPES` (PITFALL fast-path); bypasses `task_completion` gate (not applicable to observational candidates). confidence=0.82 passes threshold.
5. **`Scripts/karma_regent.py`** — `_last_ambient_count` global + `should_fire` logic in `_proactive_outreach()`; reads insight from `proposed_change.patch.ambient_insight` (spine stores it there, not in `excerpt`); urgency=`"informational"` (hub rejects `"low"`).

## Pitfalls Hit
- **P-K3-A**: `COORDINATION_BUS_URL` must be `https://hub.arknexus.net/v1/coordination/recent` — `localhost:18090` is vault-neo local, unreachable from K2 WSL.
- **P-K3-B**: Ollama is Windows-side, accessible from K2 WSL as `host.docker.internal:11434`, NOT `localhost:11434`.
- **P-K3-C**: `HUB_AUTH_TOKEN` not in systemd env — must add `Environment=HUB_AUTH_TOKEN=...` to aria.service unit.
- **P-K3-D**: Bus response structure is `{"ok":true,"entries":[...]}` — original code looked for `data.get("messages")` (missed entries).
- **P-K3-E**: Candidate filename must have `cand_` prefix — `list_candidate_files()` only globs `cand_*.json`, `candidate-*.json`.
- **P-K3-F**: `ambient_observation` type fails `task_completion` gate (scored 0.5) — add to `AWARENESS_TYPES` fast-path.
- **P-K3-G**: Spine entry has no `excerpt` field — insight is at `proposed_change.patch.ambient_insight`.
- **P-K3-H**: Hub rejects urgency `"low"` — valid values include `"informational"`.

## Verified End-to-End
```
regent → colby | [KARMA AMBIENT] I noticed something: The coordination signaling between senders shows a consistent use of alternative names for topics like "heartbeat" and "online", suggesting an informal communication style within the working environment
```
Confirmed live on coordination bus 2026-03-22T07:45:38Z.

## Next: E-1-A
Write `corpus_builder.py` (ledger instruction pairs extraction, no GPU needed) on P1.
