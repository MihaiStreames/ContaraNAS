import asyncio
from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING, Any

from fastapi import WebSocket, WebSocketDisconnect, status

from ContaraNAS.core.auth import AuthService
from ContaraNAS.core.event_bus import event_bus
from ContaraNAS.core.utils import get_logger


if TYPE_CHECKING:
    from ContaraNAS.core.module_manager import ModuleManager

logger = get_logger(__name__)


class StreamManager:
    """Manages WebSocket connections and real-time data streaming"""

    def __init__(self, module_manager: "ModuleManager", interval: float = 2.0):
        self._manager = module_manager
        self._interval = interval
        self._client: WebSocket | None = None
        self._task: asyncio.Task | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._handlers: dict[str, Any] = {}  # event_type -> handler function

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

        # Subscribe to module events for push-based updates
        self._subscribe_to_modules()

        try:
            # Send current state immediately
            await self._send_initial_state()

            # Start periodic streaming task
            self._start_streaming()

            # Process incoming messages (ping/pong, future commands)
            while True:
                msg = await websocket.receive_json()
                await self._handle_message(msg)

        except WebSocketDisconnect:
            logger.info("Client disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            self._stop_streaming()
            self._unsubscribe_from_modules()
            self._client = None
            self._loop = None

    def _subscribe_to_modules(self) -> None:
        """Subscribe to state change events for all registered modules"""
        for name in self._manager.modules:
            event_type = f"module.{name}.state_changed"
            handler = self._make_handler(name)
            self._handlers[event_type] = handler
            event_bus.subscribe(event_type, handler)

    def _unsubscribe_from_modules(self) -> None:
        """Unsubscribe from all module events"""
        for event_type, handler in self._handlers.items():
            event_bus.unsubscribe(event_type, handler)
        self._handlers.clear()

    def _make_handler(self, module_name: str):
        """Create an event handler for a specific module"""

        def handler(data: dict):
            if self._client and self._loop:
                asyncio.run_coroutine_threadsafe(
                    self._on_module_change(module_name, data),
                    self._loop,
                )

        return handler

    async def _on_module_change(self, module_name: str, data: dict) -> None:
        """Handle module state change event"""
        change_type = data.get("change_type")

        # Send lightweight state notification
        await self._send(
            {
                "type": "module_state",
                "module": module_name,
                "enabled": data.get("enabled"),
                "initialized": data.get("initialized"),
                "change_type": change_type,
            }
        )

        # Send full Steam state on any Steam change (game added/removed/updated)
        if module_name == "steam" and change_type == "state_updated":
            steam = await self._collect_steam_state()
            if steam:
                await self._send({"type": "steam_library", **steam})

    async def _send_initial_state(self) -> None:
        """Send complete initial state dump to newly connected client"""
        await self._send(
            {
                "type": "initial_state",
                "modules": self._collect_modules_state(),
                "system": await self._collect_system_state(),
                "steam": await self._collect_steam_state(),
            }
        )

    def _collect_modules_state(self) -> list[dict]:
        """Collect basic state info for all registered modules"""
        return [
            {
                "name": name,
                "display_name": m.display_name,
                "enabled": m.enable_flag,
                "initialized": m.init_flag,
            }
            for name, m in self._manager.modules.items()
        ]

    async def _collect_system_state(self) -> dict | None:
        """Collect system monitor data (CPU, memory, disks)"""
        module = self._manager.modules.get("sys_monitor")
        if not module or not module.enable_flag:
            return None

        try:
            data = await module.get_tile_data()
            return {
                "cpu": _to_dict(data.get("cpu")),
                "memory": _to_dict(data.get("memory")),
                "disks": [_to_dict(d) for d in data.get("disks", [])],
            }
        except Exception as e:
            logger.error(f"System state collection failed: {e}")
            return None

    async def _collect_steam_state(self) -> dict | None:
        """Collect Steam library data (libraries, games)"""
        module = self._manager.modules.get("steam")
        if not module or not module.enable_flag:
            return None

        try:
            return await module.get_tile_data()
        except Exception as e:
            logger.error(f"Steam state collection failed: {e}")
            return None

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

    def _start_streaming(self) -> None:
        """Start the periodic system stats streaming task"""
        if not self._task:
            self._task = asyncio.create_task(self._stream_loop())

    def _stop_streaming(self) -> None:
        """Stop the periodic streaming task"""
        if self._task:
            self._task.cancel()
            self._task = None

    async def _stream_loop(self) -> None:
        """Background loop that periodically sends system stats"""
        while True:
            try:
                await asyncio.sleep(self._interval)
                if self._client:
                    system = await self._collect_system_state()
                    if system:
                        await self._send({"type": "system_stats", **system})
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Stream loop error: {e}")

    async def shutdown(self) -> None:
        """Clean shutdown of the stream manager"""
        self._stop_streaming()
        if self._client:
            await self._client.close()
            self._client = None


def _to_dict(obj) -> dict | None:
    """Convert various object types to dict for JSON serialization"""
    if obj is None:
        return None
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return obj if isinstance(obj, dict) else None
