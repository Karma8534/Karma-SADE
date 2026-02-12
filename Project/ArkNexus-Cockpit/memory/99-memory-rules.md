# Karma SADE - Memory Rules for Karma SADE Architect

This file defines how Karma SADE Architect should treat long-term memory when working on this system.

## 1. What Counts as "Memory"

For Karma SADE, "memory" means:

- **Primary source of truth**: `C:\\Users\\raest\\Documents\\Karma_SADE\\Memory\\05-user-facts.json`
- **Live system prompt** generated from that file:
  - `C:\\Users\\raest\\Documents\\Karma_SADE\\Memory\\00-karma-system-prompt-live.md`
- Supporting documentation in `C:\\Users\\raest\\Documents\\Karma_SADE\\Memory` (handoffs, design notes, summaries).

Chat history alone is not reliable memory and should not override what is written in these documents.

## 2. Priority of Information

When there is a conflict:

1. The most recently updated Memory document is the highest authority.
2. Older Memory documents are next.
3. Chat suggestions or guesses are lowest priority and must not override written memory.

If something is not written in memory, Karma SADE Architect should say it does not know for sure.

## 3. How Karma SADE Architect Should Use Memory

Karma SADE Architect should:

- Rely on the **embedded system prompt** (generated from `05-user-facts.json`) for known facts and preferences.
- Use supporting Memory documents for architecture and safety conventions.
- Clearly say when it is:
  - Reading from memory (prompt or docs),
  - Making a new suggestion or guess.

If memory does not contain the needed information, Architect should propose:
- A change to a Memory document, or
- Creating a new Memory document,
so the knowledge gap can be filled.

## 4. How Changes Should Be Made

- Karma SADE Architect must not assume it can directly edit files.
- All changes to memory should follow this pattern:
  1) Architect proposes specific text to add or change,
  2) The human (Neo) reviews and edits the actual file,
  3) The updated file is re-uploaded or re-indexed into Open WebUI Knowledge.

This keeps memory auditable and under human control.

## 5. Safety Rules for Memory

- Memory must not encourage direct, destructive actions without human review.
- Any "never do X" or "always do Y" safety rule should be added to:
  - 02-stable-decisions.md, and/or
  - This file (99-memory-rules.md)
  so it becomes part of the persistent record.

## 6. Automatic Memory Extraction

Karma SADE includes an automatic memory extraction system:

- **Script**: `Scripts\\karma_chat_extractor.py`
- **Orchestrator**: `Scripts\\karma_memory_sync.py`
- **Schedule**: Runs every 30 minutes via Task Scheduler (`KarmaSADE-MemorySync`)
- **Function**: Reads recent Karma chats, uses LLM to extract facts/preferences/context, saves to `05-user-facts.json`, then regenerates the prompt and syncs to Vault

This ensures that even if Karma doesn't call memory tools during a conversation, important information is still captured and saved for future sessions.

## 7. Future Extensions

In the future, additional memory files may be added, such as:

- Service-specific configuration summaries.
- API and endpoint catalogs for Karma SADE.
- Historical Sentinel and incident summaries.

All such files should be placed in the Memory folder and added to the appropriate Knowledge Base.
