#!/usr/bin/env python3
"""Shared inference cascade for Regent runtime and scheduled runners."""

import json
import urllib.request
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple


Message = Dict[str, str]
LogFn = Callable[[str], None]
FallbackFn = Callable[[List[Message]], str]


@dataclass
class CascadeConfig:
    ollama_url: str
    p1_ollama_url: str
    k2_primary_model: str
    k2_fallback_model: str
    p1_model: str
    groq_url: str
    groq_model: str
    groq_api_key: str
    openrouter_url: str
    openrouter_model: str
    openrouter_api_key: str
    openrouter_headers: Dict[str, str] = field(default_factory=dict)
    zai_url: str = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    zai_model: str = "glm-4-plus"
    zai_api_key: str = ""


def _log(log_fn: Optional[LogFn], message: str) -> None:
    if log_fn:
        log_fn(message)


def _call_ollama(
    messages: List[Message],
    base_url: str,
    model: str,
    timeout: int = 25,
    system_prompt: Optional[str] = None,
    log_fn: Optional[LogFn] = None,
) -> Optional[str]:
    full_messages = list(messages)
    if system_prompt:
        full_messages = [{"role": "system", "content": system_prompt}] + full_messages
    payload = json.dumps(
        {
            "model": model,
            "messages": full_messages,
            "stream": False,
            "options": {"num_predict": 1024},
        }
    ).encode()
    req = urllib.request.Request(
        f"{base_url}/api/chat",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read())
        return body.get("message", {}).get("content", "").strip() or None
    except Exception as exc:
        _log(log_fn, f"ollama({base_url}) error: {exc}")
        return None


def _call_openai_compat(
    messages: List[Message],
    url: str,
    model: str,
    api_key: str,
    timeout: int = 30,
    system_prompt: Optional[str] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    log_fn: Optional[LogFn] = None,
) -> Optional[str]:
    full_messages = list(messages)
    if system_prompt:
        full_messages = [{"role": "system", "content": system_prompt}] + full_messages
    payload = json.dumps(
        {"model": model, "messages": full_messages, "max_tokens": 1024}
    ).encode()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = json.loads(response.read())
        return body["choices"][0]["message"]["content"].strip() or None
    except Exception as exc:
        _log(log_fn, f"openai_compat({url}) error: {exc}")
        return None


def call_with_local_first(
    messages: List[Message],
    system_prompt: str,
    config: CascadeConfig,
    fallback_fn: Optional[FallbackFn] = None,
    fallback_label: str = "claude",
    log_fn: Optional[LogFn] = None,
) -> Tuple[Optional[str], str]:
    """Cascade: K2 -> P1 -> z.ai -> Groq -> OpenRouter -> fallback (Claude)."""
    tried_models = set()
    for local_model in (config.k2_primary_model, config.k2_fallback_model):
        if not local_model or local_model in tried_models:
            continue
        tried_models.add(local_model)
        response = _call_ollama(
            messages=messages,
            base_url=config.ollama_url,
            model=local_model,
            timeout=25,
            system_prompt=system_prompt,
            log_fn=log_fn,
        )
        if response:
            _log(log_fn, f"response: K2 {local_model} ({len(response)} chars)")
            return response, "k2_ollama"

    # Tier 2: P1 local Ollama (free, zero cloud cost — before any cloud tier)
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
            return response, "openrouter"

    if fallback_fn:
        _log(log_fn, f"escalating to {fallback_label}: all other tiers failed")
        return fallback_fn(messages), fallback_label
    _log(log_fn, "all cascade tiers failed (no fallback)")
    return None, "none"
