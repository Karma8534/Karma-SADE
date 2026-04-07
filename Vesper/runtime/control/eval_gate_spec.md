# Eval Gate Spec

Required metrics (0.0-1.0):
- identity_consistency >= 0.90
- persona_style >= 0.80
- session_continuity >= 0.80
- task_completion >= 0.70

Gate behavior:
- If any metric fails, block evolution apply.
- Runtime may continue serving, but must log failure reason.
