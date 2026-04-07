"""
Karma Harness — FastAPI Backend Entry Point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from core.config import settings

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("karma_starting", version=settings.karma_version, env=settings.karma_env)
    logger.info("providers_available", providers=settings.available_providers)
    # DB init, Redis connect, persona load — wired in Step 2-4
    yield
    logger.info("karma_shutdown")


app = FastAPI(
    title="Karma Harness API",
    version=settings.karma_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:3000", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": settings.karma_version,
        "env": settings.karma_env,
        "providers": settings.available_providers,
    }


# Routers mounted in subsequent steps:
# from api.chat     import router as chat_router
# from api.cowork   import router as cowork_router
# from api.code     import router as code_router
# from api.memory   import router as memory_router
# from api.persona  import router as persona_router
# from api.selfedit import router as selfedit_router
# from api.ws       import router as ws_router
