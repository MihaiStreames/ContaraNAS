from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from watchdog.observers import Observer

from src.core.module import Module
from src.core.utils import get_logger
from src.modules.steam.services.manifest_handler import SteamManifestHandler
from src.modules.steam.utils.steam_helpers import extract_app_id

logger = get_logger(__name__)


class SteamModule(Module):
    """Module for managing Steam library"""

    def __init__(self) -> None:
        super().__init__("steam")

        # Steam-specific state
        self.steam_path: Optional[Path] = None
        self.library_paths: List[Path] = []
        self.manifest_cache: Dict[Path, float] = {}  # manifest_path -> mtime

        # Watchdog components
        self.observer: Optional[Observer] = None
        self.manifest_handler: Optional[SteamManifestHandler] = None

    async def initialize(self) -> None:
        """Initialize the module"""
        self.logger.info("Initializing Steam module...")

        # Find Steam installation
        self.steam_path = await self._find_steam_path()
        if not self.steam_path:
            raise RuntimeError("Steam installation not found")

        # Load library paths from libraryfolders.vdf
        self.library_paths = await self._load_library_paths()
        if not self.library_paths:
            raise RuntimeError("No Steam libraries found")

        # Cache initial manifest states
        await self._cache_initial_manifests()

        # Update module state
        self.update_state(
            initialized_at=datetime.now(),
            steam_path=str(self.steam_path),
            library_count=len(self.library_paths),
            game_count=len(self.manifest_cache)
        )

        self.logger.info(
            f"Steam module initialized: {len(self.library_paths)} libraries, {len(self.manifest_cache)} games"
        )

    async def start_monitoring(self) -> None:
        """Start monitoring Steam library changes"""
        self.logger.info("Starting Steam monitoring...")

        await self._start_watchdog()

        self.logger.info("Steam monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop all event handlers and watchers"""
        self.logger.info("Stopping Steam monitoring...")

        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.observer = None

        self.manifest_handler = None
        self.logger.info("Steam monitoring stopped")

    def get_tile_data(self) -> Dict[str, Any]:
        """Get summary data for dashboard tile"""
        return {
            "total_games": len(self.manifest_cache),
            "library_count": len(self.library_paths),
            "status": "running" if self.enabled else "stopped",
            "steam_path": str(self.steam_path) if self.steam_path else None,
            "last_change": self.state.get('last_change_time')
        }

    @staticmethod
    async def _find_steam_path() -> Optional[Path]:
        """Find Steam installation path"""
        from .services.path_service import SteamPathService

        steam_path = SteamPathService.find_steam_path()
        if steam_path and SteamPathService.validate_steam_path(steam_path):
            return steam_path
        return None

    async def _load_library_paths(self) -> List[Path]:
        """Load library paths from libraryfolders.vdf"""
        if not self.steam_path:
            return []

        from .services.parsing_service import SteamParsingService

        parsing_service = SteamParsingService(self.steam_path)
        return parsing_service.get_library_paths()

    async def _start_watchdog(self) -> None:
        """Start watchdog file monitoring"""
        self.observer = Observer()
        self.manifest_handler = SteamManifestHandler(self._on_manifest_change)

        # Watch each library's steamapps folder
        for library_path in self.library_paths:
            steamapps_path = library_path / 'steamapps'

            if steamapps_path.exists():
                self.observer.schedule(
                    self.manifest_handler,
                    str(steamapps_path),
                    recursive=False
                )
                self.logger.debug(f"Watching: {steamapps_path}")

        # Start the observer
        self.observer.start()

    def _on_manifest_change(self, event_type, manifest_path):
        """Handle manifest file changes"""
        app_id = extract_app_id(manifest_path)

        # Use more descriptive logging
        if app_id:
            self.logger.info(f"Steam app {app_id} {event_type}: {manifest_path.name}")
        else:
            self.logger.info(f"Manifest {event_type}: {manifest_path.name}")

        cache_action = None
        old_count = len(self.manifest_cache)

        if event_type == 'deleted':
            # Remove from cache
            if manifest_path in self.manifest_cache:
                del self.manifest_cache[manifest_path]
                cache_action = "removed"
            else:
                self.logger.debug(f"Attempted to remove non-cached manifest: {manifest_path.name}")

        elif event_type in ['created', 'modified']:
            # Update cache with new mtime
            if manifest_path.exists():
                mtime = manifest_path.stat().st_mtime
                old_mtime = self.manifest_cache.get(manifest_path)

                if old_mtime != mtime:
                    self.manifest_cache[manifest_path] = mtime
                    cache_action = "updated" if old_mtime else "added"
                else:
                    # No actual change in mtime, skip update
                    return
            else:
                self.logger.warning(f"Manifest file doesn't exist during {event_type}: {manifest_path}")
                return

        # Only log cache actions if there was an actual change
        if cache_action:
            new_count = len(self.manifest_cache)
            count_change = new_count - old_count

            if count_change != 0:
                self.logger.debug(
                    f"Cache {cache_action}: {manifest_path.name} (total: {new_count}, change: {count_change:+d})")
            else:
                self.logger.debug(f"Cache {cache_action}: {manifest_path.name}")

            # Update module state
            self.update_state(
                game_count=len(self.manifest_cache),
                last_change_type=event_type,
                last_change_file=manifest_path.name,
                last_change_time=datetime.now(),
                last_change_app_id=app_id
            )

    async def _cache_initial_manifests(self) -> None:
        """Cache initial manifest file states"""
        self.manifest_cache.clear()

        for library_path in self.library_paths:
            steamapps_path = library_path / 'steamapps'
            if not steamapps_path.exists():
                continue

            # Find all manifest files
            for manifest_path in steamapps_path.glob('appmanifest_*.acf'):
                mtime = manifest_path.stat().st_mtime
                self.manifest_cache[manifest_path] = mtime

        self.logger.debug(f"Cached {len(self.manifest_cache)} manifest files")
