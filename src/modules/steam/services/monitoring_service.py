from pathlib import Path
from typing import List, Callable, Optional

from watchdog.observers import Observer

from src.core.utils import get_logger
from ..services.manifest_handler import SteamManifestHandler

logger = get_logger(__name__)


class SteamMonitoringService:
    """Service for monitoring Steam library file changes"""

    def __init__(self, change_callback: Callable):
        self.change_callback = change_callback
        self.observer: Optional[Observer] = None
        self.manifest_handler: Optional[SteamManifestHandler] = None
        self.is_monitoring = False

    def start_monitoring(self, library_paths: List[Path]) -> None:
        """Start monitoring Steam libraries for changes"""
        if self.is_monitoring:
            logger.debug("Monitoring already started")
            return

        logger.info("Starting Steam file monitoring...")

        self.observer = Observer()
        self.manifest_handler = SteamManifestHandler(self.change_callback)

        # Watch each library's steamapps folder
        for library_path in library_paths:
            steamapps_path = library_path / 'steamapps'
            if steamapps_path.exists():
                self.observer.schedule(
                    self.manifest_handler,
                    str(steamapps_path),
                    recursive=False
                )
                logger.debug(f"Watching: {steamapps_path}")

        self.observer.start()
        self.is_monitoring = True
        logger.info("Steam file monitoring started")

    def stop_monitoring(self) -> None:
        """Stop monitoring Steam libraries"""
        if not self.is_monitoring:
            logger.debug("Monitoring already stopped")
            return

        logger.info("Stopping Steam file monitoring...")

        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5.0)
            self.observer = None

        self.manifest_handler = None
        self.is_monitoring = False
        logger.info("Steam file monitoring stopped")
