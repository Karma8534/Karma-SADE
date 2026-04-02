# Capability Inventory — Verified 2026-04-02 (Session 157)

## K2 (192.168.0.226 — Julian's Machine)

### Services (systemd, all running)
| Service | Purpose | Status |
|---------|---------|--------|
| aria.service | Local AI assistant (Flask :7890) | ACTIVE |
| karma-kiki.service | Autonomous loop (v5, contract-enforced) | ACTIVE |
| karma-regent.service | Ascendant CC daemon (Vesper pipeline host) | ACTIVE |

### Inference
- **Cortex**: julian-cortex v2.0.0 at :7892 — 101 knowledge blocks, 20,418 ingested, qwen3.5:4b (32K ctx)
- **Ollama models**: qwen3.5:4b (cortex primary), nomic-embed-text (embeddings)
- **Hardware**: RTX 4070 8GB VRAM — max viable model ~7B at 4-bit

### Vesper Pipeline (self-improvement)
- Watchdog (10min) → Eval (5min) → Governor (2min) — all active
- Spine v1262+, 1284 promotions, 20 stable patterns, 10 candidates
- self_improving: true

### Cache Files
- cc_scratchpad.md (Julian's working notes)
- cc_cognitive_checkpoint.json (session-end state)
- archonprime/archoncodex state files (agent tracking)
- vesper_identity_spine.json (behavioral patterns)

### Tools Available via K2
- 9 k2_* structured tools (file_read/write/list/search, python_exec, service_status/restart, scratchpad_read/write)
- shell_run (via aria /api/exec)
- K2 MCP server (14 tools via Scripts/k2_mcp_server.py)

---

## P1 (PAYBACK — Colby's Machine, shared with Julian)

### Services
| Service | Purpose | Status |
|---------|---------|--------|
| cc-server-p1.py | CC subprocess manager (:7891) | ACTIVE |
| claude-mem v10.6.3 | Persistent memory (:37778) | ACTIVE |
| karma_persistent.py | Karma's autonomous loop (bus poll + CC calls) | ACTIVE |

### Inference
- **CC --resume**: Claude Code subprocess with session continuity (via Max, $0/request)
- **Ollama**: Available but not running at check time (llama3.1:8b, qwen2.5-coder:3b, gemma3:4b, etc.)

### Key Resources
- 203 scripts in Scripts/
- Frontend source (Next.js static export) at frontend/
- Full git repo with all Memory/, .gsd/, .claude/ files
- CC wrapper source at docs/wip/preclaw1/ (1902 files — forensic reference)

---

## Vault-neo (arknexus.net — The Spine)

### Containers (all healthy)
| Container | Purpose | Status |
|-----------|---------|--------|
| anr-hub-bridge | Proxy + API surface (:18090) | UP |
| karma-server | FalkorDB context + tools | UP 7 days |
| anr-vault-search | FAISS semantic search (:8081) | UP 10 days |
| anr-vault-db | PostgreSQL | UP 4 weeks |
| anr-vault-api | Vault REST API | UP 25 hours |
| anr-vault-caddy | TLS termination | UP 4 weeks |
| falkordb | Graph database | UP 5 weeks |

### Data
- **Ledger**: 226,026 entries (append-only JSONL)
- **FalkorDB neo_workspace**: 5,695 Episodic + 1,181 Pattern + 571 Entity nodes
- **FAISS**: 193K+ indexed entries, auto-reindex on ledger change
- **claude-mem**: Cross-session persistent memory (P1 :37778)

### Live Endpoints (all verified 200 this session)
/health, /v1/status, /v1/chat, /v1/trace, /v1/learnings, /v1/cancel, /agora, P1:7891/health

---

## Coordination & Communication
- **Coordination bus**: In-memory + disk (JSONL), 24h TTL, approve/reject/redirect
- **Karma heartbeat**: Every 10min on bus (karma_persistent.py)
- **CC Ascendant watchdog**: K2 systemd timer 60s (cc_ascendant_watchdog.py)
- **Archon alerts**: Hourly from K2 (identity drift detection)

## What's NOT Operational
- Chrome extension (SHELVED)
- Voice pipeline (Sprint 7 — sovereign Whisper pipeline, not CC native)
- Camera widget (Sprint 7)
- Electron app (scaffold exists on K2, not built)
- OpenRouter/ngrok fallback (evaluation pending)
- P1 Ollama (not started this session)

## Key Docs
- Sacred context: Memory/00-sacred-context.md
- Resurrection Plan v2.1: Memory/03-resurrection-plan-v2.1.md
- The Nexus plan: docs/ForColby/nexus.md (APPEND ONLY)
- System prompt: Memory/00-karma-system-prompt-live.md
- Scope index: Karma2/cc-scope-index.md (67 pitfalls, 16 decisions, 5 proofs)
