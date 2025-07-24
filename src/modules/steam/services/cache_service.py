from pathlib import Path
from typing import Dict, List

from src.core.utils import get_logger

logger = get_logger(__name__)


class SteamCacheService:
    """Service for caching Steam manifest file states"""

    def __init__(self):
        self.manifest_cache: Dict[Path, float] = {}  # manifest_path -> mtime

    def initialize_cache(self, library_paths: List[Path]) -> None:
        """Initialize cache with current manifest states"""
        logger.debug("Initializing manifest cache...")
        self.manifest_cache.clear()

        for library_path in library_paths:
            steamapps_path = library_path / 'steamapps'
            if not steamapps_path.exists():
                continue

            # Cache all manifest files
            for manifest_path in steamapps_path.glob('appmanifest_*.acf'):
                if manifest_path.exists():
                    mtime = manifest_path.stat().st_mtime
                    self.manifest_cache[manifest_path] = mtime

        logger.debug(f"Cached {len(self.manifest_cache)} manifest files")

    def update_manifest(self, manifest_path: Path) -> str:
        """Update manifest in cache. Returns action taken: 'added', 'updated', or 'no_change'"""
        if not manifest_path.exists():
            return 'no_change'

        mtime = manifest_path.stat().st_mtime
        old_mtime = self.manifest_cache.get(manifest_path)

        if old_mtime != mtime:
            self.manifest_cache[manifest_path] = mtime
            return "updated" if old_mtime else "added"

        return 'no_change'

    def remove_manifest(self, manifest_path: Path) -> bool:
        """Remove manifest from cache. Returns True if it was cached."""
        return self.manifest_cache.pop(manifest_path, None) is not None

    def get_game_count(self) -> int:
        """Get total number of cached games"""
        return len(self.manifest_cache)

    def clear(self) -> None:
        """Clear the cache"""
        self.manifest_cache.clear()
