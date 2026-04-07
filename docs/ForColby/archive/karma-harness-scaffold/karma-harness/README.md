# Karma Harness

A self-hosted, self-improving AI workspace. Unified Chat + Cowork + Code in a single browser interface. Powered by smart-routing across 7 AI providers with persistent memory and evolving persona.

## Quick Start (Development)

```bash
# 1. Clone and enter
cd karma-harness

# 2. Copy and fill your env
cp .env.example .env
# edit .env with your API keys

# 3. Start everything
docker-compose up --build

# 4. Open browser
open http://localhost
```

## Architecture

```
localhost:80  ──►  nginx
                    ├── /          ──►  frontend  (Next.js 14, :3000)
                    ├── /api/      ──►  backend   (FastAPI, :8000)
                    └── /ws/       ──►  backend websocket

backend  ──►  postgres (pgvector memory)
         ──►  redis    (session cache, self-edit queue)
         ──►  sandbox  (code execution, :8888)
         ──►  [7 AI providers via smart router]
```

## Smart Router Tiers

| Tier | Provider | Models | Use Case |
|------|----------|--------|----------|
| 0 — Free | Ollama (K2 local) | qwen2.5:7b, qwen2.5-coder | Simple tasks, offline |
| 1 — Ultra-cheap | Gemini Flash, GLM-4.5-Air | z.ai, Google | Default fast chat |
| 2 — Budget | MiniMax M2.7, GLM-5, Haiku 4.5, Sonar | Various | Capable tasks |
| 3 — Mid | Gemini 3.1 Pro, Sonar Pro | Google, Perplexity | Complex reasoning |
| 4 — Heavy | Claude Opus 4.6 | Anthropic | Self-edit validation only |
| Speed | Groq | Llama/Mixtral | Sub-200ms required |
| Fallback | OpenRouter | 300+ models | Any provider down |

## Services

| Service | Port | Description |
|---------|------|-------------|
| nginx | 80 | Reverse proxy / entry point |
| frontend | 3000 | Next.js UI |
| backend | 8000 | FastAPI brain |
| postgres | 5432 | Memory + vector store |
| redis | 6379 | Cache + self-edit queue |
| sandbox | 8888 | Code execution (internal only) |

## Self-Edit Engine

Karma monitors its own performance and proposes changes to its system prompt, memory schema, and routing logic. Proposals appear in the UI for manual approval. If no action is taken within **15 minutes**, Karma auto-applies the change and logs it to `self-edit/applied/`.

## Production Deploy

Change `server_name localhost` → `hub.arknexus.net` in `nginx/conf.d/default.conf` and add SSL via Certbot or Cloudflare tunnel.
