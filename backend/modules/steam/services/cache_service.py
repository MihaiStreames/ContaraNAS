from pathlib import Path
from typing import Optional, Dict, Any

import requests

from backend.core.utils import load_json, save_json, get_logger
from ..dtos.steam_game import SteamGame

logger = get_logger(__name__)


class SteamCachingService:
    """Service responsible for caching Steam game data and cover images."""

    def __init__(self):
        self.cache_dir = Path(".cache/games")
        self.images_dir = Path("resources/images/steam")

        # Ensure directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def load_game(self, app_id: int) -> Optional[Dict[str, Any]]:
        """Load game data from cache file."""
        cache_path = self.cache_dir / f"{app_id}.json"

        if not cache_path.exists():
            logger.debug(f"No cache found for AppID: {app_id}")
            return None

        try:
            data = load_json(cache_path)
            if data:
                logger.debug(f"Loaded cached data for AppID: {app_id}")
                return data
        except Exception as e:
            logger.error(f"Error loading cache for AppID {app_id}: {e}")

        return None

    def cache_game(self, game: SteamGame) -> bool:
        """Save game data to cache file."""
        cache_path = self.cache_dir / f"{game.app_id}.json"

        try:
            cache_data = game.to_dict()
            save_json(cache_path, cache_data)
            logger.debug(f"Saved cache for {game.name} (AppID: {game.app_id})")
            return True
        except Exception as e:
            logger.error(f"Error saving cache for {game.name} (AppID: {game.app_id}): {e}")
            return False

    def cache_cover(self, game: SteamGame) -> bool:
        """Download and cache cover image for a game."""
        image_path = self.images_dir / f"{game.app_id}.jpg"

        if image_path.exists():
            logger.debug(f"Cover image already exists for {game.name} (AppID: {game.app_id})")
            return True

        logger.debug(f"Downloading cover image for {game.name} (AppID: {game.app_id})")

        try:
            # Check if image exists before downloading
            response = requests.head(game.cover_image_url, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Cover image not available for {game.name} (HTTP {response.status_code})")
                return False

            # Download and save image
            image_response = requests.get(game.cover_image_url, timeout=10)
            if image_response.status_code == 200:
                with open(image_path, 'wb') as f:
                    f.write(image_response.content)
                logger.debug(f"Successfully cached cover image for {game.name}")
                return True
            else:
                logger.warning(f"Failed to download cover image for {game.name}")
                return False

        except requests.RequestException as e:
            logger.warning(f"Failed to cache cover image for {game.name} (AppID: {game.app_id}): {e}")
            return False

    def is_cache_valid(self, app_id: int, manifest_file: Path) -> bool:
        """Check if cached data is still valid compared to manifest file."""
        cache_path = Path(self.cache_dir) / f"{app_id}.json"

        if not cache_path.exists():
            return False

        if not manifest_file.exists():
            return True  # If manifest doesn't exist, cache is still valid

        try:
            cache_mtime = cache_path.stat().st_mtime
            manifest_mtime = manifest_file.stat().st_mtime
            return cache_mtime >= manifest_mtime
        except OSError:
            return False
