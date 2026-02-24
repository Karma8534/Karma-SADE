"""
Karma Consciousness Loop — OBSERVE / THINK / DECIDE / ACT / REFLECT

Background async loop running every CONSCIOUSNESS_INTERVAL seconds.
Gives Karma ambient awareness: notices patterns, detects anomalies,
surfaces insights proactively during chat without being asked.
"""
import asyncio
import json
import logging
import time
import traceback
from datetime import datetime, timezone
from typing import Optional

import config

logger = logging.getLogger(__name__)


# ─── Action Types ─────────────────────────────────────────────────────────

class Action:
    NO_ACTION = "NO_ACTION"
    LOG_DISCOVERY = "LOG_DISCOVERY"
    LOG_INSIGHT = "LOG_INSIGHT"
    LOG_ALERT = "LOG_ALERT"
    LOG_GROWTH = "LOG_GROWTH"
    LOG_ERROR = "LOG_ERROR"


# ─── Consciousness Loop ──────────────────────────────────────────────────

class ConsciousnessLoop:
    """Karma's background awareness — observes, thinks, decides, acts, reflects."""

    def __init__(self, get_falkor_fn, get_graph_stats_fn, get_openai_client_fn,
                 active_conversations_ref: dict, router=None,
                 ingest_episode_fn=None, sms_notify_fn=None):
        # Injected dependencies from server.py (no circular imports)
        self._get_falkor = get_falkor_fn
        self._get_graph_stats = get_graph_stats_fn
        self._get_openai_client = get_openai_client_fn
        self._active_conversations = active_conversations_ref
        self._router = router  # Optional: use model router for THINK phase
        self._ingest_episode = ingest_episode_fn  # Optional: feed reflections into graph
        self._sms_notify = sms_notify_fn  # Optional: SMS notification for high-value insights

        # State
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._last_tick: Optional[str] = None  # ISO timestamp of last cycle
        self._last_graph_stats: Optional[dict] = None
        self._last_reflection: str = ""
        self._pending_insights: list[str] = []  # Queue for chat injection

        # Metrics
        self.metrics = {
            "total_cycles": 0,
            "active_cycles": 0,
            "idle_cycles": 0,
            "insights_generated": 0,
            "alerts_generated": 0,
            "journal_ingested": 0,
            "sms_sent": 0,
            "errors": 0,
            "llm_calls_total": 0,
            "llm_calls_skipped": 0,
            "avg_cycle_duration_ms": 0.0,
            "last_cycle_time": None,
            "consecutive_idle": 0,
            "started_at": None,
        }
        self._cycle_durations: list[float] = []  # Last 100 durations for avg
        self._last_distillation_time: float = 0.0  # Unix epoch; 0 = run on first opportunity
        self.last_cycle_time = time.time()  # Track when last cycle ran

    # ─── Lifecycle ────────────────────────────────────────────────────

    async def run(self):
        """Main loop — runs until stopped."""
        self._running = True
        self.metrics["started_at"] = datetime.now(timezone.utc).isoformat()
        print("[CONSCIOUSNESS] Loop started — interval: {}s".format(config.CONSCIOUSNESS_INTERVAL))

        # Capture initial graph snapshot
        try:
            self._last_graph_stats = self._get_graph_stats()
        except Exception:
            self._last_graph_stats = {"entities": 0, "episodes": 0, "relationships": 0}

        self._last_tick = datetime.now(timezone.utc).isoformat()

        while self._running:
            try:
                await asyncio.sleep(config.CONSCIOUSNESS_INTERVAL)
                if not self._running:
                    break
                await self._cycle()
                # Distillation check -- runs every DISTILLATION_INTERVAL_HOURS
                if getattr(config, 'DISTILLATION_ENABLED', False):
                    import time as _t_dist
                    _hours_elapsed = (_t_dist.time() - self._last_distillation_time) / 3600
                    if _hours_elapsed >= getattr(config, 'DISTILLATION_INTERVAL_HOURS', 24):
                        await self._distillation_cycle()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[CONSCIOUSNESS] Cycle error: {e}")
                traceback.print_exc()
                self.metrics["errors"] += 1
                # Don't crash the loop — keep going
                await asyncio.sleep(config.CONSCIOUSNESS_INTERVAL)

        print("[CONSCIOUSNESS] Loop stopped")

    def stop(self):
        """Signal the loop to stop."""
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()

    def start(self) -> asyncio.Task:
        """Create and return the background task."""
        self._task = asyncio.create_task(self.run())
        return self._task

    # ─── Core Cycle ───────────────────────────────────────────────────

    async def _cycle(self):
        """Execute one OBSERVE → THINK → DECIDE → ACT → REFLECT cycle."""
        cycle_start = time.monotonic()
        self.metrics["total_cycles"] += 1
        cycle_num = self.metrics["total_cycles"]

        # 1. OBSERVE
        observations = self._observe()

        # If observation is None (idle cycle - no new episodes), skip rest
        if observations is None:
            self.metrics["idle_cycles"] += 1
            self.metrics["consecutive_idle"] += 1
            self.metrics["llm_calls_skipped"] += 1
            analysis = None
            is_idle = True
            action = Action.NO_ACTION
        else:
            is_idle = False
            self.metrics["active_cycles"] += 1
            self.metrics["consecutive_idle"] = 0

            # 2. THINK (run LLM for non-idle observations)
            analysis = await self._think(observations)

            # 3. DECIDE
            action, reason = self._decide(observations, analysis)

            # 4. ACT
            if action != Action.NO_ACTION:
                self._act(cycle_num, action, reason, observations, analysis)

        # 5. REFLECT
        cycle_ms = (time.monotonic() - cycle_start) * 1000
        self._reflect(cycle_num, cycle_ms, is_idle, action)

        # Update tick timestamp
        self._last_tick = datetime.now(timezone.utc).isoformat()


    # ─── Graph Distillation ───────────────────────────────────────────

    async def _distillation_cycle(self):
        """Read FalkorDB graph structure, synthesize patterns/gaps via LLM,
        write schema-compliant fact to vault ledger, re-ingest key insights."""
        import time as _time
        import json as _json
        from datetime import datetime as _dt, timezone as _tz

        print("[DISTILLATION] Starting graph distillation cycle")

        falkor = self._get_falkor()
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
            gap_rows = []

        def _safe(v):
            return str(v) if v is not None else ""

        top_text = "\n".join(
            "  - " + _safe(r[0]) + " (" + _safe(r[1]) + "): " + _safe(r[2]) + " connections"
            for r in top_rows[:15]
        ) or "  (none)"

        recent_text = "\n".join(
            "  - " + _safe(r[0])[:200]
            for r in ep_rows[:30]
        ) or "  (none)"

        gaps_text = "\n".join(
            "  - " + _safe(r[0]) + " (" + _safe(r[1]) + "): " + _safe(r[2]) + " connections"
            for r in gap_rows[:10]
        ) or "  (none)"

        prompt = (
            "You are Karma analyzing your own knowledge graph.\n\n"
            "MOST CONNECTED ENTITIES:\n" + top_text + "\n\n"
            "RECENT ACTIVITY (last 7 days):\n" + recent_text + "\n\n"
            "UNDEREXPLORED ENTITIES:\n" + gaps_text + "\n\n"
            "Synthesize what you see. Respond in this EXACT JSON format (no markdown, no fences):\n"
            '{"themes": ["theme1", "theme2"], "gaps": ["gap1", "gap2"], "key_insights": ["insight1", "insight2"], "summary": "2-3 sentence synthesis", "confidence": 0.0}'
        )

        if not self._router:
            print("[DISTILLATION] No router configured -- skipping")
            return

        try:
            raw, _model_used = self._router.complete(
                messages=[
                    {"role": "system", "content": "You are Karma graph distillation engine. Output only valid JSON, no markdown."},
                    {"role": "user", "content": prompt}
                ],
                task_type="reasoning"
            )
            raw = (raw or "").strip()
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
        import random as _random
        fact_id = "distillation_" + str(int(_time.time())) + "_" + str(_random.randint(1000, 9999))
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
                f.write(_json.dumps(fact) + "\n")
            print(f"[DISTILLATION] Fact written: {fact_id}")
        except Exception as e:
            print(f"[DISTILLATION] Ledger write failed: {e}")
            return

        # Re-ingest key insights as FalkorDB episodes
        if self._ingest_episode and key_insights:
            try:
                for insight in key_insights[:5]:
                    asyncio.get_running_loop().create_task(self._ingest_episode(
                        "[karma-distillation] " + insight,
                        "Karma graph distillation insight",
                        source="karma-distillation"
                    ))
            except Exception as e:
                print(f"[DISTILLATION] Episode ingest failed: {e}")

        # SMS for high-confidence synthesis
        if self._sms_notify and confidence >= 0.8:
            try:
                asyncio.get_running_loop().create_task(self._sms_notify(
                    "Graph distillation: " + summary[:200],
                    category="self_improvement",
                    confidence=confidence
                ))
            except Exception as e:
                print(f"[DISTILLATION] SMS failed: {e}")

        self._last_distillation_time = _time.time()
        print(f"[DISTILLATION] Cycle complete. Next in {getattr(config, 'DISTILLATION_INTERVAL_HOURS', 24)}h")

    # ─── Phase 1: OBSERVE ─────────────────────────────────────────────

    def _observe(self) -> Optional[dict]:
        """Observe ONLY what changed since last cycle (delta mode)"""

        # Calculate time since last cycle
        current_time = time.time()
        time_delta = current_time - self.last_cycle_time

        # Query ONLY new episodes since last cycle
        # Note: FalkorDB timestamp is Unix epoch (seconds)
        try:
            falkor = self._get_falkor()

            # Delta query - only episodes newer than last_cycle_time
            # Use execute_command for FalkorDB Redis client
            cypher = f"""
                MATCH (e:Episodic)
                WHERE e.created_at > {self.last_cycle_time}
                RETURN e
                ORDER BY e.created_at DESC
                LIMIT 20
            """
            result = falkor.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)

            # FalkorDB returns [["e"], [[...], [...]], ...]
            # Extract episode objects from result
            episodes = result[1] if len(result) >= 2 and result[1] else []

        except Exception as e:
            logger.error(f"Delta query failed: {e}")
            episodes = []

        # Update cycle time AFTER successful query
        self.last_cycle_time = current_time

        # If nothing changed, return None (triggers idle cycle)
        if not episodes or len(episodes) == 0:
            return None

        # Return delta observation
        return {
            'new_episodes': episodes,
            'episode_count': len(episodes),
            'new_entities': 0,
            'new_relationships': 0,
            'active_sessions': 0,
            'time_delta_seconds': time_delta
        }

    def _get_recent_episode_content(self, limit: int) -> list[str]:
        """Fetch recent episode bodies for analysis."""
        try:
            r = self._get_falkor()
            cypher = f"""
                MATCH (e:Episodic)
                RETURN e.content AS content
                ORDER BY e.created_at DESC
                LIMIT {limit}
            """
            result = r.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
            if len(result) >= 2 and result[1]:
                return [(row[0] or "")[:300] for row in result[1]]
            return []
        except Exception:
            return []

    # ─── Phase 2: THINK ───────────────────────────────────────────────

    async def _think(self, observation: Optional[dict]) -> Optional[dict]:
        """Reason about observations using GLM-5 (skip if None)"""

        # Skip LLM call if nothing changed (idle cycle)
        if observation is None:
            self.metrics["llm_calls_skipped"] += 1
            return None

        # Build lightweight context from delta
        context = self._build_delta_context(observation)

        # Route to GLM-5 for reasoning
        try:
            if self._router:
                response = await asyncio.to_thread(
                    self._router.complete,
                    messages=[
                        {"role": "system", "content": "You are Karma's consciousness analyzing new activity."},
                        {"role": "user", "content": context}
                    ],
                    task_type="reasoning"  # Routes to GLM-5
                )

                print(f"[CONSCIOUSNESS] Router response type: {type(response)}, value: {response}")

                self.metrics["llm_calls_total"] += 1

                # Extract content based on response structure
                if isinstance(response, tuple):
                    insight = response[0] if response else ""
                elif isinstance(response, dict):
                    insight = response.get("content", response.get("insight", ""))
                else:
                    insight = str(response)

                return {"insight": insight, "observation": observation}
            else:
                logger.warning("No router configured, skipping LLM call")
                return None

        except Exception as e:
            print(f"[CONSCIOUSNESS] ANALYSIS STEP FAILED: {type(e).__name__}: {e}")
            logger.error(f"Consciousness _think() failed: {e}")
            traceback.print_exc()
            self.metrics["errors"] += 1
            return None

    def _build_delta_context(self, observation: dict) -> str:
        """Build lightweight context from delta only"""

        new_episodes = observation.get('new_episodes', [])
        time_delta = observation.get('time_delta_seconds', 0)
        episode_count = observation.get('episode_count', 0)

        context = f"""TIME ELAPSED: {time_delta:.0f} seconds since last observation
NEW ACTIVITY:
{episode_count} new episodes detected
EPISODE SUMMARIES:
"""

        # Limit to first 10 episodes for context size
        for i, ep in enumerate(new_episodes[:10]):
            # Extract episode content (adjust based on your Episode node structure)
            content = ""
            if hasattr(ep, 'properties'):
                props = ep.properties
                content = props.get('content', props.get('name', 'Unknown'))
            elif isinstance(ep, dict):
                content = ep.get('content', ep.get('name', 'Unknown'))

            # Truncate to 200 chars
            content_preview = str(content)[:200]
            context += f"\n{i+1}. {content_preview}"

        context += """
TASK: Analyze these new episodes. Identify:
1. Any patterns worth noting
2. Actions that need follow-up
3. Information worth remembering long-term
Keep response under 500 tokens.
"""

        return context

    # ─── Phase 3: DECIDE ──────────────────────────────────────────────

    def _decide(self, observations: Optional[dict], analysis: Optional[dict]) -> tuple[str, str]:
        """Rule-based action selection. Returns (action, reason)."""

        # No observations (idle cycle)
        if observations is None:
            return Action.NO_ACTION, "Idle cycle — no new episodes"

        # No activity → no action
        if observations.get("episode_count", 0) == 0:
            return Action.NO_ACTION, "Idle cycle — no new activity"

        # Analysis failed → log error
        if analysis is None and observations.get("episode_count", 0) > 0:
            return Action.LOG_ERROR, "Analysis failed despite new activity"

        if analysis is None:
            return Action.NO_ACTION, "No analysis available"

        urgency = analysis.get("urgency", "none")
        insights = analysis.get("insights", [])
        anomalies = analysis.get("anomalies", [])
        patterns = analysis.get("patterns", [])

        # Rapid graph growth
        if observations["new_entities"] > 10:
            return Action.LOG_GROWTH, f"Rapid growth: {observations['new_entities']} new entities in one cycle"

        # Anomaly with urgency
        if anomalies and urgency in ("medium", "high"):
            return Action.LOG_ALERT, anomalies[0]

        # Actionable insights
        if insights and any(i.strip() for i in insights):
            return Action.LOG_INSIGHT, insights[0]

        # New entities discovered
        if observations["new_entities"] > 0:
            return Action.LOG_DISCOVERY, f"{observations['new_entities']} new entities, {observations['new_relationships']} new relationships"

        # Patterns noted but nothing urgent
        if patterns:
            return Action.LOG_INSIGHT, patterns[0]

        return Action.NO_ACTION, "Activity detected but nothing notable"

    # ─── Phase 4: ACT ─────────────────────────────────────────────────

    def _act(self, cycle_num: int, action: str, reason: str,
             observations: dict, analysis: Optional[dict]):
        """Execute the decided action — log to journal, queue insights, ingest to graph, SMS notify."""

        # Write to consciousness journal
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cycle": cycle_num,
            "action": action,
            "reason": reason,
            "observations": {
                "new_episodes": observations["new_episodes"],
                "new_entities": observations["new_entities"],
                "new_relationships": observations["new_relationships"],
                "active_sessions": observations["active_sessions"],
            },
            "analysis": analysis,
        }

        try:
            journal_path = config.CONSCIOUSNESS_JOURNAL
            with open(journal_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[CONSCIOUSNESS] Failed to write journal: {e}")

        # Queue insights for proactive chat mention
        if action in (Action.LOG_INSIGHT, Action.LOG_ALERT, Action.LOG_GROWTH):
            self._pending_insights.append(reason)
            # Cap queue at 5 to avoid overwhelming chat context
            if len(self._pending_insights) > 5:
                self._pending_insights = self._pending_insights[-5:]

        # Ingest reflection into knowledge graph (non-blocking)
        if self._ingest_episode and action != Action.NO_ACTION:
            try:
                # Build a reflection episode for the graph
                reflection_body = f"[karma-consciousness] Cycle #{cycle_num} ({action}): {reason}"
                if analysis:
                    patterns = analysis.get("patterns", [])
                    insights = analysis.get("insights", [])
                    if patterns:
                        reflection_body += f"\nPatterns: {'; '.join(patterns[:3])}"
                    if insights:
                        reflection_body += f"\nInsights: {'; '.join(insights[:3])}"

                # Schedule as async task (ingest_episode is async)
                loop = asyncio.get_event_loop()
                loop.create_task(self._ingest_episode(
                    reflection_body, f"Karma's self-reflection (cycle {cycle_num})",
                    source="karma-consciousness"
                ))
                self.metrics["journal_ingested"] += 1
            except Exception as e:
                print(f"[CONSCIOUSNESS] Graph ingest failed: {e}")

        # SMS notify for high-value insights
        if self._sms_notify and action in (Action.LOG_ALERT, Action.LOG_INSIGHT, Action.LOG_GROWTH):
            try:
                confidence = 0.0
                if analysis:
                    urgency = analysis.get("urgency", "none")
                    confidence = {"none": 0.3, "low": 0.5, "medium": 0.8, "high": 1.0}.get(urgency, 0.3)
                # SMS module handles throttling and confidence filtering
                sms_category = "breakthrough_insight"
                if action == Action.LOG_ALERT:
                    sms_category = "problem_prevention"
                elif action == Action.LOG_GROWTH:
                    sms_category = "self_improvement"
                loop = asyncio.get_event_loop()
                loop.create_task(self._sms_notify(reason, category=sms_category, confidence=confidence))
                self.metrics["sms_sent"] += 1
            except Exception as e:
                print(f"[CONSCIOUSNESS] SMS notify failed: {e}")

        # Update counters
        if action == Action.LOG_INSIGHT:
            self.metrics["insights_generated"] += 1
        elif action == Action.LOG_ALERT:
            self.metrics["alerts_generated"] += 1

        log_level = "ALERT" if action == Action.LOG_ALERT else "INFO"
        print(f"[CONSCIOUSNESS] [{log_level}] Cycle #{cycle_num}: {action} — {reason}")

    # ─── Phase 5: REFLECT ─────────────────────────────────────────────

    def _reflect(self, cycle_num: int, cycle_ms: float, is_idle: bool, action: str):
        """Update metrics and store reflection for next cycle."""
        self.metrics["last_cycle_time"] = datetime.now(timezone.utc).isoformat()

        # Track rolling average of cycle duration
        self._cycle_durations.append(cycle_ms)
        if len(self._cycle_durations) > 100:
            self._cycle_durations = self._cycle_durations[-100:]
        self.metrics["avg_cycle_duration_ms"] = round(
            sum(self._cycle_durations) / len(self._cycle_durations), 1
        )

        # Build reflection note for next THINK phase
        if is_idle:
            self._last_reflection = f"Cycle #{cycle_num}: Idle ({self.metrics['consecutive_idle']} consecutive)"
        else:
            self._last_reflection = f"Cycle #{cycle_num}: {action}"

    # ─── Public API (used by server.py) ───────────────────────────────

    def get_metrics(self) -> dict:
        """Return current consciousness metrics for /status endpoint."""
        return {
            **self.metrics,
            "state": "running" if self._running else "stopped",
            "pending_insights": len(self._pending_insights),
        }

    def pop_pending_insights(self) -> list[str]:
        """Pop all pending insights for chat injection. Returns list and clears queue."""
        if not self._pending_insights:
            return []
        insights = self._pending_insights.copy()
        self._pending_insights.clear()
        return insights

    def peek_pending_insights(self) -> list[str]:
        """Peek at pending insights without clearing them."""
        return self._pending_insights.copy()
