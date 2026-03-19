#!/usr/bin/env python3
"""Patch regent_inference.py: reorder cascade K2 -> P1 -> z.ai -> Groq -> OpenRouter -> Claude.
TDD GREEN: makes test_cascade_order.py pass.
"""
import ast, sys
from pathlib import Path

TARGET = Path("/mnt/c/dev/Karma/k2/Aria/regent_inference.py")

OLD_CASCADE = '''    if config.groq_api_key:
        response = _call_openai_compat(
            messages=messages,
            url=config.groq_url,
            model=config.groq_model,
            api_key=config.groq_api_key,
            timeout=30,
            system_prompt=system_prompt,
            log_fn=log_fn,
        )
        if response:
            _log(log_fn, f"response: Groq {config.groq_model} ({len(response)} chars)")
            return response, "groq"

    if config.openrouter_api_key:
        response = _call_openai_compat(
            messages=messages,
            url=config.openrouter_url,
            model=config.openrouter_model,
            api_key=config.openrouter_api_key,
            timeout=30,
            system_prompt=system_prompt,
            extra_headers=config.openrouter_headers,
            log_fn=log_fn,
        )
        if response:
            _log(
                log_fn,
                f"response: OpenRouter {config.openrouter_model} ({len(response)} chars)",
            )
            return response, "openrouter"

    if config.zai_api_key:
        response = _call_openai_compat(
            messages=messages,
            url=config.zai_url,
            model=config.zai_model,
            api_key=config.zai_api_key,
            timeout=30,
            system_prompt=system_prompt,
            log_fn=log_fn,
        )
        if response:
            _log(log_fn, f"response: z.ai {config.zai_model} ({len(response)} chars)")
            return response, "zai"

    response = _call_ollama(
        messages=messages,
        base_url=config.p1_ollama_url,
        model=config.p1_model,
        timeout=30,
        system_prompt=system_prompt,
        log_fn=log_fn,
    )
    if response:
        _log(log_fn, f"response: P1 {config.p1_model} ({len(response)} chars)")
        return response, "p1_ollama"'''

NEW_CASCADE = '''    # Tier 2: P1 local Ollama (free, zero cloud cost — before any cloud tier)
    response = _call_ollama(
        messages=messages,
        base_url=config.p1_ollama_url,
        model=config.p1_model,
        timeout=30,
        system_prompt=system_prompt,
        log_fn=log_fn,
    )
    if response:
        _log(log_fn, f"response: P1 {config.p1_model} ({len(response)} chars)")
        return response, "p1_ollama"

    # Tier 3: z.ai (cheapest cloud — before rate-limited paid APIs)
    if config.zai_api_key:
        response = _call_openai_compat(
            messages=messages,
            url=config.zai_url,
            model=config.zai_model,
            api_key=config.zai_api_key,
            timeout=30,
            system_prompt=system_prompt,
            log_fn=log_fn,
        )
        if response:
            _log(log_fn, f"response: z.ai {config.zai_model} ({len(response)} chars)")
            return response, "zai"

    # Tier 4: Groq
    if config.groq_api_key:
        response = _call_openai_compat(
            messages=messages,
            url=config.groq_url,
            model=config.groq_model,
            api_key=config.groq_api_key,
            timeout=30,
            system_prompt=system_prompt,
            log_fn=log_fn,
        )
        if response:
            _log(log_fn, f"response: Groq {config.groq_model} ({len(response)} chars)")
            return response, "groq"

    # Tier 5: OpenRouter
    if config.openrouter_api_key:
        response = _call_openai_compat(
            messages=messages,
            url=config.openrouter_url,
            model=config.openrouter_model,
            api_key=config.openrouter_api_key,
            timeout=30,
            system_prompt=system_prompt,
            extra_headers=config.openrouter_headers,
            log_fn=log_fn,
        )
        if response:
            _log(
                log_fn,
                f"response: OpenRouter {config.openrouter_model} ({len(response)} chars)",
            )
            return response, "openrouter"'''

OLD_DOCSTRING = '"""Cascade: K2 local models -> Groq -> OpenRouter -> z.ai -> P1 Ollama -> fallback."""'
NEW_DOCSTRING = '"""Cascade: K2 -> P1 -> z.ai -> Groq -> OpenRouter -> fallback (Claude)."""'

src = TARGET.read_text(encoding="utf-8")

if OLD_CASCADE not in src:
    print("FAIL: cascade block marker not found — already patched or source changed")
    sys.exit(1)

patched = src.replace(OLD_DOCSTRING, NEW_DOCSTRING, 1).replace(OLD_CASCADE, NEW_CASCADE, 1)

try:
    ast.parse(patched)
except SyntaxError as e:
    print(f"FAIL: syntax error after patch: {e}")
    sys.exit(1)

TARGET.write_text(patched, encoding="utf-8")
print("OK   regent_inference.py cascade reordered: K2 -> P1 -> z.ai -> Groq -> OpenRouter -> Claude")
