from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import requests

from src.core.utils import load_json, save_json, get_logger
from ..dtos.steam_game import SteamGame

logger = get_logger(__name__)


class SteamCachingService:
    """Service for caching Steam game data"""

    def __init__(self):
        self.cache_dir = Path(".cache/steam/games")
        self.images_dir = Path(".cache/steam/images")

        # Create directories
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def cache_game(self, game: SteamGame) -> bool:
        """Save game data to cache"""
        cache_file = self.cache_dir / f"{game.app_id}.json"

        try:
            cache_data = {
                'data': game.to_dict(),
                'cached_at': datetime.now().isoformat(),
                'manifest_mtime': None
            }

            # Store manifest modification time if available
            if game.manifest_path.exists():
                cache_data['manifest_mtime'] = game.manifest_path.stat().st_mtime

            save_json(cache_file, cache_data)
            logger.debug(f"Cached game: {game.name} ({game.app_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to cache game {game.name}: {e}")
            return False

    def load_game(self, app_id: int) -> Optional[SteamGame]:
        """Load game from cache"""
        cache_file = self.cache_dir / f"{app_id}.json"

        if not cache_file.exists():
            return None

        try:
            cache_data = load_json(cache_file)
            if not cache_data or 'data' not in cache_data:
                return None

            game_data = cache_data['data']
            # Convert library_path back to Path
            game_data['library_path'] = Path(game_data['library_path'])

            return SteamGame(**game_data)

        except Exception as e:
            logger.error(f"Failed to load game {app_id} from cache: {e}")
            return None

    def is_cache_valid(self, app_id: int, manifest_path: Path) -> bool:
        """Check if cached data is still valid"""
        cache_file = self.cache_dir / f"{app_id}.json"

        if not cache_file.exists():
            return False

        try:
            cache_data = load_json(cache_file)
            if not cache_data:
                return False

            # Check if manifest has been modified
            if manifest_path.exists() and 'manifest_mtime' in cache_data:
                current_mtime = manifest_path.stat().st_mtime
                cached_mtime = cache_data['manifest_mtime']

                if current_mtime > cached_mtime:
                    logger.debug(f"Manifest updated for app {app_id}")
                    return False

            # Optional: Check cache age
            cached_at = datetime.fromisoformat(cache_data.get('cached_at', '2000-01-01'))
            age_days = (datetime.now() - cached_at).days

            if age_days > 7:  # Refresh after a week
                logger.debug(f"Cache too old for app {app_id}: {age_days} days")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating cache for app {app_id}: {e}")
            return False

    def cache_image(self, app_id: int, image_url: str) -> bool:
        """Download and cache game cover image"""
        image_file = self.images_dir / f"{app_id}.jpg"

        if image_file.exists():
            return True

        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                image_file.write_bytes(response.content)
                logger.debug(f"Cached image for app {app_id}")
                return True
            else:
                logger.warning(f"Failed to download image for app {app_id}: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.warning(f"Error caching image for app {app_id}: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.json"))
        image_files = list(self.images_dir.glob("*.jpg"))

        total_size = sum(f.stat().st_size for f in cache_files)
        total_size += sum(f.stat().st_size for f in image_files)

        return {
            'cached_games': len(cache_files),
            'cached_images': len(image_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_directory': str(self.cache_dir)
        }
