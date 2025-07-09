import asyncio
from abc import ABC, abstractmethod
from datetime import datetime


class Module(ABC):
    """Base class for all modules in the system"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = False
        self.task = None
        self.last_update = None
        self.state = {}

    @abstractmethod
    def initialize(self):
        """One-time setup when module is enabled"""
        pass

    @abstractmethod
    def update(self):
        """Periodic update logic for the module"""
        pass

    @abstractmethod
    def get_tile_data(self):
        """Get data for dashboard tile display"""
        pass

    async def enable(self):
        """Enable the module and monitor"""
        if self.enabled:
            return

        await self.initialize()
        self.enabled = True
        self.task = asyncio.create_task(self._monitor_loop())
        print(f"Module {self.name} enabled")

    async def disable(self):
        """Disable the module and stop monitoring"""
        if not self.enabled:
            return

        self.enabled = False
        if self.task:
            self.task.cancel()
        print(f"Module {self.name} disabled")

    async def _monitor_loop(self):
        """Background monitoring loop"""
        while self.enabled:
            try:
                await self.update()
                self.last_update = datetime.now()
                await asyncio.sleep(self.get_update_interval())
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in {self.name}: {e}")
                await asyncio.sleep(30)  # Backoff on error

    @staticmethod
    def get_update_interval() -> int:
        """Get the update interval in seconds"""
        return 30
