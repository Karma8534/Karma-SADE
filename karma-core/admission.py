"""
Memory Admission Gate — Decision #4
Threshold: 0.5 (moderate) — filters low-quality episodes before graph ingestion.
Scoring is rule-based (no LLM call) using content quality heuristics.
"""
import config


def score_episode(user_msg: str, assistant_msg: str, source: str = "") -> float:
    """Score an episode from 0.0 to 1.0 based on content quality heuristics.
    Higher = more worthy of long-term memory storage.
    No LLM call — fast, deterministic, zero-cost."""
    score = 0.0
    factors = []

    # ── Content length signals ──
    user_len = len(user_msg.strip())
    asst_len = len(assistant_msg.strip())
    if user_len < 5:
        factors.append(("too_short_user", -0.3))
    elif user_len > 50:
        factors.append(("substantive_user", 0.15))
    if user_len > 200:
        factors.append(("detailed_user", 0.1))

    if asst_len < 20:
        factors.append(("too_short_assistant", -0.2))
    elif asst_len > 100:
        factors.append(("substantive_assistant", 0.15))
    if asst_len > 500:
        factors.append(("detailed_assistant", 0.1))

    # ── Knowledge density signals ──
    combined = (user_msg + " " + assistant_msg).lower()

    # Technical content (higher value for memory)
    tech_signals = ["code", "function", "class", "docker", "config", "api",
                    "database", "deploy", "server", "error", "fix", "bug",
                    "architecture", "decision", "memory", "graph"]
    tech_hits = sum(1 for s in tech_signals if s in combined)
    if tech_hits >= 3:
        factors.append(("high_tech_density", 0.2))
    elif tech_hits >= 1:
        factors.append(("some_tech_content", 0.1))

    # Factual/declarative content
    fact_signals = ["is", "are", "was", "will", "should", "must", "because",
                    "therefore", "means", "defined as", "consists of"]
    fact_hits = sum(1 for s in fact_signals if s in combined)
    if fact_hits >= 3:
        factors.append(("factual_content", 0.1))

    # ── Noise signals (penalize) ──
    noise_patterns = ["hello", "hi", "thanks", "thank you", "ok", "okay",
                      "sure", "bye", "goodbye", "yes", "no", "hmm", "lol"]
    user_lower = user_msg.lower().strip()
    if user_lower in noise_patterns or user_len < 10:
        factors.append(("greeting_or_noise", -0.3))

    # Error responses shouldn't be memorized
    if assistant_msg.startswith("[Error") or assistant_msg.startswith("[No model"):
        factors.append(("error_response", -0.5))

    # ── Source bonus ──
    if "terminal" in source.lower():
        factors.append(("direct_interaction", 0.1))

    # ── Calculate final score ──
    base = 0.5  # Start at threshold
    for name, delta in factors:
        base += delta

    # Clamp to [0.0, 1.0]
    final = max(0.0, min(1.0, base))
    return round(final, 3)


def should_admit(user_msg: str, assistant_msg: str, source: str = "") -> tuple[bool, float]:
    """Check if an episode should be admitted to long-term memory.
    Returns (admitted: bool, score: float)."""
    s = score_episode(user_msg, assistant_msg, source)
    return s >= config.MEMORY_ADMISSION_THRESHOLD, s
