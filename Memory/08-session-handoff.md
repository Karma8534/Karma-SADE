# Karma SADE Memory System - Session Handoff

**Date**: 2026-02-10  
**Status**: Ready for implementation  
**Next Action**: Execute Option A (Prompt-First) rebuild

---

## Context: What Happened

We built a memory system for Karma but discovered it has conflicts:
- System prompt has facts ✓
- Knowledge Base files have facts ✓
- **Problem**: Open WebUI reads from disk files, not database
- **Problem**: Multiple sync points cause race conditions
- **Result**: Karma doesn't remember "favorite color: purple" despite it being in 3 places

---

## Decision: Option A - Prompt-First Architecture

### Design
```
Chat → Extract facts → 05-user-facts.json (SOURCE OF TRUTH)
                              ↓
                    refresh_karma_memory.py
                              ↓
                    ┌─────────┴──────────┐
                    ↓                    ↓
              System prompt          Vault backup
              (embedded facts)       (cloud storage)
                    ↓
            Karma reads directly
```

### Why This Works
- **Single source of truth**: `Memory/05-user-facts.json`
- **Karma reads from prompt**: No RAG, no retrieval, always correct
- **Vault is backup only**: For disaster recovery
- **Simple**: 3 scripts, 1 scheduled task

---

## Implementation Plan

### Phase 1: Cleanup (Delete Broken Parts)
1. **Stop scheduled tasks**:
   - `KarmaSADE-VectorMemory` (ChromaDB, not needed)
   - `KarmaSADE-RefreshMemory` (will recreate simpler version)
   
2. **Delete ChromaDB database**:
   - `C:\Users\raest\Documents\Karma_SADE\Memory\VectorDB\` (entire folder)
   
3. **Remove Knowledge Base files from Open WebUI**:
   - Delete or ignore: `Persistent Facts & Decisions.txt`
   - Delete or ignore: KB file syncing
   
4. **Delete redundant scripts**:
   - `karma_vector_memory.py` (ChromaDB overhead)
   - `update_knowledge_base.py` (causes conflicts)
   - `sync_kb_file.py` (not needed)

### Phase 2: Keep These (Working)
- ✓ `05-user-facts.json` - source of truth
- ✓ `karma_vault_client.py` - Vault API client
- ✓ `karma_vault_sync.py` - sync to cloud
- ✓ `generate_karma_prompt.py` - embed facts in prompt
- ✓ `update_karma_prompt.py` - write prompt to DB

### Phase 3: Create New (Simplified)
1. **karma_chat_extractor.py** (replace karma_vector_memory.py)
   - Read Open WebUI chat database
   - Extract facts/preferences/context with LLM
   - Update `05-user-facts.json`
   - No ChromaDB, just JSON

2. **karma_memory_sync.py** (master orchestrator)
   - Run chat extraction
   - Refresh system prompt
   - Sync to Vault
   - All in one script

3. **KarmaSADE-MemorySync** scheduled task
   - Run `karma_memory_sync.py` every 30 minutes
   - Replace all other memory tasks

### Phase 4: Test
1. Chat: "My favorite color is orange"
2. Wait 30 min (or run sync manually)
3. New chat: "What's my favorite color?"
4. **Expected**: "Orange"

---

## Current System State

### Files
- **Working**:
  - `Memory/05-user-facts.json` - has purple
  - `Scripts/karma_vault_sync.py` - works
  - `Scripts/karma_vault_client.py` - works
  
- **Broken**:
  - Knowledge Base files (out of sync)
  - System prompt in DB (correct but not read)
  - ChromaDB (unnecessary complexity)

### Vault Integration
- ✓ API: `https://vault.arknexus.net`
- ✓ Bearer token: stored in session
- ✓ 22 items synced successfully
- ✓ Hub Bridge available for remote access

### Machine Specs
- **GPU**: RTX 4070 Laptop (4GB VRAM)
- **RAM**: 63GB
- **Models**: llama3.1:8b, deepseek-coder:6.7b
- **OS**: Windows 11 Pro

---

## Key Commands

### View current facts
```powershell
Get-Content C:\Users\raest\Documents\Karma_SADE\Memory\05-user-facts.json | ConvertFrom-Json | ConvertTo-Json
```

### List scheduled tasks
```powershell
Get-ScheduledTask | Where-Object { $_.TaskName -like "*KarmaSADE*" } | Format-Table -AutoSize
```

### Test Vault connection
```powershell
python C:\Users\raest\Documents\Karma_SADE\Scripts\karma_vault_client.py
```

### Manual memory sync
```powershell
python C:\Users\raest\Documents\Karma_SADE\Scripts\refresh_karma_memory.py
```

---

## Next Session Instructions

**Start new conversation with:**

> "Continue Karma SADE memory system rebuild. Implement Option A (Prompt-First) architecture from session handoff document at `C:\Users\raest\Documents\Karma_SADE\Memory\08-session-handoff.md`. Execute cleanup phase then rebuild with simplified workflow."

**Or simply:**

> "Implement Karma memory cleanup and rebuild per handoff doc"

---

## Success Criteria

When complete:
- [ ] Karma remembers favorite color correctly
- [ ] Only 1 scheduled task for memory
- [ ] Only 3 scripts (extract, prompt, vault)
- [ ] No ChromaDB database
- [ ] No Knowledge Base file conflicts
- [ ] Memory syncs to Vault every 30 min
- [ ] System prompt updates every 30 min
- [ ] New chats always have current memory

---

**Status**: Ready to execute  
**Estimated time**: 15-20 minutes  
**Risk level**: Low (backups exist in Vault)
