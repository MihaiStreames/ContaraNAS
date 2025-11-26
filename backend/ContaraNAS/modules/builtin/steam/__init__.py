from typing import Any

from backend.ContaraNAS.core.module import Module
from backend.ContaraNAS.core.utils import get_logger

from .controllers import SteamController


logger = get_logger(__name__)


class SteamModule(Module):
    """Module for managing Steam library"""

    def __init__(
        self,
        name: str = "steam",
        display_name: str | None = None,
        metadata=None,
    ) -> None:
        self.controller: SteamController | None = None
        super().__init__(name, display_name, metadata)

    async def initialize(self) -> None:
        """Initialize the Steam module"""
        self.controller = SteamController(self.update_state)
        await self.controller.initialize()

    async def start_monitoring(self) -> None:
        """Start Steam library monitoring"""
        if self.controller:
            await self.controller.start_monitoring()
            if self.controller.steam_available:
                logger.info("Steam monitoring started")
            else:
                logger.info("Steam monitoring skipped - Steam not available")

    async def stop_monitoring(self) -> None:
        """Stop Steam library monitoring"""
        if self.controller:
            await self.controller.cleanup()
            logger.info("Steam monitoring stopped")

    async def get_tile_data(self) -> dict[str, Any]:
        """Get data for dashboard tile"""
        if not self.controller:
            return {
                "status": "not_initialized",
                "libraries": [],
                "games": [],
                "total_games": 0,
                "total_libraries": 0,
            }

        return await self.controller.get_tile_data()
