from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from ContaraNAS.core.module_manager import ModuleManager
from ContaraNAS.core.utils import get_logger

from .commands import create_command_routes
from .stream import StreamManager


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    logger.info("Starting ContaraNAS API...")

    app.state.module_manager = ModuleManager()
    app.state.stream_manager = StreamManager(app.state.module_manager)

    await app.state.module_manager.restore_module_states()

    logger.info(f"API started with {len(app.state.module_manager.modules)} modules")
    yield

    logger.info("Shutting down ContaraNAS API...")
    await app.state.stream_manager.shutdown()
    await app.state.module_manager.shutdown_all_modules()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="ContaraNAS API",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:1420",
            "http://127.0.0.1:1420",
            "tauri://localhost",
            "https://tauri.localhost",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(create_command_routes())

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "timestamp": datetime.now().isoformat()}

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        await app.state.stream_manager.handle_connection(websocket)

    return app


app = create_app()
