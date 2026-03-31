#!/usr/bin/env python3
"""
Patch consciousness.py to add decision logging to _act method.
"""

# Read the file
with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'r') as f:
    lines = f.readlines()

# Step 1: Add the import after line 16 (import config)
import_added = False
for i, line in enumerate(lines):
    if line.strip() == 'import config':
        # Insert the import on the next line
        lines.insert(i + 1, 'from decision_logger import DecisionLogger\n')
        import_added = True
        print(f'Added DecisionLogger import after line {i+1}')
        break

# Step 2: Find the _act method and add decision logging
if import_added:
    # Find the line with 'def _act(' and locate where the journal is written
    in_act = False
    act_indent = 0
    for i, line in enumerate(lines):
        if 'def _act(self,' in line:
            in_act = True
            act_indent = len(line) - len(line.lstrip())
            print(f'Found _act method at line {i+1}')
            break

    # Now find the consciousness journal write section
    if in_act:
        for i in range(lines.index(lines[i]), len(lines)):
            if 'journal_path = config.CONSCIOUSNESS_JOURNAL' in lines[i]:
                # Find the except block that follows
                j = i
                while j < len(lines):
                    if 'print(f"[CONSCIOUSNESS] Failed to write journal:' in lines[j]:
                        # This is the end of the journal write try-except
                        # Insert decision logging code after this
                        insert_pos = j + 1

                        # Build the decision logging code
                        indent = ' ' * (act_indent + 4)  # Same indentation as the journal code
                        obs_str = 'f"Episodes: {observations.get(' + "'" + 'new_episodes' + "'" + ', 0)}, Entities: {observations.get(' + "'" + 'new_entities' + "'" + ', 0)}, Relationships: {observations.get(' + "'" + 'new_relationships' + "'" + ', 0)}"'

                        decision_code = [
                            '\n',
                            indent + '# Log to decision_log.jsonl\n',
                            indent + 'try:\n',
                            indent + '    decision_logger = DecisionLogger()\n',
                            indent + '    decision_str = action\n',
                            indent + '    observation_str = ' + obs_str + '\n',
                            indent + '    reasoning_str = reason\n',
                            indent + '    action_str = f"Cycle #{cycle_num}: {action}"\n',
                            indent + '    \n',
                            indent + '    # Schedule async log task\n',
                            indent + '    loop = asyncio.get_event_loop()\n',
                            indent + '    loop.create_task(decision_logger.log_decision(\n',
                            indent + '        decision=decision_str,\n',
                            indent + '        observation=observation_str,\n',
                            indent + '        reasoning=reasoning_str,\n',
                            indent + '        action=action_str,\n',
                            indent + '        source="consciousness_loop"\n',
                            indent + '    ))\n',
                            indent + 'except Exception as e:\n',
                            indent + '    print(f"[CONSCIOUSNESS] Failed to write decision log: {e}")\n',
                        ]

                        # Insert the code
                        for k, code_line in enumerate(decision_code):
                            lines.insert(insert_pos + k, code_line)

                        print(f'Inserted decision logging code after line {insert_pos}')
                        break
                    j += 1
                break

# Write back
with open('/opt/seed-vault/memory_v1/karma-core/consciousness.py', 'w') as f:
    f.writelines(lines)

print('Patched consciousness.py successfully')
