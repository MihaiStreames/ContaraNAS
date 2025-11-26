from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from guard.middleware import SecurityMiddleware
from guard.models import SecurityConfig
from marketplace.server.config import config
from marketplace.server.routes import modules_router, registry_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Application lifespan"""
    # Ensure data directories exist
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.MODULES_DIR.mkdir(parents=True, exist_ok=True)

    print()
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║              ContaraNAS Marketplace Server                     ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print(f"║  Registry: {str(config.REGISTRY_FILE):<51} ║")
    print(f"║  Modules:  {str(config.MODULES_DIR):<51} ║")
    print("╠════════════════════════════════════════════════════════════════╣")
    print("║  Endpoints:                                                    ║")
    print("║    GET  /registry?backend_version=x.x.x                        ║")
    print("║    GET  /modules/{id}?backend_version=x.x.x                    ║")
    print("║    GET  /modules/{id}/versions/{version}/download              ║")
    print("║    GET  /modules/{id}/icon                                     ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()

    yield


def create_app() -> FastAPI:
    """Create the FastAPI application"""
    app = FastAPI(
        title="ContaraNAS Marketplace",
        version=config.VERSION,
        description="Module marketplace for ContaraNAS",
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
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(registry_router)
    app.include_router(modules_router)

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": config.VERSION}

    return app


app = create_app()
