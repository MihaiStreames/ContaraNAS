from typing import Any

from ContaraNAS.core.module import Module
from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.steam.controllers import SteamController


logger = get_logger(__name__)


class SteamModule(Module):
    """Module for managing Steam library"""

    def __init__(self) -> None:
        self.controller: SteamController | None = None
        super().__init__("steam")

    async def initialize(self) -> None:
        """Initialize the Steam module"""
        self.controller = SteamController(self.update_state)
        await self.controller.initialize()

    async def start_monitoring(self) -> None:
        """Start Steam library monitoring"""
        if self.controller:
            self.controller.start_monitoring()
            logger.info("Steam monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop Steam library monitoring"""
        if self.controller:
            self.controller.stop_monitoring()
            logger.info("Steam monitoring stopped")

    async def get_tile_data(self) -> dict[str, Any]:
        """Get data for dashboard tile"""
        if not self.controller:
            return {"libraries": [], "error": "Module not initialized"}

        return await self.controller.get_tile_data()
