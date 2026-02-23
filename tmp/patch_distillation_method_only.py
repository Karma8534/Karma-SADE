#!/usr/bin/env python3
"""Patch consciousness.py to insert _distillation_cycle() method body only."""

path = '/opt/seed-vault/memory_v1/karma-core/consciousness.py'
src = open(path).read()

# ── Change 3: insert _distillation_cycle() method ──────────────────────
distillation_method = '''
    # ─── Graph Distillation ───────────────────────────────────────────

    async def _distillation_cycle(self):
        """Read FalkorDB graph structure, synthesize patterns/gaps via LLM,
        write schema-compliant fact to vault ledger, re-ingest key insights."""
        import time as _time
        import json as _json
        from datetime import datetime as _dt, timezone as _tz

        print("[DISTILLATION] Starting graph distillation cycle")

        try:
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
            return

        def _safe(v):
            return str(v) if v is not None else ""

        top_text = "\\n".join(
            "  - " + _safe(r[0]) + " (" + _safe(r[1]) + "): " + _safe(r[2]) + " connections"
            for r in top_rows[:15]
        ) or "  (none)"

        recent_text = "\\n".join(
            "  - " + _safe(r[0])[:200]
            for r in ep_rows[:30]
        ) or "  (none)"

        gaps_text = "\\n".join(
            "  - " + _safe(r[0]) + " (" + _safe(r[1]) + "): " + _safe(r[2]) + " connections"
            for r in gap_rows[:10]
        ) or "  (none)"

        prompt = (
            "You are Karma analyzing your own knowledge graph.\\n\\n"
            "MOST CONNECTED ENTITIES:\\n" + top_text + "\\n\\n"
            "RECENT ACTIVITY (last 7 days):\\n" + recent_text + "\\n\\n"
            "UNDEREXPLORED ENTITIES:\\n" + gaps_text + "\\n\\n"
            "Synthesize what you see. Respond in this EXACT JSON format (no markdown, no fences):\\n"
            '{"themes": ["theme1", "theme2"], "gaps": ["gap1", "gap2"], "key_insights": ["insight1", "insight2"], "summary": "2-3 sentence synthesis", "confidence": 0.0}'
        )

        if not self._router:
            print("[DISTILLATION] No router configured -- skipping")
            return

        try:
            response = await self._router.complete(
                messages=[
                    {"role": "system", "content": "You are Karma graph distillation engine. Output only valid JSON, no markdown."},
                    {"role": "user", "content": prompt}
                ],
                task_type="reasoning"
            )
            raw = response.get("content", "").strip()
            # Strip markdown fences if model adds them
            if raw.startswith("```"):
                parts = raw.split("```")
                raw = parts[1] if len(parts) > 1 else raw
                if raw.startswith("json"):
                    raw = raw[4:]
            raw = raw.strip()
            synthesis = _json.loads(raw)
        except Exception as e:
            print(f"[DISTILLATION] LLM synthesis failed: {e}")
            return

        themes = synthesis.get("themes", [])
        gaps = synthesis.get("gaps", [])
        key_insights = synthesis.get("key_insights", [])
        summary = synthesis.get("summary", "")
        confidence = float(synthesis.get("confidence", 0.5))

        print(f"[DISTILLATION] Synthesis: confidence={confidence:.2f} themes={len(themes)} gaps={len(gaps)}")

        # Write schema-compliant fact to vault ledger
        now_iso = _dt.now(_tz.utc).isoformat()
        fact_id = "distillation_" + str(int(_time.time()))
        fact = {
            "id": fact_id,
            "type": "log",
            "tags": ["karma_distillation", "graph_synthesis"],
            "content": {
                "key": "distillation_brief",
                "distillation_brief": summary,
                "themes": themes,
                "gaps": gaps,
                "key_insights": key_insights,
            },
            "source": {"kind": "tool", "ref": "karma-consciousness:distillation"},
            "confidence": confidence,
            "created_at": now_iso,
            "updated_at": now_iso,
            "verification": {
                "protocol_version": "0.1",
                "verified_at": now_iso,
                "verifier": "karma-consciousness-distillation",
                "status": "verified",
                "notes": "auto-generated graph distillation synthesis",
            },
        }

        try:
            with open(config.LEDGER_PATH, "a", encoding="utf-8") as f:
                f.write(_json.dumps(fact) + "\\n")
            print(f"[DISTILLATION] Fact written: {fact_id}")
        except Exception as e:
            print(f"[DISTILLATION] Ledger write failed: {e}")
            return

        # Re-ingest key insights as FalkorDB episodes
        if self._ingest_episode and key_insights:
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
                print(f"[DISTILLATION] Episode ingest failed: {e}")

        # SMS for high-confidence synthesis
        if self._sms_notify and confidence >= 0.8:
            try:
                import asyncio as _aio2
                loop = _aio2.get_event_loop()
                loop.create_task(self._sms_notify(
                    "Graph distillation: " + summary[:200],
                    category="self_improvement",
                    confidence=confidence
                ))
            except Exception as e:
                print(f"[DISTILLATION] SMS failed: {e}")

        self._last_distillation_time = _time.time()
        print(f"[DISTILLATION] Cycle complete. Next in {getattr(config, 'DISTILLATION_INTERVAL_HOURS', 24)}h")

'''

# Use a more specific check: look for the method definition line, not just any mention
if 'async def _distillation_cycle(self):' in src:
    print("Change 3: _distillation_cycle method already defined, skipping")
else:
    # Insert before _observe phase anchor
    insert_before = "    # \u2500\u2500\u2500 Phase 1: OBSERVE"
    if insert_before in src:
        src = src.replace(insert_before, distillation_method + insert_before, 1)
        print("Change 3: _distillation_cycle() method inserted before Phase 1 anchor")
    else:
        print("Change 3: ERROR -- anchor not found, trying fallback")
        fallback = "    def _observe(self)"
        if fallback in src:
            src = src.replace(fallback, distillation_method + "    def _observe(self)", 1)
            print("Change 3: _distillation_cycle() inserted via fallback anchor")
        else:
            print("Change 3: FAILED -- no suitable anchor found")

open(path, 'w').write(src)
print("File written.")
print("Method present:", 'async def _distillation_cycle(self):' in open(path).read())
