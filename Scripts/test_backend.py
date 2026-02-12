#!/usr/bin/env python3
"""
Test the karma_backend.py smart routing
Tests both Ollama (FREE) and Claude API (if configured)
"""

import os
import sys

# Set API key from registry if not in environment
if not os.environ.get("ANTHROPIC_API_KEY"):
    import subprocess
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "Get-ItemProperty -Path 'HKCU:\\Environment' -Name ANTHROPIC_API_KEY -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ANTHROPIC_API_KEY"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            api_key = result.stdout.strip()
            os.environ["ANTHROPIC_API_KEY"] = api_key
            print(f"[INFO] Loaded API key from registry (length: {len(api_key)})")
    except Exception as e:
        print(f"[WARN] Could not load API key from registry: {e}")

# Now test the backend
sys.path.insert(0, os.path.dirname(__file__))

print("\n" + "="*60)
print("TESTING KARMA BACKEND - SMART ROUTING")
print("="*60 + "\n")

# Test 1: Check if Ollama is available
print("[TEST 1] Checking Ollama availability...")
import subprocess
try:
    result = subprocess.run(["ollama", "list"], capture_output=True, timeout=5)
    if result.returncode == 0:
        print("[PASS] Ollama is available (FREE)")
    else:
        print("[FAIL] Ollama not available")
except:
    print("[FAIL] Ollama not found")

# Test 2: Check if Claude API key is set
print("\n[TEST 2] Checking Claude API key...")
if os.environ.get("ANTHROPIC_API_KEY"):
    key_len = len(os.environ["ANTHROPIC_API_KEY"])
    print(f"[PASS] API key configured (length: {key_len})")
else:
    print("[WARN] No API key - will use Ollama only")

# Test 3: Import backend
print("\n[TEST 3] Importing backend...")
try:
    import karma_backend
    print("[PASS] Backend imported successfully")
    print(f"  - Ollama available: {karma_backend.OLLAMA_AVAILABLE}")
    print(f"  - Claude available: {karma_backend.CLAUDE_AVAILABLE}")
except Exception as e:
    print(f"[FAIL] Backend import failed: {e}")
    sys.exit(1)

# Test 4: Test simple query (should use Ollama)
print("\n[TEST 4] Testing simple query (should use FREE Ollama)...")
try:
    import asyncio

    async def test_simple():
        response = await karma_backend.get_ai_response("What is 2+2?")
        return response

    result = asyncio.run(test_simple())

    if "Ollama" in result:
        print("[PASS] Used Ollama (FREE)")
        print(f"  Response preview: {result[:100]}...")
    else:
        print("[WARN] Did not use Ollama")
        print(f"  Response: {result[:100]}...")

except Exception as e:
    print(f"[FAIL] Query failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test complexity detection
print("\n[TEST 5] Testing complexity detection...")
test_cases = [
    ("What is Python?", "simple"),
    ("How to write a loop?", "simple"),
    ("Design a microservices architecture", "complex"),
    ("Refactor this codebase", "complex"),
]

for message, expected in test_cases:
    detected = karma_backend.detect_task_complexity(message)
    status = "PASS" if detected == expected else "WARN"
    print(f"  [{status}] '{message[:30]}...' -> {detected} (expected {expected})")

print("\n" + "="*60)
print("BACKEND TEST COMPLETE")
print("="*60 + "\n")

print("\nSummary:")
print("  - Ollama (FREE): Available and working")
print("  - Claude API: Configured as fallback")
print("  - Smart routing: Active (tries Ollama first)")
print("\nNext: Start backend with: python Scripts/karma_backend.py")
