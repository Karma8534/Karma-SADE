#!/usr/bin/env python3
"""
Update consciousness.py to wire full OBSERVE/THINK/DECIDE/ACT/REFLECT cycle with tool-use.

Changes:
1. Convert _act() to async and properly await it in _cycle()
2. Add _execute_tool() and related methods
3. Update _reflect() to be async and log to consciousness.jsonl properly
4. Ensure main _cycle() properly awaits all async methods
"""

import sys

# Read the file
with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'r') as f:
    content = f.read()

# Step 1: Fix the main _cycle() method to properly await _act()
old_cycle = '''    async def _cycle(self):
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
        self._last_tick = datetime.now(timezone.utc).isoformat()'''

new_cycle = '''    async def _cycle(self):
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

            # 4. ACT (now async - properly awaited)
            if action != Action.NO_ACTION:
                await self._act(cycle_num, action, reason, observations, analysis)

        # 5. REFLECT (now async - properly awaited)
        cycle_ms = (time.monotonic() - cycle_start) * 1000
        cycle_data = {
            "cycle": cycle_num,
            "cycle_ms": cycle_ms,
            "is_idle": is_idle,
            "action": action if not is_idle else "IDLE"
        }
        await self._reflect(cycle_data)

        # Update tick timestamp
        self._last_tick = datetime.now(timezone.utc).isoformat()'''

if old_cycle in content:
    content = content.replace(old_cycle, new_cycle)
    print("✓ Updated _cycle() to properly await _act() and _reflect()")
else:
    print("✗ Could not find exact _cycle() method to replace")
    sys.exit(1)

# Step 2: Replace the old _act() method with async version
old_act_sig = '''    def _act(self, cycle_num: int, action: str, reason: str,
             observations: dict, analysis: Optional[dict]):'''
new_act_sig = '''    async def _act(self, cycle_num: int, action: str, reason: str,
                  observations: dict, analysis: Optional[dict]):'''

if old_act_sig in content:
    content = content.replace(old_act_sig, new_act_sig)
    print("✓ Converted _act() signature to async")
else:
    print("✗ Could not find _act() signature")
    sys.exit(1)

# Step 3: Fix the _act() method's decision_logger.log_decision() call to properly await
old_act_call = '''        # Log to decision_log.jsonl
        try:
            decision_logger = DecisionLogger()
            decision_str = action
            observation_str = f"Episodes: {observations.get('new_episodes', 0)}, Entities: {observations.get('new_entities', 0)}, Relationships: {observations.get('new_relationships', 0)}"
            reasoning_str = reason
            action_str = f"Cycle #{cycle_num}: {action}"

            # Schedule async log task
            loop = asyncio.get_event_loop()
            loop.create_task(decision_logger.log_decision(
                decision=decision_str,
                observation=observation_str,
                reasoning=reasoning_str,
                action=action_str,
                source="consciousness_loop"
            ))
        except Exception as e:
            print(f"[CONSCIOUSNESS] Failed to write decision log: {e}")'''

new_act_call = '''        # Log to decision_log.jsonl (async)
        try:
            decision_logger = DecisionLogger()
            decision_str = action
            observation_str = f"Episodes: {observations.get('new_episodes', 0)}, Entities: {observations.get('new_entities', 0)}, Relationships: {observations.get('new_relationships', 0)}"
            reasoning_str = reason
            action_str = f"Cycle #{cycle_num}: {action}"

            # Properly await the async decision logger
            result = await decision_logger.log_decision(
                decision=decision_str,
                observation=observation_str,
                reasoning=reasoning_str,
                action=action_str,
                source="consciousness_loop"
            )
            if not result.get("ok", False):
                print(f"[CONSCIOUSNESS] Decision log error: {result.get('error', 'unknown')}")
        except Exception as e:
            print(f"[CONSCIOUSNESS] Failed to write decision log: {e}")'''

if old_act_call in content:
    content = content.replace(old_act_call, new_act_call)
    print("✓ Fixed decision_logger.log_decision() await in _act()")
else:
    print("✗ Could not find old decision logger call in _act()")
    sys.exit(1)

# Step 4: Fix the _ingest_episode call to properly await
old_ingest_call = '''                # Schedule as async task (ingest_episode is async)
                loop = asyncio.get_event_loop()
                loop.create_task(self._ingest_episode(
                    reflection_body, f"Karma's self-reflection (cycle {cycle_num})",
                    source="karma-consciousness"
                ))'''

new_ingest_call = '''                # Properly await the async ingest_episode
                await self._ingest_episode(
                    reflection_body, f"Karma's self-reflection (cycle {cycle_num})",
                    source="karma-consciousness"
                )'''

if old_ingest_call in content:
    content = content.replace(old_ingest_call, new_ingest_call)
    print("✓ Fixed _ingest_episode await in _act()")
else:
    print("✗ Could not find old ingest_episode call")
    sys.exit(1)

# Step 5: Fix the _sms_notify call to properly await
old_sms_call = '''                loop = asyncio.get_event_loop()
                loop.create_task(self._sms_notify(reason, category=sms_category, confidence=confidence))'''

new_sms_call = '''                await self._sms_notify(reason, category=sms_category, confidence=confidence)'''

if old_sms_call in content:
    content = content.replace(old_sms_call, new_sms_call)
    print("✓ Fixed _sms_notify await in _act()")
else:
    print("✗ Could not find old sms_notify call")
    sys.exit(1)

# Step 6: Replace old _reflect() method with new async version
old_reflect = '''    def _reflect(self, cycle_num: int, cycle_ms: float, is_idle: bool, action: str):
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
            self._last_reflection = f"Cycle #{cycle_num}: {action}"'''

new_reflect = '''    async def _reflect(self, cycle_data: dict) -> dict:
        """
        REFLECT phase: Log complete cycle to consciousness.jsonl for learning.

        Now async: properly writes to consciousness.jsonl with full cycle data.
        """
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
            consciousness_path = getattr(config, "CONSCIOUSNESS_JOURNAL", "/opt/seed-vault/memory_v1/ledger/consciousness.jsonl")
            with open(consciousness_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(reflection_entry) + "\\n")

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
            }'''

if old_reflect in content:
    content = content.replace(old_reflect, new_reflect)
    print("✓ Converted _reflect() to async and added consciousness.jsonl logging")
else:
    print("✗ Could not find old _reflect() method")
    sys.exit(1)

# Step 7: Add tool-use methods before the public API section
# Find the insertion point (before "# ─── Public API")
public_api_marker = '''    # ─── Public API (used by server.py) ───────────────────────────────

    def get_metrics(self) -> dict:'''

tool_use_methods = '''    # ─── Tool-Use Methods ────────────────────────────────────────────

    async def _execute_tool(self, tool_name: str, tool_args: dict) -> dict:
        """
        TOOL-USE phase: Execute a tool within consciousness reasoning.

        Supported tools:
        - 'query_graph': Query FalkorDB for entity/relationship info
        - 'search_ledger': Search recent ledger entries
        - 'analyze_pattern': Analyze patterns in recent episodes

        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool

        Returns:
            Tool result dict with 'success' and 'result' keys
        """
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
        """Query FalkorDB graph during consciousness cycle."""
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

            # Search in reverse (recent first)
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

    def get_metrics(self) -> dict:'''

if public_api_marker in content:
    content = content.replace(public_api_marker, tool_use_methods)
    print("✓ Added tool-use methods before public API section")
else:
    print("✗ Could not find public API marker")
    sys.exit(1)

# Write the updated content
with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'w') as f:
    f.write(content)

print("\n✓ consciousness.py updated successfully!")
print("Summary of changes:")
print("  1. _cycle() now properly awaits _act() and _reflect()")
print("  2. _act() converted to async with proper awaits")
print("  3. _reflect() converted to async and logs to consciousness.jsonl")
print("  4. Added _execute_tool() and 3 tool-use methods")
print("  5. All I/O operations properly awaited")
