"""
Karma SADE Backend v2.0
Unified backend for Agentic Karma with integrated chat, tools, and monitoring.

Replaces Open WebUI with a lightweight FastAPI + Claude integration.
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic

# Import existing dashboard addon
import sys
sys.path.append(str(Path(__file__).parent))
import cockpit_dashboard_addon

# Configuration
LOG_DIR = Path.home() / "Documents" / "Karma_SADE" / "Logs"
MEMORY_DIR = Path.home() / "karma" / "memory"
DASHBOARD_DIR = Path.home() / "Documents" / "Karma_SADE" / "Dashboard"

LOG_DIR.mkdir(parents=True, exist_ok=True)
MEMORY_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "karma-backend.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="Karma SADE Backend", version="2.0.0")

# CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Local use only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Claude client
claude_client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
)

# Active WebSocket connections
active_connections: List[WebSocket] = []

# Conversation storage (simple in-memory for now, will add persistence)
conversations: Dict[str, List[Dict]] = {}

# Models
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    stream: bool = True

class ConversationResponse(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]

# ============================================================================
# Chat Endpoints
# ============================================================================

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Send a message to Claude and get a response.
    Supports streaming via WebSocket (preferred) or HTTP.
    """
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Get or create conversation history
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    # Add user message
    user_msg = {
        "role": "user",
        "content": request.message,
        "timestamp": datetime.now().isoformat()
    }
    conversations[conversation_id].append(user_msg)

    # Prepare messages for Claude
    claude_messages = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in conversations[conversation_id]
    ]

    try:
        # Call Claude
        response = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=claude_messages,
            system="You are Karma, an agentic AI assistant with full system access. You help Neo with coding, system administration, research, and automation. You have access to browser control, file system, and command execution via MCP tools. You are direct, technically precise, and proactive."
        )

        # Extract response
        assistant_msg = {
            "role": "assistant",
            "content": response.content[0].text,
            "timestamp": datetime.now().isoformat()
        }
        conversations[conversation_id].append(assistant_msg)

        # Log usage
        logger.info(f"Chat: {request.message[:50]}... -> {len(response.content[0].text)} chars")
        logger.info(f"Tokens: in={response.usage.input_tokens}, out={response.usage.output_tokens}")

        return {
            "conversation_id": conversation_id,
            "response": assistant_msg["content"],
            "timestamp": assistant_msg["timestamp"],
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens
            }
        }

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """
    WebSocket endpoint for streaming chat with Claude.
    Provides real-time streaming responses.
    """
    await websocket.accept()
    active_connections.append(websocket)

    logger.info(f"WebSocket connected: {conversation_id}")

    # Get or create conversation
    if conversation_id not in conversations:
        conversations[conversation_id] = []

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            user_message = message_data.get("message", "")

            # Add to conversation
            conversations[conversation_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.now().isoformat()
            })

            # Prepare messages for Claude
            claude_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in conversations[conversation_id]
            ]

            # Stream response from Claude
            full_response = ""

            with claude_client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=claude_messages,
                system="You are Karma, an agentic AI assistant with full system access. You help Neo with coding, system administration, research, and automation. You have access to browser control, file system, and command execution via MCP tools. You are direct, technically precise, and proactive."
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    # Send chunk to client
                    await websocket.send_json({
                        "type": "chunk",
                        "content": text
                    })

            # Send completion signal
            await websocket.send_json({
                "type": "complete",
                "full_response": full_response
            })

            # Save assistant response
            conversations[conversation_id].append({
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().isoformat()
            })

            logger.info(f"Streamed response: {len(full_response)} chars")

    except WebSocketDisconnect:
        active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected: {conversation_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


@app.get("/api/conversations")
async def get_conversations():
    """Get list of all conversations."""
    return {
        "conversations": [
            {
                "id": conv_id,
                "message_count": len(messages),
                "last_updated": messages[-1]["timestamp"] if messages else None
            }
            for conv_id, messages in conversations.items()
        ]
    }


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation."""
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id in conversations:
        del conversations[conversation_id]
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Conversation not found")


# ============================================================================
# Dashboard Integration (Reuse existing)
# ============================================================================

# Register existing dashboard routes
cockpit_dashboard_addon.register_dashboard_routes(app, None)

# Serve dashboard HTML
@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the enhanced dashboard with chat panel."""
    dashboard_file = DASHBOARD_DIR / "index.html"
    if dashboard_file.exists():
        return HTMLResponse(content=dashboard_file.read_text())
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


# ============================================================================
# Health & Status
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "karma-backend",
        "version": "2.0.0",
        "active_connections": len(active_connections),
        "conversations": len(conversations),
        "claude_configured": bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY"))
    }


@app.get("/api/status")
async def get_status():
    """Get detailed system status."""
    return {
        "backend": {
            "version": "2.0.0",
            "uptime": "TODO",
            "memory_usage": "TODO"
        },
        "conversations": {
            "total": len(conversations),
            "active": len(active_connections)
        },
        "models": {
            "claude": "claude-sonnet-4-20250514",
            "available": ["claude-sonnet-4", "ollama-local"]
        }
    }


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    print("=" * 70)
    print("Karma SADE Backend v2.0")
    print("=" * 70)
    print(f"Dashboard: http://localhost:9400")
    print(f"API Docs: http://localhost:9400/docs")
    print(f"WebSocket: ws://localhost:9400/ws/chat/{{conversation_id}}")
    print("=" * 70)

    # Check for API key
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")):
        print("⚠️  WARNING: No Claude API key found!")
        print("   Set ANTHROPIC_API_KEY or CLAUDE_API_KEY environment variable")
        print("=" * 70)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=9400,
        log_level="info",
        access_log=True
    )
