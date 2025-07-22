from datetime import datetime
from typing import Dict, Any, Optional

from src.core.module import Module
from src.core.utils import get_logger

logger = get_logger(__name__)


class SteamModule(Module):
    """Module for managing Steam library"""

    def __init__(self) -> None:
        super().__init__("steam")

        # Find Steam path
        from .services.path_service import SteamPathService
        steam_path = SteamPathService.find_steam_path()

        if not steam_path:
            raise RuntimeError("Steam installation not found")

        if not SteamPathService.validate_steam_path(steam_path):
            raise RuntimeError(f"Invalid Steam installation at {steam_path}")

        self.steam_path = steam_path

        # Lazy-loaded controller
        self._controller: Optional['SteamController'] = None

        # Update intervals
        self.check_interval = 10

    @property
    def controller(self) -> 'SteamController':
        """Lazy-loaded Steam controller"""
        if self._controller is None:
            from .controllers.steam_controller import SteamController
            self._controller = SteamController(self.steam_path)
        return self._controller

    async def initialize(self) -> None:
        """Initialize the module"""
        logger.info("Initializing Steam module...")

        # Load all games
        self.controller.load_games()

        # Store initialization time
        self.state["initialized_at"] = datetime.now()
        self.state["game_count"] = len(self.controller.games)

        logger.info(f"Steam module initialized with {self.state['game_count']} games")

    async def update(self) -> None:
        """Check for library changes"""
        # Check for changes
        changes = self.controller.check_for_changes()

        if changes:
            logger.info(f"Library updated: {changes}")
            self.state["last_change"] = changes
            self.state["game_count"] = len(self.controller.games)

    def get_tile_data(self) -> Dict[str, Any]:
        """Get summary data for dashboard tile"""
        stats = self.controller.get_library_stats()

        # Collect per-library size breakdowns
        lib_sizes = [
            {
                "lib_path": lib['path'],
                "size_breakdown": lib['size_breakdown']
            }
            for lib in stats['libraries']
        ]

        return {
            "total_games": stats['total_games'],
            "total_size": stats['total_size'],
            "lib_count": len(stats['libraries']),
            "lib_sizes": lib_sizes,
            "status": "running" if self.enabled else "stopped",
            "last_update": self.last_update.isoformat() if self.last_update else None
        }

    def get_detailed_data(self) -> Dict[str, Any]:
        """Get detailed library data"""
        lib_data = self.controller.get_library_data()
        lib_stats = self.controller.get_library_stats()

        return {
            'total_games': lib_stats['total_games'],
            'total_size': lib_stats['total_size'],
            'libraries': lib_data,
            'module_state': self.state
        }

    def get_update_interval(self) -> int:
        """Return update interval in seconds"""
        return self.check_interval
