"""Karma Core Configuration — Decision-aligned

Model routing locked to Decision #7:
  - GLM-4.7-Flash (free via Z.ai, ~80% of traffic)
  - gpt-4o-mini (OpenAI, ~20% — reasoning + fallback)
MiniMax and Groq REMOVED.
"""
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

# ── LLM Tier 1: GLM-4.7-Flash (free via Z.ai / BigModel, ~80% of traffic) ──
GLM_API_KEY = os.getenv("GLM_API_KEY", "")
GLM_MODEL = os.getenv("GLM_MODEL", "glm-4-flash")
GLM_BASE_URL = os.getenv("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")

# ── LLM Tier 2: OpenAI gpt-4o-mini (reasoning + fallback, ~20% of traffic) ──
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANALYSIS_MODEL = os.getenv("ANALYSIS_MODEL", "gpt-4o-mini")

# NOTE: MiniMax and Groq REMOVED per Decision #7 (two-tier lock).
# If you see MINIMAX_API_KEY or GROQ_API_KEY in .env, they are ignored.

# Twilio SMS (outbound notifications + two-way chat)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER", "")
SMS_TO_NUMBER = os.getenv("SMS_TO_NUMBER", "+14845165322")

# Ledger path (mounted read-only from host)
LEDGER_PATH = os.getenv("LEDGER_PATH", "/ledger/memory.jsonl")

# Consciousness loop — OBSERVE only per Decision #3
CONSCIOUSNESS_INTERVAL = int(os.getenv("CONSCIOUSNESS_INTERVAL", "60"))  # seconds
CONSCIOUSNESS_JOURNAL = os.getenv("CONSCIOUSNESS_JOURNAL", "/ledger/consciousness.jsonl")
CONSCIOUSNESS_ENABLED = os.getenv("CONSCIOUSNESS_ENABLED", "true").lower() in ("true", "1", "yes")

# Bootstrap
BOOTSTRAP_LIMIT = int(os.getenv("BOOTSTRAP_LIMIT", "100"))  # conversations to process on first run

# Graph distillation loop — DISABLED per Decision #3 (made autonomous LLM calls)
# Re-enable only when Karma explicitly triggers distillation during a session.
DISTILLATION_ENABLED = os.getenv("DISTILLATION_ENABLED", "false").lower() in ("true", "1", "yes")
DISTILLATION_INTERVAL_HOURS = float(os.getenv("DISTILLATION_INTERVAL_HOURS", "24"))
DISTILLATION_MAX_EPISODES = int(os.getenv("DISTILLATION_MAX_EPISODES", "200"))

# K2 Worker decision & consciousness logging
DECISION_LOG = os.getenv("DECISION_LOG", "/ledger/decision_log.jsonl")
K2_CONSCIOUSNESS_LOG = os.getenv("K2_CONSCIOUSNESS_LOG", "/ledger/k2_consciousness.jsonl")
