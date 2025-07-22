import os
from pathlib import Path
from typing import Dict, List

from src.core.utils import get_logger

logger = get_logger(__name__)


class SteamMonitoringService:
    """Service for monitoring the Steam library via game manifest files"""

    def __init__(self, steam_path: Path):
        self.steam_path = steam_path
        self._last_manifests: Dict[Path, float] = {}  # manifest_path -> mtime

    @staticmethod
    def get_manifest_files(libraries: List[Path]) -> List[Path]:
        """Get all manifest files from all libraries"""
        manifests = []
        for lib in libraries:
            steamapps = lib / 'steamapps'
            if steamapps.exists():
                manifests.extend(steamapps.glob('appmanifest_*.acf'))
        return manifests

    def check_for_changes(self, libraries: List[Path]) -> bool:
        """Check if any manifest file has changed"""
        manifests = self.get_manifest_files(libraries)
        changed = False
        current_manifests = {}

        for manifest in manifests:
            try:
                mtime = os.stat(manifest).st_mtime
                current_manifests[manifest] = mtime
                if manifest not in self._last_manifests or self._last_manifests[manifest] != mtime:
                    changed = True
            except OSError as e:
                logger.error(f"Error checking manifest {manifest}: {e}")

        self._last_manifests = current_manifests
        return changed

    def get_manifest_state(self) -> Dict[Path, float]:
        """Return current manifest paths and their mtimes"""
        return dict(self._last_manifests)

    def reset_state(self):
        self._last_manifests.clear()
        logger.debug("Monitoring state reset")
