import os
from datetime import datetime

from backend.core.module import Module
from backend.core.utils import get_logger
from backend.modules.steam.controllers.steam_controller import SteamController
from backend.modules.steam.utils.steam_helpers import format_size

logger = get_logger(__name__)


class SteamModule(Module):
    """Module to manage Steam library and monitor game data"""

    def __init__(self):
        super().__init__("steam")
        self.steam_path = self._get_steam_path()
        self.library_stats = {}
        self.controller = SteamController(self.steam_path)

    async def initialize(self):
        """One-time setup"""
        logger.info("Initializing Steam module...")
        await self._initial_scan()

    async def update(self):
        """Check for changes and update data"""
        logger.info("Checking Steam library for updates...")

        # Check if any manifest files changed
        if self._manifest_files_changed():
            logger.info("Changes detected, rescanning...")
            await self._rescan_library()
        else:
            logger.debug("No changes detected in Steam library")

        # Update statistics
        self._update_stats()

    def get_tile_data(self):
        """Data for dashboard tile"""
        total_size_bytes = sum(game.total_size for game in self.controller.games)
        total_size_gb = total_size_bytes / (1024 ** 3)  # Convert to GB

        return {
            "total_games": len(self.controller.games),
            "total_size_gb": round(total_size_gb, 2),
            "total_size_bytes": total_size_bytes,
            "libraries": len(self.library_stats.get("by_drive", {})),
            "status": "running" if self.enabled else "stopped",
            "last_update": self.last_update.isoformat() if self.last_update else None
        }

    def get_detailed_data(self):
        """Data for modal popup"""
        return {
            "games": self.controller.serialize_games(),
            "library_stats": self.library_stats,
            "drive_usage": self._get_drive_usage()
        }

    def get_update_interval(self) -> int:
        return 30  # Check every 30 seconds

    async def _initial_scan(self):
        """Full library scan"""
        logger.info("Starting initial Steam library scan...")
        self.controller.load_games()
        self.state["last_full_scan"] = datetime.now()
        logger.info(f"Initial scan completed. Found {len(self.controller.games)} games.")

    async def _rescan_library(self):
        """Rescan when changes detected"""
        logger.info("Rescanning Steam library...")
        await self._initial_scan()

    def _manifest_files_changed(self) -> bool:
        """Check if Steam manifest files changed since last scan"""
        last_scan = self.state.get("last_full_scan")
        if not last_scan:
            logger.debug("No previous scan found, triggering full scan")
            return True

        # Get library paths and check for changes
        library_paths = self.controller.parsing_service.get_library_paths()
        return self.controller.parsing_service.check_manifest_changes(library_paths, last_scan.timestamp())

    def _update_stats(self):
        """Update internal statistics"""
        logger.debug("Updating Steam library statistics...")

        total_size = sum(game.total_size for game in self.controller.games)

        self.library_stats = {
            "total_games": len(self.controller.games),
            "total_size_bytes": total_size,
            "total_size_formatted": format_size(total_size),
            "by_drive": self._group_by_drive()
        }

        logger.debug(
            f"Updated stats: {self.library_stats['total_games']} games, {self.library_stats['total_size_formatted']} total"
        )

    def _group_by_drive(self):
        """Group games by drive"""
        drives = {}

        for game in self.controller.games:
            location = str(game.library_path)

            # Extract drive letter
            if os.name == 'nt':
                drive = location[0:2] if len(location) >= 2 else "Unknown"
            else:
                drive = "/"

            if drive not in drives:
                drives[drive] = {"games": 0, "size_bytes": 0, "size_formatted": "0 B"}

            drives[drive]["games"] += 1
            drives[drive]["size_bytes"] += game.total_size
            drives[drive]["size_formatted"] = format_size(drives[drive]["size_bytes"])

        return drives

    def _get_drive_usage(self):
        """Get drive usage information"""
        return self.library_stats.get("by_drive", {})

    # TODO: This has to be replaced with a more robust method
    @staticmethod
    def _get_steam_path():
        import platform
        if platform.system() == 'Windows':
            return r'C:\Program Files (x86)\Steam'
        else:
            return os.path.expanduser('~/.steam/steam')
