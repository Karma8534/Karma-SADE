"""
Karma Cockpit Dashboard Addon v1.0.0
Add this to karma_cockpit_service.py to enable comprehensive system dashboard.

Dashboard provides:
- Service health (Open WebUI, Cockpit, Ollama)
- Scheduled task status
- Recent logs summary
- Watchdog state
- Backup status
- Memory sync status
- System resources
- API health checks

Usage:
1. Import this module in karma_cockpit_service.py
2. Call register_dashboard_routes(app, mgr) after other routes
3. Access via: GET http://localhost:9400/dashboard
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
import logging
from flask import request, send_file

# Paths
LOG_DIR = Path.home() / "Documents" / "Karma_SADE" / "Logs"
SCRIPTS_DIR = Path.home() / "Documents" / "Karma_SADE" / "Scripts"
WATCHDOG_STATE = LOG_DIR / "watchdog-state.json"
SENTINEL_LATEST = LOG_DIR / "sentinel-latest.json"


def check_service_health():
    """Check health of all Karma SADE services."""
    import requests

    services = {
        "ollama": {"url": "http://localhost:11434", "critical": False},
        "openwebui": {"url": "http://localhost:8080", "critical": True},
        "cockpit": {"url": "http://localhost:9400/health", "critical": True},
    }

    results = {}
    for name, config in services.items():
        try:
            resp = requests.get(config["url"], timeout=5)
            results[name] = {
                "status": "healthy" if resp.status_code == 200 else "degraded",
                "code": resp.status_code,
                "critical": config["critical"],
                "url": config["url"],
            }
        except requests.exceptions.RequestException as e:
            results[name] = {
                "status": "down",
                "error": str(e),
                "critical": config["critical"],
                "url": config["url"],
            }

    return results


def check_scheduled_tasks():
    """Check status of all KarmaSADE scheduled tasks."""
    try:
        cmd = 'Get-ScheduledTask -TaskName "KarmaSADE-*" | Select-Object TaskName,State,@{Name="LastRun";Expression={(Get-ScheduledTaskInfo -TaskName $_.TaskName).LastRunTime}},@{Name="LastResult";Expression={(Get-ScheduledTaskInfo -TaskName $_.TaskName).LastTaskResult}} | ConvertTo-Json'
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0 and result.stdout.strip():
            tasks = json.loads(result.stdout)
            # Handle single task (not array)
            if isinstance(tasks, dict):
                tasks = [tasks]

            parsed = []
            for task in tasks:
                parsed.append({
                    "name": task.get("TaskName", "Unknown"),
                    "state": task.get("State", "Unknown"),
                    "last_run": task.get("LastRun"),
                    "last_result": task.get("LastResult", 0),
                    "healthy": task.get("State") == "Ready" and task.get("LastResult", 0) == 0
                })
            return {"status": "ok", "tasks": parsed}
        else:
            return {"status": "error", "error": "Failed to query tasks", "stderr": result.stderr}

    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_watchdog_state():
    """Read watchdog state file."""
    try:
        if WATCHDOG_STATE.exists():
            with open(WATCHDOG_STATE, 'r') as f:
                state = json.load(f)

            # Calculate summary
            summary = {
                "healthy_services": 0,
                "failed_services": 0,
                "gave_up_services": 0,
                "details": {}
            }

            for svc_name, svc_state in state.items():
                fails = svc_state.get("consecutive_fails", 0)
                gave_up = svc_state.get("gave_up", False)

                if gave_up:
                    summary["gave_up_services"] += 1
                elif fails > 0:
                    summary["failed_services"] += 1
                else:
                    summary["healthy_services"] += 1

                summary["details"][svc_name] = {
                    "consecutive_fails": fails,
                    "gave_up": gave_up,
                    "last_restart": svc_state.get("last_restart"),
                    "status": "gave_up" if gave_up else ("failing" if fails > 0 else "healthy")
                }

            return {"status": "ok", "summary": summary}
        else:
            return {"status": "no_data", "message": "Watchdog has not run yet"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_sentinel_status():
    """Read sentinel latest status."""
    try:
        if SENTINEL_LATEST.exists():
            with open(SENTINEL_LATEST, 'r') as f:
                return {"status": "ok", "data": json.load(f)}
        else:
            return {"status": "no_data", "message": "Sentinel has not run yet"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_recent_logs(log_file, lines=20):
    """Get last N lines from a log file."""
    try:
        log_path = LOG_DIR / log_file
        if not log_path.exists():
            return {"status": "no_file", "file": log_file}

        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            recent = all_lines[-lines:] if len(all_lines) > lines else all_lines

        return {
            "status": "ok",
            "file": log_file,
            "lines": [line.strip() for line in recent if line.strip()],
            "total_lines": len(all_lines)
        }
    except Exception as e:
        return {"status": "error", "file": log_file, "error": str(e)}


def get_backup_status():
    """Check backup directory and most recent backup."""
    try:
        backup_dir = Path.home() / "karma" / "backups"
        if not backup_dir.exists():
            return {"status": "no_backups", "message": "Backup directory does not exist"}

        # Find most recent backup
        backups = sorted(backup_dir.glob("webui_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)

        if not backups:
            return {"status": "no_backups", "message": "No backups found"}

        most_recent = backups[0]
        stats = most_recent.stat()
        age_hours = (datetime.now().timestamp() - stats.st_mtime) / 3600

        return {
            "status": "ok",
            "most_recent": {
                "file": most_recent.name,
                "size_mb": round(stats.st_size / (1024*1024), 2),
                "age_hours": round(age_hours, 1),
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "stale": age_hours > 26  # Should run daily at 3am
            },
            "total_backups": len(backups)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_secrets_status():
    """Check if secrets management is configured."""
    try:
        secrets_file = Path.home() / "karma" / "secrets.json"

        if not secrets_file.exists():
            return {
                "status": "not_configured",
                "message": "Secrets file does not exist. API keys may be in plaintext.",
                "action_required": True
            }

        stats = secrets_file.stat()

        # Try to read and count keys
        try:
            with open(secrets_file, 'r') as f:
                secrets = json.load(f)
                key_count = len(secrets) if isinstance(secrets, dict) else len(secrets.__dict__)
        except:
            key_count = "unknown"

        return {
            "status": "configured",
            "key_count": key_count,
            "file_size": stats.st_size,
            "modified": datetime.fromtimestamp(stats.st_mtime).isoformat()
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_system_status():
    """Get overall system health summary."""
    services = check_service_health()
    tasks = check_scheduled_tasks()
    watchdog = get_watchdog_state()
    sentinel = get_sentinel_status()
    backups = get_backup_status()
    secrets = get_secrets_status()

    # Determine overall health
    critical_down = any(
        svc["status"] == "down" and svc["critical"]
        for svc in services.values()
    )

    watchdog_issues = (
        watchdog.get("status") == "ok" and
        (watchdog.get("summary", {}).get("failed_services", 0) > 0 or
         watchdog.get("summary", {}).get("gave_up_services", 0) > 0)
    )

    backup_stale = (
        backups.get("status") == "ok" and
        backups.get("most_recent", {}).get("stale", False)
    )

    secrets_missing = secrets.get("status") == "not_configured"

    # Overall status
    if critical_down:
        overall = "critical"
        message = "Critical services are down"
    elif watchdog_issues:
        overall = "degraded"
        message = "Services have failures"
    elif backup_stale or secrets_missing:
        overall = "warning"
        issues = []
        if backup_stale:
            issues.append("backups stale")
        if secrets_missing:
            issues.append("secrets not configured")
        message = f"Issues: {', '.join(issues)}"
    else:
        overall = "healthy"
        message = "All systems operational"

    return {
        "overall": overall,
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "services": services,
        "scheduled_tasks": tasks,
        "watchdog": watchdog,
        "sentinel": sentinel,
        "backups": backups,
        "secrets": secrets,
    }


def register_dashboard_routes(app, mgr):
    """Register dashboard routes with the Flask app."""

    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        """Comprehensive system dashboard."""
        # If requesting HTML (browser), serve the visual dashboard
        if 'text/html' in request.headers.get('Accept', ''):
            dashboard_html = Path.home() / "Documents" / "Karma_SADE" / "Dashboard" / "index.html"
            if dashboard_html.exists():
                return send_file(str(dashboard_html))
        # Otherwise return JSON (API calls)
        return get_system_status()

    @app.route("/dashboard/html", methods=["GET"])
    def dashboard_html_view():
        """Visual HTML dashboard (always returns HTML)."""
        dashboard_file = Path.home() / "Documents" / "Karma_SADE" / "Dashboard" / "index.html"
        if dashboard_file.exists():
            return send_file(str(dashboard_file))
        return {"error": "Dashboard HTML file not found"}, 404

    @app.route("/dashboard/services", methods=["GET"])
    def dashboard_services():
        """Service health only."""
        return check_service_health()

    @app.route("/dashboard/tasks", methods=["GET"])
    def dashboard_tasks():
        """Scheduled tasks status."""
        return check_scheduled_tasks()

    @app.route("/dashboard/watchdog", methods=["GET"])
    def dashboard_watchdog():
        """Watchdog state."""
        return get_watchdog_state()

    @app.route("/dashboard/sentinel", methods=["GET"])
    def dashboard_sentinel():
        """Sentinel status."""
        return get_sentinel_status()

    @app.route("/dashboard/backups", methods=["GET"])
    def dashboard_backups():
        """Backup status."""
        return get_backup_status()

    @app.route("/dashboard/secrets", methods=["GET"])
    def dashboard_secrets():
        """Secrets management status."""
        return get_secrets_status()

    @app.route("/dashboard/logs/<log_name>", methods=["GET"])
    def dashboard_logs(log_name):
        """Get recent log entries."""
        # Security: only allow known log files
        allowed_logs = [
            "karma-watchdog.log",
            "karma-backup.log",
            "karma-startup.log",
            "sentinel-runtime.log",
            "cockpit-service.log",
            "karma-sade.log"
        ]

        if log_name not in allowed_logs:
            return {"error": "Invalid log file"}, 400

        lines = int(request.args.get("lines", 50))
        lines = min(lines, 500)  # Cap at 500 lines

        return get_recent_logs(log_name, lines)

    logging.info("[dashboard] Dashboard routes registered")
