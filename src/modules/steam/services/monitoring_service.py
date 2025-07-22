from pathlib import Path
from typing import Dict, Set, Optional

from src.core.utils import get_logger

logger = get_logger(__name__)


class SteamMonitoringService:
    """Service for monitoring Steam library changes via libraryfolders.vdf"""

    def __init__(self, steam_path: Path):
        self.steam_path = steam_path
        self.library_folders_path = steam_path / 'steamapps' / 'libraryfolders.vdf'

        # State tracking
        self._last_mtime: Optional[float] = None
        self._last_apps: Dict[str, Set[int]] = {}   # library_path -> set of app_ids
        self._last_sizes: Dict[int, int] = {}       # app_id -> size

    def check_for_changes(self) -> bool:
        """Quick check if libraryfolders.vdf has been modified"""
        try:
            current_mtime = self.library_folders_path.stat().st_mtime

            if self._last_mtime is None:
                self._last_mtime = current_mtime
                return True  # First check, consider as changed

            if current_mtime > self._last_mtime:
                self._last_mtime = current_mtime
                logger.debug("libraryfolders.vdf has been modified")
                return True

            return False

        except OSError as e:
            logger.error(f"Error checking libraryfolders.vdf: {e}")
            return False

    def analyze_changes(self, current_libraries: Dict[str, Dict]) -> Dict[str, any]:
        """Analyze what changed in the libraries"""
        changes = {
            'added_apps': [],        # List of (app_id, library_path)
            'removed_apps': [],      # List of (app_id, library_path)
            'size_changes': [],      # List of (app_id, old_size, new_size)
            'new_libraries': [],     # List of library paths
            'removed_libraries': []  # List of library paths
        }

        current_apps = {}  # app_id -> (library_path, size)
        current_libs = set()

        # Build current state
        for lib_path, lib_data in current_libraries.items():
            current_libs.add(lib_path)

            for app_id_str, size_str in lib_data.get('apps', {}).items():
                app_id = int(app_id_str)
                size = int(size_str)
                current_apps[app_id] = (lib_path, size)

        # Check for library changes
        old_libs = set(self._last_apps.keys())
        changes['new_libraries'] = list(current_libs - old_libs)
        changes['removed_libraries'] = list(old_libs - current_libs)

        # Check for app changes
        old_app_ids = set()
        for apps in self._last_apps.values():
            old_app_ids.update(apps)

        current_app_ids = set(current_apps.keys())

        # Added apps
        for app_id in current_app_ids - old_app_ids:
            lib_path, size = current_apps[app_id]
            changes['added_apps'].append((app_id, lib_path))
            logger.info(f"New app detected: {app_id} in {lib_path}")

        # Removed apps
        for app_id in old_app_ids - current_app_ids:
            # Find which library it was in
            for lib_path, apps in self._last_apps.items():
                if app_id in apps:
                    changes['removed_apps'].append((app_id, lib_path))
                    logger.info(f"App removed: {app_id} from {lib_path}")
                    break

        # Size changes
        for app_id in current_app_ids & old_app_ids:
            current_size = current_apps[app_id][1]
            old_size = self._last_sizes.get(app_id, 0)

            if current_size != old_size:
                changes['size_changes'].append((app_id, old_size, current_size))
                logger.debug(f"Size change for {app_id}: {old_size} -> {current_size}")

        # Update state
        self._last_apps.clear()
        self._last_sizes.clear()

        for lib_path, lib_data in current_libraries.items():
            app_ids = set()
            for app_id_str, size_str in lib_data.get('apps', {}).items():
                app_id = int(app_id_str)
                size = int(size_str)
                app_ids.add(app_id)
                self._last_sizes[app_id] = size

            self._last_apps[lib_path] = app_ids

        return changes

    def get_app_locations(self, libraries: Dict[str, Dict]) -> Dict[int, str]:
        """Get mapping of app_id to library_path from libraryfolders data"""
        app_locations = {}

        for lib_path, lib_data in libraries.items():
            for app_id_str in lib_data.get('apps', {}):
                app_id = int(app_id_str)
                app_locations[app_id] = lib_path

        return app_locations

    def reset_state(self):
        """Reset monitoring state"""
        self._last_mtime = None
        self._last_apps.clear()
        self._last_sizes.clear()
        logger.debug("Monitoring state reset")
