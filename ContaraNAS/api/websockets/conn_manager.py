import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from fastapi import WebSocket

from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class SubscriptionType(str, Enum):
    """Types of data subscriptions available"""

    SYSTEM_STATS = "system_stats"
    MODULE_STATE = "module_state"
    STEAM_UPDATES = "steam_updates"
    ALL = "all"


@dataclass
class ClientConnection:
    """Represents a connected WebSocket client"""

    websocket: WebSocket
    client_id: str
    connected_at: datetime = field(default_factory=datetime.now)
    subscriptions: set[SubscriptionType] = field(default_factory=set)
    last_ping: datetime = field(default_factory=datetime.now)

    def is_subscribed(self, sub_type: SubscriptionType) -> bool:
        """Check if client is subscribed to a specific type"""
        return SubscriptionType.ALL in self.subscriptions or sub_type in self.subscriptions


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""

    def __init__(self):
        self._connections: dict[str, ClientConnection] = {}
        self._lock = asyncio.Lock()
        self._message_handlers: dict[str, Callable] = {}

    @property
    def connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self._connections)

    @property
    def client_ids(self) -> list[str]:
        """Get list of connected client IDs"""
        return list(self._connections.keys())

    async def connect(
        self,
        websocket: WebSocket,
        client_id: str,
        subscriptions: set[SubscriptionType] | None = None,
    ) -> ClientConnection:
        """Accept a new WebSocket connection"""
        await websocket.accept()

        client = ClientConnection(
            websocket=websocket,
            client_id=client_id,
            subscriptions=subscriptions or {SubscriptionType.ALL},
        )

        async with self._lock:
            # Disconnect existing connection with same ID if exists
            if client_id in self._connections:
                await self._disconnect_client(client_id)

            self._connections[client_id] = client

        logger.info(f"Client connected: {client_id} (total: {self.connection_count})")
        return client

    async def disconnect(self, client_id: str) -> None:
        """Disconnect a client"""
        async with self._lock:
            await self._disconnect_client(client_id)

    async def _disconnect_client(self, client_id: str) -> None:
        """Internal disconnect without lock (must be called with lock held)"""
        if client_id in self._connections:
            client = self._connections.pop(client_id)
            try:
                await client.websocket.close()
            except Exception:
                pass  # Connection may already be closed
            logger.info(f"Client disconnected: {client_id} (total: {self.connection_count})")

    async def send_to_client(self, client_id: str, message: dict[str, Any]) -> bool:
        """Send a message to a specific client"""
        if client_id not in self._connections:
            return False

        client = self._connections[client_id]
        try:
            await client.websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Error sending to client {client_id}: {e}")
            await self.disconnect(client_id)
            return False

    async def broadcast(
        self,
        message: dict[str, Any],
        subscription_type: SubscriptionType | None = None,
    ) -> int:
        """Broadcast a message to all connected clients (or those with specific subscription)"""
        if not self._connections:
            return 0

        sent_count = 0
        failed_clients: list[str] = []

        # Get snapshot of connections to avoid modification during iteration
        async with self._lock:
            connections = list(self._connections.items())

        for client_id, client in connections:
            # Check subscription filter
            if subscription_type and not client.is_subscribed(subscription_type):
                continue

            try:
                await client.websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.debug(f"Failed to send to {client_id}: {e}")
                failed_clients.append(client_id)

        # Clean up failed connections
        for client_id in failed_clients:
            await self.disconnect(client_id)

        return sent_count

    async def update_subscriptions(
        self, client_id: str, subscriptions: set[SubscriptionType]
    ) -> bool:
        """Update a client's subscriptions"""
        if client_id not in self._connections:
            return False

        async with self._lock:
            if client_id in self._connections:
                self._connections[client_id].subscriptions = subscriptions
                logger.debug(f"Updated subscriptions for {client_id}: {subscriptions}")
                return True
        return False

    async def ping_client(self, client_id: str) -> bool:
        """Send a ping to a specific client"""
        return await self.send_to_client(
            client_id, {"type": "ping", "timestamp": datetime.now().isoformat()}
        )

    async def broadcast_ping(self) -> int:
        """Send ping to all clients"""
        return await self.broadcast({"type": "ping", "timestamp": datetime.now().isoformat()})

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Register a handler for a specific message type"""
        self._message_handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type}")

    async def handle_message(self, client_id: str, message: dict[str, Any]) -> dict[str, Any]:
        """Handle an incoming message from a client"""
        msg_type = message.get("type", "unknown")

        # Built-in handlers
        if msg_type == "ping":
            return {"type": "pong", "timestamp": datetime.now().isoformat()}

        if msg_type == "subscribe":
            subs = message.get("subscriptions", [])
            sub_types = {SubscriptionType(s) for s in subs if s in SubscriptionType.__members__}
            await self.update_subscriptions(client_id, sub_types)
            return {"type": "subscribed", "subscriptions": [s.value for s in sub_types]}

        if msg_type == "unsubscribe":
            await self.update_subscriptions(client_id, set())
            return {"type": "unsubscribed"}

        # Custom handlers
        if msg_type in self._message_handlers:
            try:
                return await self._message_handlers[msg_type](client_id, message)
            except Exception as e:
                logger.error(f"Error in handler for {msg_type}: {e}")
                return {"type": "error", "error": str(e)}

        return {"type": "error", "error": f"Unknown message type: {msg_type}"}

    async def close_all(self) -> None:
        """Close all connections"""
        async with self._lock:
            for client_id in list(self._connections.keys()):
                await self._disconnect_client(client_id)

        logger.info("All WebSocket connections closed")


# Global connection manager instance
connection_manager = ConnectionManager()