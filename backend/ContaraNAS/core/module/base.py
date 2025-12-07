from abc import ABC, abstractmethod
from typing import Any

from ContaraNAS.core.event_bus import event_bus
from ContaraNAS.core.exceptions import ModuleError, ModuleInitializationError
from ContaraNAS.core.utils import get_logger

from .metadata import ModuleMetadata


logger = get_logger(__name__)


class Module(ABC):
    """Base class for all modules"""

    def __init__(
        self,
        name: str,
        display_name: str | None = None,
        metadata: ModuleMetadata | None = None,
    ):
        self.name: str = name
        self.display_name: str = display_name or name.replace("_", " ").title()
        self.enable_flag: bool = False
        self.init_flag: bool = False
        self.state: dict[str, Any] = {}

        # Store metadata
        self._metadata: ModuleMetadata | None = metadata

        # If metadata was provided, use it to update display_name if not explicitly set
        if metadata and not display_name:
            self.display_name = metadata.name

    @property
    def metadata(self) -> ModuleMetadata:
        """Get module metadata"""
        if self._metadata is None:
            raise ModuleError(
                self.name,
                "Metadata not available. Metadata should be provided by ModuleLoader during instantiation.",
            )
        return self._metadata

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
    async def get_tile_data(self):
        """Get data for dashboard tile display"""

    async def enable(self):
        """Enable the module and start monitoring"""
        if self.enable_flag:
            logger.debug(f"Module {self.name} is already enabled")
            return

        logger.info(f"Enabling module: {self.name}")

        try:
            if not self.init_flag:
                logger.debug(f"Initializing module {self.name} for first time")
                await self.initialize()
                self.init_flag = True

            if not self.init_flag:
                raise ModuleError(self.name, "Module failed to initialize")

            await self.start_monitoring()
            self.enable_flag = True
            logger.info(f"Module {self.name} enabled successfully")
        except Exception as e:
            logger.error(f"Failed to enable module {self.name}: {e!s}")
            raise ModuleInitializationError(self.name, str(e)) from e

        await self._emit_event("enabled")

    async def disable(self):
        """Disable the module and stop monitoring"""
        if not self.enable_flag:
            logger.debug(f"Module {self.name} is already disabled")
            return

        logger.info(f"Disabling module: {self.name}")

        try:
            await self.stop_monitoring()
            self.enable_flag = False
            logger.info(f"Module {self.name} disabled successfully")
            await self._emit_event("disabled")
        except Exception as e:
            logger.error(f"Failed to disable module {self.name}: {e!s}")
            raise ModuleError(self.name, str(e)) from e

    async def update_state(self, **kwargs):
        """Update module state"""
        old_state = self.state.copy()
        self.state.update(kwargs)
        logger.trace(f"Module {self.name} state updated: {kwargs}")

        await self._emit_event(
            "state_updated",
            {
                "module_name": self.name,
                "old_state": old_state,
                "new_state": self.state,
                "changes": kwargs,
            },
        )

    async def _emit_event(self, change_type: str, data: dict | None = None):
        """Emit state change event"""
        event_data = {
            "name": self.name,
            "display_name": self.display_name,
            "enabled": self.enable_flag,
            "initialized": self.init_flag,
            "state": self.state.copy(),
            "tile_data": await self.get_tile_data(),
            "change_type": change_type,
        }

        # Include metadata if available
        if self._metadata:
            event_data["metadata"] = self.metadata.to_dict()

        if data:
            event_data.update(data)

        event_bus.emit(f"module.{self.name}.state_changed", event_data)
