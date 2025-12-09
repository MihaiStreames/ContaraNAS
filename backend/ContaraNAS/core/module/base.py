from abc import ABC, abstractmethod
from typing import Any, ClassVar
from warnings import warn

from ContaraNAS.core.event_bus import event_bus
from ContaraNAS.core.exceptions import ModuleError, ModuleInitializationError
from ContaraNAS.core.ui import Modal, Tile
from ContaraNAS.core.utils import get_logger

from .metadata import ModuleMetadata
from .state import ModuleState


logger = get_logger(__name__)


class Module(ABC):
    """Base class for all modules"""

    # Subclasses can define a State inner class
    State: ClassVar[type[ModuleState] | None] = None

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

        # Initialize typed state if State class is defined
        self._typed_state: ModuleState | None = None
        self._init_typed_state()

    @property
    def metadata(self) -> ModuleMetadata:
        """Get module metadata"""
        if self._metadata is None:
            raise ModuleError(
                self.name,
                "Metadata not available. Metadata should be provided by ModuleLoader during instantiation.",
            )
        return self._metadata

    @property
    def typed_state(self) -> ModuleState | None:
        """Get typed state if available"""
        return self._typed_state

    @abstractmethod
    async def initialize(self):
        """One-time setup when module is enabled"""

    @abstractmethod
    async def start_monitoring(self):
        """Start event handlers/watchers"""

    @abstractmethod
    async def stop_monitoring(self):
        """Stop all event handlers/watchers"""

    def get_tile(self) -> Tile:
        """Return the dashboard tile UI component"""
        raise NotImplementedError(f"Module {self.name} must implement get_tile()")

    def get_modals(self) -> list[Modal]:
        """Return modal definitions for this module"""
        return []

    def render_tile(self) -> dict[str, Any]:
        """Serialize tile to dict for frontend"""
        try:
            return self.get_tile().to_dict()
        except NotImplementedError:
            return {}

    def render_modals(self) -> list[dict[str, Any]]:
        """Serialize modals to dicts for frontend"""
        return [modal.to_dict() for modal in self.get_modals()]

    def render_ui(self) -> dict[str, Any]:
        """Return complete UI state for frontend"""
        return {
            "tile": self.render_tile(),
            "modals": self.render_modals(),
        }

    async def get_tile_data(self) -> dict[str, Any]:
        """Get data for dashboard tile display

        .. deprecated::
            Use get_tile() instead which returns a Tile component directly
        """
        warn(
            f"{self.__class__.__name__}.get_tile_data() is deprecated"
            "Override get_tile() instead which returns a Tile component directly",
            DeprecationWarning,
            stacklevel=2,
        )
        return {}

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

    def _init_typed_state(self) -> None:
        """Initialize typed state from State inner class"""
        state_class = self._get_state_class()
        if state_class is None:
            return

        self._typed_state = state_class()
        self._typed_state.set_commit_callback(self._on_state_commit)

    def _get_state_class(self) -> type[ModuleState] | None:
        """Get the State class defined on this module"""
        for cls in type(self).__mro__:
            if cls is Module:
                break
            if "State" in cls.__dict__:
                state_cls = cls.__dict__["State"]
                if isinstance(state_cls, type) and issubclass(state_cls, ModuleState):
                    return state_cls
        return None

    def _on_state_commit(self) -> None:
        """Called when typed state is committed - triggers UI re-render"""
        if self._typed_state is None:
            return

        event_bus.emit(
            f"module.{self.name}.state_committed",
            {
                "name": self.name,
                "state": self._typed_state.to_dict(),
                "ui": self.render_ui(),
            },
        )

    async def _emit_event(self, change_type: str, data: dict | None = None):
        """Emit state change event"""
        # Try new render methods first, fall back to get_tile_data() for legacy
        tile_data = self.render_tile()
        if not tile_data:
            # Legacy module using get_tile_data()
            tile_data = await self.get_tile_data()

        event_data = {
            "name": self.name,
            "display_name": self.display_name,
            "enabled": self.enable_flag,
            "initialized": self.init_flag,
            "state": self.state.copy(),
            "tile_data": tile_data,
            "modals": self.render_modals(),
            "change_type": change_type,
        }

        if self._metadata:
            event_data["metadata"] = self.metadata.to_dict()

        if data:
            event_data.update(data)

        event_bus.emit(f"module.{self.name}.state_changed", event_data)
