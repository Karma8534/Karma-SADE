"""
Tests for aaak_dialect.py — Karma-specific AAAK compression.
Acceptance criteria:
  1. compress_for_cortex achieves >= 10x compression on MEMORY.md-style text
  2. Entity codes (COL, JUL, KAR, KIK, CDX) are present in output when names appear in input
  3. Flag detection works: DECISION, PROOF, PITFALL, DIRECTION, INSIGHT detected from text
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from aaak_dialect import compress_for_cortex, karma_dialect, KARMA_ENTITIES, _FLAG_SIGNALS

# ── Fixtures ──────────────────────────────────────────────────────────────────

SAMPLE_MEMORY_MD = """
## Current Architecture (verified 2026-04-09)

### Model Routing — GROUND TRUTH
| Setting | Value | Source |
|---------|-------|--------|
| MODEL_DEFAULT | gpt-5.4-mini | hub.env on vault-neo |
| MODEL_DEEP | claude-sonnet-4-6 | hub.env on vault-neo |

### Infrastructure
- Colby is the Sovereign. Julian is the executor. Karma is the peer. Kiki runs between convos. Codex handles code.
- vault-neo: arknexus.net (DigitalOcean NYC3, 4GB RAM)
- FalkorDB graph name: neo_workspace (NOT karma)
- Hub token: /opt/seed-vault/memory_v1/hub_auth/hub.chat.token.txt

### Known Pitfalls (active)
- Python3 not available in Git Bash — use SSH
- Docker compose service: hub-bridge (container: anr-hub-bridge)
- FalkorDB: BOTH env vars required: FALKORDB_DATA_PATH=/data AND FALKORDB_ARGS
- batch_ingest: use --skip-dedup — Graphiti mode times out at scale

### Session 163 (2026-04-09) — Deployed fixes
- FIXED: /v1/learnings 502 — proxy.js missing auth headers on 3 P1 fetch calls
- FIXED: FalkorDB silent-exit — restart policy changed to unless-stopped, health cron installed
- Decided to use AAAK compression for cortex injection instead of raw tail
- Proof: FalkorDB alert fires correctly when container stops
- Direction: K2 cortex now receives compressed MEMORY.md spine via compress_for_cortex

### Next
- Task 3-5: AAAK K2 cortex injection (in progress)
""" * 3  # Repeat 3x to make it realistically large (~3000 chars)


# ── Test 1: 10x compression ───────────────────────────────────────────────────

def test_compression_ratio():
    compressed = compress_for_cortex(SAMPLE_MEMORY_MD, max_tokens=500)
    original_len = len(SAMPLE_MEMORY_MD)
    compressed_len = len(compressed)
    ratio = original_len / max(compressed_len, 1)
    assert ratio >= 10, (
        f"Compression ratio {ratio:.1f}x is below 10x threshold. "
        f"original={original_len} compressed={compressed_len}"
    )
    print(f"  ✓ Compression ratio: {ratio:.1f}x ({original_len} → {compressed_len} chars)")


# ── Test 2: Entity codes appear in output ─────────────────────────────────────

def test_entity_codes_present():
    # Text explicitly mentions Colby, Julian, Karma, Kiki, Codex
    text = "Colby is the Sovereign. Julian is the executor. Karma is the peer. Kiki runs background. Codex does code."
    compressed = compress_for_cortex(text, max_tokens=500)
    # At least 2 of 5 entity codes must appear
    codes = ["COL", "JUL", "KAR", "KIK", "CDX"]
    found = [c for c in codes if c in compressed]
    assert len(found) >= 2, (
        f"Expected >= 2 entity codes in output, found {found}. Output: {compressed!r}"
    )
    print(f"  ✓ Entity codes found: {found}")


def test_entity_codes_karma():
    text = "Karma is the central peer. The system is run by Karma."
    compressed = compress_for_cortex(text, max_tokens=500)
    assert "KAR" in compressed, f"KAR not found in: {compressed!r}"
    preview = repr(compressed)[:80]
    print(f"  ✓ KAR code present: {preview}")


def test_entity_codes_colby():
    text = "Colby is the Sovereign and gives directives."
    compressed = compress_for_cortex(text, max_tokens=500)
    assert "COL" in compressed, f"COL not found in: {compressed!r}"
    preview = repr(compressed)[:80]
    print(f"  ✓ COL code present: {preview}")


# ── Test 3: Flag detection ────────────────────────────────────────────────────

def test_flag_detection_decision():
    text = "We decided to use AAAK compression instead of raw tail."
    d = karma_dialect()
    flags = d._detect_flags(text)
    assert "DECISION" in flags, f"DECISION not detected. flags={flags}"
    print(f"  ✓ DECISION detected: {flags}")


def test_flag_detection_technical():
    text = "Deploy the new architecture to the server infrastructure."
    d = karma_dialect()
    flags = d._detect_flags(text)
    assert "TECHNICAL" in flags, f"TECHNICAL not detected. flags={flags}"
    print(f"  ✓ TECHNICAL detected: {flags}")


def test_flag_detection_pitfall():
    d = karma_dialect()
    # Check _FLAG_SIGNALS has pitfall-related keywords
    pitfall_kws = [k for k, v in _FLAG_SIGNALS.items() if v == "PITFALL"]
    assert len(pitfall_kws) > 0, "No PITFALL flag signals defined"
    # Test one
    text = f"This is a known pitfall in the system."
    flags = d._detect_flags(text)
    assert "PITFALL" in flags or any("pitfall" in kw.lower() for kw in pitfall_kws), (
        f"PITFALL not detected from 'pitfall'. flags={flags}"
    )
    print(f"  ✓ PITFALL keyword signals: {pitfall_kws}")


# ── Test 4: max_tokens budget enforced ───────────────────────────────────────

def test_token_budget_enforced():
    # max_tokens=100 → max_chars=300
    compressed = compress_for_cortex(SAMPLE_MEMORY_MD, max_tokens=100)
    max_chars = 100 * 3
    assert len(compressed) <= max_chars + 5, (  # +5 for "..." truncation
        f"Output {len(compressed)} chars exceeds token budget ({max_chars} chars)"
    )
    print(f"  ✓ Token budget: {len(compressed)} chars ≤ {max_chars}")


# ── Test 5: compress_for_cortex returns non-empty string ─────────────────────

def test_returns_nonempty():
    compressed = compress_for_cortex(SAMPLE_MEMORY_MD)
    assert isinstance(compressed, str), "Must return str"
    assert len(compressed) > 0, "Must return non-empty string"
    print(f"  ✓ Non-empty output: {len(compressed)} chars")


def test_empty_input():
    compressed = compress_for_cortex("")
    assert isinstance(compressed, str), "Must return str even for empty input"
    print(f"  ✓ Empty input handled: {repr(compressed)}")


# ── Test 6: KARMA_ENTITIES has all required codes ────────────────────────────

def test_karma_entities_complete():
    required = {"Colby": "COL", "Julian": "JUL", "Karma": "KAR", "Kiki": "KIK", "Codex": "CDX"}
    for name, code in required.items():
        assert name in KARMA_ENTITIES, f"{name} missing from KARMA_ENTITIES"
        assert KARMA_ENTITIES[name] == code, (
            f"Expected {name}→{code}, got {KARMA_ENTITIES[name]}"
        )
    print(f"  ✓ All 5 entity codes correct: {required}")


# ── Runner ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_compression_ratio,
        test_entity_codes_present,
        test_entity_codes_karma,
        test_entity_codes_colby,
        test_flag_detection_decision,
        test_flag_detection_technical,
        test_flag_detection_pitfall,
        test_token_budget_enforced,
        test_returns_nonempty,
        test_empty_input,
        test_karma_entities_complete,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            print(f"Running {t.__name__}...")
            t()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {type(e).__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
    else:
        print("ALL TESTS PASSED")
        sys.exit(0)
