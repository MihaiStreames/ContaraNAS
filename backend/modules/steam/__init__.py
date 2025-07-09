import os
from datetime import datetime

from backend.core.module import Module
from backend.core.utils import get_logger

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
        print("Initializing Steam module...")
        await self._initial_scan()

    async def update(self):
        """Check for changes and update data"""
        print("Checking Steam library for updates...")

        # Check if any manifest files changed
        if self._manifest_files_changed():
            print("Changes detected, rescanning...")
            await self._rescan_library()

        # Update statistics
        self._update_stats()

    def get_tile_data(self):
        """Data for dashboard tile"""
        return {
            "total_games": len(self.games),
            "total_size_gb": sum(game.get("size_gb", 0) for game in self.games),
            "libraries": len(self.library_stats),
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

        manager = SteamGameManager(self.steam_path, self.cache_dir)
        manager.load_games()
        self.games = manager.serialize_games()
        self.state["last_full_scan"] = datetime.now()

    async def _rescan_library(self):
        """Rescan when changes detected"""
        await self._initial_scan()

    def _manifest_files_changed(self) -> bool:
        """Check if Steam manifest files changed since last scan"""
        last_scan = self.state.get("last_full_scan")
        if not last_scan:
            return True

        # Check manifest modification times
        import os
        steamapps_path = os.path.join(self.steam_path, 'steamapps')

        for file in os.listdir(steamapps_path):
            if file.startswith("appmanifest_") and file.endswith(".acf"):
                manifest_path = os.path.join(steamapps_path, file)
                if os.path.getmtime(manifest_path) > last_scan.timestamp():
                    return True

        return False

    def _update_stats(self):
        """Update internal statistics"""
        self.library_stats = {
            "total_games": len(self.games),
            "total_size": sum(game.get("size_on_disk", 0) for game in self.games),
            "by_drive": self._group_by_drive()
        }

    def _group_by_drive(self):
        """Group games by drive"""
        drives = {}

        for game in self.games:
            drive = game.get("location", "C:")[0:2]  # Get drive letter

            if drive not in drives:
                drives[drive] = {"games": 0, "size": 0}

            drives[drive]["games"] += 1
            drives[drive]["size"] += game.get("size_on_disk", 0)

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
