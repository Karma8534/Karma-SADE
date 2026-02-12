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

# ============================================================================
# Load API keys from Windows registry (if not in environment)
# ============================================================================
def load_api_key_from_registry(key_name: str) -> Optional[str]:
    """Load API key from Windows registry if not in environment"""
    if os.environ.get(key_name):
        return os.environ.get(key_name)

    try:
        result = subprocess.run(
            ["powershell", "-Command",
             f"Get-ItemProperty -Path 'HKCU:\\Environment' -Name {key_name} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty {key_name}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            key = result.stdout.strip()
            os.environ[key_name] = key  # Set in environment for this session
            return key
    except:
        pass
    return None

# ============================================================================
# Multi-API Client Initialization
# Priority: Ollama (FREE) → Gemini (FREE) → OpenAI (CHEAP) → Claude (EXPENSIVE)
# ============================================================================

# 1. Ollama (FREE - local, unlimited)
import subprocess
OLLAMA_AVAILABLE = False
try:
    subprocess.run(["ollama", "list"], capture_output=True, check=True, timeout=5)
    OLLAMA_AVAILABLE = True
    logger.info("[OK] Ollama available (FREE - unlimited local)")
except:
    logger.warning("[WARN] Ollama not available")

# 2. Gemini (FREE - 1,500 requests/day)
GEMINI_AVAILABLE = False
gemini_client = None
try:
    import google.generativeai as genai
    gemini_key = load_api_key_from_registry("GEMINI_API_KEY")
    if gemini_key:
        genai.configure(api_key=gemini_key)
        gemini_client = genai.GenerativeModel('gemini-1.5-flash')
        GEMINI_AVAILABLE = True
        logger.info("[OK] Gemini available (FREE - 1,500/day)")
    else:
        logger.info("[INFO] GEMINI_API_KEY not set - skipping Gemini")
except ImportError:
    logger.warning("[WARN] google-generativeai not installed: pip install google-generativeai")
except Exception as e:
    logger.warning(f"[WARN] Gemini initialization failed: {e}")

# 3. OpenAI (PAID - cheap, ~$0.0025/query)
OPENAI_AVAILABLE = False
openai_client = None
try:
    from openai import OpenAI
    openai_key = load_api_key_from_registry("OPENAI_API_KEY")
    if openai_key:
        openai_client = OpenAI(api_key=openai_key)
        OPENAI_AVAILABLE = True
        logger.info("[OK] OpenAI available (PAID - ~$0.0025/query)")
    else:
        logger.info("[INFO] OPENAI_API_KEY not set - skipping OpenAI")
except ImportError:
    logger.warning("[WARN] openai not installed: pip install openai")
except Exception as e:
    logger.warning(f"[WARN] OpenAI initialization failed: {e}")

# 4. Perplexity (PAID - good for research, ~$0.001/query)
PERPLEXITY_AVAILABLE = False
perplexity_client = None
try:
    from openai import OpenAI  # Perplexity uses OpenAI-compatible API
    perplexity_key = load_api_key_from_registry("PERPLEXITY_API_KEY")
    if perplexity_key:
        perplexity_client = OpenAI(
            api_key=perplexity_key,
            base_url="https://api.perplexity.ai"
        )
        PERPLEXITY_AVAILABLE = True
        logger.info("[OK] Perplexity available (PAID - research specialist)")
    else:
        logger.info("[INFO] PERPLEXITY_API_KEY not set - skipping Perplexity")
except Exception as e:
    logger.warning(f"[WARN] Perplexity initialization failed: {e}")

# 5. Claude (PAID - expensive, DISABLED due to no credits)
CLAUDE_AVAILABLE = False
claude_client = None
try:
    claude_key = load_api_key_from_registry("ANTHROPIC_API_KEY") or load_api_key_from_registry("CLAUDE_API_KEY")
    if claude_key:
        # DISABLED: No credits available
        # claude_client = anthropic.Anthropic(api_key=claude_key)
        # CLAUDE_AVAILABLE = True
        logger.info("[DISABLED] Claude API - no credits available")
    else:
        logger.info("[INFO] ANTHROPIC_API_KEY not set - skipping Claude")
except Exception as e:
    logger.warning(f"[WARN] Claude initialization failed: {e}")

# Log final configuration
total_backends = sum([OLLAMA_AVAILABLE, GEMINI_AVAILABLE, OPENAI_AVAILABLE, CLAUDE_AVAILABLE])
logger.info(f"[CONFIG] {total_backends} AI backends available")
if total_backends == 0:
    logger.error("[ERROR] No AI backends available! Please configure at least one API key or install Ollama.")

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
# Smart Model Routing (Ollama First, Claude Fallback)
# ============================================================================

def detect_task_complexity(message: str) -> str:
    """Detect if task is simple, medium, or complex"""
    message_lower = message.lower()

    # Complex keywords - need research/deep reasoning (Perplexity or OpenAI)
    complex_keywords = ["architect", "design", "refactor", "multi-step", "complex", "integrate", "research", "compare", "analyze"]
    if any(kw in message_lower for kw in complex_keywords):
        return "complex"

    # Simple keywords - Ollama can handle
    simple_keywords = ["what is", "explain", "how to", "list", "show", "check", "status"]
    if any(kw in message_lower for kw in simple_keywords):
        return "simple"

    return "medium"

def call_ollama(message: str, model: str = "llama3.1", timeout: int = 60) -> Optional[str]:
    """Call Ollama directly - FREE"""
    try:
        result = subprocess.run(
            ["ollama", "run", model, message],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            logger.info(f"[OK] Ollama response (FREE) - model: {model}")
            return result.stdout.strip()
        else:
            logger.warning(f"Ollama error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        logger.warning(f"Ollama timeout after {timeout}s")
        return None
    except Exception as e:
        logger.error(f"Ollama failed: {e}")
        return None

def call_gemini(message: str, timeout: int = 30) -> Optional[str]:
    """Call Gemini API - FREE (1,500 requests/day)"""
    try:
        response = gemini_client.generate_content(message)
        logger.info("[OK] Gemini response (FREE - 1,500/day)")
        return response.text
    except Exception as e:
        logger.warning(f"Gemini error: {e}")
        return None

def call_openai(message: str, model: str = "gpt-4o-mini") -> Optional[str]:
    """Call OpenAI API - CHEAP (~$0.0025/query)"""
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            max_tokens=1000
        )
        logger.info(f"[OK] OpenAI response (PAID - {model}) - tokens: {response.usage.total_tokens}")
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"OpenAI error: {e}")
        return None

def call_perplexity(message: str, model: str = "llama-3.1-sonar-small-128k-online") -> Optional[str]:
    """Call Perplexity API - CHEAP, great for research with web search"""
    try:
        response = perplexity_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}]
        )
        logger.info(f"[OK] Perplexity response (PAID - {model})")
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Perplexity error: {e}")
        return None

def call_claude(message: str, conversation_history: List[Dict] = None) -> Optional[str]:
    """Call Claude API - DISABLED (no credits available)"""
    logger.warning("[DISABLED] Claude API called but is disabled due to no credits")
    return None

async def get_ai_response(message: str, conversation_history: List[Dict] = None) -> str:
    """
    4-Tier Smart Routing:
    1. Ollama (FREE - unlimited local)
    2. Gemini (FREE - 1,500/day)
    3. OpenAI (CHEAP - ~$0.0025/query)
    4. Claude (EXPENSIVE - last resort)
    """
    complexity = detect_task_complexity(message)
    conversation_history = conversation_history or []

    # Tier 1: Always try Ollama first (FREE, unlimited)
    if complexity in ["simple", "medium"] and OLLAMA_AVAILABLE:
        logger.info(f"[ROUTE] Task complexity: {complexity} - Trying Ollama (FREE)")

        # Choose appropriate Ollama model
        if "code" in message.lower():
            model = "deepseek-coder:6.7b"
        else:
            model = "llama3.1"

        response = call_ollama(message, model=model)

        if response:
            return f"[Ollama/{model} - $0.00]\n\n{response}"
        else:
            logger.info("Ollama failed, trying next tier...")

    # Tier 2: Try Gemini (FREE, 1,500/day)
    if GEMINI_AVAILABLE and complexity in ["simple", "medium"]:
        logger.info(f"[ROUTE] Trying Gemini (FREE - 1,500/day)")
        response = call_gemini(message)
        if response:
            return f"[Gemini 1.5 Flash - $0.00]\n\n{response}"
        else:
            logger.info("Gemini failed, trying next tier...")

    # Tier 3: Try OpenAI (CHEAP, good for code)
    if OPENAI_AVAILABLE:
        logger.info(f"[ROUTE] Trying OpenAI (PAID - ~$0.0025/query)")
        # Use cheaper model for simple/medium, GPT-4o for complex
        model = "gpt-4o-mini" if complexity != "complex" else "gpt-4o"
        response = call_openai(message, model=model)
        if response:
            return f"[OpenAI {model} - ~$0.0025]\n\n{response}"
        else:
            logger.info("OpenAI failed, trying next tier...")

    # Tier 4: Claude (EXPENSIVE - last resort)
    if CLAUDE_AVAILABLE:
        logger.info(f"[ROUTE] Using Claude (EXPENSIVE - last resort, complexity: {complexity})")
        response = call_claude(message, conversation_history)
        if response:
            return f"[Claude Sonnet 4 - ~$0.015]\n\n{response}"
        else:
            return "Error: Claude API failed"

    # No AI available
    return "Error: No AI backend available. Please configure at least one API key or install Ollama."

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

    try:
        # Smart routing: Ollama first, Claude fallback
        response_text = await get_ai_response(
            request.message,
            conversation_history=conversations[conversation_id][:-1]  # Exclude current message
        )

        # Response generated by smart routing (Ollama or Claude)

        # Store assistant response
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
    """Serve the original dashboard."""
    dashboard_file = DASHBOARD_DIR / "index.html"
    if dashboard_file.exists():
        return HTMLResponse(content=dashboard_file.read_text())
    return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)

@app.get("/unified", response_class=HTMLResponse)
async def serve_unified_dashboard():
    """Serve the unified 3-panel dashboard with chat."""
    dashboard_file = DASHBOARD_DIR / "unified.html"
    if dashboard_file.exists():
        return HTMLResponse(content=dashboard_file.read_text())
    return HTMLResponse(content="<h1>Unified dashboard not found</h1>", status_code=404)


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

    PORT = 9401  # Use 9401 to avoid conflict with Cockpit on 9400

    print("=" * 70)
    print("Karma SADE Backend v2.0 - Multi-API Edition")
    print("=" * 70)
    print(f"Unified Dashboard: http://localhost:{PORT}/unified")
    print(f"API Docs: http://localhost:{PORT}/docs")
    print(f"WebSocket: ws://localhost:{PORT}/ws/chat/{{conversation_id}}")
    print(f"\nAI Backends Available: {total_backends}")
    if OLLAMA_AVAILABLE:
        print("  - Ollama (FREE - unlimited)")
    if GEMINI_AVAILABLE:
        print("  - Gemini (FREE - 1,500/day)")
    if OPENAI_AVAILABLE:
        print("  - OpenAI (CHEAP - ~$0.0025/query)")
    if CLAUDE_AVAILABLE:
        print("  - Claude (EXPENSIVE - last resort)")
    print("=" * 70)

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=PORT,
        log_level="info",
        access_log=True
    )
