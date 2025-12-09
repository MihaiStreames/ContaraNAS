from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, ClassVar

from ContaraNAS.core.exceptions import ModuleError, ModuleInitializationError
from ContaraNAS.core.ui import Alert, Badge, Modal, Stat, Tile
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

        # Store metadata
        self._metadata: ModuleMetadata | None = metadata

        # If metadata was provided, use it to update display_name if not explicitly set
        if metadata and not display_name:
            self.display_name = metadata.name

        # Initialize typed state if State class is defined
        self._typed_state: ModuleState | None = None
        self._ui_update_callback: Callable[[Module], None] | None = None
        self._init_typed_state()

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
        """Called when typed state is committed"""
        if self._ui_update_callback is not None:
            self._ui_update_callback(self)

    def _error_tile(self, error_message: str) -> Tile:
        """Return an error tile when get_tile() fails"""
        return Tile(
            icon="AlertTriangle",
            title=self.display_name,
            badge=Badge(text="Error", variant="error"),
            stats=[Stat(label="Status", value="Failed")],
            content=[
                Alert(
                    message=f"Module error: {error_message}",
                    variant="error",
                    title="Render Failed",
                )
            ],
        )

    @property
    def metadata(self) -> ModuleMetadata:
        """Get module metadata"""
        if self._metadata is None:
            raise ModuleError(
                self.name,
                "Metadata not available",
            )
        return self._metadata

    @property
    def typed_state(self) -> ModuleState | None:
        """Get typed state if available"""
        return self._typed_state

    def set_ui_update_callback(self, callback: Callable[["Module"], None]) -> None:
        """Set callback to be called when UI should be pushed to clients"""
        self._ui_update_callback = callback

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
        """Serialize tile to dict for frontend - catches errors gracefully"""
        try:
            return self.get_tile().to_dict()
        except NotImplementedError:
            return {}
        except Exception as e:
            logger.exception(f"Error rendering tile for module {self.name}")
            return self._error_tile(str(e)).to_dict()

    def render_modals(self) -> list[dict[str, Any]]:
        """Serialize modals to dicts for frontend - catches errors gracefully"""
        try:
            return [modal.to_dict() for modal in self.get_modals()]
        except Exception:
            logger.exception(f"Error rendering modals for module {self.name}")
            return []

    def render_ui(self) -> dict[str, Any]:
        """Return complete UI state for frontend"""
        return {
            "tile": self.render_tile(),
            "modals": self.render_modals(),
        }

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

        self._on_state_commit()

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
            self._on_state_commit()
        except Exception as e:
            logger.error(f"Failed to disable module {self.name}: {e!s}")
            raise ModuleError(self.name, str(e)) from e
