import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.steam.services import (
    SteamCacheService,
    SteamGameLoaderService,
    SteamImageService,
    SteamLibraryService,
    SteamMonitoringService,
    SteamParsingService,
)
from ContaraNAS.modules.steam.utils import extract_app_id, get_drive_info


logger = get_logger(__name__)


class SteamController:
    """Controller that orchestrates Steam module operations"""

    def __init__(self, state_update_callback):
        self._state_update_callback = state_update_callback
        self._monitor_flag = False
        self._event_loop = None

        self.library_service = SteamLibraryService()
        self.parsing_service = SteamParsingService(self.library_service.get_steam_path())
        self.game_loader_service = SteamGameLoaderService(self.parsing_service)
        self.cache_service = SteamCacheService()
        self.image_service = SteamImageService()
        self.monitoring_service = SteamMonitoringService(self._handle_manifest_change)

    async def initialize(self) -> None:
        """Initialize the controller and its services"""
        logger.info("Initializing Steam controller...")

        # Capture the event loop for thread callbacks
        self._event_loop = asyncio.get_running_loop()

        # Initialize library service
        if not self.library_service.initialize():
            raise RuntimeError("Failed to initialize Steam library service")

        # Initialize manifest cache
        library_paths = self.library_service.get_library_paths()
        self.cache_service.initialize_cache(library_paths)

        # Sync image cache with manifest cache
        installed_app_ids = self.cache_service.get_installed_app_ids()
        self.image_service.sync_with_manifest_cache(installed_app_ids)

        await self._state_update_callback(
            initialized_at=datetime.now(),
            steam_path=str(self.library_service.get_steam_path()),
            last_scan_completed=datetime.now(),
        )

        logger.info("Steam controller initialized successfully")

    def start_monitoring(self) -> None:
        """Start monitoring Steam libraries"""
        if self._monitor_flag:
            logger.debug("Monitoring already started")
            return

        self.cache_service.update_cache(self.library_service.get_library_paths())
        self.monitoring_service.start_monitoring(self.library_service.get_library_paths())
        self._monitor_flag = True

    def stop_monitoring(self) -> None:
        """Stop monitoring Steam libraries"""
        if not self._monitor_flag:
            logger.debug("Monitoring already stopped")
            return

        self.monitoring_service.stop_monitoring()
        self._monitor_flag = False

    async def get_tile_data(self) -> dict[str, Any]:
        """Build tile data for display"""
        libraries_data = []

        for library_path in self.library_service.get_library_paths():
            library_info = await self._analyze_library(library_path)
            libraries_data.append(library_info)

        return {
            "libraries": libraries_data,
            "total_games": sum(lib["game_count"] for lib in libraries_data),
            "total_libraries": len(libraries_data),
        }

    async def get_library_games(self, library_path: str) -> list[dict[str, Any]]:
        """Get all games for a specific library with full details"""
        library_path_obj = Path(library_path)
        games = await self.game_loader_service.load_games_from_library(library_path_obj)
        return [game.to_dict() for game in games]

    async def _analyze_library(self, library_path: Path) -> dict[str, Any]:
        """Analyze a single library with async directory size calculations"""
        # Load all games with complete size information
        games = await self.game_loader_service.load_games_from_library(library_path)

        # Calculate totals
        total_games_size = sum(game.size_on_disk for game in games)
        total_shader_size = sum(game.shader_cache_size for game in games)
        total_workshop_size = sum(game.workshop_content_size for game in games)
        total_size = total_games_size + total_shader_size + total_workshop_size

        # Get drive info
        drive_info = get_drive_info(library_path)

        return {
            "path": str(library_path),
            "game_count": len(games),
            "total_games_size": total_games_size,
            "total_shader_size": total_shader_size,
            "total_workshop_size": total_workshop_size,
            "total_size": total_size,
            "drive_total": drive_info["total"],
            "drive_free": drive_info["free"],
            "drive_used": drive_info["used"],
        }

    def _handle_manifest_change(self, event_type: str, manifest_path: Path) -> None:
        """Handle manifest file changes from the monitoring service"""
        app_id_str = extract_app_id(manifest_path)
        if not app_id_str:
            return

        app_id = int(app_id_str)
        logger.info(f"Steam app {app_id} {event_type}: {manifest_path.name}")

        # Update manifest cache
        cache_action = None

        if event_type == "deleted":
            if self.cache_service.remove_manifest(manifest_path):
                cache_action = "removed"
                self.image_service.remove_image(app_id)
        elif event_type in ["created", "modified"]:
            action = self.cache_service.update_manifest(manifest_path)
            if action != "no_change":
                cache_action = action
                if action == "added":
                    self.image_service.download_image(app_id)

        # Update state if there was a change
        if cache_action and self._event_loop:
            asyncio.run_coroutine_threadsafe(
                self._state_update_callback(
                    last_change_at=datetime.now(),
                    last_change_type=event_type,
                    last_change_app_id=app_id,
                ),
                self._event_loop
            )
