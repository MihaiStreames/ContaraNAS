import asyncio
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ContaraNAS.core.utils import get_cache_dir, get_logger
from ContaraNAS.modules.steam.constants import (
    HTTP_RETRY_COUNT,
    HTTP_TIMEOUT_SECONDS,
    IMAGE_CACHE_DIR,
    IMAGE_DOWNLOAD_DELAY,
    MIN_VALID_IMAGE_SIZE,
)


logger = get_logger(__name__)


class SteamImageService:
    """Service for caching Steam game images"""

    def __init__(self):
        self._image_cache_dir = get_cache_dir() / "steam" / IMAGE_CACHE_DIR
        self._image_cache_dir.mkdir(parents=True, exist_ok=True)

        # Setup requests session with retries
        self._session = requests.Session()
        retry_strategy = Retry(
            total=HTTP_RETRY_COUNT,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def sync_with_manifest_cache(self, installed_app_ids: list[int]) -> None:
        """Sync images with current manifest cache state"""
        installed_set = set(installed_app_ids)

        # Remove images for games no longer in manifest cache
        for image_file in self._image_cache_dir.glob("*.jpg"):
            try:
                app_id = int(image_file.stem)
                if app_id not in installed_set:
                    image_file.unlink()
                    logger.debug(f"Removed orphaned image for app {app_id}")
            except ValueError:
                continue

        # Download missing images in background
        missing_app_ids = []
        for app_id in installed_app_ids:
            image_path = self._image_cache_dir / f"{app_id}.jpg"
            if not image_path.exists():
                missing_app_ids.append(app_id)

        if missing_app_ids:
            asyncio.create_task(self._download_images(missing_app_ids))
            logger.info(f"Queued {len(missing_app_ids)} images for background download")

    def download_image(self, app_id: int) -> None:
        """Download image for a single app ID"""
        image_path = self._image_cache_dir / f"{app_id}.jpg"

        # Skip if already cached
        if image_path.exists():
            return

        cover_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{app_id}/header.jpg"

        try:
            logger.debug(f"Downloading image for app {app_id}")
            response = self._session.get(cover_url, timeout=HTTP_TIMEOUT_SECONDS)
            response.raise_for_status()

            # Check if we got a valid image
            if len(response.content) < MIN_VALID_IMAGE_SIZE:
                logger.warning(f"Received small image for app {app_id}, skipping")
                return

            # Save the image
            with Path.open(image_path, "wb") as f:
                f.write(response.content)

            logger.debug(f"Successfully cached image for app {app_id}")

        except Exception as e:
            logger.error(f"Failed to download image for app {app_id}: {e}")

    def remove_image(self, app_id: int) -> None:
        """Remove cached image for app ID"""
        image_path = self._image_cache_dir / f"{app_id}.jpg"

        if image_path.exists():
            image_path.unlink()
            logger.debug(f"Removed cached image for app {app_id}")

    async def _download_images(self, app_ids: list[int]) -> None:
        """Download images in background"""
        for app_id in app_ids:
            try:
                await asyncio.get_event_loop().run_in_executor(None, self.download_image, app_id)
                # Rate limit to be nice to Steam's servers
                await asyncio.sleep(IMAGE_DOWNLOAD_DELAY)
            except Exception as e:
                logger.error(f"Error in background download for app {app_id}: {e}")
