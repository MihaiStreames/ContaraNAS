from abc import ABC, abstractmethod

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

    @abstractmethod
    async def initialize(self):
        """One-time setup when module is enabled"""
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

        # Unsure if this should be here
        # a better implementation would be to have a separate
        # initialization step that is called when the module is registered
        await self.initialize()

        await self.start_monitoring()
        self.enabled = True
        self.logger.info(f"Module {self.name} enabled successfully")

    async def disable(self):
        """Disable the module and stop monitoring"""
        if not self.enabled:
            self.logger.debug(f"Module {self.name} is already disabled")
            return

        await self.stop_monitoring()
        self.enabled = False
        self.logger.info(f"Module {self.name} disabled successfully")

    def update_state(self, **kwargs):
        """Helper method for modules to update their state"""
        self.state.update(kwargs)
        self.logger.debug(f"Module {self.name} state updated: {kwargs}")
