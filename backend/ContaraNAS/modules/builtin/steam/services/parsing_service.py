from pathlib import Path
from typing import Any

import vdf

from ContaraNAS.core.utils import get_logger
from ContaraNAS.modules.builtin.steam.constants import LIBRARY_FOLDERS_FILE, STEAMAPPS_DIR
from ContaraNAS.modules.builtin.steam.dtos import SteamGame


logger = get_logger(__name__)


class SteamParsingService:
    """Service for parsing Steam VDF and ACF files"""

    def __init__(self, steam_path: Path):
        self._libraries: list[Path] = []
        self._steam_path: Path = steam_path

    def get_library_paths(self) -> list[Path]:
        """Get all Steam library paths from libraryfolders.vdf"""
        if not self._libraries:
            libraryfolders_file = self._steam_path / STEAMAPPS_DIR / LIBRARY_FOLDERS_FILE
            if not libraryfolders_file.exists():
                logger.error(f"{LIBRARY_FOLDERS_FILE} not found at {libraryfolders_file}")
                return []

            try:
                with Path.open(libraryfolders_file, encoding="utf-8") as f:
                    data = vdf.load(f)
                    libraries_data = data.get("libraryfolders", {})

                    for lib_data in libraries_data.values():
                        if isinstance(lib_data, dict) and "path" in lib_data:
                            path = lib_data["path"]
                            self._libraries.append(Path(path))

                    if not self._libraries:
                        logger.warning("No library folders found in libraryfolders.vdf")
            except Exception as e:
                logger.error(f"Error reading libraryfolders.vdf: {e}")
                return []

        return self._libraries

    @staticmethod
    def parse_app_manifest(manifest_path: Path) -> dict[str, Any] | None:
        """Parse an app manifest (ACF) file"""
        try:
            with Path.open(manifest_path, encoding="utf-8") as f:
                data = vdf.load(f)
                app_state = data.get("AppState", {})

                if not app_state:
                    logger.warning(f"No AppState in manifest: {manifest_path}")
                    return None

                return app_state

        except Exception as e:
            logger.error(f"Error parsing manifest {manifest_path}: {e}")
            return None

    def create_game_from_manifest(
        self, manifest_path: Path, library_path: Path
    ) -> SteamGame | None:
        """Create a SteamGame instance from a manifest file"""
        app_state = self.parse_app_manifest(manifest_path)
        if not app_state:
            return None

        # Extract relevant fields
        app_id = int(app_state.get("appid", 0))
        name = app_state.get("name", "")

        if not app_id or not name:
            logger.warning(f"Missing required fields in manifest: {manifest_path}")
            return None

        # Create game instance
        try:
            return SteamGame(
                app_id=app_id,
                name=name,
                install_dir=app_state.get("installdir", ""),
                library_path=library_path,
                size_on_disk=int(app_state.get("SizeOnDisk", 0)),
                last_updated=int(app_state.get("lastupdated", 0)),
                last_played=int(app_state.get("LastPlayed", 0)),
                build_id=app_state.get("buildid", ""),
                bytes_to_download=int(app_state.get("BytesToDownload", 0)),
                bytes_downloaded=int(app_state.get("BytesDownloaded", 0)),
                state_flags=int(app_state.get("StateFlags", 4)),
                installed_depots=app_state.get("InstalledDepots", {}),
            )

        except Exception as e:
            logger.error(f"Error creating game from manifest {manifest_path}: {e}")
            return None
