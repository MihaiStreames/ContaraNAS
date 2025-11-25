from collections.abc import Callable
from pathlib import Path

from backend.ContaraNAS.core.utils import get_logger
from backend.ContaraNAS.modules.steam.constants import OBSERVER_JOIN_TIMEOUT
from watchdog.observers import Observer

from .manifest_handler import SteamManifestHandler


logger = get_logger(__name__)


class SteamMonitoringService:
    """Service for monitoring Steam library file changes"""

    def __init__(self, change_callback: Callable[[str, Path], None]):
        self._change_callback: Callable[[str, Path], None] = change_callback
        self._monitor_flag: bool = False
        self._observer: Observer | None = None

        self.manifest_handler: SteamManifestHandler | None = None

    def start_monitoring(self, library_paths: list[Path]) -> None:
        """Start monitoring Steam libraries for changes"""
        if self._monitor_flag:
            logger.debug("Monitoring already started")
            return

        logger.info("Starting Steam file monitoring...")

        self._observer = Observer()
        self.manifest_handler = SteamManifestHandler(self._change_callback)

        # Watch each library's steamapps folder
        for library_path in library_paths:
            steamapps_path = library_path / "steamapps"
            if steamapps_path.exists():
                self._observer.schedule(self.manifest_handler, str(steamapps_path), recursive=False)
                logger.debug(f"Watching: {steamapps_path}")

        self._observer.start()
        self._monitor_flag = True
        logger.info("Steam file monitoring started")

    def stop_monitoring(self) -> None:
        """Stop monitoring Steam libraries"""
        if not self._monitor_flag:
            logger.debug("Monitoring already stopped")
            return

        logger.info("Stopping Steam file monitoring...")

        if self._observer:
            self._observer.stop()
            self._observer.join(timeout=OBSERVER_JOIN_TIMEOUT)
            self._observer = None

        self.manifest_handler = None
        self._monitor_flag = False
        logger.info("Steam file monitoring stopped")
