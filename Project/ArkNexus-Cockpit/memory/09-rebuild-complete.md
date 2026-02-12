# Karma SADE Memory System - Optimized Architecture

**Date**: 2026-02-10  
**Status**: Production Ready  
**Architecture**: Prompt-First (Simplified)

---

## Overview

Karma SADE uses a Prompt-First architecture where facts are embedded directly into Karma's system prompt. No RAG, no Knowledge Base lookups—just clean, fast, reliable memory.

---

## Scripts (8 total)

- `session-startup.ps1` - Entry point, runs sync workflow
- `karma_memory_sync.py` - Master orchestrator (4 steps)
- `karma_chat_extractor.py` - Extracts facts from chat history
- `generate_karma_prompt.py` - Builds system prompt with facts
- `update_karma_prompt.py` - Writes prompt to Open WebUI DB
- `karma_vault_sync.py` - Syncs facts to cloud Vault
- `sync_docs_to_droplet.py` - Backs up docs to vault-neo
- `karma_health.py` - Health check utility
- `karma_vault_client.py` - Vault API client library

---

## Data Flow

```
Chat History
    |
    v
karma_chat_extractor.py (LLM extracts facts)
    |
    v
05-user-facts.json (SOURCE OF TRUTH)
    |
    +---> generate_karma_prompt.py ---> update_karma_prompt.py ---> Karma reads from prompt
    |
    +---> karma_vault_sync.py ---> Vault (cloud backup)
    |
    +---> sync_docs_to_droplet.py ---> vault-neo (droplet backup)
```

---

## Commands

- `karma` - Full sync (memory + droplet)
- `karma -SkipDroplet` - Memory sync only
- `newchat` - Alias for karma
- `python karma_health.py` - Check system health

---

## Scheduled Tasks

- `KarmaSADE-MemorySync` - Runs every 10 minutes

---

## Files

### Memory Directory
- `05-user-facts.json` - All facts, preferences, context
- `00-karma-system-prompt-live.md` - Generated prompt (auto-updated)
- `.chat_extraction_state.json` - Tracks processed chats
- `.vault_sync_state.json` - Tracks Vault sync state

### Logs
- `karma-sade.log` - Single consolidated log file

---

## Backup Locations

1. **Local**: `C:\Users\raest\Documents\Karma_SADE\Memory\`
2. **Droplet**: `vault-neo:~/karma-sade-docs/`
3. **Vault**: `https://vault.arknexus.net`

---

## Quick Reference

Run health check:
```
python C:\Users\raest\Documents\Karma_SADE\Scripts\karma_health.py
```

Manual sync:
```
karma
```

View logs:
```
Get-Content C:\Users\raest\Documents\Karma_SADE\Logs\karma-sade.log -Tail 30
```

---

## What Was Removed (Optimization)

- ChromaDB vector database
- 9 redundant scripts
- 5 Knowledge Base collections
- Multiple log files (consolidated to 1)
- Complex deploy script (simplified to session-startup.ps1)

---

**Last Updated**: 2026-02-10 04:25 UTC
