# Karma-SADE

**Durable memory backbone for autonomous AI agents.**

Karma-SADE provides the memory primitives that agent projects need but rarely get right: a temporal knowledge graph with integrity proofs, hot/warm/cold retrieval tiers, and a validated promotion pipeline — all framework-agnostic and designed to drop into any agent architecture.

---

## The Problem

Every serious agent project eventually hits the same wall: memory. Today's common approaches all break at scale:

- **Context stuffing** — expensive, lossy, and capped by model limits
- **Bolted-on vector stores** — no validation layer, no audit trail, prone to hallucination drift
- **Custom one-offs** — brittle, untested, rebuilt from scratch in every project

Karma-SADE solves this by providing a reusable memory spine with verification built in from the ground up.

## Core Architecture

### Temporal Knowledge Graph (FalkorDB)

Agent memories are stored as episodes in a temporal knowledge graph, not flat embeddings. Each episode carries relationships, timestamps, and integrity hashes — making memory queryable by structure, not just similarity.

### Raw → Candidate → Canonical Pipeline

Observations flow through three validation stages before becoming trusted memory. Raw captures are unfiltered. Candidates pass structural checks. Canonical memories are integrity-hashed and anchored — creating a provenance chain that makes the agent's reasoning history auditable and reproducible.

### Hot / Warm / Cold Memory Tiers

- **Hot** — Last 100 episodes. Immediate context for active reasoning.
- **Warm** — Last 1,000 episodes. Relevant history without full graph traversal.
- **Cold** — Complete history. Queryable on demand, never loaded by default.

This keeps retrieval fast without discarding long-term context or blowing up token costs.

### Consciousness Loop

A continuous cycle of observation, reflection, and memory consolidation. Delta-only queries ensure idle cycles cost nothing — the system only calls LLMs when new data arrives. The loop supports configurable intervals and graceful restart without replaying history.

### Multi-Model Cognitive Routing

Framework-agnostic patterns for routing cognitive tasks across different LLM providers under a single agent identity. Supported backends include MiniMax, GLM-5, Groq, Gemini, DeepSeek, and OpenAI — selectable per-task based on cost, capability, and latency requirements.

## What You Can Use

Karma-SADE is designed as composable primitives, not a monolithic framework. Adopt what you need:

| Component | Use Case |
|-----------|----------|
| **Vault schema** | Standardized episode storage with integrity proofs |
| **Validation pipeline** | Raw → Candidate → Canonical promotion workflow |
| **Memory tiers** | Hot/warm/cold retrieval without full graph loads |
| **Consciousness loop** | Continuous observation-reflection cycles with delta queries |
| **Multi-model router** | Cost-optimized LLM routing under a single identity |
| **Gateway patterns** | Auth, rate limiting, and capture middleware |

## Current State

- **600+ verified episodes** in production FalkorDB instance
- **Consciousness loop** running stable with delta-only queries
- **Infrastructure**: Docker / Caddy / Cloudflare on DigitalOcean
- **Active development**: Memory architecture, daily logging, long-term consolidation

## Getting Started

### Prerequisites

- Python 3.10+
- Docker (for FalkorDB)
- At least one LLM API key (MiniMax, OpenAI, Groq, Gemini, or GLM)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Karma8534/Karma-SADE.git
cd Karma-SADE/karma-core

# Start FalkorDB
docker run -d -p 6379:6379 falkordb/falkordb

# Configure environment
cp .env.example .env
# Edit .env with your API keys and FalkorDB connection

# Run the consciousness loop
python consciousness.py
```

### Configuration

Copy `.env.example` to `.env` and set:

```
FALKORDB_HOST=localhost
FALKORDB_PORT=6379
CONSCIOUSNESS_ENABLED=true
CONSCIOUSNESS_INTERVAL=60
```

## Project Structure

```
Karma-SADE/
├── karma-core/
│   ├── consciousness.py       # Consciousness loop with delta queries
│   ├── server.py              # API endpoints and gateway
│   ├── memory/
│   │   ├── daily/             # Daily memory logs (YYYY-MM-DD.md)
│   │   └── LONG_TERM_MEMORY.md
│   └── .env.example
├── docs/                      # Architecture documentation
└── README.md
```

## Roadmap

- [x] Temporal knowledge graph with FalkorDB
- [x] Consciousness loop with delta-only queries
- [x] Multi-model cognitive routing
- [x] Vault schema with integrity hashes
- [ ] Memory tier query optimization
- [ ] Standardized plugin interface for external agent frameworks
- [ ] Comprehensive test suite (Vitest + Riteway)
- [ ] Documentation site

## Contributing

Contributions welcome. Please open an issue first to discuss what you'd like to change.

## License

MIT

---

Built by [Karma8534](https://github.com/Karma8534)
