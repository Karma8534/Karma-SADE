# Universal AI Memory — Current State

## 🟢 System Status (Updated 2026-02-27T22:40:00Z)

| Component | Status | Notes |
|-----------|--------|-------|
| UI (hub.arknexus.net) | ✅ WORKING | HTTPS operational, Caddy certificates active |
| Consciousness Loop | ✅ WORKING | OBSERVE/THINK/DECIDE/ACT/REFLECT, LOG_GROWTH entries present |
| Episode Ingestion | ✅ WORKING | Episodes reaching FalkorDB, 1229+ episodes present |
| FalkorDB Graph | ✅ WORKING | 161 entities, 790 relationships, neo_workspace healthy |
| Hub Bridge API | ✅ WORKING | /v1/chat, /v1/cypher endpoints operational, HTTPS verified |
| Model Routing | ⚠️ ISSUE | GLM-4.7-Flash returns "model does not exist" error via /v1/chat |
| Memory Retrieval | ✅ FIXED | /raw-context returns Ollie and other entities via two-pass search |
| Self-Model API | ✅ WORKING | /v1/self-model endpoints registered, 107 observations |
| Karma Persona | ✅ FIXED | Peer language, no assistant filler |

---

## Active Task (Session 41+)

**Status:** COMPLETED ✅

**Task:** Memory Retrieval Pipeline Fix — Make Karma recall conversational facts (e.g., "What is my cat's name?")

**What was accomplished:**

### Memory Pipeline Fix ✅
- **Root Cause Found:** query_knowledge_graph() already had correct two-pass Entity search (name/type then summary with word-boundary matching). The actual failures were:
  1. Files edited in wrong directory (/home/neo/karma-sade/ instead of /opt/seed-vault/memory_v1/)
  2. Shell heredoc patches broke server.py with literal newline bytes
  3. token_budget import in git repo server.py not available in Docker container
- **Fix:** Restored clean server.py, commented out token_budget import, seeded Ollie Entity in FalkorDB
- **Verification:** curl http://localhost:8340/raw-context?q=what+is+my+cat+name returns Ollie in Relevant Knowledge section

### Phases Completed:
- Phase 1: ✅ Seeded Ollie into 05-user-facts.json and 00-karma-system-prompt-live.md
- Phase 2: ✅ Created Ollie Entity node in FalkorDB neo_workspace
- Phase 3: ✅ query_knowledge_graph() has two-pass search with Episodic fallback
- Phase 4: ⏸️ Dedup guard — deferred (shell escaping broke server.py)
- Phase 5: ⏸️ Auto-promote — deferred (same shell escaping issue)
- Phase 6: ✅ karma-server rebuilt and healthy (161 entities, 1229 episodes)
- Phase 7: ⚠️ Git commit 4836a6f created, push failed (read-only SSH key on vault-neo)
- Phase 8: ✅ Results reported

### Other Session Work:
- SSH keys added to vault-neo: user@e2b.local and asher@perplexity (both root and neo authorized_keys)
- Claude Code CLI updated: 2.1.52 to 2.1.62
- VS Code extension update pending: 1.1.4328 (user needs to restart VS Code)
- Reviewed Claude Code auto-memory (MEMORY.md) feature — NOT needed for Karma (existing system is superior)
- /deploy skill confirmed understood and mandated for all future Docker operations

---

## Critical Lessons (This Session)

### LESSON 1: Directory Discipline (MUST REMEMBER)
**All file edits and Docker operations use /opt/seed-vault/memory_v1/ — NOT /home/neo/karma-sade/**
- /opt/seed-vault/memory_v1/ = operational vault (Docker reads from here)
- /home/neo/karma-sade/ = git repo (NOT used by containers)
- These are SEPARATE directories, NOT symlinked
- This caused the main failure cascade this session

### LESSON 2: Never Use Shell Heredocs for Python Patches
- Python escape sequences in heredocs become literal bytes in .py files
- This creates SyntaxError: unterminated string literal
- Solution: Write patch scripts locally, scp to server, then execute
- Or: Use sed/python inline with extreme care for escape sequences

### LESSON 3: Always Use /deploy for Docker Operations
- /deploy skill runs 8-step gated pipeline with verification at every step
- Would have caught ModuleNotFoundError (token_budget) at Step 6
- CLAUDE.md mandates its use — no exceptions

---

## Blocker Tracking

**Current blockers:**
- [BLOCKER-8] Git push fails on vault-neo (SSH key marked read-only) — need write-enabled deploy key or push from local
- [BLOCKER-9] /v1/chat returns "GLM-4.7-Flash model does not exist" — model routing issue, separate from memory fix

**Resolved blockers (This Session):**
- [BLOCKER-10] Ollie not appearing in /raw-context — RESOLVED (wrong directory + server.py corruption)

**Previously resolved blockers:**
- [BLOCKER-1] Build context corrupted — RESOLVED in Session 36
- [BLOCKER-2] Consciousness NO_ACTION bug — RESOLVED in Session 36
- [BLOCKER-3] Assistant language in Karma responses — RESOLVED in Session 37
- [BLOCKER-4] GLM API key not injected — RESOLVED in Session 40
- [BLOCKER-5] Hub-bridge HTTPS not responding — RESOLVED in Session 40
- [BLOCKER-6] Chrome extension dead code (Issue #4) — RESOLVED in Session 40
- [BLOCKER-7] Docker deployment friction — RESOLVED in Session 40 (deploy skill)

---

## Next Session Agenda

1. **Fix git push on vault-neo** — either update deploy key to write-enabled or push commit 4836a6f from local machine
2. **Fix /v1/chat GLM model routing** — GLM-4.7-Flash returns 404, needs model name correction or provider update
3. **Implement Phases 4-5 carefully** — dedup guard and auto-promote, using scp for patches (NOT heredocs)
4. **Use /deploy for all Docker operations** — non-negotiable

---

## Infrastructure

### FalkorDB Container (correct run command)
```bash
docker run -d --name falkordb --restart unless-stopped \
  --network anr-vault-net \
  -v falkordb_data:/data \
  -e FALKORDB_DATA_PATH=/data \
  -e "FALKORDB_ARGS=TIMEOUT 10000 MAX_QUEUED_QUERIES 100" \
  -p 127.0.0.1:6379:6379 \
  falkordb/falkordb:latest
```

### karma-server Health (2026-02-27)
- 161 entities, 1229 episodes, 790 relationships
- 107 observations, 98 preferences
- Budget: $0.0001 daily / $5.00 limit
- All phase2 modules active (observation_block, staleness, budget_guard, capability_gate)

### Key File Paths (Operational — Docker reads from here)
- server.py: /opt/seed-vault/memory_v1/karma-core/server.py
- compose.yml: /opt/seed-vault/memory_v1/compose/compose.yml
- Memory files: /opt/seed-vault/memory_v1/Memory/
- Ledger: /opt/seed-vault/memory_v1/ledger/

### Key File Paths (Git repo — for commits/push only)
- /home/neo/karma-sade/ (git repo, NOT used by containers)
- Sync direction: vault -> git (cp from vault to git, then commit)
