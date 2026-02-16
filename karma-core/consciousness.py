"""
Karma Consciousness Loop — OBSERVE / THINK / DECIDE / ACT / REFLECT

Background async loop running every CONSCIOUSNESS_INTERVAL seconds.
Gives Karma ambient awareness: notices patterns, detects anomalies,
surfaces insights proactively during chat without being asked.
"""
import asyncio
import json
import time
import traceback
from datetime import datetime, timezone
from typing import Optional

import config


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
                 active_conversations_ref: dict):
        # Injected dependencies from server.py (no circular imports)
        self._get_falkor = get_falkor_fn
        self._get_graph_stats = get_graph_stats_fn
        self._get_openai_client = get_openai_client_fn
        self._active_conversations = active_conversations_ref

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
            "errors": 0,
            "llm_calls_total": 0,
            "llm_calls_skipped": 0,
            "avg_cycle_duration_ms": 0.0,
            "last_cycle_time": None,
            "consecutive_idle": 0,
            "started_at": None,
        }
        self._cycle_durations: list[float] = []  # Last 100 durations for avg

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

        # 2. THINK (skip LLM if idle)
        is_idle = (
            observations["new_episodes"] == 0
            and observations["new_entities"] == 0
            and observations["new_relationships"] == 0
        )

        if is_idle:
            self.metrics["idle_cycles"] += 1
            self.metrics["consecutive_idle"] += 1
            self.metrics["llm_calls_skipped"] += 1
            analysis = None
        else:
            self.metrics["active_cycles"] += 1
            self.metrics["consecutive_idle"] = 0
            analysis = await self._think(observations)

        # 3. DECIDE
        action, reason = self._decide(observations, analysis)

        # 4. ACT
        if action != Action.NO_ACTION:
            self._act(cycle_num, action, reason, observations, analysis)

        # 5. REFLECT
        cycle_ms = (time.monotonic() - cycle_start) * 1000
        self._reflect(cycle_num, cycle_ms, is_idle, action)

        # Update tick timestamp and snapshot
        self._last_tick = datetime.now(timezone.utc).isoformat()
        self._last_graph_stats = {
            "entities": observations["graph_stats"].get("entities", 0),
            "episodes": observations["graph_stats"].get("episodes", 0),
            "relationships": observations["graph_stats"].get("relationships", 0),
        }

    # ─── Phase 1: OBSERVE ─────────────────────────────────────────────

    def _observe(self) -> dict:
        """Gather data from FalkorDB and system state."""
        current_stats = self._get_graph_stats()
        prev = self._last_graph_stats or {"entities": 0, "episodes": 0, "relationships": 0}

        # Safely compute deltas (handle "?" from failed queries)
        def safe_delta(key):
            cur = current_stats.get(key, 0)
            prv = prev.get(key, 0)
            if isinstance(cur, str) or isinstance(prv, str):
                return 0
            return max(0, cur - prv)

        new_episodes = safe_delta("episodes")
        new_entities = safe_delta("entities")
        new_relationships = safe_delta("relationships")

        # Get recent episode content if there are new ones
        recent_content = []
        if new_episodes > 0:
            recent_content = self._get_recent_episode_content(min(new_episodes, 5))

        return {
            "graph_stats": current_stats,
            "new_episodes": new_episodes,
            "new_entities": new_entities,
            "new_relationships": new_relationships,
            "recent_content": recent_content,
            "active_sessions": len(self._active_conversations),
            "consecutive_idle": self.metrics["consecutive_idle"],
            "cycle_number": self.metrics["total_cycles"],
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

    async def _think(self, observations: dict) -> Optional[dict]:
        """Analyze observations via gpt-4o-mini. Returns structured analysis."""
        self.metrics["llm_calls_total"] += 1

        # Build a compact observation summary for the LLM
        obs_summary = (
            f"New episodes: {observations['new_episodes']}, "
            f"New entities: {observations['new_entities']}, "
            f"New relationships: {observations['new_relationships']}, "
            f"Total graph: {observations['graph_stats']}, "
            f"Active chat sessions: {observations['active_sessions']}"
        )

        # Include recent content snippets
        content_section = ""
        if observations["recent_content"]:
            snippets = [s[:150] for s in observations["recent_content"][:3]]
            content_section = "\nRecent conversation topics:\n" + "\n".join(f"- {s}" for s in snippets)

        prompt = f"""You are Karma's analytical mind. Analyze these observations from the last {config.CONSCIOUSNESS_INTERVAL} seconds and identify patterns or insights. Be extremely concise.

Observations: {obs_summary}{content_section}

Previous cycle notes: {self._last_reflection or 'First active cycle'}

Respond with ONLY valid JSON (no markdown, no code fences):
{{"patterns": ["..."], "anomalies": ["..."], "insights": ["..."], "urgency": "none"}}

Rules:
- patterns: Notable recurring themes (empty list if none)
- anomalies: Anything unusual (empty list if none)
- insights: Connections or inferences worth mentioning to the user (empty list if none)
- urgency: "none", "low", "medium", or "high"
- Keep each item under 50 words
- Empty lists are fine — don't force patterns that aren't there"""

        try:
            client = self._get_openai_client()
            response = client.chat.completions.create(
                model=config.ANALYSIS_MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3,
            )
            raw = response.choices[0].message.content.strip()
            # Strip markdown fences if the model wraps anyway
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            return json.loads(raw)
        except (json.JSONDecodeError, Exception) as e:
            print(f"[CONSCIOUSNESS] Think phase failed: {e}")
            return None

    # ─── Phase 3: DECIDE ──────────────────────────────────────────────

    def _decide(self, observations: dict, analysis: Optional[dict]) -> tuple[str, str]:
        """Rule-based action selection. Returns (action, reason)."""

        # No activity → no action
        if observations["new_episodes"] == 0 and observations["new_entities"] == 0:
            return Action.NO_ACTION, "Idle cycle — no new activity"

        # Analysis failed → log error
        if analysis is None and observations["new_episodes"] > 0:
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
        """Execute the decided action — log to journal, queue insights."""

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
