import json
from pathlib import Path

from ContaraNAS.core.utils import get_cache_dir, get_logger


logger = get_logger(__name__)


class StateManager:
    """Manages persistent state for modules across application restarts"""

    def __init__(self):
        self.state_file = get_cache_dir() / "module_states.json"
        self._enabled_modules: set[str] = set()
        self._load_state()

    def _load_state(self) -> None:
        """Load module states from disk"""
        try:
            if self.state_file.exists():
                with Path.open(self.state_file, encoding="utf-8") as f:
                    data = json.load(f)
                    self._enabled_modules = set(data.get("enabled_modules", []))
                    logger.info(
                        f"Loaded module states: {len(self._enabled_modules)} modules were enabled"
                    )
            else:
                logger.info("No previous module states found")
        except Exception as e:
            logger.error(f"Failed to load module states: {e}")
            self._enabled_modules = set()

    def _save_state(self) -> None:
        """Save module states to disk"""
        try:
            data = {"enabled_modules": list(self._enabled_modules)}

            with Path.open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved module states: {len(self._enabled_modules)} enabled modules")
        except Exception as e:
            logger.error(f"Failed to save module states: {e}")

    def mark_enabled(self, module_name: str) -> None:
        """Mark a module as enabled (will be restored on next startup)"""
        if module_name not in self._enabled_modules:
            self._enabled_modules.add(module_name)
            self._save_state()
            logger.debug(f"Marked module '{module_name}' as enabled")

    def mark_disabled(self, module_name: str) -> None:
        """Mark a module as disabled (won't be restored on next startup)"""
        if module_name in self._enabled_modules:
            self._enabled_modules.remove(module_name)
            self._save_state()
            logger.debug(f"Marked module '{module_name}' as disabled")

    def get_enabled_modules(self) -> set[str]:
        """Get all modules that should be enabled on startup"""
        return self._enabled_modules.copy()


# Global state manager instance
state_manager = StateManager()
