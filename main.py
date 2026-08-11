"""
Main FastAPI Application Entry Point.
App Factory & Middleware Assembly (Layered Architecture).
Python 3.11.2 Compatible.
"""

import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api import routes_media, routes_stats, routes_stream, routes_system
from core.config import STATIC_DIR
from services.library_service import library_service


def create_app() -> FastAPI:
    """Application Factory function."""
    app = FastAPI(
        title="Lightweight 32-Bit Python Media Server",
        description="Layered Architecture Media Server optimized for 32-bit hardware & 720p Direct Play.",
        version="2.0.0"
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Startup event
    @app.on_event("startup")
    async def startup_event():
        loaded = library_service.load_cache()
        if not loaded:
            asyncio.create_task(library_service.refresh_scan())

    # Include API Routers
    app.include_router(routes_media.router)
    app.include_router(routes_stream.router)
    app.include_router(routes_stats.router)
    app.include_router(routes_system.router)

    # Mount static Web UI assets
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    async def get_index():
        """Serve main Single Page Application index.html."""
        index_file = STATIC_DIR / "index.html"
        if not index_file.exists():
            raise HTTPException(status_code=404, detail="UI index.html not found.")
        return FileResponse(str(index_file))

    return app


app = create_app()
