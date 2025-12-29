"""FastAPI application for miu-studio."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from miu_studio.api.routes import chat, health, sessions
from miu_studio.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown."""
    # Startup
    session_dir = Path(settings.session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    yield
    # Shutdown - cleanup if needed


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="miu Studio",
        description="Web server for miu AI agent",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, prefix="/api/v1")
    app.include_router(sessions.router, prefix="/api/v1/sessions")
    app.include_router(chat.router, prefix="/api/v1/chat")

    # Static files (will be used for web UI)
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    return app
