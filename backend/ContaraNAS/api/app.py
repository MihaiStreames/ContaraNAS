from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from backend.ContaraNAS.core.module_manager import ModuleManager
from backend.ContaraNAS.core.security import AuthService, PairingConfig
from backend.ContaraNAS.core.utils import get_logger
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from guard.middleware import SecurityMiddleware
from guard.models import SecurityConfig

from .auth import create_auth_routes
from .commands import create_command_routes
from .stream import StreamManager


logger = get_logger(__name__)

# Allowed origins for CORS
ALLOWED_ORIGINS = [
    "http://localhost:1420",    # Vite dev server
    "http://127.0.0.1:1420",    # Vite dev server (alt)
    "tauri://localhost",        # Tauri production (macOS/Linux)
    "https://tauri.localhost",  # Tauri production (Windows)
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager"""
    logger.info("Starting ContaraNAS API...")

    auth_config = PairingConfig(
        token_validity_seconds=300,
        max_failed_attempts=5,
        lockout_duration_seconds=300,
    )
    app.state.auth_service = AuthService(auth_config)

    app.state.module_manager = ModuleManager()
    app.state.stream_manager = StreamManager(app.state.module_manager)

    # Restore previously enabled modules
    await app.state.module_manager.restore_module_states()

    logger.info(f"API started with {len(app.state.module_manager.modules)} modules")

    if not app.state.auth_service.has_devices():
        logger.info("No paired devices - generating initial pairing code...")
        try:
            app.state.auth_service.generate_pairing_code()
        except RuntimeError as e:
            logger.error(f"Failed to generate pairing code: {e}")
    yield

    logger.info("Shutting down ContaraNAS API...")
    await app.state.stream_manager.shutdown()
    await app.state.module_manager.shutdown_all_modules()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="ContaraNAS API",
        version="0.1.0",
        description="Backend API for ContaraNAS system monitoring and management",
        lifespan=lifespan,
    )

    security_config = SecurityConfig(
        enable_redis=False,
        rate_limit=100,
        rate_limit_window=60,
        auto_ban_threshold=5,
        auto_ban_duration=3600,
        whitelist=["192.168.0.0/16", "10.0.0.0/8", "127.0.0.1"],
    )

    app.add_middleware(SecurityMiddleware, config=security_config)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(create_command_routes())
    app.include_router(create_auth_routes())

    @app.get("/health")
    async def health() -> dict:
        """Health check endpoint"""
        return {"status": "ok", "timestamp": datetime.now().isoformat()}

    @app.get("/info")
    async def info() -> dict:
        """Server information"""
        return {
            "name": "ContaraNAS",
            "version": "0.1.0",
            "timestamp": datetime.now().isoformat(),
        }

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket for real-time data streaming"""
        await app.state.stream_manager.handle_connection(websocket)

    return app


# Application instance
app = create_app()
