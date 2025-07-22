import os
from pathlib import Path
from typing import Dict, Any, List

from src.core.utils import save_json, load_json, get_logger

logger = get_logger(__name__)


class SteamCachingService:
    """Service for caching important data for faster access"""

    def __init__(self):
        self.cache_dir = Path(".cache/steam/libraries")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def cache_library(
            self,
            library_path: Path,
            manifests: List[Path],
            size_breakdown: Dict[str, int],
            game_count: int
    ) -> bool:
        """Cache library stats and manifest mtimes"""
        cache_file = self.cache_dir / f"{library_path.name}.json"
        try:
            manifest_info = {
                str(m): os.stat(m).st_mtime for m in manifests if m.exists()
            }
            cache_data = {
                "library_path": str(library_path),
                "last_modified": max(manifest_info.values(), default=0),
                "size_breakdown": size_breakdown,
                "game_count": game_count,
                "manifests": manifest_info
            }
            save_json(cache_file, cache_data)
            logger.debug(f"Cached library: {library_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to cache library {library_path}: {e}")
            return False

    def load_library_cache(
            self,
            library_path: Path
    ) -> Dict[str, Any]:
        """Load cached library info"""
        cache_file = self.cache_dir / f"{library_path.name}.json"
        if not cache_file.exists():
            return {}
        try:
            return load_json(cache_file)
        except Exception as e:
            logger.error(f"Failed to load cache for {library_path}: {e}")
            return {}
