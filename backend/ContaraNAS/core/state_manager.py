import json
from pathlib import Path

from ContaraNAS.core import settings, get_logger, load_file, save_file

logger = get_logger(__name__)


class StateManager:
    """Manages persistent state for modules across application restarts"""

    def __init__(self):
        self._state_file = settings.cache_dir / "module_states.json"
        self._enabled_modules: set[str] = set()
        self._load_state()

    def _load_state(self) -> None:
        """Load module states from disk"""
        data = load_file(self._state_file)
        
        if data:
            self._enabled_modules = set(data.get("enabled_modules", []))
            logger.info(f"Loaded module states: {len(self._enabled_modules)} modules were enabled")
        else:
            logger.info("No previous module states found")

    def _save_state(self) -> None:
        """Save module states to disk"""
        try:
            settings.cache_dir.mkdir(parents=True, exist_ok=True)
            save_file(
                self._state_file,
                {"enabled_modules": list(self._enabled_modules)},
                pretty=True,
            )
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


state_manager = StateManager()
