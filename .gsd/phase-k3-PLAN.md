# K-3: Echo Integration — Ambient Observer Plan
**Created:** 2026-03-22 (Session 120)
**Author:** CC (Ascendant)
**Context:** See phase-k3-CONTEXT.md — design decisions locked there.

Execute one task at a time. Mark `<done>` only after `<verify>` passes with actual output.

---

## Task 1: Read existing code to understand integration points
<verify>Can state exact: (a) where Echo step is called in aria_consciousness.py, (b) _proactive_outreach() line number, (c) vesper_watchdog.py source field detection pattern</verify>
<done>true</done>

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'grep -n \"echo_consciousness_step\|echo_actions\" /mnt/c/dev/Karma/k2/aria/aria_consciousness.py | head -20 && echo === && grep -n \"_last_rsc_count\|_proactive_outreach\" /mnt/c/dev/Karma/k2/aria/karma_regent.py | head -20 && echo === && grep -n \"source\|ambient\" /mnt/c/dev/Karma/k2/aria/vesper_watchdog.py | head -20'"
```

---

## Task 2: Write ambient_observer.py on K2
<verify>File exists at /mnt/c/dev/Karma/k2/aria/ambient_observer.py with wc -l > 80 lines AND python3 -c "import sys; sys.path.insert(0,'/mnt/c/dev/Karma/k2/aria'); import ambient_observer; print('OK')" returns OK</verify>
<done>true</done>

Write locally, then scp to K2 (P019 — never heredoc for Python files).
Module must implement:
- `observe(cycle_id: str) -> list[dict]` — main entry point called from Echo step
- Poll `GET http://localhost:18090/v1/coordination/recent?limit=50` (coordination bus, local K2 port)
- Extract signal batch: unique senders, message frequency, topic word clusters (split on spaces, top 5 non-stopwords)
- If signal batch is not empty: call Ollama nemotron-mini with prompt "Given these coordination bus signals from the last hour: [batch], what is one specific behavioral pattern or insight you observe about Colby's work context? One sentence, factual, specific."
- Write to `/mnt/c/dev/Karma/k2/cache/regent_evolution.jsonl` as: `{"ts": "<iso>", "source": "ambient_observer", "cycle_id": "<id>", "insight": "<ollama output>", "signal_count": N}`
- Dedup: skip if last ambient entry was < 6h ago (check regent_evolution.jsonl last entry with source=ambient_observer)
- Return list of written entries (empty list = nothing new)

---

## Task 3: Hook ambient_observer into aria_consciousness.py Echo step
<verify>grep -n "ambient_observer" /mnt/c/dev/Karma/k2/aria/aria_consciousness.py shows import AND call inside Echo step block</verify>
<done>true</done>

After existing `echo_consciousness_step` call block (~line 150), add:
```python
try:
    from ambient_observer import observe as ambient_observe
    ambient_results = ambient_observe(cycle_id)
    if ambient_results:
        logger.info(f"[CONSCIOUSNESS] Ambient observer: {len(ambient_results)} new entries")
except Exception as amb_err:
    logger.error(f"[CONSCIOUSNESS] Ambient observer failed: {amb_err}")
```
Write file locally → scp to K2 (P019).

---

## Task 4: Extend vesper_watchdog.py — recognize ambient_observer entries
<verify>grep -n "ambient_observer\|ambient_observation" /mnt/c/dev/Karma/k2/aria/vesper_watchdog.py shows recognition logic</verify>
<done>true</done>

In `load_evolution_stats()` or the candidate emission function:
- When processing regent_evolution.jsonl entries with `source == "ambient_observer"`: emit candidate with `type="ambient_observation"`, `excerpt=entry["insight"][:200]`, `evidence={"source": "ambient_observer", "signal_count": entry.get("signal_count", 0)}`
- Write candidate to `regent_candidates/ambient_{cycle_id}.json`
Write file locally → scp to K2 (P019).

---

## Task 5: Extend vesper_eval.py — add ambient_observation to HEURISTIC_BLIND_TYPES
<verify>grep "ambient_observation" /mnt/c/dev/Karma/k2/aria/vesper_eval.py shows it in HEURISTIC_BLIND_TYPES list</verify>
<done>true</done>

Add `"ambient_observation"` to the `HEURISTIC_BLIND_TYPES` set/list.
This forces `model_weight=1.0` — prevents the fixed 0.25 heuristic score from dragging merged score below 0.80 gate (P035).
Write file locally → scp to K2 (P019).

---

## Task 6: Enhance karma_regent.py — _proactive_outreach() ambient trigger
<verify>grep -n "_last_ambient_count\|ambient_observation" /mnt/c/dev/Karma/k2/aria/karma_regent.py shows global + logic in _proactive_outreach()</verify>
<done>true</done>

Add after existing `_last_rsc_count = -1` global:
```python
_last_ambient_count = -1  # K-3: track ambient_observation promotions for proactive outreach
```

In `_proactive_outreach()`, after RSC logic block, add:
```python
# K-3: ambient_observation proactive trigger
global _last_ambient_count
try:
    ambient_patterns = [s for s in stable if s.get("type") == "ambient_observation"]
    current_ambient = len(ambient_patterns)
    if _last_ambient_count < 0:
        _last_ambient_count = current_ambient
    elif current_ambient > _last_ambient_count:
        newest = ambient_patterns[-1] if ambient_patterns else {}
        insight = newest.get("excerpt", "")[:200]
        msg = f"[KARMA AMBIENT] I noticed something: {insight}"
        bus_post("colby", msg, urgency="low")
        log(f"K-3: ambient proactive outreach fired — {insight[:80]}")
        _last_ambient_count = current_ambient
    else:
        _last_ambient_count = current_ambient
except Exception as e:
    log(f"_proactive_outreach ambient error: {e}")
```
Write file locally → scp to K2 (P019).

---

## Task 7: Restart aria.service on K2 + verify integration
<verify>systemctl --user status aria shows active AND aria.log shows "[CONSCIOUSNESS] Ambient observer:" within 5 minutes AND regent_evolution.jsonl has at least one entry with source=ambient_observer after 1 consciousness cycle</verify>
<done>true</done>

```bash
ssh vault-neo "ssh -p 2223 -l karma localhost 'systemctl --user restart aria && sleep 10 && tail -20 /mnt/c/dev/Karma/k2/aria/aria.log'"
```

---

## Task 8: End-to-end gate verification
<verify>Coordination bus shows a message from `regent` or `karma` with content "I noticed" addressed to `colby` that was NOT triggered by Colby sending a message. This is the K-3 gate.</verify>
<done>true</done>

Wait for vesper_watchdog cycle (~10 min), then vesper_eval + governor (~10 min), then _proactive_outreach() check in regent cycle (~5 min).
Check bus: `ssh vault-neo "TOKEN=$(cat /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt) && curl -s -H 'Authorization: Bearer $TOKEN' 'https://hub.arknexus.net/v1/coordination/recent?from=regent&limit=5'"`
Gate passes when: message content contains "I noticed" AND message was not in response to a Colby message.

---

## Summary Gate
K-3 is COMPLETE when Task 8 verify passes and the bus message is confirmed.
Update PLAN.md K-3 status to `✅ DONE [date]`.
Update MEMORY.md Next Session to E-1-A Step 1.
