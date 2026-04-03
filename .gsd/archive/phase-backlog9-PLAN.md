# Backlog-9: karma-observer.py — PLAN
**Date:** 2026-03-25 | **Session:** 143

## Tasks

### Task 1: Build karma_observer.py
Write the observer script. Polling loop that:
1. Reads recent ledger entries via hub-bridge /v1/search (semantic search)
2. Extracts behavioral rules from [karma-correction], [PITFALL], thumbs-down patterns
3. Deduplicates against existing rules (fingerprint-based)
4. Writes new rules to karma_behavioral_rules.jsonl
5. POSTs each new rule to /v1/ambient with tags: `karma-behavioral-rule, karma-observer`
<verify>Python imports cleanly, no syntax errors. Rule extraction from sample data produces valid JSON.</verify>
<done>Script exists at Scripts/karma_observer.py, runs without error on sample input</done>

### Task 2: Deploy to K2
- scp script to K2:/mnt/c/dev/Karma/k2/aria/karma_observer.py
- Create systemd timer: karma-observer.timer (every 15min)
- Create systemd service: karma-observer.service
- Start and enable timer
<verify>systemctl status karma-observer.timer shows active. First run produces log output.</verify>
<done>Timer running on K2, first extraction cycle completed</done>

### Task 3: Seed test data
- POST a test [karma-correction] entry to /v1/ambient
- Wait for observer cycle (or trigger manually)
- Verify rule appears in karma_behavioral_rules.jsonl
- Verify rule appears in FAISS search results
<verify>Search for "karma-behavioral-rule" returns the test entry. jsonl file has the extracted rule.</verify>
<done>Test rule extracted, persisted, and searchable</done>

### Task 4: Verify in /v1/chat context
- Chat with Karma on hub.arknexus.net
- Ask about a topic related to the test rule
- Karma's response should be influenced by the rule (visible in semanticCtx)
<verify>Karma references or follows the behavioral rule without being explicitly told about it</verify>
<done>Rule visible in Karma's behavior — Backlog-9 GATE passed</done>

## Gate
First rule self-extracted and visible in a live /v1/chat context injection.
