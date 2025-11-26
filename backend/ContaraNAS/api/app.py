from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from backend.ContaraNAS.core import MarketplaceClient, ModuleManager, settings
from backend.ContaraNAS.core.auth import AuthService, PairingConfig
from backend.ContaraNAS.core.exceptions import ContaraNASError
from backend.ContaraNAS.core.utils import get_logger, setup_logging
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from .responses import HealthResponse, InfoResponse
from .routes import create_auth_routes, create_command_routes, create_marketplace_routes
from .stream import StreamManager


setup_logging(
    level=settings.log_level,
    rotation=settings.log_rotation,
    retention=settings.log_retention,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan manager"""
    logger.info("Starting ContaraNAS API...")

    # Auth service
    auth_config = PairingConfig(
        token_validity_seconds=settings.pairing_code_validity_seconds,
        max_failed_attempts=settings.pairing_max_failed_attempts,
        lockout_duration_seconds=settings.pairing_lockout_duration_seconds,
    )
    app.state.auth_service = AuthService(auth_config)

    # Module manager
    app.state.module_manager = ModuleManager()
    app.state.stream_manager = StreamManager(app.state.module_manager)

    # Marketplace client
    app.state.marketplace_client = MarketplaceClient(
        base_url=settings.marketplace_url,
        backend_version=settings.backend_version,
    )

    # Restore previously enabled modules
    await app.state.module_manager.restore_module_states()

    logger.info(f"API started with {len(app.state.module_manager.modules)} modules")

    # Generate pairing code on launch if not already paired
    if not app.state.auth_service.is_paired():
        logger.info("No app paired - generating pairing code...")
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
        version=settings.backend_version,
        description="Backend API for ContaraNAS",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(create_command_routes())
    app.include_router(create_auth_routes())
    app.include_router(create_marketplace_routes())

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

    @app.get("/health", response_model=HealthResponse)
    async def health(request: Request) -> HealthResponse:
        """Health check endpoint"""
        checks = {
            "api": "ok",
            "modules": "ok" if request.app.state.module_manager else "degraded",
            "websocket": "ok" if request.app.state.stream_manager else "degraded",
        }

        status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"

        return HealthResponse(status=status, timestamp=datetime.now().isoformat(), checks=checks)

    @app.get("/info", response_model=InfoResponse)
    async def info() -> InfoResponse:
        """Server information"""
        return InfoResponse(
            name="ContaraNAS",
            version=settings.backend_version,
            timestamp=datetime.now().isoformat(),
        )

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket, token: str | None = None):
        """WebSocket for real-time data streaming. Requires token query param."""
        await app.state.stream_manager.handle_connection(websocket, app.state.auth_service, token)

    return app


# Application instance
app = create_app()
