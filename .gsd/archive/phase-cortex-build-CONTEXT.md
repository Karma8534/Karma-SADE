# Phase: Build the Brain (K2 Memory Cortex) — CONTEXT

## Design Decisions (locked)

1. **K2 is primary, P1 is fallback.** K2 is Julian's dedicated hardware. Colby only RDPs to oversee.
2. **Nemotron Nano 9B v2** is the cortex model. 131K context, hybrid Mamba-2, agent/tool-use tuned by NVIDIA. Already pulled (9.1GB).
3. **Cortex is a persistent HTTP service** on K2 — not a one-shot script. Always-on, auto-restart via systemd.
4. **Single API endpoint** for context: `POST K2:PORT/context` returns full current state. Replaces 20-file reads.
5. **Ingestion at startup + real-time feed**: loads core files at boot, receives bus posts and new sessions as webhooks.
6. **Ollama persistent session**: model stays loaded in VRAM. Context window is the "working memory."
7. **9.1GB model on 8GB VRAM**: ~1GB will offload to system RAM. K2 has 64GB — this is fine. Verify tok/s after loading.

## What We're NOT Doing

- NOT building a RAG system — cortex holds everything in 128K context, no retrieval needed for current state
- NOT replacing FalkorDB/FAISS — those handle historical data beyond the 128K window
- NOT touching hub-bridge yet — that's Phase 3
- NOT touching Anthropic routing — that's Phase 3
- NOT building the P1 fallback — that's Phase 4

## Constraints

- K2 MCP tools have 30s timeout — long operations must go through SSH
- K2 Ollama is at `/mnt/c/Users/karma/AppData/Local/Programs/Ollama/ollama.exe` (Windows side from WSL)
- K2 systemd services run in WSL — `systemctl --user` for karma user
- Cortex must be reachable from vault-neo (via Tailscale 100.75.109.92) and P1 (via LAN 192.168.0.226)
