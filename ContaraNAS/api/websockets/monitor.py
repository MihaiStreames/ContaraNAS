import asyncio
from dataclasses import asdict
from datetime import datetime
from typing import TYPE_CHECKING

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from ContaraNAS.core.utils import get_logger
from .conn_manager import ConnectionManager, SubscriptionType, connection_manager

if TYPE_CHECKING:
    from ContaraNAS.core.module_manager import ModuleManager

logger = get_logger(__name__)

router = APIRouter()


class MonitorBroadcaster:
    """Handles periodic broadcasting of system stats to WebSocket clients"""

    def __init__(
            self,
            manager: ConnectionManager,
            module_manager: "ModuleManager | None" = None,
            interval: float = 2.0,
    ):
        self._connection_manager = manager
        self._module_manager: ModuleManager | None = module_manager
        self._interval = interval
        self._running = False
        self._task: asyncio.Task | None = None

    def set_module_manager(self, module_manager: "ModuleManager") -> None:
        """Set the module manager (for deferred initialization)"""
        self._module_manager = module_manager

    async def start(self) -> None:
        """Start the broadcast loop"""
        if self._running:
            logger.debug("Broadcaster already running")
            return

        self._running = True
        self._task = asyncio.create_task(self._broadcast_loop())
        logger.info(f"Monitor broadcaster started (interval: {self._interval}s)")

    async def stop(self) -> None:
        """Stop the broadcast loop"""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        logger.info("Monitor broadcaster stopped")

    async def _broadcast_loop(self) -> None:
        """Main broadcast loop"""
        while self._running:
            try:
                # Only broadcast if there are connected clients
                if self._connection_manager.connection_count > 0:
                    await self._broadcast_system_stats()

                await asyncio.sleep(self._interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in broadcast loop: {e}")
                await asyncio.sleep(self._interval)

    async def _broadcast_system_stats(self) -> None:
        """Collect and broadcast system stats"""
        if not self._module_manager:
            return

        # Get sys_monitor module
        sys_monitor = self._module_manager.modules.get("sys_monitor")
        if not sys_monitor or not sys_monitor.enable_flag:
            return

        try:
            # Get tile data from the module
            tile_data = await sys_monitor.get_tile_data()

            # Convert dataclass objects to dicts for JSON serialization
            message = {
                "type": "system_stats",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "cpu": self._serialize_dataclass(tile_data.get("cpu")),
                    "memory": self._serialize_dataclass(tile_data.get("memory")),
                    "disks": [
                        self._serialize_dataclass(disk) for disk in tile_data.get("disks", [])
                    ],
                },
            }

            sent = await self._connection_manager.broadcast(
                message, SubscriptionType.SYSTEM_STATS
            )
            logger.debug(f"Broadcasted system stats to {sent} clients")

        except Exception as e:
            logger.error(f"Error broadcasting system stats: {e}")

    @staticmethod
    def _serialize_dataclass(obj) -> dict | None:
        """Serialize a dataclass to dict, handling None"""
        if obj is None:
            return None
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        if hasattr(obj, "__dataclass_fields__"):
            return asdict(obj)
        if isinstance(obj, dict):
            return obj
        return None

    async def broadcast_module_state(
            self, module_name: str, change_type: str, data: dict | None = None
    ) -> None:
        """Broadcast a module state change"""
        message = {
            "type": "module_state",
            "timestamp": datetime.now().isoformat(),
            "module_name": module_name,
            "change_type": change_type,
            "data": data or {},
        }

        await self._connection_manager.broadcast(message, SubscriptionType.MODULE_STATE)

    async def broadcast_steam_update(
            self, event_type: str, app_id: int, data: dict | None = None
    ) -> None:
        """Broadcast a Steam library update"""
        message = {
            "type": "steam_update",
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "app_id": app_id,
            "data": data or {},
        }

        await self._connection_manager.broadcast(message, SubscriptionType.STEAM_UPDATES)


# Global broadcaster instance
monitor_broadcaster = MonitorBroadcaster(connection_manager)


def get_monitor_websocket_router(module_manager: "ModuleManager") -> APIRouter:
    """Create and return the WebSocket router with module manager configured"""

    # Configure the broadcaster with the module manager
    monitor_broadcaster.set_module_manager(module_manager)

    @router.websocket("/ws/monitor")
    async def websocket_monitor(websocket: WebSocket):
        """Main WebSocket endpoint for real-time monitoring"""
        # Generate unique client ID
        client_id = f"client_{id(websocket)}_{datetime.now().timestamp()}"

        try:
            # Accept connection with default subscriptions
            client = await connection_manager.connect(
                websocket, client_id, {SubscriptionType.ALL}
            )

            # Send initial connection confirmation
            await connection_manager.send_to_client(
                client_id,
                {
                    "type": "connected",
                    "client_id": client_id,
                    "subscriptions": [s.value for s in client.subscriptions],
                    "timestamp": datetime.now().isoformat(),
                },
            )

            # Start broadcaster if not running
            if not monitor_broadcaster._running:
                await monitor_broadcaster.start()

            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_json()
                    response = await connection_manager.handle_message(client_id, data)
                    await connection_manager.send_to_client(client_id, response)
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")
                    await connection_manager.send_to_client(
                        client_id, {"type": "error", "error": str(e)}
                    )

        except WebSocketDisconnect:
            logger.debug(f"Client {client_id} disconnected")
        except Exception as e:
            logger.error(f"WebSocket error for {client_id}: {e}")
        finally:
            await connection_manager.disconnect(client_id)

            # Stop broadcaster if no more clients
            if connection_manager.connection_count == 0:
                await monitor_broadcaster.stop()

    @router.websocket("/ws/system")
    async def websocket_system_only(websocket: WebSocket):
        """WebSocket endpoint for system stats only"""
        client_id = f"sys_{id(websocket)}_{datetime.now().timestamp()}"

        try:
            await connection_manager.connect(
                websocket, client_id, {SubscriptionType.SYSTEM_STATS}
            )

            await connection_manager.send_to_client(
                client_id,
                {
                    "type": "connected",
                    "client_id": client_id,
                    "subscriptions": [SubscriptionType.SYSTEM_STATS.value],
                    "timestamp": datetime.now().isoformat(),
                },
            )

            if not monitor_broadcaster._running:
                await monitor_broadcaster.start()

            while True:
                try:
                    data = await websocket.receive_json()
                    response = await connection_manager.handle_message(client_id, data)
                    await connection_manager.send_to_client(client_id, response)
                except WebSocketDisconnect:
                    break

        except WebSocketDisconnect:
            pass
        finally:
            await connection_manager.disconnect(client_id)
            if connection_manager.connection_count == 0:
                await monitor_broadcaster.stop()

    return router
