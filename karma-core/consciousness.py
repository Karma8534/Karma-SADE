"""
Karma Consciousness Loop — OBSERVE-only (Decision #3 aligned)

Background async loop running every CONSCIOUSNESS_INTERVAL seconds.
OBSERVE phase: rule-based delta scan of FalkorDB graph, no LLM calls.
THINK/DECIDE/ACT: removed per Decision #3 — Karma is the ONLY origin of
thought; K2 never calls LLM autonomously. The consciousness loop logs
observations to consciousness.jsonl for Karma to review in-session.

Distillation cycle: DISABLED — was making autonomous LLM calls.
Re-enable only when Karma explicitly triggers it during a session.
"""
import asyncio
import json
import logging
import time
import traceback
from datetime import datetime, timezone
from typing import Optional

import config
from decision_logger import DecisionLogger

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
    """Karma's background awareness — OBSERVE only, no autonomous LLM calls.

    Decision #3: Keep OBSERVE (60s, no LLM), kill THINK/DECIDE/ACT LLM calls.
    K2 is a continuity substrate, not an agent — preserve, observe, sync only.
    """

    def __init__(self, get_falkor_fn, get_graph_stats_fn, get_openai_client_fn,
                 active_conversations_ref: dict, router=None,
                 ingest_episode_fn=None, sms_notify_fn=None):
        # Injected dependencies from server.py (no circular imports)
        self._get_falkor = get_falkor_fn
        self._get_graph_stats = get_graph_stats_fn
        self._get_openai_client = get_openai_client_fn
        self._active_conversations = active_conversations_ref
        # Router kept for interface compatibility but NOT used for autonomous calls
        self._router = router
        self._ingest_episode = ingest_episode_fn
        self._sms_notify = sms_notify_fn  # Kept but only fires for rule-based alerts

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
            "proposals_written": 0,
            "journal_ingested": 0,
            "sms_sent": 0,
            "errors": 0,
            "llm_calls_total": 0,       # Should always be 0 now
            "llm_calls_skipped": 0,
            "avg_cycle_duration_ms": 0.0,
            "last_cycle_time": None,
            "consecutive_idle": 0,
            "started_at": None,
        }
        self._cycle_durations: list[float] = []  # Last 100 durations for avg
        self.last_cycle_time = 0  # Track when last cycle ran (0 = first cycle observes all)

    # ─── Lifecycle ────────────────────────────────────────────────────

    async def run(self):
        """Main loop — runs until stopped. OBSERVE only, no LLM calls."""
        self._running = True
        self.metrics["started_at"] = datetime.now(timezone.utc).isoformat()
        print("[CONSCIOUSNESS] Loop started — interval: {}s (OBSERVE-only mode, no LLM)".format(
            config.CONSCIOUSNESS_INTERVAL))

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
                # NOTE: Distillation cycle DISABLED — it made autonomous LLM calls.
                # To re-enable, Karma must explicitly trigger distillation during a session.
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

    # ─── Core Cycle (OBSERVE → rule-based DECIDE → log) ──────────────

    async def _cycle(self):
        """Execute one OBSERVE → DECIDE → LOG cycle. NO LLM calls."""
        cycle_start = time.monotonic()
        self.metrics["total_cycles"] += 1
        cycle_num = self.metrics["total_cycles"]

        # 1. OBSERVE (rule-based, no LLM)
        observations = self._observe()

        # If observation is None (idle cycle - no new episodes), skip rest
        if observations is None:
            self.metrics["idle_cycles"] += 1
            self.metrics["consecutive_idle"] += 1
            self.metrics["llm_calls_skipped"] += 1
            action = Action.NO_ACTION
            reason = "Idle cycle — no new episodes"
        else:
            self.metrics["active_cycles"] += 1
            self.metrics["consecutive_idle"] = 0

            # 2. DECIDE (rule-based — NO LLM, replaces old THINK+DECIDE)
            action, reason = self._decide_rule_based(observations)

            # 3. ACT (log only — no LLM, no autonomous graph ingest)
            if action != Action.NO_ACTION:
                await self._act(cycle_num, action, reason, observations)

        # 4. REFLECT (write cycle data to consciousness.jsonl)
        cycle_ms = (time.monotonic() - cycle_start) * 1000
        cycle_data = {
            "cycle": cycle_num,
            "cycle_ms": cycle_ms,
            "is_idle": observations is None,
            "action": action if observations is not None else "IDLE"
        }
        await self._reflect(cycle_data)

        # Update tick timestamp
        self._last_tick = datetime.now(timezone.utc).isoformat()

    # ─── Phase 1: OBSERVE ─────────────────────────────────────────────

    def _observe(self) -> Optional[dict]:
        """Observe ONLY what changed since last cycle (delta mode).
        Pure graph query — no LLM calls."""

        # Calculate time since last cycle
        current_time = time.time()
        time_delta = current_time - self.last_cycle_time

        # Query ONLY new episodes since last cycle
        try:
            falkor = self._get_falkor()
            cypher = f"""
                MATCH (e:Episodic)
                WHERE e.created_at > {self.last_cycle_time}
                RETURN e
                ORDER BY e.created_at DESC
                LIMIT 20
            """
            result = falkor.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, cypher)
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
            'time_delta_seconds': time_delta,
            'episode_count': len(episodes)
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

    # ─── Phase 2: DECIDE (rule-based, replaces THINK+DECIDE) ─────────

    def _decide_rule_based(self, observations: dict) -> tuple[str, str]:
        """Pure rule-based action selection. NO LLM calls.
        Replaces the old _think() + _decide() pipeline."""

        episode_count = observations.get("episode_count", 0)

        # No activity → no action
        if episode_count == 0:
            return Action.NO_ACTION, "No new activity"

        # Rapid graph growth (>10 episodes in one 60s cycle = unusual)
        if episode_count > 10:
            return Action.LOG_GROWTH, f"Rapid growth: {episode_count} new episodes in one cycle"

        # Moderate activity — just log discovery
        if episode_count > 0:
            return Action.LOG_DISCOVERY, f"{episode_count} new episodes"

        return Action.NO_ACTION, "Activity detected but nothing notable"

    # ─── Phase 3: ACT (log only — no LLM, no autonomous ingest) ──────

    async def _act(self, cycle_num: int, action: str, reason: str,
                  observations: dict):
        """Execute the decided action — LOG ONLY.
        No LLM calls, no autonomous graph ingest, no autonomous SMS.
        Proposals written to collab.jsonl for Karma to review in-session."""

        # Write to consciousness journal
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cycle": cycle_num,
            "action": action,
            "reason": reason,
            "model": "none",  # No LLM used
            "observations": {
                "episode_count": observations.get("episode_count", 0),
                "time_delta_seconds": observations.get("time_delta_seconds", 0),
            },
        }

        try:
            journal_path = config.CONSCIOUSNESS_JOURNAL
            with open(journal_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"[CONSCIOUSNESS] Failed to write journal: {e}")

        # Log to decision_log.jsonl
        try:
            decision_logger = DecisionLogger()
            result = await decision_logger.log_decision(
                decision=action,
                observation=f"Episodes: {observations.get('episode_count', 0)}",
                reasoning=reason,
                action=f"Cycle #{cycle_num}: {action}",
                source="consciousness_loop"
            )
        except Exception as e:
            print(f"[CONSCIOUSNESS] Failed to write decision log: {e}")

        # Queue insights for proactive chat mention (Karma reads these in-session)
        if action in (Action.LOG_INSIGHT, Action.LOG_ALERT, Action.LOG_GROWTH):
            self._pending_insights.append(reason)
            if len(self._pending_insights) > 5:
                self._pending_insights = self._pending_insights[-5:]

        # NOTE: Autonomous graph ingest REMOVED — Karma decides what to ingest during sessions
        # NOTE: Autonomous SMS REMOVED — Karma decides when to notify during sessions

        # Update counters
        if action == Action.LOG_INSIGHT:
            self.metrics["insights_generated"] += 1
        elif action == Action.LOG_ALERT:
            self.metrics["alerts_generated"] += 1

        log_level = "ALERT" if action == Action.LOG_ALERT else "INFO"
        print(f"[CONSCIOUSNESS] [{log_level}] Cycle #{cycle_num}: {action} — {reason}")

    # ─── Phase 4: REFLECT ─────────────────────────────────────────────

    async def _reflect(self, cycle_data: dict) -> dict:
        """REFLECT phase: Log complete cycle to consciousness.jsonl.
        Pure logging — no LLM calls."""
        try:
            cycle_num = cycle_data.get("cycle", 0)
            cycle_ms = cycle_data.get("cycle_ms", 0)
            is_idle = cycle_data.get("is_idle", False)
            action = cycle_data.get("action", "NO_ACTION")

            reflection_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "CYCLE_REFLECTION",
                "cycle": cycle_num,
                "is_idle": is_idle,
                "action": action,
                "cycle_duration_ms": cycle_ms,
                "cycle_data": cycle_data
            }

            # Append to consciousness.jsonl
            consciousness_path = getattr(config, "CONSCIOUSNESS_JOURNAL",
                "/opt/seed-vault/memory_v1/ledger/consciousness.jsonl")
            with open(consciousness_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(reflection_entry) + "\n")

            # Update metrics
            self.metrics["last_cycle_time"] = reflection_entry["timestamp"]

            # Track rolling average of cycle duration
            self._cycle_durations.append(cycle_ms)
            if len(self._cycle_durations) > 100:
                self._cycle_durations = self._cycle_durations[-100:]
            self.metrics["avg_cycle_duration_ms"] = round(
                sum(self._cycle_durations) / len(self._cycle_durations), 1
            )

            # Update last reflection
            if is_idle:
                self._last_reflection = f"Cycle #{cycle_num}: Idle ({self.metrics['consecutive_idle']} consecutive)"
            else:
                self._last_reflection = f"Cycle #{cycle_num}: {action}"

            return {
                "phase": "REFLECT",
                "reflected": True,
                "timestamp": reflection_entry["timestamp"]
            }
        except Exception as e:
            return {
                "phase": "REFLECT",
                "reflected": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    # ─── Tool-Use Methods (available for Karma to call in-session) ────

    async def _execute_tool(self, tool_name: str, tool_args: dict) -> dict:
        """TOOL-USE: Execute a tool when Karma explicitly requests it.
        NOT called autonomously by the consciousness loop."""
        try:
            if tool_name == "query_graph":
                return await self._tool_query_graph(tool_args)
            elif tool_name == "search_ledger":
                return await self._tool_search_ledger(tool_args)
            elif tool_name == "analyze_pattern":
                return await self._tool_analyze_pattern(tool_args)
            else:
                return {
                    "success": False,
                    "tool": tool_name,
                    "error": f"Unknown tool: {tool_name}"
                }
        except Exception as e:
            return {
                "success": False,
                "tool": tool_name,
                "error": str(e)
            }

    async def _tool_query_graph(self, args: dict) -> dict:
        """Query FalkorDB graph — available for Karma in-session use."""
        try:
            query = args.get("cypher", "MATCH (e:Entity) RETURN count(e) LIMIT 1")
            falkor = self._get_falkor()
            result = falkor.execute_command("GRAPH.QUERY", config.GRAPHITI_GROUP_ID, query)
            return {
                "success": True,
                "tool": "query_graph",
                "result": result[:2] if len(result) >= 2 else result
            }
        except Exception as e:
            return {
                "success": False,
                "tool": "query_graph",
                "error": str(e)
            }

    async def _tool_search_ledger(self, args: dict) -> dict:
        """Search recent ledger entries for patterns."""
        try:
            query = args.get("search_term", "")
            limit = args.get("limit", 10)
            ledger_file = config.LEDGER_PATH

            results = []
            with open(ledger_file, "r") as f:
                lines = f.readlines()

            for line in reversed(lines[-100:]):
                if line.strip():
                    entry = json.loads(line)
                    if query.lower() in json.dumps(entry).lower():
                        results.append(entry)
                        if len(results) >= limit:
                            break

            return {
                "success": True,
                "tool": "search_ledger",
                "query": query,
                "matches": len(results),
                "result": results
            }
        except Exception as e:
            return {
                "success": False,
                "tool": "search_ledger",
                "error": str(e)
            }

    async def _tool_analyze_pattern(self, args: dict) -> dict:
        """Analyze patterns in recent episodes."""
        try:
            limit = args.get("limit", 20)
            recent_content = self._get_recent_episode_content(limit)

            if not recent_content:
                return {
                    "success": True,
                    "tool": "analyze_pattern",
                    "pattern": "insufficient_data",
                    "count": 0
                }

            return {
                "success": True,
                "tool": "analyze_pattern",
                "count": len(recent_content),
                "sample_episodes": recent_content[:5]
            }
        except Exception as e:
            return {
                "success": False,
                "tool": "analyze_pattern",
                "error": str(e)
            }

    # ─── Public API (used by server.py) ───────────────────────────────

    def get_metrics(self) -> dict:
        """Return current consciousness metrics for /status endpoint."""
        return {
            **self.metrics,
            "state": "running" if self._running else "stopped",
            "mode": "observe-only",  # Signal that no LLM calls happen
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
