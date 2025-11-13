from collections.abc import Callable
from typing import Any

from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class EventBus:
    """Simple event bus for Module -> GUI communication"""

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Subscribe to an event type"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        self._listeners[event_type].append(callback)
        logger.debug(f"Subscribed to event: {event_type}")

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]):
        """Unsubscribe from an event type"""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
                logger.debug(f"Unsubscribed from event: {event_type}")
            except ValueError:
                pass

    def emit(self, event_type: str, data: Any = None):
        """Emit an event to all subscribers"""
        if event_type in self._listeners:
            logger.debug(
                f"Emitting event: {event_type} to {len(self._listeners[event_type])} listeners"
            )

            for callback in self._listeners[event_type][
                :
            ]:  # Copy list to avoid modification during iteration
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_type}: {e}")
        else:
            logger.debug(f"No listeners for event: {event_type}")


# Global event bus instance
event_bus = EventBus()
