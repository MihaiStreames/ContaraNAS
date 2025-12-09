import asyncio
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect, status

from ContaraNAS.core.auth import AuthService
from ContaraNAS.core.module import Module
from ContaraNAS.core.module_manager import ModuleManager
from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class StreamManager:
    """Manages WebSocket connections and real-time UI streaming"""

    def __init__(self, module_manager: ModuleManager):
        self._manager = module_manager
        self._client: WebSocket | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def notify_module_ui_update(self, module: Module) -> None:
        """Push a module's UI to connected clients"""
        if not self._client or not self._loop:
            return

        asyncio.run_coroutine_threadsafe(
            self._push_module_ui(module),
            self._loop,
        )

    def notify_app_state_change(self, active_modal: str | None = None) -> None:
        """Push app-level state to connected clients"""
        if not self._client or not self._loop:
            return

        asyncio.run_coroutine_threadsafe(
            self._push_app_state(active_modal),
            self._loop,
        )

    async def handle_connection(
        self, websocket: WebSocket, auth_service: AuthService, token: str | None
    ) -> None:
        """Handle a new WebSocket connection"""
        # Authenticate before accepting
        if not token or not auth_service.verify_token(token):
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            logger.warning("WebSocket connection rejected: invalid or missing token")
            return

        # Replace existing client if any
        if self._client:
            try:
                await self._client.close()
                logger.info("Replaced previous client")
            except RuntimeError:
                # Already closed, ignore
                logger.debug("Previous client already closed")
            except Exception as e:
                logger.warning(f"Error closing previous client: {e}")

        await websocket.accept()
        self._client = websocket
        self._loop = asyncio.get_running_loop()
        logger.info("Client connected")

        try:
            await self._send_full_state()

            while True:
                msg = await websocket.receive_json()
                await self._handle_message(msg)

        except WebSocketDisconnect:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self._client = None
            self._loop = None

    async def _push_module_ui(self, module: Module) -> None:
        """Push full UI update for a single module"""
        ui = module.render_ui() if module.enable_flag else None
        await self._send(
            {
                "type": "module_ui",
                "module": module.name,
                "display_name": module.display_name,
                "enabled": module.enable_flag,
                "initialized": module.init_flag,
                "ui": ui,
            }
        )

    async def _push_app_state(self, active_modal: str | None = None) -> None:
        """Push app-level state update"""
        await self._send(
            {
                "type": "app_state",
                "active_modal": active_modal,
            }
        )

    async def _send_full_state(self) -> None:
        """Send complete app state to client"""
        modules = []
        for name, module in self._manager.modules.items():
            ui = None
            if module.enable_flag:
                ui = module.render_ui()

            modules.append(
                {
                    "name": name,
                    "display_name": module.display_name,
                    "enabled": module.enable_flag,
                    "initialized": module.init_flag,
                    "ui": ui,
                }
            )

        await self._send(
            {
                "type": "full_state",
                "modules": modules,
                "active_modal": None,
            }
        )

    async def _send(self, data: dict) -> None:
        """Send JSON message to connected client"""
        if not self._client:
            return
        try:
            data["timestamp"] = datetime.now().isoformat()
            await self._client.send_json(data)
        except Exception as e:
            logger.error(f"Send failed: {e}")

    async def _handle_message(self, msg: dict) -> None:
        """Handle incoming message from client"""
        if msg.get("type") == "ping":
            await self._send({"type": "pong"})

    async def shutdown(self) -> None:
        """Shutdown the stream manager"""
        if self._client:
            await self._client.close()
            self._client = None
