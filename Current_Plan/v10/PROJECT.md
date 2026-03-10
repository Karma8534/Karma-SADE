# PROJECT: Karma Peer — Universal AI Memory (v10)

## What This Is

Karma is a single coherent peer whose long-term identity lives in a verified memory spine; that memory enables continuity, evidence-based self-improvement, multi-model cognition when needed, and selective delegation — without introducing parallel sources of truth.

**North Star:** State resurrection, not transcript replay. Single canonical spine: Droplet FalkorDB + Vault ledger only. No parallel truth stores.

## Core Value

Problem: AI assistants lose continuity, hallucinate APIs, and make uncontrolled memory writes.
Solution: Persistent droplet identity + GSD workflow + human-gated memory writes + anti-hallucination discipline.

## System Architecture

- **vault-neo:** Karma's permanent home. FalkorDB neo_workspace, identity.json, consciousness.jsonl, hub-bridge API.
- **Hub Bridge:** https://hub.arknexus.net/v1/ — all AI requests route through here.
- **P1 (Colby):** Runs Claude Code. Chats with Karma from here.

## Capabilities (Current — v10 start)

- **Dual-model routing:** GLM-4.7-Flash (primary, standard) + gpt-4o-mini (deep mode, tool-calling)
- **Deep-mode tools:** graph_query, get_vault_file, write_memory (human-gated), fetch_url
- **Context pipeline:** karmaCtx (Entity Relationships + Recurring Topics) + semanticCtx (FAISS) + Brave Search + system prompt
- **Memory write gate:** write_memory → pending_writes Map → thumbs /v1/feedback → MEMORY.md append + DPO pair
- **Voice:** Peer-level. Direct, opinionated, dry humor. No service-desk closers.
- **Behavioral coaching:** Concrete trigger→action patterns for Recurring Topics + Entity Relationships
- **Deep mode UI:** DEEP button in unified.html sends x-karma-deep header

## Planned v10 Enhancements

| Enhancement | Source | Priority |
|-------------|--------|--------|
| Universal thumbs via turn_id | Session 71 plan (written) | HIGH |
| Entity Relationships data quality fix | Session 71 analysis | HIGH |
| Confidence levels (HIGH/MEDIUM/LOW) | CCintoanOS.PDF | MEDIUM |
| Anti-hallucination pre-check coaching | CCintoanOS.PDF | MEDIUM |
| Context7 MCP for live docs | CCintoanOS.PDF + PiMonoCoder.PDF | MEDIUM |
| PostToolUseFailure logging | CCintoanOS.PDF | LOW |
| Pi-mono 4-tool coding philosophy | PiMonoCoder.PDF | LOW |
| Hooks > LLMs for deterministic tasks | CCintoanOS.PDF | LOW |
| Path-based rules (global vs project CLAUDE.md) | CCintoanOS.PDF | LOW |
| Plans as Files discipline | PiMonoCoder.PDF | LOW |
| Multi-agent brainstorm for complex questions | CCintoanOS.PDF | FUTURE |

## Key Invariants

1. Truth alignment: Ground truth is FalkorDB neo_workspace. Never knowingly assert false facts.
2. Single source of truth: Droplet canonical. No parallel memory systems.
3. Continuity: State lives on droplet. Sessions end, droplet persists.
4. Substrate independence: Reasoning rooted in droplet state, not LLM computation.
5. No reset: Colby never re-explains himself.
6. Human gate on memory writes: write_memory requires explicit thumbs approval.

## Success Metrics

- ✅ Coherence across sessions (no reset)
- ✅ Human-gated memory writes (write_memory + /v1/feedback)
- ✅ GLM tool-calling (graph_query, get_vault_file, write_memory, fetch_url)
- ⏳ DPO fine-tuning loop (0/20 pairs)
- ⏳ Anti-hallucination discipline (v10 target)
- ⏳ Coding agency with live docs (v10 target)

---

**Last updated:** 2026-03-10 (v10 snapshot — Sessions 65-71 complete)
