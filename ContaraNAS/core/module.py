from abc import ABC, abstractmethod

from ContaraNAS.core.event_bus import event_bus
from ContaraNAS.core.exceptions import ModuleError, ModuleInitializationError
from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class Module(ABC):
    """Base class for all modules in the system"""

    def __init__(self, name: str):
        self.name = name
        self.enable_flag = False
        self.init_flag = False
        self.state = {}
        self.event_handlers = []

    @abstractmethod
    async def initialize(self):
        """One-time setup when module is enabled"""

    @abstractmethod
    async def start_monitoring(self):
        """Start event handlers/watchers"""

    @abstractmethod
    async def stop_monitoring(self):
        """Stop all event handlers/watchers"""

    @abstractmethod
    def get_tile_data(self):
        """Get data for dashboard tile display"""

    async def enable(self):
        """Enable the module and start monitoring"""
        if self.enable_flag:
            logger.debug(f"Module {self.name} is already enabled")
            return

        try:
            # Lazy initialization: only initialize if not already done
            if not self.init_flag:
                await self.initialize()
                self.init_flag = True

            # Check if module was initialized successfully
            if not self.init_flag:
                error_msg = f"Cannot enable module {self.name}: not initialized"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            await self.start_monitoring()
            self.enable_flag = True
            logger.info(f"Module {self.name} enabled successfully")
        except Exception as e:
            raise ModuleInitializationError(self.name, str(e)) from e

        self._emit_event("enabled")

    async def disable(self):
        """Disable the module and stop monitoring"""
        if not self.enable_flag:
            logger.debug(f"Module {self.name} is already disabled")
            return

        try:
            await self.stop_monitoring()
            self.enable_flag = False
            logger.info(f"Module {self.name} disabled successfully")

            self._emit_event("disabled")
        except Exception as e:
            logger.error(f"Failed to disable module {self.name}: {e!s}")
            raise ModuleError(self.name, str(e)) from e

    def update_state(self, **kwargs):
        """Helper method for modules to update their state"""
        old_state = self.state.copy()
        self.state.update(kwargs)
        logger.debug(f"Module {self.name} state updated: {kwargs}")

        self._emit_event(
            "state_updated",
            {
                "module_name": self.name,
                "old_state": old_state,
                "new_state": self.state,
                "changes": kwargs,
            },
        )

    def _emit_event(self, change_type: str, data: dict | None = None):
        """Emit a state change event for GUI components to listen to"""
        event_data = {
            "name": self.name,
            "enabled": self.enable_flag,
            "initialized": self.init_flag,
            "state": self.state.copy(),
            "tile_data": self.get_tile_data(),
            "change_type": change_type,
        }

        if data:
            event_data.update(data)

        # Emit specific module event
        event_bus.emit(f"module.{self.name}.state_changed", event_data)
