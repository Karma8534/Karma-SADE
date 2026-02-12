# Karma SADE - Core Architecture (Source of Truth)

## 1. Purpose

Karma SADE is my personal infrastructure and automation environment.
It manages local AI tools, agents, and supporting services on my machines and remote servers.

## 2. High-Level Components

- Local AI stack (Ollama, Open WebUI, local models).
- Karma SADE Architect (architecture/infra assistant persona in Open WebUI).
- Monitoring and Sentinel/watchdog services.
- Storage for designs, memory, and logs on my Windows 11 machine.

## 3. Host System

- OS: Windows 11
- Primary user profile: C:\Users\raest
- Project root (documents): C:\Users\raest\Documents\Karma_SADE

## 4. Local Folders Used by Karma SADE

- Design documents: C:\Users\raest\Documents\Karma_SADE\Design
- Persistent memory docs: C:\Users\raest\Documents\Karma_SADE\Memory
- Logs and exported reports: C:\Users\raest\Documents\Karma_SADE\Logs
- Scripts and automation: C:\Users\raest\Documents\Karma_SADE\Scripts

## 5. Key Services and Tools

- Ollama: local model runtime (http://localhost:11434), provides llama3.1:8b, nomic-embed-text, and others.
- Open WebUI v0.7.2: user interface and orchestration (http://localhost:8080).
- Karma SADE Architect: main persona for infra and architecture work inside Open WebUI.
- Sentinel: health monitoring system (PowerShell scripts, runs every 15 minutes).
- Warp: Agentic Development Environment — primary terminal + AI agent (Oz).
- VS Code + Continue.dev: AI-assisted coding with local Ollama backend.
- Perplexity Max: cloud research assistant (citation-first web retrieval, Labs).
- ArkNexus Vault: cloud memory persistence on DigitalOcean droplet (vault.arknexus.net).
- Hub Bridge v2.0.0: OpenAI proxy at hub.arknexus.net — GPT-5-mini/GPT-5.2, fact-based prompt, spend cap.
- Full resource inventory: Memory/12-resource-inventory.json (canonical copy on Vault at /opt/seed-vault/memory_v1/canon/resources.v1.json).

## 6. Aria — Single Source of Truth

Aria is the canonical shared knowledge layer for the ArkNexus ecosystem.
All reference data (resource inventories, architecture decisions, facts) lives in Aria
so that every agent — Karma (via Open WebUI), Warp (via terminal), and Hub Bridge (via Vault API) —
works from the same truth.

- Canonical store: ArkNexus Vault on vault-neo droplet (/opt/seed-vault/memory_v1/canon/)
- Local mirror: C:\Users\raest\Documents\Karma_SADE\Memory\
- Sync: karma_vault_sync.py, bidirectional, every 5 minutes via KarmaSADE-MemorySync task
- API access: GET /v1/facts (deduplicated facts + preferences)

## 7. Memory System (Prompt-First Architecture)

- Source of truth: 05-user-facts.json (local) ↔ Vault ledger (cloud)
- ArkNexus Vault: Durable cloud storage with append-only JSONL ledger and audit trail.
- Sync: karma_vault_sync.py runs every 5 minutes, bidirectional with timestamp conflict resolution.
- Resource inventory: 12-resource-inventory.json (local) ↔ /opt/seed-vault/memory_v1/canon/resources.v1.json (cloud)

## 8. Networking

- Ollama API: http://localhost:11434
- Open WebUI: http://localhost:8080
- Vault API: https://vault.arknexus.net (bearer auth)
- Hub Bridge: https://hub.arknexus.net/v1/chat (token auth)

## 9. Notes

This document is the high-level source of truth about Karma SADE's architecture.
Aria is the canonical knowledge layer — all agents read from it.
More detailed service descriptions and network layouts should be added here as they are finalized.
