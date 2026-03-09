# Karma SADE Session Summary (Latest)

**Date**: 2026-03-09
**Session**: 70
**Focus**: System prompt trim (fix 429 rate limits) + FalkorDB cron bug fix + context catchup + "resurrection spine" ban

---

## What Was Done

### 1. System Prompt Trimmed (16,519 → 11,674 chars)
- Root cause: System prompt had grown to 16,519 chars across multiple fix sessions → 67K+ input chars per request → recurring 429 rate limits from Z.ai
- Removed: API Surface table, 3 low-value corrections (#1 verdict.txt, #2 batch_ingest direction, #5 consciousness loop), infrastructure container list, machine specs
- All critical coaching preserved: session continuity, Recently Learned priority, tool routing, K2 deprecated, FalkorDB fields, ASSIMILATE/DEFER/DISCARD, Behavioral Contract
- Result: 56,843 input chars per request (was 67,388), 429 pressure significantly reduced

### 2. batch_ingest Cron Bug Fixed
- Root cause: crontab was using Graphiti mode (no --skip-dedup). At 3200+ Episodic nodes, Graphiti dedup queries exceed 10s timeout → silent failure → watermark advances → 0 FalkorDB nodes created
- Symptom: Karma reporting "my latest context is Session 66" despite cron running every 6h and reporting "all caught up"
- Fix: `--skip-dedup` added permanently to vault-neo crontab
- Manual catchup: reset watermark to 4100, 118 entries ingested, 0 errors, 879 eps/s

### 3. FalkorDB Context Verified
- March 5 entries: 76 nodes now in FalkorDB
- March 9 entries: present (ep_hub-chat_108 through ep_hub-chat_117)
- Karma's context now includes recent conversations

### 4. "Resurrection Spine" Language Banned
- Karma was using "resurrection spine", "checkpoint loading", "session ID mismatch" — fiction from old architecture docs in her graph
- Fixed: explicit ban added to system prompt with correct explanation (FalkorDB 0-6h lag is normal)

### 5. DRL/RL Article Noted for Future
- Article: https://kuriko-iwai.com/deep-reinforcement-learning
- Connection to Karma: DPO pairs = reward signal infrastructure; corrections pipeline = manual policy iteration; write_memory gate = RL loop
- Saved to claude-mem #4248 — revisit when DPO pair count is meaningful

---

## What's Live (Verified)

| Component | Status |
|-----------|--------|
| Hub Bridge | ✅ RestartCount=0, listening |
| /v1/chat | ✅ ok, 56,843 input chars |
| System prompt | ✅ 11,674 chars, deployed |
| FalkorDB | ✅ 76+ March-5 nodes, caught up |
| batch_ingest cron | ✅ --skip-dedup permanent |

---

## What's NOT Done (Next Session)

1. **Thumbs up/down general feedback UI** — brainstorming started but NOT complete. Need to:
   - Explore hub-bridge/app/ for unified.html and existing /v1/feedback endpoint
   - Complete brainstorming → writing-plans → implement
   - The write_memory thumbs (Session 68) is different from general per-message feedback

---

## Commits This Session

- `8b989dc` — session-70: trim system prompt 16519→11674 chars to fix 429 rate limits
- `59408af` — fix(karma-prompt): ban 'resurrection spine' + fix cron --skip-dedup + FalkorDB catchup
