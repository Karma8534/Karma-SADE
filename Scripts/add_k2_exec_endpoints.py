#!/usr/bin/env python3
"""
Add K2 execution endpoints to karma-server/server.py

Inserts /v1/k2-exec (PowerShell command execution) and /v1/k2-write (file deployment)
endpoints to enable Karma direct control over K2 via WinRM.
"""

ENDPOINTS_CODE = '''

# ─── K2 Remote Execution Interface ────────────────────────────────────────

@app.post("/v1/k2-exec")
async def k2_exec(request: Request):
    """
    Execute PowerShell or CMD commands on K2 (192.168.0.226) via WinRM.

    Request body: {
        command: str,      # PowerShell or CMD command to execute
        mode: str          # "ps" (PowerShell) or "cmd" (CMD), default: "ps"
    }

    Returns: {
        stdout: str,       # Command output
        stderr: str,       # Error output
        status_code: int   # Exit code
    }
    """
    import winrm
    import os

    try:
        data = await request.json()
        command = data.get("command")
        mode = data.get("mode", "ps")  # ps or cmd

        if not command:
            return {"error": "No command provided"}, 400

        # Get K2 credentials from environment
        k2_host = os.getenv("K2_HOST", "192.168.0.226")
        k2_port = os.getenv("K2_WINRM_PORT", "5985")
        k2_user = os.getenv("K2_USERNAME", "karma")
        k2_pass = os.getenv("K2_PASSWORD", "")

        if not k2_pass:
            return {"error": "K2_PASSWORD not configured"}, 500

        # Create WinRM session
        endpoint = f"http://{k2_host}:{k2_port}/wsman"
        session = winrm.Session(
            endpoint,
            auth=(k2_user, k2_pass),
            transport="ntlm"
        )

        # Execute command
        if mode == "ps":
            result = session.run_ps(command)
        elif mode == "cmd":
            result = session.run_cmd(command)
        else:
            return {"error": f"Unknown mode: {mode}"}, 400

        return {
            "stdout": result.std_out.decode("utf-8", errors="replace"),
            "stderr": result.std_err.decode("utf-8", errors="replace"),
            "status_code": result.status_code,
            "mode": mode,
            "command": command[:100]  # First 100 chars for logging
        }

    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "details": traceback.format_exc()
        }, 500


@app.post("/v1/k2-write")
async def k2_write(request: Request):
    """
    Write a file to K2 (192.168.0.226) via WinRM.

    Request body: {
        filepath: str,     # Full path on K2, e.g. C:\\\\Users\\\\karma\\\\karma_files.py
        content: str       # File content as string
    }

    Returns: {
        stdout: str,       # PowerShell output
        stderr: str,       # Error output
        status_code: int,  # Exit code
        filepath: str      # Path written to
    }
    """
    import winrm
    import os
    import base64

    try:
        data = await request.json()
        filepath = data.get("filepath")
        content = data.get("content")

        if not filepath or content is None:
            return {"error": "filepath and content required"}, 400

        # Get K2 credentials from environment
        k2_host = os.getenv("K2_HOST", "192.168.0.226")
        k2_port = os.getenv("K2_WINRM_PORT", "5985")
        k2_user = os.getenv("K2_USERNAME", "karma")
        k2_pass = os.getenv("K2_PASSWORD", "")

        if not k2_pass:
            return {"error": "K2_PASSWORD not configured"}, 500

        # Create WinRM session
        endpoint = f"http://{k2_host}:{k2_port}/wsman"
        session = winrm.Session(
            endpoint,
            auth=(k2_user, k2_pass),
            transport="ntlm"
        )

        # Encode content as base64 to avoid PowerShell quoting nightmares
        encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")

        ps_script = f"""
$bytes = [System.Convert]::FromBase64String('{encoded}')
$content = [System.Text.Encoding]::UTF8.GetString($bytes)
$dir = Split-Path -Parent '{filepath}'
if (-not (Test-Path $dir)) {{
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
}}
$content | Out-File -FilePath '{filepath}' -Encoding utf8 -Force
Write-Host "Wrote $($(Get-Item '{filepath}').Length) bytes to {filepath}"
"""

        result = session.run_ps(ps_script)

        return {
            "stdout": result.std_out.decode("utf-8", errors="replace"),
            "stderr": result.std_err.decode("utf-8", errors="replace"),
            "status_code": result.status_code,
            "filepath": filepath,
            "content_length": len(content)
        }

    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "details": traceback.format_exc()
        }, 500

'''

def add_endpoints():
    """Read server.py, insert K2 exec endpoints before K2 polling endpoints."""

    server_file = "/opt/seed-vault/memory_v1/karma-core/server.py"

    with open(server_file, "r") as f:
        content = f.read()

    # Check if endpoints already exist
    if "/v1/k2-exec" in content:
        print("INFO: K2 exec endpoints already exist")
        return True

    # Find the K2 polling endpoints section
    polling_marker = '@app.get("/v1/k2-proposals")'
    if polling_marker not in content:
        print("ERROR: Could not find K2 polling section marker")
        return False

    insert_pos = content.find(polling_marker)

    # Insert the new code before polling endpoints
    new_content = content[:insert_pos] + ENDPOINTS_CODE + "\n\n" + content[insert_pos:]

    with open(server_file, "w") as f:
        f.write(new_content)

    print("✓ K2 execution endpoints added to server.py")
    return True


if __name__ == "__main__":
    success = add_endpoints()
    exit(0 if success else 1)
