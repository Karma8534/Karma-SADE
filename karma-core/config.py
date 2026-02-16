"""Karma Core Configuration"""
import os

# FalkorDB (temporal knowledge graph)
# FalkorDB uses Redis protocol on port 6379 internally
# Docker exposes 7687 externally but internal network uses 6379
FALKORDB_HOST = os.getenv("FALKORDB_HOST", "falkordb")
FALKORDB_PORT = int(os.getenv("FALKORDB_PORT", "6379"))

# Graphiti settings
GRAPHITI_GROUP_ID = os.getenv("GRAPHITI_GROUP_ID", "neo_workspace")

# PostgreSQL (analysis engine)
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "anr-vault-db")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "memoryvault")
POSTGRES_USER = os.getenv("POSTGRES_USER", "memory")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# LLM — OpenAI (default fallback + consciousness analysis)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANALYSIS_MODEL = os.getenv("ANALYSIS_MODEL", "gpt-4o-mini")

# LLM — Groq (speed: Llama on custom silicon, ~100ms responses)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# LLM — MiniMax M2.5 (coding: 80.2% SWE-Bench, OpenAI-compatible)
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")
MINIMAX_MODEL = os.getenv("MINIMAX_MODEL", "MiniMax-M2.5")

# LLM — GLM-5 (reasoning: deep analysis, complex problem-solving)
GLM_API_KEY = os.getenv("GLM_API_KEY", "")
GLM_MODEL = os.getenv("GLM_MODEL", "glm-5")
GLM_BASE_URL = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")

# Twilio SMS (outbound notifications + two-way chat)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")
SMS_TO_NUMBER = os.getenv("SMS_TO_NUMBER", "+14845165322")

# Ledger path (mounted read-only from host)
LEDGER_PATH = os.getenv("LEDGER_PATH", "/ledger/memory.jsonl")

# Consciousness loop
CONSCIOUSNESS_INTERVAL = int(os.getenv("CONSCIOUSNESS_INTERVAL", "60"))  # seconds
CONSCIOUSNESS_JOURNAL = os.getenv("CONSCIOUSNESS_JOURNAL", "/ledger/consciousness.jsonl")
CONSCIOUSNESS_ENABLED = os.getenv("CONSCIOUSNESS_ENABLED", "true").lower() in ("true", "1", "yes")

# Bootstrap
BOOTSTRAP_LIMIT = int(os.getenv("BOOTSTRAP_LIMIT", "100"))  # conversations to process on first run
