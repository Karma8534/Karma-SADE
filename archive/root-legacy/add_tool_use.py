#!/usr/bin/env python3
"""Add tool-use methods before Public API section"""

with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'r') as f:
    content = f.read()

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

# Insert before Public API section
content = content.replace(
    '    # ─── Public API (used by server.py) ───────────────────────────────',
    tool_use_section + '    # ─── Public API (used by server.py) ───────────────────────────────'
)

with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'w') as f:
    f.write(content)

print("[OK] Added tool-use methods")
