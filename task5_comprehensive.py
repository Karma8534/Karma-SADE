#!/usr/bin/env python3
"""Comprehensive Task 5 update: Full async cycle with tool-use integration"""

import re

with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'r') as f:
    content = f.read()

print("[1/6] Converting _act() to async...")
# Change 1: Make _act() async
content = content.replace(
    '    def _act(self, cycle_num: int, action: str, reason: str,\n             observations: dict, analysis: Optional[dict]):',
    '    async def _act(self, cycle_num: int, action: str, reason: str,\n                  observations: dict, analysis: Optional[dict]):'
)

print("[2/6] Updating _cycle() to await _act()...")
# Change 2: Await _act() call
content = content.replace(
    '                self._act(cycle_num, action, reason, observations, analysis)',
    '                await self._act(cycle_num, action, reason, observations, analysis)'
)

print("[3/6] Fixing decision logger to use await...")
# Change 3: Fix decision logger
content = content.replace(
    '''            # Schedule async log task
            loop = asyncio.get_event_loop()
            loop.create_task(decision_logger.log_decision(
                decision=decision_str,
                observation=observation_str,
                reasoning=reasoning_str,
                action=action_str,
                source="consciousness_loop"
            ))''',
    '''            # Properly await the async decision logger
            result = await decision_logger.log_decision(
                decision=decision_str,
                observation=observation_str,
                reasoning=reasoning_str,
                action=action_str,
                source="consciousness_loop"
            )'''
)

print("[4/6] Fixing _ingest_episode to use await...")
# Change 4: Fix ingest_episode
content = content.replace(
    '''                # Schedule as async task (ingest_episode is async)
                loop = asyncio.get_event_loop()
                loop.create_task(self._ingest_episode(
                    reflection_body, f"Karma's self-reflection (cycle {cycle_num})",
                    source="karma-consciousness"
                ))''',
    '''                # Properly await the async ingest_episode
                await self._ingest_episode(
                    reflection_body, f"Karma's self-reflection (cycle {cycle_num})",
                    source="karma-consciousness"
                )'''
)

print("[5/6] Fixing _sms_notify to use await...")
# Change 5: Fix sms_notify
content = content.replace(
    '''                loop = asyncio.get_event_loop()
                loop.create_task(self._sms_notify(reason, category=sms_category, confidence=confidence))''',
    '''                await self._sms_notify(reason, category=sms_category, confidence=confidence)'''
)

print("[6/6] Updating _cycle() reflect call and replacing _reflect() method...")
# Change 6: Update _reflect() call in _cycle
old_reflect_call = '''        # 5. REFLECT
        cycle_ms = (time.monotonic() - cycle_start) * 1000
        self._reflect(cycle_num, cycle_ms, is_idle, action)'''

new_reflect_call = '''        # 5. REFLECT
        cycle_ms = (time.monotonic() - cycle_start) * 1000
        cycle_data = {
            "cycle": cycle_num,
            "cycle_ms": cycle_ms,
            "is_idle": is_idle,
            "action": action if not is_idle else "IDLE"
        }
        await self._reflect(cycle_data)'''

content = content.replace(old_reflect_call, new_reflect_call)

# Change 7: Replace old _reflect() method with new async version
old_reflect_pattern = r'    def _reflect\(self, cycle_num: int, cycle_ms: float, is_idle: bool, action: str\):.*?(?=\n    # ─── Public API|\n    def get_metrics)'

new_reflect_method = '''    async def _reflect(self, cycle_data: dict) -> dict:
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
            }
'''

content = re.sub(old_reflect_pattern, new_reflect_method, content, flags=re.DOTALL)

# Change 8: Add tool-use methods before Public API
tool_use_section = '''    # ─── Tool-Use Methods ────────────────────────────────────────────

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

'''

# Insert before Public API
content = content.replace(
    '    # ─── Public API (used by server.py) ───────────────────────────────',
    tool_use_section + '    # ─── Public API (used by server.py) ───────────────────────────────'
)

# Write the updated file
with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'w') as f:
    f.write(content)

print("\n[SUCCESS] All updates applied to consciousness.py")
print("Summary:")
print("  - Converted _act() to async")
print("  - Updated _cycle() to await _act() and _reflect()")
print("  - Fixed all decision_logger, ingest_episode, sms_notify awaits")
print("  - Converted _reflect() to async with consciousness.jsonl logging")
print("  - Added tool-use methods: _execute_tool, _tool_query_graph, _tool_search_ledger, _tool_analyze_pattern")
