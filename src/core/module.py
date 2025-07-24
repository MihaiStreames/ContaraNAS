from abc import ABC, abstractmethod

from src.core.event_bus import event_bus
from src.core.utils import get_logger

logger = get_logger(__name__)


class Module(ABC):
    """Base class for all modules in the system"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = False
        self.state = {}
        self.logger = get_logger(f"backend.modules.{name}")
        self.event_handlers = []

        self.initialized = False
        self._initialization_lock = False
        self._perform_initialization()

    @abstractmethod
    def initialize(self):
        """One-time setup when module is created"""
        pass

    @abstractmethod
    async def start_monitoring(self):
        """Start event handlers/watchers"""
        pass

    @abstractmethod
    async def stop_monitoring(self):
        """Stop all event handlers/watchers"""
        pass

    @abstractmethod
    def get_tile_data(self):
        """Get data for dashboard tile display"""
        pass

    async def enable(self):
        """Enable the module and start monitoring"""
        if self.enabled:
            self.logger.debug(f"Module {self.name} is already enabled")
            return

        # Check if module was initialized successfully
        if not self.initialized:
            error_msg = f"Cannot enable module {self.name}: not initialized"
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)

        await self.start_monitoring()
        self.enabled = True
        self.logger.info(f"Module {self.name} enabled successfully")

        self._emit_event('enabled')

    async def disable(self):
        """Disable the module and stop monitoring"""
        if not self.enabled:
            self.logger.debug(f"Module {self.name} is already disabled")
            return

        await self.stop_monitoring()
        self.enabled = False
        self.logger.info(f"Module {self.name} disabled successfully")

        self._emit_event('disabled')

    def update_state(self, **kwargs):
        """Helper method for modules to update their state"""
        old_state = self.state.copy()
        self.state.update(kwargs)
        self.logger.debug(f"Module {self.name} state updated: {kwargs}")

        self._emit_event('state_updated', {
            'module_name': self.name,
            'old_state': old_state,
            'new_state': self.state,
            'changes': kwargs
        })

    def _emit_event(self, change_type: str, data: dict = None):
        """Emit a state change event for GUI components to listen to"""
        event_data = {
            'module_name': self.name,
            'change_type': change_type,
            'enabled': self.enabled,
            'state': self.state,
            'tile_data': self.get_tile_data()
        }

        if data:
            event_data.update(data)

        # Emit specific module event
        event_bus.emit(f'module.{self.name}.state_changed', event_data)

    def _perform_initialization(self):
        """Perform module initialization"""
        if self._initialization_lock:
            self.logger.warning(f"Module {self.name} initialization already in progress")
            return

        if self.initialized:
            self.logger.debug(f"Module {self.name} already initialized")
            return

        self._initialization_lock = True
        try:
            self.logger.info(f"Initializing module {self.name}...")
            self.initialize()
            self.initialized = True
            self.logger.info(f"Module {self.name} initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize module {self.name}: {e}")
            raise
        finally:
            self._initialization_lock = False
