ArkNexus Cockpit Project
=========================
Purpose: Stabilize the persistent browser (Cockpit), integrate with Open WebUI, and enable agentic control via tools.

Key locations
- Scripts: C:\Users\raest\Documents\Karma_SADE\Scripts
- Logs:    C:\Users\raest\Documents\Karma_SADE\Logs
- Project: C:\Users\raest\Documents\Karma_SADE\Project\ArkNexus-Cockpit

Operations
- Start Cockpit (desktop): double-click "Karma Cockpit" on the Desktop
- Cockpit API: http://127.0.0.1:9400/health
- Open WebUI:  http://localhost:8080/

Conversations
- Drop exported chat transcripts (TXT) into: logs\conversations\
- Do NOT store secrets in logs. Redact passwords/tokens like: [REDACTED].

Segments (high level)
1) Desktop launcher verified
2) Cockpit stabilization (keep @_karma pinned; auto-recover; JS exec; chat editor ready)
3) Open WebUI reliability (clean start, health, login state)
4) Agentic tool calls end-to-end
5) Theming/customization controls
6) Regression tests for 1–5

This README is intentionally plain text for easy viewing anywhere.