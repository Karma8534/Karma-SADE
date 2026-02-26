"""
Karma Self-Model — Vault API endpoint integration

Adds /v1/self-model endpoints to the karma-core server:
  GET  /v1/self-model          → Returns current self-model summary (for prompt injection)
  POST /v1/self-model/reflect  → Writes session reflections to 13-self-model.json
  POST /v1/self-model/prune    → Manual pruning trigger

These endpoints are called by Karma during sessions (via hub-bridge tool-use)
and by the system prompt generator on session start.

Integration: Import this module in server.py and call register_self_model_routes(app)
"""
from typing import Optional

# Import from self_reflection module (same karma-core package)
from self_reflection import (
    reflect_on_session,
    prune_self_model,
    get_self_model_summary,
    SELF_MODEL_PATH,
)


def register_self_model_routes(app, require_auth_fn=None):
    """Register self-model API routes on a FastAPI/Starlette app.

    Usage in server.py:
        from self_model_api import register_self_model_routes
        register_self_model_routes(app)
    """
    from starlette.requests import Request
    from starlette.responses import JSONResponse

    @app.route("/v1/self-model", methods=["GET"])
    async def get_self_model(request: Request):
        """Return self-model summary as text for prompt injection."""
        try:
            summary = get_self_model_summary()
            return JSONResponse({
                "ok": True,
                "summary": summary,
                "path": SELF_MODEL_PATH,
            })
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    @app.route("/v1/self-model/reflect", methods=["POST"])
    async def reflect(request: Request):
        """Write session reflections to self-model.

        Body: {
            "session_id": "session_38",
            "observations": [
                {
                    "category": "communication_style",
                    "observation": "I over-explain on short questions",
                    "confidence": 0.8,
                    "evidence": "Colby said 'too long' in session 37"
                }
            ]
        }
        """
        try:
            body = await request.json()
            observations = body.get("observations", [])
            session_id = body.get("session_id", None)

            if not observations:
                return JSONResponse(
                    {"ok": False, "error": "No observations provided"},
                    status_code=400
                )

            result = reflect_on_session(
                observations=observations,
                session_id=session_id,
            )
            return JSONResponse(result)
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    @app.route("/v1/self-model/prune", methods=["POST"])
    async def prune(request: Request):
        """Manual pruning trigger — removes decayed entries."""
        try:
            result = prune_self_model()
            return JSONResponse({"ok": True, **result})
        except Exception as e:
            return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
