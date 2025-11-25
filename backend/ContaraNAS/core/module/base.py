from abc import ABC, abstractmethod
import inspect
import json
from pathlib import Path
from typing import Any

from backend.ContaraNAS.core.event_bus import event_bus
from backend.ContaraNAS.core.exceptions import ModuleError, ModuleInitializationError
from backend.ContaraNAS.core.utils import get_logger

from .metadata import ModuleMetadata


logger = get_logger(__name__)


class Module(ABC):
    """Base class for all modules"""

    def __init__(self, name: str, display_name: str | None = None):
        self.name: str = name
        self.display_name: str = display_name or name.replace("_", " ").title()
        self.enable_flag: bool = False
        self.init_flag: bool = False
        self.state: dict[str, Any] = {}

        # Load metadata from module.json
        self._metadata: ModuleMetadata | None = None

    @property
    def metadata(self) -> ModuleMetadata:
        """Get module metadata, loading from module.json if needed"""
        if self._metadata is None:
            self._metadata = self._load_metadata()
        return self._metadata

    def _load_metadata(self) -> ModuleMetadata:
        """Load metadata from module.json alongside the module's __init__.py"""
        # Get the directory containing the module's __init__.py
        module_file = inspect.getfile(self.__class__)
        module_dir = Path(module_file).parent
        json_path = module_dir / "module.json"

        if json_path.exists():
            try:
                with open(json_path, encoding="utf-8") as f:
                    data = json.load(f)
                logger.debug(f"Loaded metadata for {self.name} from {json_path}")
                return ModuleMetadata.from_dict(data)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"Failed to load module.json for {self.name}: {e}")

        logger.debug(f"No module.json found for {self.name}, using defaults")
        return ModuleMetadata()

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

        try:
            if not self.init_flag:
                await self.initialize()
                self.init_flag = True

            if not self.init_flag:
                raise RuntimeError(f"Cannot enable module {self.name}: not initialized")

            await self.start_monitoring()
            self.enable_flag = True
            logger.info(f"Module {self.name} enabled successfully")
        except Exception as e:
            raise ModuleInitializationError(self.name, str(e)) from e

        await self._emit_event("enabled")

    async def disable(self):
        """Disable the module and stop monitoring"""
        if not self.enable_flag:
            logger.debug(f"Module {self.name} is already disabled")
            return

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
        logger.debug(f"Module {self.name} state updated: {kwargs}")

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
            "metadata": self.metadata.to_dict(),
        }

        if data:
            event_data.update(data)

        event_bus.emit(f"module.{self.name}.state_changed", event_data)
