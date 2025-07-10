import asyncio
from abc import ABC, abstractmethod
from datetime import datetime

from src.core.utils import get_logger

logger = get_logger(__name__)


class Module(ABC):
    """Base class for all modules in the system"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = False
        self.task = None
        self.last_update = None
        self.state = {}
        self.logger = get_logger(f"backend.modules.{name}")

    @abstractmethod
    def initialize(self):
        """One-time setup when module is enabled."""
        pass

    @abstractmethod
    def update(self):
        """Periodic update logic for the module."""
        pass

    @abstractmethod
    def get_tile_data(self):
        """Get data for dashboard tile display."""
        pass

    @abstractmethod
    def get_detailed_data(self):
        """Get detailed data for the module."""
        pass

    async def enable(self):
        """Enable the module and monitor."""
        if self.enabled:
            self.logger.debug(f"Module {self.name} is already enabled")
            return

        try:
            await self.initialize()
            self.enabled = True
            self.task = asyncio.create_task(self._monitor_loop())
            self.logger.info(f"Module {self.name} enabled successfully")
        except Exception as e:
            self.logger.error(f"Failed to enable module {self.name}: {e}")
            raise

    async def disable(self):
        """Disable the module and stop monitoring."""
        if not self.enabled:
            self.logger.debug(f"Module {self.name} is already disabled")
            return

        self.enabled = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        self.logger.info(f"Module {self.name} disabled successfully")

    async def _monitor_loop(self):
        """Background monitoring loop."""
        self.logger.debug(f"Starting monitor loop for module {self.name}")

        while self.enabled:
            try:
                await self.update()
                self.last_update = datetime.now()
                await asyncio.sleep(self.get_update_interval())
            except asyncio.CancelledError:
                self.logger.debug(f"Monitor loop for module {self.name} cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in module {self.name}: {e}")
                await asyncio.sleep(30)  # Backoff on error

    @staticmethod
    def get_update_interval() -> int:
        """Get the update interval in seconds."""
        return 30
