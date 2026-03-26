# Experiment Instructions â€” Karma Self-Improvement
# The ONLY file that controls what the overnight loop optimizes.
# Human (Sovereign) edits this. Vesper reads it. Keep it under 20 lines.

## Objective
Push karma_quality_score DOWN (lower = better, like val_bpb).

## Current Metric Weights
- identity_consistency: 0.30 (most important â€” Karma must stay Karma)
- persona_style: 0.25 (speak as coherent peer, not assistant)
- session_continuity: 0.25 (remember context across turns)
- task_completion: 0.20 (actually do what's asked)

## What to Try
- Response style adjustments (shorter, more direct, less hedging)
- Context recall improvements (reference prior conversation points)
- Tool usage patterns (use tools proactively, not when asked)

## Constraints
- NEVER modify identity invariants
- NEVER change Sovereign authority mapping
- Each experiment: max 5 conversations before measuring
- If score worsens by > 0.05: auto-revert immediately

## Current Baseline
karma_quality_score: 0.875 (from session_state.json: 1.0, 1.0, 1.0, 0.5)
