from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ContaraNAS.core.module_manager import ModuleManager
from ContaraNAS.core.utils import get_logger
from .routes import create_modules_router, create_steam_router, create_system_router
from .websockets import connection_manager, get_monitor_websocket_router, monitor_broadcaster

logger = get_logger(__name__)

# Global module manager instance
_module_manager: ModuleManager | None = None


def get_module_manager() -> ModuleManager:
    """Get the global module manager instance"""
    global _module_manager
    if _module_manager is None:
        _module_manager = ModuleManager()
    return _module_manager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown"""
    logger.info("Starting ContaraNAS API...")

    # Initialize module manager
    module_manager = get_module_manager()

    # Restore previously enabled modules
    await module_manager.restore_module_states()

    logger.info(f"ContaraNAS API started with {len(module_manager.modules)} modules")

    yield

    # Shutdown
    logger.info("Shutting down ContaraNAS API...")

    # Stop the WebSocket broadcaster
    await monitor_broadcaster.stop()

    # Close all WebSocket connections
    await connection_manager.close_all()

    # Shutdown all modules
    await module_manager.shutdown_all_modules()

    logger.info("ContaraNAS API shutdown complete")


def create_app(
        title: str = "ContaraNAS API",
        version: str = "0.1.0",
        cors_origins: list[str] | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application"""

    # Create app with lifespan
    app = FastAPI(
        title=title,
        version=version,
        description="REST API and WebSocket server for ContaraNAS system monitoring",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    if cors_origins is None:
        # Default: allow Tauri app and localhost development
        cors_origins = [
            "http://localhost",
            "http://localhost:1420",  # Vite dev server
            "http://127.0.0.1",
            "http://127.0.0.1:1420",
            "tauri://localhost",  # Tauri app
            "https://tauri.localhost",
        ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Get module manager
    module_manager = get_module_manager()

    # Register REST API routes
    app.include_router(create_modules_router(module_manager), prefix="/api/v1")
    app.include_router(create_system_router(module_manager), prefix="/api/v1")
    app.include_router(create_steam_router(module_manager), prefix="/api/v1")

    # Register WebSocket routes
    app.include_router(get_monitor_websocket_router(module_manager))

    # Health check endpoint
    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": version,
        }

    # API info endpoint
    @app.get("/")
    async def api_info() -> dict:
        """API information"""
        return {
            "name": title,
            "version": version,
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "websocket": {
                "monitor": "/ws/monitor",
                "system": "/ws/system",
            },
            "api": {
                "modules": "/api/v1/modules",
                "system": "/api/v1/system",
                "steam": "/api/v1/steam",
            },
        }

    @app.get("/api/v1/status")
    async def api_status() -> dict:
        """Get current API status including module states"""
        states = await module_manager.get_all_states()

        return {
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "modules": {
                name: {
                    "enabled": state["enabled"] if state else False,
                    "initialized": state["initialized"] if state else False,
                }
                for name, state in states.items()
            },
            "websocket": {
                "connected_clients": connection_manager.connection_count,
                "broadcaster_running": monitor_broadcaster._running,
            },
        }

    logger.info("FastAPI application created")
    return app


# Default app instance for uvicorn
app = create_app()
