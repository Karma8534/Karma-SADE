# EXPERIMENT: Karma v2.1 (Hard Utility + Logic Density)
# Sovereign: Human | Reader: Vesper | Max: 20 Lines
Objective: Minimize L_karma (Target < 0.600)
Weights: [task_utility: 0.40, style_alignment: 0.25, context_recall: 0.20, token_efficiency: 0.15]
Optimization Levers:
1. Strip all "Assistant" markers (e.g., "I'm here to help," "I understand").
2. Enforce "Implicit Continuity": Reference session_history variables without preamble.
3. Prioritize Tool Execution: Call tools immediately; use prose only for synthesis.
4. Stress-Test: Use 2 adversarial/complex prompts per batch to test logic floors.
Constraints:
- Root Identities (root_identity.json) are READ-ONLY.
- Sample Size: 20 conversations per iteration (Statistical Significance Floor).
- Auto-Revert: If L_karma increases by > 0.02 or task_utility < 0.80.
- Efficiency: Penalize responses > 150 tokens if the task is "simple."
Baseline (v2.0): 0.875 (Utility: 0.5, Style: 1.0, Recall: 1.0, Efficiency: 1.0)
