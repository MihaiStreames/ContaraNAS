import asyncio
import contextlib
from pathlib import Path

import aiohttp
from backend.ContaraNAS.core import settings
from backend.ContaraNAS.core.utils import get_logger
from backend.ContaraNAS.modules.builtin.steam.constants import (
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
        self._image_cache_dir: Path = settings.cache_dir / "steam" / IMAGE_CACHE_DIR
        self._image_cache_dir.mkdir(parents=True, exist_ok=True)

        self._session: aiohttp.ClientSession | None = None
        self._download_task: asyncio.Task | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=HTTP_TIMEOUT_SECONDS)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def cleanup(self) -> None:
        """Clean up resources"""
        if self._download_task and not self._download_task.done():
            self._download_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._download_task
            self._download_task = None

        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def sync_with_manifest_cache(self, installed_app_ids: list[int]) -> None:
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

        # Find missing images
        missing_app_ids = []
        for app_id in installed_app_ids:
            image_path = self._image_cache_dir / f"{app_id}.jpg"
            if not image_path.exists():
                missing_app_ids.append(app_id)

        # Download missing images in background
        if missing_app_ids:
            # Cancel any existing download task
            if self._download_task and not self._download_task.done():
                self._download_task.cancel()
                with contextlib.suppress(asyncio.CancelledError):
                    await self._download_task

            self._download_task = asyncio.create_task(self._download_images(missing_app_ids))
            logger.info(f"Queued {len(missing_app_ids)} images for background download")

    async def download_image(self, app_id: int) -> None:
        """Download image for a single app ID"""
        image_path = self._image_cache_dir / f"{app_id}.jpg"

        # Skip if already cached
        if image_path.exists():
            return

        cover_url = f"https://steamcdn-a.akamaihd.net/steam/apps/{app_id}/header.jpg"

        session = await self._get_session()

        for attempt in range(HTTP_RETRY_COUNT):
            try:
                logger.debug(f"Downloading image for app {app_id} (attempt {attempt + 1})")
                async with session.get(cover_url) as response:
                    response.raise_for_status()
                    content = await response.read()

                    # Check if we got a valid image
                    if len(content) < MIN_VALID_IMAGE_SIZE:
                        logger.warning(f"Received small image for app {app_id}, skipping")
                        return

                    # Save the image
                    image_path.write_bytes(content)
                    logger.debug(f"Successfully cached image for app {app_id}")
                    return

            except aiohttp.ClientResponseError as e:
                if e.status in {429, 500, 502, 503, 504} and attempt < HTTP_RETRY_COUNT - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff
                    continue
                logger.error(f"Failed to download image for app {app_id}: HTTP {e.status}")
                return
            except Exception as e:
                logger.error(f"Failed to download image for app {app_id}: {e}")
                return

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
                await self.download_image(app_id)
                # Rate limit to be nice to Steam's servers
                await asyncio.sleep(IMAGE_DOWNLOAD_DELAY)
            except asyncio.CancelledError:
                logger.debug("Image download task cancelled")
                raise
            except Exception as e:
                logger.error(f"Error in background download for app {app_id}: {e}")
