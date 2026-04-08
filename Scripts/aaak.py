"""
AAAK shorthand generator for Nexus wake-up contexts.
Lightweight, lossless-enough compression: normalize whitespace, strip vowels in non-proper tokens,
and cap output length. Designed to run locally without model calls.
"""
from __future__ import annotations

import re
from typing import Iterable, List

VOWEL_STRIP_RE = re.compile(r"(?<![A-Z])[aeiou]", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")


def normalize_chunk(text: str) -> str:
    """Normalize whitespace and lightly compress tokens."""
    if not text:
        return ""
    t = WHITESPACE_RE.sub(" ", text).strip()
    # Strip vowels on lower/Title tokens to shrink size; keep all-caps (IDs/acronyms).
    tokens: List[str] = []
    for tok in t.split(" "):
        if tok.isupper() or len(tok) <= 3:
            tokens.append(tok)
        else:
            tokens.append(VOWEL_STRIP_RE.sub("", tok))
    return " ".join(tokens)


def aaak_encode(chunks: Iterable[str], max_chars: int = 1200) -> str:
    """Encode a list of text chunks into AAAK-ish shorthand, capped to max_chars."""
    out: List[str] = []
    length = 0
    for raw in chunks:
        norm = normalize_chunk(raw)
        if not norm:
            continue
        # Prefix with bullet-ish marker for scanning
        piece = f"* {norm}"
        if length + len(piece) > max_chars:
            # Keep at least a truncated first block instead of returning an empty body.
            remaining = max_chars - length
            if remaining > 4:
                out.append(piece[:remaining])
            break
        out.append(piece)
        length += len(piece) + 1
    return "\n".join(out)


def build_wakeup_block(facts: Iterable[str], header: str = "AAAK WAKEUP") -> str:
    body = aaak_encode(facts)
    if not body:
        return header
    return f"{header}\n{body}"
