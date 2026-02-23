#!/usr/bin/env python3
"""
Karma File Management Service — K2 Local File Operations

Run on K2 (192.168.0.226):
  pip install fastapi uvicorn
  uvicorn karma_files:app --host 0.0.0.0 --port 8001

Endpoints:
  POST /v1/file-move       — Move files between Inbox/Processing/Done/Gated
  GET  /v1/file-list?folder=...  — List files in folder
  GET  /health             — Health check
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import shutil
import os
from pathlib import Path

app = FastAPI()

# Adjust this path if OneDrive mount point differs on K2
KARMA_ROOT = Path.home() / "OneDrive" / "Karma"

class MoveRequest(BaseModel):
    source: str
    destination: str

def safe_path(p: str) -> Path:
    """Resolve path and verify it stays inside KARMA_ROOT."""
    resolved = (KARMA_ROOT / p).resolve() if not Path(p).is_absolute() else Path(p).resolve()
    if not str(resolved).startswith(str(KARMA_ROOT)):
        raise HTTPException(status_code=403, detail="Path outside Karma root — rejected.")
    return resolved

@app.post("/v1/file-move")
def file_move(req: MoveRequest):
    """Move file from source to destination within KARMA_ROOT."""
    src = safe_path(req.source)
    dst = safe_path(req.destination)

    if not src.exists():
        raise HTTPException(status_code=404, detail=f"Source not found: {src}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))

    return {"status": "ok", "moved": str(src), "to": str(dst)}

@app.get("/v1/file-list")
def file_list(folder: str = "Inbox"):
    """List files in a folder within KARMA_ROOT."""
    target = safe_path(folder)

    if not target.exists():
        raise HTTPException(status_code=404, detail=f"Folder not found: {target}")

    files = [
        {
            "name": f.name,
            "size_bytes": f.stat().st_size,
            "modified": f.stat().st_mtime
        }
        for f in sorted(target.iterdir())
        if f.is_file()
    ]

    return {"folder": str(target), "count": len(files), "files": files}

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "karma_root": str(KARMA_ROOT)}
