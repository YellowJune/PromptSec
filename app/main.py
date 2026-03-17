"""FastAPI application entry point for PromptSec platform."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.api.routes import detect, analyze, redteam
from app.storage.postgres_db import init_db
from app.storage.redis_cache import init_redis
from app.models.loader import load_llm_models, get_available_models


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown lifecycle."""
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    await init_db()
    await init_redis()
    await load_llm_models()
    logger.info("Application startup complete.")
    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include API routes
app.include_router(detect.router, prefix="/api/v1", tags=["Detection"])
app.include_router(analyze.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(redteam.router, prefix="/api/v1", tags=["Red Teaming"])


@app.get("/healthz")
async def healthz() -> dict:
    return {
        "status": "ok",
        "version": settings.VERSION,
        "models_loaded": get_available_models(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
