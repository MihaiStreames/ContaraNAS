from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from src.core.utils import get_logger

from ..services import (SteamCacheService, SteamLibraryService,
                        SteamMonitoringService, SteamParsingService)
from ..utils.steam_helpers import extract_app_id, get_drive_info

logger = get_logger(__name__)


class SteamController:
    """Controller that orchestrates Steam module operations"""

    def __init__(self, state_update_callback):
        self.state_update_callback = state_update_callback
        self.monitor_flag = False

        self.library_service = SteamLibraryService()
        self.parsing_service = SteamParsingService(
            self.library_service.get_steam_path()
        )
        self.cache_service = SteamCacheService()
        self.monitoring_service = SteamMonitoringService(self._handle_manifest_change)

    def initialize(self) -> None:
        """Initialize the controller and its services"""
        logger.info("Initializing Steam controller...")

        # Initialize library service
        if not self.library_service.initialize():
            raise RuntimeError("Failed to initialize Steam library service")

        # Initialize cache
        library_paths = self.library_service.get_library_paths()
        self.cache_service.initialize_cache(library_paths)

        # Update state
        self.state_update_callback(
            initialized_at=datetime.now(),
            steam_path=str(self.library_service.get_steam_path()),
            total_games=self.cache_service.get_game_count(),
            total_libraries=len(library_paths),
            last_scan_completed=datetime.now(),
        )

        logger.info("Steam controller initialized successfully")

    def start_monitoring(self) -> None:
        """Start monitoring Steam libraries"""
        if self.monitor_flag:
            logger.debug("Monitoring already started")
            return

        self.cache_service.update_cache(self.library_service.get_library_paths())
        self.monitoring_service.start_monitoring(
            self.library_service.get_library_paths()
        )
        self.monitor_flag = True

    def stop_monitoring(self) -> None:
        """Stop monitoring Steam libraries"""
        if not self.monitor_flag:
            logger.debug("Monitoring already stopped")
            return

        self.monitoring_service.stop_monitoring()
        self.monitor_flag = False

    def get_tile_data(self) -> Dict[str, Any]:
        """Build tile data for display"""
        libraries_data = []

        for library_path in self.library_service.get_library_paths():
            library_info = self._analyze_library(library_path)
            libraries_data.append(library_info)

        return {
            "libraries": libraries_data,
        }

    def _analyze_library(self, library_path: Path) -> Dict[str, Any]:
        """Analyze a single library"""
        steamapps_path = library_path / "steamapps"
        games = []

        # Parse all games in this library
        if steamapps_path.exists():
            for manifest_path in steamapps_path.glob("appmanifest_*.acf"):
                game = self.parsing_service.create_game_from_manifest(
                    manifest_path, library_path
                )
                if game:
                    games.append(game)

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
        app_id = extract_app_id(manifest_path)
        logger.info(f"Steam app {app_id} {event_type}: {manifest_path.name}")

        # Update cache
        cache_action = None

        if event_type == "deleted":
            if self.cache_service.remove_manifest(manifest_path):
                cache_action = "removed"
        elif event_type in ["created", "modified"]:
            action = self.cache_service.update_manifest(manifest_path)
            if action != "no_change":
                cache_action = action

        # Update state if there was a change
        if cache_action:
            self.state_update_callback(
                total_games=self.cache_service.get_game_count(),
                last_change_at=datetime.now(),
                last_change_type=event_type,
                last_change_app_id=app_id,
            )
