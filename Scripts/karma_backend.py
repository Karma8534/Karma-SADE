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

# Import existing dashboard addon and quota manager
import sys
sys.path.append(str(Path(__file__).parent))
import cockpit_dashboard_addon
from karma_quota_manager import quota_manager

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

# 4. Z.ai GLM (FREE Flash models + PAID GLM-5, ~$0.004/query)
ZAI_AVAILABLE = False
zai_client = None
try:
    from openai import OpenAI  # Z.ai uses OpenAI-compatible API
    zai_key = load_api_key_from_registry("ZAI_API_KEY")
    if zai_key:
        zai_client = OpenAI(
            api_key=zai_key,
            base_url="https://open.bigmodel.cn/api/paas/v4"
        )
        ZAI_AVAILABLE = True
        logger.info("[OK] Z.ai GLM available (FREE Flash + PAID GLM-5)")
    else:
        logger.info("[INFO] ZAI_API_KEY not set - skipping Z.ai")
except Exception as e:
    logger.warning(f"[WARN] Z.ai initialization failed: {e}")

# 5. Perplexity (PAID - good for research, ~$0.001/query)
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

# 6. Claude (PAID - expensive, QUOTA MANAGED - 30 queries/day)
CLAUDE_AVAILABLE = False
claude_client = None
try:
    claude_key = load_api_key_from_registry("ANTHROPIC_API_KEY") or load_api_key_from_registry("CLAUDE_API_KEY")
    if claude_key:
        claude_client = anthropic.Anthropic(api_key=claude_key)
        CLAUDE_AVAILABLE = True
        logger.info("[OK] Claude available (PAID - QUOTA: 30/day, premium tier)")
    else:
        logger.info("[INFO] ANTHROPIC_API_KEY not set - skipping Claude")
except Exception as e:
    logger.warning(f"[WARN] Claude initialization failed: {e}")

# Log final configuration
total_backends = sum([OLLAMA_AVAILABLE, GEMINI_AVAILABLE, OPENAI_AVAILABLE, ZAI_AVAILABLE, PERPLEXITY_AVAILABLE, CLAUDE_AVAILABLE])
logger.info(f"[CONFIG] {total_backends} AI backends available")

# Log quota status
if CLAUDE_AVAILABLE or OPENAI_AVAILABLE or ZAI_AVAILABLE or PERPLEXITY_AVAILABLE:
    logger.info("[QUOTA] Paid API quota management enabled")
    daily_stats = {
        "claude": quota_manager.get_daily_usage("claude")[0],
        "openai": quota_manager.get_daily_usage("openai")[0],
        "zai_paid": quota_manager.get_daily_usage("zai_paid")[0],
        "perplexity": quota_manager.get_daily_usage("perplexity")[0]
    }
    logger.info(f"[QUOTA] Today's usage: Claude={daily_stats['claude']}/30, OpenAI={daily_stats['openai']}/100, GLM-5={daily_stats['zai_paid']}/200, Perplexity={daily_stats['perplexity']}/50")
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
    """Detect if task is simple, medium, complex, or premium"""
    message_lower = message.lower()

    # Premium keywords - need Claude's best reasoning (architecture, system design)
    premium_keywords = ["architect", "design system", "refactor everything", "deep analysis", "system design", "evaluate approach"]
    if any(kw in message_lower for kw in premium_keywords):
        return "premium"

    # Complex keywords - need good reasoning (GLM-5, OpenAI, or Claude)
    complex_keywords = ["design", "refactor", "multi-step", "complex", "integrate", "research", "compare", "analyze"]
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
    """Call OpenAI API - PAID (~$0.0025/query, quota: 100/day)"""
    # Check quota
    can_use, reason = quota_manager.check_quota("openai")
    if not can_use:
        logger.warning(f"[QUOTA] OpenAI blocked: {reason}")
        return None

    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            max_tokens=1000
        )

        # Calculate cost (rough estimate)
        total_tokens = response.usage.total_tokens
        cost = total_tokens / 1_000_000 * 0.15 if model == "gpt-4o-mini" else total_tokens / 1_000_000 * 2.5

        # Record usage
        quota_manager.record_usage(
            "openai",
            cost=cost,
            tokens_input=response.usage.prompt_tokens,
            tokens_output=response.usage.completion_tokens,
            model=model,
            success=True
        )

        logger.info(f"[OK] OpenAI {model} - tokens: {total_tokens}, cost: ${cost:.4f}")
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"OpenAI error: {e}")
        quota_manager.record_usage("openai", cost=0, success=False)
        return None

def call_zai(message: str, model: str = "GLM-4-Flash", complexity: str = "simple") -> Optional[str]:
    """Call Z.ai GLM API - FREE Flash models or PAID GLM-5 (quota: 200/day)"""
    # Smart model selection based on complexity
    if complexity == "simple":
        model = "GLM-4-Flash"  # FREE
        is_paid = False
    elif complexity == "medium" and "code" in message.lower():
        model = "GLM-4-Flash"  # FREE, good for basic code
        is_paid = False
    elif complexity == "complex" and "code" in message.lower():
        model = "GLM-5-Code"  # PAID, excellent for complex code
        is_paid = True
    elif complexity == "complex":
        model = "GLM-5"  # PAID, best reasoning
        is_paid = True
    else:
        model = "GLM-4-FlashX"  # CHEAP fallback
        is_paid = True

    # Check quota for paid models
    if is_paid:
        can_use, reason = quota_manager.check_quota("zai_paid")
        if not can_use:
            logger.warning(f"[QUOTA] Z.ai GLM-5 blocked: {reason}")
            return None

    try:
        response = zai_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            max_tokens=2000
        )

        # Record usage for paid models
        if is_paid:
            # Estimate cost
            if "GLM-5-Code" in model:
                cost = 0.006  # Rough estimate
            elif "GLM-5" in model:
                cost = 0.004
            else:
                cost = 0.0005  # FlashX

            quota_manager.record_usage(
                "zai_paid",
                cost=cost,
                tokens_input=0,  # Z.ai doesn't return token counts
                tokens_output=0,
                model=model,
                success=True
            )
            logger.info(f"[OK] Z.ai {model} (PAID) - cost: ${cost:.4f}")
        else:
            logger.info(f"[OK] Z.ai {model} (FREE)")

        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Z.ai error: {e}")
        if is_paid:
            quota_manager.record_usage("zai_paid", cost=0, success=False)
        return None

def call_perplexity(message: str, model: str = "llama-3.1-sonar-small-128k-online") -> Optional[str]:
    """Call Perplexity API - CHEAP, great for research with web search (quota: 100/day)"""
    # Check quota
    can_use, reason = quota_manager.check_quota("perplexity")
    if not can_use:
        logger.warning(f"[QUOTA] Perplexity blocked: {reason}")
        return None

    try:
        response = perplexity_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}]
        )

        # Estimate cost
        cost = 0.001  # Average cost per query

        # Record usage
        quota_manager.record_usage(
            "perplexity",
            cost=cost,
            tokens_input=0,
            tokens_output=0,
            model=model,
            success=True
        )

        logger.info(f"[OK] Perplexity {model} - cost: ${cost:.4f}")
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Perplexity error: {e}")
        quota_manager.record_usage("perplexity", cost=0, success=False)
        return None

def call_claude(message: str, conversation_history: List[Dict] = None) -> Optional[str]:
    """Call Claude API - PREMIUM TIER (quota managed, 30/day)"""
    # Check quota first
    can_use, reason = quota_manager.check_quota("claude")
    if not can_use:
        logger.warning(f"[QUOTA] Claude blocked: {reason}")
        return None

    try:
        messages = []
        for msg in (conversation_history or [])[-10:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        messages.append({"role": "user", "content": message})

        response = claude_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            messages=messages,
            system="You are Karma, an agentic AI assistant with full system access. Be concise and helpful."
        )

        # Calculate actual cost
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens / 1_000_000 * 3.0) + (output_tokens / 1_000_000 * 15.0)

        # Record usage
        quota_manager.record_usage(
            "claude",
            cost=cost,
            tokens_input=input_tokens,
            tokens_output=output_tokens,
            model="claude-sonnet-4",
            success=True
        )

        logger.info(f"[OK] Claude response - tokens: {input_tokens + output_tokens}, cost: ${cost:.4f}")
        return response.content[0].text
    except Exception as e:
        logger.error(f"Claude error: {e}")
        quota_manager.record_usage("claude", cost=0, success=False)
        return None

async def get_ai_response(message: str, conversation_history: List[Dict] = None) -> str:
    """
    7-Tier Smart Routing (with Quota Management):
    1. Ollama (FREE - unlimited local)
    2. Z.ai GLM-4-Flash (FREE - cloud backup)
    3. Gemini (FREE - 1,500/day)
    4. Z.ai GLM-5 (PAID - $0.004/query, quota: 250/day)
    5. OpenAI (PAID - $0.0025/query, quota: 150/day)
    6. Perplexity (PAID - $0.001/query, quota: 100/day)
    7. Claude (PREMIUM - $0.015/query, quota: 71/day - SAVE FOR CRITICAL TASKS!)
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

    # Tier 2: Try Z.ai GLM-4-Flash (FREE, unlimited)
    if ZAI_AVAILABLE and complexity in ["simple", "medium"]:
        logger.info(f"[ROUTE] Trying Z.ai GLM-4-Flash (FREE)")
        response = call_zai(message, model="GLM-4-Flash", complexity=complexity)
        if response:
            return f"[Z.ai GLM-4-Flash - $0.00]\n\n{response}"
        else:
            logger.info("Z.ai Flash failed, trying next tier...")

    # Tier 3: Try Gemini (FREE, 1,500/day)
    if GEMINI_AVAILABLE and complexity in ["simple", "medium"]:
        logger.info(f"[ROUTE] Trying Gemini (FREE - 1,500/day)")
        response = call_gemini(message)
        if response:
            return f"[Gemini 1.5 Flash - $0.00]\n\n{response}"
        else:
            logger.info("Gemini failed, trying next tier...")

    # Tier 4: Try Z.ai GLM-5 (PAID but cheap, excellent for complex tasks)
    if ZAI_AVAILABLE and complexity in ["complex", "premium"]:
        logger.info(f"[ROUTE] Trying Z.ai GLM-5 (PAID - ~$0.004/query, quota: 250/day)")
        response = call_zai(message, model="GLM-5", complexity=complexity)
        if response:
            model_used = "GLM-5-Code" if "code" in message.lower() else "GLM-5"
            return f"[Z.ai {model_used} - ~$0.004]\n\n{response}"
        else:
            logger.info("Z.ai GLM-5 failed, trying next tier...")

    # Tier 5: Try OpenAI (PAID, good for code)
    if OPENAI_AVAILABLE and complexity in ["complex", "premium"]:
        logger.info(f"[ROUTE] Trying OpenAI (PAID - ~$0.0025/query, quota: 150/day)")
        # Use cheaper model for complex, GPT-4o for premium
        model = "gpt-4o-mini" if complexity != "premium" else "gpt-4o"
        response = call_openai(message, model=model)
        if response:
            return f"[OpenAI {model} - ~$0.0025]\n\n{response}"
        else:
            logger.info("OpenAI failed, trying next tier...")

    # Tier 6: Try Perplexity (CHEAPEST PAID - research specialist)
    if PERPLEXITY_AVAILABLE and "research" in message.lower():
        logger.info(f"[ROUTE] Trying Perplexity (PAID - research, quota: 100/day)")
        response = call_perplexity(message)
        if response:
            return f"[Perplexity Llama 3.1 Sonar - ~$0.001]\n\n{response}"
        else:
            logger.info("Perplexity failed, trying Claude...")

    # Tier 7: Claude (PREMIUM - use ONLY for critical architecture/design tasks)
    if CLAUDE_AVAILABLE and complexity == "premium":
        logger.info(f"[ROUTE] PREMIUM TASK - Using Claude (quota: 71/day, $15 budget)")
        response = call_claude(message, conversation_history)
        if response:
            return f"[Claude Sonnet 4 - PREMIUM - ~$0.015]\n\n{response}"
        else:
            logger.warning("Claude failed or quota exceeded")

    # Final fallback - if we have quota remaining, try any available paid API
    if complexity in ["complex", "premium"]:
        # Try any remaining APIs with quota
        if OPENAI_AVAILABLE:
            logger.info("[FALLBACK] Trying OpenAI as final fallback")
            response = call_openai(message, model="gpt-4o-mini")
            if response:
                return f"[OpenAI gpt-4o-mini - FALLBACK]\n\n{response}"

    # No AI available
    return "Error: No AI backend available or all quotas exceeded. Please check quota status."

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

            # Get AI response using smart routing
            full_response = await get_ai_response(
                user_message,
                conversation_history=conversations[conversation_id][:-1]  # Exclude the just-added user message
            )

            # Send complete response to client
            await websocket.send_json({
                "type": "response",
                "content": full_response
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


@app.get("/api/quota/stats")
async def get_quota_stats():
    """Get quota usage statistics for all paid APIs."""
    return quota_manager.get_all_usage_stats()


@app.get("/api/quota/report")
async def get_quota_report():
    """Get formatted quota usage report."""
    return {
        "report": quota_manager.get_usage_report(),
        "stats": quota_manager.get_all_usage_stats()
    }


@app.post("/api/quota/update")
async def update_quota(api_name: str, daily_limit: int = None, monthly_limit: int = None):
    """Update quota limits for a specific API."""
    try:
        quota_manager.update_quota(api_name, daily_limit, monthly_limit)
        return {"status": "success", "message": f"Updated quota for {api_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
