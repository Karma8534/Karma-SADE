#!/usr/bin/env python3
"""TDD: Verify cascade order is K2 -> P1 -> z.ai -> Groq/OpenRouter -> Claude.

RED: fails against current order (K2 -> Groq -> OpenRouter -> z.ai -> P1 -> Claude).
GREEN: passes after reorder in regent_inference.py.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "k2" / "Aria"))

import unittest
from unittest.mock import patch
import regent_inference
from regent_inference import CascadeConfig, call_with_local_first


def _cfg():
    return CascadeConfig(
        ollama_url="http://k2:11434",
        p1_ollama_url="http://p1:11434",
        k2_primary_model="k2model",
        k2_fallback_model="",
        p1_model="p1model",
        groq_url="https://groq.example",
        groq_model="groq-m",
        groq_api_key="groq-key",
        openrouter_url="https://openrouter.example",
        openrouter_model="or-m",
        openrouter_api_key="or-key",
        zai_url="https://bigmodel.example",
        zai_model="zai-m",
        zai_api_key="zai-key",
    )


class TestCascadeOrder(unittest.TestCase):

    def test_p1_tried_before_zai_when_k2_fails(self):
        """K2 fails → P1 must be attempted before z.ai (or any cloud tier)."""
        call_log = []

        def fake_ollama(messages, base_url, model, **kwargs):
            call_log.append(("ollama", base_url))
            return "p1-response" if "p1" in base_url else None  # K2 fails, P1 succeeds

        def fake_openai(messages, url, model, api_key, **kwargs):
            call_log.append(("cloud", url))
            return None  # cloud should not be reached

        with patch.object(regent_inference, "_call_ollama", side_effect=fake_ollama), \
             patch.object(regent_inference, "_call_openai_compat", side_effect=fake_openai):
            result, source = call_with_local_first(
                messages=[{"role": "user", "content": "hello"}],
                system_prompt="sys",
                config=_cfg(),
            )

        self.assertEqual(source, "p1_ollama", f"Expected p1_ollama, got {source!r}")
        self.assertEqual(result, "p1-response")
        cloud_calls = [c for c in call_log if c[0] == "cloud"]
        self.assertEqual(cloud_calls, [], "Cloud should not be reached when P1 succeeds")

    def test_zai_tried_before_groq_when_k2_and_p1_fail(self):
        """K2 fails, P1 fails → z.ai must be tried before Groq."""
        call_log = []

        def fake_ollama(messages, base_url, model, **kwargs):
            call_log.append(("ollama", base_url))
            return None  # both K2 and P1 fail

        def fake_openai(messages, url, model, api_key, **kwargs):
            call_log.append(("cloud", url))
            return "zai-response" if "bigmodel" in url else None

        with patch.object(regent_inference, "_call_ollama", side_effect=fake_ollama), \
             patch.object(regent_inference, "_call_openai_compat", side_effect=fake_openai):
            result, source = call_with_local_first(
                messages=[{"role": "user", "content": "hello"}],
                system_prompt="sys",
                config=_cfg(),
            )

        self.assertEqual(source, "zai", f"Expected zai, got {source!r}")
        cloud_urls = [c[1] for c in call_log if c[0] == "cloud"]
        self.assertTrue(cloud_urls, "No cloud tier was called")
        zai_idx = next((i for i, u in enumerate(cloud_urls) if "bigmodel" in u), None)
        groq_idx = next((i for i, u in enumerate(cloud_urls) if "groq" in u), None)
        self.assertIsNotNone(zai_idx, "z.ai was never called")
        if groq_idx is not None:
            self.assertLess(zai_idx, groq_idx, "z.ai must be called before Groq")

    def test_full_cascade_falls_through_to_claude(self):
        """All local + cloud tiers fail → fallback_fn (Claude) is invoked."""
        with patch.object(regent_inference, "_call_ollama", return_value=None), \
             patch.object(regent_inference, "_call_openai_compat", return_value=None):
            result, source = call_with_local_first(
                messages=[{"role": "user", "content": "hello"}],
                system_prompt="sys",
                config=_cfg(),
                fallback_fn=lambda msgs: "claude-response",
            )

        self.assertEqual(source, "claude")
        self.assertEqual(result, "claude-response")


if __name__ == "__main__":
    unittest.main(verbosity=2)
