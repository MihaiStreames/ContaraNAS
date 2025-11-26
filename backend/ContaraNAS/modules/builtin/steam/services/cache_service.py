from pathlib import Path

from backend.ContaraNAS.core import settings
from backend.ContaraNAS.core.utils import get_logger, load_json, save_json
from backend.ContaraNAS.modules.builtin.steam.utils import extract_app_id


logger = get_logger(__name__)


class SteamCacheService:
    """Service for caching Steam manifest file states"""

    def __init__(self):
        self._manifest_cache: dict[str, float] = {}  # manifest_path -> mtime
        self._cache_file: Path = settings.cache_dir / "steam" / "steam_cache.json"

    def initialize_cache(self, library_paths: list[Path]) -> None:
        """Initialize cache with current manifest states"""
        logger.debug("Initializing manifest cache...")

        if self._load_cache():
            logger.info(f"Loaded manifest cache from disk: {len(self._manifest_cache)} games")
            self.update_cache(library_paths)
        else:
            logger.info("No cache found, performing fresh initialization...")
            self._scan(library_paths)
            self._save_cache()

        logger.info(f"Cache initialized: {len(self._manifest_cache)} manifest files")

    def update_manifest(self, manifest_path: Path) -> str:
        """Update manifest in cache. Returns action taken: 'added', 'updated', or 'no_change'"""
        if not manifest_path.exists():
            return "no_change"

        mtime = manifest_path.stat().st_mtime
        old_mtime = self._manifest_cache.get(str(manifest_path))

        if old_mtime != mtime:
            self._manifest_cache[str(manifest_path)] = mtime
            self._save_cache()
            return "updated" if old_mtime else "added"

        return "no_change"

    def remove_manifest(self, manifest_path: Path) -> bool:
        """Remove manifest from cache. Returns True if it was cached."""
        was_cached = self._manifest_cache.pop(str(manifest_path), None) is not None

        if was_cached:
            self._save_cache()
        return was_cached

    def update_cache(self, library_paths: list[Path]) -> None:
        """Update cache with current manifest states"""
        logger.debug("Updating manifest cache...")

        current_manifests = self._get_manifests(library_paths)
        added, removed, changed = self._find_diff(current_manifests)
        self._apply_changes(current_manifests, added, removed, changed)

        self._save_cache()

        logger.info(
            f"Cache updated: {len(self._manifest_cache)} manifest files "
            f"(+{len(added)} added, -{len(removed)} removed, "
            f"{len(changed)} changed)"
        )

    def get_installed_app_ids(self) -> list[int]:
        """Get list of currently installed app IDs from manifest cache"""
        app_ids = []
        for manifest_path_str in self._manifest_cache:
            app_id_str = extract_app_id(Path(manifest_path_str))
            if app_id_str:
                app_ids.append(int(app_id_str))
        return app_ids

    def _save_cache(self) -> None:
        """Save manifest cache to JSON file"""
        cache_data = {"manifests": self._manifest_cache}
        save_json(self._cache_file, cache_data)
        logger.debug(f"Saved cache to {self._cache_file}")

    def _load_cache(self) -> bool:
        """Load manifest cache from JSON file"""
        if not self._cache_file.exists():
            return False

        cache_data = load_json(self._cache_file)
        if not cache_data or "manifests" not in cache_data:
            return False

        self._manifest_cache = cache_data["manifests"]
        logger.debug(f"Loaded cache from {self._cache_file}")
        return True

    def _scan(self, library_paths: list[Path]) -> None:
        """Scan library paths and update cache"""
        self._manifest_cache.clear()
        self._manifest_cache.update(self._get_manifests(library_paths))
        logger.debug(f"Cached {len(self._manifest_cache)} manifest files")

    @staticmethod
    def _get_manifests(library_paths: list[Path]) -> dict[str, float]:
        """Get current manifest files"""
        current_manifests = {}

        for library_path in library_paths:
            steamapps_path = library_path / "steamapps"
            if not steamapps_path.exists():
                continue

            for manifest_path in steamapps_path.glob("appmanifest_*.acf"):
                if manifest_path.exists():
                    mtime = manifest_path.stat().st_mtime
                    current_manifests[str(manifest_path)] = mtime

        return current_manifests

    def _find_diff(self, current_manifests: dict[str, float]) -> tuple:
        """Find manifests that were added, removed, or changed"""
        cached_paths = set(self._manifest_cache.keys())
        current_paths = set(current_manifests.keys())

        removed = cached_paths - current_paths
        added = current_paths - cached_paths
        existing = cached_paths & current_paths

        changed = {
            path for path in existing if self._manifest_cache[path] != current_manifests[path]
        }

        return added, removed, changed

    def _apply_changes(
        self,
        current_manifests: dict[str, float],
        added: set,
        removed: set,
        changed: set,
    ) -> None:
        """Apply the detected changes to the manifest cache"""
        # Remove missing manifests
        for manifest_path in removed:
            del self._manifest_cache[manifest_path]
            logger.debug(f"Removed missing manifest: {manifest_path}")

        # Add new manifests
        for manifest_path in added:
            self._manifest_cache[manifest_path] = current_manifests[manifest_path]
            logger.debug(f"Added new manifest: {manifest_path}")

        # Update changed manifests
        for manifest_path in changed:
            self._manifest_cache[manifest_path] = current_manifests[manifest_path]
            logger.debug(f"Updated manifest mtime: {manifest_path}")
