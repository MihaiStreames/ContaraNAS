from typing import Dict, Any, Optional

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
        return {
            "total_games": self.state.get('game_count', 0),
            "library_count": self.state.get('library_count', 0),
            "status": "monitoring" if self.enable_flag else "idle",
            "steam_path": self.state.get('steam_path'),
        }
