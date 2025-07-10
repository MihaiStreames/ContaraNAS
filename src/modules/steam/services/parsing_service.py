from pathlib import Path
from typing import List, Optional

import vdf

from src.core.utils import get_logger
from ..dtos.steam_game import SteamGame
from ..utils.steam_helpers import get_size, check_url

logger = get_logger(__name__)


class SteamParsingService:
    """Service responsible for parsing Steam manifests and library folders."""

    def __init__(self, steam_path: str):
        self.steam_path = Path(steam_path)

    def get_library_paths(self) -> List[Path]:
        """Parse Steam library folders and return all library paths."""
        library_folders_file = self.steam_path / 'steamapps' / 'libraryfolders.vdf'

        try:
            with open(library_folders_file, 'r', encoding='utf-8') as f:
                libraries = vdf.load(f).get('libraryfolders', {})
                paths = [Path(lib['path']) for lib in libraries.values() if 'path' in lib]
                logger.info(f"Found {len(paths)} Steam library paths: {paths}")
                return paths
        except (FileNotFoundError, KeyError) as e:
            logger.error(f"Error: Unable to load library folders from {library_folders_file}: {e}")
            return []

    @staticmethod
    def get_manifest_files(library_path: Path) -> List[Path]:
        """Get all manifest files in a library path."""
        steamapps_path = library_path / 'steamapps'

        if not steamapps_path.exists():
            logger.warning(f"Steam library path does not exist: {steamapps_path}")
            return []

        manifest_files = []
        for file in steamapps_path.iterdir():
            if file.name.startswith('appmanifest_') and file.name.endswith('.acf'):
                manifest_files.append(file)

        return manifest_files

    def parse_manifest_file(self, manifest_path: Path, library_path: Path) -> Optional[SteamGame]:
        """Parse a single manifest file and return a SteamGame DTO."""
        try:
            # Extract app_id from filename
            app_id = int(manifest_path.stem.split('_')[1])

            logger.debug(f"Parsing manifest: {manifest_path}")

            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = vdf.load(f).get('AppState', {})
                name = data.get('name')

                if not name:
                    logger.warning(f"No name found in manifest {manifest_path}")
                    return None

                # Create base SteamGame with required fields
                game_data = {
                    'app_id': app_id,
                    'name': name,
                    'library_path': library_path,
                    'cover_image_url': f"https://steamcdn-a.akamaihd.net/steam/apps/{app_id}/header.jpg"
                }

                # Parse manifest data
                self._parse_manifest_data(game_data, data, library_path, app_id)

                # Create and return SteamGame DTO
                return SteamGame(**game_data)

        except Exception as e:
            logger.error(f"Error parsing manifest {manifest_path}: {e}")
            return None

    def check_manifest_changes(self, library_paths: List[Path], last_scan_time: float) -> bool:
        """Check if any manifest files have been modified since last scan."""
        for library_path in library_paths:
            manifest_files = self.get_manifest_files(library_path)

            for manifest_file in manifest_files:
                try:
                    if manifest_file.stat().st_mtime > last_scan_time:
                        logger.debug(f"Manifest file changed: {manifest_file.name}")
                        return True
                except OSError as e:
                    logger.error(f"Error checking manifest file {manifest_file}: {e}")

        return False

    def _parse_manifest_data(self, game_data: dict, acf_data: dict, library_path: Path, app_id: int):
        """Parse manifest ACF data and populate game_data dictionary."""
        # Basic size information
        game_data['size_on_disk'] = int(acf_data.get('SizeOnDisk', 0))

        # Store page URL (with validation)
        store_url = f"https://store.steampowered.com/app/{app_id}/"
        game_data['store_page_url'] = store_url if check_url(store_url) else None

        # Calculate additional sizes
        game_data['shader_cache_size'] = self._get_shader_cache_size(library_path, app_id)
        game_data['workshop_content_size'] = self._get_workshop_content_size(library_path, app_id)

        # Parse depots and calculate DLC size
        depots_info, dlc_size = self._parse_depots(acf_data, app_id)
        game_data['depots'] = depots_info
        game_data['dlc_size'] = dlc_size

    @staticmethod
    def _get_shader_cache_size(library_path: Path, app_id: int) -> int:
        """Calculate shader cache size for a game."""
        shader_cache_path = library_path / 'steamapps' / 'shadercache' / str(app_id)
        return get_size(shader_cache_path) if shader_cache_path.exists() else 0

    @staticmethod
    def _get_workshop_content_size(library_path: Path, app_id: int) -> int:
        """Calculate workshop content size for a game."""
        workshop_path = library_path / 'steamapps' / 'workshop' / 'content' / str(app_id)
        return get_size(workshop_path) if workshop_path.exists() else 0

    @staticmethod
    def _parse_depots(acf_data: dict, app_id: int) -> tuple[dict[str, int], int]:
        """Parse depot information from manifest data."""
        installed_depots = acf_data.get('InstalledDepots', {})
        depots_info = {}
        dlc_size_total = 0

        for depot_id, depot_data in installed_depots.items():
            depot_size = int(depot_data.get('size', 0))
            dlc_id = depot_data.get('dlcappid')

            if dlc_id:
                # DLC depot: show as "DLC_ID: DEPOT_ID"
                depot_name = f"{dlc_id}: {depot_id}"
                dlc_size_total += depot_size
            else:
                # Main game depot: show as "GAME_ID: DEPOT_ID"
                depot_name = f"{app_id}: {depot_id}"

            depots_info[depot_name] = depot_size

        return depots_info, dlc_size_total
