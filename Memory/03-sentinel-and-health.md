# Karma SADE - Sentinel and Health Monitoring (Design)

This file describes the Sentinel/watchdog concept for Karma SADE.
It is a design document and source of truth for what "healthy" means in this system.

## 1. Purpose of Sentinel

- Monitor the health of key services and resources.
- Detect problems early (stopped services, high resource usage, repeated errors).
- Provide simple, clear status signals for the human (Neo) and for Karma SADE Architect.

Sentinel itself should be simple, transparent, and easy to disable or adjust.

## 2. Initial Scope of Monitoring

Sentinel should focus on:

- Service health:
  - Ollama service.
  - Open WebUI service.
  - Any future Karma SADE services (to be listed here as they are added).
- Resource health:
  - Disk usage on main drives.
  - Basic CPU/memory load ranges (to be defined later).
- Log signals:
  - Repeated errors in key logs (e.g., Open WebUI logs, sentinel logs).

## 3. Health Checks (Implemented)

The Sentinel script performs the following checks:

- Ollama process: Is the ollama process running?
- Ollama HTTP: Is http://localhost:11434 responding?
- Open WebUI process: Is the open-webui process running?
- Open WebUI HTTP: Is http://localhost:8080 responding?
- Disk C: usage (warning at 80%, critical at 90%)

### Thresholds
- Disk warning: 80% used
- Disk critical: 90% used
- HTTP timeout: 10 seconds

## 4. Sentinel Scripts and Schedule

### Scripts
- Main script: C:\Users\raest\Documents\Karma_SADE\Scripts\sentinel.ps1
- Daily summary: C:\Users\raest\Documents\Karma_SADE\Scripts\sentinel-daily-summary.ps1

### Scheduled Tasks
- KarmaSADE-Sentinel: runs every 15 minutes
- KarmaSADE-DailySummary: runs daily at 11:59 PM

## 5. Sentinel Outputs and Logs

Log locations:

- Sentinel logs directory: C:\Users\raest\Documents\Karma_SADE\Logs
- Runtime log: sentinel-runtime.log (appended every 15 minutes)
- Latest status: sentinel-latest.json (overwritten each run, JSON format)
- Daily summary: sentinel-daily-summary.log (appended nightly)

These logs can be summarized into memory documents and added to Open WebUI Knowledge for historical analysis.

## 5. Interaction with Karma SADE Architect

- Karma SADE Architect should be aware of the Sentinel design and log locations.
- When the user asks about "health" or "recent issues", Architect should:
  1) Refer to this document for design intent,
  2) Read actual Sentinel logs (via tools, when configured),
  3) Combine both to provide advice.

## 6. Future Work

- Define precise thresholds for "warning" and "critical" states.
- Define notification methods (e.g., simple text files, desktop notifications, or emails).
- Document any scripts or scheduled tasks used to run Sentinel and update this file accordingly.
