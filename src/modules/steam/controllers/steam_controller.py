from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.core.utils import get_logger
from ..dtos.steam_game import SteamGame
from ..services.cache_service import SteamCachingService
from ..services.monitoring_service import SteamMonitoringService
from ..services.parsing_service import SteamParsingService

logger = get_logger(__name__)


class SteamController:
    """Controller orchestrating Steam services"""

    def __init__(self, steam_path: Path):
        self.steam_path = steam_path
        self.games: List[SteamGame] = []

        # Initialize services
        self.parsing_service = SteamParsingService(steam_path)
        self.caching_service = SteamCachingService()
        self.monitoring_service = SteamMonitoringService(steam_path)

        logger.info(f"SteamController initialized with path: {steam_path}")

    def load_games(self) -> None:
        """Load all games from Steam libraries"""
        logger.info("Loading Steam games...")
        start_time = datetime.now()

        # Parse library folders
        libraries = self.parsing_service.parse_library_folders()
        if not libraries:
            logger.error("No Steam libraries found")
            return

        self.games = []
        cached_count = 0
        parsed_count = 0

        # Get app locations from libraryfolders.vdf
        app_locations = self.monitoring_service.get_app_locations(libraries)

        # Process each app
        for app_id, library_path_str in app_locations.items():
            library_path = Path(library_path_str)
            manifest_path = library_path / 'steamapps' / f'appmanifest_{app_id}.acf'

            if not manifest_path.exists():
                logger.warning(f"Manifest not found for app {app_id}")
                continue

            # Try cache first
            if self.caching_service.is_cache_valid(app_id, manifest_path):
                game = self.caching_service.load_game(app_id)
                if game:
                    self.games.append(game)
                    cached_count += 1
                    continue

            # Parse from manifest
            game = self.parsing_service.create_game_from_manifest(manifest_path, library_path)
            if game:
                self.games.append(game)
                parsed_count += 1

                # Cache the game
                self.caching_service.cache_game(game)
                self.caching_service.cache_image(game.app_id, game.cover_url)

        duration = (datetime.now() - start_time).total_seconds()
        logger.info(
            f"Loaded {len(self.games)} games in {duration:.2f}s "
            f"(cached: {cached_count}, parsed: {parsed_count})"
        )

        # Reset monitoring state after full load
        self.monitoring_service.reset_state()

    def check_for_changes(self) -> Optional[Dict[str, Any]]:
        """Check for library changes using monitoring service"""
        if not self.monitoring_service.check_for_changes():
            return None

        logger.info("Library changes detected")

        # Get current library state
        libraries = self.parsing_service.parse_library_folders()
        if not libraries:
            return None

        # Analyze changes
        changes = self.monitoring_service.analyze_changes(libraries)

        # Process changes
        if changes['added_apps'] or changes['removed_apps'] or changes['size_changes']:
            self._process_changes(changes)

            return {
                'timestamp': datetime.now().isoformat(),
                'added': len(changes['added_apps']),
                'removed': len(changes['removed_apps']),
                'updated': len(changes['size_changes'])
            }

        return None

    def _process_changes(self, changes: Dict[str, Any]) -> None:
        """Process detected changes"""
        # Remove games
        for app_id, library_path in changes['removed_apps']:
            self.games = [g for g in self.games if g.app_id != app_id]
            logger.info(f"Removed game: {app_id}")

        # Add new games
        for app_id, library_path_str in changes['added_apps']:
            library_path = Path(library_path_str)
            manifest_path = library_path / 'steamapps' / f'appmanifest_{app_id}.acf'

            if manifest_path.exists():
                game = self.parsing_service.create_game_from_manifest(manifest_path, library_path)
                if game:
                    self.games.append(game)
                    self.caching_service.cache_game(game)
                    self.caching_service.cache_image(game.app_id, game.cover_url)
                    logger.info(f"Added game: {game.name}")

        # Handle size changes (potential updates)
        for app_id, old_size, new_size in changes['size_changes']:
            # Find the game
            game = next((g for g in self.games if g.app_id == app_id), None)
            if game:
                # Reload from manifest to get updated info
                manifest_path = game.manifest_path
                if manifest_path.exists():
                    updated_game = self.parsing_service.create_game_from_manifest(
                        manifest_path,
                        game.library_path
                    )
                    if updated_game:
                        # Replace in list
                        self.games = [g if g.app_id != app_id else updated_game for g in self.games]
                        self.caching_service.cache_game(updated_game)
                        logger.info(f"Updated game: {updated_game.name}")

    def get_games_by_library(self) -> Dict[str, List[SteamGame]]:
        """Group games by library path"""
        grouped = {}

        for game in self.games:
            lib_path = str(game.library_path)
            if lib_path not in grouped:
                grouped[lib_path] = []
            grouped[lib_path].append(game)

        # Sort games in each library by name
        for games in grouped.values():
            games.sort(key=lambda g: g.name.lower())

        return grouped

    def get_library_stats(self) -> Dict[str, Any]:
        """Get statistics for all libraries"""
        libraries = self.parsing_service.parse_library_folders()
        games_by_lib = self.get_games_by_library()

        stats = {
            'total_games': len(self.games),
            'total_size': sum(g.total_size for g in self.games),
            'libraries': []
        }

        for lib_path, lib_data in libraries.items():
            games = games_by_lib.get(lib_path, [])

            lib_stats = {
                'path': lib_path,
                'label': lib_data.get('label', ''),
                'game_count': len(games),
                'total_size': sum(g.total_size for g in games),
                'size_breakdown': {
                    'games': sum(g.size_on_disk for g in games),
                    'shader_cache': sum(g.shader_cache_size for g in games),
                    'workshop': sum(g.workshop_content_size for g in games)
                }
            }

            stats['libraries'].append(lib_stats)

        return stats
