from ContaraNAS.core.utils import get_cache_dir, get_logger, load_json, save_json


logger = get_logger(__name__)


class SysMonitorPreferenceService:
    """Service for managing system monitor user preferences"""

    def __init__(self):
        self.cache_file = get_cache_dir() / "sys_monitor_preferences.json"
        self._preferences = self._load_preferences()

    def get_cpu_view_preference(self) -> bool:
        """Get the user's CPU view preference. Returns True for per-core view, False for general view"""
        return self._preferences.get("show_per_core", True)

    def set_cpu_view_preference(self, show_per_core: bool) -> None:
        """Set the user's CPU view preference"""
        self._preferences["show_per_core"] = show_per_core
        self._save_preferences()
        logger.debug(f"CPU view preference updated: show_per_core={show_per_core}")

    def _load_preferences(self) -> dict:
        """Load preferences from cache file"""
        if not self.cache_file.exists():
            logger.debug("No preference cache found, using defaults")
            return {}

        prefs = load_json(self.cache_file)
        if prefs:
            logger.debug(f"Loaded preferences from {self.cache_file}")
            return prefs

        logger.debug("Empty preference cache, using defaults")
        return {}

    def _save_preferences(self) -> None:
        """Save preferences to cache file"""
        try:
            save_json(self.cache_file, self._preferences)
            logger.debug(f"Saved preferences to {self.cache_file}")
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")
