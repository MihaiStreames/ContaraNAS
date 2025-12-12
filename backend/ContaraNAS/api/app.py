from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from ContaraNAS.core import ModuleManager
from ContaraNAS.core import get_logger
from ContaraNAS.core import settings
from ContaraNAS.core import setup_logging
from ContaraNAS.core.action import ActionDispatcher
from ContaraNAS.core.auth import AuthService
from ContaraNAS.core.auth import PairingConfig
from ContaraNAS.core.exceptions import ContaraNASError

from .responses import HealthResponse
from .responses import InfoResponse
from .routes import create_auth_routes
from .routes import create_command_routes
from .routes import create_module_routes
from .routes import create_state_routes
from .stream import StreamManager


setup_logging(
    level=settings.log_level,
    rotation=settings.log_rotation,
    retention=settings.log_retention,
    compression=settings.log_compression,
)

logger = get_logger(__name__)


def setup_services(app: FastAPI) -> None:
    """Setup core services"""
    auth_config = PairingConfig(
        token_validity_seconds=settings.pairing_code_validity_seconds,
        max_failed_attempts=settings.pairing_max_failed_attempts,
        lockout_duration_seconds=settings.pairing_lockout_duration_seconds,
    )
    app.state.auth_service = AuthService(auth_config)

    app.state.module_manager = ModuleManager()
    app.state.stream_manager = StreamManager(app.state.module_manager)

    app.state.module_manager.set_ui_update_callback(
        app.state.stream_manager.notify_module_ui_update
    )

    app.state.action_dispatcher = ActionDispatcher()
    for module in app.state.module_manager.modules.values():
        app.state.action_dispatcher.register_module(module)


def setup_pairing(app: FastAPI) -> None:
    """Setup pairing if not already paired"""
    if not app.state.auth_service.is_paired():
        logger.info("No app paired - generating pairing code...")
        try:
            app.state.auth_service.generate_pairing_code()

        except RuntimeError as e:
            logger.error(f"Failed to generate pairing code: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager"""
    logger.info("Starting ContaraNAS API...")

    setup_services(app)

    await app.state.module_manager.restore_module_states()

    logger.info(f"API started with {len(app.state.module_manager.modules)} modules")

    setup_pairing(app)

    yield

    logger.info("Shutting down ContaraNAS Server API...")

    await app.state.stream_manager.shutdown()
    await app.state.module_manager.shutdown_all_modules()

    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the application"""
    app = FastAPI(
        title="ContaraNAS Server API",
        version=settings.backend_version,
        description="Server API for ContaraNAS",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(create_command_routes())
    app.include_router(create_auth_routes())
    app.include_router(create_module_routes())
    app.include_router(create_state_routes())

    @app.exception_handler(ContaraNASError)
    async def contaranas_error_handler(_request: Request, exc: ContaraNASError):
        logger.error(f"Application error: {exc}")
        return JSONResponse(
            status_code=500, content={"detail": str(exc), "error_type": exc.__class__.__name__}
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(_request: Request, _exc: Exception):
        logger.exception("Unhandled exception")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    @app.get("/api/health", response_model=HealthResponse)
    async def health(request: Request) -> HealthResponse:
        """Health check endpoint"""
        checks = {
            "api": "ok",
            "modules": "ok" if request.app.state.module_manager else "degraded",
            "websocket": "ok" if request.app.state.stream_manager else "degraded",
        }

        status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"

        return HealthResponse(status=status, timestamp=datetime.now().isoformat(), checks=checks)

    @app.get("/api/info", response_model=InfoResponse)
    async def info() -> InfoResponse:
        """Server information"""
        return InfoResponse(
            name="ContaraNAS",
            version=settings.backend_version,
            timestamp=datetime.now().isoformat(),
        )

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket, token: str | None = None):
        """WebSocket for real-time data streaming"""
        await app.state.stream_manager.handle_connection(websocket, app.state.auth_service, token)

    return app


# Application instance
app = create_app()
