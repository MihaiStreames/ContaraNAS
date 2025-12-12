from collections.abc import Callable
import time
from typing import Any

import psutil

from ContaraNAS.core import get_logger
from ContaraNAS.core import load_file
from ContaraNAS.core import save_file
from ContaraNAS.core import settings


logger = get_logger(__name__)


class HardwareCacheService:
    """Service for caching hardware information that requires elevated privileges"""

    def __init__(self, cache_name: str = "hardware"):
        self._cache_dir = settings.cache_dir / "hardware"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_file = self._cache_dir / f"{cache_name}_cache.json"
        self._boot_time = psutil.boot_time()

    def needs_refresh(self) -> bool:
        """Check if cache needs refresh (based on system boot time)"""
        cache_data = load_file(self._cache_file)

        if not cache_data:
            logger.warning(f"Hardware cache is corrupted or empty: {self._cache_file}")
            return True

        cached_boot_time = cache_data.get("boot_time")
        if cached_boot_time is None:
            return True

        if abs(cached_boot_time - self._boot_time) > 1.0:
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

        save_file(self._cache_file, cache_data, pretty=True)
        logger.debug(f"Saved hardware cache to {self._cache_file}")

    def load_cache(self) -> dict[str, Any] | None:
        """Load hardware information from cache"""
        cache_data = load_file(self._cache_file)
        return cache_data.get("hardware") if cache_data else None

    def get_or_collect_hardware_info(self, collect_fn: Callable) -> dict[str, Any]:
        """Get hardware info from cache or collect it (requiring sudo)"""
        if not self.needs_refresh():
            cached_data = self.load_cache()
            if cached_data:
                logger.debug(f"Using cached hardware info from {self._cache_file}")
                return cached_data

        logger.debug(f"Collecting fresh hardware info (may require sudo) for {self._cache_file}")
        hardware_data = collect_fn()
        self.save_cache(hardware_data)
        return hardware_data
