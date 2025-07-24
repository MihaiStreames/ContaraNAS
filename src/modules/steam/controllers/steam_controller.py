from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from src.core.utils import get_logger
from ..services.cache_service import SteamCacheService
from ..services.library_service import SteamLibraryService
from ..services.monitoring_service import SteamMonitoringService
from ..utils.steam_helpers import extract_app_id

logger = get_logger(__name__)


class SteamController:
    """Controller that orchestrates Steam module operations"""

    def __init__(self, state_update_callback):
        self.state_update_callback = state_update_callback
        self.monitor_flag = False
        self.library_service = SteamLibraryService()
        self.cache_service = SteamCacheService()
        self.monitoring_service = SteamMonitoringService(self._handle_manifest_change)

    def initialize(self) -> None:
        """Initialize the controller and its services"""
        logger.info("Initializing Steam controller...")

        # Initialize library service
        if not self.library_service.initialize():
            raise RuntimeError("Failed to initialize Steam library service")

        # Initialize cache
        self.cache_service.initialize_cache(self.library_service.get_library_paths())

        # Update state
        self.state_update_callback(
            initialized_at=datetime.now(),
            steam_path=str(self.library_service.get_steam_path()),
            library_count=len(self.library_service.get_library_paths()),
            game_count=self.cache_service.get_game_count()
        )

        logger.info("Steam controller initialized successfully")

    def start_monitoring(self) -> None:
        """Start monitoring Steam libraries"""
        if self.monitor_flag:
            logger.debug("Monitoring already started")
            return

        self.monitoring_service.start_monitoring(self.library_service.get_library_paths())
        self.monitor_flag = True

    def stop_monitoring(self) -> None:
        """Stop monitoring Steam libraries"""
        if not self.monitor_flag:
            logger.debug("Monitoring already stopped")
            return

        self.monitoring_service.stop_monitoring()
        self.monitor_flag = False

    def get_tile_data(self) -> Dict[str, Any]:
        """Get data for the dashboard tile"""
        return {
            "total_games": self.cache_service.get_game_count(),
            "library_count": len(self.library_service.get_library_paths()),
            "status": "monitoring" if self.monitor_flag else "idle",
            "steam_path": str(self.library_service.get_steam_path()) if self.library_service.get_steam_path() else None,
        }

    def _handle_manifest_change(self, event_type: str, manifest_path: Path) -> None:
        """Handle manifest file changes from the monitoring service"""
        app_id = extract_app_id(manifest_path)

        # Log the change
        if app_id:
            logger.info(f"Steam app {app_id} {event_type}: {manifest_path.name}")
        else:
            logger.info(f"Manifest {event_type}: {manifest_path.name}")

        # Update cache
        cache_action = None
        old_count = self.cache_service.get_game_count()

        if event_type == 'deleted':
            if self.cache_service.remove_manifest(manifest_path):
                cache_action = "removed"
        elif event_type in ['created', 'modified']:
            action = self.cache_service.update_manifest(manifest_path)
            if action != 'no_change':
                cache_action = action

        # Update state if there was a change
        if cache_action:
            new_count = self.cache_service.get_game_count()
            count_change = new_count - old_count

            if count_change != 0:
                logger.debug(
                    f"Cache {cache_action}: {manifest_path.name} (total: {new_count}, change: {count_change:+d})")
            else:
                logger.debug(f"Cache {cache_action}: {manifest_path.name}")

            # Update module state
            self.state_update_callback(
                game_count=self.cache_service.get_game_count(),
                last_change_type=event_type,
                last_change_file=manifest_path.name,
                last_change_time=datetime.now(),
                last_change_app_id=app_id
            )
