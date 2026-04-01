"""smart_router.py — Complexity-Scored Provider Routing (Sprint 3c).

Routes requests to cheapest capable provider based on message complexity.
HTTP-only — NO external SDKs. CLI is the stable interface.

Tiers:
  0: Local Ollama (K2 or P1) — trivial queries, $0
  1: CC --resume (Max subscription) — everything else, $0
  2: Future cloud providers via HTTP (placeholder)
"""
import re, time, os, json, urllib.request, urllib.error
from dataclasses import dataclass, field
from typing import Optional

# ── Provider definitions ─────────────────────────────────────────────────────

@dataclass
class Provider:
    name: str
    tier: int
    url: str  # health check URL
    model: str
    healthy: bool = True
    failures: int = 0
    cooldown_until: float = 0.0
    last_checked: float = 0.0

    MAX_FAILURES = 3
    COOLDOWN_SECS = 60.0

    def mark_failure(self):
        self.failures += 1
        if self.failures >= self.MAX_FAILURES:
            self.cooldown_until = time.time() + self.COOLDOWN_SECS
            self.healthy = False

    def mark_success(self):
        self.failures = 0
        self.healthy = True
        self.cooldown_until = 0.0

    def is_available(self) -> bool:
        if self.cooldown_until > 0 and time.time() < self.cooldown_until:
            return False
        if self.cooldown_until > 0 and time.time() >= self.cooldown_until:
            # Cooldown expired — allow retry
            self.cooldown_until = 0.0
            self.healthy = True
        return self.healthy


# ── Complexity scoring ───────────────────────────────────────────────────────

# Indicators of complex queries
MULTI_STEP_PATTERNS = [
    r'\bthen\b', r'\bafter that\b', r'\bfinally\b', r'\bnext\b',
    r'\bstep \d', r'\bphase \d', r'\bfirst\b.*\bthen\b',
    r'\banalyze\b', r'\brefactor\b', r'\barchitect\b', r'\bdesign\b',
    r'\bimplement\b', r'\bdebug\b', r'\binvestigate\b',
]

CODE_BLOCK_RE = re.compile(r'```[\s\S]*?```')
QUESTION_COMPLEXITY_WORDS = {
    'why', 'how', 'explain', 'compare', 'evaluate', 'assess',
    'trade-off', 'tradeoff', 'pros and cons', 'alternatives',
}


def score_complexity(message: str) -> float:
    """Score message complexity from 0.0 (trivial) to 1.0 (highly complex).

    Factors:
    - Message length
    - Code block count
    - Multi-step indicators
    - Question complexity words
    """
    if not message:
        return 0.0

    score = 0.0
    msg_lower = message.lower()

    # Length factor (0-0.3)
    length = len(message)
    if length < 20:
        score += 0.0
    elif length < 100:
        score += 0.1
    elif length < 500:
        score += 0.2
    else:
        score += 0.3

    # Code blocks (0-0.2)
    code_blocks = len(CODE_BLOCK_RE.findall(message))
    score += min(code_blocks * 0.1, 0.2)

    # Multi-step indicators (0-0.3)
    step_count = sum(1 for p in MULTI_STEP_PATTERNS if re.search(p, msg_lower))
    score += min(step_count * 0.1, 0.3)

    # Question complexity (0-0.2)
    complexity_words = sum(1 for w in QUESTION_COMPLEXITY_WORDS if w in msg_lower)
    score += min(complexity_words * 0.1, 0.2)

    return min(score, 1.0)


# ── SmartRouter ──────────────────────────────────────────────────────────────

class SmartRouter:
    def __init__(self):
        self.providers: list[Provider] = []
        self._init_providers()
        self._log_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "tmp", "routing_decisions.jsonl"
        )
        os.makedirs(os.path.dirname(self._log_path), exist_ok=True)

    def _init_providers(self):
        """Initialize provider list from environment or defaults."""
        # Tier 0: Local Ollama (K2 primary, P1 fallback)
        k2_url = os.environ.get("K2_OLLAMA_URL", "http://100.75.109.92:11434")
        p1_url = os.environ.get("P1_OLLAMA_URL", "http://localhost:11434")
        k2_model = os.environ.get("K2_OLLAMA_MODEL", "qwen3:8b")
        p1_model = os.environ.get("P1_OLLAMA_MODEL", "gemma3:4b")

        self.providers = [
            Provider("k2-ollama", 0, k2_url, k2_model),
            Provider("p1-ollama", 0, p1_url, p1_model),
            Provider("cc-resume", 1, "http://localhost:7891", "cc-sovereign"),
            # Tier 2: placeholder for future HTTP-based cloud providers
        ]

    def check_health(self, provider: Provider) -> bool:
        """Check if a provider is reachable."""
        now = time.time()
        # Don't re-check within 30s
        if now - provider.last_checked < 30:
            return provider.healthy

        provider.last_checked = now
        try:
            if provider.tier == 0:
                # Ollama health check
                req = urllib.request.Request(f"{provider.url}/api/tags", method="GET")
                resp = urllib.request.urlopen(req, timeout=3)
                provider.mark_success()
                return True
            elif provider.tier == 1:
                # CC server health check
                req = urllib.request.Request(f"{provider.url}/health", method="GET")
                resp = urllib.request.urlopen(req, timeout=3)
                provider.mark_success()
                return True
        except Exception:
            provider.mark_failure()
            return False
        return False

    def route(self, message: str) -> dict:
        """Route a message to the best available provider.

        Returns: {provider: str, model: str, tier: int, complexity: float, reason: str}
        """
        complexity = score_complexity(message)

        # Determine target tier
        if complexity < 0.2:
            target_tier = 0  # Try local first for trivial
        else:
            target_tier = 1  # CC for everything non-trivial

        # Try providers in target tier first, then cascade up
        for tier in range(target_tier, 3):
            for provider in self.providers:
                if provider.tier != tier:
                    continue
                if not provider.is_available():
                    continue
                if self.check_health(provider):
                    decision = {
                        "provider": provider.name,
                        "model": provider.model,
                        "tier": provider.tier,
                        "complexity": round(complexity, 3),
                        "reason": f"complexity={complexity:.2f} -> tier {tier}",
                    }
                    self._log_decision(decision, message)
                    return decision

        # Fallback: CC is always available (it's our Max subscription)
        fallback = {
            "provider": "cc-resume",
            "model": "cc-sovereign",
            "tier": 1,
            "complexity": round(complexity, 3),
            "reason": "fallback — all preferred providers unavailable",
        }
        self._log_decision(fallback, message)
        return fallback

    def _log_decision(self, decision: dict, message: str):
        """Log routing decision to JSONL."""
        try:
            entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "message_preview": message[:100],
                **decision,
            }
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

    def list_providers(self) -> list[dict]:
        """List all providers with status."""
        return [
            {
                "name": p.name, "tier": p.tier, "model": p.model,
                "healthy": p.healthy, "failures": p.failures,
                "available": p.is_available(),
            }
            for p in self.providers
        ]


# ── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    r = SmartRouter()

    # Test complexity scoring
    assert score_complexity("hi") < 0.2, f"'hi' scored {score_complexity('hi')}"
    assert score_complexity("Read MEMORY.md, analyze the architecture, then write a 500-line refactor plan with tests") > 0.3

    print(f"PASS: complexity scoring works")
    print(f"  'hi' -> {score_complexity('hi'):.3f}")
    print(f"  complex -> {score_complexity('Read MEMORY.md, analyze the architecture, then write a 500-line refactor plan with tests'):.3f}")

    # Test routing
    t = r.route("hi")
    print(f"  Simple routes to: {t['provider']} (tier {t['tier']})")
    t = r.route("Analyze the full codebase and write a migration plan")
    print(f"  Complex routes to: {t['provider']} (tier {t['tier']})")

    print(f"\nProviders: {json.dumps(r.list_providers(), indent=2)}")
