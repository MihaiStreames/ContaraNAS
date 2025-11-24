import time
from typing import Any

import psutil

from ContaraNAS.core.utils import get_cache_dir, get_logger, load_json, save_json


logger = get_logger(__name__)


class HardwareCacheService:
    """Service for caching hardware information that requires elevated privileges"""

    def __init__(self, cache_name: str = "hardware"):
        self._cache_dir = get_cache_dir() / "hardware"
        self._cache_dir.mkdir(parents=True, exist_ok=True)

        self._cache_file = self._cache_dir / f"{cache_name}_cache.json"
        self._boot_time = psutil.boot_time()

    def needs_refresh(self) -> bool:
        """Check if cache needs refresh (based on system boot time)"""
        if not self._cache_file.exists():
            logger.warning(f"Hardware cache does not exist: {self._cache_file}")
            return True

        cache_data = load_json(self._cache_file)
        if not cache_data:
            logger.warning(f"Hardware cache is corrupted or empty: {self._cache_file}")
            return True

        cached_boot_time = cache_data.get("boot_time")
        if cached_boot_time is None:
            logger.warning(f"No boot time in cache: {self._cache_file}")
            return True

        # If boot time changed, system was rebooted
        if abs(cached_boot_time - self._boot_time) > 1.0:  # Allow 1 second tolerance
            logger.debug(
                f"System rebooted: cached boot time {cached_boot_time} != current {self._boot_time}"
            )
            return True

        logger.debug(f"Hardware cache is still valid: {self._cache_file}")
        return False

    def save_cache(self, hardware_data: dict[str, Any]) -> None:
        """Save hardware information to cache with current boot time"""
        cache_data = {
            "boot_time": self._boot_time,
            "cached_at": time.time(),
            "hardware": hardware_data,
        }
        save_json(self._cache_file, cache_data)
        logger.info(f"Saved hardware cache to {self._cache_file}")

    def load_cache(self) -> dict[str, Any] | None:
        """Load hardware information from cache"""
        if not self._cache_file.exists():
            return None

        cache_data = load_json(self._cache_file)
        if not cache_data:
            return None

        return cache_data.get("hardware")

    def get_or_collect_hardware_info(self, collect_fn: callable) -> dict[str, Any]:
        """Get hardware info from cache or collect it (requiring sudo)"""
        if not self.needs_refresh():
            cached_data = self.load_cache()
            if cached_data:
                logger.info(f"Using cached hardware information from {self._cache_file}")
                return cached_data

        logger.info(
            f"Collecting fresh hardware information (may require sudo) for {self._cache_file}"
        )
        hardware_data = collect_fn()
        self.save_cache(hardware_data)
        return hardware_data
