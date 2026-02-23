"""
Patch script for consciousness.py _distillation_cycle() fixes:

Fix 1 — Separate FalkorDB query exception handlers (3 individual try/except)
Fix 2 — Replace asyncio.get_event_loop() with asyncio.get_running_loop()
         and remove redundant inline 'import asyncio as _aio' / '_aio2'
Fix 4 — Add random suffix to fact_id
"""
import sys

FILEPATH = "/opt/seed-vault/memory_v1/karma-core/consciousness.py"

with open(FILEPATH, "r", encoding="utf-8") as f:
    src = f.read()

original = src  # keep for diff reporting

# ─── Fix 1: Separate FalkorDB query handlers ──────────────────────────────
# Replace the single monolithic try/except block that wraps all three queries
# with three individual try/except blocks.

OLD_FALKOR_BLOCK = '''        try:
            falkor = self._get_falkor()
            group_id = config.GRAPHITI_GROUP_ID

            # Query 1: Top entities by relationship count
            top_q = (
                "MATCH (e:Entity) "
                "OPTIONAL MATCH (e)-[r]-() "
                "RETURN e.name, e.entity_type, count(r) AS rel_count "
                "ORDER BY rel_count DESC "
                "LIMIT 15"
            )
            top_result = falkor.execute_command("GRAPH.QUERY", group_id, top_q)
            top_rows = top_result[1] if len(top_result) >= 2 and top_result[1] else []

            # Query 2: Recent episodes (last 7 days)
            seven_days_ago = _time.time() - (7 * 24 * 3600)
            max_ep = getattr(config, 'DISTILLATION_MAX_EPISODES', 200)
            ep_q = (
                "MATCH (ep:Episodic) "
                "WHERE ep.created_at > " + str(seven_days_ago) + " "
                "RETURN ep.content, ep.created_at "
                "ORDER BY ep.created_at DESC "
                "LIMIT " + str(max_ep)
            )
            ep_result = falkor.execute_command("GRAPH.QUERY", group_id, ep_q)
            ep_rows = ep_result[1] if len(ep_result) >= 2 and ep_result[1] else []

            # Query 3: Low-connection entities (gaps)
            gap_q = (
                "MATCH (e:Entity) "
                "OPTIONAL MATCH (e)-[r]-() "
                "WITH e, count(r) AS rel_count "
                "WHERE rel_count <= 2 "
                "RETURN e.name, e.entity_type, rel_count "
                "ORDER BY rel_count ASC "
                "LIMIT 10"
            )
            gap_result = falkor.execute_command("GRAPH.QUERY", group_id, gap_q)
            gap_rows = gap_result[1] if len(gap_result) >= 2 and gap_result[1] else []

        except Exception as e:
            print(f"[DISTILLATION] FalkorDB query failed: {e}")
            return'''

NEW_FALKOR_BLOCK = '''        falkor = self._get_falkor()
        group_id = config.GRAPHITI_GROUP_ID

        # Query 1: Top entities by relationship count
        try:
            top_q = (
                "MATCH (e:Entity) "
                "OPTIONAL MATCH (e)-[r]-() "
                "RETURN e.name, e.entity_type, count(r) AS rel_count "
                "ORDER BY rel_count DESC "
                "LIMIT 15"
            )
            top_result = falkor.execute_command("GRAPH.QUERY", group_id, top_q)
            top_rows = top_result[1] if len(top_result) >= 2 and top_result[1] else []
        except Exception as e:
            print(f"[DISTILLATION] Query 1 (top entities) failed: {e}")
            top_rows = []

        # Query 2: Recent episodes (last 7 days)
        try:
            seven_days_ago = _time.time() - (7 * 24 * 3600)
            max_ep = getattr(config, 'DISTILLATION_MAX_EPISODES', 200)
            ep_q = (
                "MATCH (ep:Episodic) "
                "WHERE ep.created_at > " + str(seven_days_ago) + " "
                "RETURN ep.content, ep.created_at "
                "ORDER BY ep.created_at DESC "
                "LIMIT " + str(max_ep)
            )
            ep_result = falkor.execute_command("GRAPH.QUERY", group_id, ep_q)
            ep_rows = ep_result[1] if len(ep_result) >= 2 and ep_result[1] else []
        except Exception as e:
            print(f"[DISTILLATION] Query 2 (recent episodes) failed: {e}")
            ep_rows = []

        # Query 3: Low-connection entities (gaps)
        try:
            gap_q = (
                "MATCH (e:Entity) "
                "OPTIONAL MATCH (e)-[r]-() "
                "WITH e, count(r) AS rel_count "
                "WHERE rel_count <= 2 "
                "RETURN e.name, e.entity_type, rel_count "
                "ORDER BY rel_count ASC "
                "LIMIT 10"
            )
            gap_result = falkor.execute_command("GRAPH.QUERY", group_id, gap_q)
            gap_rows = gap_result[1] if len(gap_result) >= 2 and gap_result[1] else []
        except Exception as e:
            print(f"[DISTILLATION] Query 3 (gap entities) failed: {e}")
            gap_rows = []'''

if OLD_FALKOR_BLOCK in src:
    src = src.replace(OLD_FALKOR_BLOCK, NEW_FALKOR_BLOCK, 1)
    print("[PATCH] Fix 1 applied: separated FalkorDB query handlers")
else:
    print("[ERROR] Fix 1: OLD_FALKOR_BLOCK not found — check indentation/content")
    sys.exit(1)

# ─── Fix 2a: Replace loop.create_task for episode ingest ──────────────────
OLD_INGEST_BLOCK = '''        if self._ingest_episode and key_insights:
            import asyncio as _aio
            try:
                loop = _aio.get_event_loop()
                for insight in key_insights[:5]:
                    loop.create_task(self._ingest_episode(
                        "[karma-distillation] " + insight,
                        "Karma graph distillation insight",
                        source="karma-distillation"
                    ))
            except Exception as e:
                print(f"[DISTILLATION] Episode ingest failed: {e}")'''

NEW_INGEST_BLOCK = '''        if self._ingest_episode and key_insights:
            try:
                for insight in key_insights[:5]:
                    asyncio.get_running_loop().create_task(self._ingest_episode(
                        "[karma-distillation] " + insight,
                        "Karma graph distillation insight",
                        source="karma-distillation"
                    ))
            except Exception as e:
                print(f"[DISTILLATION] Episode ingest failed: {e}")'''

if OLD_INGEST_BLOCK in src:
    src = src.replace(OLD_INGEST_BLOCK, NEW_INGEST_BLOCK, 1)
    print("[PATCH] Fix 2a applied: replaced get_event_loop() for episode ingest")
else:
    print("[ERROR] Fix 2a: OLD_INGEST_BLOCK not found — check indentation/content")
    sys.exit(1)

# ─── Fix 2b: Replace loop.create_task for SMS notify ─────────────────────
OLD_SMS_BLOCK = '''        if self._sms_notify and confidence >= 0.8:
            try:
                import asyncio as _aio2
                loop = _aio2.get_event_loop()
                loop.create_task(self._sms_notify(
                    "Graph distillation: " + summary[:200],
                    category="self_improvement",
                    confidence=confidence
                ))
            except Exception as e:
                print(f"[DISTILLATION] SMS failed: {e}")'''

NEW_SMS_BLOCK = '''        if self._sms_notify and confidence >= 0.8:
            try:
                asyncio.get_running_loop().create_task(self._sms_notify(
                    "Graph distillation: " + summary[:200],
                    category="self_improvement",
                    confidence=confidence
                ))
            except Exception as e:
                print(f"[DISTILLATION] SMS failed: {e}")'''

if OLD_SMS_BLOCK in src:
    src = src.replace(OLD_SMS_BLOCK, NEW_SMS_BLOCK, 1)
    print("[PATCH] Fix 2b applied: replaced get_event_loop() for SMS notify")
else:
    print("[ERROR] Fix 2b: OLD_SMS_BLOCK not found — check indentation/content")
    sys.exit(1)

# ─── Fix 4: Add random suffix to fact_id ─────────────────────────────────
OLD_FACTID = '        fact_id = "distillation_" + str(int(_time.time()))'
NEW_FACTID = ('        import random as _random\n'
              '        fact_id = "distillation_" + str(int(_time.time())) + "_" + str(_random.randint(1000, 9999))')

if OLD_FACTID in src:
    src = src.replace(OLD_FACTID, NEW_FACTID, 1)
    print("[PATCH] Fix 4 applied: added random suffix to fact_id")
else:
    print("[ERROR] Fix 4: OLD_FACTID not found — check content")
    sys.exit(1)

# ─── Write patched file ───────────────────────────────────────────────────
with open(FILEPATH, "w", encoding="utf-8") as f:
    f.write(src)

print(f"[PATCH] All fixes written to {FILEPATH}")
print(f"[PATCH] Original size: {len(original)} chars, Patched size: {len(src)} chars")
