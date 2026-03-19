#!/usr/bin/env python3
"""Smoke tests for Vesper greeting fast path logic."""

GREETING_SKIP_VERBS = {"fix","deploy","run","check","update","build","restart",
                       "kill","show","list","debug","add","remove","get","set",
                       "stop","start","send","post","read","write","create","delete"}

def is_greeting(content):
    if len(content) >= 60:
        return False
    words = set(content.lower().split())
    return not (words & GREETING_SKIP_VERBS)

# Should be greetings (fast path)
assert is_greeting("Hello Vesper"),            "plain hello should be greeting"
assert is_greeting("Good morning, Vesper"),    "morning greeting"
assert is_greeting("Hey"),                     "single word"
assert is_greeting("Vesper, you there?"),      "casual check-in"

# Should NOT be greetings (go to LLM)
assert not is_greeting("Fix the hallucination bug"),   "fix = action verb"
assert not is_greeting("Deploy karma_regent"),          "deploy = action verb"
assert not is_greeting("Run the tests"),                "run = action verb"
assert not is_greeting("x" * 61),                      "too long — not a greeting"
assert not is_greeting("Check the bus for messages"),  "check = action verb"
assert not is_greeting("Debug why Vesper is silent"),  "debug = action verb"

print("ALL 10 GREETING FAST PATH TESTS PASSED")
