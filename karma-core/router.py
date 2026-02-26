"""
Karma Model Router — Two-Tier Locked (Decision #7 aligned)

Routes ALL requests through exactly two models:
  - GLM-4.7-Flash (free via Z.ai, ~80% of traffic — coding, speed, general)
  - gpt-4o-mini (OpenAI, ~20% — reasoning, analysis, final fallback)

MiniMax, Groq, GLM-5 REMOVED per Decision #7.
All providers expose OpenAI-compatible /v1/chat/completions endpoints,
so we use the OpenAI Python SDK with different base_url + api_key per provider.
"""
import time
from dataclasses import dataclass, field
from typing import Optional

from openai import OpenAI

import config


# ─── Model Definitions ───────────────────────────────────────────────────

@dataclass
class ModelProvider:
    """A model provider with its connection details and capabilities."""
    name: str               # Human-readable name
    model: str              # Model identifier for API calls
    base_url: str           # OpenAI-compatible base URL
    api_key: str            # API key (from env)
    task_types: list[str]   # What this model is good at
    max_tokens: int = 1024  # Default max tokens
    temperature: float = 0.7
    priority: int = 0       # Lower = higher priority within same task type
    enabled: bool = True    # Can be disabled if key is missing

    _client: Optional[OpenAI] = field(default=None, repr=False, compare=False)

    def get_client(self) -> OpenAI:
        """Lazy-init OpenAI-compatible client."""
        if self._client is None:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=30.0,
            )
        return self._client


# ─── Task Types ───────────────────────────────────────────────────────────

class TaskType:
    CODING = "coding"           # Code generation, debugging, technical
    REASONING = "reasoning"     # Complex analysis, multi-step logic
    SPEED = "speed"             # Quick answers, simple chat, low latency
    ANALYSIS = "analysis"       # Pattern detection (used by Karma in-session)
    GENERAL = "general"         # Default catch-all


# ─── Task Classifier ─────────────────────────────────────────────────────

# Keyword sets for fast classification (no LLM needed)
_CODING_SIGNALS = frozenset([
    "code", "function", "class", "debug", "error", "bug", "fix", "implement",
    "refactor", "api", "endpoint", "database", "sql", "python", "javascript",
    "typescript", "rust", "docker", "git", "deploy", "build", "compile",
    "test", "unittest", "import", "module", "package", "library", "framework",
    "variable", "loop", "array", "dict", "json", "yaml", "html", "css",
    "react", "fastapi", "django", "flask", "node", "npm", "pip", "cargo",
    "def ", "async", "await", "return", "exception", "traceback", "stack",
    "regex", "parse", "serialize", "schema", "migration", "query", "index",
    "algorithm", "data structure", "binary", "hex", "encode", "decode",
    "write a script", "write code", "code review", "pull request",
])

_REASONING_SIGNALS = frozenset([
    "analyze", "reason", "think through", "step by step", "why does",
    "explain why", "compare", "trade-off", "tradeoff", "pros and cons",
    "evaluate", "assess", "implications", "consequence", "strategy",
    "architecture", "design decision", "should i", "which approach",
    "what if", "hypothetical", "scenario", "plan", "roadmap",
    "deep dive", "root cause", "fundamentally", "philosophical",
    "logic", "proof", "theorem", "derive", "mathematical",
    "complex", "nuanced", "multifaceted", "weigh",
])

_SPEED_SIGNALS = frozenset([
    "hi", "hello", "hey", "thanks", "thank you", "ok", "okay", "sure",
    "yes", "no", "bye", "goodbye", "what time", "weather", "quick question",
    "remind me", "what is", "who is", "when did", "where is", "how old",
    "define", "meaning of", "translate", "convert", "calculate",
    "tldr", "summary", "short answer", "briefly", "one word",
])


def classify_task(message: str) -> str:
    """Classify a user message into a task type using keyword matching.
    Fast, deterministic, zero-cost (no LLM call)."""
    msg_lower = message.lower().strip()
    words = set(msg_lower.split())

    # Short messages (< 15 chars) → speed
    if len(msg_lower) < 15:
        return TaskType.SPEED

    # Check for code blocks or technical patterns
    if "```" in message or "def " in msg_lower or "function " in msg_lower:
        return TaskType.CODING

    # Score each category
    coding_score = sum(1 for signal in _CODING_SIGNALS if signal in msg_lower)
    reasoning_score = sum(1 for signal in _REASONING_SIGNALS if signal in msg_lower)
    speed_score = sum(1 for signal in _SPEED_SIGNALS if signal in msg_lower)

    # Boost reasoning for question marks + longer messages
    if "?" in message and len(msg_lower) > 100:
        reasoning_score += 2

    # Pick highest score
    scores = {
        TaskType.CODING: coding_score,
        TaskType.REASONING: reasoning_score,
        TaskType.SPEED: speed_score,
    }
    best = max(scores, key=scores.get)

    # If no strong signal, default to general
    if scores[best] < 2:
        return TaskType.GENERAL

    return best


# ─── Router ───────────────────────────────────────────────────────────────

class ModelRouter:
    """Routes requests to EXACTLY two models per Decision #7:
      - GLM-4.7-Flash (free, ~80% of traffic)
      - gpt-4o-mini (~20%, reasoning + fallback)
    """

    def __init__(self):
        self.providers: list[ModelProvider] = []
        self.routing_stats: dict[str, dict] = {}  # model_name → {calls, total_ms, errors}
        self._init_providers()

    def _init_providers(self):
        """Initialize the two locked model providers.
        Decision #7: GLM-4.7-Flash (free, ~80%) + gpt-4o-mini (~20%)."""

        # ── Tier 1: GLM-4.7-Flash — PRIMARY for coding, speed, general ──
        # Free via Z.ai / BigModel. Handles ~80% of traffic.
        if config.GLM_API_KEY:
            self.providers.append(ModelProvider(
                name="glm-flash",
                model=config.GLM_MODEL,  # "glm-4-flash" from config
                base_url=config.GLM_BASE_URL,
                api_key=config.GLM_API_KEY,
                task_types=[TaskType.CODING, TaskType.SPEED, TaskType.GENERAL,
                            TaskType.REASONING, TaskType.ANALYSIS],
                max_tokens=2048,
                temperature=0.7,
                priority=0,  # Highest priority — default for everything
            ))
            print(f"[ROUTER] GLM-4.7-Flash registered: {config.GLM_MODEL} (PRIMARY — free tier, ~80%)")

        # ── Tier 2: OpenAI gpt-4o-mini — reasoning + final fallback ──
        # ~20% of traffic. Used for reasoning/analysis tasks, fallback for all.
        if config.OPENAI_API_KEY:
            self.providers.append(ModelProvider(
                name="openai",
                model=config.ANALYSIS_MODEL,  # "gpt-4o-mini" from config
                base_url="https://api.openai.com/v1",
                api_key=config.OPENAI_API_KEY,
                task_types=[TaskType.REASONING, TaskType.ANALYSIS,
                            TaskType.GENERAL, TaskType.CODING, TaskType.SPEED],
                max_tokens=1024,
                temperature=0.7,
                priority=5,  # Lower priority — reasoning specialist + fallback
            ))
            print(f"[ROUTER] OpenAI registered: {config.ANALYSIS_MODEL} (TIER 2 — reasoning + fallback, ~20%)")

        if not self.providers:
            print("[ROUTER] WARNING: No model providers configured! Need GLM_API_KEY or OPENAI_API_KEY.")

    def get_provider(self, task_type: str) -> Optional[ModelProvider]:
        """Get the best provider for a task type.
        Returns highest-priority (lowest number) enabled provider that supports this task."""
        candidates = [
            p for p in self.providers
            if p.enabled and task_type in p.task_types
        ]
        if not candidates:
            # Fallback: any enabled provider
            candidates = [p for p in self.providers if p.enabled]
        if not candidates:
            return None
        return min(candidates, key=lambda p: p.priority)

    def complete(self, messages: list[dict], task_type: str = TaskType.GENERAL,
                 max_tokens: Optional[int] = None,
                 temperature: Optional[float] = None) -> tuple[str, str]:
        """Route a chat completion to the best model.
        Returns (response_text, model_name_used).
        Falls back to next provider on error."""

        provider = self.get_provider(task_type)
        if provider is None:
            return "[No model providers available]", "none"

        # Build fallback chain: primary → other providers that support this task → any enabled
        providers_to_try = [provider]
        for p in sorted(self.providers, key=lambda x: x.priority):
            if p.enabled and p.name != provider.name and p not in providers_to_try:
                if task_type in p.task_types:
                    providers_to_try.append(p)
        for p in sorted(self.providers, key=lambda x: x.priority):
            if p.enabled and p not in providers_to_try:
                providers_to_try.append(p)

        for p in providers_to_try:
            try:
                start = time.monotonic()
                client = p.get_client()
                response = client.chat.completions.create(
                    model=p.model,
                    messages=messages,
                    max_tokens=max_tokens or p.max_tokens,
                    temperature=temperature if temperature is not None else p.temperature,
                )
                elapsed_ms = (time.monotonic() - start) * 1000
                reply = response.choices[0].message.content

                # Strip <think>...</think> reasoning blocks (some models expose CoT)
                if reply and "<think>" in reply:
                    import re
                    reply = re.sub(r"<think>.*?</think>\s*", "", reply, flags=re.DOTALL).strip()

                # Track stats
                self._track(p.name, elapsed_ms, success=True)
                display_name = f"{p.name}/{p.model}"
                print(f"[ROUTER] {task_type} → {display_name} ({elapsed_ms:.0f}ms)")
                return reply, display_name

            except Exception as e:
                self._track(p.name, 0, success=False)
                print(f"[ROUTER] {p.name} failed: {e}")
                if p == providers_to_try[-1]:
                    return f"[All models failed. Last error: {e}]", "error"
                print(f"[ROUTER] Falling back to next provider...")

        return "[No response generated]", "none"

    def _track(self, model_name: str, elapsed_ms: float, success: bool):
        """Track routing statistics."""
        if model_name not in self.routing_stats:
            self.routing_stats[model_name] = {
                "calls": 0, "errors": 0, "total_ms": 0.0,
            }
        stats = self.routing_stats[model_name]
        stats["calls"] += 1
        if success:
            stats["total_ms"] += elapsed_ms
        else:
            stats["errors"] += 1

    def get_stats(self) -> dict:
        """Return routing statistics for all models."""
        result = {}
        for name, stats in self.routing_stats.items():
            successful = stats["calls"] - stats["errors"]
            result[name] = {
                "calls": stats["calls"],
                "errors": stats["errors"],
                "avg_ms": round(stats["total_ms"] / successful, 1) if successful > 0 else 0,
            }
        return result

    def get_model_info(self) -> list[dict]:
        """Return info about all registered providers."""
        return [
            {
                "name": p.name,
                "model": p.model,
                "task_types": p.task_types,
                "enabled": p.enabled,
                "priority": p.priority,
            }
            for p in self.providers
        ]
