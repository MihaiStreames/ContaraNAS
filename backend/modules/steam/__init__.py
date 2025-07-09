import os
from datetime import datetime

from backend.core.module import Module
from backend.core.utils import get_logger
from backend.modules.steam.utils.steam_helpers import format_size

logger = get_logger(__name__)


class SteamModule(Module):
    def __init__(self):
        super().__init__("steam")
        self.steam_path = self._get_steam_path()
        self.games = []
        self.library_stats = {}
        self.cache_dir = ".cache/games"

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
        total_size_bytes = sum(game.get("total_size", 0) for game in self.games)
        total_size_gb = total_size_bytes / (1024 ** 3)  # Convert to GB

        return {
            "total_games": len(self.games),
            "total_size_gb": round(total_size_gb, 2),
            "total_size_bytes": total_size_bytes,
            "libraries": len(self.library_stats.get("by_drive", {})),
            "status": "running" if self.enabled else "stopped",
            "last_update": self.last_update.isoformat() if self.last_update else None
        }

    def get_detailed_data(self):
        """Data for modal popup"""
        return {
            "games": self.games,
            "library_stats": self.library_stats,
            "recent_updates": self._get_recent_updates(),
            "drive_usage": self._get_drive_usage(),
            "update_history": self._get_update_history()
        }

    def get_update_interval(self) -> int:
        return 30  # Check every 30 seconds

    async def _initial_scan(self):
        """Full library scan"""
        from .manager.steam_game_manager import SteamGameManager

        logger.info("Starting initial Steam library scan...")
        manager = SteamGameManager(self.steam_path, self.cache_dir)
        manager.load_games()
        self.games = manager.serialize_games()
        self.state["last_full_scan"] = datetime.now()
        logger.info(f"Initial scan completed. Found {len(self.games)} games.")

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

        # Check manifest modification times
        steamapps_path = os.path.join(self.steam_path, 'steamapps')

        if not os.path.exists(steamapps_path):
            logger.warning(f"Steam apps path not found: {steamapps_path}")
            return False

        try:
            for file in os.listdir(steamapps_path):
                if file.startswith("appmanifest_") and file.endswith(".acf"):
                    manifest_path = os.path.join(steamapps_path, file)
                    if os.path.getmtime(manifest_path) > last_scan.timestamp():
                        logger.debug(f"Manifest file changed: {file}")
                        return True
        except Exception as e:
            logger.error(f"Error checking manifest files: {e}")
            return False

        return False

    def _update_stats(self):
        """Update internal statistics"""
        logger.debug("Updating Steam library statistics...")

        total_size = sum(game.get("total_size", 0) for game in self.games)

        self.library_stats = {
            "total_games": len(self.games),
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

        for game in self.games:
            location = game.get("location", "")
            if not location:
                continue

            # Extract drive letter (works for both Windows and Unix paths)
            if os.name == 'nt':  # Windows
                drive = location[0:2] if len(location) >= 2 else "Unknown"
            else:  # Unix-like systems
                drive = "/"

            if drive not in drives:
                drives[drive] = {"games": 0, "size_bytes": 0, "size_formatted": "0 B"}

            drives[drive]["games"] += 1
            game_size = game.get("total_size", 0)
            drives[drive]["size_bytes"] += game_size
            drives[drive]["size_formatted"] = format_size(drives[drive]["size_bytes"])

        return drives

    def _get_recent_updates(self):
        """Get recently updated games"""
        return [game for game in self.games if game.get("recently_updated", False)]

    def _get_drive_usage(self):
        """Get drive usage information"""
        return self.library_stats.get("by_drive", {})

    def _get_update_history(self):
        """Get update history"""
        return self.state.get("update_history", [])

    @staticmethod
    def _get_steam_path():
        import platform
        if platform.system() == 'Windows':
            return r'C:\Program Files (x86)\Steam'
        else:
            return os.path.expanduser('~/.steam/steam')
