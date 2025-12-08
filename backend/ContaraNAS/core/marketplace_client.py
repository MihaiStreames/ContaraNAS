import hashlib
import json
from pathlib import Path
import time

import aiohttp

from ContaraNAS.core import settings
from ContaraNAS.core.exceptions import ChecksumMismatchError, MarketplaceError
from ContaraNAS.core.utils import get_logger


logger = get_logger(__name__)


class MarketplaceClient:
    """HTTP client for ContaraNAS marketplace server"""

    def __init__(
        self,
        base_url: str,
        backend_version: str,
        cache_ttl: int = 3600,
    ):
        self._base_url = base_url.rstrip("/")
        self._backend_version = backend_version
        self._cache_ttl = cache_ttl

        # Cache
        self._cache_dir = settings.cache_dir / "marketplace"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._registry_cache: dict | None = None
        self._registry_cache_time: float = 0

    async def get_registry(self, force_refresh: bool = False) -> dict:
        """Fetch module registry from marketplace"""
        # Return cache if valid
        if not force_refresh and self._is_cache_valid():
            logger.debug("Using cached registry")
            return self._registry_cache

        logger.info(f"Fetching registry from {self._base_url}")

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self._base_url}/registry"
                params = {"backend_version": self._backend_version}

                async with session.get(url, params=params, timeout=30) as resp:
                    if resp.status != 200:
                        raise MarketplaceError(f"Failed to fetch registry: HTTP {resp.status}")

                    data = await resp.json()

        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to marketplace: {e}")

            # Return stale cache if available
            if self._registry_cache:
                logger.warning("Using stale cache due to connection error")
                return self._registry_cache

            raise MarketplaceError(f"Cannot connect to marketplace: {e}") from e

        # Verify checksum
        expected_checksum = data.get("checksum", "")
        modules_data = data.get("modules", {})

        if not self._verify_checksum(modules_data, expected_checksum):
            raise ChecksumMismatchError("Registry checksum verification failed")

        # Update cache
        self._registry_cache = data
        self._registry_cache_time = time.time()
        self._save_cache_to_disk(data)

        logger.info(f"Registry loaded: {len(modules_data)} modules available")
        return data

    async def get_module(self, module_id: str) -> dict | None:
        """Fetch detailed information about a specific module"""
        logger.debug(f"Fetching module details: {module_id}")

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self._base_url}/modules/{module_id}"
                params = {"backend_version": self._backend_version}

                async with session.get(url, params=params, timeout=30) as resp:
                    if resp.status == 404:
                        return None

                    if resp.status != 200:
                        raise MarketplaceError(f"Failed to fetch module: HTTP {resp.status}")

                    data = await resp.json()
                    return data.get("module")

        except aiohttp.ClientError as e:
            logger.error(f"Failed to fetch module {module_id}: {e}")
            raise MarketplaceError(f"Cannot fetch module: {e}") from e

    async def download_module(self, module_id: str, version: str) -> Path:
        """Download a module zip file"""
        logger.info(f"Downloading module: {module_id} v{version}")

        download_dir = self._cache_dir / "downloads"
        download_dir.mkdir(parents=True, exist_ok=True)

        zip_path = download_dir / f"{module_id}-{version}.zip"

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self._base_url}/modules/{module_id}/versions/{version}/download"

                async with session.get(url, timeout=300) as resp:
                    if resp.status == 404:
                        raise MarketplaceError(f"Module {module_id} v{version} not found")

                    if resp.status != 200:
                        raise MarketplaceError(f"Download failed: HTTP {resp.status}")

                    expected_checksum = resp.headers.get("X-Checksum-SHA256")
                    content = await resp.read()

        except aiohttp.ClientError as e:
            logger.error(f"Failed to download module: {e}")
            raise MarketplaceError(f"Download failed: {e}") from e

        # Verify checksum
        if expected_checksum:
            computed = hashlib.sha256(content).hexdigest()
            if computed != expected_checksum:
                raise ChecksumMismatchError(
                    f"Module download corrupted: expected {expected_checksum}, got {computed}"
                )
            logger.debug("Checksum verified")
        else:
            logger.warning("No checksum header in response, skipping verification")

        # Save to file
        zip_path.write_bytes(content)
        logger.info(f"Module downloaded to {zip_path}")

        return zip_path

    def _is_cache_valid(self) -> bool:
        """Check if cached registry is still valid"""
        if self._registry_cache is None:
            # Try loading from disk
            self._load_cache_from_disk()

        if self._registry_cache is None:
            return False

        age = time.time() - self._registry_cache_time
        return age < self._cache_ttl

    @staticmethod
    def _verify_checksum(modules_data: dict, expected: str) -> bool:
        """Verify registry checksum"""
        if not expected:
            logger.warning("No checksum provided by marketplace")
            return True

        content = json.dumps(modules_data, sort_keys=True).encode()
        computed = f"sha256:{hashlib.sha256(content).hexdigest()}"

        if computed != expected:
            logger.error(f"Checksum mismatch: expected {expected}, got {computed}")
            return False

        logger.debug("Registry checksum verified")
        return True

    def _save_cache_to_disk(self, data: dict) -> None:
        """Save registry cache to disk"""
        cache_file = self._cache_dir / "registry_cache.json"
        cache_data = {
            "cached_at": self._registry_cache_time,
            "data": data,
        }

        try:
            with cache_file.open("w", encoding="utf-8") as f:
                json.dump(cache_data, f)
            logger.debug(f"Registry cache saved to {cache_file}")
        except OSError as e:
            logger.warning(f"Failed to save cache: {e}")

    def _load_cache_from_disk(self) -> None:
        """Load registry cache from disk"""
        cache_file = self._cache_dir / "registry_cache.json"

        if not cache_file.exists():
            return

        try:
            with cache_file.open(encoding="utf-8") as f:
                cache_data = json.load(f)

            self._registry_cache = cache_data.get("data")
            self._registry_cache_time = cache_data.get("cached_at", 0)
            logger.debug("Registry cache loaded from disk")

        except (OSError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load cache: {e}")
