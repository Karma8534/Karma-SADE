# Karma SADE - Stable Decisions and Conventions

This file lists decisions that should remain stable over time.
Karma SADE Architect should treat these as authoritative unless explicitly changed here.

## 1. Naming Conventions

- Main project name: "Karma SADE".
- Local folders:
  - Design: C:\Users\raest\Documents\Karma_SADE\Design
  - Memory: C:\Users\raest\Documents\Karma_SADE\Memory
  - Logs: C:\Users\raest\Documents\Karma_SADE\Logs
- Use underscores in Windows folder names when needed (e.g., Karma_SADE).

## 2. Safety and Change Management

- No destructive changes (deleting data, changing production configs) should be done directly by any agent.
- All risky changes must go through:
  1) Proposal in a chat,
  2) Written config/script in a file,
  3) Manual review and approval by the human (Neo),
  4) Then applied to the system.
- Karma SADE Architect should never assume it has direct shell access; it must always describe steps for the user to run.

## 3. Documentation and Memory

- Architecture and design docs live in the Design folder.
- Long-term facts and decisions live in the Memory folder and are synced into Open WebUI Knowledge.
- Logs and exported reports live in the Logs folder.
- When a decision becomes "how we do things now", it should be added or updated in this file.

## 4. Tools and Assistants

- Karma SADE Architect is the primary assistant for infrastructure and architecture planning.
- Perplexity Max is used for high-level research and external knowledge.
- Local tools (scripts, Sentinel, etc.) should be documented in Memory before being used by agents.

## 5. Future Extensions

- When new services (e.g., APIs, agents, databases) are added, their stable names, ports, and responsibilities should be recorded here.
- Any new "never do X" rule must be added to this file so it becomes part of persistent memory.
