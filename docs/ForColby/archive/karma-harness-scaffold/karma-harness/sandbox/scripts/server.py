"""
Karma Sandbox Server
Executes code and terminal commands in an isolated container.
Only accessible internally within karma-net.
"""
import asyncio
import os
import subprocess
import uuid
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel

app = FastAPI(title="Karma Sandbox")
SANDBOX_TOKEN = os.getenv("SANDBOX_TOKEN", "")
WORKSPACE = "/workspace"


def verify_token(x_sandbox_token: str = Header(...)):
    if x_sandbox_token != SANDBOX_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid sandbox token")


class ExecRequest(BaseModel):
    language: str        # python | bash | node | shell
    code: str
    timeout: int = 30    # seconds
    session_id: str = ""


class ExecResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    session_id: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "karma-sandbox"}


@app.post("/exec", response_model=ExecResult)
async def execute(req: ExecRequest, x_sandbox_token: str = Header(...)):
    verify_token(x_sandbox_token)

    session_id = req.session_id or str(uuid.uuid4())
    session_dir = os.path.join(WORKSPACE, session_id)
    os.makedirs(session_dir, exist_ok=True)

    language_map = {
        "python": ["python3", "-c"],
        "bash":   ["bash", "-c"],
        "shell":  ["bash", "-c"],
        "node":   ["node", "-e"],
    }

    runner = language_map.get(req.language.lower())
    if not runner:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {req.language}")

    try:
        proc = await asyncio.create_subprocess_exec(
            *runner, req.code,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=session_dir,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=req.timeout
        )
        return ExecResult(
            stdout=stdout.decode("utf-8", errors="replace"),
            stderr=stderr.decode("utf-8", errors="replace"),
            exit_code=proc.returncode or 0,
            session_id=session_id,
        )
    except asyncio.TimeoutError:
        proc.kill()
        return ExecResult(
            stdout="",
            stderr=f"Execution timed out after {req.timeout}s",
            exit_code=124,
            session_id=session_id,
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
