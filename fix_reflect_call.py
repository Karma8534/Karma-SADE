#!/usr/bin/env python3
import re

with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'r') as f:
    content = f.read()

# Replace the _reflect() call
old_call = '''        # 5. REFLECT
        cycle_ms = (time.monotonic() - cycle_start) * 1000
        self._reflect(cycle_num, cycle_ms, is_idle, action)'''

new_call = '''        # 5. REFLECT
        cycle_ms = (time.monotonic() - cycle_start) * 1000
        cycle_data = {
            "cycle": cycle_num,
            "cycle_ms": cycle_ms,
            "is_idle": is_idle,
            "action": action if not is_idle else "IDLE"
        }
        await self._reflect(cycle_data)'''

content = content.replace(old_call, new_call)

# Now find and replace the old _reflect() method definition
# Old method starts at "def _reflect(self, cycle_num:" and ends before next "def " or "#"
pattern = r'    def _reflect\(self, cycle_num: int, cycle_ms: float, is_idle: bool, action: str\):.*?(?=\n    # ─── Public API|\n    def get_metrics)'

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

content = re.sub(pattern, new_reflect_method, content, flags=re.DOTALL)

with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'w') as f:
    f.write(content)

print("[OK] Updated _reflect() call and method")
