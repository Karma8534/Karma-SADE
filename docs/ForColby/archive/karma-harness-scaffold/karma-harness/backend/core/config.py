"""
Karma core configuration — loaded from .env at startup
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    karma_version: str = "1.0.0"
    karma_env: str = "development"

    # Database
    database_url: str

    # Redis
    redis_url: str

    # Sandbox
    sandbox_url: str = "http://sandbox:8888"
    sandbox_token: str

    # Auth
    jwt_secret: str
    jwt_expire_minutes: int = 10080

    # Self-edit
    self_edit_approval_window_minutes: int = 15
    self_edit_auto_approve: bool = True

    # Provider keys
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    zai_api_key: Optional[str] = None
    zai_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    perplexity_api_key: Optional[str] = None
    minimax_api_key: Optional[str] = None
    minimax_group_id: Optional[str] = None
    groq_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_models: str = "qwen2.5:7b,qwen2.5-coder:7b"

    @property
    def available_providers(self) -> list[str]:
        """Returns list of providers with valid API keys"""
        providers = []
        if self.anthropic_api_key:    providers.append("anthropic")
        if self.google_api_key:       providers.append("google")
        if self.openai_api_key:       providers.append("openai")
        if self.zai_api_key:          providers.append("zai")
        if self.perplexity_api_key:   providers.append("perplexity")
        if self.minimax_api_key:      providers.append("minimax")
        if self.groq_api_key:         providers.append("groq")
        if self.openrouter_api_key:   providers.append("openrouter")
        providers.append("ollama")    # always available (local)
        return providers

    @property
    def ollama_model_list(self) -> list[str]:
        return [m.strip() for m in self.ollama_models.split(",") if m.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
