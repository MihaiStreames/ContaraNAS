from typing import Any, Dict, Optional

from src.core.module import Module
from src.core.utils import get_logger

from .controllers.steam_controller import SteamController

logger = get_logger(__name__)


class SteamModule(Module):
    """Module for managing Steam library"""

    def __init__(self) -> None:
        self.controller: Optional[SteamController] = None
        super().__init__("steam")

    async def initialize(self) -> None:
        """Initialize the Steam module"""
        self.controller = SteamController(self.update_state)
        self.controller.initialize()

    async def start_monitoring(self) -> None:
        """Start Steam library monitoring"""
        self.controller.start_monitoring()
        logger.info("Steam monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop Steam library monitoring"""
        self.controller.stop_monitoring()
        logger.info("Steam monitoring stopped")

    def get_tile_data(self) -> Dict[str, Any]:
        """Get data for dashboard tile"""
        if not self.controller:
            return {"libraries": [], "error": "Module not initialized"}

        return self.controller.get_tile_data()
