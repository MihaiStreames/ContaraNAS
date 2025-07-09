from pathlib import Path

from backend.core.utils import get_logger
from ..dtos.steam_game import SteamGame
from ..services.cache_service import SteamCachingService
from ..services.parsing_service import SteamParsingService

logger = get_logger(__name__)


class SteamController:
    """Controller that orchestrates Steam services to manage game data"""

    def __init__(self, steam_path: str):
        self.steam_path = steam_path
        self.games = []

        # Initialize services
        self.parsing_service = SteamParsingService(steam_path)
        self.caching_service = SteamCachingService()

        logger.info("SteamController initialized")

    def load_games(self):
        """Load all games from Steam libraries."""
        library_paths = self.parsing_service.get_library_paths()
        logger.info("Loading installed games from libraries.")

        self.games = []

        for library_path in library_paths:
            manifest_files = self.parsing_service.get_manifest_files(library_path)

            for manifest_file in manifest_files:
                try:
                    game = self._process_manifest(library_path, manifest_file)
                    if game:
                        self.games.append(game)
                except Exception as e:
                    logger.error(f"Error processing manifest {manifest_file.name}: {e}")

    def serialize_games(self):
        """Serialize games to dictionary format."""
        serialized = []

        for game in self.games:
            serialized.append(game.to_dict())

        logger.info(f"Serialized {len(serialized)} games")
        return serialized

    def _process_manifest(self, library_path: Path, manifest_file: Path) -> SteamGame | None:
        """Process a single manifest file."""
        app_id = int(manifest_file.stem.split('_')[1])

        logger.debug(f"Processing manifest: {manifest_file}")

        # Try to load from cache first
        cached_data = self.caching_service.load_game(app_id)
        if cached_data and self.caching_service.is_cache_valid(app_id, manifest_file):
            logger.debug(f"Loading {cached_data['name']} from cache")
            return self._create_game_from_cache(cached_data)

        # Parse from manifest if not in cache or cache is invalid
        game = self.parsing_service.parse_manifest_file(manifest_file, library_path)
        if game:
            logger.debug(f"Checking for updates for {game.name} (AppID: {game.app_id})")

            # Cache the game data and cover image
            self.caching_service.cache_game(game)
            self.caching_service.cache_cover(game)

            return game

        return None

    def _create_game_from_cache(self, cache_data: dict) -> SteamGame:
        """Create a SteamGame DTO from cached data."""
        game_data = {
            'app_id': cache_data['app_id'],
            'name': cache_data['name'],
            'library_path': Path(cache_data['library_path']),
            'cover_image_url': cache_data.get('cover_image_url', ''),
            'store_page_url': cache_data.get('store_page_url'),
            'size_on_disk': cache_data.get('size_on_disk', 0),
            'dlc_size': cache_data.get('dlc_size', 0),
            'shader_cache_size': cache_data.get('shader_cache_size', 0),
            'workshop_content_size': cache_data.get('workshop_content_size', 0),
            'depots': cache_data.get('depots', {})
        }

        return SteamGame(**game_data)
