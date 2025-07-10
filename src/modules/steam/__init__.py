import os
from datetime import datetime
from typing import Dict, Any, Optional

from src.core.module import Module
from src.core.utils import get_logger

logger = get_logger(__name__)


class SteamModule(Module):
    """Module for managing Steam library and monitoring game data"""

    def __init__(self) -> None:
        super().__init__("steam")
        self.steam_path = self._get_steam_path()
        self.library_stats: Dict[str, Any] = {}
        self.cache_dir = ".cache/games"

        # Lazy-loaded controller to prevent circular imports
        self._controller: Optional['SteamController'] = None

    @property
    def controller(self) -> 'SteamController':
        """Lazy-loaded Steam controller instance"""
        if self._controller is None:
            from src.modules.steam.controllers.steam_controller import SteamController
            self._controller = SteamController(self.steam_path)
        return self._controller

    async def initialize(self) -> None:
        """
        Initialize the Steam module with a full library scan.

        Performs the initial scan of all Steam libraries and caches
        the results for future updates.
        """
        logger.info("Initializing Steam module...")
        await self._initial_scan()

    async def update(self) -> None:
        """
        Check for changes in Steam library and update data if needed.

        Checks if any manifest files have changed since the last
        scan and triggers a rescan if changes are detected.
        """
        logger.info("Checking Steam library for updates...")

        # Check for manifest file changes since last scan
        if self._manifest_files_changed():
            logger.info("Changes detected, rescanning...")
            await self._rescan_library()
        else:
            logger.debug("No changes detected in Steam library")

        # Update cached statistics
        self._update_stats()

    def get_tile_data(self) -> Dict[str, Any]:
        """Get data for dashboard tile display"""
        # Get libraries grouped data
        libraries_data = self._group_by_library()

        # Transform libraries data for tile display (exclude games list, add count)
        libraries_tile_data = {}
        for library_path, library_info in libraries_data.items():
            libraries_tile_data[library_path] = {
                "game_count": len(library_info["games"]),
                "size_breakdown": library_info["size_breakdown"]
            }

        return {
            "total_games": self.library_stats.get("total_games", 0),
            "total_size": self.library_stats.get("size_breakdown", {}).get("total", 0),
            "libraries": libraries_tile_data,
            "status": "running" if self.enabled else "stopped"
        }

    def get_detailed_data(self) -> Dict[str, Any]:
        """Return detailed data organized by libraries"""
        libraries_data = self._group_by_library()

        # Add game count to each library
        for library_path, library_info in libraries_data.items():
            library_info["game_count"] = len(library_info["games"])

        return {
            "total_games": len(self.controller.games),
            "libraries": libraries_data
        }

    @staticmethod
    def get_update_interval() -> int:
        return 30

    async def _initial_scan(self) -> None:
        """
        Perform a full scan of all Steam libraries.

        This method loads all games from all Steam library directories
        and caches the scan timestamp for future change detection.
        """
        logger.info("Starting initial Steam library scan...")
        self.controller.load_games()
        self.state["last_full_scan"] = datetime.now()
        logger.info(f"Initial scan completed. Found {len(self.controller.games)} games")

    async def _rescan_library(self) -> None:
        """Perform a rescan when changes are detected."""
        logger.info("Rescanning Steam library...")
        await self._initial_scan()

    def _manifest_files_changed(self) -> bool:
        """
        Check if any Steam manifest files have changed since the last scan.
        If no previous scan exists, this will return True to trigger an initial scan.
        """
        last_scan = self.state.get("last_full_scan")
        if not last_scan:
            logger.debug("No previous scan found, triggering full scan")
            return True

        # Check all library paths for manifest changes
        library_paths = self.controller.parsing_service.get_library_paths()
        return self.controller.parsing_service.check_manifest_changes(
            library_paths,
            last_scan.timestamp()
        )

    def _update_stats(self) -> None:
        """Update internal statistics about the Steam library."""
        logger.debug("Updating Steam library statistics...")

        # Calculate total size breakdown for tile display
        size_breakdown = {
            "games": sum(game.size_on_disk for game in self.controller.games),
            "dlc": sum(game.dlc_size for game in self.controller.games),
            "shader_cache": sum(game.shader_cache_size for game in self.controller.games),
            "workshop": sum(game.workshop_content_size for game in self.controller.games),
        }
        size_breakdown["total"] = sum(size_breakdown.values())

        self.library_stats = {
            "total_games": len(self.controller.games),
            "size_breakdown": size_breakdown,
            "libraries_count": len(self.controller.parsing_service.get_library_paths())
        }

        logger.debug(
            f"Updated stats: {self.library_stats['total_games']} games, "
            f"{size_breakdown['total']} bytes total"
        )

    def _group_by_library(self) -> Dict[str, Dict[str, Any]]:
        """Group games by their library paths."""
        libraries: Dict[str, Dict[str, Any]] = {}

        for game in self.controller.games:
            library_path = str(game.library_path)

            if library_path not in libraries:
                libraries[library_path] = {
                    "games": [],
                    "size_breakdown": {
                        "games": 0,
                        "dlc": 0,
                        "shader_cache": 0,
                        "workshop": 0,
                        "total": 0
                    }
                }

            # Add game to library's games list
            libraries[library_path]["games"].append(game.to_dict())

            # Update size breakdown
            lib_stats = libraries[library_path]["size_breakdown"]
            lib_stats["games"] += game.size_on_disk
            lib_stats["dlc"] += game.dlc_size
            lib_stats["shader_cache"] += game.shader_cache_size
            lib_stats["workshop"] += game.workshop_content_size
            lib_stats["total"] += game.total_size

        return libraries

    # TODO: This has to be replaced with a more robust method
    @staticmethod
    def _get_steam_path() -> str:
        import platform
        if platform.system() == 'Windows':
            return r'C:\Program Files (x86)\Steam'
        else:
            return os.path.expanduser('~/.steam/steam')
